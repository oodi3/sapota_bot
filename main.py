import os
import random
import telebot
from telebot import types
from res import response

from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Token is not set in environment variables")

bot = telebot.TeleBot(TOKEN)

SAVE_DIR = 'downloads'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_download_video = types.InlineKeyboardButton(
        "download video", callback_data='download_video'
    )
    btn_upload_video = types.InlineKeyboardButton(
        "post video", callback_data='post_video'
    )
    keyboard.add(btn_download_video, btn_upload_video)
    bot.send_message(
        message.chat.id, f" Hi ! How can I help you ? ", reply_markup=keyboard
    )


@bot.message_handler()
def echo(message):
    random_response = random.choice(response)
    bot.send_message(message.chat.id, random_response)


print("Bot is working...")
bot.polling()
