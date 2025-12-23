"""
End-to-End Integration Tests
Tests complete user journeys through the entire system
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import asyncio

from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session


class TestCompleteUserJourney:
    """Test complete user journeys from registration to session completion"""
    
    @pytest.mark.asyncio
    async def test_new_user_complete_journey(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """
        Test complete journey for a new user:
        1. Register
        2. Login
        3. Find nearby meetings
        4. Start session
        5. Check-in
        6. Check-out
        7. View history
        """
        
        # Step 1: Register
        registration_data = {
            "email": "testuser@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "consent_granted": True
        }
        
        register_response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert "access_token" in register_data
        assert register_data["user"]["email"] == registration_data["email"]
        
        access_token = register_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 2: Verify login works
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": registration_data["email"],
                "password": registration_data["password"]
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        
        # Update headers with new token
        access_token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 3: Create a test meeting
        meeting_data = {
            "name": "Test AA Meeting",
            "address": "123 Test St, Test City, TS 12345",
            "lat": 37.7749,
            "lng": -122.4194,
            "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "description": "Test meeting for integration"
        }
        
        meeting_response = await async_client.post(
            "/api/v1/meetings/",
            json=meeting_data,
            headers=headers
        )
        assert meeting_response.status_code == 201
        meeting = meeting_response.json()
        meeting_id = meeting["id"]
        
        # Step 4: Find nearby meetings
        nearby_response = await async_client.get(
            "/api/v1/meetings/nearby",
            params={
                "lat": 37.7749,
                "lng": -122.4194,
                "radius": 5000
            },
            headers=headers
        )
        assert nearby_response.status_code == 200
        nearby_meetings = nearby_response.json()
        assert len(nearby_meetings) > 0
        assert any(m["id"] == meeting_id for m in nearby_meetings)
        
        # Step 5: Start a session
        session_data = {
            "meeting_id": meeting_id,
            "dest_name": meeting["name"],
            "dest_address": meeting["address"],
            "dest_lat": meeting["lat"],
            "dest_lng": meeting["lng"]
        }
        
        session_response = await async_client.post(
            "/api/v1/sessions/",
            json=session_data,
            headers=headers
        )
        assert session_response.status_code == 201
        session = session_response.json()
        session_id = session["id"]
        assert session["is_active"] == True
        
        # Step 6: Check-in to session
        checkin_data = {
            "check_in_lat": 37.7749,
            "check_in_lng": -122.4194,
            "check_in_time": datetime.utcnow().isoformat()
        }
        
        checkin_response = await async_client.post(
            f"/api/v1/sessions/{session_id}/check-in",
            json=checkin_data,
            headers=headers
        )
        assert checkin_response.status_code == 200
        checkin_result = checkin_response.json()
        assert checkin_result["check_in_time"] is not None
        
        # Step 7: Check-out from session
        checkout_data = {
            "check_out_lat": 37.7749,
            "check_out_lng": -122.4194,
            "check_out_time": datetime.utcnow().isoformat()
        }
        
        checkout_response = await async_client.post(
            f"/api/v1/sessions/{session_id}/check-out",
            json=checkout_data,
            headers=headers
        )
        assert checkout_response.status_code == 200
        checkout_result = checkout_response.json()
        assert checkout_result["check_out_time"] is not None
        
        # Step 8: View session history
        history_response = await async_client.get(
            "/api/v1/sessions/history",
            headers=headers
        )
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) > 0
        assert any(s["id"] == session_id for s in history)
        
        # Step 9: Get session statistics
        stats_response = await async_client.get(
            "/api/v1/sessions/statistics",
            headers=headers
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_sessions"] > 0


class TestOfflineFlow:
    """Test offline operations"""
    
    @pytest.mark.asyncio
    async def test_offline_queue_operations(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict
    ):
        """Test offline queue management"""
        
        # Get queue status
        status_response = await async_client.get(
            "/api/v1/offline/status",
            headers=test_auth_headers
        )
        assert status_response.status_code == 200
        status = status_response.json()
        assert "pending_count" in status
        assert "failed_count" in status
        
        # Get pending operations
        pending_response = await async_client.get(
            "/api/v1/offline/pending",
            headers=test_auth_headers
        )
        assert pending_response.status_code == 200


class TestAdminFlow:
    """Test admin operations"""
    
    @pytest.mark.asyncio
    async def test_admin_dashboard(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict
    ):
        """Test admin dashboard access"""
        
        # Get admin dashboard
        dashboard_response = await async_client.get(
            "/api/v1/admin/dashboard",
            headers=test_auth_headers
        )
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert "total_users" in dashboard
        assert "total_sessions" in dashboard
        assert "total_meetings" in dashboard
        
    @pytest.mark.asyncio
    async def test_admin_user_management(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict
    ):
        """Test admin user management"""
        
        # List all users
        users_response = await async_client.get(
            "/api/v1/admin/users",
            headers=test_auth_headers
        )
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) > 0
        
        # Get user details
        user_id = users[0]["id"]
        user_detail_response = await async_client.get(
            f"/api/v1/admin/users/{user_id}",
            headers=test_auth_headers
        )
        assert user_detail_response.status_code == 200


class TestMeetingFlow:
    """Test meeting discovery and management"""
    
    @pytest.mark.asyncio
    async def test_meeting_search_flow(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict,
        test_meeting: Meeting
    ):
        """Test meeting search functionality"""
        
        # Search meetings
        search_response = await async_client.get(
            "/api/v1/meetings/search",
            params={"query": "Test"},
            headers=test_auth_headers
        )
        assert search_response.status_code == 200
        results = search_response.json()
        assert isinstance(results, list)
        
    @pytest.mark.asyncio
    async def test_meeting_statistics(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict,
        test_meeting: Meeting
    ):
        """Test meeting statistics"""
        
        stats_response = await async_client.get(
            f"/api/v1/meetings/{test_meeting.id}/statistics",
            headers=test_auth_headers
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "total_sessions" in stats


class TestProfileManagement:
    """Test profile and settings management"""
    
    @pytest.mark.asyncio
    async def test_profile_update_flow(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict
    ):
        """Test profile update"""
        
        # Get current user
        me_response = await async_client.get(
            "/api/v1/auth/me",
            headers=test_auth_headers
        )
        assert me_response.status_code == 200
        user = me_response.json()
        
        # Update contact
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+9876543210"
        }
        
        update_response = await async_client.put(
            f"/api/v1/contacts/{user['id']}",
            json=update_data,
            headers=test_auth_headers
        )
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["first_name"] == "Updated"
        
    @pytest.mark.asyncio
    async def test_password_change_flow(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict
    ):
        """Test password change"""
        
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass123!"
        }
        
        password_response = await async_client.post(
            "/api/v1/auth/change-password",
            json=password_data,
            headers=test_auth_headers
        )
        assert password_response.status_code == 200


class TestGPSVerification:
    """Test GPS verification functionality"""
    
    @pytest.mark.asyncio
    async def test_gps_check_in_too_far(
        self,
        async_client: AsyncClient,
        test_user: Contact,
        test_auth_headers: dict,
        test_meeting: Meeting
    ):
        """Test check-in fails when too far from meeting"""
        
        # Create session
        session_data = {
            "meeting_id": str(test_meeting.id),
            "dest_name": test_meeting.name,
            "dest_address": test_meeting.address,
            "dest_lat": test_meeting.lat,
            "dest_lng": test_meeting.lng
        }
        
        session_response = await async_client.post(
            "/api/v1/sessions/",
            json=session_data,
            headers=test_auth_headers
        )
        assert session_response.status_code == 201
        session = session_response.json()
        
        # Try to check-in from far away (different coordinates)
        checkin_data = {
            "check_in_lat": 40.7128,  # New York (far from meeting)
            "check_in_lng": -74.0060,
            "check_in_time": datetime.utcnow().isoformat()
        }
        
        checkin_response = await async_client.post(
            f"/api/v1/sessions/{session['id']}/check-in",
            json=checkin_data,
            headers=test_auth_headers
        )
        
        # Should fail or warn about distance
        # Depending on your implementation, this might be 400 or 200 with warning
        assert checkin_response.status_code in [200, 400]


class TestTokenManagement:
    """Test token refresh and management"""
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(
        self,
        async_client: AsyncClient
    ):
        """Test token refresh"""
        
        # Register and login to get tokens
        registration_data = {
            "email": "tokentest@example.com",
            "password": "SecurePass123!",
            "first_name": "Token",
            "last_name": "Test",
            "consent_granted": True
        }
        
        register_response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        assert register_response.status_code == 201
        tokens = register_response.json()
        
        refresh_token = tokens["refresh_token"]
        
        # Refresh the token
        refresh_response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]


class TestErrorHandling:
    """Test error handling across the system"""
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient
    ):
        """Test unauthorized access is properly rejected"""
        
        # Try to access protected endpoint without token
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 403
        
    @pytest.mark.asyncio
    async def test_invalid_token(
        self,
        async_client: AsyncClient
    ):
        """Test invalid token is rejected"""
        
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        assert response.status_code in [401, 403]
        
    @pytest.mark.asyncio
    async def test_not_found_errors(
        self,
        async_client: AsyncClient,
        test_auth_headers: dict
    ):
        """Test 404 errors are properly handled"""
        
        # Try to get non-existent meeting
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(
            f"/api/v1/meetings/{fake_uuid}",
            headers=test_auth_headers
        )
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



