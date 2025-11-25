import logging
import aiohttp
import ssl
from typing import Optional

logger = logging.getLogger(__name__)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def download_video(url: str, path: str, timeout: int = 300) -> Optional[str]:
    """
    Скачивает видео по URL и сохраняет в файл
    
    Args:
        url: URL видео для скачивания
        path: Путь для сохранения файла
        timeout: Таймаут в секундах
        
    Returns:
        Путь к сохраненному файлу или None при ошибке
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context),
            timeout=timeout_obj
        ) as session:
            logger.info(f"Downloading video from: {url[:100]}...")
            
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to download video: HTTP {resp.status}")
                    raise Exception(f"Не удалось скачать видео: HTTP {resp.status}")

                # Проверяем размер файла (ограничение 2GB)
                content_length = resp.headers.get('Content-Length')
                if content_length and int(content_length) > 2 * 1024 * 1024 * 1024:
                    logger.error(f"Video file too large: {content_length} bytes")
                    raise Exception("Файл слишком большой (максимум 2GB)")

                data = await resp.read()
                logger.info(f"Downloaded {len(data)} bytes")

            # Сохраняем файл
            with open(path, "wb") as f:
                f.write(data)

            logger.info(f"Video saved to: {path}")
            return path

    except aiohttp.ClientError as e:
        logger.error(f"Network error downloading video: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Error downloading video: {e}", exc_info=True)
        return None


