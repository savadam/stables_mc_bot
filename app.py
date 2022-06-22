import os
import telebot
from flask import Flask

TOKEN = os.environ.get('API_TOKEN', None)

telegram_bot = telebot.TeleBot(TOKEN)
telebot_chat_id = '471928485'

telegram_bot.send_message(telebot_chat_id, 'Hello')

app = Flask(__name__)
app.run(os.environ.get('PORT'))