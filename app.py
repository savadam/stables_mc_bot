import os
import telebot

# TOKEN = os.environ.get('API_TOKEN', None)
TOKEN = '5513863043:AAG5b6vY-GcTNrXyfFvGf_notlv4js2wjds'

telegram_bot = telebot.TeleBot(TOKEN)
telebot_chat_id = '471928485'

telegram_bot.send_message(telebot_chat_id, 'Hello')