import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_TOKEN
from bot.handlers import start, film, help, random
from bot.middlewares.database import DatabaseMiddleware
from database.connection import init_db


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Инициализация БД
    await init_db()
    logger.info("Database initialized")

    # Создание бота и диспетчера
    bot = Bot(
        token=API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Регистрация middleware
    dp.message.middleware(DatabaseMiddleware())

    # Регистрация роутеров (порядок важен - более специфичные первыми)
    from bot.handlers import text
    dp.include_router(start.router)
    dp.include_router(film.router)
    dp.include_router(random.router)
    dp.include_router(help.router)
    dp.include_router(text.router)  # Текстовые обработчики последними

    # Удаление вебхука и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())