"""
Test script to verify all primary user happy paths are working
"""

import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_user_flows():
    """Test all primary user flows"""
    
    print("=" * 60)
    print("TESTING PRIMARY USER HAPPY PATHS")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = {}
        
        # Test 1: Registration
        print("1. Testing User Registration...")
        import random
        test_email = f"flowtest{random.randint(1000, 9999)}@test.com"
        try:
            reg_data = {
                "email": test_email,
                "password": "TestPass123!",
                "first_name": "Flow",
                "last_name": "Test",
                "phone": "+1234567890",
                "consent_granted": True
            }
            response = await client.post(f"{BASE_URL}/auth/register", json=reg_data)
            if response.status_code == 201:
                print("   [OK] Registration successful")
                results["registration"] = True
                user_data = response.json()
            else:
                print(f"   [FAIL] Registration failed: {response.status_code} - {response.text}")
                results["registration"] = False
                return results
        except Exception as e:
            print(f"   [FAIL] Registration error: {e}")
            results["registration"] = False
            return results
        
        # Test 2: Login
        print("\n2. Testing User Login...")
        try:
            login_data = {
                "email": test_email,
                "password": "TestPass123!"
            }
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                print("   [OK] Login successful")
                results["login"] = True
                token_data = response.json()
                access_token = token_data["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
            else:
                print(f"   [FAIL] Login failed: {response.status_code} - {response.text}")
                results["login"] = False
                return results
        except Exception as e:
            print(f"   [FAIL] Login error: {e}")
            results["login"] = False
            return results
        
        # Test 3: Get Current User
        print("\n3. Testing Get Current User...")
        try:
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                print("   [OK] Get current user successful")
                results["get_current_user"] = True
                current_user = response.json()
            else:
                print(f"   [FAIL] Get current user failed: {response.status_code} - {response.text}")
                results["get_current_user"] = False
        except Exception as e:
            print(f"   [FAIL] Get current user error: {e}")
            results["get_current_user"] = False
        
        # Test 4: List Meetings
        print("\n4. Testing List Meetings...")
        try:
            response = await client.get(f"{BASE_URL}/meetings/my-meetings", headers=headers)
            if response.status_code == 200:
                meetings = response.json()
                print(f"   [OK] List meetings successful ({len(meetings)} meetings)")
                results["list_meetings"] = True
            else:
                print(f"   [FAIL] List meetings failed: {response.status_code} - {response.text}")
                results["list_meetings"] = False
        except Exception as e:
            print(f"   [FAIL] List meetings error: {e}")
            results["list_meetings"] = False
        
        # Test 5: Get Nearby Meetings
        print("\n5. Testing Get Nearby Meetings...")
        try:
            # NYC coordinates
            response = await client.get(
                f"{BASE_URL}/meetings/nearby",
                headers=headers,
                params={"lat": 40.7128, "lng": -74.0060, "radius_km": 5.0}
            )
            if response.status_code == 200:
                nearby = response.json()
                print(f"   [OK] Get nearby meetings successful ({len(nearby)} meetings)")
                results["nearby_meetings"] = True
            else:
                print(f"   [FAIL] Get nearby meetings failed: {response.status_code} - {response.text}")
                results["nearby_meetings"] = False
        except Exception as e:
            print(f"   [FAIL] Get nearby meetings error: {e}")
            results["nearby_meetings"] = False
        
        # Test 6: Create Session
        print("\n6. Testing Create Session...")
        try:
            # First get a meeting ID
            meetings_response = await client.get(f"{BASE_URL}/admin/meetings?limit=1", headers=headers)
            if meetings_response.status_code == 200:
                meetings = meetings_response.json()
                if meetings:
                    meeting_id = meetings[0]["id"]
                    session_data = {
                        "meeting_id": meeting_id,
                        "notes": "Test session from flow test"
                    }
                    response = await client.post(f"{BASE_URL}/sessions/", json=session_data, headers=headers, follow_redirects=True)
                    if response.status_code == 201:
                        print("   [OK] Create session successful")
                        results["create_session"] = True
                        session = response.json()
                        session_id = session["id"]
                    else:
                        print(f"   [FAIL] Create session failed: {response.status_code} - {response.text}")
                        results["create_session"] = False
                else:
                    print("   [SKIP] No meetings available to create session")
                    results["create_session"] = None
            else:
                print(f"   [FAIL] Could not get meetings: {meetings_response.status_code}")
                results["create_session"] = False
        except Exception as e:
            print(f"   [FAIL] Create session error: {e}")
            results["create_session"] = False
        
        # Test 7: List Sessions
        print("\n7. Testing List Sessions...")
        try:
            response = await client.get(f"{BASE_URL}/sessions/", headers=headers, follow_redirects=True)
            if response.status_code == 200:
                sessions = response.json()
                print(f"   [OK] List sessions successful ({len(sessions)} sessions)")
                results["list_sessions"] = True
            else:
                print(f"   [FAIL] List sessions failed: {response.status_code} - {response.text}")
                results["list_sessions"] = False
        except Exception as e:
            print(f"   [FAIL] List sessions error: {e}")
            results["list_sessions"] = False
        
        # Test 8: Update Profile
        print("\n8. Testing Update Profile...")
        try:
            update_data = {
                "first_name": "FlowUpdated",
                "last_name": "TestUpdated"
            }
            response = await client.put(f"{BASE_URL}/contacts/me", json=update_data, headers=headers)
            if response.status_code == 200:
                print("   [OK] Update profile successful")
                results["update_profile"] = True
            else:
                print(f"   [FAIL] Update profile failed: {response.status_code} - {response.text}")
                results["update_profile"] = False
        except Exception as e:
            print(f"   [FAIL] Update profile error: {e}")
            results["update_profile"] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        for test_name, result in results.items():
            status = "[PASS]" if result is True else "[FAIL]" if result is False else "[SKIP]"
            print(f"  {test_name:30} {status}")
        
        passed = sum(1 for r in results.values() if r is True)
        total = sum(1 for r in results.values() if r is not None)
        print(f"\nPassed: {passed}/{total}")
        print("=" * 60)
        
        return results

if __name__ == "__main__":
    asyncio.run(test_user_flows())

