import os
import requests, json
from telebot import TeleBot, types
from flask import Flask, request
import time
from quickchart import QuickChart

TOKEN = os.environ.get('API_TOKEN', None)
APP_NAME = os.environ.get('APP_NAME', None)

bot = TeleBot(TOKEN)
server = Flask(__name__)

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'Q'][magnitude])

def get_chart(msg, coin):
    try:
        url = requests.get("https://api.coingecko.com/api/v3/coins/" + coin)
        data = json.loads(url.text)

        token_id = data['id']
        symbol = data['symbol']
        token_name = data['name']
        market_cap = human_format(data['market_data']['market_cap']['usd'])
        mc_change = human_format(data['market_data']['market_cap_change_24h'])
        mc_change_perc = human_format(data['market_data']['market_cap_change_percentage_24h'])

        text_to_send = f'*{str(token_name)}* ({str(symbol).upper()})\n\n❇️ *Market Cap*: ${str(market_cap)}\n❇️ *MC Change*(24hr): {str(mc_change)}\n❇️ *% MC Change(24hr)*: {str(mc_change_perc)}%'

        url = requests.get("https://api.coingecko.com/api/v3/coins/" + str(token_id) + "/market_chart?vs_currency=usd&days=7")
        data = json.loads(url.text)['market_caps']

        tstamps = []
        for item in range(0, len(data)):
            ts = int(data[item][0]/1000)
            tstamps.append(str(time.strftime("%b %d %H:%M", time.localtime(ts))))

        mc_data =[]
        for item in range(0, len(data)):
            mc_data.append((data[item][1])/1000000000)

        qc = QuickChart()
        qc.width = 1500
        qc.height = 900

        # Config can be set as a string or as a nested dict
        qc.config = """{
            type: 'line',
            data: {
                labels: """ + str(tstamps[0::2]) + """,
                datasets: [
                {
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: """ + str(mc_data[0::2]) + """,
                    label: '""" + str(token_name) + """ Market Cap in Billions (Last 7 days)',
                    fill: false,
                },
                ],
            },
            options: {
                scales: {
                xAxes: [
                    {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 90,
                    },
                    },
                ],
                },
                title: {
                text: 'fill: false',
                display: false,
                },
            },
        }"""

        bot.send_photo(
            msg.chat.id,
            qc.get_url(),
            caption=text_to_send,
            parse_mode='markdown',
            reply_to_message_id=msg.id
        )

    except:
        bot.send_message(msg.chat.id, '*❌ This currency is not supported or either it is wrong!*', parse_mode='markdown', reply_to_message_id=msg.id)


@bot.message_handler(commands=['start'], chat_types=['private'])
def startPrivate(msg : types.Message):
    bot.send_message(
        msg.chat.id,
        '<b>Welcome Stables MarketCap Update Bot\n\nFormat : /s</b>'.format(msg.from_user.first_name),
        parse_mode='html',
        reply_to_message_id=msg.id,
        disable_web_page_preview=True
    )

@bot.message_handler(func= lambda msg : msg.text.startswith('/s'))
def getPrice(msg):
    if len(msg.text) == 2:
        try:        
            stables = ['tether', 'usd-coin', 'binance-usd']
            text_to_send = '*COIN  |    MC    | 24hr Change*\n------------------------------\n'
            for coin in stables:
                url = requests.get("https://api.coingecko.com/api/v3/coins/" + coin)
                data = json.loads(url.text)

                token_id = data['id']
                symbol = data['symbol']
                token_name = data['name']
                market_cap = human_format(data['market_data']['market_cap']['usd'])
                mc_change = human_format(data['market_data']['market_cap_change_24h'])
                mc_change_perc = human_format(data['market_data']['market_cap_change_percentage_24h'])

                text_to_send = text_to_send + f'*{str(symbol).upper()}* | {str(market_cap)} | {str(mc_change)} ({str(mc_change_perc)}%)\n'

            bot.send_message(
                        msg.chat.id,
                        text_to_send,
                        parse_mode='markdown',
                        reply_to_message_id=msg.id
                    )               

        except:
            bot.send_message(msg.chat.id, '*❌ This currency is not supported or either it is wrong!*', parse_mode='markdown', reply_to_message_id=msg.id)

    elif msg.text == '/s usdt':
        coin = 'tether'
        get_chart(msg, coin)
    elif msg.text == '/s usdc':
        coin = 'usd-coin'
        get_chart(msg, coin)
    elif msg.text == '/s busd':
        coin = 'binance-usd'
        get_chart(msg, coin)
    
    elif msg.text == '/sd':                    
        stables = ['tether', 'usd-coin', 'binance-usd']
        for coin in stables:
            get_chart(msg, coin)

    elif msg.text == '/s help':                    
        bot.send_message(msg.chat.id, '*Supported Commands:\n\n/s : Simple MC Information of all Stables\n\n/sd : Detailed MC Information of all Stables\n\n/s <symbol> : Detailed MC Information of specific Stable Coin.\nExample: /s usdt\n\n[Supported Stable Coins: USDT, USDC, BUSD]*', parse_mode='markdown', reply_to_message_id=msg.id)

            
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/setWebhook")
def webhook():
    if not APP_NAME or not TOKEN:
        return 'Setup TOKEN & URL environment variable from heroku dashboard.'
    bot.remove_webhook()
    bot.set_webhook(url= f'https://{APP_NAME}.herokuapp.com/{TOKEN}')
    return "Webhook Done!", 200

@server.route("/")
def home():
    return "<h1>Server Running!</h1>", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))