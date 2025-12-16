import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bot.config import TIMEZONE
from bot.services.reminder_service import (
    get_reminders_to_send,
    schedule_next_daily
)
from bot.database.models import get_user, delete_reminder

logger = logging.getLogger(__name__)

bot_instance = None


def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot


async def check_and_send_reminders():
    if not bot_instance:
        logger.warning("Bot instance not set")
        return
    
    reminders = get_reminders_to_send()
    
    if not reminders:
        return
    
    logger.info(f"Found {len(reminders)} reminders to send")
    
    for reminder in reminders:
        reminder_id = reminder[0]
        user_id = reminder[1]
        sender_id = reminder[2]
        text = reminder[3]
        is_daily = reminder[5]
        
        try:
            sender_info = ""
            if sender_id:
                sender = get_user(sender_id)
                if sender:
                    sender_username = sender[1]
                    sender_first_name = sender[2]
                    if sender_username:
                        sender_info = f"\n\n<i>От:</i> @{sender_username}"
                    elif sender_first_name:
                        sender_info = f"\n\n<i>От:</i> {sender_first_name}"
                    else:
                        sender_info = "\n\n<i>От: пользователя</i>"
                else:
                    sender_info = "\n\n<i>От: пользователя</i>"
            
            message_text = (
                f"<b>💡 Напоминание!</b>\n\n"
                f"{text}"
                f"{sender_info}"
            )
            
            await bot_instance.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent reminder {reminder_id} to user {user_id}")
            
            if is_daily:
                schedule_next_daily(reminder_id)
                logger.info(f"Scheduled next daily reminder {reminder_id}")
            else:
                delete_reminder(reminder_id, user_id)
                logger.info(f"Deleted one-time reminder {reminder_id}")
            
        except TelegramForbiddenError:
            logger.warning(f"User {user_id} blocked the bot")
            
            if sender_id:
                try:
                    error_message = (
                        f"<b>⚠️ Ошибка доставки</b>\n\n"
                        f"<i>Не удалось доставить напоминание пользователю</i>\n"
                        f"<i>Возможно, пользователь заблокировал бота</i>"
                    )
                    await bot_instance.send_message(
                        chat_id=sender_id,
                        text=error_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify sender {sender_id}: {e}")
            
            delete_reminder(reminder_id, user_id)
            
        except TelegramBadRequest as e:
            logger.error(f"Bad request for reminder {reminder_id}: {e}")
            delete_reminder(reminder_id, user_id)
            
        except Exception as e:
            logger.error(f"Error sending reminder {reminder_id}: {e}")


def start_scheduler(bot: Bot):
    set_bot(bot)
    
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    
    scheduler.add_job(
        check_and_send_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="check_reminders",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    
    return scheduler
