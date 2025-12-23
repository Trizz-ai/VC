"""
Script to activate all meetings in the database
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

from app.models.meeting import Meeting
from app.core.database import create_engine_with_pool_config


async def activate_all_meetings():
    """Activate all meetings in the database"""
    
    # Create engine using the same method as the app
    engine = create_engine_with_pool_config()
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Get all meetings
            result = await session.execute(select(Meeting))
            meetings = result.scalars().all()
            
            print(f"Found {len(meetings)} meetings")
            
            if len(meetings) == 0:
                print("No meetings found in database")
                return
            
            # Update all meetings to be active
            await session.execute(
                update(Meeting).values(is_active=True)
            )
            await session.commit()
            
            print("=" * 50)
            print("✅ ALL MEETINGS ACTIVATED!")
            print("=" * 50)
            print(f"Updated {len(meetings)} meetings to active status")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error activating meetings: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(activate_all_meetings())



