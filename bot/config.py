import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/reminders.db")
BOT_NAME = "Напоминалкин"
