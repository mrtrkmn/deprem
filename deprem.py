# Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü'nün
# http://www.koeri.boun.edu.tr/scripts/lasteq.asp adresinden
# son 24 saatte meydana gelen depremlerin içerisinden
# aranan şehire göre bildirim gönderen script

import csv
import time
from datetime import datetime, timezone
from io import StringIO
from os import environ

import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

KANDILLI_URL = "http://www.koeri.boun.edu.tr/scripts/lasteq.asp"
SEARCH_RECENT_FOR_EVENTS = "http://sc3.koeri.boun.edu.tr/eqevents/eq_events"
TELEGRAM_CHAT_ID = environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = environ.get("TELEGRAM_TOKEN")
TIME_INTERVAL = environ.get("TIME_INTERVAL")  # minutes
CITY_TO_BE_CHECKED = environ.get("CITY_TO_BE_CHECKED")
DATA_DIR = environ.get("DATA_DIR")
CHROME_EXECUTABLE_PATH = environ.get("CHROME_EXECUTABLE_PATH")
# create array of cities in Turkey
CITIES = [
    "ADANA",
    "ADIYAMAN",
    "AFYON",
    "AGRI",
    "AKSARAY",
    "AMASYA",
    "ANKARA",
    "ANTALYA",
    "ARDAHAN",
    "ARTVIN",
    "AYDIN",
    "BALIKESIR",
    "BARTIN",
    "BATMAN",
    "BAYBURT",
    "BILECIK",
    "BINGOL",
    "BITLIS",
    "BOLU",
    "BURDUR",
    "BURSA",
    "CANAKKALE",
    "CANKIRI",
    "CORUM",
    "DENIZLI",
    "DIYARBAKIR",
    "DUZCE",
    "EDIRNE",
    "ELAZIG",
    "ERZINCAN",
    "ERZURUM",
    "ESKISEHIR",
    "GAZIANTEP",
    "GIRESUN",
    "GUMUSHANE",
    "HAKKARI",
    "HATAY",
    "IGDIR",
    "ISPARTA",
    "ISTANBUL",
    "IZMIR",
    "KAHRAMANMARAS",
    "KARABUK",
    "KARAMAN",
    "KARS",
    "KASTAMONU",
    "KAYSERI",
    "KILIS",
    "KIRIKKALE",
    "KIRKLARELI",
    "KIRSEHIR",
    "KOCAELI",
    "KONYA",
    "KUTAHYA",
    "MALATYA",
    "MANISA",
    "MARDIN",
    "MERSIN",
    "MUGLA",
    "MUS",
    "NEVSEHIR",
    "NIGDE",
    "ORDU",
    "OSMANIYE",
    "RIZE",
    "SAKARYA",
    "SAMSUN",
    "SANLIURFA",
    "SIIRT",
    "SINOP",
    "SIRNAK",
    "SIVAS",
    "TEKIRDAG",
    "TOKAT",
    "TRABZON",
    "TUNCELI",
    "USAK",
    "VAN",
    "YALOVA",
    "YOZGAT",
    "ZONGULDAK",
]

class Deprem: 
   
    def __init__(self):
    #    convert string input to int
        try:
            TIME_INTERVAL = int(TIME_INTERVAL)
        except Exception as e:
            print(e)
            exit(1)
        self.headers = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        
        self.chrome_options = webdriver.ChromeOptions()
        self.executable_path = CHROME_EXECUTABLE_PATH
        preferences = {"download.default_directory": DATA_DIR}

            # add user agent to avoid bot detection
        self.chrome_options.add_experimental_option("prefs", preferences)
        self.chrome_options.add_argument(self.headers)
        # if environ.get("LOCAL_DEV") != "True":
        #     self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--window-size=1920,1080") 
        self.chrome_options.add_argument("--disable-gpu")   
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_service = ChromeService(executable_path=self.executable_path)
        self.driver = webdriver.Chrome(
            service=self.chrome_service, options=self.chrome_options
        )
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
        
    def __enter__(self):
        return self

    def send_message(self, message):
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
            )
            if response.status_code != 200:
                print("Error while sending message: ", response.status_code)
        except Exception as e:
            print(e)


    def check_city_input(self):
        if unidecode.unidecode(CITY_TO_BE_CHECKED.upper()) not in CITIES:
            print("Türkiye'de bulunmayan bir şehir girdiniz veya şehir adını yanlış girdiniz.")
            exit(1)

    def get_data_from_kandilli(self):
        
        # get data from kandilli url and parse it
        try:
            response = requests.get(KANDILLI_URL)
            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")
            table = soup.find("pre").find(string=True)
            return table
        except Exception as e:
            print(e)
            exit(1)

    def extract_data(self, table, send_message):
        # find the earthquake pre table
        buff = StringIO(table)
        reader = csv.reader(buff)

        for line in reader:
            try:
                attributes = line[0].split()
                city = attributes[8] + " " + attributes[9]
                date_time = attributes[0] + " " + attributes[1]
                # parse the date and time
                timestamp = datetime.strptime(date_time, "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc).replace(tzinfo=None)
                current_timestamp = datetime.utcnow().replace(tzinfo=None)
                time_difference = (current_timestamp - timestamp).total_seconds() / 60
                if time_difference <= TIME_INTERVAL and CITY_TO_BE_CHECKED.upper() in city.upper():
                    message = f"""Tarih/Zaman: {attributes[0]} {attributes[1]}\n\nŞehir: {city}\n\nDerinlik(km): {attributes[4]}\t MD: {attributes[5]}\t ML: {attributes[6]}\tMw: {attributes[7]}\n\nKaynak: Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü """
                    send_message(message)
            except Exception as e:
                print(e)
                continue
    
    
    def search_on_kandilli_with_selenium(self):
        
        self.driver.get(SEARCH_RECENT_FOR_EVENTS)
        
        FROM_YEAR_XPATH = '//*[@id="fromTY"]'  
        FROM_MONTH_XPATH = '//*[@id="fromTM"]'
        FROM_DAY_XPATH = '//*[@id="fromTD"]'
        
        WebDriverWait(
                self.driver,
                30 *
                5).until(
                EC.element_to_be_clickable(
                (By.XPATH,
                    FROM_YEAR_XPATH)))
        
        try: 
            from_year_field = self.driver.find_element(By.XPATH, FROM_YEAR_XPATH)
            from_year_field.clear()
            from_year_field.send_keys('2022')
            time.sleep(0.5)
            from_month_field = self.driver.find_element(By.XPATH, FROM_MONTH_XPATH)
            from_month_field.clear()
            from_month_field.send_keys('02')
            time.sleep(0.5)
            from_day_field = self.driver.find_element(By.XPATH, FROM_DAY_XPATH)
            from_day_field.clear()
            from_day_field.send_keys('02')
            time.sleep(0.5)
        except Exception as e:
            print(e)
            exit(1)
            
        
        
        TO_YEAR_XPATH = '//*[@id="toY"]'
        TO_MONTH_XPATH = '//*[@id="toM"]'
        TO_DAY_XPATH = '//*[@id="toD"]'
        
        try: 
            to_year_field = self.driver.find_element(By.XPATH, TO_YEAR_XPATH)
            to_year_field.clear()
            to_year_field.send_keys('2022')
            time.sleep(0.5)
            to_month_field = self.driver.find_element(By.XPATH, TO_MONTH_XPATH)
            to_month_field.clear()
            to_month_field.send_keys('02')
            time.sleep(0.5)
            to_day_field = self.driver.find_element(By.XPATH, TO_DAY_XPATH)
            to_day_field.clear()
            to_day_field.send_keys('20')
            time.sleep(0.5)
        except Exception as e:
            print(e)
            exit(1)
            
        
        APPLY_FILTER_BUTTON = '//*[@id="myPost"]/fieldset/div/input[1]'
            
        try: 
            apply_button = self.driver.find_element(By.XPATH, APPLY_FILTER_BUTTON)
            apply_button.click()
        except Exception as e:
            print (e)
            
        time.sleep(4)
        
        all_tables = pd.read_html(self.driver.page_source, attrs={'class': 'index'})
        df = all_tables[0]
        
        timestamp = timestamp = datetime.now().strftime("%d_%m_%Y")
        df.to_excel(f"depremler-{timestamp}.xlsx")
        


# create main function
if __name__ == "__main__":
    with Deprem() as deprem_bot:
        deprem_bot.search_on_kandilli_with_selenium()


