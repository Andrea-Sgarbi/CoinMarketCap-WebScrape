import csv
import gzip
import requests
import locale

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# Constants
DIV_CLASS = "sc-65e7f566-0 WXGwg base-text"
MAX_RETRIES = 3

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
    i = 0
    data = None
    while ((i < MAX_RETRIES) and (data is None)):
        page = urlopen(url[0])
        # sleep(2)
        check_type = page.info().get('content-encoding')
        if check_type == 'gzip':
            html = gzip.decompress(page.read()).decode('utf-8')
        else:
            html = page.read().decode("utf-8")

        soup = BeautifulSoup(html, "html.parser")
        data = soup.find('span', {'class': url[1]})
        if data is None:
            data = soup.find('div', {'class': "priceValue"})

        if data is None:
            response = requests.get(url[0])
            # sleep(2)
            html = response.content
            soup = BeautifulSoup(html, "html.parser")
            data = soup.find('span', {'class': url[1]})
            if data is None:
                data = soup.find('div', {'class': "priceValue"})

        i += 1

    if data is None:
        return '0.0'

    return data.text


# Funzione per scrivere i dati sul CSV
def csv_append(csv, info, price):
    try:
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
    except locale.Error:
        print("Warning: 'it_IT.UTF-8' locale is not available. Falling back to the default locale.")
        locale.setlocale(locale.LC_ALL, '')
    # Sanitizza l'input
    sanitized_price = price.replace('€', '')
    sanitized_price = sanitized_price.replace('.', '')
    # Converte in float
    price_float = locale.atof(sanitized_price)
    # Format a 8 decimali e sostituisci il punto con la virgola
    price_str = f"{price_float:.8f}".replace('.', ',')
    print(info[2] + ': ' + price_str)
    # Scrivi sul CSV usando la stringa con virgola
    csv.writerow([info[2], info[3], info[4], price_str])
    return 0


# Funzione principale
if __name__ == '__main__':
    # Percorso del file CSV da leggere
    csv_path = 'CryptoValue.csv'
    csv_data = csv_to_list(csv_path)

    # Creazione degli oggetti URL
    url_list = url_object(csv_data)

    # Percorso del file CSV da scrivere
    csv_path_out = 'CryptoValueOut.csv'
    with open(csv_path_out, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['Column1.name', 'Column2.symbol', 'Column3.id', 'Column4.price_usd'])

        for url in url_list:
            price = url_data(url)
            res = csv_append(writer, url, price)
