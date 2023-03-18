# Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü'nün
# http://www.koeri.boun.edu.tr/scripts/lasteq.asp adresinden
# son 24 saatte meydana gelen depremlerin içerisinden
# aranan şehire göre bildirim gönderen ve
# Aynı zamanda detaylı aramak yaparak veri seti indirebileceğiniz bir script

import csv
import datetime as dt
import time
from io import StringIO
from os import environ

import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup

KANDILLI_URL = "http://www.koeri.boun.edu.tr/scripts/lasteq.asp"
SEARCH_RECENT_FOR_EVENTS = "http://sc3.koeri.boun.edu.tr/eqevents/eq_events"
TELEGRAM_CHAT_ID = environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = environ.get("TELEGRAM_TOKEN")
CITY_TO_BE_CHECKED = environ.get("CITY_TO_BE_CHECKED")
TIME_INTERVAL = environ.get("TIME_INTERVAL")

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
        if environ.get("TIME_INTERVAL"):
            self.time_interval = int(environ.get("TIME_INTERVAL"))
        else:
            self.time_interval = 5

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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

    def export_data_to_excel_file(self, source, city="", filter_city=False):
        timestamp = dt.datetime.now().strftime("%d_%m_%Y")

        if filter_city:
            data_file_name = "deprem_data_" + city + "_" + timestamp + ".xlsx"
        else:
            data_file_name = "deprem_data_" + timestamp + ".xlsx"

        try:
            all_tables = pd.read_html(source, attrs={"class": "index"})
            df = all_tables[0]
            if filter_city:
                df = df[df["Yer-Region Name"].str.contains(unidecode.unidecode(city), case=False)]
            df.to_excel(data_file_name)
        except Exception as e:
            print(e)
            exit(1)
        print(f"Deprem verileri {data_file_name} excel dosyasina aktarildi\n ")

    def search_and_filter_on_kandilli(self, from_date, to_date, city):
        resp = self.search_on_kandilli_with_requests(from_date, to_date)
        self.export_data_to_excel_file(source=resp, city=city, filter_city=True)

    def search_on_kandilli_with_requests(
        self,
        start_date,
        end_date,
        min_depth=0,
        max_depth=50,
        min_magnitude=1,
        max_magnitude=7,
        sorting="Origin Time UTC",
        asc_desc="descending",
    ):
        from_year, from_month, from_day = start_date.split("-")
        to_year, to_month, to_day = end_date.split("-")
        # create POST request to get data
        try:
            user_request = requests.post(
                SEARCH_RECENT_FOR_EVENTS,
                data={
                    "MIME Type": "application/x-www-form-urlencoded",
                    "fromTY": from_year,  # 1900-2020
                    "fromTM": from_month,  # 1-12
                    "fromTD": from_day,  # 1-31
                    "toY": to_year,  # 1900-2020
                    "toM": to_month,  # 1-12
                    "toD": to_day,  # 1-31
                    "min_lat": "",  # 35-42
                    "max_lat": "",
                    "min_long": "",
                    "max_long": "",
                    "min_depth": min_depth,  # 0-700
                    "max_depth": max_depth,  # 0-700
                    "min_mag": min_magnitude,  # 0-10
                    "max_mag": max_magnitude,  # 0-10
                    "sort": sorting.capitalize(),  # Origin Time UTC, Longitude, Latitude, Magnitude, Depth
                    "desc": asc_desc.lower(),  # ascending or descending
                    "get_events": "true",
                },
            )
            if user_request.status_code == 200:
                return user_request.text
            else:
                print("Kandilli'den veri çekilemedi")
                print(f"Sunucu cevabı: {user_request.status_code}")
        except Exception as e:
            print(e)
            exit(1)


def retrive_data_from_kandilli(city, time_interval):
    with Deprem() as deprem_bot:
        deprem_bot.check_city_input(city)
        depremler = deprem_bot.get_data_from_kandilli()
        # extract data is either sending message to telegram or printing to console
        deprem_bot.extract_data(depremler, city, time_interval)


if __name__ == "__main__":
    if TELEGRAM_CHAT_ID is not None or TELEGRAM_TOKEN is not None:
        retrive_data_from_kandilli(CITY_TO_BE_CHECKED, TIME_INTERVAL)
        exit(0)

    print("Deprem veri çekme programı başlatılıyor...")
    print("Ne yapmak istersiniz?")
    print("1. Şehir ve zamana bağlı arama ya ve yazdır")
    print("2. Detaylı arama yaparak, istenilen veriyi excel dosyasına aktar")
    print("3. Şehir bazında geçmişe dair verileri excel dosyasına aktar\n")

    choose = input("Seçiminiz: ")

    if choose == "1":
        city = input("Sehir giriniz: ")
        time_interval = input("Zaman araligi giriniz:  (* 90: son 90 dk icindeki depremler)\n")
        retrive_data_from_kandilli(city, time_interval)

    if choose == "2":
        print(
            "Detaylı arama yapabilmek için, aşağıdaki bilgileri giriniz, boş bırakmak istediğiniz alanları boş bırakınız"
        )

        user_input = input("Tarih aralığı belirlemek istiyor musunuz ? (e/h)\n")

        start_date = ""
        end_date = ""

        min_depth = ""
        max_depth = ""

        min_magnitude = ""
        max_magnitude = ""

        ordered_by = ""
        sorting_type = ""

        if user_input == "e":
            start_date = input("Baslangic tarihi: (YYYY-MM-DD)\n")
            end_date = input("Bitis tarihi: (YYYY-MM-DD)\n")

        user_input = input("Derinlik aralığı belirlemek istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            min_depth = float(input("Minimum derinlik: (km))\n"))
            max_depth = float(input("Maksimum derinlik: (km)\n"))

        user_input = input("Büyüklük aralığı belirlemek istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            min_magnitude = float(input("Minimum büyüklük: (Richter)\n"))
            max_magnitude = float(input("Maksimum büyüklük: (Richter)\n"))

        user_input = input("Siralamak istiyor musunuz ? (e/h)\n")

        if user_input == "e":
            order_options = ["Origin Time UTC", "Longitude", "Latitude", "Magnitude", "Depth"]
            ordered_by = input("Siralanma kriteri: *(Origin Time UTC, Longitude, Latitude, Magnitude, Depth)*\n")
            while ordered_by not in order_options:
                print("Hatali giris yaptiniz, lutfen tekrar deneyiniz")
                ordered_by = input("Siralanma kriteri: *(Origin Time UTC, Longitude, Latitude, Magnitude, Depth)*\n")
            sorting_options = ["ascending", "descending"]
            sorting_type = input("Siralama tipi: *(Ascending, Descending)*\n")
            while sorting_type.lower() not in sorting_options:
                print("Hatali giris yaptiniz, lutfen tekrar deneyiniz")
                sorting_type = input("Siralama tipi: *(Ascending, Descending)*\n")

        with Deprem() as deprem_bot:
            source = deprem_bot.search_on_kandilli_with_requests(
                start_date, end_date, min_depth, max_depth, min_magnitude, max_magnitude, ordered_by, sorting_type
            )
            deprem_bot.export_data_to_excel_file(source)

    if choose == "3":
        city = input("Sehir giriniz: ")
        date = input(
            "Geçmişe dair verileri almak için aşağıda belirtildiği şekilde zaman belirtiniz:\n * 3A - Son 3 Aydaki veriler\n * 3Y - Son 3 Yildaki veriler\n * 3D - Son 3 Gunluk veriler\n"
        )

        if date[-1] not in ["A", "Y", "D"]:
            print("Kabul edilen zaman dilimleri: A (Ay), Y (Yil), D (Gun) \n")
            print("Yanlis zaman dilimi belirttiniz, program kapatiliyor...")
            exit(1)

        # take digit part of the string
        time_interval = date[:-1]
        if not time_interval.isdigit():
            print("Zaman dilimi rakam olmalıdır. Program kapatiliyor...")
            exit(1)

        if date[-1] == "A":
            from_date = dt.datetime.now() - dt.timedelta(days=int(time_interval) * 30)
        if date[-1] == "Y":
            from_date = dt.datetime.now() - dt.timedelta(days=int(time_interval) * 365)
        if date[-1] == "D":
            from_date = dt.datetime.now() - dt.timedelta(days=int(time_interval))

        from_date = from_date.strftime("%Y-%m-%d")
        now_date = dt.datetime.now().strftime("%Y-%m-%d")

        with Deprem() as deprem_bot:
            deprem_bot.check_city_input(city)
            deprem_bot.search_and_filter_on_kandilli(from_date, now_date, city)

    if choose not in ["1", "2", "3"]:
        print("Yanlis secim yaptiniz, program kapatiliyor...")
        exit(1)
