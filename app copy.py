import os
from flask import Flask
import requests, json
from time import sleep
import schedule

# TOKEN = os.environ.get('API_TOKEN', None)
TOKEN = '5513863043:AAG5b6vY-GcTNrXyfFvGf_notlv4js2wjds'

import telebot
telegram_bot = telebot.TeleBot(TOKEN)
telebot_chat_id = '471928485'

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B'][magnitude])

stables = ['tether', 'usd-coin', 'binance-usd', 'dai']

app = Flask(__name__)

@app.route("/")
def home():
    def task():
        for coin in stables:
            url = requests.get("https://api.coingecko.com/api/v3/coins/" + coin)
            data = json.loads(url.text)
            output_string = "Coin: " + str(data['symbol']).upper() + '\n' +\
                "Current MC: " + human_format(data['market_data']['market_cap']['usd']) + '\n' +\
                "MC Change in 24hr: " + human_format(data['market_data']['market_cap_change_24h']) + '\n' +\
                "MC Change in 24hr(%): " + human_format(data['market_data']['market_cap_change_percentage_24h']) + '%\n'    
            telegram_bot.send_message(chat_id=telebot_chat_id, text=output_string)

    schedule.every().day.at("07:18").do(task)

    while True:
        schedule.run_pending()
        sleep(5)

app.run(os.environ.get('PORT'))