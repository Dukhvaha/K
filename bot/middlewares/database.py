from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.connection import get_db_session


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для предоставления сессии БД в обработчики"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with get_db_session() as session:
            data['db_session'] = session
            return await handler(event, data)



