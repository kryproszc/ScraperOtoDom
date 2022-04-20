from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import sqlite3
import numpy as np
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.test_database
mojaBaza = db["Otodom"]

driver = webdriver.Chrome('/Users/Szczesny/.wdm/drivers/chromedriver/mac64/97.0.4692.71/chromedriver')

def wypiszInformacje(zmienna):
    try:
        Dana = driver.find_element_by_xpath(f"//div[@aria-label='{zmienna}']")
    except NoSuchElementException as err:
        return "-"
    else:
        return Dana.text.split('\n')[1]

def wypiszInformacjeDodatkowe(clasa):
    try:
        elementy =driver.find_element_by_css_selector(f"{clasa}").text
    except NoSuchElementException as err:
        return ["-"]
    else:
        return [informacja.replace('/',',') for informacja in elementy.split('\n') if informacja[0].islower()]

def zwracLinkiOgoszen(URL,iloscPodstron):
    linki = []
    link = URL
    for i in range(1,iloscPodstron+1):
        link = link+str(i)
        page = get(link)
        bs=BeautifulSoup(page.content,'html.parser')
        ogloszenia = bs.find_all('a', class_="css-1aeekh1 es62z2j27")
        linki = linki + list(map(lambda x: x['href'],ogloszenia))
        link = URL
    return linki

linki = zwracLinkiOgoszen('https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/krakow?page=',510)
linki = list(set(linki))

for link in linki:
    URL = "https://www.otodom.pl"+link
    driver.get(URL)
    dane = {
        'Cena':driver.find_elements_by_class_name("css-b114we.eu6swcv14")[0].text,
        'Powierzchnia':wypiszInformacje('Powierzchnia'),
        'Rynek':wypiszInformacje('Rynek'),
        'Lokalizacja':driver.find_element_by_css_selector("div.css-1k12nzr.eu6swcv10").text,
        'Ogrzewanie': wypiszInformacje('Ogrzewanie'),
        'Liczba_pokoi':wypiszInformacje('Liczba pokoi'),
        'Stan':wypiszInformacje('Stan Wykończenia'),
        'Pietro':wypiszInformacje('Piętro'),
        'Rok':wypiszInformacje('Rok budowy'),
        'informacjeDodatkowe':wypiszInformacjeDodatkowe("div.css-1lw3ul3.ex3yvbv4")}
    mojaBaza.insert_one(dane) 