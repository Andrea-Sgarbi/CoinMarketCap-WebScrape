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
        next(reader)  # Skip header
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


# Function to extract data from the page
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


# Function to write data to the CSV
def csv_append(csv, info):
    try:
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
    except locale.Error:
        print("Warning: 'it_IT.UTF-8' locale is not available. Falling back to the default locale.")
        locale.setlocale(locale.LC_ALL, '')
    # Sanitize input
    sanitized_price = info[3].replace('€', '')
    sanitized_price = sanitized_price.replace('.', '')
    # Convert to float
    price_float = locale.atof(sanitized_price)
    # Format to 8 decimal places and replace dot with comma
    price_str = f"{price_float:.8f}".replace('.', ',')
    print(info[1] + ': ' + price_str)
    # Write to CSV using the comma-separated string
    csv.writerow([info[0], info[1], info[2], price_str])
    return 0


# Main function
if __name__ == '__main__':
    # Path to the CSV file to read
    csv_path = 'CryptoValue.csv'
    csv_data = csv_to_list(csv_path)

    # Create URL objects with the following elements:
    # 0. URL to connect to
    # 1. Class of the div containing the price
    # 2. Cryptocurrency symbol
    # 3. Cryptocurrency name
    # 4. Cryptocurrency ID
    crypto_objects = url_object(csv_data)

    # Extract data for writing to CSV
    # 0. Cryptocurrency symbol
    # 1. Cryptocurrency name
    # 2. Cryptocurrency ID
    # 3. Price
    csv_write_data = []
    print("Start of data extraction...")
    for crypto in crypto_objects:
        price = url_data(crypto)
        csv_write_data.append([crypto[2], crypto[3], crypto[4], price])

    if len(csv_data) != len(csv_write_data):  # Replace with your error condition
        print("Missing elements for writing to CSV!")
        sys.exit(1)

    # Path to the CSV file to write
    print("Start of CSV writing...")
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['Column1.name', 'Column2.symbol', 'Column3.id', 'Column4.price_usd'])

        for data in csv_write_data:
            res = csv_append(writer, data)
