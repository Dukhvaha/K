import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from aiogram import Bot
from aiogram.types import FSInputFile

from services.downloader import download_video
from config import CHANNEL_ID
from database.models import VideoCache
from database.connection import get_db_session

logger = logging.getLogger(__name__)


async def get_or_upload_video(
    bot: Bot,
    video_url: str,
    title: str,
    kinopoisk_data: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Получает file_id из кеша или загружает видео в канал.
    
    Args:
        bot: Экземпляр бота
        video_url: URL видео для загрузки
        title: Название фильма
        kinopoisk_data: Дополнительные данные из Kinopoisk
        
    Returns:
        file_id или None при ошибке
    """
    try:
        # Проверяем кеш по URL
        async with get_db_session() as session:
            cached = await VideoCache.get_by_url(session, video_url)
            if cached and cached.file_id:
                logger.info(f"Found cached file_id for URL: {video_url[:50]}...")
                return cached.file_id

        # Если нет в кеше, загружаем
        logger.info(f"Uploading video to channel: {title}")
        
        # Создаем временный файл
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / f"video_{os.getpid()}.mp4"
        
        try:
            # Скачиваем видео
            path = await download_video(video_url, str(temp_file))
            
            # Загружаем в канал
            caption = f"🎬 {title}"
            if kinopoisk_data and kinopoisk_data.get('name'):
                caption = f"🎬 {kinopoisk_data['name']}"
            
            message = await bot.send_video(
                chat_id=CHANNEL_ID,
                video=FSInputFile(path),
                caption=caption
            )
            
            file_id = message.video.file_id
            logger.info(f"Successfully uploaded video, file_id: {file_id[:20]}...")
            
            return file_id
            
        finally:
            # Удаляем временный файл
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temp file: {e}")
                    
    except Exception as e:
        logger.error(f"Error in get_or_upload_video: {e}", exc_info=True)
        return None
