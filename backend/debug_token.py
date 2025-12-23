import asyncio
import httpx
from app.core.auth import create_access_token, verify_token
from datetime import datetime
import jwt
from app.core.config import settings

async def debug():
    # Test token creation
    token = create_access_token({"sub": "test-user-id"})
    print(f"Token created: {token[:50]}...")
    
    # Decode token manually
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"\nToken payload:")
    print(f"  sub: {payload.get('sub')}")
    print(f"  type: {payload.get('type')}")
    print(f"  exp: {payload.get('exp')}")
    exp_time = datetime.fromtimestamp(payload.get('exp'))
    now = datetime.utcnow()
    print(f"  exp datetime: {exp_time}")
    print(f"  now: {now}")
    print(f"  expired?: {now > exp_time}")
    
    # Test verification
    verified = verify_token(token)
    print(f"\nVerification result: {verified}")
    
    # Test actual API call
    async with httpx.AsyncClient() as client:
        login = await client.post(
            'http://127.0.0.1:8000/api/v1/auth/login',
            json={'email': 'admin@admin.com', 'password': 'admin123'}
        )
        if login.status_code == 200:
            token_data = login.json()
            api_token = token_data['access_token']
            print(f"\nAPI Token: {api_token[:50]}...")
            
            # Decode API token
            api_payload = jwt.decode(api_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print(f"\nAPI Token payload:")
            print(f"  sub: {api_payload.get('sub')}")
            print(f"  type: {api_payload.get('type')}")
            
            # Test /auth/me
            headers = {'Authorization': f'Bearer {api_token}'}
            me = await client.get('http://127.0.0.1:8000/api/v1/auth/me', headers=headers)
            print(f"\n/auth/me status: {me.status_code}")
            print(f"Response: {me.text}")

if __name__ == "__main__":
    asyncio.run(debug())



