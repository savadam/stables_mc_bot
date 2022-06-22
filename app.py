import os
import telebot

TOKEN = os.environ.get('API_TOKEN', None)

telegram_bot = telebot.TeleBot(TOKEN)
telebot_chat_id = '471928485'

telegram_bot.send_message(telebot_chat_id, 'Hello')