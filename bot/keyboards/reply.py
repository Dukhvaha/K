from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_keyboard() -> ReplyKeyboardBuilder:
    """Создает главную reply-клавиатуру"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎬 Найти фильм")
    builder.button(text="🎲 Случайный фильм")
    builder.button(text="📖 Справка")
    builder.adjust(2, 1)
    return builder

