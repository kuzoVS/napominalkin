from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")
        ],
        [
            InlineKeyboardButton(text="👤 Напомнить другому", callback_data="remind_other")
        ],
        [
            InlineKeyboardButton(text="🔁 Ежедневное напоминание", callback_data="daily_reminder")
        ],
        [
            InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")
        ]
    ])
    return keyboard


def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ]
    ])
    return keyboard


def get_reminders_keyboard(reminders):
    buttons = []
    
    for reminder in reminders:
        reminder_id = reminder[0]
        text = reminder[3]
        remind_at = reminder[4]
        
        display_text = text[:30] + "..." if len(text) > 30 else text
        
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {display_text}",
                callback_data=f"delete_reminder_{reminder_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
        ]
    ])
    return keyboard


def get_date_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="set_today"),
            InlineKeyboardButton(text="📅 Завтра", callback_data="set_tomorrow")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ]
    ])
    return keyboard


def get_time_keyboard(is_today=False):
    buttons = []
    if is_today:
        buttons.append([
            InlineKeyboardButton(text="⏰ Через 15 минут", callback_data="set_15min")
        ])
    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
