import datetime
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from calendar_utils import show_calendar
from download_utils import download_videos
from res import response


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Download Video", callback_data='download_video'),
            InlineKeyboardButton("Post Video", callback_data='post_video')
        ]]
    )
    await update.message.reply_text(
        "Hi! How can I help you?", reply_markup=keyboard
    )


async def handle_download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send me the video or playlist link you want to download")
    context.user_data['action'] = 'download_video'


async def handle_post_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Select the start date for posting:")
    await show_calendar(update, context, datetime.date.today())
    context.user_data['action'] = 'post_video'


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_action = context.user_data.get('action')
    if user_action == 'download_video':
        await process_video_download(update.message)
    elif user_action == 'post_video':
        await handle_post_video(update.message, context)
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
