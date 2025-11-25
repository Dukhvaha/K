import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Загружаем .env файл если он существует
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    
    # Telegram
    API_TOKEN: str = os.getenv("API_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    
    # Kinopoisk
    KINOPOISK_TOKEN: Optional[str] = os.getenv("KINOPOISK_TOKEN")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./movies.db"
    )
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = os.getenv("DB_PORT")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    
    # Redis (опционально)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Environment
    ENV: str = os.getenv("ENV", "development")  # development, production
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
try:
    settings = Settings()
except Exception as e:
    # Fallback для обратной совместимости со старым config.py
    import logging
    logging.warning(f"Error loading settings: {e}. Using environment variables directly.")
    settings = type('Settings', (), {
        'API_TOKEN': os.getenv("API_TOKEN", ""),
        'CHANNEL_ID': os.getenv("CHANNEL_ID", ""),
        'KINOPOISK_TOKEN': os.getenv("KINOPOISK_TOKEN"),
        'DATABASE_URL': os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./movies.db"),
        'ENV': os.getenv("ENV", "development"),
        'LOG_LEVEL': os.getenv("LOG_LEVEL", "INFO"),
    })()

# Для обратной совместимости (deprecated, используйте settings)
API_TOKEN = settings.API_TOKEN
CHANNEL_ID = settings.CHANNEL_ID
kinopoisk_token = settings.KINOPOISK_TOKEN
