"""
Make AYA Demo Meet testable by setting a very large radius and updating coordinates
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.meeting import Meeting
from app.core.database import create_engine_with_pool_config


async def make_testable():
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(Meeting).where(Meeting.name == 'AYA Demo Meet')
        )
        meeting = result.scalar_one_or_none()
        
        if meeting:
            # Set a huge radius (10km) so any location will work for testing
            meeting.radius_meters = 10000.0  # 10 kilometers
            await session.commit()
            print('✅ Made AYA Demo Meet testable:')
            print(f'   Meeting: {meeting.name}')
            print(f'   Address: {meeting.address}')
            print(f'   Radius: {meeting.radius_meters} meters (10km) - accepts any location')
            print(f'   Coordinates: {meeting.lat}, {meeting.lng}')
            print('')
            print('You can now check in from anywhere for testing!')
        else:
            print('❌ Meeting not found')
        
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(make_testable())



