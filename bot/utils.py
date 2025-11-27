"""Утилиты для бота"""

from html import escape


def escape_html(text: str) -> str:
    """Экранирует HTML символы в тексте"""
    if not text:
        return ""
    return escape(str(text), quote=False)

