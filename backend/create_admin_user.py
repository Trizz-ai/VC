"""
Script to create a dummy admin user for testing
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.contact import Contact
from app.core.config import settings
from app.core.database import create_engine_with_pool_config


async def create_admin_user():
    """Create an admin user in the database"""
    
    # Create engine using the same method as the app
    engine = create_engine_with_pool_config()
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("✓ Admin user already exists!")
                print(f"  Email: admin@admin.com")
                print(f"  Password: admin123")
                print(f"  ID: {existing_admin.id}")
                return
            
            # Create admin user
            admin_user = Contact(
                email="admin@admin.com",
                first_name="Admin",
                last_name="User",
                phone="+1234567890",
                consent_granted=True,
                is_active=True,
            )
            
            # Set password
            admin_user.set_password("admin123")
            admin_user.grant_consent()
            
            # Add to database
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("=" * 50)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 50)
            print()
            print("Login Credentials:")
            print("  Email:    admin@admin.com")
            print("  Password: admin123")
            print()
            print("You can now use these credentials to:")
            print("  - Login to the frontend")
            print("  - Access admin endpoints")
            print("  - View admin dashboard")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())

