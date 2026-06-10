import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.db import Database
from app.handlers.notes import router
from app.middlewares import RateLimitMiddleware
from config import BOT_TOKEN, DATABASE_PATH


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    db = Database(DATABASE_PATH)
    db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(db=db)

    dp.message.middleware(RateLimitMiddleware(limit_seconds=3))
    dp.include_router(router)

    logging.info("Bot started successfully.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())