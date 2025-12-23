import asyncio
from app.core.database import create_engine_with_pool_config
from app.models.session import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

async def check_sessions():
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(Session))
        sessions = result.scalars().all()
        print(f'Total sessions in database: {len(sessions)}')
        if len(sessions) > 0:
            print(f'\nFirst 5 sessions:')
            for i, s in enumerate(sessions[:5], 1):
                print(f'  {i}. Session {s.id} - Status: {s.status.value if hasattr(s.status, "value") else s.status}')
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_sessions())



