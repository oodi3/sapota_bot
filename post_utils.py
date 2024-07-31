import asyncio
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ContextTypes

load_dotenv()

POST_CHANNEL_ID = os.getenv('POST_CHANNEL_ID')

if POST_CHANNEL_ID is None:
    raise ValueError("POST_CHANNEL_ID is not set. Please check your .env file.")

SAVE_DIR = 'downloads'


async def show_intervals(update: Update, context: CallbackContext) -> None:
    intervals = [1, 2, 4, 8, 12, 24]  # Интервалы в часах
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{interval} hours", callback_data=f"select_interval_{interval}") for interval in
         intervals]
    ])
    await update.callback_query.message.reply_text("Select interval:", reply_markup=keyboard)


async def interval_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    interval = int(query.data.split('_')[-1])
    context.user_data['post_interval'] = interval
    selected_date = context.user_data.get('post_date', 'not set')
    await query.edit_message_text(
        text=f"Selected interval: {interval} hours\nPosting will start on {selected_date}.\nConfirm?"
    )
    context.user_data['action'] = 'confirm_posting'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data='confirm_posting')],
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ])
    await query.message.reply_text("Confirm your selection:", reply_markup=keyboard)


async def confirm_posting(update: Update, context: CallbackContext) -> None:
    print(f"Loaded to chat id: {POST_CHANNEL_ID}")  # Отладочное сообщение
    await process_post_videos(context)


async def process_post_videos(context: CallbackContext) -> None:
    post_date = context.user_data.get('post_date', 'not set')
    interval = context.user_data['post_interval']
    files = sorted(os.listdir(SAVE_DIR))

    for file in files:
        if file.endswith(".mp4"):
            file_path = os.path.join(SAVE_DIR, file)
            try:
                with open(file_path, 'rb') as video_file:
                    await context.bot.send_video(chat_id=POST_CHANNEL_ID, video=video_file)
                    await context.bot.send_message(chat_id=POST_CHANNEL_ID, text=f"Posted video: {file}")
                await asyncio.sleep(interval * 3600)
            except Exception as e:
                print(f"Failed to post video {file}: {e}")
                try:
                    await context.bot.send_message(chat_id=POST_CHANNEL_ID, text=f"Failed to post video {file}: {e}")
                except Exception as inner_e:
                    print(f"Failed to send error message: {inner_e}")
