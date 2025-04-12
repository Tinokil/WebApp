import asyncio
import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()

from aiogram import Dispatcher
from other import get_logger, bot
from database import db
from handlers.commands import router as cmd_router
from handlers.user import router as user_router


dp = Dispatcher()
dp.include_routers(cmd_router, user_router)
logger = get_logger(__name__)


async def on_startup():
    bot_data = await bot.get_me()
    logger.info(f'Бот @{bot_data.username} - {bot_data.full_name} запущен') 


async def on_shutdown():
    logger.info('Бот остановлен')

async def main() -> None:
    try:
        logging.getLogger("aiogram.event").setLevel(logging.WARNING)
        dp.shutdown.register(on_shutdown)
        dp.startup.register(on_startup)
        await db.create_tables()
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f'Ошибка при запуске бота: {e}')


if __name__ == "__main__":
    asyncio.run(main())
    