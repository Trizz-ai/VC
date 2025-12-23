"""
Session schemas for request/response models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.session import SessionStatus


class SessionCreate(BaseModel):
    """Session creation request schema"""
    meeting_id: str  # Meeting.id is a String, not UUID
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    """Session update request schema"""
    notes: Optional[str] = None
    status: Optional[SessionStatus] = None


class SessionResponse(BaseModel):
    """Session response schema"""
    id: str  # Session.id is a String, not UUID
    contact_id: str  # Session.contact_id is a String, not UUID
    meeting_id: Optional[str] = None  # Session.meeting_id is a String, not UUID
    status: SessionStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    session_notes: Optional[str] = None
    dest_name: Optional[str] = None
    dest_address: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None
    is_complete: bool = False
    is_active: Optional[bool] = None  # Computed from status
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LocationData(BaseModel):
    """Location data schema"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0, le=1000)
    altitude: Optional[float] = None
    speed: Optional[float] = Field(None, ge=0)
    heading: Optional[float] = Field(None, ge=0, le=360)
    timestamp: Optional[float] = None


class SessionEventCreate(BaseModel):
    """Session event creation request schema"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0, le=1000)
    altitude: Optional[float] = None
    speed: Optional[float] = Field(None, ge=0)
    heading: Optional[float] = Field(None, ge=0, le=360)
    timestamp: Optional[float] = None
    notes: Optional[str] = None


class SessionEventResponse(BaseModel):
    """Session event response schema"""
    id: UUID
    session_id: UUID
    type: str
    lat: float
    lng: float
    accuracy: Optional[float]
    altitude: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    notes: Optional[str]
    location_flag: bool
    ts_client: Optional[datetime]
    ts_server: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionStatistics(BaseModel):
    """Session statistics schema"""
    total_sessions: int
    status_breakdown: Dict[str, int]
    completed_sessions: int
    average_duration_minutes: float
    date_range: Dict[str, Optional[str]]


class SessionDetails(BaseModel):
    """Detailed session information schema"""
    session: Dict[str, Any]
    meeting: Optional[Dict[str, Any]]
    events: List[Dict[str, Any]]