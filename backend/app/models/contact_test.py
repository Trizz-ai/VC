"""
Contact model for testing with SQLite compatibility
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Boolean, Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.models.base_test import BaseTest


class ContactTest(BaseTest):
    """Contact model for testing with SQLite compatibility"""
    
    __tablename__ = "contacts"
    
    # Primary key - using String for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Contact information
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)
    
    # GoHighLevel integration
    ghl_contact_id = Column(String(100), unique=True, nullable=True, index=True)
    
    # Consent and privacy
    consent_granted = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    sessions = relationship("SessionTest", back_populates="contact", cascade="all, delete-orphan")
    meetings = relationship("MeetingTest", back_populates="contacts", secondary="meeting_contacts", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<ContactTest(id={self.id}, email={self.email})>"
    
    def __eq__(self, other) -> bool:
        """Test equality based on ID"""
        if not isinstance(other, ContactTest):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
    
    def __init__(self, **kwargs):
        """Initialize Contact with default values"""
        # Set default values if not provided
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'consent_granted' not in kwargs:
            kwargs['consent_granted'] = False
        super().__init__(**kwargs)
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email
    
    def has_consent(self) -> bool:
        """Check if user has granted consent"""
        return self.consent_granted and self.consent_timestamp is not None
    
    def grant_consent(self) -> None:
        """Grant consent for GPS tracking"""
        self.consent_granted = True
        self.consent_timestamp = datetime.utcnow()
    
    def revoke_consent(self) -> None:
        """Revoke consent for GPS tracking"""
        self.consent_granted = False
        self.consent_timestamp = None
    
    def set_password(self, password: str) -> None:
        """Set password hash"""
        from app.core.auth import get_password_hash
        self.password_hash = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        from app.core.auth import verify_password
        if not self.password_hash:
            return False
        return verify_password(password, self.password_hash)
