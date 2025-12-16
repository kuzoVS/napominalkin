import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.scheduler.reminder_scheduler import start_scheduler

from bot.handlers import (
    start,
    create_reminder,
    remind_other,
    daily_reminder,
    my_reminders
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    dp.include_router(start.router)
    dp.include_router(create_reminder.router)
    dp.include_router(remind_other.router)
    dp.include_router(daily_reminder.router)
    dp.include_router(my_reminders.router)
    
    logger.info("Starting scheduler...")
    scheduler = start_scheduler(bot)
    
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
