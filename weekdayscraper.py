from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb


import re

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


def getProduct(URL, SIZE):

    display = Xvfb()
    display.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)
    SIZE = SIZE.upper()
    driver.get(URL)
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()

    page = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(page.content, features='lxml')
    if soup.find("div", {"class": re.compile(r'.*is-selected out-of-stock.*')}) or not soup.find("button", {"id": "selectSizeLabel"}):
        availability = "Out of Stock"
    else:
        driver.find_element(
            By.XPATH, "//button[@id='selectSizeLabel']").click()
        if soup.find("li", {"class": "a-option is-disabled", "data-value": SIZE}):
            availability = "out of stock"

        else:
            wait = WebDriverWait(driver, 20)

            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//li[@data-value='" + SIZE + "']"))).click()
            availability = 'Available' if soup.find_all(
                "button", {"id": "addToBagButton"}) else "Not Available"

    title = soup.select("#productTitle")[0].get_text().strip()
    price = soup.select("#product-price")[0]
    reduced = price.find("span", {"class": "is-reduced"})
    if reduced:
        price = (price.findAll("span", {
            "class": "is-deprecated"})[0].text) + " reduced to " + reduced.text
    else:
        price = price.get_text().strip()
    features = [title, price, availability]
    print(features)
    driver.quit()
    display.stop()


URL = input("Paste URL of product: ")
SIZE = input("Enter size: ")
getProduct(URL, SIZE)
