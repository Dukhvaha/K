import logging
from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

from services.zona_parser_service import get_video_url
from services.kinopoisk_service import search_movie_kinopoisk
from bot.file_storage import get_or_upload_video
from database.models import VideoCache
from database.connection import get_db_session

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command('film', 'search'))
async def film_handler(message: Message, bot: Bot):
    """Обработчик команды /film и /search"""
    title = message.text.replace("/film", "").replace("/search", "").strip()

    if not title:
        await message.answer(
            "❌ <b>Использование:</b> /film <название фильма>\n"
            "Пример: /film Матрица"
        )
        return

    # Показываем, что ищем
    search_msg = await message.answer(f"🔍 Ищу: <b>{title}</b>...")

    try:
        # Проверяем кеш в БД
        async with get_db_session() as session:
            cached = await VideoCache.get_by_title(session, title)
            if cached and cached.file_id:
                logger.info(f"Found cached video for: {title}")
                await search_msg.delete()
                await message.answer_video(
                    video=cached.file_id,
                    caption=f"🎬 <b>{cached.title}</b>\n\n{cached.description or ''}",
                    reply_markup=_get_film_keyboard(cached.kinopoisk_id) if cached.kinopoisk_id else None
                )
                return

        # Ищем через Kinopoisk для получения метаданных
        kinopoisk_data = None
        try:
            kinopoisk_data = await search_movie_kinopoisk(title)
            if kinopoisk_data:
                logger.info(f"Found Kinopoisk data for: {title}")
        except Exception as e:
            logger.warning(f"Kinopoisk search failed: {e}")

        # Ищем видео через парсер
        await search_msg.edit_text(f"🔍 Ищу: <b>{title}</b>...\n📥 Ищу видео...")
        video_url = await get_video_url(title)

        if not video_url:
            await search_msg.edit_text(
                f"❌ Фильм <b>{title}</b> не найден.\n"
                "Попробуйте другое название или используйте /random"
            )
            return

        # Загружаем в канал и получаем file_id
        await search_msg.edit_text(f"🔍 Ищу: <b>{title}</b>...\n📤 Загружаю в хранилище...")
        file_id = await get_or_upload_video(bot, video_url, title, kinopoisk_data)

        if not file_id:
            await search_msg.edit_text("❌ Ошибка при загрузке видео. Попробуйте позже.")
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

        # Отправляем пользователю
        await search_msg.delete()
        caption = f"🎬 <b>{kinopoisk_data.get('name', title) if kinopoisk_data else title}</b>"
        if kinopoisk_data and kinopoisk_data.get('description'):
            caption += f"\n\n{kinopoisk_data['description'][:500]}..."
        
        await message.answer_video(
            video=file_id,
            caption=caption,
            reply_markup=_get_film_keyboard(kinopoisk_data.get('id')) if kinopoisk_data else None
        )

    except Exception as e:
        logger.error(f"Error in film_handler: {e}", exc_info=True)
        await search_msg.edit_text(
            f"❌ Произошла ошибка при поиске фильма.\n"
            f"Попробуйте позже или используйте другое название."
        )


def _get_film_keyboard(kinopoisk_id: int | None) -> InlineKeyboardMarkup | None:
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


@router.callback_query(lambda c: c.data.startswith('favorite_'))
async def favorite_handler(callback: CallbackQuery):
    """Обработчик добавления в избранное"""
    # TODO: Реализовать добавление в избранное
    await callback.answer("⭐ Добавлено в избранное!", show_alert=False)

