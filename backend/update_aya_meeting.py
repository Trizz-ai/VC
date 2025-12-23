"""
Script to update AYA Demo Meet with correct address
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


async def update_meeting():
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(
            select(Meeting).where(Meeting.name == 'AYA Demo Meet')
        )
        meeting = result.scalar_one_or_none()
        
        if meeting:
            meeting.address = '440 Irving Avenue, Brooklyn, NY 11237'
            meeting.lat = 40.7008
            meeting.lng = -73.9205
            await session.commit()
            print('✅ Updated address and coordinates')
            print(f'   Address: {meeting.address}')
            print(f'   Coordinates: {meeting.lat}, {meeting.lng}')
        else:
            print('❌ Meeting not found')
        
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_meeting())



