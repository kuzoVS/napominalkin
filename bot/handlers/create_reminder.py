from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import pytz
from bot.config import TIMEZONE

from bot.states.reminder_states import CreateReminderStates
from bot.keyboards.menu import get_cancel_keyboard, get_back_keyboard, get_main_menu, get_date_keyboard, get_time_keyboard
from bot.services.reminder_service import (
    create_reminder_for_user,
    parse_datetime,
    validate_datetime
)

moscow_tz = pytz.timezone(TIMEZONE)

router = Router()


@router.callback_query(F.data == "create_reminder")
async def start_create_reminder(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateReminderStates.waiting_for_text)
    
    text = (
        "<b>➕ Создать напоминание</b>\n\n"
        "<i>Напиши текст напоминания:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(CreateReminderStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(CreateReminderStates.waiting_for_date)
    
    text = (
        "<b>📅 Укажи дату</b>\n\n"
        "<i>Формат: YYYY-MM-DD</i>\n"
        "<i>Например: 2025-12-25</i>\n\n"
        "<i>Или нажми кнопку:</i>"
    )
    
    await message.answer(text, reply_markup=get_date_keyboard(), parse_mode="HTML")


@router.message(CreateReminderStates.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    date_str = message.text.strip()
    
    try:
        parts = date_str.split("-")
        if len(parts) != 3 or len(parts[0]) != 4:
            raise ValueError
        int(parts[0])
        int(parts[1])
        int(parts[2])
    except (ValueError, IndexError):
        await message.answer(
            "<b>❌ Неверный формат даты!</b>\n\n"
            "<i>Используй формат: YYYY-MM-DD</i>\n"
            "<i>Например: 2025-12-25</i>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(date=date_str)
    await state.set_state(CreateReminderStates.waiting_for_time)
    
    now_moscow = datetime.now(moscow_tz)
    today_str = now_moscow.strftime("%Y-%m-%d")
    is_today = (date_str == today_str)
    
    text = (
        "<b>🕐 Укажи время</b>\n\n"
        "<i>Формат: HH:MM</i>\n"
        "<i>Например: 14:30</i>"
    )
    
    if is_today:
        text += "\n\n<i>Или нажми кнопку:</i>"
    
    await message.answer(text, reply_markup=get_time_keyboard(is_today=is_today), parse_mode="HTML")


@router.message(CreateReminderStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    data = await state.get_data()
    
    date_str = data.get("date")
    reminder_text = data.get("text")
    
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError
    except (ValueError, IndexError):
        await message.answer(
            "<b>❌ Неверный формат времени!</b>\n\n"
            "<i>Используй формат: HH:MM</i>\n"
            "<i>Например: 14:30</i>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    if not validate_datetime(date_str, time_str):
        await message.answer(
            "<b>❌ Дата и время должны быть в будущем!</b>\n\n"
            "<i>Попробуй снова:</i>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    remind_at = parse_datetime(date_str, time_str)
    reminder_id = create_reminder_for_user(
        user_id=message.from_user.id,
        text=reminder_text,
        remind_at=remind_at
    )
    
    await state.clear()
    
    text = (
        "<b>✅ Напоминание создано!</b>\n\n"
        f"<i>Текст:</i> {reminder_text}\n"
        f"<i>Дата и время:</i> <code>{date_str} {time_str}</code>"
    )
    
    await message.answer(text, reply_markup=get_back_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "set_today")
async def set_today(callback: CallbackQuery, state: FSMContext):
    now_moscow = datetime.now(moscow_tz)
    today_str = now_moscow.strftime("%Y-%m-%d")
    
    await state.update_data(date=today_str)
    await state.set_state(CreateReminderStates.waiting_for_time)
    
    text = (
        "<b>🕐 Укажи время</b>\n\n"
        f"<i>Дата установлена: <code>{today_str}</code></i>\n\n"
        "<i>Формат: HH:MM</i>\n"
        "<i>Например: 14:30</i>\n\n"
        "<i>Или нажми кнопку:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_time_keyboard(is_today=True), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "set_tomorrow")
async def set_tomorrow(callback: CallbackQuery, state: FSMContext):
    now_moscow = datetime.now(moscow_tz)
    tomorrow = now_moscow + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    await state.update_data(date=tomorrow_str)
    await state.set_state(CreateReminderStates.waiting_for_time)
    
    text = (
        "<b>🕐 Укажи время</b>\n\n"
        f"<i>Дата установлена: <code>{tomorrow_str}</code></i>\n\n"
        "<i>Формат: HH:MM</i>\n"
        "<i>Например: 14:30</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_time_keyboard(is_today=False), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "set_15min")
async def set_15min(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date_str = data.get("date")
    reminder_text = data.get("text")
    
    if not date_str:
        await callback.answer("Сначала укажи дату!", show_alert=True)
        return
    
    now_moscow = datetime.now(moscow_tz)
    remind_at = now_moscow + timedelta(minutes=15)
    
    date_from_state = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = now_moscow.date()
    
    if date_from_state == today:
        remind_at_str = remind_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        remind_at = moscow_tz.localize(datetime.combine(date_from_state, remind_at.time()))
        remind_at_str = remind_at.strftime("%Y-%m-%d %H:%M:%S")
    
    reminder_id = create_reminder_for_user(
        user_id=callback.from_user.id,
        text=reminder_text,
        remind_at=remind_at_str
    )
    
    await state.clear()
    
    display_date = remind_at.strftime("%Y-%m-%d")
    display_time = remind_at.strftime("%H:%M")
    
    text = (
        "<b>✅ Напоминание создано!</b>\n\n"
        f"<i>Текст:</i> {reminder_text}\n"
        f"<i>Дата и время:</i> <code>{display_date} {display_time}</code>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = (
        "<b>❌ Создание отменено</b>\n\n"
        "<i>Выбери действие:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()
