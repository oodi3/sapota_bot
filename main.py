import os
import asyncio
import datetime
import calendar
import random
import time

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
    ContextTypes,
    filters,
)

from res import response

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
POST_CHANNEL_ID = os.getenv('POST_CHANNEL_ID')

if not TOKEN:
    raise ValueError("Token is not set in environment variables")
if not POST_CHANNEL_ID:
    raise ValueError("Post channel ID is not set in environment variables")

SAVE_DIR = 'downloads'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


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


async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, current_date: datetime.date) -> None:
    keyboard = InlineKeyboardMarkup(generate_calendar(current_date))
    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text(text="Select date:", reply_markup=keyboard)
    else:
        await update.message.reply_text("Select date:", reply_markup=keyboard)


def generate_calendar(date: datetime.date) -> list:
    keyboard = []
    today = datetime.date.today()
    current_date = date

    # Add month navigation buttons
    prev_callback = f"prev_{current_date.year}_{current_date.month}"
    next_callback = f"next_{current_date.year}_{current_date.month}"
    keyboard.append([
        InlineKeyboardButton("<", callback_data=prev_callback),
        InlineKeyboardButton(f"{calendar.month_name[current_date.month]} {current_date.year}", callback_data="ignore"),
        InlineKeyboardButton(">", callback_data=next_callback)
    ])

    # Debug output
    print(f"Month navigation callbacks: {prev_callback}, {next_callback}")

    # Add days of the month & today button
    month_calendar = calendar.monthcalendar(current_date.year, current_date.month)
    for week in month_calendar:
        week_buttons = []
        for day in week:
            if day == 0:
                week_buttons.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                day_callback = f"select_{current_date.year}_{current_date.month}_{day}"
                week_buttons.append(InlineKeyboardButton(str(day), callback_data=day_callback))
        keyboard.append(week_buttons)

    today_callback = f"select_{today.year}_{today.month}_{today.day}"
    keyboard.append([
        InlineKeyboardButton("Today", callback_data=today_callback)
    ])

    return keyboard


async def calendar_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data.split('_')

    print(f"Callback data received: {data}")  # Отладочное сообщение

    if len(data) == 4 and data[0] == "select":
        action = data[0]
        year, month, day = int(data[1]), int(data[2]), int(data[3])
        selected_date = datetime.date(year, month, day)
        context.user_data['post_date'] = selected_date
        await query.edit_message_text(text=f"Selected date: {selected_date}\nSelect the posting interval:")
        await show_intervals(update, context)
    elif len(data) == 3 and data[0] == "select" and data[1] == "interval":
        await interval_selection(update, context)  # Обработка выбора интервала
    else:
        print(f"Error parsing callback data: {query.data}")  # Отладочное сообщение
        await query.edit_message_text(text="Callback data for date selection is incomplete")


async def show_intervals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intervals = [1, 2, 4, 8, 12, 24]  # Интервалы в часах
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{interval} hours", callback_data=f"select_interval_{interval}") for interval in
         intervals]
    ])
    await update.callback_query.message.reply_text("Select interval:", reply_markup=keyboard)


async def interval_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    interval = int(query.data.split('_')[-1])
    context.user_data['post_interval'] = interval
    selected_date = context.user_data['post_date']
    await query.edit_message_text(
        text=f"Selected interval: {interval} hours\nPosting will start on {selected_date}.\nConfirm?")
    context.user_data['action'] = 'confirm_posting'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data='confirm_posting')],
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ])
    await query.message.reply_text("Confirm your selection:", reply_markup=keyboard)


async def confirm_posting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Posting confirmed! Starting to post videos...")
    await process_post_videos(context)


async def process_post_videos(context: ContextTypes.DEFAULT_TYPE) -> None:
    post_date = context.user_data['post_date']
    interval = context.user_data['post_interval']
    files = sorted(os.listdir(SAVE_DIR))

    for file in files:
        if file.endswith(".mp4"):
            file_path = os.path.join(SAVE_DIR, file)
            try:
                await context.bot.send_video(chat_id=POST_CHANNEL_ID, video=open(file_path, 'rb'))
                await context.bot.send_message(chat_id=POST_CHANNEL_ID, text=f"Posted video: {file}")
                await asyncio.sleep(interval * 3600)
            except Exception as e:
                print(f"Failed to post video {file}: {e}")
                await context.bot.send_message(chat_id=POST_CHANNEL_ID, text=f"Failed to post video {file}: {e}")


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def process_post_video(message, context) -> None:
    await message.reply_text("You can now select a date and interval for posting videos.")
    await handle_post_video(message, context)


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


application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_download_video, pattern='download_video'))
application.add_handler(CallbackQueryHandler(handle_post_video, pattern='post_video'))
application.add_handler(CallbackQueryHandler(calendar_navigation, pattern='^(prev|next|select)'))
application.add_handler(CallbackQueryHandler(interval_selection, pattern='select_interval_'))
application.add_handler(CallbackQueryHandler(confirm_posting, pattern='confirm_posting'))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

print("Bot is working...")
application.run_polling()
