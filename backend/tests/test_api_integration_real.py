"""
Real API integration tests without mocks, simulations, or hardcoded responses
Tests actual FastAPI endpoints with real database operations
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta
from uuid import uuid4

from app.main import app
from app.models.base import Base
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType
from app.core.auth import create_access_token, get_password_hash


class TestAPIIntegrationReal:
    """Real API integration tests using actual implementations"""
    
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
    def real_client(self):
        """Create real FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def real_contact(self, real_database):
        """Create real contact in database"""
        async with real_database() as db:
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
            return contact
    
    @pytest.fixture
    async def real_meeting(self, real_database):
        """Create real meeting in database"""
        async with real_database() as db:
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
            return meeting
    
    @pytest.fixture
    def real_auth_token(self, real_contact):
        """Create real authentication token"""
        return create_access_token(
            data={"sub": real_contact.email, "user_id": str(real_contact.id)}
        )
    
    def test_health_endpoint(self, real_client):
        """Test health endpoint with real client"""
        response = real_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_api_docs_endpoint(self, real_client):
        """Test API documentation endpoint"""
        response = real_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_endpoint(self, real_client):
        """Test OpenAPI schema endpoint"""
        response = real_client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    @pytest.mark.asyncio
    async def test_user_registration_real(self, real_client, real_database):
        """Test user registration with real database"""
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "+1234567890",
            "password": "securepassword123",
            "consent_granted": True
        }
        
        response = real_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert "id" in data
        
        # Verify user was actually created in database
        async with real_database() as db:
            result = await db.execute(
                text("SELECT * FROM contacts WHERE email = :email"),
                {"email": "newuser@example.com"}
            )
            user = result.fetchone()
            assert user is not None
            assert user[1] == "newuser@example.com"  # email column
    
    @pytest.mark.asyncio
    async def test_user_login_real(self, real_client, real_database):
        """Test user login with real authentication"""
        # Create real user with hashed password
        async with real_database() as db:
            contact = Contact(
                email="loginuser@example.com",
                first_name="Login",
                last_name="User",
                phone="+1234567890",
                password_hash=get_password_hash("testpassword123"),
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
        
        login_data = {
            "email": "loginuser@example.com",
            "password": "testpassword123"
        }
        
        response = real_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user_real(self, real_client, real_auth_token):
        """Test getting current user with real authentication"""
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        response = real_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "real-test@example.com"
        assert data["first_name"] == "Real"
        assert data["last_name"] == "Test"
    
    @pytest.mark.asyncio
    async def test_create_meeting_real(self, real_client, real_auth_token, real_database):
        """Test creating meeting with real database operations"""
        meeting_data = {
            "name": "Real API Test Meeting",
            "description": "A meeting created via real API",
            "address": "456 Real API Street, Test City, TC 12345",
            "lat": 40.7589,
            "lng": -73.9851,
            "radius_meters": 150,
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        response = real_client.post("/api/v1/meetings/", json=meeting_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Real API Test Meeting"
        assert data["description"] == "A meeting created via real API"
        assert data["lat"] == 40.7589
        assert data["lng"] == -73.9851
        assert data["radius_meters"] == 150
        assert data["is_active"] == True
        assert "id" in data
        
        # Verify meeting was actually created in database
        async with real_database() as db:
            result = await db.execute(
                text("SELECT * FROM meetings WHERE name = :name"),
                {"name": "Real API Test Meeting"}
            )
            meeting = result.fetchone()
            assert meeting is not None
            assert meeting[1] == "Real API Test Meeting"  # name column
    
    @pytest.mark.asyncio
    async def test_get_nearby_meetings_real(self, real_client, real_auth_token, real_database):
        """Test getting nearby meetings with real location data"""
        # Create multiple real meetings at different locations
        async with real_database() as db:
            meetings = [
                Meeting(
                    name="Meeting 1",
                    address="123 Test St",
                    lat=40.7128,
                    lng=-74.0060,
                    radius_meters=100,
                    is_active=True
                ),
                Meeting(
                    name="Meeting 2", 
                    address="456 Test Ave",
                    lat=40.7589,
                    lng=-73.9851,
                    radius_meters=100,
                    is_active=True
                ),
                Meeting(
                    name="Meeting 3",
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
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        params = {
            "lat": 40.7128,
            "lng": -74.0060,
            "radius_km": 5.0
        }
        
        response = real_client.get("/api/v1/meetings/nearby", params=params, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "meetings" in data
        assert len(data["meetings"]) >= 3  # Should find all meetings
        
        # Verify meeting data structure
        for meeting in data["meetings"]:
            assert "id" in meeting
            assert "name" in meeting
            assert "lat" in meeting
            assert "lng" in meeting
            assert "distance_meters" in meeting
    
    @pytest.mark.asyncio
    async def test_create_session_real(self, real_client, real_auth_token, real_contact, real_meeting):
        """Test creating session with real database operations"""
        session_data = {
            "meeting_id": str(real_meeting.id),
            "session_notes": "Real session created via API"
        }
        
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        response = real_client.post("/api/v1/sessions/", json=session_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["meeting_id"] == str(real_meeting.id)
        assert data["session_notes"] == "Real session created via API"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_session_check_in_real(self, real_client, real_auth_token, real_contact, real_meeting):
        """Test session check-in with real location data"""
        # Create real session first
        session_data = {
            "meeting_id": str(real_meeting.id),
            "session_notes": "Real check-in session"
        }
        
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        response = real_client.post("/api/v1/sessions/", json=session_data, headers=headers)
        assert response.status_code == 201
        session = response.json()
        
        # Test check-in with real location data
        check_in_data = {
            "lat": 40.7128,
            "lng": -74.0060,
            "accuracy": 10.0,
            "altitude": 10.0,
            "speed": 0.0,
            "heading": 0.0
        }
        
        response = real_client.post(
            f"/api/v1/sessions/{session['id']}/check-in",
            json=check_in_data,
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "session_event" in data
        assert data["session_event"]["type"] == "check_in"
        assert data["session_event"]["lat"] == 40.7128
        assert data["session_event"]["lng"] == -74.0060
    
    @pytest.mark.asyncio
    async def test_get_session_history_real(self, real_client, real_auth_token, real_contact, real_meeting):
        """Test getting session history with real data"""
        # Create multiple real sessions
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        
        for i in range(3):
            session_data = {
                "meeting_id": str(real_meeting.id),
                "session_notes": f"Real session {i+1}"
            }
            response = real_client.post("/api/v1/sessions/", json=session_data, headers=headers)
            assert response.status_code == 201
        
        # Get session history
        response = real_client.get("/api/v1/sessions/history", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) >= 3
        
        # Verify session data structure
        for session in data["sessions"]:
            assert "id" in session
            assert "meeting_id" in session
            assert "status" in session
            assert "created_at" in session
    
    @pytest.mark.asyncio
    async def test_offline_queue_real(self, real_client, real_auth_token):
        """Test offline queue operations with real data"""
        # Test getting pending operations
        headers = {"Authorization": f"Bearer {real_auth_token}"}
        response = real_client.get("/api/v1/offline/pending", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "operations" in data
        assert isinstance(data["operations"], list)
    
    def test_authentication_required_endpoints(self, real_client):
        """Test that authentication is required for protected endpoints"""
        # Test without authentication
        response = real_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        response = real_client.post("/api/v1/meetings/", json={})
        assert response.status_code == 401
        
        response = real_client.get("/api/v1/sessions/history")
        assert response.status_code == 401
    
    def test_invalid_authentication_token(self, real_client):
        """Test invalid authentication token handling"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = real_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_database_connection_real(self, real_database):
        """Test real database connection and operations"""
        async with real_database() as db:
            # Test basic database query
            result = await db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
            
            # Test table existence
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            assert "contacts" in table_names
            assert "meetings" in table_names
            assert "sessions" in table_names
            assert "session_events" in table_names
    
    @pytest.mark.asyncio
    async def test_real_data_persistence(self, real_database):
        """Test real data persistence across operations"""
        async with real_database() as db:
            # Create real contact
            contact = Contact(
                email="persistence@example.com",
                first_name="Persistence",
                last_name="Test",
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            
            # Create real meeting
            meeting = Meeting(
                name="Persistence Meeting",
                address="123 Persistence St",
                lat=40.7128,
                lng=-74.0060,
                radius_meters=100,
                is_active=True
            )
            db.add(meeting)
            await db.commit()
            await db.refresh(meeting)
            
            # Create real session
            session = Session(
                contact_id=contact.id,
                meeting_id=meeting.id,
                status=SessionStatus.ACTIVE,
                session_notes="Persistence test session"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            # Verify data persistence
            result = await db.execute(
                text("SELECT COUNT(*) FROM contacts WHERE email = :email"),
                {"email": "persistence@example.com"}
            )
            contact_count = result.scalar()
            assert contact_count == 1
            
            result = await db.execute(
                text("SELECT COUNT(*) FROM meetings WHERE name = :name"),
                {"name": "Persistence Meeting"}
            )
            meeting_count = result.scalar()
            assert meeting_count == 1
            
            result = await db.execute(
                text("SELECT COUNT(*) FROM sessions WHERE contact_id = :contact_id"),
                {"contact_id": contact.id}
            )
            session_count = result.scalar()
            assert session_count == 1
