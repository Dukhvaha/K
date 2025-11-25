from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.keyboards import get_main_keyboard

router = Router()


@router.message(Command('start'))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "🎬 <b>Добро пожаловать в бота для поиска фильмов!</b>\n\n"
        "Я помогу вам найти и посмотреть фильмы.\n\n"
        "<b>Доступные команды:</b>\n"
        "/film <название> - найти фильм\n"
        "/search <название> - альтернативный поиск\n"
        "/random - случайный фильм\n"
        "/help - справка\n\n"
        "Используйте кнопки ниже для быстрого доступа!"
    )
    
    keyboard = get_main_keyboard()
    await message.answer(
        welcome_text,
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
