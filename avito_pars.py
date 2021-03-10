import time, requests, random, fake_useragent
from bs4 import BeautifulSoup
import pandas as pd

user_agent = fake_useragent.UserAgent(verify_ssl=False).random
URL = input('Введите URL страницы парсинга на авито (пример - "https://www.avito.ru/moskva/nastolnye_kompyutery"): ')
HEADERS = {
    'user-agent': user_agent
}


#   производим запрос на сервер и получаем первую страницу для выполнения парсинга страниц по данной категории
response = requests.get(URL, headers=HEADERS)
first_page = response.text
first_page_soup = BeautifulSoup(first_page, 'lxml')
page_count = first_page_soup.find_all('span', class_='pagination-item-1WyVp')[7].string  # получаено количество страниц на сайте
print(f'Количество страниц для парсинга: {page_count}')

#   определение диапазона страниц парсинга
print(f'Какие страницы будем парсить? Внимание! при большом количество страниц для парсинга, есть вероятность бана вашего IP адреса')
first_page_for_parsing = int(input('Введите с какой страницы начать парсинг: '))
if first_page_for_parsing <= 0:
    while first_page_for_parsing <= 0:
        print('Число не может быть меньше 0!')
        first_page_for_parsing = int(input('Введите с какой страницы начать парсинг: '))
last_page_for_parsing = int(input('Введите по какую страницу парсинг: '))
if last_page_for_parsing <= first_page_for_parsing:
    while last_page_for_parsing <= first_page_for_parsing:
        print('Последний номер страницы парсинка не может быть меньше первого')
        last_page_for_parsing = int(input('Введите по какую страницу парсинг: '))

#   выполнение парсинга запрошенных страниц
number_of_page = first_page_for_parsing
for page in range(first_page_for_parsing, last_page_for_parsing):
    url_page = f"{URL}{page}"
    response_page = requests.get(url_page, headers=HEADERS).text
    with open(f'pages/avito#{page}.html', 'w') as file:
        file.write(response_page)
    print(f'Страница №{number_of_page} спарсина, осталось еще {last_page_for_parsing-number_of_page} страниц')
    number_of_page += 1
    random_time = random.randrange(0, 40)
    time.sleep(random_time / 10)
print("Все страницы спарсены удачно!")

df = {}
product_name = []
product_price = []
product_publ_date = []
product_adress = []
seller_name_list = []
product_link = []

#   выполнение парсинга с сохраненных страниц
for page_file in range(first_page_for_parsing, last_page_for_parsing):
    with open(f'pages/avito#{page_file}.html', 'r') as file_parse:
        src = file_parse.read()
        file_parse_soup = BeautifulSoup(src, 'lxml')
        name = file_parse_soup.find_all('div', class_='iva-item-titleStep-2bjuh')
        price = file_parse_soup.find_all('span', class_='price-price-32bra')
        link = file_parse_soup.find_all('a', class_='iva-item-sliderLink-2hFV_')
        for i in name:
            product_name.append(i.string)
        for i in price:
            product_price.append(i.text)
        for i in link:
            product_link.append("https://www.avito.ru" + i.get('href'))
        link_count = 1
        for link in product_link:
            response_of_links = requests.get(link, headers=HEADERS).text
            file_name = link.split('/')[-1]
            with open(f'product_page/{file_name}.html', 'w') as file:
                file.write(response_of_links)
                print(f'Получена информация со страницы № {link_count} из {len(product_link)} ({file_name}))')
                random_time = random.randrange(0, 40)
                time.sleep(random_time / 10)
            with open(f'product_page/{file_name}.html', 'r') as file:
                src = file.read()
                link_count += 1
                soup = BeautifulSoup(src, 'lxml')
                if 'title-info-metadata-item-redesign' not in soup:
                    publ_date = "Нет даты публикации"
                else:
                    publ_date = soup.find('div', class_='title-info-metadata-item-redesign').text.strip()
                product_publ_date.append(publ_date)
                if 'item-address__string' not in soup:
                    publ_adress = "Нет адреса"
                else:
                    publ_adress = soup.find('span', class_='item-address__string').text.strip()
                product_adress.append(publ_adress)
                name = soup.find('div', class_='seller-info-prop seller-info-prop_short_margin')
                print(name)
                if name is None:
                    name = soup.find('div', class_='sticky-header-prop sticky-header-seller').find('span',
                                                                                                   class_='sticky-header-seller-text').string.strip()
                else:
                    seller_name = soup.find('div', class_='seller-info-prop seller-info-prop_short_margin').find('div',
                                                                                                                 class_='seller-info-value').string.strip()

df['Name'] = product_name
df['Price'] = product_price
df['Publ_date'] = product_publ_date
df['Publ_adress'] = product_adress
df['Seller_name'] = seller_name_list
df['Link'] = product_link

data = pd.DataFrame(df)
data.to_excel('data.xlsx')
