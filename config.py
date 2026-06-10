import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "notes.db")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set. Create .env file and add your Telegram bot token."
    )