"""
Real meeting service tests without mocks, simulations, or hardcoded responses
Tests actual meeting service operations with real database
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.services.meeting_service import MeetingService
from app.models.base import Base
from app.models.meeting import Meeting
from app.models.contact import Contact


class TestMeetingServiceReal:
    """Real meeting service tests using actual implementations"""
    
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
    def real_meeting_service(self):
        """Create real meeting service instance"""
        return MeetingService()
    
    @pytest.fixture
    async def real_contact(self, real_database):
        """Create real contact in database"""
        async with real_database() as db:
            contact = Contact(
                email="meeting-test@example.com",
                first_name="Meeting",
                last_name="Test",
                phone="+1234567890",
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            return contact
    
    @pytest.fixture
    async def sample_meeting_data(self):
        """Create sample meeting data"""
        return {
            "name": "Real Test Meeting",
            "description": "A real test meeting",
            "address": "123 Real Test Street, Test City, TC 12345",
            "lat": 40.7128,
            "lng": -74.0060,
            "radius_meters": 100,
            "is_active": True
        }
    
    @pytest.mark.asyncio
    async def test_create_meeting_real(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test creating meeting with real database operations"""
        async with real_database() as db:
            # Create real meeting
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            assert meeting is not None
            assert meeting.name == "Real Test Meeting"
            assert meeting.description == "A real test meeting"
            assert meeting.address == "123 Real Test Street, Test City, TC 12345"
            assert meeting.lat == 40.7128
            assert meeting.lng == -74.0060
            assert meeting.radius_meters == 100
            assert meeting.is_active == True
            assert meeting.created_by == real_contact.id
            assert meeting.id is not None
            assert meeting.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_meeting_by_id_real(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test getting meeting by ID with real database"""
        async with real_database() as db:
            # Create real meeting first
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Get meeting by ID
            retrieved_meeting = await real_meeting_service.get_meeting_by_id(
                meeting_id=meeting.id,
                db=db
            )
            
            assert retrieved_meeting is not None
            assert retrieved_meeting.id == meeting.id
            assert retrieved_meeting.name == meeting.name
            assert retrieved_meeting.description == meeting.description
            assert retrieved_meeting.address == meeting.address
            assert retrieved_meeting.lat == meeting.lat
            assert retrieved_meeting.lng == meeting.lng
            assert retrieved_meeting.radius_meters == meeting.radius_meters
            assert retrieved_meeting.is_active == meeting.is_active
    
    @pytest.mark.asyncio
    async def test_get_meeting_not_found_real(self, real_meeting_service, real_database):
        """Test getting non-existent meeting with real database"""
        async with real_database() as db:
            # Try to get non-existent meeting
            meeting = await real_meeting_service.get_meeting_by_id(
                meeting_id=uuid4(),
                db=db
            )
            
            assert meeting is None
    
    @pytest.mark.asyncio
    async def test_find_nearby_meetings_real(self, real_meeting_service, real_database, real_contact):
        """Test getting nearby meetings with real location data"""
        async with real_database() as db:
            # Create multiple real meetings at different locations
            meetings_data = [
                {
                    "name": "Meeting 1",
                    "description": "First meeting",
                    "address": "123 Test St",
                    "lat": 40.7128,
                    "lng": -74.0060,
                    "radius_meters": 100,
                    "is_active": True
                },
                {
                    "name": "Meeting 2",
                    "description": "Second meeting",
                    "address": "456 Test Ave",
                    "lat": 40.7589,
                    "lng": -73.9851,
                    "radius_meters": 100,
                    "is_active": True
                },
                {
                    "name": "Meeting 3",
                    "description": "Third meeting",
                    "address": "789 Test Blvd",
                    "lat": 40.6892,
                    "lng": -74.0445,
                    "radius_meters": 100,
                    "is_active": True
                }
            ]
            
            # Create all meetings
            for meeting_data in meetings_data:
                await real_meeting_service.create_meeting(
                    update_data=meeting_data,
                    created_by=real_contact.id,
                    db=db
                )
            
            # Test nearby meetings from NYC location
            nearby_meetings = await real_meeting_service.find_nearby_meetings(
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
    
    @pytest.mark.asyncio
    async def test_find_nearby_meetings_empty_real(self, real_meeting_service, real_database):
        """Test getting nearby meetings when none exist"""
        async with real_database() as db:
            # Test with no meetings in database
            nearby_meetings = await real_meeting_service.find_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=True,
                db=db
            )
            
            assert len(nearby_meetings) == 0
    
    @pytest.mark.asyncio
    async def test_find_nearby_meetings_inactive_real(self, real_meeting_service, real_database, real_contact):
        """Test getting nearby meetings with inactive meetings"""
        async with real_database() as db:
            # Create inactive meeting
            inactive_meeting_data = {
                "name": "Inactive Meeting",
                "description": "Inactive meeting",
                "address": "123 Inactive St",
                "lat": 40.7128,
                "lng": -74.0060,
                "radius_meters": 100,
                "is_active": False
            }
            
            await real_meeting_service.create_meeting(
                meeting_data=inactive_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Test with active_only=True
            nearby_meetings = await real_meeting_service.find_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=True,
                db=db
            )
            
            assert len(nearby_meetings) == 0  # Should not find inactive meeting
            
            # Test with active_only=False
            nearby_meetings = await real_meeting_service.find_nearby_meetings(
                lat=40.7128,
                lng=-74.0060,
                radius_km=5.0,
                active_only=False,
                db=db
            )
            
            assert len(nearby_meetings) == 1  # Should find inactive meeting
    
    @pytest.mark.asyncio
    async def test_update_meeting_real(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test updating meeting with real database operations"""
        async with real_database() as db:
            # Create real meeting first
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Update meeting data
            update_data = {
                "name": "Updated Real Test Meeting",
                "description": "An updated real test meeting",
                "address": "456 Updated Real Test Street, Test City, TC 12345",
                "lat": 40.7589,
                "lng": -73.9851,
                "radius_meters": 150,
                "is_active": False
            }
            
            # Update meeting
            updated_meeting = await real_meeting_service.update_meeting(
                meeting_id=meeting.id,
                update_data=update_data,
                db=db
            )
            
            assert updated_meeting is not None
            assert updated_meeting.id == meeting.id
            assert updated_meeting.name == "Updated Real Test Meeting"
            assert updated_meeting.description == "An updated real test meeting"
            assert updated_meeting.address == "456 Updated Real Test Street, Test City, TC 12345"
            assert updated_meeting.lat == 40.7589
            assert updated_meeting.lng == -73.9851
            assert updated_meeting.radius_meters == 150
            assert updated_meeting.is_active == False
    
    @pytest.mark.asyncio
    async def test_update_meeting_not_found_real(self, real_meeting_service, real_database):
        """Test updating non-existent meeting"""
        async with real_database() as db:
            update_data = {
                "name": "Updated Meeting",
                "description": "Updated description"
            }
            
            # Try to update non-existent meeting
            updated_meeting = await real_meeting_service.update_meeting(
                meeting_id=uuid4(),
                update_data=update_data,
                db=db
            )
            
            assert updated_meeting is None
    
    @pytest.mark.asyncio
    async def test_deactivate_meeting_real(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test deleting meeting with real database operations"""
        async with real_database() as db:
            # Create real meeting first
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Delete meeting
            success = await real_meeting_service.deactivate_meeting(
                meeting_id=meeting.id,
                db=db
            )
            
            assert success == True
            
            # Verify meeting was deleted
            deleted_meeting = await real_meeting_service.get_meeting_by_id(
                meeting_id=meeting.id,
                db=db
            )
            
            assert deleted_meeting is None
    
    @pytest.mark.asyncio
    async def test_deactivate_meeting_not_found_real(self, real_meeting_service, real_database):
        """Test deleting non-existent meeting"""
        async with real_database() as db:
            # Try to delete non-existent meeting
            success = await real_meeting_service.deactivate_meeting(
                meeting_id=uuid4(),
                db=db
            )
            
            assert success == False
    
    @pytest.mark.asyncio
    async def test_get_meeting_statistics_real(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test getting meeting statistics with real data"""
        async with real_database() as db:
            # Create real meeting first
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Get meeting statistics
            stats = await real_meeting_service.get_meeting_statistics(
                meeting_id=meeting.id,
                db=db
            )
            
            assert stats is not None
            assert "total_sessions" in stats
            assert "active_sessions" in stats
            assert "completed_sessions" in stats
            assert "total_events" in stats
            assert "check_ins" in stats
            assert "check_outs" in stats
    
    @pytest.mark.asyncio
    async def test_get_meeting_statistics_not_found_real(self, real_meeting_service, real_database):
        """Test getting statistics for non-existent meeting"""
        async with real_database() as db:
            # Try to get stats for non-existent meeting
            stats = await real_meeting_service.get_meeting_statistics(
                meeting_id=uuid4(),
                db=db
            )
            
            assert stats is None
    
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
            assert "contacts" in table_names
    
    @pytest.mark.asyncio
    async def test_real_meeting_creation_persistence(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test real meeting creation and data persistence"""
        async with real_database() as db:
            # Create real meeting
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Verify meeting was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM meetings WHERE id = :meeting_id"),
                {"meeting_id": meeting.id}
            )
            db_meeting = result.fetchone()
            assert db_meeting is not None
            assert db_meeting[1] == "Real Test Meeting"  # name column
            assert db_meeting[2] == "A real test meeting"  # description column
            assert db_meeting[3] == "123 Real Test Street, Test City, TC 12345"  # address column
            assert db_meeting[4] == 40.7128  # lat column
            assert db_meeting[5] == -74.0060  # lng column
            assert db_meeting[6] == 100  # radius_meters column
            assert db_meeting[7] == True  # is_active column
    
    @pytest.mark.asyncio
    async def test_real_meeting_update_persistence(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test real meeting update and data persistence"""
        async with real_database() as db:
            # Create real meeting
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Update meeting
            update_data = {
                "name": "Updated Real Test Meeting",
                "description": "An updated real test meeting",
                "is_active": False
            }
            
            updated_meeting = await real_meeting_service.update_meeting(
                meeting_id=meeting.id,
                update_data=update_data,
                db=db
            )
            
            # Verify update was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM meetings WHERE id = :meeting_id"),
                {"meeting_id": meeting.id}
            )
            db_meeting = result.fetchone()
            assert db_meeting is not None
            assert db_meeting[1] == "Updated Real Test Meeting"  # name column
            assert db_meeting[2] == "An updated real test meeting"  # description column
            assert db_meeting[7] == False  # is_active column
    
    @pytest.mark.asyncio
    async def test_real_meeting_deletion_persistence(self, real_meeting_service, real_database, sample_meeting_data, real_contact):
        """Test real meeting deletion and data persistence"""
        async with real_database() as db:
            # Create real meeting
            meeting = await real_meeting_service.create_meeting(
                meeting_data=sample_meeting_data,
                created_by=real_contact.id,
                db=db
            )
            
            # Delete meeting
            success = await real_meeting_service.deactivate_meeting(
                meeting_id=meeting.id,
                db=db
            )
            
            assert success == True
            
            # Verify meeting was actually deleted from database
            result = await db.execute(
                text("SELECT * FROM meetings WHERE id = :meeting_id"),
                {"meeting_id": meeting.id}
            )
            db_meeting = result.fetchone()
            assert db_meeting is None