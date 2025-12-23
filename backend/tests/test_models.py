"""
Test-specific model configurations for SQLite compatibility
"""

import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.sqlite import CHAR
from app.models.base import Base


class TestBase(Base):
    """Test base class with SQLite-compatible ID generation"""
    
    # Override ID column for SQLite compatibility
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Override timestamp columns for SQLite compatibility
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )
