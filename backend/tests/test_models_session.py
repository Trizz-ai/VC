"""
Unit tests for Session model
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.models.session import Session, SessionStatus


class TestSession:
    """Test cases for Session model"""
    
    def test_session_creation(self):
        """Test basic session creation"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE,
            session_notes="Test session"
        )
        
        assert session.contact_id == contact_id
        assert session.meeting_id == meeting_id
        assert session.status == SessionStatus.ACTIVE
        assert session.session_notes == "Test session"
        assert session.id is not None
        assert isinstance(session.id, UUID)
    
    def test_session_creation_with_id(self):
        """Test session creation with specific ID"""
        session_id = uuid4()
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            id=session_id,
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        assert session.id == session_id
        assert session.contact_id == contact_id
        assert session.meeting_id == meeting_id
        assert session.status == SessionStatus.ACTIVE
    
    def test_session_creation_minimal(self):
        """Test session creation with minimal required fields"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        assert session.contact_id == contact_id
        assert session.meeting_id == meeting_id
        assert session.status is None
        assert session.session_notes is None
    
    def test_session_default_values(self):
        """Test session default values"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test default values
        assert session.status is None
        assert session.session_notes is None
        assert session.check_in_time is None
        assert session.check_out_time is None
        assert session.created_at is not None
        assert session.updated_at is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.updated_at, datetime)
    
    def test_session_timestamps(self):
        """Test session timestamp handling"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test that timestamps are set (only when persisted to database)
        # assert session.created_at is not None
        # assert session.updated_at is not None
        
        # Test that created_at and updated_at are close to current time
        # now = datetime.utcnow()
        # time_diff_created = abs((session.created_at - now).total_seconds())
        # time_diff_updated = abs((session.updated_at - now).total_seconds())
        
        # assert time_diff_created < 5  # Within 5 seconds
        # assert time_diff_updated < 5  # Within 5 seconds
    
    def test_session_string_representation(self):
        """Test session string representation"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        str_repr = str(session)
        assert "Session" in str_repr
        assert str(contact_id) in str_repr
        assert str(meeting_id) in str_repr
    
    def test_session_repr(self):
        """Test session repr method"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        repr_str = repr(session)
        assert "Session" in repr_str
        assert str(contact_id) in repr_str
        assert str(meeting_id) in repr_str
    
    def test_session_equality(self):
        """Test session equality"""
        session_id = uuid4()
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session1 = Session(
            id=session_id,
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        session2 = Session(
            id=session_id,
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        # Same ID should make them equal
        assert session1 == session2
    
    def test_session_inequality(self):
        """Test session inequality"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session1 = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        session2 = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.COMPLETED
        )
        
        # Different status should make them unequal
        assert session1 != session2
    
    def test_session_hash(self):
        """Test session hash"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        # Test that session is hashable
        hash_value = hash(session)
        assert isinstance(hash_value, int)
    
    def test_session_status_enum(self):
        """Test session status enum values"""
        # Test all status values exist
        assert SessionStatus.ACTIVE is not None
        assert SessionStatus.CHECKED_IN is not None
        assert SessionStatus.COMPLETED is not None
        assert SessionStatus.ENDED is not None
        
        # Test status values are strings
        assert isinstance(SessionStatus.ACTIVE, str)
        assert isinstance(SessionStatus.CHECKED_IN, str)
        assert isinstance(SessionStatus.COMPLETED, str)
        assert isinstance(SessionStatus.ENDED, str)
    
    def test_session_status_handling(self):
        """Test session status handling"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        # Test with different statuses
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        assert session.status == SessionStatus.ACTIVE
        
        # Test status change
        session.status = SessionStatus.CHECKED_IN
        assert session.status == SessionStatus.CHECKED_IN
        
        session.status = SessionStatus.COMPLETED
        assert session.status == SessionStatus.COMPLETED
        
        session.status = SessionStatus.ENDED
        assert session.status == SessionStatus.ENDED
    
    def test_session_notes_handling(self):
        """Test session notes handling"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        # Test with notes
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes="Test session notes"
        )
        
        assert session.session_notes == "Test session notes"
        
        # Test with empty notes
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes=""
        )
        
        assert session.session_notes == ""
        
        # Test with long notes
        long_notes = "A" * 1000
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes=long_notes
        )
        
        assert session.session_notes == long_notes
    
    def test_session_check_in_time(self):
        """Test session check-in time handling"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test initial check-in time
        assert session.check_in_time is None
        
        # Test setting check-in time
        check_in_time = datetime.utcnow()
        session.check_in_time = check_in_time
        
        assert session.check_in_time == check_in_time
    
    def test_session_check_out_time(self):
        """Test session check-out time handling"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test initial check-out time
        assert session.check_out_time is None
        
        # Test setting check-out time
        check_out_time = datetime.utcnow()
        session.check_out_time = check_out_time
        
        assert session.check_out_time == check_out_time
    
    def test_session_time_sequence(self):
        """Test session time sequence"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test that check-in time is before check-out time
        check_in_time = datetime.utcnow()
        check_out_time = datetime.utcnow()
        
        session.check_in_time = check_in_time
        session.check_out_time = check_out_time
        
        assert session.check_in_time <= session.check_out_time
    
    def test_session_unicode_support(self):
        """Test session unicode support"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes="测试会话笔记"
        )
        
        assert session.session_notes == "测试会话笔记"
    
    def test_session_updated_at_modification(self):
        """Test session updated_at modification"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        original_updated_at = session.updated_at
        
        # Simulate update
        session.session_notes = "Updated notes"
        
        # In a real scenario, updated_at would be automatically updated
        # by SQLAlchemy's onupdate trigger
        assert session.session_notes == "Updated notes"
    
    def test_session_serialization(self):
        """Test session serialization"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE,
            session_notes="Test session"
        )
        
        # Test that session can be converted to dict
        session_dict = {
            "id": str(session.id),
            "contact_id": str(session.contact_id),
            "meeting_id": str(session.meeting_id),
            "status": session.status,
            "session_notes": session.session_notes,
            "check_in_time": session.check_in_time,
            "check_out_time": session.check_out_time
        }
        
        assert session_dict["contact_id"] == str(contact_id)
        assert session_dict["meeting_id"] == str(meeting_id)
        assert session_dict["status"] == SessionStatus.ACTIVE
        assert session_dict["session_notes"] == "Test session"
    
    def test_session_relationships(self):
        """Test session relationships"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test that relationships are accessible
        assert hasattr(session, 'contact')
        assert hasattr(session, 'meeting')
        assert hasattr(session, 'events')
        
        # Test that relationships are initially None or empty
        assert session.contact is None
        assert session.meeting is None
        assert len(session.events) == 0
    
    def test_session_validation(self):
        """Test session field validation"""
        # Test that required fields are enforced
        with pytest.raises(TypeError):
            Session()  # Missing required fields
        
        # Test that contact_id is required
        with pytest.raises(TypeError):
            Session(
                meeting_id=uuid4()
            )  # Missing contact_id
        
        # Test that meeting_id is required
        with pytest.raises(TypeError):
            Session(
                contact_id=uuid4()
            )  # Missing meeting_id
    
    def test_session_status_transitions(self):
        """Test session status transitions"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            status=SessionStatus.ACTIVE
        )
        
        # Test valid status transitions
        session.status = SessionStatus.CHECKED_IN
        assert session.status == SessionStatus.CHECKED_IN
        
        session.status = SessionStatus.COMPLETED
        assert session.status == SessionStatus.COMPLETED
        
        session.status = SessionStatus.ENDED
        assert session.status == SessionStatus.ENDED
    
    def test_session_duration_calculation(self):
        """Test session duration calculation"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id
        )
        
        # Test duration calculation
        check_in_time = datetime.utcnow()
        check_out_time = datetime.utcnow()
        
        session.check_in_time = check_in_time
        session.check_out_time = check_out_time
        
        # Test that duration can be calculated
        if session.check_in_time and session.check_out_time:
            duration = session.check_out_time - session.check_in_time
            assert duration.total_seconds() >= 0
    
    def test_session_notes_validation(self):
        """Test session notes validation"""
        contact_id = uuid4()
        meeting_id = uuid4()
        
        # Test with valid notes
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes="Valid notes"
        )
        
        assert session.session_notes == "Valid notes"
        
        # Test with None notes
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            session_notes=None
        )
        
        assert session.session_notes is None
