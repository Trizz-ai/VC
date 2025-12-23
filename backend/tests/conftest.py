"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
import uuid
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.sqlite import CHAR

from app.core.database import get_db
from app.core.database_sqlite import get_sqlite_db, create_sqlite_tables
from app.models.base import Base
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType


# Test configuration for SQLite compatibility


# Remove custom event_loop fixture to use pytest-asyncio's default


@pytest.fixture
def loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create test database with SQLite compatibility"""
    # Create SQLite-compatible tables
    await create_sqlite_tables()
    
    # Return the SQLite session factory
    from app.core.database_sqlite import SQLiteSessionLocal
    yield SQLiteSessionLocal


@pytest.fixture
async def real_database():
    """Create real database for testing with proper async handling"""
    # Use file-based SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///test_real.db",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
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
async def db_session(test_db):
    """Create database session for testing"""
    async with test_db() as session:
        yield session


@pytest.fixture
def sample_contact():
    """Create sample contact for testing"""
    return Contact(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone="+1234567890",
        consent_granted=True
    )


@pytest.fixture
def sample_meeting():
    """Create sample meeting for testing"""
    return Meeting(
        name="Test Meeting",
        description="A test meeting",
        address="123 Test Street, Test City, TC 12345",
        lat=40.7128,
        lng=-74.0060,
        radius_meters=100,
        is_active=True
    )


@pytest.fixture
def sample_session(sample_contact, sample_meeting):
    """Create sample session for testing"""
    return Session(
        contact_id=sample_contact.id,
        meeting_id=sample_meeting.id,
        status=SessionStatus.ACTIVE,
        session_notes="Test session"
    )


@pytest.fixture
def sample_session_event(sample_session):
    """Create sample session event for testing"""
    return SessionEvent(
        session_id=sample_session.id,
        type=EventType.CHECK_IN,
        lat=40.7128,
        lng=-74.0060,
        accuracy=10.0,
        location_flag=True
    )


@pytest.fixture
def mock_redis():
    """Create mock Redis client"""
    return AsyncMock()


@pytest.fixture
def mock_ghl_service():
    """Create mock GHL service"""
    return AsyncMock()


@pytest.fixture
def mock_google_maps_service():
    """Create mock Google Maps service"""
    return AsyncMock()


@pytest.fixture
def mock_email_service():
    """Create mock email service"""
    return AsyncMock()


@pytest.fixture
def mock_notification_service():
    """Create mock notification service"""
    return AsyncMock()


@pytest.fixture
def mock_location_service():
    """Create mock location service"""
    return AsyncMock()


@pytest.fixture
def mock_session_service():
    """Create mock session service"""
    return AsyncMock()


@pytest.fixture
def mock_meeting_service():
    """Create mock meeting service"""
    return AsyncMock()


@pytest.fixture
def mock_offline_service():
    """Create mock offline service"""
    return AsyncMock()


@pytest.fixture
def mock_auth_service():
    """Create mock auth service"""
    return AsyncMock()


@pytest.fixture
def sample_location_data():
    """Create sample location data"""
    from app.services.location_service import LocationData
    return LocationData(
        latitude=40.7128,
        longitude=-74.0060,
        accuracy=10.0,
        altitude=10.0,
        speed=0.0,
        heading=0.0,
        timestamp=1234567890.0
    )


@pytest.fixture
def sample_proximity_result():
    """Create sample proximity result"""
    from app.services.location_service import ProximityResult
    return ProximityResult(
        is_within_range=True,
        distance_meters=50.0,
        meeting_id="test-meeting-id",
        meeting_name="Test Meeting",
        accuracy_confidence=0.9
    )


@pytest.fixture
def sample_offline_operation():
    """Create sample offline operation"""
    from app.services.offline_service import OfflineOperation
    return OfflineOperation(
        operation_type="check_in",
        data={"latitude": 40.7128, "longitude": -74.0060},
        user_id="123e4567-e89b-12d3-a456-426614174000",
        priority=1
    )


@pytest.fixture
def sample_ghl_webhook():
    """Create sample GHL webhook data"""
    return {
        "type": "ContactCreate",
        "contact": {
            "id": "ghl_contact_123",
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "phone": "+1234567890"
        }
    }


@pytest.fixture
def sample_fcm_notification():
    """Create sample FCM notification"""
    return {
        "to": "device_token_123",
        "notification": {
            "title": "Test Notification",
            "body": "This is a test notification"
        },
        "data": {
            "type": "test",
            "session_id": "123e4567-e89b-12d3-a456-426614174002"
        }
    }


@pytest.fixture
def sample_sendgrid_email():
    """Create sample SendGrid email"""
    return {
        "to": "test@example.com",
        "subject": "Test Email",
        "html_content": "<h1>Test Email</h1>",
        "text_content": "Test Email"
    }


@pytest.fixture
def sample_google_maps_response():
    """Create sample Google Maps API response"""
    return {
        "status": "OK",
        "results": [
            {
                "formatted_address": "123 Test Street, Test City, TC 12345, USA",
                "geometry": {
                    "location": {
                        "lat": 40.7128,
                        "lng": -74.0060
                    }
                }
            }
        ]
    }


@pytest.fixture
def sample_static_map_url():
    """Create sample static map URL"""
    return "https://maps.googleapis.com/maps/api/staticmap?center=40.7128,-74.0060&zoom=15&size=400x400&maptype=roadmap&markers=color:red|40.7128,-74.0060&key=test_key"


@pytest.fixture
def sample_directions_response():
    """Create sample directions response"""
    return {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "distance": {"text": "1.0 km", "value": 1000},
                        "duration": {"text": "5 mins", "value": 300},
                        "start_address": "123 Start St, City, State",
                        "end_address": "456 End St, City, State"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_distance_matrix_response():
    """Create sample distance matrix response"""
    return {
        "status": "OK",
        "rows": [
            {
                "elements": [
                    {
                        "status": "OK",
                        "distance": {"text": "1.0 km", "value": 1000},
                        "duration": {"text": "5 mins", "value": 300}
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_elevation_response():
    """Create sample elevation response"""
    return {
        "status": "OK",
        "results": [
            {
                "elevation": 10.0,
                "location": {"lat": 40.7128, "lng": -74.0060}
            }
        ]
    }


@pytest.fixture
def sample_timezone_response():
    """Create sample timezone response"""
    return {
        "status": "OK",
        "timeZoneId": "America/New_York",
        "timeZoneName": "Eastern Standard Time"
    }


@pytest.fixture
def sample_place_details_response():
    """Create sample place details response"""
    return {
        "status": "OK",
        "result": {
            "name": "Test Place",
            "formatted_address": "123 Test Street, Test City, TC 12345",
            "geometry": {
                "location": {"lat": 40.7128, "lng": -74.0060}
            },
            "types": ["establishment"],
            "rating": 4.5,
            "user_ratings_total": 100
        }
    }


@pytest.fixture
def sample_nearby_places_response():
    """Create sample nearby places response"""
    return {
        "status": "OK",
        "results": [
            {
                "name": "Nearby Place 1",
                "place_id": "place_123",
                "geometry": {
                    "location": {"lat": 40.7128, "lng": -74.0060}
                },
                "types": ["establishment"],
                "rating": 4.0
            }
        ]
    }


@pytest.fixture
def sample_attendance_statistics():
    """Create sample attendance statistics"""
    return {
        "total_sessions": 10,
        "status_breakdown": {
            "completed": 8,
            "active": 1,
            "ended": 1
        },
        "completed_sessions": 8,
        "average_duration_minutes": 45.5,
        "date_range": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-31T23:59:59Z"
        }
    }


@pytest.fixture
def sample_meeting_statistics():
    """Create sample meeting statistics"""
    return {
        "meeting_id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Test Meeting",
        "is_active": True,
        "is_currently_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T11:00:00Z",
        "location": {
            "address": "123 Test Street, Test City, TC 12345",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius_meters": 100
        }
    }


@pytest.fixture
def sample_offline_queue_status():
    """Create sample offline queue status"""
    return {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "status_counts": {
            "pending": 5,
            "processing": 1,
            "failed": 2,
            "total": 8
        },
        "pending_count": 5,
        "failed_count": 2,
        "oldest_pending": "2024-01-01T00:00:00Z",
        "newest_failed": "2024-01-01T12:00:00Z"
    }


@pytest.fixture
def sample_offline_process_result():
    """Create sample offline process result"""
    return {
        "processed": 3,
        "failed": 1,
        "total": 4
    }


@pytest.fixture
def sample_ghl_contact():
    """Create sample GHL contact"""
    return {
        "id": "ghl_contact_123",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "phone": "+1234567890",
        "tags": ["verified-compliance", "attendance-tracking"],
        "customFields": [
            {"key": "consent_granted", "value": "true"},
            {"key": "app_user_id", "value": "123e4567-e89b-12d3-a456-426614174000"}
        ]
    }


@pytest.fixture
def sample_ghl_opportunity():
    """Create sample GHL opportunity"""
    return {
        "id": "ghl_opportunity_123",
        "contactId": "ghl_contact_123",
        "name": "Attendance - Test Meeting",
        "status": "attended",
        "source": "Verified Compliance App",
        "tags": ["attendance", "verified-compliance", "test-meeting"],
        "customFields": [
            {"key": "session_id", "value": "123e4567-e89b-12d3-a456-426614174002"},
            {"key": "meeting_name", "value": "Test Meeting"}
        ]
    }


@pytest.fixture
def sample_ghl_task():
    """Create sample GHL task"""
    return {
        "id": "ghl_task_123",
        "contactId": "ghl_contact_123",
        "title": "Follow up on attendance",
        "description": "Follow up with user about their attendance at Test Meeting",
        "status": "pending",
        "tags": ["verified-compliance", "automated"]
    }


@pytest.fixture
def sample_ghl_webhook_response():
    """Create sample GHL webhook response"""
    return {
        "status": "success",
        "message": "Webhook processed"
    }


@pytest.fixture
def sample_sendgrid_response():
    """Create sample SendGrid response"""
    return {
        "status_code": 202,
        "message": "Email sent successfully"
    }


@pytest.fixture
def sample_fcm_response():
    """Create sample FCM response"""
    return {
        "success": 1,
        "failure": 0,
        "results": [
            {
                "message_id": "fcm_message_123"
            }
        ]
    }


@pytest.fixture
def sample_bulk_fcm_response():
    """Create sample bulk FCM response"""
    return {
        "success": 5,
        "failure": 1,
        "results": [
            {"message_id": "fcm_message_1"},
            {"message_id": "fcm_message_2"},
            {"message_id": "fcm_message_3"},
            {"message_id": "fcm_message_4"},
            {"message_id": "fcm_message_5"},
            {"error": "Invalid registration token"}
        ]
    }
