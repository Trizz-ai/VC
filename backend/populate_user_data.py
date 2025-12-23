"""
Script to populate meetings and sessions for the admin user
This ensures the logged-in user has data to see
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.meeting import Meeting
from app.models.contact import Contact
from app.models.session import Session
from app.models.session_event import SessionEvent
from app.core.database import create_engine_with_pool_config
from app.models.session import SessionStatus


async def populate_user_data():
    """Populate meetings and sessions for admin user"""
    engine = create_engine_with_pool_config()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Get admin user
            result = await session.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            admin = result.scalar_one_or_none()
            
            if not admin:
                print("❌ Admin user not found!")
                return
            
            print(f"✓ Found admin user: {admin.email} (ID: {admin.id})")
            
            # Check existing meetings
            meeting_result = await session.execute(select(Meeting))
            all_meetings = meeting_result.scalars().all()
            print(f"✓ Found {len(all_meetings)} meetings in database")
            
            # Get some NYC meetings (where most meetings are)
            nyc_meetings = [m for m in all_meetings if 40.6 < m.lat < 40.8 and -74.1 < m.lng < -73.8]
            print(f"✓ Found {len(nyc_meetings)} NYC meetings")
            
            # Check existing sessions for admin
            session_result = await session.execute(
                select(Session).where(Session.contact_id == admin.id)
            )
            admin_sessions = session_result.scalars().all()
            print(f"✓ Admin has {len(admin_sessions)} existing sessions")
            
            # Create some sessions for admin if needed
            if len(admin_sessions) < 10:
                print("\nCreating sessions for admin user...")
                sessions_to_create = 10 - len(admin_sessions)
                
                for i in range(sessions_to_create):
                    meeting = random.choice(nyc_meetings) if nyc_meetings else random.choice(all_meetings[:10])
                    
                    # Create session with various statuses
                    statuses = [SessionStatus.COMPLETED, SessionStatus.COMPLETED, SessionStatus.COMPLETED, SessionStatus.ENDED]
                    status = random.choice(statuses)
                    
                    check_in_time = datetime.utcnow() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
                    check_out_time = None
                    is_complete = False
                    
                    if status == SessionStatus.COMPLETED:
                        check_out_time = check_in_time + timedelta(hours=random.randint(1, 3))
                        is_complete = True
                    
                    session_obj = Session(
                        contact_id=admin.id,
                        meeting_id=meeting.id,
                        dest_name=meeting.name,
                        dest_address=meeting.address,
                        dest_lat=meeting.lat,
                        dest_lng=meeting.lng,
                        status=status,
                        is_complete=is_complete,
                    )
                    
                    session.add(session_obj)
                    await session.flush()
                    
                    # Create check-in event
                    check_in_event = SessionEvent(
                        session_id=session_obj.id,
                        event_type="check_in",
                        latitude=meeting.lat,
                        longitude=meeting.lng,
                        accuracy=10.0,
                        timestamp=check_in_time,
                    )
                    session.add(check_in_event)
                    
                    # Create check-out event if completed
                    if check_out_time:
                        check_out_event = SessionEvent(
                            session_id=session_obj.id,
                            event_type="check_out",
                            latitude=meeting.lat,
                            longitude=meeting.lng,
                            accuracy=10.0,
                            timestamp=check_out_time,
                        )
                        session.add(check_out_event)
                
                await session.commit()
                print(f"✓ Created {sessions_to_create} sessions for admin user")
            
            print("\n" + "=" * 60)
            print("✅ DATA POPULATION COMPLETE!")
            print("=" * 60)
            print(f"  Admin user: {admin.email}")
            print(f"  Total meetings: {len(all_meetings)}")
            print(f"  Admin sessions: {len(admin_sessions) + (10 - len(admin_sessions) if len(admin_sessions) < 10 else 0)}")
            print("\nYou can now:")
            print("  1. Log in with admin@admin.com / admin123")
            print("  2. View meetings in the meeting finder")
            print("  3. View logs in the logs screen")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Populating User Data")
    print("=" * 60)
    print()
    asyncio.run(populate_user_data())



