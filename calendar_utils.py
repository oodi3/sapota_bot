import datetime

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from post_utils import show_intervals, interval_selection
from utils import generate_calendar


async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, current_date: datetime.date) -> None:
    keyboard = InlineKeyboardMarkup(generate_calendar(current_date))
    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text(text="Select date:", reply_markup=keyboard)
    else:
        await update.message.reply_text("Select date:", reply_markup=keyboard)


async def calendar_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data.split('_')

    if len(data) == 4 and data[0] == "select":
        action = data[0]
        year, month, day = int(data[1]), int(data[2]), int(data[3])
        selected_date = datetime.date(year, month, day)
        context.user_data['post_date'] = selected_date
        await query.edit_message_text(text=f"Selected date: {selected_date}\nSelect the posting interval:")
        await show_intervals(update, context)
    elif len(data) == 3 and data[0] == "select" and data[1] == "interval":
        await interval_selection(update, context)
    else:
        await query.edit_message_text(text="Callback data for date selection is incomplete")
