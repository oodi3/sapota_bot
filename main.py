import os
import time
import random

import yt_dlp
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

from res import response

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Token is not set in environment variables")

SAVE_DIR = 'downloads'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Download Video", callback_data='download_video'),
            InlineKeyboardButton("Post Video", callback_data='post_video')
        ]]
    )
    await update.message.reply_text(
        "Hi! How can I help you?", reply_markup=keyboard
    )


async def handle_download_video(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send me the video or playlist link you want to download")
    context.user_data['action'] = 'download_video'


async def handle_post_video(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send me the video you want to post and specify the posting time and interval.")
    context.user_data['action'] = 'post_video'


async def process_message(update: Update, context: CallbackContext) -> None:
    user_action = context.user_data.get('action')
    if user_action == 'download_video':
        await process_video_download(update.message)
    elif user_action == 'post_video':
        await process_post_video(update.message, context)
    else:
        random_response = random.choice(response)
        await update.message.reply_text(random_response)


async def process_video_download(message) -> None:
    url = message.text
    try:
        await message.reply_text("Downloading video(s)...")
        download_videos(url)
        await message.reply_text("Download completed! 😊 Your video(s) are saved locally.")
    except Exception as e:
        await message.reply_text(f"Failed to download video(s). 😿 Error: {e}")


def download_videos(url, output_dir=SAVE_DIR) -> list:
    start_timer = time.time()

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

    end_timer = time.time() - start_timer
    print(f"Time taken: {end_timer:.2f} seconds")

    return downloaded_files


async def process_post_video(message, context):
    pass


application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_download_video, pattern='download_video'))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

print("Bot is working...")
application.run_polling()
