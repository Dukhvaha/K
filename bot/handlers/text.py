from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Text

from bot.handlers import film, random, help

router = Router()


@router.message(Text("🎬 Найти фильм"))
async def find_film_button(message: Message):
    """Обработчик кнопки 'Найти фильм'"""
    await message.answer(
        "🔍 <b>Введите название фильма:</b>\n\n"
        "Или используйте команду /film <название>"
    )


@router.message(Text("🎲 Случайный фильм"))
async def random_film_button(message: Message, bot: Bot):
    """Обработчик кнопки 'Случайный фильм'"""
    # Импортируем обработчик напрямую
    from bot.handlers.random import random_handler
    await random_handler(message, bot)


@router.message(Text("📖 Справка"))
async def help_button(message: Message):
    """Обработчик кнопки 'Справка'"""
    # Импортируем обработчик напрямую
    from bot.handlers.help import help_handler
    await help_handler(message)


@router.message()
async def text_handler(message: Message, bot: Bot):
    """Обработчик произвольного текста - пытаемся найти фильм"""
    if not message.text:
        return
        
    text = message.text.strip()
    
    # Игнорируем команды
    if text.startswith('/'):
        return
    
    # Если текст похож на запрос фильма (больше 2 символов)
    if len(text) > 2:
        # Вызываем обработчик напрямую
        from bot.handlers.film import film_handler
        # Создаем копию сообщения с командой
        message.text = f"/film {text}"
        await film_handler(message, bot)

