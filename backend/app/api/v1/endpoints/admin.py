"""
Admin endpoints
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.auth import get_current_user_dependency
from app.core.database import get_db
from app.models.contact import Contact
from app.models.session import Session
from app.models.meeting import Meeting
from app.models.session_event import SessionEvent

router = APIRouter()


async def verify_admin_access(current_user: Contact) -> Contact:
    """Verify user has admin access - for now, allow all authenticated users"""
    # In production, you would check if user has admin role
    # For now, we'll allow all authenticated users
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    return current_user


@router.get("/dashboard")
async def admin_dashboard(
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Admin dashboard statistics"""
    await verify_admin_access(current_user)
    
    try:
        # Get total counts
        total_users_result = await db.execute(select(func.count(Contact.id)))
        total_users = total_users_result.scalar() or 0
        
        total_sessions_result = await db.execute(select(func.count(Session.id)))
        total_sessions = total_sessions_result.scalar() or 0
        
        total_meetings_result = await db.execute(select(func.count(Meeting.id)))
        total_meetings = total_meetings_result.scalar() or 0
        
        active_sessions_result = await db.execute(
            select(func.count(Session.id)).where(Session.is_complete == False)
        )
        active_sessions = active_sessions_result.scalar() or 0
        
        # Get recent activity
        recent_sessions_result = await db.execute(
            select(Session)
            .order_by(Session.created_at.desc())
            .limit(10)
        )
        recent_sessions = recent_sessions_result.scalars().all()
        
        # Get user statistics
        active_users_result = await db.execute(
            select(func.count(Contact.id)).where(Contact.is_active == True)
        )
        active_users = active_users_result.scalar() or 0
        
        return {
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_meetings": total_meetings,
            },
            "recent_sessions": [
                {
                    "id": str(session.id),
                    "contact_id": str(session.contact_id),
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "is_complete": session.is_complete,
                }
                for session in recent_sessions
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard data: {str(e)}"
        )


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """List all users"""
    await verify_admin_access(current_user)
    
    try:
        query = select(Contact)
        
        if active_only:
            query = query.where(Contact.is_active == True)
        
        query = query.order_by(Contact.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "consent_granted": user.consent_granted,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get user details"""
    await verify_admin_access(current_user)
    
    try:
        result = await db.execute(
            select(Contact).where(Contact.id == str(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user's sessions count
        sessions_count_result = await db.execute(
            select(func.count(Session.id)).where(Session.contact_id == str(user_id))
        )
        sessions_count = sessions_count_result.scalar() or 0
        
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "is_active": user.is_active,
            "consent_granted": user.consent_granted,
            "consent_timestamp": user.consent_timestamp.isoformat() if user.consent_timestamp else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "sessions_count": sessions_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )


@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Activate a user account"""
    await verify_admin_access(current_user)
    
    try:
        result = await db.execute(
            select(Contact).where(Contact.id == str(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        await db.commit()
        
        return {"message": "User activated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user account"""
    await verify_admin_access(current_user)
    
    try:
        result = await db.execute(
            select(Contact).where(Contact.id == str(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        await db.commit()
        
        return {"message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )


@router.get("/sessions")
async def list_all_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    contact_id: Optional[UUID] = Query(None),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions (admin view)"""
    await verify_admin_access(current_user)
    
    try:
        query = select(Session)
        
        if contact_id:
            query = query.where(Session.contact_id == str(contact_id))
        
        query = query.order_by(Session.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return [
            {
                "id": str(session.id),
                "contact_id": str(session.contact_id),
                "meeting_id": str(session.meeting_id) if session.meeting_id else None,
                "dest_name": session.dest_name,
                "dest_address": session.dest_address,
                "is_complete": session.is_complete,
                "created_at": session.created_at.isoformat() if session.created_at else None,
            }
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/meetings")
async def list_all_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """List all meetings (admin view)"""
    await verify_admin_access(current_user)
    
    try:
        query = select(Meeting)
        
        if active_only:
            query = query.where(Meeting.is_active == True)
        
        query = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        meetings = result.scalars().all()
        
        return [
            {
                "id": str(meeting.id),
                "name": meeting.name,
                "address": meeting.address,
                "is_active": meeting.is_active,
                "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
            }
            for meeting in meetings
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list meetings: {str(e)}"
        )


@router.get("/statistics")
async def get_system_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics"""
    await verify_admin_access(current_user)
    
    try:
        # Base queries
        total_users_query = select(func.count(Contact.id))
        total_sessions_query = select(func.count(Session.id))
        total_meetings_query = select(func.count(Meeting.id))
        
        # Apply date filters if provided
        if start_date or end_date:
            if start_date:
                total_sessions_query = total_sessions_query.where(
                    Session.created_at >= start_date
                )
            if end_date:
                total_sessions_query = total_sessions_query.where(
                    Session.created_at <= end_date
                )
        
        total_users_result = await db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0
        
        total_sessions_result = await db.execute(total_sessions_query)
        total_sessions = total_sessions_result.scalar() or 0
        
        total_meetings_result = await db.execute(total_meetings_query)
        total_meetings = total_meetings_result.scalar() or 0
        
        # Active counts
        active_users_result = await db.execute(
            select(func.count(Contact.id)).where(Contact.is_active == True)
        )
        active_users = active_users_result.scalar() or 0
        
        active_sessions_result = await db.execute(
            select(func.count(Session.id)).where(Session.is_complete == False)
        )
        active_sessions = active_sessions_result.scalar() or 0
        
        active_meetings_result = await db.execute(
            select(func.count(Meeting.id)).where(Meeting.is_active == True)
        )
        active_meetings = active_meetings_result.scalar() or 0
        
        # Users with consent
        consent_users_result = await db.execute(
            select(func.count(Contact.id)).where(Contact.consent_granted == True)
        )
        consent_users = consent_users_result.scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "with_consent": consent_users,
            },
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
            },
            "meetings": {
                "total": total_meetings,
                "active": active_meetings,
            },
            "date_range": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
