"""
Base model class for testing with SQLite compatibility
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, func, Table, ForeignKey, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.dialects.postgresql import UUID

@as_declarative()
class BaseTest:
    """Base class for all database models with SQLite compatibility"""
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common columns
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


# Association table for many-to-many relationship between contacts and meetings
meeting_contacts_test = Table(
    'meeting_contacts',
    BaseTest.metadata,
    Column('meeting_id', String(36), ForeignKey('meetings.id'), primary_key=True),
    Column('contact_id', String(36), ForeignKey('contacts.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)
