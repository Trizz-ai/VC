"""
Session management endpoints
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_dependency
from app.core.database import get_db
from app.models.contact import Contact
from app.models.session import Session, SessionStatus
from app.schemas.session import (
    SessionCreate, 
    SessionResponse, 
    SessionUpdate,
    SessionEventCreate,
    SessionEventResponse,
    SessionStatistics,
    LocationData,
)
from app.services.session_service import SessionService
from app.services.location_service import LocationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions for the current user"""
    try:
        session_service = SessionService()
        sessions = await session_service.get_sessions_by_contact(
            contact_id=str(current_user.id),
            db=db
        )
        return [SessionResponse.from_orm(session) for session in sessions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a new attendance session"""
    try:
        session_service = SessionService()
        
        # Session IDs are strings
        try:
            session = await session_service.create_session(
                contact_id=str(current_user.id),
                meeting_id=str(session_data.meeting_id),
                notes=session_data.notes,
                db=db
            )
        except ValueError as e:
            # Handle validation errors (meeting not found, inactive, etc.)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except RuntimeError as e:
            # Handle runtime errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create session. Meeting may not exist or may be inactive."
            )
        
        # Convert to response model
        # Get check-in/check-out times safely (they depend on events relationship)
        check_in_time = None
        check_out_time = None
        try:
            # Try to access check_in_time property safely
            if hasattr(session, 'events'):
                check_in_time = session.check_in_time
        except Exception as e:
            logger.debug(f"Could not get check_in_time: {e}")
        try:
            if hasattr(session, 'events'):
                check_out_time = session.check_out_time
        except Exception as e:
            logger.debug(f"Could not get check_out_time: {e}")
        
        try:
            # Convert status to SessionStatus enum if it's a string
            session_status = session.status
            if isinstance(session_status, str):
                try:
                    session_status = SessionStatus(session_status)
                except ValueError:
                    logger.warning(f"Invalid session status: {session_status}, defaulting to ACTIVE")
                    session_status = SessionStatus.ACTIVE
            
            # Create response manually to ensure proper type conversion
            # Compute is_active from status
            is_active = session_status in [SessionStatus.ACTIVE, SessionStatus.CHECKED_IN]
            
            response = SessionResponse(
                id=str(session.id),
                contact_id=str(session.contact_id),
                meeting_id=str(session.meeting_id) if session.meeting_id else None,
                status=session_status,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                session_notes=session.session_notes,
                dest_name=session.dest_name,
                dest_address=session.dest_address,
                dest_lat=session.dest_lat,
                dest_lng=session.dest_lng,
                is_complete=getattr(session, 'is_complete', False),
                is_active=is_active,
                created_at=getattr(session, 'created_at', None),
                updated_at=getattr(session, 'updated_at', None),
            )
            return response
        except Exception as e:
            # If response creation fails, log and re-raise with more context
            logger.error(f"Error creating session response: {e}", exc_info=True)
            logger.error(f"Session data: id={session.id}, contact_id={session.contact_id}, meeting_id={session.meeting_id}, status={session.status}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create session response: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/general", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_general_session(
    notes: Optional[str] = None,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Create a general session without a meeting (for login tracking)"""
    try:
        session_service = SessionService()
        
        session = await session_service.create_general_session(
            contact_id=str(current_user.id),
            notes=notes,
            db=db
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create general session"
            )
        
        # Get check-in/check-out times safely (they depend on events relationship)
        check_in_time = None
        check_out_time = None
        try:
            if hasattr(session, 'events'):
                check_in_time = session.check_in_time
        except Exception as e:
            logger.debug(f"Could not get check_in_time: {e}")
        try:
            if hasattr(session, 'events'):
                check_out_time = session.check_out_time
        except Exception as e:
            logger.debug(f"Could not get check_out_time: {e}")
        
        # Convert status to SessionStatus enum if it's a string
        session_status = session.status
        if isinstance(session_status, str):
            try:
                session_status = SessionStatus(session_status)
            except ValueError:
                logger.warning(f"Invalid session status: {session_status}, defaulting to ACTIVE")
                session_status = SessionStatus.ACTIVE
        
        # Compute is_active from status
        is_active = session_status in [SessionStatus.ACTIVE, SessionStatus.CHECKED_IN]
        
        # Create response manually to ensure proper type conversion
        response = SessionResponse(
            id=str(session.id),
            contact_id=str(session.contact_id),
            meeting_id=str(session.meeting_id) if session.meeting_id else None,
            status=session_status,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            session_notes=session.session_notes,
            dest_name=session.dest_name,
            dest_address=session.dest_address,
            dest_lat=session.dest_lat,
            dest_lng=session.dest_lng,
            is_complete=getattr(session, 'is_complete', False),
            is_active=is_active,
            created_at=getattr(session, 'created_at', None),
            updated_at=getattr(session, 'updated_at', None),
        )
        return response
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating general session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create general session: {str(e)}"
        )


@router.get("/active", response_model=SessionResponse)
async def get_active_session(
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get active session for current user"""
    logger.info(f"get_active_session called for user: {current_user.id}")
    try:
        session_service = SessionService()
        
        logger.info(f"Getting active session for contact_id: {current_user.id}")
        session = await session_service.get_active_session(current_user.id, db)
        logger.info(f"Active session query result: {session is not None}")
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active session found"
            )
        
        # Get check-in/check-out times safely (they depend on events relationship)
        check_in_time = None
        check_out_time = None
        try:
            if hasattr(session, 'events'):
                check_in_time = session.check_in_time
        except Exception as e:
            logger.debug(f"Could not get check_in_time: {e}")
        try:
            if hasattr(session, 'events'):
                check_out_time = session.check_out_time
        except Exception as e:
            logger.debug(f"Could not get check_out_time: {e}")
        
        # Convert status to SessionStatus enum if it's a string
        session_status = session.status
        if isinstance(session_status, str):
            try:
                session_status = SessionStatus(session_status)
            except ValueError:
                logger.warning(f"Invalid session status: {session_status}, defaulting to ACTIVE")
                session_status = SessionStatus.ACTIVE
        
        # Compute is_active from status
        is_active = session_status in [SessionStatus.ACTIVE, SessionStatus.CHECKED_IN]
        
        # Create response manually to ensure proper type conversion
        try:
            response = SessionResponse(
                id=str(session.id),
                contact_id=str(session.contact_id),
                meeting_id=str(session.meeting_id) if session.meeting_id else None,
                status=session_status,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                session_notes=session.session_notes,
                dest_name=session.dest_name,
                dest_address=session.dest_address,
                dest_lat=session.dest_lat,
                dest_lng=session.dest_lng,
                is_complete=getattr(session, 'is_complete', False),
                is_active=is_active,
                created_at=getattr(session, 'created_at', None),
                updated_at=getattr(session, 'updated_at', None),
            )
            logger.info(f"SessionResponse created successfully: id={response.id}, status={response.status}")
            return response
        except Exception as e:
            logger.error(f"Error creating SessionResponse: {e}", exc_info=True)
            # Return dict as fallback to avoid validation error
            return {
                "id": str(session.id),
                "contact_id": str(session.contact_id),
                "meeting_id": str(session.meeting_id) if session.meeting_id else None,
                "status": session_status.value if hasattr(session_status, 'value') else str(session_status),
                "check_in_time": check_in_time.isoformat() if check_in_time else None,
                "check_out_time": check_out_time.isoformat() if check_out_time else None,
                "session_notes": session.session_notes,
                "dest_name": session.dest_name,
                "dest_address": session.dest_address,
                "dest_lat": session.dest_lat,
                "dest_lng": session.dest_lng,
                "is_complete": getattr(session, 'is_complete', False),
                "is_active": is_active,
                "created_at": session.created_at.isoformat() if hasattr(session, 'created_at') and session.created_at else None,
                "updated_at": session.updated_at.isoformat() if hasattr(session, 'updated_at') and session.updated_at else None,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active session: {str(e)}"
        )


@router.get("/history", response_model=List[SessionResponse])
async def get_session_history(
    limit: int = 50,
    offset: int = 0,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get session history for current user"""
    try:
        session_service = SessionService()
        
        sessions = await session_service.get_session_history(
            contact_id=current_user.id,
            limit=limit,
            offset=offset,
            db=db
        )
        
        # Build response list manually to handle events relationship safely
        response_list = []
        for session in sessions:
            # Get check-in/check-out times safely (they depend on events relationship)
            check_in_time = None
            check_out_time = None
            try:
                if hasattr(session, 'events'):
                    check_in_time = session.check_in_time
            except Exception as e:
                logger.debug(f"Could not get check_in_time for session {session.id}: {e}")
            try:
                if hasattr(session, 'events'):
                    check_out_time = session.check_out_time
            except Exception as e:
                logger.debug(f"Could not get check_out_time for session {session.id}: {e}")
            
            # Convert status to SessionStatus enum if it's a string
            session_status = session.status
            if isinstance(session_status, str):
                try:
                    session_status = SessionStatus(session_status)
                except ValueError:
                    logger.warning(f"Invalid session status: {session_status}, defaulting to ACTIVE")
                    session_status = SessionStatus.ACTIVE
            
            # Compute is_active from status
            is_active = session_status in [SessionStatus.ACTIVE, SessionStatus.CHECKED_IN]
            
            # Create response manually to ensure proper type conversion
            response_list.append(SessionResponse(
                id=str(session.id),
                contact_id=str(session.contact_id),
                meeting_id=str(session.meeting_id) if session.meeting_id else None,
                status=session_status,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                session_notes=session.session_notes,
                dest_name=session.dest_name,
                dest_address=session.dest_address,
                dest_lat=session.dest_lat,
                dest_lng=session.dest_lng,
                is_complete=getattr(session, 'is_complete', False),
                is_active=is_active,
                created_at=getattr(session, 'created_at', None),
                updated_at=getattr(session, 'updated_at', None),
            ))
        
        return response_list
    except Exception as e:
        logger.error(f"Error getting session history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session history: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get session by ID"""
    try:
        # FastAPI should validate UUID format before reaching here
        # If we get here, session_id is a valid UUID format
        session_service = SessionService()
        session = await session_service.get_session_by_id(str(session_id), db)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        # Verify user owns the session
        if str(session.contact_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this session"
            )
        return SessionResponse.from_orm(session)
    except HTTPException:
        raise
    except ValueError as e:
        # If UUID parsing fails, FastAPI should catch this before reaching here
        # But just in case, return 422 validation error
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid session ID format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.post("/{session_id}/check-in", response_model=SessionEventResponse)
async def check_in(
    session_id: str,  # Session IDs are strings, not UUIDs
    event_data: SessionEventCreate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Check in to a session with GPS verification"""
    session_service = SessionService()
    location_service = LocationService()
    
    # Create location data
    location_data = LocationData(
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        accuracy=event_data.accuracy,
        altitude=event_data.altitude,
        speed=event_data.speed,
        heading=event_data.heading,
        timestamp=event_data.timestamp,
    )
    
    # Verify location is valid
    if not location_service.is_location_valid(
        location_data.latitude,
        location_data.longitude,
        location_data.accuracy
    ):
        error_detail = f"Invalid location data: lat={location_data.latitude}, lng={location_data.longitude}"
        if location_data.accuracy:
            error_detail += f", accuracy={location_data.accuracy}m (max: 1000m)"
        logger.warning(error_detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    # Perform check-in
    # Convert session_id to string if needed
    event = await session_service.check_in(
        session_id=str(session_id),
        location_data=location_data,
        notes=event_data.notes,
        db=db
    )
    
    if not event:
        # Get more details about why check-in failed
        logger.error(f"Check-in failed for session {session_id}")
        logger.error(f"Location: {location_data.latitude}, {location_data.longitude}, accuracy: {location_data.accuracy}m")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-in failed - location verification failed. Check backend logs for details."
        )
    
    return SessionEventResponse.from_orm(event)


@router.post("/{session_id}/check-out", response_model=SessionEventResponse)
async def check_out(
    session_id: UUID,
    event_data: SessionEventCreate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Check out of a session with GPS verification"""
    session_service = SessionService()
    location_service = LocationService()
    
    # Create location data
    location_data = LocationData(
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        accuracy=event_data.accuracy,
        altitude=event_data.altitude,
        speed=event_data.speed,
        heading=event_data.heading,
        timestamp=event_data.timestamp,
    )
    
    # Verify location is valid
    if not location_service.is_location_valid(
        location_data.latitude,
        location_data.longitude,
        location_data.accuracy
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location data"
        )
    
    # Perform check-out
    event = await session_service.check_out(
        session_id=session_id,
        location_data=location_data,
        notes=event_data.notes,
        db=db
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out failed - location verification failed"
        )
    
    return SessionEventResponse.from_orm(event)


@router.get("/{session_id}/details")
async def get_session_details(
    session_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed session information"""
    session_service = SessionService()
    
    session_details = await session_service.get_session_details(session_id, db)
    
    if not session_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session_details


@router.post("/{session_id}/end")
async def end_session(
    session_id: UUID,
    reason: str = "Manual end",
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """End a session manually"""
    session_service = SessionService()
    
    success = await session_service.end_session(
        session_id=session_id,
        reason=reason,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to end session"
        )
    
    return {"message": "Session ended successfully"}


@router.get("/statistics/overview", response_model=SessionStatistics)
async def get_session_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get session statistics for current user"""
    session_service = SessionService()
    
    statistics = await session_service.get_session_statistics(
        contact_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    
    return SessionStatistics(**statistics)
