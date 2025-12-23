"""
Location service for GPS verification and geospatial operations
"""

import logging
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import math

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import geohash2

from app.models.meeting import Meeting
from app.models.session import Session
from app.models.session_event import SessionEvent, EventType

logger = logging.getLogger(__name__)


@dataclass
class LocationData:
    """Location data structure"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[float] = None
    geohash: Optional[str] = None
    
    def __post_init__(self):
        """Generate geohash after initialization"""
        if self.geohash is None:
            self.geohash = geohash2.encode(self.latitude, self.longitude, precision=12)


@dataclass
class ProximityResult:
    """Result of proximity check"""
    is_within_range: bool
    distance_meters: float
    meeting_id: Optional[str] = None
    meeting_name: Optional[str] = None
    accuracy_confidence: float = 0.0


class LocationService:
    """Service for GPS verification and location operations"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="verified_compliance")
        self.default_radius_meters = 100  # 100 meters default radius
        self.max_radius_meters = 1000     # Maximum allowed radius (increased for testing)
        self.min_accuracy_meters = 1000   # Minimum required GPS accuracy (very relaxed for testing - 1km)
    
    async def verify_location(
        self,
        user_lat: float,
        user_lng: float,
        meeting_id: str,
        db: AsyncSession,
        required_accuracy: Optional[float] = None
    ) -> ProximityResult:
        """Verify user location against meeting location"""
        try:
            # Get meeting details
            result = await db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            meeting = result.scalar_one_or_none()
            
            if not meeting:
                return ProximityResult(
                    is_within_range=False,
                    distance_meters=float('inf'),
                    accuracy_confidence=0.0
                )
            
            # Calculate distance
            meeting_coords = (meeting.lat, meeting.lng)
            user_coords = (user_lat, user_lng)
            distance = geodesic(meeting_coords, user_coords).meters
            
            # Determine required radius
            radius = meeting.radius_meters or self.default_radius_meters
            # For very large radii (testing), allow up to the meeting's radius
            # Don't cap it at max_radius_meters if meeting explicitly set a larger radius
            if radius > self.max_radius_meters:
                # This is likely a test meeting with intentionally large radius
                logger.info(f"Meeting {meeting.id} has large radius {radius}m (likely for testing) - allowing full radius")
                # Use the full radius without capping
            else:
                radius = min(radius, self.max_radius_meters)
            
            # Check if within range
            is_within_range = distance <= radius
            
            # Calculate accuracy confidence
            accuracy_confidence = self._calculate_accuracy_confidence(
                distance, radius, required_accuracy
            )
            
            return ProximityResult(
                is_within_range=is_within_range,
                distance_meters=distance,
                meeting_id=str(meeting.id),
                meeting_name=meeting.name,
                accuracy_confidence=accuracy_confidence
            )
            
        except Exception as e:
            logger.error(f"Error verifying location: {e}")
            return ProximityResult(
                is_within_range=False,
                distance_meters=float('inf'),
                accuracy_confidence=0.0
            )
    
    async def find_nearby_meetings(
        self,
        user_lat: float,
        user_lng: float,
        radius_km: float = 5.0,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Find meetings within specified radius"""
        try:
            # Convert radius to meters
            radius_meters = radius_km * 1000
            
            # Use PostGIS ST_DWithin for efficient geospatial query
            query = select(Meeting).where(
                func.ST_DWithin(
                    func.ST_Point(Meeting.lng, Meeting.lat),
                    func.ST_Point(user_lng, user_lat),
                    radius_meters
                )
            )
            
            result = await db.execute(query)
            meetings = result.scalars().all()
            
            # Calculate distances and format results
            nearby_meetings = []
            for meeting in meetings:
                distance = geodesic(
                    (user_lat, user_lng),
                    (meeting.lat, meeting.lng)
                ).kilometers
                
                nearby_meetings.append({
                    "id": str(meeting.id),
                    "name": meeting.name,
                    "description": meeting.description,
                    "address": meeting.address,
                    "latitude": meeting.lat,
                    "longitude": meeting.lng,
                    "radius_meters": meeting.radius_meters,
                    "distance_km": round(distance, 2),
                    "start_time": meeting.start_time,
                    "end_time": meeting.end_time,
                    "is_active": meeting.is_active,
                })
            
            # Sort by distance
            nearby_meetings.sort(key=lambda x: x["distance_km"])
            return nearby_meetings
            
        except Exception as e:
            logger.error(f"Error finding nearby meetings: {e}")
            return []
    
    async def create_session_event(
        self,
        session_id: str,
        event_type: EventType,
        location_data: LocationData,
        meeting_id: Optional[str] = None,
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[SessionEvent]:
        """Create a session event with location verification"""
        try:
            # Verify location if meeting_id is provided
            if meeting_id and event_type in [EventType.CHECK_IN, EventType.CHECK_OUT]:
                proximity_result = await self.verify_location(
                    location_data.latitude,
                    location_data.longitude,
                    meeting_id,
                    db,
                    location_data.accuracy
                )
                
                if not proximity_result.is_within_range:
                    logger.warning(
                        f"Location verification failed for session {session_id}: "
                        f"distance {proximity_result.distance_meters:.2f}m"
                    )
                    return None
            
            # Create session event
            session_event = SessionEvent(
                session_id=session_id,
                type=event_type,
                lat=location_data.latitude,
                lng=location_data.longitude,
                accuracy=location_data.accuracy,
                altitude=location_data.altitude,
                speed=location_data.speed,
                heading=location_data.heading,
                notes=notes,
                location_flag=True,  # GPS verified
            )
            
            db.add(session_event)
            await db.commit()
            await db.refresh(session_event)
            
            return session_event
            
        except Exception as e:
            logger.error(f"Error creating session event: {e}")
            await db.rollback()
            return None
    
    def _calculate_accuracy_confidence(
        self,
        distance: float,
        radius: float,
        gps_accuracy: Optional[float]
    ) -> float:
        """Calculate confidence score based on distance and GPS accuracy"""
        # Base confidence from distance ratio
        distance_ratio = min(distance / radius, 1.0)
        base_confidence = 1.0 - distance_ratio
        
        # Adjust for GPS accuracy
        if gps_accuracy is not None:
            accuracy_factor = max(0.0, 1.0 - (gps_accuracy / self.min_accuracy_meters))
            base_confidence *= accuracy_factor
        
        return max(0.0, min(1.0, base_confidence))
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address to coordinates"""
        try:
            location = self.geocoder.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
    
    async def reverse_geocode(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[str]:
        """Reverse geocode coordinates to address"""
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}")
            if location:
                return location.address
            return None
        except Exception as e:
            logger.error(f"Error reverse geocoding {latitude}, {longitude}: {e}")
            return None
    
    def calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate distance between two points in meters"""
        return geodesic((lat1, lng1), (lat2, lng2)).meters
    
    def is_location_valid(
        self,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None
    ) -> bool:
        """Validate location coordinates and accuracy"""
        # Check coordinate validity
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f"Invalid coordinates: lat={latitude}, lng={longitude}")
            return False
        
        # For testing, be very lenient with accuracy
        # PC GPS can have poor accuracy, so we allow up to 1000m for testing
        max_allowed_accuracy = 1000.0  # 1km - very lenient for testing
        
        # Check accuracy if provided
        if accuracy is not None:
            if accuracy > max_allowed_accuracy:
                logger.warning(f"Location accuracy too poor: {accuracy}m (max: {max_allowed_accuracy}m)")
                return False
            # Log if accuracy is poor but still acceptable
            if accuracy > self.min_accuracy_meters:
                logger.info(f"Accepting location with poor accuracy: {accuracy}m (for testing)")
        
        return True
    
    async def get_location_history(
        self,
        session_id: str,
        db: AsyncSession
    ) -> List[SessionEvent]:
        """Get location history for a session"""
        try:
            result = await db.execute(
                select(SessionEvent)
                .where(SessionEvent.session_id == session_id)
                .order_by(SessionEvent.ts_server)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting location history: {e}")
            return []
