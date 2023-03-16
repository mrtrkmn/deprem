# Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü'nün
# http://www.koeri.boun.edu.tr/scripts/lasteq.asp adresinden
# son 24 saatte meydana gelen depremlerin içerisinden
# aranan şehire göre bildirim gönderen script

import csv
import datetime as dt
import time
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
from selenium.webdriver.support.ui import Select, WebDriverWait

KANDILLI_URL = "http://www.koeri.boun.edu.tr/scripts/lasteq.asp"
SEARCH_RECENT_FOR_EVENTS = "http://sc3.koeri.boun.edu.tr/eqevents/eq_events"
TELEGRAM_CHAT_ID = environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = environ.get("TELEGRAM_TOKEN")
CITY_TO_BE_CHECKED = environ.get("CITY_TO_BE_CHECKED")
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
    def __init__(self, is_selenium_active=False):
        #    convert string input to int
        self.is_selenium_active = is_selenium_active
        if environ.get("TIME_INTERVAL"):
            self.time_interval = int(environ.get("TIME_INTERVAL"))
        else:
            self.time_interval = 5

        if environ.get("DATA_DIR"):
            self.data_dir = environ.get("DATA_DIR")
        else:
            self.data_dir = "./dat/"

    def __exit__(self, exc_type, exc_value, traceback):
        if self.is_selenium_active:
            self.driver.quit()

    def __enter__(self):
        if self.is_selenium_active:
            self.headers = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"

            self.chrome_options = webdriver.ChromeOptions()
            self.executable_path = CHROME_EXECUTABLE_PATH
            preferences = {"download.default_directory": self.data_dir}

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
            self.driver = webdriver.Chrome(service=self.chrome_service, options=self.chrome_options)

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

    def check_date_time(self, date_text):
        try:
            dt.date.fromisoformat(date_text)
            return True
        except ValueError:
            print(f"Hatalı tarih aralığı, tarih aralığı değiştirilmeden devam ediliyor {date_text}")
            return False

    def check_city_input(self, city):
        if unidecode.unidecode(city.upper()) not in CITIES:
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

    def extract_data(self, table, city_to_be_checked, time_interval):
        # find the earthquake pre table

        try:
            time_interval = int(time_interval)
        except ValueError:
            print("Lütfen zaman aralığını sayı olarak giriniz.")
            exit(1)

        buff = StringIO(table)
        reader = csv.reader(buff)

        for line in reader:
            try:
                attributes = line[0].split()
                city = attributes[8] + " " + attributes[9]
                date_time = attributes[0] + " " + attributes[1]
                # parse the date and time
                timestamp = (
                    dt.datetime.strptime(date_time, "%Y.%m.%d %H:%M:%S")
                    .replace(tzinfo=dt.timezone.utc)
                    .replace(tzinfo=None)
                )
                current_timestamp = dt.datetime.utcnow().replace(tzinfo=None)
                time_difference = (current_timestamp - timestamp).total_seconds() / 60
                if time_difference <= time_interval and city_to_be_checked.upper() in city.upper():
                    print("-" * 100)
                    message = f"""Tarih/Zaman: {attributes[0]} {attributes[1]}\nŞehir: {city}\nDerinlik(km): {attributes[4]}\t MD: {attributes[5]}\t ML: {attributes[6]}\tMw: {attributes[7]}\nKaynak: Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü """
                    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
                        print(message)
                    else:
                        self.send_message(message)
            except Exception as e:
                # print(e)
                continue

    def select_from_year(self, year, month, day):
        FROM_YEAR_XPATH = '//*[@id="fromTY"]'
        FROM_MONTH_XPATH = '//*[@id="fromTM"]'
        FROM_DAY_XPATH = '//*[@id="fromTD"]'

        WebDriverWait(self.driver, 30 * 5).until(EC.element_to_be_clickable((By.XPATH, FROM_YEAR_XPATH)))

        try:
            from_year_field = self.driver.find_element(By.XPATH, FROM_YEAR_XPATH)
            from_year_field.clear()
            from_year_field.send_keys(year)
            time.sleep(0.5)
            from_month_field = self.driver.find_element(By.XPATH, FROM_MONTH_XPATH)
            from_month_field.clear()
            from_month_field.send_keys(month)
            time.sleep(0.5)
            from_day_field = self.driver.find_element(By.XPATH, FROM_DAY_XPATH)
            from_day_field.clear()
            from_day_field.send_keys(day)
            time.sleep(0.5)
        except Exception as e:
            print(e)
            exit(1)

    def select_to_year(self, year, month, day):
        TO_YEAR_XPATH = '//*[@id="toY"]'
        TO_MONTH_XPATH = '//*[@id="toM"]'
        TO_DAY_XPATH = '//*[@id="toD"]'

        WebDriverWait(self.driver, 30 * 5).until(EC.element_to_be_clickable((By.XPATH, TO_YEAR_XPATH)))

        try:
            to_year_field = self.driver.find_element(By.XPATH, TO_YEAR_XPATH)
            to_year_field.clear()
            to_year_field.send_keys(year)
            time.sleep(0.5)
            to_month_field = self.driver.find_element(By.XPATH, TO_MONTH_XPATH)
            to_month_field.clear()
            to_month_field.send_keys(month)
            time.sleep(0.5)
            to_day_field = self.driver.find_element(By.XPATH, TO_DAY_XPATH)
            to_day_field.clear()
            to_day_field.send_keys(day)
            time.sleep(0.5)
        except Exception as e:
            print(e)
            exit(1)

    def set_depth(self, min, max):
        MIN_DEPTH = '//*[@id="min_depth"]'
        MAX_DEPTH = '//*[@id="max_depth"]'

        if not min or not max:
            min = 0
            max = 60

        if min > max or min < 0:
            print("Derinlik aralığı hatalı, min 0'dan küçük olamaz, max min'den küçük olamaz")
            exit(1)

        try:
            min_depth = self.driver.find_element(By.XPATH, MIN_DEPTH)
            min_depth.clear()
            min_depth.send_keys(min)
            time.sleep(0.5)
            max_depth = self.driver.find_element(By.XPATH, MAX_DEPTH)
            max_depth.clear()
            max_depth.send_keys(max)
            time.sleep(0.5)
        except Exception as e:
            print(e)

    def set_magnitude(self, min, max):
        MIN_MAGNITUDE = '//*[@id="min_mag"]'
        MAX_MAGNITUDE = '//*[@id="max_mag"]'

        if not min or not max:
            min = 0
            max = 10

        if min > max or min < 0:
            print("Siddet aralığı hatalı, min 0'dan küçük olamaz, max min'den küçük olamaz")

        try:
            min_magnitude = self.driver.find_element(By.XPATH, MIN_MAGNITUDE)
            min_magnitude.clear()
            min_magnitude.send_keys(min)
            time.sleep(0.5)
            max_magnitude = self.driver.find_element(By.XPATH, MAX_MAGNITUDE)
            max_magnitude.clear()
            max_magnitude.send_keys(max)
            time.sleep(0.5)
        except Exception as e:
            print(e)

    def set_sorting(self, choose):
        ORDERED_BY = '//*[@id="myPost"]/fieldset/table/tbody/tr[12]/td[2]/select'
        ALLOWED_VALUES = ["Origin Time UTC", "Longitude", "Latitude", "Magnitude", "Depth"]

        if choose not in ALLOWED_VALUES:
            print("Choosing default value: ", "Origin Time UTC")
            choose = "Origin Time UTC"

        if choose not in ALLOWED_VALUES:
            print("Choose one of the following values: ", ALLOWED_VALUES)
            exit(1)

        try:
            dropdown_element = Select(self.driver.find_element(By.XPATH, ORDERED_BY))
            dropdown_element.select_by_visible_text(choose)
        except Exception as e:
            print(e)

    def set_asc_desc(self, choose):
        ORDER_TYPE = ["ascending", "descending"]
        ASC_DESC = '//*[@id="myPost"]/fieldset/table/tbody/tr[12]/td[3]/select'

        if choose.lower() not in ORDER_TYPE:
            print("Choose one of the following values: ", ORDER_TYPE)
            choose = "ascending"

        try:
            sorting_value = Select(self.driver.find_element(By.XPATH, ASC_DESC))
            sorting_value.select_by_visible_text(choose)
        except Exception as e:
            print(e)

    def apply_changes(self):
        APPLY_FILTER_BUTTON = '//*[@id="myPost"]/fieldset/div/input[1]'

        try:
            apply_button = self.driver.find_element(By.XPATH, APPLY_FILTER_BUTTON)
            apply_button.click()
        except Exception as e:
            print(e)

        time.sleep(4)

    def export_data_to_excel_file(self, file_name):
        all_tables = pd.read_html(self.driver.page_source, attrs={"class": "index"})
        df = all_tables[0]
        df.to_excel(file_name)

    def search_on_kandilli_with_selenium(
        self, start_date, end_date, min_depth, max_depth, min_magnitude, max_magnitude, sorting, asc_desc
    ):
        self.driver.get(SEARCH_RECENT_FOR_EVENTS)

        if not start_date or not end_date:
            if self.check_date_time(start_date) and self.check_date_time(end_date):
                from_year, from_month, from_day = start_date.split("-")
                to_year, to_month, to_day = end_date.split("-")
                self.select_from_year(from_year, from_month, from_day)
                self.select_to_year(to_year, to_month, to_day)

        self.set_depth(min_depth, max_depth)
        self.set_magnitude(min_magnitude, max_magnitude)
        self.set_sorting(sorting)
        self.set_asc_desc(asc_desc)
        self.apply_changes()

        timestamp = dt.datetime.now().strftime("%d_%m_%Y")
        data_file_name = "deprem_data_" + timestamp + ".xlsx"
        self.export_data_to_excel_file(data_file_name)


# create main function
if __name__ == "__main__":
    #
    print("Deprem Botu Baslatiliyor...")
    print("Ne yapmak istersiniz?")
    print("1. Sehir ve zamana bağlı arama yap")
    print("2. Detaylı arama yaparak, istenilen veriyi excel dosyasına aktar")

    choose = input("Seciminiz: ")

    if choose == "1":
        with Deprem(is_selenium_active=False) as deprem_bot:
            city = input("Sehir giriniz: ")
            time_interval = input("Zaman araligi giriniz:  (* 90: son 90 dk icindeki depremler)\n")
            deprem_bot.check_city_input(city)
            depremler = deprem_bot.get_data_from_kandilli()
            # extract data is either sending message to telegram or printing to console
            deprem_bot.extract_data(depremler, city, time_interval)

    if choose == "2":
        print(
            "Detaylı arama yapabilmek için, aşağıdaki bilgileri giriniz, boş bırakmak istediğiniz alanları boş bırakınız"
        )

        user_input = input("Tarih aralığı belirlemek istiyor musunuz ? (e/h)")

        start_date = ""
        end_date = ""

        min_depth = ""
        max_depth = ""

        min_magnitude = ""
        max_magnitude = ""

        ordered_by = ""
        sorting_type = ""

        if user_input == "e":
            from_year = input("Baslangic yili: (YYYY)\n")
            from_month = input("Baslangic ayi: (MM) \n")
            from_day = input("Baslangic gunu: (DD)\n")

            start_date = from_year + "-" + from_month + "-" + from_day

            to_year = input("Bitis yili: (YYYY)\n")
            to_month = input("Bitis ayi: (MM)\n")
            to_day = input("Bitis gunu: (DD)\n")

            end_date = to_year + "-" + to_month + "-" + to_day

        user_input = input("Derinlik aralığı belirlemek istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            min_depth = float(input("Minimum derinlik: (km))\n"))
            max_depth = float(input("Maksimum derinlik: (km)\n"))

        user_input = input("Büyüklük aralığı belirlemek istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            min_magnitude = float(input("Minimum buyukluk: (Richter)\n"))
            max_magnitude = float(input("Maksimum buyukluk: (Richter)\n"))

        user_input = input("Siralamak istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            ordered_by = input("Siralanma kriteri: *(Origin Time UTC, Longitude, Latitude, Magnitude, Depth)*\n")
            sorting_type = input("Siralama tipi: *(Ascending, Descending)*\n")

        with Deprem(is_selenium_active=True) as deprem_bot:
            dep = deprem_bot.search_on_kandilli_with_selenium(
                start_date, end_date, min_depth, max_depth, min_magnitude, max_magnitude, ordered_by, sorting_type
            )
