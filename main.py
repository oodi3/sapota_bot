import os
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from handlers import (
    start,
    get_channel_id,
    handle_download_video,
    handle_post_video,
    process_message,
)

from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Token is not set in environment variables")


application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("get_channel_id", get_channel_id))  # NEED TEST
application.add_handler(CallbackQueryHandler(handle_download_video, pattern='download_video'))
application.add_handler(CallbackQueryHandler(handle_post_video, pattern='post_video'))

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))


logging.info("Bot start working 😊")

application.run_polling()
