import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.db import Database
from app.handlers.notes import router
from config import BOT_TOKEN, DATABASE_PATH


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    db = Database(DATABASE_PATH)
    db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(db=db)

    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())