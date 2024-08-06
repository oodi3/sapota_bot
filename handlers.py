import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from download_utils import process_video_download
from upload_utils import process_post_videos
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


# NEED TEST
async def get_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    print(f"Received request in chat ID: {chat_id}")
    await update.message.reply_text(f"Your channel ID is {chat_id}")


async def handle_download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send me the video or playlist link you want to download")
    context.user_data['action'] = 'download_video'


async def handle_post_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Select the start date for posting:")
    context.user_data['action'] = 'post_video'


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_action = context.user_data.get('action')
    if user_action == 'download_video':
        await process_video_download(update.message)
    elif user_action == 'post_video':
        message_text = update.message.text.strip()
        caption = message_text if message_text else None
        await process_post_videos(caption)
    else:
        random_response = random.choice(response)
        await update.message.reply_text(random_response)
