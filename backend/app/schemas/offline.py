"""
Offline operation schemas for request/response models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel


class OfflineOperationResponse(BaseModel):
    """Offline operation response schema"""
    id: str
    operation_type: str
    data: Dict[str, Any]
    priority: int
    retry_count: int
    max_retries: int
    created_at: datetime
    last_attempt: Optional[datetime]
    status: str


class OfflineQueueResponse(BaseModel):
    """Offline queue status response schema"""
    user_id: UUID
    status_counts: Dict[str, int]
    pending_count: int
    failed_count: int
    oldest_pending: Optional[datetime]
    newest_failed: Optional[datetime]


class OfflineRetryRequest(BaseModel):
    """Retry failed operation request schema"""
    operation_id: str


class OfflineProcessResponse(BaseModel):
    """Process offline operations response schema"""
    processed: int
    failed: int
    total: int


class OfflineCheckInRequest(BaseModel):
    """Offline check-in request schema"""
    session_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[float] = None
    notes: Optional[str] = None


class OfflineCheckOutRequest(BaseModel):
    """Offline check-out request schema"""
    session_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[float] = None
    notes: Optional[str] = None


class OfflineCreateSessionRequest(BaseModel):
    """Offline create session request schema"""
    meeting_id: str
    notes: Optional[str] = None


class OfflineEndSessionRequest(BaseModel):
    """Offline end session request schema"""
    session_id: str
    reason: str = "Offline end"
