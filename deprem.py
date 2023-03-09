# Kandilli Rasathanesi ve Deprem Araştırma Enstitüsü'nün
# http://www.koeri.boun.edu.tr/scripts/lasteq.asp adresinden
# son 24 saatte meydana gelen depremlerin içerisinden 
# aranan şehire göre bildirim gönderen script 

import csv
from datetime import datetime, timezone
from io import StringIO
from os import environ

import requests
from bs4 import BeautifulSoup

KANDILLI_URL = 'http://www.koeri.boun.edu.tr/scripts/lasteq.asp'

STELEGRAM_CHAT_ID = environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN')
TIME_INTERVAL = environ.get("CHECK_TIME") # minutes 
CITY_TO_BE_CHECKED = environ.get("CITY_TO_BE_CHECKED")

# get data from kandilli url and parse it
try:
    response = requests.get(KANDILLI_URL)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
except Exception as e:
    print(e)
    exit(1)
    

# sends message to telegram
def send_message(message):
    try: 
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}")
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
        timestamp = datetime.strptime(date_time, '%Y.%m.%d %H:%M:%S').replace(tzinfo=timezone.utc).replace(tzinfo=None)
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
