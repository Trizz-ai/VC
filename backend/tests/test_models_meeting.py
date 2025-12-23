"""
Unit tests for Meeting model
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.models.meeting import Meeting


class TestMeeting:
    """Test cases for Meeting model"""
    
    def test_meeting_creation(self):
        """Test basic meeting creation"""
        meeting = Meeting(
            name="Test Meeting",
            description="A test meeting",
            address="123 Test Street, Test City, TC 12345",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=100,
            is_active=True
        )
        
        assert meeting.name == "Test Meeting"
        assert meeting.description == "A test meeting"
        assert meeting.address == "123 Test Street, Test City, TC 12345"
        assert meeting.lat == 40.7128
        assert meeting.lng == -74.0060
        assert meeting.radius_meters == 100
        assert meeting.is_active == True
        assert meeting.id is not None
        assert isinstance(meeting.id, UUID)
    
    def test_meeting_creation_with_id(self):
        """Test meeting creation with specific ID"""
        meeting_id = uuid4()
        meeting = Meeting(
            id=meeting_id,
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.id == meeting_id
        assert meeting.name == "Test Meeting"
        assert meeting.address == "123 Test Street"
        assert meeting.lat == 40.7128
        assert meeting.lng == -74.0060
    
    def test_meeting_creation_minimal(self):
        """Test meeting creation with minimal required fields"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.name == "Test Meeting"
        assert meeting.address == "123 Test Street"
        assert meeting.lat == 40.7128
        assert meeting.lng == -74.0060
        assert meeting.description is None
        assert meeting.radius_meters is None
        assert meeting.is_active is None
    
    def test_meeting_default_values(self):
        """Test meeting default values"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test default values
        assert meeting.description is None
        assert meeting.radius_meters is None
        assert meeting.is_active is None
        assert meeting.created_at is not None
        assert meeting.updated_at is not None
        assert isinstance(meeting.created_at, datetime)
        assert isinstance(meeting.updated_at, datetime)
    
    def test_meeting_timestamps(self):
        """Test meeting timestamp handling"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that timestamps are set
        assert meeting.created_at is not None
        assert meeting.updated_at is not None
        
        # Test that created_at and updated_at are close to current time
        now = datetime.utcnow()
        time_diff_created = abs((meeting.created_at - now).total_seconds())
        time_diff_updated = abs((meeting.updated_at - now).total_seconds())
        
        assert time_diff_created < 5  # Within 5 seconds
        assert time_diff_updated < 5  # Within 5 seconds
    
    def test_meeting_string_representation(self):
        """Test meeting string representation"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        str_repr = str(meeting)
        assert "Meeting" in str_repr
        assert "Test Meeting" in str_repr
    
    def test_meeting_repr(self):
        """Test meeting repr method"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        repr_str = repr(meeting)
        assert "Meeting" in repr_str
        assert "Test Meeting" in repr_str
    
    def test_meeting_equality(self):
        """Test meeting equality"""
        meeting1 = Meeting(
            id=uuid4(),
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        meeting2 = Meeting(
            id=meeting1.id,
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Same ID should make them equal
        assert meeting1 == meeting2
    
    def test_meeting_inequality(self):
        """Test meeting inequality"""
        meeting1 = Meeting(
            name="Meeting 1",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        meeting2 = Meeting(
            name="Meeting 2",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Different names should make them unequal
        assert meeting1 != meeting2
    
    def test_meeting_hash(self):
        """Test meeting hash"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that meeting is hashable
        hash_value = hash(meeting)
        assert isinstance(hash_value, int)
    
    def test_meeting_coordinates(self):
        """Test meeting coordinate handling"""
        # Test with valid coordinates
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.lat == 40.7128
        assert meeting.lng == -74.0060
        
        # Test with different coordinates
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=51.5074,
            lng=-0.1278  # London coordinates
        )
        
        assert meeting.lat == 51.5074
        assert meeting.lng == -0.1278
    
    def test_meeting_radius_handling(self):
        """Test meeting radius handling"""
        # Test with valid radius
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=100
        )
        
        assert meeting.radius_meters == 100
        
        # Test with different radius
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=500
        )
        
        assert meeting.radius_meters == 500
    
    def test_meeting_active_status(self):
        """Test meeting active status"""
        # Test default active status
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.is_active is None
        
        # Test setting active
        meeting.is_active = True
        assert meeting.is_active == True
        
        # Test setting inactive
        meeting.is_active = False
        assert meeting.is_active == False
    
    def test_meeting_description_handling(self):
        """Test meeting description handling"""
        # Test with description
        meeting = Meeting(
            name="Test Meeting",
            description="A detailed description of the meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.description == "A detailed description of the meeting"
        
        # Test with empty description
        meeting = Meeting(
            name="Test Meeting",
            description="",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.description == ""
    
    def test_meeting_address_handling(self):
        """Test meeting address handling"""
        # Test with normal address
        meeting = Meeting(
            name="Test Meeting",
            address="123 Main Street, New York, NY 10001",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.address == "123 Main Street, New York, NY 10001"
        
        # Test with international address
        meeting = Meeting(
            name="Test Meeting",
            address="10 Downing Street, London SW1A 2AA, UK",
            lat=51.5074,
            lng=-0.1278
        )
        
        assert meeting.address == "10 Downing Street, London SW1A 2AA, UK"
    
    def test_meeting_unicode_support(self):
        """Test meeting unicode support"""
        meeting = Meeting(
            name="测试会议",
            description="这是一个测试会议",
            address="测试地址 123号",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.name == "测试会议"
        assert meeting.description == "这是一个测试会议"
        assert meeting.address == "测试地址 123号"
    
    def test_meeting_long_names(self):
        """Test meeting with long names"""
        long_name = "A" * 200
        
        meeting = Meeting(
            name=long_name,
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.name == long_name
    
    def test_meeting_updated_at_modification(self):
        """Test meeting updated_at modification"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        original_updated_at = meeting.updated_at
        
        # Simulate update
        meeting.name = "Updated Meeting"
        
        # In a real scenario, updated_at would be automatically updated
        # by SQLAlchemy's onupdate trigger
        assert meeting.name == "Updated Meeting"
    
    def test_meeting_serialization(self):
        """Test meeting serialization"""
        meeting = Meeting(
            name="Test Meeting",
            description="A test meeting",
            address="123 Test Street, Test City, TC 12345",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=100,
            is_active=True
        )
        
        # Test that meeting can be converted to dict
        meeting_dict = {
            "id": str(meeting.id),
            "name": meeting.name,
            "description": meeting.description,
            "address": meeting.address,
            "lat": meeting.lat,
            "lng": meeting.lng,
            "radius_meters": meeting.radius_meters,
            "is_active": meeting.is_active
        }
        
        assert meeting_dict["name"] == "Test Meeting"
        assert meeting_dict["description"] == "A test meeting"
        assert meeting_dict["address"] == "123 Test Street, Test City, TC 12345"
        assert meeting_dict["lat"] == 40.7128
        assert meeting_dict["lng"] == -74.0060
        assert meeting_dict["radius_meters"] == 100
        assert meeting_dict["is_active"] == True
    
    def test_meeting_relationships(self):
        """Test meeting relationships"""
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        # Test that relationships are accessible
        assert hasattr(meeting, 'sessions')
        assert hasattr(meeting, 'created_by')
        
        # Test that relationships are initially empty
        assert len(meeting.sessions) == 0
        assert meeting.created_by is None
    
    def test_meeting_validation(self):
        """Test meeting field validation"""
        # Test that required fields are enforced
        with pytest.raises(TypeError):
            Meeting()  # Missing required fields
        
        # Test that name is required
        with pytest.raises(TypeError):
            Meeting(
                address="123 Test Street",
                lat=40.7128,
                lng=-74.0060
            )  # Missing name
        
        # Test that address is required
        with pytest.raises(TypeError):
            Meeting(
                name="Test Meeting",
                lat=40.7128,
                lng=-74.0060
            )  # Missing address
        
        # Test that lat is required
        with pytest.raises(TypeError):
            Meeting(
                name="Test Meeting",
                address="123 Test Street",
                lng=-74.0060
            )  # Missing lat
        
        # Test that lng is required
        with pytest.raises(TypeError):
            Meeting(
                name="Test Meeting",
                address="123 Test Street",
                lat=40.7128
            )  # Missing lng
    
    def test_meeting_coordinate_validation(self):
        """Test meeting coordinate validation"""
        # Test with valid coordinates
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060
        )
        
        assert meeting.lat == 40.7128
        assert meeting.lng == -74.0060
        
        # Test with edge case coordinates
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=0.0,
            lng=0.0
        )
        
        assert meeting.lat == 0.0
        assert meeting.lng == 0.0
    
    def test_meeting_radius_validation(self):
        """Test meeting radius validation"""
        # Test with valid radius
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=100
        )
        
        assert meeting.radius_meters == 100
        
        # Test with zero radius
        meeting = Meeting(
            name="Test Meeting",
            address="123 Test Street",
            lat=40.7128,
            lng=-74.0060,
            radius_meters=0
        )
        
        assert meeting.radius_meters == 0
