import aiohttp
import datetime
import aiofiles
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiocsv import AsyncWriter

ua = UserAgent()

async def get_data():
    kategory = input("Введите название категории: ")
    url = f'https://www.citilink.ru/catalog/{kategory}/?view_type=grid&p=1'
    # url=f'https://www.citilink.ru/catalog/{kategory}/?p=1'
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')


    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': f'{ua.random}',
    }

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")


        pagination = int(soup.find('div', class_='PaginationWidget__wrapper-pagination').find('a', class_='PaginationWidget__page_last').text.strip())

        data = []
        for page in range(1, pagination + 1):
            url = f'https://www.citilink.ru/catalog/{kategory}/?view_type=grid&p={page}'
            # url = f'https://www.citilink.ru/catalog/{kategory}/?p={page}'

            response = await session.get(url=url, headers=headers)
            soup = BeautifulSoup(await response.text(), "lxml")

            all_cards = soup.find_all('div', class_='ProductCardVertical_separated')

            for card in all_cards:
                try:
                    card_title = card.find('div', class_='ProductCardVertical__description').find('a', class_='ProductCardVertical__name').text.strip()

                    card_name = card_title.split(',')[0].strip()

                    # card_code = card_title.split(',')[1].strip()

                    card_color = card_title.split(',')[-1].strip()
                    
                    card_url = f"https://www.citilink.ru{card.find('a', class_='ProductCardVertical__link').get('href')}"
                    
                    card_sale_price = card.find('span', class_='ProductCardVerticalPrice__price-club_current-price').text.strip()

                    card_current_price = card.find('span', class_='ProductCardVerticalPrice__price-current_current-price').text.strip()

                    data.append(
                        [card_name, card_color, card_current_price, card_sale_price, card_url]
                    )            

                except AttributeError :
                    continue

            print(f"[+] Data collected from {page} out of {pagination}")

    async with aiofiles.open(f"data/{cur_time}.csv", "w") as file:
        writer = AsyncWriter(file)

        await writer.writerow(
            [
                'Name',
                'Color',
                'Current price',
                'Price with citilink card',
                # 'Product code',
                'Url'
            ]
        )

        await writer.writerows(
            data
        )

    return f'{cur_time}.csv'

async def main():
    await get_data()

if __name__ == '__main__':
    asyncio.run(main())