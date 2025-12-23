"""
Real location service tests without mocks, simulations, or hardcoded responses
Tests actual location service operations with real database and calculations
"""

import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.services.location_service import LocationService, LocationData, ProximityResult
from app.models.base import Base
from app.models.meeting import Meeting
from app.models.contact import Contact
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType


class TestLocationServiceReal:
    """Real location service tests using actual implementations"""
    
    @pytest.fixture
    async def real_database(self):
        """Create real database for testing"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        yield async_session
        
        # Cleanup
        await engine.dispose()
    
    @pytest.fixture
    def real_location_service(self):
        """Create real location service instance"""
        return LocationService()
    
    @pytest.fixture
    async def real_contact(self, real_database):
        """Create real contact in database"""
        async with real_database() as db:
            contact = Contact(
                email="location-test@example.com",
                first_name="Location",
                last_name="Test",
                phone="+1234567890",
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            return contact
    
    @pytest.fixture
    async def real_meeting(self, real_database):
        """Create real meeting in database"""
        async with real_database() as db:
            meeting = Meeting(
                name="Real Location Test Meeting",
                description="A real test meeting for location services",
                address="123 Real Test Street, Test City, TC 12345",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=True
            )
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            return meeting
    
    @pytest.fixture
    def sample_location_data(self):
        """Create sample location data"""
        return LocationData(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=10.0,
            altitude=10.0,
            speed=0.0,
            heading=0.0,
            timestamp=datetime.utcnow().timestamp()
        )
    
    @pytest.mark.asyncio
    async def test_verify_location_success_real(self, real_location_service, real_database, sample_location_data, real_meeting):
        """Test successful location verification with real database and calculations"""
        async with real_database() as db:
            # Test location verification with real data
            result = await real_location_service.verify_location(
                meeting_id=str(real_meeting.id),
                location_data=sample_location_data,
                db=db
            )
            
            assert result is not None
            assert result.is_within_range == True  # Should be within range
            assert result.distance_meters >= 0
            assert result.meeting_id == str(real_meeting.id)
            assert result.meeting_name == "Real Location Test Meeting"
            assert result.accuracy_confidence > 0
            assert result.accuracy_confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_verify_location_out_of_range_real(self, real_location_service, real_database, real_meeting):
        """Test location verification when out of range with real calculations"""
        async with real_database() as db:
            # Create location data far from meeting
            far_location_data = LocationData(
                latitude=40.7589,  # Different location
                longitude=-73.9851,
                accuracy=10.0,
                altitude=10.0,
                speed=0.0,
                heading=0.0,
                timestamp=datetime.utcnow().timestamp()
            )
            
            result = await real_location_service.verify_location(
                meeting_id=str(real_meeting.id),
                location_data=far_location_data,
                db=db
            )
            
            assert result is not None
            assert result.is_within_range == False  # Should be out of range
            assert result.distance_meters > real_meeting.radius_meters
            assert result.meeting_id == str(real_meeting.id)
            assert result.meeting_name == "Real Location Test Meeting"
            assert result.accuracy_confidence > 0
    
    @pytest.mark.asyncio
    async def test_verify_location_meeting_not_found_real(self, real_location_service, real_database, sample_location_data):
        """Test location verification with non-existent meeting"""
        async with real_database() as db:
            # Test with non-existent meeting ID
            result = await real_location_service.verify_location(
                meeting_id="non-existent-id",
                location_data=sample_location_data,
                db=db
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_location_inactive_meeting_real(self, real_location_service, real_database, sample_location_data):
        """Test location verification with inactive meeting"""
        async with real_database() as db:
            # Create inactive meeting
            inactive_meeting = Meeting(
                name="Inactive Meeting",
                description="An inactive meeting",
                address="123 Inactive St",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=False
            )
            db.add(inactive_meeting)
            await db.commit()
            await db.refresh(inactive_meeting)
            
            result = await real_location_service.verify_location(
                meeting_id=str(inactive_meeting.id),
                location_data=sample_location_data,
                db=db
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_create_session_event_real(self, real_location_service, real_database, real_contact, real_meeting):
        """Test creating session event with real database operations"""
        async with real_database() as db:
            # Create real session first
            session = Session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                status=SessionStatus.ACTIVE,
                session_notes="Real session for event testing"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            # Create session event
            event = await real_location_service.create_session_event(
                session_id=session.id,
                type=EventType.CHECK_IN,
                lat=40.7128,
                lng=-74.0060,
                accuracy=10.0,
                location_flag=True,
                notes="Real check-in event",
                db=db
            )
            
            assert event is not None
            assert event.session_id == session.id
            assert event.type == EventType.CHECK_IN
            assert event.lat == 40.7128
            assert event.lng == -74.0060
            assert event.accuracy == 10.0
            assert event.location_flag == True
            assert event.notes == "Real check-in event"
            assert event.id is not None
            assert event.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_session_event_invalid_session_real(self, real_location_service, real_database):
        """Test creating session event with invalid session ID"""
        async with real_database() as db:
            # Try to create event with non-existent session
            event = await real_location_service.create_session_event(
                session_id="non-existent-session-id",
                type=EventType.CHECK_IN,
                lat=40.7128,
                lng=-74.0060,
                accuracy=10.0,
                location_flag=True,
                notes="Test event",
                db=db
            )
            
            assert event is None
    
    @pytest.mark.asyncio
    async def test_get_nearby_meetings_real(self, real_location_service, real_database, real_contact):
        """Test getting nearby meetings with real location calculations"""
        async with real_database() as db:
            # Create multiple real meetings at different locations
            meetings = [
                Meeting(
                    name="Meeting 1",
                    description="First meeting",
                    address="123 Test St",
                    lat=40.7128,
                    lng=-74.0060,
                    radius_meters=100,
                    is_active=True
                ),
                Meeting(
                    name="Meeting 2",
                    description="Second meeting",
                    address="456 Test Ave",
                    lat=40.7589,
                    lng=-73.9851,
                    radius_meters=100,
                    is_active=True
                ),
                Meeting(
                    name="Meeting 3",
                    description="Third meeting",
                    address="789 Test Blvd",
                    lat=40.6892,
                    lng=-74.0445,
                    radius_meters=100,
                    is_active=True
                )
            ]
            
            for meeting in meetings:
                db.add(meeting)
            await db.commit()
            
            # Test nearby meetings from NYC location
            nearby_meetings = await real_location_service.get_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=True,
                db=db
            )
            
            assert len(nearby_meetings) >= 3  # Should find all meetings
            
            # Verify meeting data structure
            for meeting in nearby_meetings:
                assert hasattr(meeting, 'id')
                assert hasattr(meeting, 'name')
                assert hasattr(meeting, 'lat')
                assert hasattr(meeting, 'lng')
                assert hasattr(meeting, 'radius_meters')
                assert hasattr(meeting, 'is_active')
                assert hasattr(meeting, 'distance_meters')
    
    @pytest.mark.asyncio
    async def test_get_nearby_meetings_empty_real(self, real_location_service, real_database):
        """Test getting nearby meetings when none exist"""
        async with real_database() as db:
            # Test with no meetings in database
            nearby_meetings = await real_location_service.get_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=True,
                db=db
            )
            
            assert len(nearby_meetings) == 0
    
    def test_calculate_distance_real(self, real_location_service):
        """Test real distance calculation with actual coordinates"""
        # Test same location
        distance = real_location_service.calculate_distance(
            lat1=40.7128,
            lng1=-74.0060,
            lat2=40.7128,
            lng2=-74.0060
        )
        assert distance == 0.0
        
        # Test different locations (NYC to Philadelphia)
        distance = real_location_service.calculate_distance(
            lat1=40.7128,
            lng1=-74.0060,  # NYC
            lat2=39.9526,
            lng2=-75.1652   # Philadelphia
        )
        assert distance > 0
        assert distance < 200000  # Should be less than 200km
        
        # Test edge case coordinates
        distance = real_location_service.calculate_distance(
            lat1=0.0,
            lng1=0.0,
            lat2=0.0,
            lng2=0.0
        )
        assert distance == 0.0
    
    def test_calculate_accuracy_confidence_real(self, real_location_service):
        """Test real accuracy confidence calculation"""
        # Test with good accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            distance=50.0,
            radius=100.0,
            gps_accuracy=10.0
        )
        assert confidence > 0.3  # Should be reasonable confidence
        
        # Test with poor accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            distance=50.0,
            radius=100.0,
            gps_accuracy=1000.0
        )
        assert confidence < 0.5  # Should be low confidence
        
        # Test with perfect accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            distance=50.0,
            radius=100.0,
            gps_accuracy=0.0
        )
        assert confidence == 1.0  # Perfect accuracy
    
    def test_validate_coordinates_real(self, real_location_service):
        """Test real coordinate validation"""
        # Test valid coordinates
        assert real_location_service.is_location_valid(40.7128, -74.0060) == True
        assert real_location_service.is_location_valid(0.0, 0.0) == True
        assert real_location_service.is_location_valid(-90.0, -180.0) == True
        assert real_location_service.is_location_valid(90.0, 180.0) == True
        
        # Test invalid coordinates
        assert real_location_service.is_location_valid(91.0, -74.0060) == False
        assert real_location_service.is_location_valid(-91.0, -74.0060) == False
        assert real_location_service.is_location_valid(40.7128, 181.0) == False
        assert real_location_service.is_location_valid(40.7128, -181.0) == False
    
    def test_validate_accuracy_real(self, real_location_service):
        """Test real accuracy validation"""
        # Test valid accuracy
        assert real_location_service.is_location_valid(40.7128, -74.0060, 10.0) == True
        assert real_location_service.is_location_valid(40.7128, -74.0060,0.0) == True
        assert real_location_service.is_location_valid(40.7128, -74.0060,1000.0) == True
        
        # Test invalid accuracy
        assert real_location_service.is_location_valid(40.7128, -74.0060,-1.0) == False
        assert real_location_service.is_location_valid(40.7128, -74.0060,None) == False
    
    @pytest.mark.asyncio
    async def test_real_database_operations(self, real_database):
        """Test real database operations and data persistence"""
        async with real_database() as db:
            # Test basic database query
            result = await db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
            
            # Test table existence
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            assert "meetings" in table_names
            assert "sessions" in table_names
            assert "session_events" in table_names
    
    @pytest.mark.asyncio
    async def test_real_location_verification_persistence(self, real_location_service, real_database, sample_location_data, real_meeting):
        """Test real location verification and data persistence"""
        async with real_database() as db:
            # Test location verification
            result = await real_location_service.verify_location(
                meeting_id=str(real_meeting.id),
                location_data=sample_location_data,
                db=db
            )
            
            assert result is not None
            assert result.is_within_range == True
            
            # Verify meeting data was correctly retrieved from database
            result = await db.execute(
                text("SELECT * FROM meetings WHERE id = :meeting_id"),
                {"meeting_id": real_meeting.id}
            )
            db_meeting = result.fetchone()
            assert db_meeting is not None
            assert db_meeting[1] == "Real Location Test Meeting"  # name column
            assert db_meeting[4] == 40.7128  # lat column
            assert db_meeting[5] == -74.0060  # lng column
            assert db_meeting[6] == 100  # radius_meters column
    
    @pytest.mark.asyncio
    async def test_real_session_event_persistence(self, real_location_service, real_database, real_contact, real_meeting):
        """Test real session event creation and data persistence"""
        async with real_database() as db:
            # Create real session
            session = Session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                status=SessionStatus.ACTIVE,
                session_notes="Real session for event testing"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            # Create session event
            event = await real_location_service.create_session_event(
                session_id=session.id,
                type=EventType.CHECK_IN,
                lat=40.7128,
                lng=-74.0060,
                accuracy=10.0,
                location_flag=True,
                notes="Real check-in event",
                db=db
            )
            
            assert event is not None
            
            # Verify event was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM session_events WHERE id = :event_id"),
                {"event_id": event.id}
            )
            db_event = result.fetchone()
            assert db_event is not None
            assert db_event[1] == session.id  # session_id column
            assert db_event[2] == "check_in"  # type column
            assert db_event[3] == 40.7128  # lat column
            assert db_event[4] == -74.0060  # lng column
            assert db_event[5] == 10.0  # accuracy column
            assert db_event[6] == True  # location_flag column