from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.menu import get_reminders_keyboard, get_back_keyboard, get_main_menu
from bot.services.reminder_service import get_reminders_for_user, remove_reminder

router = Router()


@router.callback_query(F.data == "my_reminders")
async def show_reminders(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = callback.from_user.id
    reminders = get_reminders_for_user(user_id)
    
    if not reminders:
        text = (
            "<b>📋 Мои напоминания</b>\n\n"
            "<i>У тебя пока нет активных напоминаний</i>"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
        await callback.answer()
        return
    
    reminders_text = "<b>📋 Твои напоминания:</b>\n\n"
    
    for i, reminder in enumerate(reminders, 1):
        reminder_id = reminder[0]
        text = reminder[3]
        remind_at = reminder[4]
        is_daily = reminder[5]
        
        date_time = remind_at.split()[0] + " " + remind_at.split()[1][:5] if " " in remind_at else remind_at
        
        daily_mark = " 🔁" if is_daily else ""
        reminders_text += f"{i}. {text}{daily_mark}\n"
        reminders_text += f"   🕐 <code>{date_time}</code>\n\n"
    
    await callback.message.edit_text(
        reminders_text,
        reply_markup=get_reminders_keyboard(reminders),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_reminder_"))
async def delete_reminder(callback: CallbackQuery, state: FSMContext):
    reminder_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    deleted = remove_reminder(reminder_id, user_id)
    
    if deleted:
        text = "<b>✅ Напоминание удалено</b>"
        await callback.answer(text, show_alert=True)
        
        reminders = get_reminders_for_user(user_id)
        
        if not reminders:
            text = (
                "<b>📋 Мои напоминания</b>\n\n"
                "<i>У тебя пока нет активных напоминаний</i>"
            )
            await callback.message.edit_text(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
        else:
            reminders_text = "<b>📋 Твои напоминания:</b>\n\n"
            
            for i, reminder in enumerate(reminders, 1):
                reminder_id = reminder[0]
                text = reminder[3]
                remind_at = reminder[4]
                is_daily = reminder[5]
                
                date_time = remind_at.split()[0] + " " + remind_at.split()[1][:5] if " " in remind_at else remind_at
                
                daily_mark = " 🔁" if is_daily else ""
                reminders_text += f"{i}. {text}{daily_mark}\n"
                reminders_text += f"   🕐 <code>{date_time}</code>\n\n"
            
            await callback.message.edit_text(
                reminders_text,
                reply_markup=get_reminders_keyboard(reminders),
                parse_mode="HTML"
            )
    else:
        text = "<b>❌ Не удалось удалить напоминание</b>"
        await callback.answer(text, show_alert=True)
