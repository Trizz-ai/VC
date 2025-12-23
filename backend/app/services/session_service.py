"""
Session management service for attendance tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType
from app.models.meeting import Meeting
from app.models.contact import Contact
from app.services.location_service import LocationService, LocationData, ProximityResult

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing attendance sessions"""
    
    def __init__(self):
        self.location_service = LocationService()
    
    async def create_session(
        self,
        contact_id: Union[str, UUID],
        meeting_id: Union[str, UUID],
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[Session]:
        """Create a new attendance session"""
        try:
            # Verify meeting exists and is active
            # Meeting.id is a String, not UUID
            meeting_str_id = str(meeting_id)
            meeting_result = await db.execute(
                select(Meeting).where(
                    and_(
                        Meeting.id == meeting_str_id,
                        Meeting.is_active == True
                    )
                )
            )
            meeting = meeting_result.scalar_one_or_none()
            
            if not meeting:
                # Check if meeting exists but is inactive
                inactive_result = await db.execute(
                    select(Meeting).where(Meeting.id == meeting_str_id)
                )
                inactive_meeting = inactive_result.scalar_one_or_none()
                if inactive_meeting:
                    logger.warning(f"Meeting {meeting_id} exists but is inactive")
                    raise ValueError(f"Meeting {meeting_id} is not active")
                else:
                    logger.warning(f"Meeting {meeting_id} not found")
                    raise ValueError(f"Meeting {meeting_id} not found")
            
            # Check for existing active session
            existing_session = await self.get_active_session(str(contact_id), db)
            if existing_session:
                logger.warning(
                    f"Contact {contact_id} already has active session {existing_session.id} "
                    f"for meeting {existing_session.meeting_id}. "
                    f"New session requested for meeting {meeting_str_id}. "
                    f"Ending existing session and creating new one."
                )
                # End the existing session before creating a new one
                existing_session.status = SessionStatus.ENDED
                existing_session.is_complete = True
                await db.commit()
                await db.refresh(existing_session)
                logger.info(f"Ended existing session {existing_session.id} to create new session")
            
            # Create new session
            # Session IDs are strings
            session = Session(
                contact_id=str(contact_id),
                meeting_id=meeting_str_id,
                status=SessionStatus.ACTIVE,
                session_notes=notes,
                dest_name=meeting.name,
                dest_address=meeting.address,
                dest_lat=meeting.lat,
                dest_lng=meeting.lng,
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created session {session.id} for contact {contact_id} at meeting {meeting_str_id}")
            return session
            
        except ValueError as e:
            # Re-raise ValueError so it can be caught and returned as proper error
            logger.error(f"Validation error creating session: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating session: {e}", exc_info=True)
            await db.rollback()
            raise RuntimeError(f"Failed to create session: {str(e)}")
    
    async def create_general_session(
        self,
        contact_id: Union[str, UUID],
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[Session]:
        """Create a general session without a meeting (for login tracking)"""
        try:
            # Check for existing active session
            existing_session = await self.get_active_session(str(contact_id), db)
            if existing_session:
                logger.info(
                    f"Contact {contact_id} already has active session {existing_session.id}. "
                    f"Returning existing session."
                )
                return existing_session
            
            # Create new general session without meeting
            session = Session(
                contact_id=str(contact_id),
                meeting_id=None,  # No meeting for general session
                status=SessionStatus.ACTIVE,
                session_notes=notes or "General session created on login",
                dest_name="General Session",
                dest_address="N/A",
                dest_lat=0.0,  # Default location
                dest_lng=0.0,  # Default location
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created general session {session.id} for contact {contact_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating general session: {e}", exc_info=True)
            await db.rollback()
            raise RuntimeError(f"Failed to create general session: {str(e)}")
    
    async def check_in(
        self,
        session_id: Union[str, UUID],
        location_data: LocationData,
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[SessionEvent]:
        """Check in to a session with GPS verification"""
        try:
            # Get session details
            session_result = await db.execute(
                select(Session).where(Session.id == str(session_id))
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            if session.status != SessionStatus.ACTIVE:
                logger.warning(f"Session {session_id} is not active (status: {session.status})")
                return None
            
            # Get meeting for radius check and test mode detection
            meeting_result = await db.execute(
                select(Meeting).where(Meeting.id == str(session.meeting_id))
            )
            meeting = meeting_result.scalar_one_or_none()
            
            if not meeting:
                logger.warning(f"Meeting {session.meeting_id} not found for session {session_id}")
                return None
            
            # Verify location
            proximity_result = await self.location_service.verify_location(
                location_data.latitude,
                location_data.longitude,
                str(session.meeting_id),
                db,
                location_data.accuracy
            )
            
            # For AYA Demo Meet or large-radius meetings, be extra lenient (testing)
            is_test_meeting = "AYA Demo" in meeting.name or meeting.radius_meters >= 5000
            
            if not proximity_result.is_within_range:
                if is_test_meeting:
                    # For test meetings, allow check-in even if slightly outside radius
                    # This helps with PC GPS inaccuracy
                    logger.info(
                        f"Test meeting detected: Allowing check-in despite distance "
                        f"{proximity_result.distance_meters:.2f}m (radius: {meeting.radius_meters}m)"
                    )
                    # Continue with check-in - don't return None
                else:
                    logger.warning(
                        f"Check-in location verification failed: "
                        f"distance {proximity_result.distance_meters:.2f}m, "
                        f"required radius: {meeting.radius_meters}m, "
                        f"meeting: {meeting.name}"
                    )
                    # For testing, log more details
                    logger.info(f"Meeting location: {meeting.lat}, {meeting.lng}")
                    logger.info(f"User location: {location_data.latitude}, {location_data.longitude}")
                    return None
            
            # Create check-in event
            event = await self.location_service.create_session_event(
                session_id=str(session_id),
                event_type=EventType.CHECK_IN,
                location_data=location_data,
                meeting_id=str(session.meeting_id),
                notes=notes,
                db=db
            )
            
            if event:
                # Update session status
                session.status = SessionStatus.CHECKED_IN
                session.check_in_time = datetime.utcnow()
                await db.commit()
                
                logger.info(f"Check-in successful for session {session_id}")
            
            return event
            
        except Exception as e:
            logger.error(f"Error checking in: {e}")
            await db.rollback()
            return None
    
    async def check_out(
        self,
        session_id: UUID,
        location_data: LocationData,
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[SessionEvent]:
        """Check out of a session with GPS verification"""
        try:
            # Get session details
            session_result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            if session.status != SessionStatus.CHECKED_IN:
                logger.warning(f"Session {session_id} is not checked in (status: {session.status})")
                return None
            
            # Verify location
            proximity_result = await self.location_service.verify_location(
                location_data.latitude,
                location_data.longitude,
                str(session.meeting_id),
                db,
                location_data.accuracy
            )
            
            if not proximity_result.is_within_range:
                logger.warning(
                    f"Check-out location verification failed: "
                    f"distance {proximity_result.distance_meters:.2f}m"
                )
                return None
            
            # Create check-out event
            event = await self.location_service.create_session_event(
                session_id=str(session_id),
                event_type=EventType.CHECK_OUT,
                location_data=location_data,
                meeting_id=str(session.meeting_id),
                notes=notes,
                db=db
            )
            
            if event:
                # Update session status
                session.status = SessionStatus.COMPLETED
                session.check_out_time = datetime.utcnow()
                await db.commit()
                
                logger.info(f"Check-out successful for session {session_id}")
            
            return event
            
        except Exception as e:
            logger.error(f"Error checking out: {e}")
            await db.rollback()
            return None
    
    async def get_active_session(
        self,
        contact_id: Union[str, UUID],
        db: AsyncSession
    ) -> Optional[Session]:
        """Get active session for a contact"""
        try:
            result = await db.execute(
                select(Session).where(
                    and_(
                        Session.contact_id == str(contact_id),
                        Session.status.in_([
                            SessionStatus.ACTIVE,
                            SessionStatus.CHECKED_IN
                        ])
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting active session: {e}")
            return None
    
    async def get_sessions_by_contact(
        self,
        contact_id: str,
        db: AsyncSession
    ) -> List[Session]:
        """Get all sessions for a contact"""
        try:
            result = await db.execute(
                select(Session)
                .where(Session.contact_id == contact_id)
                .order_by(Session.created_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting sessions for contact {contact_id}: {e}")
            return []
    
    async def get_session_history(
        self,
        contact_id: UUID,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[Session]:
        """Get session history for a contact"""
        try:
            result = await db.execute(
                select(Session)
                .where(Session.contact_id == contact_id)
                .order_by(Session.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    async def get_session_details(
        self,
        session_id: UUID,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get detailed session information with events"""
        try:
            # Get session
            session_result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                return None
            
            # Get session events
            events_result = await db.execute(
                select(SessionEvent)
                .where(SessionEvent.session_id == session_id)
                .order_by(SessionEvent.ts_server)
            )
            events = events_result.scalars().all()
            
            # Get meeting details
            meeting_result = await db.execute(
                select(Meeting).where(Meeting.id == session.meeting_id)
            )
            meeting = meeting_result.scalar_one_or_none()
            
            return {
                "session": {
                    "id": str(session.id),
                    "status": session.status.value,
                    "created_at": session.created_at,
                    "check_in_time": session.check_in_time,
                    "check_out_time": session.check_out_time,
                    "notes": session.session_notes,
                    "destination": {
                        "name": session.dest_name,
                        "address": session.dest_address,
                        "latitude": session.dest_lat,
                        "longitude": session.dest_lng,
                    }
                },
                "meeting": {
                    "id": str(meeting.id) if meeting else None,
                    "name": meeting.name if meeting else None,
                    "description": meeting.description if meeting else None,
                    "start_time": meeting.start_time if meeting else None,
                    "end_time": meeting.end_time if meeting else None,
                } if meeting else None,
                "events": [
                    {
                        "id": str(event.id),
                        "type": event.type.value,
                        "timestamp": event.ts_server,
                        "location": {
                            "latitude": event.lat,
                            "longitude": event.lng,
                            "accuracy": event.accuracy,
                            "altitude": event.altitude,
                        },
                        "notes": event.notes,
                        "location_verified": event.location_flag,
                    }
                    for event in events
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting session details: {e}")
            return None
    
    async def end_session(
        self,
        session_id: UUID,
        reason: str = "Manual end",
        db: AsyncSession = None
    ) -> bool:
        """End a session manually"""
        try:
            session_result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                return False
            
            # Update session status
            session.status = SessionStatus.ENDED
            session.check_out_time = datetime.utcnow()
            session.session_notes = f"{session.session_notes or ''}\nEnded: {reason}".strip()
            
            await db.commit()
            
            logger.info(f"Session {session_id} ended: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            await db.rollback()
            return False
    
    async def get_session_statistics(
        self,
        contact_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Get session statistics for a contact"""
        try:
            # Build date filter
            date_filter = Session.contact_id == contact_id
            if start_date:
                date_filter = and_(date_filter, Session.created_at >= start_date)
            if end_date:
                date_filter = and_(date_filter, Session.created_at <= end_date)
            
            # Get session counts by status
            result = await db.execute(
                select(
                    Session.status,
                    func.count(Session.id).label('count')
                )
                .where(date_filter)
                .group_by(Session.status)
            )
            
            status_counts = {row.status.value: row.count for row in result}
            
            # Get total sessions
            total_result = await db.execute(
                select(func.count(Session.id)).where(date_filter)
            )
            total_sessions = total_result.scalar() or 0
            
            # Get average session duration
            completed_sessions = await db.execute(
                select(Session)
                .where(
                    and_(
                        date_filter,
                        Session.status == SessionStatus.COMPLETED,
                        Session.check_in_time.isnot(None),
                        Session.check_out_time.isnot(None)
                    )
                )
            )
            
            completed = completed_sessions.scalars().all()
            total_duration = sum([
                (s.check_out_time - s.check_in_time).total_seconds()
                for s in completed
            ])
            
            avg_duration_minutes = (
                total_duration / len(completed) / 60
                if completed else 0
            )
            
            return {
                "total_sessions": total_sessions,
                "status_breakdown": status_counts,
                "completed_sessions": len(completed),
                "average_duration_minutes": round(avg_duration_minutes, 2),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {}