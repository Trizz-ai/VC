"""
Real session service tests without mocks, simulations, or hardcoded responses
Tests actual session service operations with real database
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.services.session_service import SessionService
from app.models.base import Base
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType


class TestSessionServiceReal:
    """Real session service tests using actual implementations"""
    
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
    def real_session_service(self):
        """Create real session service instance"""
        return SessionService()
    
    @pytest.fixture
    async def real_contact(self, real_database):
        """Create real contact in database"""
        async with real_database() as db:
            contact = Contact(
                email="session-test@example.com",
                first_name="Session",
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
                name="Real Session Test Meeting",
                description="A real test meeting for session services",
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
    
    @pytest.mark.asyncio
    async def test_create_session_success_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test successful session creation with real database operations"""
        async with real_database() as db:
            # Create real session
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real session test",
                db=db
        )
        
        assert session is not None
        assert session.contact_id == real_contact.id
        assert session.meeting_id == real_meeting.id
        assert session.status == SessionStatus.ACTIVE
        assert session.session_notes == "Real session test"
        assert session.id is not None
        assert session.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_session_meeting_not_found_real(self, real_session_service, real_database, real_contact):
        """Test session creation with non-existent meeting"""
        async with real_database() as db:
            # Try to create session with non-existent meeting
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=uuid4(),
            notes="Test session",
                db=db
        )
        
        assert session is None
    
    @pytest.mark.asyncio
    async def test_create_session_meeting_inactive_real(self, real_session_service, real_database, real_contact):
        """Test session creation with inactive meeting"""
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
            
            # Try to create session with inactive meeting
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
            meeting_id=inactive_meeting.id,
            notes="Test session",
                db=db
        )
        
        assert session is None
    
    @pytest.mark.asyncio
    async def test_check_in_success_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test successful check-in with real database operations"""
        async with real_database() as db:
            # Create real session first
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real check-in session",
                db=db
            )
            
            assert session is not None
            
            # Test check-in
            check_in_data = {
                "lat": 40.7128,
                "lng": -74.0060,
                "accuracy": 10.0,
                "altitude": 10.0,
                "speed": 0.0,
                "heading": 0.0,
                "notes": "Real check-in"
            }
            
            result = await real_session_service.check_in(
                session_id=session.id,
                location_data=check_in_data,
                db=db
            )
            
            assert result is not None
            assert result["success"] == True
            assert "session_event" in result
            assert result["session_event"]["type"] == "check_in"
            assert result["session_event"]["lat"] == 40.7128
            assert result["session_event"]["lng"] == -74.0060
    
    @pytest.mark.asyncio
    async def test_check_in_session_not_found_real(self, real_session_service, real_database):
        """Test check-in with non-existent session"""
        async with real_database() as db:
            # Try to check-in with non-existent session
            check_in_data = {
                "lat": 40.7128,
                "lng": -74.0060,
                "accuracy": 10.0,
                "altitude": 10.0,
                "speed": 0.0,
                "heading": 0.0,
                "notes": "Test check-in"
            }
            
            result = await real_session_service.check_in(
                session_id=uuid4(),
                location_data=check_in_data,
                db=db
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_check_out_success_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test successful check-out with real database operations"""
        async with real_database() as db:
            # Create real session first
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real check-out session",
                db=db
            )
            
            assert session is not None
            
            # Test check-out
            check_out_data = {
                "lat": 40.7128,
                "lng": -74.0060,
                "accuracy": 10.0,
                "altitude": 10.0,
                "speed": 0.0,
                "heading": 0.0,
                "notes": "Real check-out"
            }
            
            result = await real_session_service.check_out(
                session_id=session.id,
                location_data=check_out_data,
                db=db
            )
            
            assert result is not None
            assert result["success"] == True
            assert "session_event" in result
            assert result["session_event"]["type"] == "check_out"
            assert result["session_event"]["lat"] == 40.7128
            assert result["session_event"]["lng"] == -74.0060
    
    @pytest.mark.asyncio
    async def test_check_out_session_not_found_real(self, real_session_service, real_database):
        """Test check-out with non-existent session"""
        async with real_database() as db:
            # Try to check-out with non-existent session
            check_out_data = {
                "lat": 40.7128,
                "lng": -74.0060,
                "accuracy": 10.0,
                "altitude": 10.0,
                "speed": 0.0,
                "heading": 0.0,
                "notes": "Test check-out"
            }
            
            result = await real_session_service.check_out(
                session_id=uuid4(),
                location_data=check_out_data,
                db=db
            )
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_active_session_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test getting active session with real database"""
        async with real_database() as db:
            # Create real session
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real active session",
                db=db
            )
            
            assert session is not None
            
            # Get active session
            active_session = await real_session_service.get_active_session(
                contact_id=real_contact.id,
                db=db
            )
            
            assert active_session is not None
            assert active_session.id == session.id
            assert active_session.contact_id == real_contact.id
            assert active_session.meeting_id == real_meeting.id
            assert active_session.status == SessionStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_active_session_none_real(self, real_session_service, real_database, real_contact):
        """Test getting active session when none exists"""
        async with real_database() as db:
            # Try to get active session when none exists
            active_session = await real_session_service.get_active_session(
                contact_id=real_contact.id,
                db=db
            )
            
            assert active_session is None
    
    @pytest.mark.asyncio
    async def test_get_session_history_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test getting session history with real database"""
        async with real_database() as db:
            # Create multiple real sessions
            sessions = []
            for i in range(3):
                session = await real_session_service.create_session(
                    contact_id=real_contact.id,
                    meeting_id=real_meeting.id,
                    notes=f"Real session {i+1}",
                    db=db
                )
                sessions.append(session)
            
            # Get session history
            history = await real_session_service.get_session_history(
                contact_id=real_contact.id,
                limit=10,
                offset=0,
                db=db
            )
            
            assert len(history) >= 3
            
            # Verify session data structure
            for session in history:
                assert hasattr(session, 'id')
                assert hasattr(session, 'contact_id')
                assert hasattr(session, 'meeting_id')
                assert hasattr(session, 'status')
                assert hasattr(session, 'created_at')
                assert session.contact_id == real_contact.id
    
    @pytest.mark.asyncio
    async def test_get_session_history_empty_real(self, real_session_service, real_database, real_contact):
        """Test getting session history when none exist"""
        async with real_database() as db:
            # Try to get session history when none exist
            history = await real_session_service.get_session_history(
                contact_id=real_contact.id,
                limit=10,
                offset=0,
                db=db
            )
            
            assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_complete_session_real(self, real_session_service, real_database, real_contact, real_meeting):
        """Test completing session with real database operations"""
        async with real_database() as db:
            # Create real session
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real session to complete",
                db=db
            )
            
            assert session is not None
            
            # Complete session
            completed_session = await real_session_service.complete_session(
                session_id=session.id,
                notes="Session completed",
                db=db
            )
            
            assert completed_session is not None
            assert completed_session.id == session.id
            assert completed_session.status == SessionStatus.COMPLETED
            assert completed_session.session_notes == "Session completed"
    
    @pytest.mark.asyncio
    async def test_complete_session_not_found_real(self, real_session_service, real_database):
        """Test completing non-existent session"""
        async with real_database() as db:
            # Try to complete non-existent session
            completed_session = await real_session_service.complete_session(
                session_id=uuid4(),
                notes="Session completed",
                db=db
            )
            
            assert completed_session is None
    
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
            assert "sessions" in table_names
            assert "session_events" in table_names
            assert "contacts" in table_names
            assert "meetings" in table_names
    
    @pytest.mark.asyncio
    async def test_real_session_creation_persistence(self, real_session_service, real_database, real_contact, real_meeting):
        """Test real session creation and data persistence"""
        async with real_database() as db:
            # Create real session
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real session test",
                db=db
            )
            
            assert session is not None
            
            # Verify session was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM sessions WHERE id = :session_id"),
                {"session_id": session.id}
            )
            db_session = result.fetchone()
            assert db_session is not None
            assert db_session[1] == real_contact.id  # contact_id column
            assert db_session[2] == real_meeting.id  # meeting_id column
            assert db_session[3] == "active"  # status column
            assert db_session[4] == "Real session test"  # session_notes column
    
    @pytest.mark.asyncio
    async def test_real_session_event_creation_persistence(self, real_session_service, real_database, real_contact, real_meeting):
        """Test real session event creation and data persistence"""
        async with real_database() as db:
            # Create real session
            session = await real_session_service.create_session(
                contact_id=real_contact.id,
                meeting_id=real_meeting.id,
                notes="Real session for event testing",
                db=db
            )
            
            assert session is not None
            
            # Create session event
            check_in_data = {
                "lat": 40.7128,
                "lng": -74.0060,
                "accuracy": 10.0,
                "altitude": 10.0,
                "speed": 0.0,
                "heading": 0.0,
                "notes": "Real check-in event"
            }
            
            result = await real_session_service.check_in(
                session_id=session.id,
                location_data=check_in_data,
                db=db
            )
            
            assert result is not None
            assert result["success"] == True
            
            # Verify event was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM session_events WHERE session_id = :session_id"),
                {"session_id": session.id}
            )
            db_events = result.fetchall()
            assert len(db_events) >= 1
            
            # Verify event data
            event = db_events[0]
            assert event[1] == session.id  # session_id column
            assert event[2] == "check_in"  # type column
            assert event[3] == 40.7128  # lat column
            assert event[4] == -74.0060  # lng column
            assert event[5] == 10.0  # accuracy column
            assert event[6] == True  # location_flag column