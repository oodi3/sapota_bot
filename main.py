import os

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from post_utils import interval_selection, confirm_posting
from calendar_utils import calendar_navigation
from handlers import (
    start,
    handle_download_video,
    handle_post_video,
    process_message,
)

load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Token is not set in environment variables")


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
