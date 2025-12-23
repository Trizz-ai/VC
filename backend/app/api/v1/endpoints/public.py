"""
Public endpoints for sharing
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import verify_token, TokenType
from app.models.session import Session
from app.models.meeting import Meeting
from app.models.session_event import SessionEvent

router = APIRouter()


@router.get("/{token}")
async def public_share(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Public share endpoint - view session or meeting data by public token"""
    try:
        # Verify the public token
        payload = verify_token(token, TokenType.PUBLIC)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Get resource type and ID from query params or token
        # For now, we'll return user's recent sessions
        # In a full implementation, the token would encode the resource type and ID
        
        # Get recent sessions for the user
        result = await db.execute(
            select(Session)
            .where(Session.contact_id == user_id)
            .order_by(Session.created_at.desc())
            .limit(10)
        )
        sessions = result.scalars().all()
        
        return {
            "user_id": user_id,
            "sessions": [
                {
                    "id": str(session.id),
                    "dest_name": session.dest_name,
                    "dest_address": session.dest_address,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "is_complete": session.is_complete,
                }
                for session in sessions
            ],
            "message": "Public share data retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve public share data: {str(e)}"
        )


@router.get("/session/{session_id}")
async def public_session_share(
    session_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Public share endpoint for a specific session"""
    try:
        # Verify the public token
        payload = verify_token(token, TokenType.PUBLIC)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Get the session
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Verify the session belongs to the user in the token
        if str(session.contact_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get session events
        events_result = await db.execute(
            select(SessionEvent)
            .where(SessionEvent.session_id == session_id)
            .order_by(SessionEvent.created_at.asc())
        )
        events = events_result.scalars().all()
        
        return {
            "session": {
                "id": str(session.id),
                "dest_name": session.dest_name,
                "dest_address": session.dest_address,
                "dest_lat": session.dest_lat,
                "dest_lng": session.dest_lng,
                "is_complete": session.is_complete,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            },
            "events": [
                {
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                }
                for event in events
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session data: {str(e)}"
        )


@router.get("/meeting/{meeting_id}")
async def public_meeting_share(
    meeting_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Public share endpoint for a specific meeting"""
    try:
        # Verify the public token
        payload = verify_token(token, TokenType.PUBLIC)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get the meeting
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        )
        meeting = result.scalar_one_or_none()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        # Get meeting statistics
        sessions_result = await db.execute(
            select(Session).where(Session.meeting_id == meeting_id)
        )
        sessions = sessions_result.scalars().all()
        
        return {
            "meeting": {
                "id": str(meeting.id),
                "name": meeting.name,
                "description": meeting.description,
                "address": meeting.address,
                "latitude": meeting.latitude,
                "longitude": meeting.longitude,
                "is_active": meeting.is_active,
                "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
            },
            "statistics": {
                "total_sessions": len(sessions),
                "active_sessions": len([s for s in sessions if not s.is_complete]),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve meeting data: {str(e)}"
        )
