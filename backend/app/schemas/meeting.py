"""
Meeting schemas for request/response models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    """Meeting creation request schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    address: str = Field(..., min_length=1, max_length=500)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_meters: Optional[int] = Field(100, ge=10, le=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool = True


class MeetingUpdate(BaseModel):
    """Meeting update request schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius_meters: Optional[int] = Field(None, ge=10, le=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None


class MeetingResponse(BaseModel):
    """Meeting response schema"""
    id: UUID
    name: str
    description: Optional[str]
    address: str
    lat: float
    lng: float
    radius_meters: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_active: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NearbyMeetingResponse(BaseModel):
    """Nearby meeting response schema"""
    id: UUID
    name: str
    description: Optional[str]
    address: str
    latitude: float
    longitude: float
    radius_meters: int
    distance_meters: float
    distance_km: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_active: bool
    is_currently_active: bool
    created_at: datetime


class MeetingSearchRequest(BaseModel):
    """Meeting search request schema"""
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(20, ge=1, le=100)


class MeetingSearchResponse(BaseModel):
    """Meeting search response schema"""
    id: UUID
    name: str
    description: Optional[str]
    address: str
    latitude: float
    longitude: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    is_currently_active: bool


class MeetingStatistics(BaseModel):
    """Meeting statistics schema"""
    meeting_id: UUID
    name: str
    is_active: bool
    is_currently_active: bool
    created_at: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    location: Dict[str, Any]


class UpcomingMeetingResponse(BaseModel):
    """Upcoming meeting response schema"""
    id: UUID
    name: str
    description: Optional[str]
    address: str
    latitude: float
    longitude: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    radius_meters: int