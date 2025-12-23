"""
Test database configuration with SQLite compatibility
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Test database engine - always use SQLite for testing
def create_test_engine():
    """Create test database engine with SQLite"""
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

test_engine = create_test_engine()

# Test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_test_tables():
    """Create test database tables"""
    try:
        from app.models.base_test import BaseTest
        
        async with test_engine.begin() as conn:
            await conn.run_sync(BaseTest.metadata.create_all)
        
        logger.info("Test database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create test database tables: {e}")
        raise


async def close_test_connections():
    """Close test database connections"""
    try:
        await test_engine.dispose()
        logger.info("Test database connections closed")
    except Exception as e:
        logger.error(f"Error closing test connections: {e}")
        raise
