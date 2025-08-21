import csv
import locale
import sys

from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from helium import *

from bs4 import BeautifulSoup


# Constants
DIV_CLASS = 'sc-65e7f566-0 WXGwg base-text'


# Read CSV file and convert to list
def csv_to_list(csv_path):
    result = []
    with open(csv_path, mode='r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader)  # Salta l'intestazione
        for row in reader:
            if len(row) >= 2:
                result.append([row[0], row[1], row[2]])
    return result


# Create URL objects for each coin
def url_object(coin_list):
    data = []
    for coin in coin_list:
        data.append([f"https://coinmarketcap.com/it/currencies/{coin[2]}/", DIV_CLASS, coin[0], coin[1], coin[2]])
    return data


# Funzione per estrarre i dati dalla pagina
def url_data(url):

    options = ChromeOptions()
    options.add_argument("--headless=new")
    service = Service(executable_path='/usr/local/bin/chromedriver')
    driver = Chrome(service=service, options=options)
    driver.get(url[0])
    delay = 3
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, f"//span[@class={repr(url[1])}]")))
        print(f"Page for {url[3]} is ready!")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = soup.find('span', {'class': url[1]})
        if data is None:
            price = soup.find('div', {'class': "priceValue"})
        else:
            price = data.text
    except TimeoutException:
        print(f"Loading took too much time for page {url[3]}!")
        price = '0.0'

    return price


# Funzione per scrivere i dati sul CSV
def csv_append(csv, info):
    try:
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
    except locale.Error:
        print("Warning: 'it_IT.UTF-8' locale is not available. Falling back to the default locale.")
        locale.setlocale(locale.LC_ALL, '')
    # Sanitizza l'input
    sanitized_price = info[3].replace('€', '')
    sanitized_price = sanitized_price.replace('.', '')
    # Converte in float
    price_float = locale.atof(sanitized_price)
    # Format a 8 decimali e sostituisci il punto con la virgola
    price_str = f"{price_float:.8f}".replace('.', ',')
    print(info[1] + ': ' + price_str)
    # Scrivi sul CSV usando la stringa con virgola
    csv.writerow([info[0], info[1], info[2], price_str])
    return 0


# Funzione principale
if __name__ == '__main__':
    # Percorso del file CSV da leggere
    csv_path = 'CryptoValue.csv'
    csv_data = csv_to_list(csv_path)

    # Creazione degli oggetti URL con i seguenti elementi:
    # 0. URL a cui collegarsi
    # 1. Classe del div contenente il prezzo
    # 2. Simbolo criptovaluta
    # 3. Nome criptovaluta
    # 4. ID criptovaluta
    crypto_objects = url_object(csv_data)

    # Estrazione dei dati per la scrittura su CSV
    # 0. Simbolo criptovaluta
    # 1. Nome criptovaluta
    # 2. ID criptovaluta
    # 3. Prezzo
    csv_write_data = []
    print("Inizio estrazione dati...")
    for crypto in crypto_objects:
        price = url_data(crypto)
        csv_write_data.append([crypto[2], crypto[3], crypto[4], price])

    if len(csv_data) != len(csv_write_data):  # Sostituisci con la tua condizione di errore
        print("Elementi mancanti per la scrittura su CSV!")
        sys.exit(1)

    # Percorso del file CSV da scrivere
    print("Inizio scrittura su CSV...")
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['Column1.name', 'Column2.symbol', 'Column3.id', 'Column4.price_usd'])

        for data in csv_write_data:
            res = csv_append(writer, data)
