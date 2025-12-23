import asyncio
import httpx

async def test_token():
    async with httpx.AsyncClient() as client:
        # Login
        login = await client.post(
            'http://127.0.0.1:8000/api/v1/auth/login',
            json={'email': 'admin@admin.com', 'password': 'admin123'}
        )
        print(f"Login status: {login.status_code}")
        if login.status_code != 200:
            print(f"Login error: {login.text}")
            return
        
        token_data = login.json()
        token = token_data['access_token']
        print(f"Token received: {token[:50]}...")
        
        # Test /auth/me
        headers = {'Authorization': f'Bearer {token}'}
        me = await client.get('http://127.0.0.1:8000/api/v1/auth/me', headers=headers)
        print(f"\n/auth/me status: {me.status_code}")
        print(f"Response: {me.text}")
        
        # Test /sessions
        sessions = await client.get('http://127.0.0.1:8000/api/v1/sessions', headers=headers)
        print(f"\n/sessions status: {sessions.status_code}")
        if sessions.status_code == 307:
            print(f"Redirect location: {sessions.headers.get('location', 'N/A')}")
        print(f"Response: {sessions.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_token())



