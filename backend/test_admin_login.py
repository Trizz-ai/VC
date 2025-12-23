"""Test admin login directly"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.models.contact import Contact
from app.core.database import AsyncSessionLocal
from app.core.auth import authenticate_user

async def test_login():
    async with AsyncSessionLocal() as db:
        # Test authenticate_user function
        user = await authenticate_user("admin@admin.com", "admin123", db)
        if user:
            print(f"✅ Login successful!")
            print(f"   User: {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   ID: {user.id}")
        else:
            print("❌ Login failed!")
            # Check if user exists
            result = await db.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            user = result.scalar_one_or_none()
            if user:
                print(f"   User exists: {user.email}")
                print(f"   Active: {user.is_active}")
                print(f"   Has password: {bool(user.password_hash)}")
                # Test password directly
                from app.core.auth import verify_password
                if user.password_hash:
                    verified = verify_password("admin123", user.password_hash)
                    print(f"   Password verification: {verified}")
            else:
                print("   User does not exist!")

if __name__ == "__main__":
    asyncio.run(test_login())



