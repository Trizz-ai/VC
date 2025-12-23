"""
SQLite-compatible database configuration for testing
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, event, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import CHAR

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLite-compatible database engine
def create_sqlite_engine():
    """Create SQLite-compatible database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Add SQLite UUID support
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine

sqlite_engine = create_sqlite_engine()

# SQLite session factory
SQLiteSessionLocal = sessionmaker(
    sqlite_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_sqlite_db() -> AsyncGenerator[AsyncSession, None]:
    """Get SQLite database session"""
    async with SQLiteSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_sqlite_tables():
    """Create SQLite-compatible database tables"""
    try:
        from app.models.base import Base
        
        # Create a custom metadata that uses String instead of UUID for SQLite
        from sqlalchemy import MetaData
        from sqlalchemy import Table, Column, String, DateTime, Boolean, Text, Integer, Float
        from sqlalchemy import ForeignKey
        from sqlalchemy.sql import func
        
        metadata = MetaData()
        
        # Create tables with String IDs for SQLite compatibility
        contacts_table = Table(
            'contacts',
            metadata,
            Column('id', String(36), primary_key=True),
            Column('email', String(255), unique=True, nullable=False),
            Column('phone', String(20), nullable=True),
            Column('first_name', String(100), nullable=True),
            Column('last_name', String(100), nullable=True),
            Column('password_hash', String(255), nullable=True),
            Column('ghl_contact_id', String(100), unique=True, nullable=True),
            Column('consent_granted', Boolean, default=False, nullable=False),
            Column('consent_timestamp', DateTime(timezone=True), nullable=True),
            Column('notes', Text, nullable=True),
            Column('is_active', Boolean, default=True, nullable=False),
            Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
        )
        
        meetings_table = Table(
            'meetings',
            metadata,
            Column('id', String(36), primary_key=True),
            Column('name', String(255), nullable=False),
            Column('description', Text, nullable=True),
            Column('address', String(500), nullable=True),
            Column('lat', Float, nullable=True),
            Column('lng', Float, nullable=True),
            Column('radius_meters', Float, nullable=True),
            Column('start_time', DateTime(timezone=True), nullable=True),
            Column('end_time', DateTime(timezone=True), nullable=True),
            Column('is_active', Boolean, default=True, nullable=False),
            Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
        )
        
        sessions_table = Table(
            'sessions',
            metadata,
            Column('id', String(36), primary_key=True),
            Column('contact_id', String(36), ForeignKey('contacts.id'), nullable=False),
            Column('meeting_id', String(36), ForeignKey('meetings.id'), nullable=False),
            Column('status', String(50), nullable=False),
            Column('check_in_time', DateTime(timezone=True), nullable=True),
            Column('check_out_time', DateTime(timezone=True), nullable=True),
            Column('session_notes', Text, nullable=True),
            Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
        )
        
        session_events_table = Table(
            'session_events',
            metadata,
            Column('id', String(36), primary_key=True),
            Column('session_id', String(36), ForeignKey('sessions.id'), nullable=False),
            Column('type', String(50), nullable=False),
            Column('lat', Float, nullable=True),
            Column('lng', Float, nullable=True),
            Column('accuracy', Float, nullable=True),
            Column('location_flag', Boolean, default=False, nullable=False),
            Column('timestamp', DateTime(timezone=True), default=func.now(), nullable=False),
            Column('created_at', DateTime(timezone=True), default=func.now(), nullable=False),
            Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
        )
        
        meeting_contacts_table = Table(
            'meeting_contacts',
            metadata,
            Column('meeting_id', String(36), ForeignKey('meetings.id'), primary_key=True),
            Column('contact_id', String(36), ForeignKey('contacts.id'), primary_key=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
        )
        
        async with sqlite_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        
        logger.info("SQLite-compatible database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create SQLite database tables: {e}")
        raise


async def close_sqlite_connections():
    """Close SQLite database connections"""
    try:
        await sqlite_engine.dispose()
        logger.info("SQLite database connections closed")
    except Exception as e:
        logger.error(f"Error closing SQLite connections: {e}")
        raise
