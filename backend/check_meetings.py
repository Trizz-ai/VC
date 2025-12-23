import asyncio
from app.core.database import get_db
from app.models.meeting import Meeting
from sqlalchemy import select

async def check_meetings():
    async for db in get_db():
        result = await db.execute(select(Meeting))
        meetings = result.scalars().all()
        print(f'Total meetings in database: {len(meetings)}')
        if len(meetings) > 0:
            print(f'\nFirst 5 meetings:')
            for i, meeting in enumerate(meetings[:5], 1):
                print(f'  {i}. {meeting.name} - {meeting.address} (Active: {meeting.is_active})')
        break

if __name__ == "__main__":
    asyncio.run(check_meetings())



