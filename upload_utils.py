import os
import logging

from telegram import Bot, InputFile

from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('POST_CHANNEL_ID')
bot = Bot(token=TOKEN)

directory = 'downloads'
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB


def get_file_size(file_path):
    return os.path.getsize(file_path)


async def post_video(file_path, caption=None):
    try:
        with open(file_path, 'rb') as file:
            await bot.send_video(chat_id=CHANNEL_ID, video=InputFile(file), caption=caption)
        logging.info(f'Video posted successfully: {file_path}')
    except Exception as e:
        logging.error(f'Failed to post video: {e}')


async def post_document(file_path, caption=None):
    try:
        with open(file_path, 'rb') as file:
            await bot.send_document(chat_id=CHANNEL_ID, document=InputFile(file), caption=caption)
        logging.info(f'Document posted successfully: {file_path}')
    except Exception as e:
        logging.error(f'Failed to post document: {e}')


async def process_post_videos(caption=None):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            file_size = get_file_size(file_path)
            if file_size > MAX_VIDEO_SIZE:
                await post_document(file_path, caption)
            else:
                await post_video(file_path, caption)
