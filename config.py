import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "notes.db")
FERNET_KEY = os.getenv("FERNET_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Create a .env file and add your Telegram bot token.")

if not FERNET_KEY:
    raise ValueError("FERNET_KEY is not set. Generate it and add it to your .env file.")