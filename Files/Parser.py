from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

options = Options()
# Запуск браузера с развернутым экраном
options.add_argument('start-maximized')
# Будем использовать браузер Chrom
driver = webdriver.Chrome(options=options)
# Открываем ссылку
url_list=[]
time.sleep(5)

# Прокручиваем страницу и записываем все ссылки на книги,
# если есть кнопка "далее" - нажимаем её или выходим из цикла
for i in range (1,27):
    try:
        driver.get('https://www.chitai-gorod.ru/catalog/books/publicistika-110028?page='+str(i))
        time.sleep(10)
    except Exception:
        time.sleep(500)

    wait = WebDriverWait(driver, 10)
    # Количество книг на странице
    count = None
    while True:
        time.sleep(10)
        # Ожидаем появление объекта (html код) карточек товара
        cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "products-list"]/article')))
        # Выходим из цикла, если при прокрутке страницы, количество товаров не меняется
        if len(cards) == count:
            break
            # Вычисляем сколько карточек товара на странице
        count = len(cards)
        # Прокручиваем страницу выполняя JAVA Script
        driver.execute_script('window.scrollBy(0, 1800)')
        time.sleep(2)

    # На полностью загруженной странице соберём информацию
    url_list_one = [card.find_element(By.XPATH, './a').get_attribute('href') for card in cards]
    url_list.extend(url_list_one)

print(f'Всего получено: {len(url_list)} ссылок на книги')

# Заходим на каждую страницу найденных книг и парсим её
driver2 = webdriver.Chrome(options=options)
wait2 = WebDriverWait(driver2, 2)
books_list = []

# Просматриваем все ссылки на книги
n=1
for url_item in url_list:
    books_dict = {}
    book_response = requests.get(url_item)
    book_soup = BeautifulSoup(book_response.text, "html.parser")


    driver2.get(url_item)
    time.sleep(5)
    books_dict['N'] = n
    n+=1


    # Заносим назание книги
    try:
        books_dict['name'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//h1"))).text.partition('\n')[0]    
    except Exception:
        books_dict['name'] = None
    
    #Заносим цену книги
    try:
        priceS = book_soup.find("span", class_="product-offer-price__current product-offer-price__current--discount").text.strip()
    except Exception:
        try:
            priceS = book_soup.find("span", class_="product-offer-price__current").text.strip()
        except Exception:
            priceS = None  

    try:
        priceS=priceS.replace('&nbsp;','')
    except Exception:
        print(priceS)
    try:
        priceS=priceS.replace('\xa0','')
    except Exception:
        print(priceS)


    #Переводим цену книги в формат Float
    try:
        books_dict['price'] = float(priceS[:-2])  
    except Exception:
        books_dict['price'] = priceS
   
    # Заносим url ссылку на книгу
    books_dict['url'] = url_item

   #Заносим количество страниц книги
    try:
        books_dict['pages'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Количество страниц')]/following-sibling::span[1]"))).text
    except Exception:
        books_dict['pages'] = None

    #Заносим размер книги
    try:
        size = wait2.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Размер')]/following-sibling::span[1]"))).text
    except Exception:
        size = "0x0x0" 
    
    #Раскладываем размер на три поля
    books_dict['size1'] = size.split('x')[0]
    books_dict['size2'] = size.split('x')[1]
    books_dict['size3'] = size.split('x')[2]

    #Заносим вес книги
    try:
        books_dict['weight'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Вес, г')]/following-sibling::span[1]"))).text
    except Exception:
        books_dict['weight'] = None
   
    #Заносим тип олбожки
    try:
        books_dict['cover'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Тип обложки')]/following-sibling::span[1]"))).text
    except Exception:
        books_dict['cover'] = None
    
    #Заносим год издания
    try:
        books_dict['year'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Год издания')]/following-sibling::span[1]"))).text
    except Exception:
        books_dict['year'] = None
    
    #Заносим описание книги
    try:
        books_dict['description'] = wait2.until(EC.presence_of_element_located((By.XPATH, "//article[@class = 'detail-description__text']"))).text
    except Exception:
        books_dict['description'] = None
   
   

    # Добавляем словарь в список книг
    print(books_dict)
    books_list.append(books_dict)
    
    #сохраняем в JSON

with open('resultDiplom.json', 'w', encoding='utf-8') as json_file:
    json.dump(books_list, json_file, ensure_ascii=False, indent=4)
