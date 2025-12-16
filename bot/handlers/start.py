from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.menu import get_main_menu, get_back_keyboard
from bot.services.user_service import register_user

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    text = (
        "<b>💡 Привет! Я Напоминалкин</b>\n\n"
        "Я помогу тебе не забывать о важных делах!\n\n"
        "<i>Выбери действие:</i>"
    )
    
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = (
        "<b>💡 Главное меню</b>\n\n"
        "<i>Выбери действие:</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()
