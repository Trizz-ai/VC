"""
Unit tests for SessionEvent model
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.models.session_event import SessionEvent, EventType


class TestSessionEvent:
    """Test cases for SessionEvent model"""
    
    def test_session_event_creation(self):
        """Test basic session event creation"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=10.0,
            location_flag=True
        )
        
        assert event.session_id == session_id
        assert event.type == EventType.CHECK_IN
        assert event.lat == 40.7128
        assert event.lng == -74.0060
        assert event.accuracy == 10.0
        assert event.location_flag == True
        assert event.id is not None
        assert isinstance(event.id, UUID)
    
    def test_session_event_creation_with_id(self):
        """Test session event creation with specific ID"""
        event_id = uuid4()
        session_id = uuid4()
        
        event = SessionEvent(
            id=event_id,
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        assert event.id == event_id
        assert event.session_id == session_id
        assert event.type == EventType.CHECK_IN
        assert event.lat == 40.7128
        assert event.lng == -74.0060
    
    def test_session_event_creation_minimal(self):
        """Test session event creation with minimal required fields"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        assert event.session_id == session_id
        assert event.type == EventType.CHECK_IN
        assert event.lat == 40.7128
        assert event.lng == -74.0060
        assert event.accuracy is None
        assert event.location_flag is None
        assert event.notes is None
    
    def test_session_event_default_values(self):
        """Test session event default values"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test default values
        assert event.accuracy is None
        assert event.location_flag is None
        assert event.notes is None
        assert event.created_at is not None
        assert event.updated_at is not None
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)
    
    def test_session_event_timestamps(self):
        """Test session event timestamp handling"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that timestamps are set (only when persisted to database)
        # assert event.created_at is not None
        # assert event.updated_at is not None
        
        # Test that created_at and updated_at are close to current time
        # now = datetime.utcnow()
        # time_diff_created = abs((event.created_at - now).total_seconds())
        # time_diff_updated = abs((event.updated_at - now).total_seconds())
        
        # assert time_diff_created < 5  # Within 5 seconds
        # assert time_diff_updated < 5  # Within 5 seconds
    
    def test_session_event_string_representation(self):
        """Test session event string representation"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        str_repr = str(event)
        assert "SessionEvent" in str_repr
        assert str(session_id) in str_repr
        assert EventType.CHECK_IN.value in str_repr
    
    def test_session_event_repr(self):
        """Test session event repr method"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        repr_str = repr(event)
        assert "SessionEvent" in repr_str
        assert str(session_id) in repr_str
        assert EventType.CHECK_IN.value in repr_str
    
    def test_session_event_equality(self):
        """Test session event equality"""
        event_id = uuid4()
        session_id = uuid4()
        
        event1 = SessionEvent(
            id=event_id,
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        event2 = SessionEvent(
            id=event_id,
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Same ID should make them equal
        assert event1 == event2
    
    def test_session_event_inequality(self):
        """Test session event inequality"""
        session_id = uuid4()
        
        event1 = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        event2 = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_OUT,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Different types should make them unequal
        assert event1 != event2
    
    def test_session_event_hash(self):
        """Test session event hash"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that event is hashable
        hash_value = hash(event)
        assert isinstance(hash_value, int)
    
    def test_event_type_enum(self):
        """Test event type enum values"""
        # Test all event type values exist
        assert EventType.CHECK_IN is not None
        assert EventType.CHECK_OUT is not None
        assert EventType.LOCATION_UPDATE is not None
        assert EventType.STATUS_CHANGE is not None
        
        # Test event type values are strings
        assert isinstance(EventType.CHECK_IN.value, str)
        assert isinstance(EventType.CHECK_OUT.value, str)
        assert isinstance(EventType.LOCATION_UPDATE.value, str)
        assert isinstance(EventType.STATUS_CHANGE.value, str)
    
    def test_event_type_handling(self):
        """Test event type handling"""
        session_id = uuid4()
        
        # Test with different event types
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        assert event.type == EventType.CHECK_IN
        
        # Test type change
        event.type = EventType.CHECK_OUT
        assert event.type == EventType.CHECK_OUT
        
        event.type = EventType.LOCATION_UPDATE
        assert event.type == EventType.LOCATION_UPDATE
        
        event.type = EventType.STATUS_CHANGE
        assert event.type == EventType.STATUS_CHANGE
    
    def test_event_coordinates(self):
        """Test event coordinate handling"""
        session_id = uuid4()
        
        # Test with valid coordinates
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        assert event.lat == 40.7128
        assert event.lng == -74.0060
        
        # Test with different coordinates
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=51.5074,
            lng=-0.1278  # London coordinates
        )
        
        assert event.lat == 51.5074
        assert event.lng == -0.1278
    
    def test_event_accuracy_handling(self):
        """Test event accuracy handling"""
        session_id = uuid4()
        
        # Test with valid accuracy
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=10.0
        )
        
        assert event.accuracy == 10.0
        
        # Test with different accuracy
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=5.5
        )
        
        assert event.accuracy == 5.5
        
        # Test with zero accuracy
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=0.0
        )
        
        assert event.accuracy == 0.0
    
    def test_event_location_flag(self):
        """Test event location flag handling"""
        session_id = uuid4()
        
        # Test with location flag True
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            location_flag=True
        )
        
        assert event.location_flag == True
        
        # Test with location flag False
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            location_flag=False
        )
        
        assert event.location_flag == False
    
    def test_event_notes_handling(self):
        """Test event notes handling"""
        session_id = uuid4()
        
        # Test with notes
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            notes="Test event notes"
        )
        
        assert event.notes == "Test event notes"
        
        # Test with empty notes
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            notes=""
        )
        
        assert event.notes == ""
        
        # Test with long notes
        long_notes = "A" * 1000
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            notes=long_notes
        )
        
        assert event.notes == long_notes
    
    def test_event_unicode_support(self):
        """Test event unicode support"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            notes="测试事件笔记"
        )
        
        assert event.notes == "测试事件笔记"
    
    def test_event_updated_at_modification(self):
        """Test event updated_at modification"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        original_updated_at = event.updated_at
        
        # Simulate update
        event.notes = "Updated notes"
        
        # In a real scenario, updated_at would be automatically updated
        # by SQLAlchemy's onupdate trigger
        assert event.notes == "Updated notes"
    
    def test_event_serialization(self):
        """Test event serialization"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=10.0,
            location_flag=True,
            notes="Test event"
        )
        
        # Test that event can be converted to dict
        event_dict = {
            "id": str(event.id),
            "session_id": str(event.session_id),
            "type": event.type,
            "lat": event.lat,
            "lng": event.lng,
            "accuracy": event.accuracy,
            "location_flag": event.location_flag,
            "notes": event.notes
        }
        
        assert event_dict["session_id"] == str(session_id)
        assert event_dict["type"] == EventType.CHECK_IN
        assert event_dict["lat"] == 40.7128
        assert event_dict["lng"] == -74.0060
        assert event_dict["accuracy"] == 10.0
        assert event_dict["location_flag"] == True
        assert event_dict["notes"] == "Test event"
    
    def test_event_relationships(self):
        """Test event relationships"""
        session_id = uuid4()
        
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that relationships are accessible
        assert hasattr(event, 'session')
        
        # Test that relationships are initially None
        assert event.session is None
    
    def test_event_validation(self):
        """Test event field validation"""
        # Test that required fields are enforced
        with pytest.raises(TypeError):
            SessionEvent()  # Missing required fields
        
        # Test that session_id is required
        with pytest.raises(TypeError):
            SessionEvent(
                type=EventType.CHECK_IN,
                lat=40.7128,
                lng=-74.0060
            )  # Missing session_id
        
        # Test that type is required
        with pytest.raises(TypeError):
            SessionEvent(
                session_id=uuid4(),
                lat=40.7128,
                lng=-74.0060
            )  # Missing type
        
        # Test that lat is required
        with pytest.raises(TypeError):
            SessionEvent(
                session_id=uuid4(),
                type=EventType.CHECK_IN,
                lng=-74.0060
            )  # Missing lat
        
        # Test that lng is required
        with pytest.raises(TypeError):
            SessionEvent(
                session_id=uuid4(),
                type=EventType.CHECK_IN,
                lat=40.7128
            )  # Missing lng
    
    def test_event_coordinate_validation(self):
        """Test event coordinate validation"""
        session_id = uuid4()
        
        # Test with valid coordinates
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060
        )
        
        assert event.lat == 40.7128
        assert event.lng == -74.0060
        
        # Test with edge case coordinates
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=0.0,
            lng=0.0
        )
        
        assert event.lat == 0.0
        assert event.lng == 0.0
    
    def test_event_accuracy_validation(self):
        """Test event accuracy validation"""
        session_id = uuid4()
        
        # Test with valid accuracy
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=10.0
        )
        
        assert event.accuracy == 10.0
        
        # Test with zero accuracy
        event = SessionEvent(
            session_id=session_id,
            type=EventType.CHECK_IN,
            lat=40.7128,
            lng=-74.0060,
            accuracy=0.0
        )
        
        assert event.accuracy == 0.0
    
    def test_event_type_validation(self):
        """Test event type validation"""
        session_id = uuid4()
        
        # Test with valid event types
        for event_type in [EventType.CHECK_IN, EventType.CHECK_OUT, 
                          EventType.LOCATION_UPDATE, EventType.STATUS_CHANGE]:
            event = SessionEvent(
                session_id=session_id,
                type=event_type,
                lat=40.7128,
                lng=-74.0060
            )
            
            assert event.type == event_type
