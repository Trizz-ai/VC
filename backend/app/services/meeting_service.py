"""
Meeting service for managing meetings and events
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.contact import Contact
from app.services.location_service import LocationService

logger = logging.getLogger(__name__)


class MeetingService:
    """Service for managing meetings and events"""
    
    def __init__(self):
        self.location_service = LocationService()
    
    async def create_meeting(
        self,
        meeting_data: Dict[str, Any],
        created_by: UUID,
        db: AsyncSession
    ) -> Optional[Meeting]:
        """Create a new meeting"""
        try:
            meeting = Meeting(
                name=meeting_data["name"],
                description=meeting_data.get("description"),
                address=meeting_data["address"],
                lat=meeting_data["lat"],
                lng=meeting_data["lng"],
                radius_meters=meeting_data.get("radius_meters", 100),
                start_time=meeting_data.get("start_time"),
                end_time=meeting_data.get("end_time"),
                is_active=meeting_data.get("is_active", True),
                created_by=created_by,
            )
            
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            
            logger.info(f"Created meeting {meeting.id}: {meeting.name}")
            return meeting
            
        except Exception as e:
            logger.error(f"Error creating meeting: {e}")
            await db.rollback()
            return None
    
    async def get_meeting_by_id(
        self,
        meeting_id: UUID,
        db: AsyncSession
    ) -> Optional[Meeting]:
        """Get meeting by ID"""
        try:
            result = await db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting meeting {meeting_id}: {e}")
            return None
    
    async def find_nearby_meetings(
        self,
        user_lat: float,
        user_lng: float,
        radius_km: float = 5.0,
        active_only: bool = True,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Find meetings within specified radius"""
        try:
            # Convert radius to meters
            radius_meters = radius_km * 1000
            
            # Build query conditions (SQLite-compatible - no PostGIS)
            conditions = []
            
            if active_only:
                conditions.append(Meeting.is_active == True)
            
            # Get all meetings (or active ones) - we'll filter by distance in Python
            # This works for SQLite which doesn't have PostGIS
            query = select(Meeting)
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await db.execute(query)
            all_meetings = result.scalars().all()
            
            # Calculate distances and filter by radius
            nearby_meetings = []
            for meeting in all_meetings:
                distance = self.location_service.calculate_distance(
                    user_lat, user_lng, meeting.lat, meeting.lng
                )
                
                # Filter by radius
                if distance > radius_meters:
                    continue
                
                # Check if meeting is currently active (within time range)
                is_currently_active = self._is_meeting_currently_active(meeting)
                
                nearby_meetings.append({
                    "id": str(meeting.id),
                    "name": meeting.name,
                    "description": meeting.description,
                    "address": meeting.address,
                    "latitude": meeting.lat,
                    "longitude": meeting.lng,
                    "radius_meters": meeting.radius_meters,
                    "distance_meters": round(distance, 2),
                    "distance_km": round(distance / 1000, 2),
                    "start_time": meeting.start_time,
                    "end_time": meeting.end_time,
                    "is_active": meeting.is_active,
                    "is_currently_active": is_currently_active,
                    "created_at": meeting.created_at,
                })
            
            # Sort by distance
            nearby_meetings.sort(key=lambda x: x["distance_meters"])
            return nearby_meetings
            
        except Exception as e:
            logger.error(f"Error finding nearby meetings: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def get_meetings_by_creator(
        self,
        creator_id: UUID,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[Meeting]:
        """Get meetings created by a specific user"""
        try:
            result = await db.execute(
                select(Meeting)
                .where(Meeting.created_by == creator_id)
                .order_by(Meeting.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting meetings by creator: {e}")
            return []
    
    async def update_meeting(
        self,
        meeting_id: UUID,
        update_data: Dict[str, Any],
        db: AsyncSession
    ) -> Optional[Meeting]:
        """Update meeting information"""
        try:
            result = await db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            meeting = result.scalar_one_or_none()
            
            if not meeting:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(meeting, field) and value is not None:
                    setattr(meeting, field, value)
            
            meeting.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(meeting)
            
            logger.info(f"Updated meeting {meeting_id}")
            return meeting
            
        except Exception as e:
            logger.error(f"Error updating meeting {meeting_id}: {e}")
            await db.rollback()
            return None
    
    async def deactivate_meeting(
        self,
        meeting_id: UUID,
        db: AsyncSession
    ) -> bool:
        """Deactivate a meeting"""
        try:
            result = await db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            meeting = result.scalar_one_or_none()
            
            if not meeting:
                return False
            
            meeting.is_active = False
            meeting.updated_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Deactivated meeting {meeting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating meeting {meeting_id}: {e}")
            await db.rollback()
            return False
    
    async def get_meeting_statistics(
        self,
        meeting_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get statistics for a specific meeting"""
        try:
            # Get meeting details
            meeting = await self.get_meeting_by_id(meeting_id, db)
            if not meeting:
                return {}
            
            # Get session counts (this would require session queries)
            # For now, return basic meeting info
            return {
                "meeting_id": str(meeting.id),
                "name": meeting.name,
                "is_active": meeting.is_active,
                "is_currently_active": self._is_meeting_currently_active(meeting),
                "created_at": meeting.created_at,
                "start_time": meeting.start_time,
                "end_time": meeting.end_time,
                "location": {
                    "address": meeting.address,
                    "latitude": meeting.lat,
                    "longitude": meeting.lng,
                    "radius_meters": meeting.radius_meters,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting meeting statistics: {e}")
            return {}
    
    async def search_meetings(
        self,
        query: str,
        limit: int = 20,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Search meetings by name or description"""
        try:
            search_term = f"%{query}%"
            result = await db.execute(
                select(Meeting)
                .where(
                    and_(
                        Meeting.is_active == True,
                        or_(
                            Meeting.name.ilike(search_term),
                            Meeting.description.ilike(search_term),
                            Meeting.address.ilike(search_term)
                        )
                    )
                )
                .order_by(Meeting.created_at.desc())
                .limit(limit)
            )
            
            meetings = result.scalars().all()
            
            return [
                {
                    "id": str(meeting.id),
                    "name": meeting.name,
                    "description": meeting.description,
                    "address": meeting.address,
                    "latitude": meeting.lat,
                    "longitude": meeting.lng,
                    "start_time": meeting.start_time,
                    "end_time": meeting.end_time,
                    "is_currently_active": self._is_meeting_currently_active(meeting),
                }
                for meeting in meetings
            ]
            
        except Exception as e:
            logger.error(f"Error searching meetings: {e}")
            return []
    
    def _is_meeting_currently_active(self, meeting: Meeting) -> bool:
        """Check if meeting is currently active based on time"""
        now = datetime.utcnow()
        
        # If no time constraints, meeting is always "active" when is_active=True
        if not meeting.start_time and not meeting.end_time:
            return meeting.is_active
        
        # Check if within time range
        if meeting.start_time and now < meeting.start_time:
            return False
        
        if meeting.end_time and now > meeting.end_time:
            return False
        
        return meeting.is_active
    
    async def get_upcoming_meetings(
        self,
        days_ahead: int = 7,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Get upcoming meetings within specified days"""
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(days=days_ahead)
            
            result = await db.execute(
                select(Meeting)
                .where(
                    and_(
                        Meeting.is_active == True,
                        Meeting.start_time >= start_time,
                        Meeting.start_time <= end_time
                    )
                )
                .order_by(Meeting.start_time)
            )
            
            meetings = result.scalars().all()
            
            return [
                {
                    "id": str(meeting.id),
                    "name": meeting.name,
                    "description": meeting.description,
                    "address": meeting.address,
                    "latitude": meeting.lat,
                    "longitude": meeting.lng,
                    "start_time": meeting.start_time,
                    "end_time": meeting.end_time,
                    "radius_meters": meeting.radius_meters,
                }
                for meeting in meetings
            ]
            
        except Exception as e:
            logger.error(f"Error getting upcoming meetings: {e}")
            return []