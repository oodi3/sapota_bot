import os
import time
import random

import telebot
from telebot import types
from res import response
import yt_dlp

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


@bot.callback_query_handler(func=lambda call: call.data == 'download_video')
def handle_download_video(call):
    bot.send_message(call.message.chat.id, "Send me the video or playlist link you want to download")
    bot.register_next_step_handler(call.message, process_video_download)


def process_video_download(message):
    url = message.text
    try:
        bot.send_message(message.chat.id, "Downloading video(s)... ")
        video_paths = download_videos(url)

        bot.send_message(message.chat.id, "Download completed! 😊 Your video(s) are saved locally.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Failed to download video(s). 😿 Error: {e}")


def download_videos(url, output_dir=SAVE_DIR):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'noplaylist': False,
        # launch video converter ffmpeg :
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print("Video downloaded successfully!")

    downloaded_files = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            downloaded_files.append(os.path.join(root, file))
    return downloaded_files


@bot.message_handler()
def echo(message):
    random_response = random.choice(response)
    bot.send_message(message.chat.id, random_response)


print("Bot is working...")
bot.polling()
