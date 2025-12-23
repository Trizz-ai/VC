"""
Database configuration and connection management
"""

import logging
from typing import AsyncGenerator

import redis.asyncio as redis
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine
def create_engine_with_pool_config():
    """Create database engine with appropriate pool configuration for the database type"""
    database_url = settings.DATABASE_URL
    if "sqlite" in database_url.lower():
        # SQLite async requires aiosqlite driver
        if not database_url.startswith("sqlite+aiosqlite"):
            # Replace sqlite:// with sqlite+aiosqlite://
            database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        # SQLite doesn't support connection pooling
        return create_async_engine(
            database_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False} if "sqlite" in database_url.lower() else {},
        )
    else:
        # PostgreSQL and other databases support connection pooling
        return create_async_engine(
            database_url,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            echo=settings.DEBUG,
        )

engine = create_engine_with_pool_config()

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Redis connection (optional - will be None if Redis is not available)
redis_client = None
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_POOL_SIZE,
        decode_responses=True,
    )
except Exception as e:
    logger.warning(f"Redis connection failed (optional): {e}. Continuing without Redis.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis | None:
    """Get Redis client (returns None if Redis is not available)"""
    return redis_client


async def create_tables():
    """Create database tables"""
    try:
        from app.models import Base
        
        # For SQLite, we need to ensure the database file directory exists
        if "sqlite" in settings.DATABASE_URL.lower():
            import os
            db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
            if db_path and db_path != ":memory:":
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def close_connections():
    """Close database and Redis connections"""
    try:
        await engine.dispose()
        if redis_client:
            await redis_client.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing connections: {e}")
        raise
