"""
Script to deactivate half of the meetings in the database
"""

import asyncio
import sys
import random
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.meeting import Meeting
from app.core.database import create_engine_with_pool_config


async def deactivate_half_meetings():
    """Deactivate approximately half of the meetings"""
    
    # Create engine
    engine = create_engine_with_pool_config()
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Get all meetings
            result = await session.execute(
                select(Meeting)
            )
            all_meetings = result.scalars().all()
            
            total_meetings = len(all_meetings)
            print(f"Found {total_meetings} total meetings")
            
            if total_meetings == 0:
                print("No meetings found in database")
                return
            
            # Randomly select half to deactivate
            meetings_to_deactivate = random.sample(
                all_meetings, 
                k=total_meetings // 2
            )
            
            # Deactivate selected meetings
            deactivated_count = 0
            for meeting in meetings_to_deactivate:
                meeting.is_active = False
                deactivated_count += 1
            
            await session.commit()
            
            # Verify the changes
            result = await session.execute(
                select(Meeting).where(Meeting.is_active == True)
            )
            active_meetings = result.scalars().all()
            
            result = await session.execute(
                select(Meeting).where(Meeting.is_active == False)
            )
            inactive_meetings = result.scalars().all()
            
            print("=" * 60)
            print(f"✅ SUCCESSFULLY UPDATED MEETINGS!")
            print("=" * 60)
            print()
            print(f"  Total meetings: {total_meetings}")
            print(f"  Active meetings: {len(active_meetings)}")
            print(f"  Inactive meetings: {len(inactive_meetings)}")
            print(f"  Deactivated: {deactivated_count} meetings")
            print()
            print("Approximately half of the meetings are now inactive.")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error updating meetings: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(deactivate_half_meetings())



