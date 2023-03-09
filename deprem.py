# Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü'nün
# http://www.koeri.boun.edu.tr/scripts/lasteq.asp adresinden
# son 24 saatte meydana gelen depremlerin içerisinden
# aranan şehire göre bildirim gönderen script

import csv
from datetime import datetime, timezone
from io import StringIO
from os import environ

import requests
import unidecode
from bs4 import BeautifulSoup

KANDILLI_URL = "http://www.koeri.boun.edu.tr/scripts/lasteq.asp"

TELEGRAM_CHAT_ID = environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = environ.get("TELEGRAM_TOKEN")
TIME_INTERVAL = environ.get("TIME_INTERVAL")  # minutes
CITY_TO_BE_CHECKED = environ.get("CITY_TO_BE_CHECKED")
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

if unidecode.unidecode(CITY_TO_BE_CHECKED.upper()) not in CITIES:
    print("Türkiye'de bulunmayan bir şehir girdiniz veya şehir adını yanlış girdiniz.")
    exit(1)

# convert string input to int
try:
    TIME_INTERVAL = int(TIME_INTERVAL)
except Exception as e:
    print(e)
    exit(1)

# get data from kandilli url and parse it
try:
    response = requests.get(KANDILLI_URL)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
except Exception as e:
    print(e)
    exit(1)


# sends message to telegram
def send_message(message):
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        )
        if response.status_code != 200:
            print("Error while sending message: ", response.status_code)
    except Exception as e:
        print(e)


# find the earthquake pre table
table = soup.find("pre").find(string=True)
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
            message = f"""Tarih/Zaman: {attributes[0]} {attributes[1]}\n\n
                            Şehir: {city}\n\n
                            Derinlik(km): {attributes[4]}\t 
                            MD: {attributes[5]}\t 
                            ML: {attributes[6]}\t 
                            Mw: {attributes[7]}\n\n
                            Kaynak: Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü """
            send_message(message)
    except Exception as e:
        print(e)
        continue
