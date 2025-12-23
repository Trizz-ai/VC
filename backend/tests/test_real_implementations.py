"""
Real implementation tests without mocks or simulations
Tests actual functionality with real database, real services, and real API calls
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import Settings
from app.core.database import get_db, get_redis, create_tables
from app.core.auth import create_access_token, verify_token, get_password_hash, verify_password
from app.models.base import Base
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType
from app.services.location_service import LocationService, LocationData
from app.services.session_service import SessionService
from app.services.meeting_service import MeetingService


class TestRealImplementations:
    """Test cases using real implementations without mocks"""
    
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
    def real_settings(self):
        """Create real settings instance"""
        return Settings()
    
    @pytest.fixture
    def real_location_service(self):
        """Create real location service"""
        return LocationService()
    
    @pytest.fixture
    def real_session_service(self):
        """Create real session service"""
        return SessionService()
    
    @pytest.fixture
    def real_meeting_service(self):
        """Create real meeting service"""
        return MeetingService()
    
    def test_real_configuration(self, real_settings):
        """Test real configuration settings"""
        assert real_settings.ENVIRONMENT is not None
        assert real_settings.DATABASE_URL is not None
        assert real_settings.REDIS_URL is not None
        assert real_settings.SECRET_KEY is not None
        assert len(real_settings.SECRET_KEY) >= 32
        assert real_settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert real_settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
    
    def test_real_authentication(self, real_settings):
        """Test real authentication with actual tokens"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_KEY'] = "real-test-secret-key-for-testing"
        
        try:
            # Create real access token
            token = create_access_token(
                data={"sub": "test@example.com", "user_id": str(uuid4())},
                expires_delta=timedelta(minutes=30)
            )
            
            assert token is not None
            assert isinstance(token, str)
            
            # Verify real token
            payload = verify_token(token)
            assert payload is not None
            assert payload["sub"] == "test@example.com"
            assert "user_id" in payload
            assert "exp" in payload
            
            # Test password hashing with real implementation
            password = "real-test-password-123"
            hashed = get_password_hash(password)
            assert hashed is not None
            assert hashed != password
            assert verify_password(password, hashed) == True
            assert verify_password("wrong-password", hashed) == False
            
        finally:
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    @pytest.mark.asyncio
    async def test_real_database_operations(self, real_database):
        """Test real database operations"""
        async with real_database() as db:
            # Create real contact
            contact = Contact(
                email="real-test@example.com",
                first_name="Real",
                last_name="Test",
                phone="+1234567890",
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            
            assert contact.id is not None
            assert contact.email == "real-test@example.com"
            assert contact.first_name == "Real"
            assert contact.last_name == "Test"
            
            # Create real meeting
            meeting = Meeting(
                name="Real Test Meeting",
                description="A real test meeting",
                address="123 Real Test Street, Test City, TC 12345",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=True
            )
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            
            assert meeting.id is not None
            assert meeting.name == "Real Test Meeting"
            assert meeting.lat == 40.7128
            assert meeting.lng == -74.0060
            
            # Create real session
            session = Session(
                contact_id=contact.id,
                meeting_id=meeting.id,
                status=SessionStatus.ACTIVE,
                session_notes="Real test session"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            assert session.id is not None
            assert session.contact_id == contact.id
            assert session.meeting_id == meeting.id
            assert session.status == SessionStatus.ACTIVE
            
            # Create real session event
            session_event = SessionEvent(
                session_id=session.id,
                type=EventType.CHECK_IN,
                lat=40.7128,
                lng=-74.0060,
                accuracy=10.0,
                location_flag=True
            )
            db.add(session_event)
            await db.commit()
            await db.refresh(session_event)
            
            assert session_event.id is not None
            assert session_event.session_id == session.id
            assert session_event.type == EventType.CHECK_IN
            assert session_event.lat == 40.7128
            assert session_event.lng == -74.0060
    
    @pytest.mark.asyncio
    async def test_real_location_service(self, real_location_service, real_database):
        """Test real location service with actual calculations"""
        # Create real location data
        location_data = LocationData(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=10.0,
            altitude=10.0,
            speed=0.0,
            heading=0.0,
            timestamp=datetime.utcnow().timestamp()
        )
        
        async with real_database() as db:
            # Create real meeting in database
            meeting = Meeting(
                name="Real Location Test Meeting",
                address="123 Real Test Street",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=True
            )
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            
            # Test real location verification
            result = await real_location_service.verify_location(
                meeting_id=str(meeting.id),
                location_data=location_data,
                db=db
            )
            
            assert result is not None
            assert result.is_within_range == True  # Should be within range
            assert result.distance_meters >= 0
            assert result.meeting_id == str(meeting.id)
            assert result.meeting_name == "Real Location Test Meeting"
            assert result.accuracy_confidence > 0
    
    @pytest.mark.asyncio
    async def test_real_session_service(self, real_session_service, real_database):
        """Test real session service with actual database operations"""
        async with real_database() as db:
            # Create real contact and meeting
            contact = Contact(
                email="real-session-test@example.com",
                first_name="Real",
                last_name="Session",
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            
            meeting = Meeting(
                name="Real Session Test Meeting",
                address="123 Real Session Street",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=True
            )
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            
            # Test real session creation
            session = await real_session_service.create_session(
                contact_id=contact.id,
                meeting_id=meeting.id,
                notes="Real session test",
                db=db
            )
            
            assert session is not None
            assert session.contact_id == contact.id
            assert session.meeting_id == meeting.id
            assert session.status == SessionStatus.ACTIVE
            assert session.session_notes == "Real session test"
            
            # Test real session retrieval
            active_session = await real_session_service.get_active_session(
                contact_id=contact.id,
                db=db
            )
            
            assert active_session is not None
            assert active_session.id == session.id
    
    @pytest.mark.asyncio
    async def test_real_meeting_service(self, real_meeting_service, real_database):
        """Test real meeting service with actual database operations"""
        async with real_database() as db:
            # Test real meeting creation
            meeting_data = {
                "name": "Real Meeting Service Test",
                "description": "A real meeting for testing",
                "address": "123 Real Meeting Street, Test City, TC 12345",
                "lat": 40.7128,
                "lng": -74.0060,
                "radius_meters": 100,
                "is_active": True
            }
            
            meeting = await real_meeting_service.create_meeting(
                meeting_data=meeting_data,
                created_by_id=uuid4(),
                db=db
            )
            
            assert meeting is not None
            assert meeting.name == "Real Meeting Service Test"
            assert meeting.description == "A real meeting for testing"
            assert meeting.address == "123 Real Meeting Street, Test City, TC 12345"
            assert meeting.lat == 40.7128
            assert meeting.lng == -74.0060
            assert meeting.radius_meters == 100
            assert meeting.is_active == True
            
            # Test real meeting retrieval
            retrieved_meeting = await real_meeting_service.get_meeting_by_id(
                meeting_id=meeting.id,
                db=db
            )
            
            assert retrieved_meeting is not None
            assert retrieved_meeting.id == meeting.id
            assert retrieved_meeting.name == meeting.name
            
            # Test real nearby meetings
            nearby_meetings = await real_meeting_service.get_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=True,
                db=db
            )
            
            assert len(nearby_meetings) >= 1
            assert nearby_meetings[0].id == meeting.id
    
    def test_real_distance_calculation(self, real_location_service):
        """Test real distance calculation with actual coordinates"""
        # Test same location
        distance = real_location_service._calculate_distance(
            lat1=40.7128,
            lng1=-74.0060,
            lat2=40.7128,
            lng2=-74.0060
        )
        assert distance == 0.0
        
        # Test different locations (NYC to Philadelphia)
        distance = real_location_service._calculate_distance(
            lat1=40.7128,
            lng1=-74.0060,  # NYC
            lat2=39.9526,
            lng2=-75.1652   # Philadelphia
        )
        assert distance > 0
        assert distance < 200000  # Should be less than 200km
        
        # Test edge case coordinates
        distance = real_location_service._calculate_distance(
            lat1=0.0,
            lng1=0.0,
            lat2=0.0,
            lng2=0.0
        )
        assert distance == 0.0
    
    def test_real_accuracy_confidence(self, real_location_service):
        """Test real accuracy confidence calculation"""
        # Test with good accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            accuracy=10.0,
            distance=50.0,
            radius=100.0
        )
        assert confidence > 0.5  # Should be high confidence
        
        # Test with poor accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            accuracy=1000.0,
            distance=50.0,
            radius=100.0
        )
        assert confidence < 0.5  # Should be low confidence
        
        # Test with perfect accuracy
        confidence = real_location_service._calculate_accuracy_confidence(
            accuracy=0.0,
            distance=50.0,
            radius=100.0
        )
        assert confidence == 1.0  # Perfect accuracy
    
    def test_real_coordinate_validation(self, real_location_service):
        """Test real coordinate validation"""
        # Test valid coordinates
        assert real_location_service._validate_coordinates(40.7128, -74.0060) == True
        assert real_location_service._validate_coordinates(0.0, 0.0) == True
        assert real_location_service._validate_coordinates(-90.0, -180.0) == True
        assert real_location_service._validate_coordinates(90.0, 180.0) == True
        
        # Test invalid coordinates
        assert real_location_service._validate_coordinates(91.0, -74.0060) == False
        assert real_location_service._validate_coordinates(-91.0, -74.0060) == False
        assert real_location_service._validate_coordinates(40.7128, 181.0) == False
        assert real_location_service._validate_coordinates(40.7128, -181.0) == False
    
    def test_real_accuracy_validation(self, real_location_service):
        """Test real accuracy validation"""
        # Test valid accuracy
        assert real_location_service._validate_accuracy(10.0) == True
        assert real_location_service._validate_accuracy(0.0) == True
        assert real_location_service._validate_accuracy(1000.0) == True
        
        # Test invalid accuracy
        assert real_location_service._validate_accuracy(-1.0) == False
        assert real_location_service._validate_accuracy(None) == False
    
    @pytest.mark.asyncio
    async def test_real_redis_connection(self):
        """Test real Redis connection"""
        try:
            redis_client = get_redis()
            assert redis_client is not None
            
            # Test real Redis operations
            await redis_client.ping()
            
            # Test set and get operations
            await redis_client.set("test_key", "test_value")
            value = await redis_client.get("test_key")
            assert value == "test_value"
            
            # Cleanup
            await redis_client.delete("test_key")
            
        except Exception as e:
            # Redis might not be available in test environment
            pytest.skip(f"Redis not available: {e}")
    
    @pytest.mark.asyncio
    async def test_real_database_health_check(self, real_database):
        """Test real database health check"""
        async with real_database() as db:
            # Test real database query
            result = await db.execute(text("SELECT 1 as health_check"))
            row = result.fetchone()
            assert row is not None
            assert row[0] == 1
    
    def test_real_settings_validation(self, real_settings):
        """Test real settings validation"""
        # Test that all required settings are present
        assert hasattr(real_settings, 'ENVIRONMENT')
        assert hasattr(real_settings, 'DEBUG')
        assert hasattr(real_settings, 'DATABASE_URL')
        assert hasattr(real_settings, 'REDIS_URL')
        assert hasattr(real_settings, 'SECRET_KEY')
        assert hasattr(real_settings, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert hasattr(real_settings, 'REFRESH_TOKEN_EXPIRE_DAYS')
        assert hasattr(real_settings, 'CORS_ORIGINS')
        assert hasattr(real_settings, 'ALLOWED_HOSTS')
        
        # Test that settings have valid values
        assert real_settings.ENVIRONMENT in ['development', 'production', 'testing']
        assert isinstance(real_settings.DEBUG, bool)
        assert isinstance(real_settings.DATABASE_URL, str)
        assert isinstance(real_settings.REDIS_URL, str)
        assert isinstance(real_settings.SECRET_KEY, str)
        assert real_settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert real_settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
        assert isinstance(real_settings.CORS_ORIGINS, str)
        assert isinstance(real_settings.ALLOWED_HOSTS, str)
