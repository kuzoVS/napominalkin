from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.reminder_states import DailyReminderStates
from bot.keyboards.menu import get_cancel_keyboard, get_back_keyboard, get_main_menu
from bot.services.reminder_service import (
    create_reminder_for_user,
    parse_time
)

router = Router()


@router.callback_query(F.data == "daily_reminder")
async def start_daily_reminder(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DailyReminderStates.waiting_for_text)
    
    text = (
        "<b>🔁 Ежедневное напоминание</b>\n\n"
        "<i>Напиши текст напоминания:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(DailyReminderStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(DailyReminderStates.waiting_for_time)
    
    text = (
        "<b>🕐 Укажи время</b>\n\n"
        "<i>Формат: HH:MM</i>\n"
        "<i>Например: 09:00</i>\n\n"
        "<i>Напоминание будет приходить каждый день в это время</i>"
    )
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(DailyReminderStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    data = await state.get_data()
    
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
            "<i>Например: 09:00</i>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    remind_at = parse_time(time_str)
    
    if not remind_at:
        await message.answer(
            "<b>❌ Ошибка при обработке времени!</b>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    reminder_id = create_reminder_for_user(
        user_id=message.from_user.id,
        text=reminder_text,
        remind_at=remind_at,
        is_daily=True
    )
    
    await state.clear()
    
    text = (
        "<b>✅ Ежедневное напоминание создано!</b>\n\n"
        f"<i>Текст:</i> {reminder_text}\n"
        f"<i>Время:</i> <code>{time_str}</code>\n\n"
        "<i>Напоминание будет приходить каждый день в это время</i>"
    )
    
    await message.answer(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
