"""
Increase radius for AYA Demo Meet to make check-in easier
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


async def increase_radius():
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(Meeting).where(Meeting.name == 'AYA Demo Meet')
        )
        meeting = result.scalar_one_or_none()
        
        if meeting:
            meeting.radius_meters = 500.0  # Increase to 500 meters
            await session.commit()
            print('✅ Increased radius to 500 meters')
            print(f'   Meeting: {meeting.name}')
            print(f'   Address: {meeting.address}')
            print(f'   Radius: {meeting.radius_meters} meters')
        else:
            print('❌ Meeting not found')
        
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(increase_radius())



