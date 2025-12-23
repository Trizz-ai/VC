"""
Meeting management endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_dependency
from app.core.database import get_db
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.schemas.meeting import (
    MeetingCreate, 
    MeetingResponse, 
    MeetingUpdate,
    NearbyMeetingResponse,
    MeetingSearchResponse,
    MeetingStatistics,
    UpcomingMeetingResponse,
)
from app.services.meeting_service import MeetingService

router = APIRouter()


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a new meeting"""
    meeting_service = MeetingService()
    
    meeting = await meeting_service.create_meeting(
        meeting_data=meeting_data.dict(),
        created_by=current_user.id,
        db=db
    )
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create meeting"
        )
    
    return MeetingResponse.from_orm(meeting)


# IMPORTANT: Specific routes must come BEFORE parameterized routes
@router.get("/nearby", response_model=List[NearbyMeetingResponse])
async def get_nearby_meetings(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=5.0, description="Search radius in kilometers"),
    active_only: bool = Query(default=True, description="Only show active meetings"),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Find nearby meetings with GPS verification"""
    meeting_service = MeetingService()
    
    meetings = await meeting_service.find_nearby_meetings(
        user_lat=lat,
        user_lng=lng,
        radius_km=radius_km,
        active_only=active_only,
        db=db
    )
    
    return [NearbyMeetingResponse(**meeting) for meeting in meetings]


@router.get("/search", response_model=List[MeetingSearchResponse])
async def search_meetings(
    query: str = Query(..., description="Search query"),
    limit: int = Query(default=20, description="Maximum number of results"),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Search meetings by name or description"""
    meeting_service = MeetingService()
    
    meetings = await meeting_service.search_meetings(
        query=query,
        limit=limit,
        db=db
    )
    
    return [MeetingSearchResponse(**meeting) for meeting in meetings]


@router.get("/upcoming", response_model=List[UpcomingMeetingResponse])
async def get_upcoming_meetings(
    days_ahead: int = Query(default=7, description="Days ahead to search"),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming meetings"""
    meeting_service = MeetingService()
    
    meetings = await meeting_service.get_upcoming_meetings(
        days_ahead=days_ahead,
        db=db
    )
    
    return [UpcomingMeetingResponse(**meeting) for meeting in meetings]


@router.get("/my-meetings", response_model=List[MeetingResponse])
async def get_my_meetings(
    limit: int = Query(default=50, description="Maximum number of results"),
    offset: int = Query(default=0, description="Offset for pagination"),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get meetings created by current user"""
    meeting_service = MeetingService()
    
    meetings = await meeting_service.get_meetings_by_creator(
        creator_id=current_user.id,
        limit=limit,
        offset=offset,
        db=db
    )
    
    return [MeetingResponse.from_orm(meeting) for meeting in meetings]


# Now parameterized routes can be defined
@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get meeting by ID"""
    try:
        meeting_service = MeetingService()
        meeting = await meeting_service.get_meeting_by_id(meeting_id, db)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        return MeetingResponse.from_orm(meeting)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get meeting: {str(e)}"
        )


@router.get("/{meeting_id}/statistics", response_model=MeetingStatistics)
async def get_meeting_statistics(
    meeting_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a specific meeting"""
    meeting_service = MeetingService()
    
    statistics = await meeting_service.get_meeting_statistics(
        meeting_id=meeting_id,
        db=db
    )
    
    if not statistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    return MeetingStatistics(**statistics)


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: UUID,
    meeting_data: MeetingUpdate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Update meeting information"""
    meeting_service = MeetingService()
    
    # Filter out None values
    update_data = {k: v for k, v in meeting_data.dict().items() if v is not None}
    
    meeting = await meeting_service.update_meeting(
        meeting_id=meeting_id,
        update_data=update_data,
        db=db
    )
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    return MeetingResponse.from_orm(meeting)


@router.post("/{meeting_id}/deactivate")
async def deactivate_meeting(
    meeting_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a meeting"""
    meeting_service = MeetingService()
    
    success = await meeting_service.deactivate_meeting(
        meeting_id=meeting_id,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    return {"message": "Meeting deactivated successfully"}
