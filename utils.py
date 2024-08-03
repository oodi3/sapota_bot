import calendar
import datetime

from telegram import InlineKeyboardButton


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

    # Add days of the month
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

    # Add "Today" button
    today_callback = f"select_{today.year}_{today.month}_{today.day}"
    keyboard.append([
        InlineKeyboardButton("Today", callback_data=today_callback)
    ])
    print(f"Today button callback: {today_callback}")  # Отладочное сообщение

    return keyboard
