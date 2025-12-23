"""
Session model for attendance sessions
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    ENDED = "ended"


class Session(Base):
    """Session model for attendance tracking sessions"""
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=True, index=True)
    
    # Destination information
    dest_name = Column(String(255), nullable=False, comment="Destination name")
    dest_address = Column(String(500), nullable=False, comment="Destination address")
    dest_lat = Column(Float, nullable=False, comment="Destination latitude")
    dest_lng = Column(Float, nullable=False, comment="Destination longitude")
    
    # Session information
    session_notes = Column(Text, nullable=True, comment="Session notes")
    status = Column(String(20), default=SessionStatus.ACTIVE, nullable=False, index=True)
    is_complete = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    contact = relationship("Contact", back_populates="sessions")
    meeting = relationship("Meeting", back_populates="sessions")
    events = relationship("SessionEvent", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, contact_id={self.contact_id}, meeting_id={self.meeting_id}, dest_name={self.dest_name})>"
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID"""
        if not isinstance(other, Session):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
    
    def __init__(self, **kwargs):
        """Initialize Session with default values"""
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Set default values if not provided
        if 'is_complete' not in kwargs:
            kwargs['is_complete'] = False
        if 'status' not in kwargs:
            kwargs['status'] = SessionStatus.ACTIVE
        super().__init__(**kwargs)
    
    @property
    def is_checked_in(self) -> bool:
        """Check if session has check-in event"""
        return any(event.type == "check_in" for event in self.events)
    
    @property
    def is_checked_out(self) -> bool:
        """Check if session has check-out event"""
        return any(event.type == "check_out" for event in self.events)
    
    @property
    def check_in_time(self) -> Optional[datetime]:
        """Get check-in timestamp"""
        check_in_event = next((event for event in self.events if event.type == "check_in"), None)
        return check_in_event.ts_client if check_in_event else None
    
    @check_in_time.setter
    def check_in_time(self, value: Optional[datetime]) -> None:
        """Set check-in timestamp by creating/updating check-in event"""
        if value is None:
            # Remove existing check-in event
            if hasattr(self, 'events') and self.events:
                check_in_events = [event for event in self.events if event.type == "check_in"]
                for event in check_in_events:
                    self.events.remove(event)
        else:
            # Find or create check-in event
            if hasattr(self, 'events') and self.events:
                check_in_event = next((event for event in self.events if event.type == "check_in"), None)
                if check_in_event:
                    check_in_event.ts_client = value
                else:
                    # Create new check-in event
                    from app.models.session_event import SessionEvent, EventType
                    check_in_event = SessionEvent(
                        session_id=self.id,
                        type=EventType.CHECK_IN,
                        ts_client=value
                    )
                    self.events.append(check_in_event)
            else:
                # If events relationship is not loaded, we can't set the time
                # This is a limitation when the relationship is not loaded
                pass
    
    @property
    def check_out_time(self) -> Optional[datetime]:
        """Get check-out timestamp"""
        check_out_event = next((event for event in self.events if event.type == "check_out"), None)
        return check_out_event.ts_client if check_out_event else None
    
    @check_out_time.setter
    def check_out_time(self, value: Optional[datetime]) -> None:
        """Set check-out timestamp by creating/updating check-out event"""
        if value is None:
            # Remove existing check-out event
            if hasattr(self, 'events') and self.events:
                check_out_events = [event for event in self.events if event.type == "check_out"]
                for event in check_out_events:
                    self.events.remove(event)
        else:
            # Find or create check-out event
            if hasattr(self, 'events') and self.events:
                check_out_event = next((event for event in self.events if event.type == "check_out"), None)
                if check_out_event:
                    check_out_event.ts_client = value
                else:
                    # Create new check-out event
                    from app.models.session_event import SessionEvent, EventType
                    check_out_event = SessionEvent(
                        session_id=self.id,
                        type=EventType.CHECK_OUT,
                        ts_client=value
                    )
                    self.events.append(check_out_event)
            else:
                # If events relationship is not loaded, we can't set the time
                # This is a limitation when the relationship is not loaded
                pass
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get session duration"""
        if self.check_in_time and self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.is_checked_in and not self.is_checked_out and not self.is_complete
    
    def complete(self) -> None:
        """Mark session as complete"""
        self.is_complete = True
    
    def get_public_token(self) -> str:
        """Generate public token for sharing"""
        # This would generate a secure token for public sharing
        # Implementation depends on your token generation strategy
        return f"public_{self.id}"
