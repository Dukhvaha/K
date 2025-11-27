import logging
from typing import Optional, Dict, Any, List
import aiohttp
import ssl
from config import KINOPOISK_TOKEN

logger = logging.getLogger(__name__)

# Используем неофициальный API kinopoisk.dev
KINOPOISK_API_URL = "https://api.kinopoisk.dev/v1.4"

# SSL контекст для обхода проблем с сертификатами
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def search_movie_kinopoisk(query: str) -> Optional[Dict[str, Any]]:
    """
    Поиск фильма через Kinopoisk API
    
    Args:
        query: Название фильма для поиска
        
    Returns:
        Словарь с данными фильма или None
    """
    if not KINOPOISK_TOKEN:
        logger.warning("Kinopoisk token not configured")
        return None
    
    try:
        headers = {
            "X-API-KEY": KINOPOISK_TOKEN,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            # Поиск фильма
            search_url = f"{KINOPOISK_API_URL}/movie/search"
            params = {
                "query": query,
                "limit": 1
            }
            
            async with session.get(search_url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Kinopoisk API returned status {resp.status}")
                    return None
                
                data = await resp.json()
                
                if not data.get("docs") or len(data["docs"]) == 0:
                    logger.info(f"No results for query: {query}")
                    return None
                
                movie = data["docs"][0]
                
                # Получаем детальную информацию
                movie_id = movie.get("id")
                if movie_id:
                    detail_url = f"{KINOPOISK_API_URL}/movie/{movie_id}"
                    async with session.get(detail_url, headers=headers) as detail_resp:
                        if detail_resp.status == 200:
                            detail_data = await detail_resp.json()
                            return _format_movie_data(detail_data)
                
                return _format_movie_data(movie)
                
    except Exception as e:
        logger.error(f"Error searching Kinopoisk: {e}", exc_info=True)
        return None


async def get_random_movie() -> Optional[Dict[str, Any]]:
    """
    Получить случайный популярный фильм
    
    Returns:
        Словарь с данными фильма или None
    """
    if not KINOPOISK_TOKEN:
        return None
    
    try:
        headers = {
            "X-API-KEY": KINOPOISK_TOKEN,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            # Получаем топ фильмов
            url = f"{KINOPOISK_API_URL}/movie"
            params = {
                "page": 1,
                "limit": 100,
                "rating.kp": "7-10",
                "sortField": "rating.kp",
                "sortType": "-1"
            }
            
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                if not data.get("docs") or len(data["docs"]) == 0:
                    return None
                
                import random
                movie = random.choice(data["docs"])
                return _format_movie_data(movie)
                
    except Exception as e:
        logger.error(f"Error getting random movie: {e}", exc_info=True)
        return None


def _format_movie_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Форматирует данные фильма из API"""
    return {
        "id": data.get("id"),
        "name": data.get("name") or data.get("alternativeName") or data.get("enName"),
        "description": data.get("description"),
        "year": data.get("year"),
        "rating": data.get("rating", {}).get("kp"),
        "poster": data.get("poster", {}).get("url") if isinstance(data.get("poster"), dict) else data.get("poster"),
        "genres": [g.get("name") for g in data.get("genres", [])],
        "countries": [c.get("name") for c in data.get("countries", [])],
    }



