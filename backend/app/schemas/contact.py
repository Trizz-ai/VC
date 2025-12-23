"""
Contact Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    """Base contact schema"""
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Contact creation schema"""
    consent_granted: bool = Field(..., description="User consent for GPS tracking")


class ContactUpdate(BaseModel):
    """Contact update schema"""
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    notes: Optional[str] = None
    consent_granted: Optional[bool] = None


class ContactResponse(ContactBase):
    """Contact response schema"""
    id: str  # Contact.id is a String, not UUID
    ghl_contact_id: Optional[str] = None
    consent_granted: bool
    consent_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """Contact list response schema"""
    contacts: list[ContactResponse]
    total: int
    skip: int
    limit: int
