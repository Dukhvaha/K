from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from database.connection import Base


class VideoCache(Base):
    """Модель для кеширования видео"""
    __tablename__ = "video_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    file_id = Column(String(200), nullable=True)  # Telegram file_id
    video_url = Column(Text, nullable=True)  # Оригинальный URL видео
    kinopoisk_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())
    
    __table_args__ = (
        Index('idx_title', 'title'),
        Index('idx_kinopoisk_id', 'kinopoisk_id'),
        Index('idx_video_url', 'video_url'),
    )
    
    @classmethod
    async def get_by_title(cls, session: AsyncSession, title: str) -> Optional['VideoCache']:
        """Получить кеш по названию"""
        stmt = select(cls).where(cls.title.ilike(f"%{title}%")).order_by(cls.updated_at.desc())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_url(cls, session: AsyncSession, video_url: str) -> Optional['VideoCache']:
        """Получить кеш по URL видео"""
        stmt = select(cls).where(cls.video_url == video_url).order_by(cls.updated_at.desc())
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_kinopoisk_id(cls, session: AsyncSession, kinopoisk_id: int) -> Optional['VideoCache']:
        """Получить кеш по ID Kinopoisk"""
        stmt = select(cls).where(cls.kinopoisk_id == kinopoisk_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def create_or_update(
        cls,
        session: AsyncSession,
        title: str,
        file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        kinopoisk_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> 'VideoCache':
        """Создать или обновить запись в кеше"""
        # Пытаемся найти существующую запись
        existing = None
        if kinopoisk_id:
            existing = await cls.get_by_kinopoisk_id(session, kinopoisk_id)
        elif video_url:
            existing = await cls.get_by_url(session, video_url)
        else:
            existing = await cls.get_by_title(session, title)
        
        if existing:
            # Обновляем существующую
            if file_id:
                existing.file_id = file_id
            if video_url:
                existing.video_url = video_url
            if kinopoisk_id:
                existing.kinopoisk_id = kinopoisk_id
            if description:
                existing.description = description
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            return existing
        else:
            # Создаем новую
            new_cache = cls(
                title=title,
                file_id=file_id,
                video_url=video_url,
                kinopoisk_id=kinopoisk_id,
                description=description
            )
            session.add(new_cache)
            return new_cache


class UserFavorite(Base):
    """Модель для избранных фильмов пользователей"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    kinopoisk_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    
    __table_args__ = (
        Index('idx_user_kinopoisk', 'user_id', 'kinopoisk_id', unique=True),
    )
    
    @classmethod
    async def add_favorite(cls, session: AsyncSession, user_id: int, kinopoisk_id: int) -> 'UserFavorite':
        """Добавить фильм в избранное"""
        # Проверяем, не добавлен ли уже
        stmt = select(cls).where(
            cls.user_id == user_id,
            cls.kinopoisk_id == kinopoisk_id
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        favorite = cls(user_id=user_id, kinopoisk_id=kinopoisk_id)
        session.add(favorite)
        return favorite
    
    @classmethod
    async def remove_favorite(cls, session: AsyncSession, user_id: int, kinopoisk_id: int) -> bool:
        """Удалить фильм из избранного"""
        stmt = select(cls).where(
            cls.user_id == user_id,
            cls.kinopoisk_id == kinopoisk_id
        )
        result = await session.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if favorite:
            await session.delete(favorite)
            return True
        return False
    
    @classmethod
    async def get_user_favorites(cls, session: AsyncSession, user_id: int) -> list['UserFavorite']:
        """Получить все избранные фильмы пользователя"""
        stmt = select(cls).where(cls.user_id == user_id).order_by(cls.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())



