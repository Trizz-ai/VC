"""
Meeting model for meeting locations and information
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Meeting(Base):
    """Meeting model for meeting locations and information"""
    
    __tablename__ = "meetings"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Meeting information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Location information
    address = Column(String(500), nullable=False)
    lat = Column(Float, nullable=False, comment="Latitude")
    lng = Column(Float, nullable=False, comment="Longitude")
    radius_meters = Column(Float, default=100.0, nullable=False, comment="Radius in meters for location verification")
    
    # Time information
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    qr_code = Column(String(100), unique=True, nullable=True, index=True)
    
    # Creator information
    created_by = Column(String(36), nullable=True, comment="Admin user who created this meeting")
    
    # Relationships
    sessions = relationship("Session", back_populates="meeting")
    contacts = relationship("Contact", secondary="meeting_contacts", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, name={self.name})>"
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID"""
        if not isinstance(other, Meeting):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
    
    def __init__(self, **kwargs):
        """Initialize Meeting with default values"""
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Set default values if not provided
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        super().__init__(**kwargs)
    
    @property
    def is_recurring(self) -> bool:
        """Check if meeting is recurring"""
        return self.start_time is not None and self.end_time is not None
    
    @property
    def is_active_meeting(self) -> bool:
        """Check if meeting is currently active"""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        
        return True
    
    def activate(self) -> None:
        """Activate the meeting"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the meeting"""
        self.is_active = False
