"""
SessionEvent model for tracking check-in/check-out events
"""

import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class EventType(enum.Enum):
    """Session event types"""
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    LOCATION_UPDATE = "location_update"
    STATUS_CHANGE = "status_change"


class LocationFlag(enum.Enum):
    """Location permission flags"""
    GRANTED = "granted"
    DENIED = "denied"
    TIMEOUT = "timeout"


class SessionEvent(Base):
    """SessionEvent model for tracking check-in/check-out events"""
    
    __tablename__ = "session_events"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Event information
    type = Column(Enum(EventType), nullable=False, index=True, comment="Event type")
    
    # Timestamps
    ts_client = Column(DateTime(timezone=True), nullable=False, comment="Client timestamp")
    ts_server = Column(DateTime(timezone=True), nullable=False, comment="Server timestamp")
    
    # Location information
    lat = Column(Float, nullable=False, comment="Latitude")
    lng = Column(Float, nullable=False, comment="Longitude")
    accuracy = Column(Float, nullable=True, comment="Location accuracy in meters")
    
    # Location permission status
    location_flag = Column(Enum(LocationFlag), nullable=False, comment="Location permission status")
    
    # Additional information
    notes = Column(Text, nullable=True, comment="Event notes")
    
    # Relationships
    session = relationship("Session", back_populates="events")
    
    def __repr__(self) -> str:
        return f"<SessionEvent(id={self.id}, session_id={self.session_id}, type={self.type.value if self.type else None})>"
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID"""
        if not isinstance(other, SessionEvent):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
    
    def __init__(self, **kwargs):
        """Initialize SessionEvent with default values"""
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Set default values if not provided
        if 'location_flag' not in kwargs:
            kwargs['location_flag'] = LocationFlag.GRANTED
        if 'ts_server' not in kwargs:
            kwargs['ts_server'] = datetime.utcnow()
        super().__init__(**kwargs)
    
    @property
    def is_check_in(self) -> bool:
        """Check if this is a check-in event"""
        return self.type == EventType.CHECK_IN
    
    @property
    def is_check_out(self) -> bool:
        """Check if this is a check-out event"""
        return self.type == EventType.CHECK_OUT
    
    @property
    def location_granted(self) -> bool:
        """Check if location permission was granted"""
        return self.location_flag == LocationFlag.GRANTED
    
    @property
    def location_denied(self) -> bool:
        """Check if location permission was denied"""
        return self.location_flag == LocationFlag.DENIED
    
    @property
    def location_timeout(self) -> bool:
        """Check if location permission timed out"""
        return self.location_flag == LocationFlag.TIMEOUT
    
    def is_valid_location(self) -> bool:
        """Check if location data is valid"""
        return (
            self.location_granted and
            self.lat is not None and
            self.lng is not None and
            -90 <= self.lat <= 90 and
            -180 <= self.lng <= 180
        )
