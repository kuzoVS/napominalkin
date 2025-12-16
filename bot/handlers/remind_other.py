from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.states.reminder_states import RemindOtherStates
from bot.keyboards.menu import get_cancel_keyboard, get_back_keyboard, get_main_menu
from bot.services.reminder_service import (
    create_reminder_for_user,
    parse_datetime,
    validate_datetime
)

router = Router()


@router.callback_query(F.data == "remind_other")
async def start_remind_other(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RemindOtherStates.waiting_for_username)
    
    text = (
        "<b>👤 Напомнить другому</b>\n\n"
        "<i>Укажи @username или user_id получателя:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.message(RemindOtherStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    username_or_id = message.text.strip()
    
    target_user_id = None
    
    try:
        target_user_id = int(username_or_id)
    except ValueError:
        if username_or_id.startswith("@"):
            await state.update_data(target_username=username_or_id)
        else:
            await message.answer(
                "<b>❌ Неверный формат!</b>\n\n"
                "<i>Укажи @username или числовой user_id</i>",
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )
            return
    
    if target_user_id:
        await state.update_data(target_user_id=target_user_id)
    
    await state.set_state(RemindOtherStates.waiting_for_text)
    
    text = (
        "<b>💬 Напиши текст напоминания</b>\n\n"
        "<i>Что нужно напомнить?</i>"
    )
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(RemindOtherStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(RemindOtherStates.waiting_for_date)
    
    text = (
        "<b>📅 Укажи дату</b>\n\n"
        "<i>Формат: YYYY-MM-DD</i>\n"
        "<i>Например: 2025-12-25</i>"
    )
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(RemindOtherStates.waiting_for_date)
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
    await state.set_state(RemindOtherStates.waiting_for_time)
    
    text = (
        "<b>🕐 Укажи время</b>\n\n"
        "<i>Формат: HH:MM</i>\n"
        "<i>Например: 14:30</i>"
    )
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(RemindOtherStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    data = await state.get_data()
    
    date_str = data.get("date")
    reminder_text = data.get("text")
    target_user_id = data.get("target_user_id")
    target_username = data.get("target_username")
    
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
    
    if target_username and not target_user_id:
        await message.answer(
            "<b>⚠️ Не удалось найти пользователя по username</b>\n\n"
            "<i>Используй числовой user_id для надежности</i>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    if not target_user_id:
        await message.answer(
            "<b>❌ Ошибка: не указан получатель</b>",
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
        user_id=target_user_id,
        text=reminder_text,
        remind_at=remind_at,
        sender_id=message.from_user.id
    )
    
    await state.clear()
    
    text = (
        "<b>✅ Напоминание создано!</b>\n\n"
        f"<i>Получатель:</i> {target_username or f'ID: {target_user_id}'}\n"
        f"<i>Текст:</i> {reminder_text}\n"
        f"<i>Дата и время:</i> <code>{date_str} {time_str}</code>"
    )
    
    await message.answer(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
