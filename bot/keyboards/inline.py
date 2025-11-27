from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def get_film_keyboard(kinopoisk_id: Optional[int] = None) -> Optional[InlineKeyboardMarkup]:
    """Создает inline-клавиатуру для фильма"""
    if not kinopoisk_id:
        return None
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐ Добавить в избранное",
                callback_data=f"favorite_{kinopoisk_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Открыть на Кинопоиске",
                url=f"https://www.kinopoisk.ru/film/{kinopoisk_id}/"
            )
        ]
    ])
    return keyboard

