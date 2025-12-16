from datetime import datetime, timedelta
import pytz
from bot.config import TIMEZONE
from bot.database.models import (
    create_reminder,
    get_user_reminders,
    get_due_reminders,
    delete_reminder,
    deactivate_reminder,
    update_daily_reminder
)

moscow_tz = pytz.timezone(TIMEZONE)


def create_reminder_for_user(user_id, text, remind_at, sender_id=None, is_daily=False):
    return create_reminder(user_id, text, remind_at, sender_id, is_daily)


def get_reminders_for_user(user_id):
    return get_user_reminders(user_id, active_only=True)


def remove_reminder(reminder_id, user_id):
    return delete_reminder(reminder_id, user_id)


def disable_reminder(reminder_id, user_id):
    return deactivate_reminder(reminder_id, user_id)


def get_reminders_to_send():
    return get_due_reminders()


def schedule_next_daily(reminder_id):
    update_daily_reminder(reminder_id)


def parse_datetime(date_str, time_str):
    try:
        datetime_str = f"{date_str} {time_str}"
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        dt = moscow_tz.localize(dt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        now_moscow = datetime.now(moscow_tz)
        today = now_moscow.date()
        dt = moscow_tz.localize(datetime.combine(today, time_obj))
        
        if dt < now_moscow:
            dt = dt + timedelta(days=1)
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def validate_datetime(date_str, time_str):
    dt_str = parse_datetime(date_str, time_str)
    if not dt_str:
        return False
    
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        dt = moscow_tz.localize(dt)
        now_moscow = datetime.now(moscow_tz)
        return dt > now_moscow
    except ValueError:
        return False
