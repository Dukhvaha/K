from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards import get_main_keyboard

router = Router()


@router.message(Command('start'))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "Привет, зритель! 👋\n\n"
        "Этот бот создан специально для тебя нашим новостным Telegram-каналом 📽️ KINOLINK!\n\n"
        "🎬 Здесь ты можешь смотреть фильмы и сериалы абсолютно бесплатно.\n\n"
        "Единственное условие — подпишись на наш канал, чтобы открыть доступ и не пропускать новые релизы! 🚀"
    )
    
    keyboard = get_main_keyboard()
    await message.answer(
        welcome_text,
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
