"""
Quick script to fix CORS and ensure admin user exists
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.contact import Contact
from app.core.database import create_engine_with_pool_config


async def ensure_admin_user():
    """Ensure admin user exists with correct password"""
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if admin exists
            result = await session.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            admin = result.scalar_one_or_none()
            
            if admin:
                print(f"✓ Admin user exists: {admin.email}")
                # Update password to ensure it's correct
                admin.set_password("admin123")
                admin.is_active = True
                admin.consent_granted = True
                await session.commit()
                print("✓ Admin password updated to 'admin123'")
            else:
                print("Creating admin user...")
                admin = Contact(
                    email="admin@admin.com",
                    first_name="Admin",
                    last_name="User",
                    is_active=True,
                    consent_granted=True,
                )
                admin.set_password("admin123")
                session.add(admin)
                await session.commit()
                print("✓ Admin user created: admin@admin.com / admin123")
            
            print("\n✅ Admin user ready!")
            print("   Email: admin@admin.com")
            print("   Password: admin123")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Ensuring Admin User Exists")
    print("=" * 60)
    print()
    asyncio.run(ensure_admin_user())



