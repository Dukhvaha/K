import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Базовая модель
Base = declarative_base()

# Движок БД
DATABASE_URL = "sqlite+aiosqlite:///./movies.db"
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_db_session():
    """Context manager для сессий БД - использовать через async with"""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db():
    """Инициализация БД - создание таблиц"""
    from database.models import VideoCache, UserFavorite  # noqa
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")



