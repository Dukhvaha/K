import logging
import random
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

from services.kinopoisk_service import get_random_movie
from services.zona_parser_service import get_video_url
from bot.file_storage import get_or_upload_video
from database.models import VideoCache
from database.connection import get_db_session

router = Router()
logger = logging.getLogger(__name__)

# Популярные фильмы для случайного выбора (fallback)
POPULAR_MOVIES = [
    "Матрица", "Интерстеллар", "Начало", "Терминатор", "Чужой",
    "Бегущий по лезвию", "Побег из Шоушенка", "Криминальное чтиво",
    "Форрест Гамп", "Список Шиндлера", "Властелин колец", "Гарри Поттер"
]


@router.message(Command('random'))
async def random_handler(message: Message, bot: Bot):
    """Обработчик команды /random - случайный фильм"""
    await message.answer("🎲 Выбираю случайный фильм...")

    try:
        # Пытаемся получить случайный фильм через Kinopoisk
        kinopoisk_data = None
        try:
            kinopoisk_data = await get_random_movie()
            if kinopoisk_data:
                title = kinopoisk_data.get('name', '')
                logger.info(f"Got random movie from Kinopoisk: {title}")
        except Exception as e:
            logger.warning(f"Kinopoisk random failed: {e}")

        # Если Kinopoisk не сработал, используем fallback
        if not kinopoisk_data:
            title = random.choice(POPULAR_MOVIES)
            logger.info(f"Using fallback random movie: {title}")

        # Проверяем кеш
        async with get_db_session() as session:
            cached = await VideoCache.get_by_title(session, title)
            if cached and cached.file_id:
                logger.info(f"Found cached video for random: {title}")
                await message.answer_video(
                    video=cached.file_id,
                    caption=f"🎲 <b>Случайный фильм:</b> {title}\n\n{cached.description or ''}"
                )
                return

        # Ищем видео
        search_msg = await message.answer(f"🔍 Ищу: <b>{title}</b>...")
        video_url = await get_video_url(title)

        if not video_url:
            # Пробуем другой фильм
            title = random.choice([m for m in POPULAR_MOVIES if m != title])
            await search_msg.edit_text(f"🔍 Ищу: <b>{title}</b>...")
            video_url = await get_video_url(title)

        if not video_url:
            await search_msg.edit_text(
                "❌ Не удалось найти случайный фильм.\n"
                "Попробуйте использовать /film с конкретным названием."
            )
            return

        # Загружаем видео
        await search_msg.edit_text(f"📤 Загружаю: <b>{title}</b>...")
        file_id = await get_or_upload_video(bot, video_url, title, kinopoisk_data)

        if not file_id:
            await search_msg.edit_text("❌ Ошибка при загрузке видео.")
            return

        # Сохраняем в кеш
        async with get_db_session() as session:
            await VideoCache.create_or_update(
                session,
                title=title,
                file_id=file_id,
                video_url=video_url,
                kinopoisk_id=kinopoisk_data.get('id') if kinopoisk_data else None,
                description=kinopoisk_data.get('description') if kinopoisk_data else None
            )
            await session.commit()

        # Отправляем
        await search_msg.delete()
        caption = f"🎲 <b>Случайный фильм:</b> {kinopoisk_data.get('name', title) if kinopoisk_data else title}"
        if kinopoisk_data and kinopoisk_data.get('description'):
            caption += f"\n\n{kinopoisk_data['description'][:500]}..."

        await message.answer_video(
            video=file_id,
            caption=caption
        )

    except Exception as e:
        logger.error(f"Error in random_handler: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при поиске случайного фильма.\n"
            "Попробуйте использовать /film с конкретным названием."
        )


