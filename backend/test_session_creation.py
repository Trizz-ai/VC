"""
Test script to investigate session creation issues
"""

import asyncio
import httpx
import json

async def test_session_creation():
    async with httpx.AsyncClient() as client:
        print("1. Logging in as admin...")
        login_resp = await client.post(
            'http://127.0.0.1:8000/api/v1/auth/login',
            json={'email': 'admin@admin.com', 'password': 'admin123'}
        )
        print(f"   Login status: {login_resp.status_code}")
        if login_resp.status_code != 200:
            print(f"   Error: {login_resp.text}")
            return
        token = login_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("\n2. Getting meetings...")
        meetings_resp = await client.get(
            'http://127.0.0.1:8000/api/v1/meetings/upcoming',
            headers=headers,
            params={'days_ahead': 7}
        )
        print(f"   Meetings status: {meetings_resp.status_code}")
        if meetings_resp.status_code != 200:
            print(f"   Error: {meetings_resp.text}")
            return
        meetings = meetings_resp.json()
        if len(meetings) == 0:
            print("   No meetings found")
            return
        meeting_id = meetings[0]['id']
        print(f"   Found meeting: {meetings[0].get('name', 'Unknown')} (ID: {meeting_id})")
        print(f"   Meeting is_active: {meetings[0].get('is_active', 'N/A')}")
        
        print(f"\n3. Creating session for meeting {meeting_id}...")
        session_resp = await client.post(
            'http://127.0.0.1:8000/api/v1/sessions/',
            headers=headers,
            json={'meeting_id': meeting_id}
        )
        print(f"   Session creation status: {session_resp.status_code}")
        if session_resp.status_code == 201:
            print(f"   ✅ Success!")
            print(f"   Response: {json.dumps(session_resp.json(), indent=2)}")
        else:
            print(f"   ❌ Error: {session_resp.text}")

if __name__ == "__main__":
    asyncio.run(test_session_creation())



