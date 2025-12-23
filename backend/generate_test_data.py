"""
Generate comprehensive test data for the Verified Compliance application
Creates meetings, sessions, and events for thorough testing
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.contact import Contact
from app.models.meeting import Meeting
from app.models.session import Session, SessionStatus
from app.models.session_event import SessionEvent, EventType, LocationFlag


# Sample locations (realistic addresses in various cities)
SAMPLE_LOCATIONS = [
    {"name": "Downtown Office", "address": "123 Main St, New York, NY 10001", "lat": 40.7128, "lng": -74.0060},
    {"name": "Tech Hub", "address": "456 Silicon Valley Blvd, San Francisco, CA 94102", "lat": 37.7749, "lng": -122.4194},
    {"name": "Corporate Center", "address": "789 Business Park Dr, Chicago, IL 60601", "lat": 41.8781, "lng": -87.6298},
    {"name": "Regional Office", "address": "321 Commerce St, Dallas, TX 75201", "lat": 32.7767, "lng": -96.7970},
    {"name": "Headquarters", "address": "555 Innovation Way, Boston, MA 02101", "lat": 42.3601, "lng": -71.0589},
    {"name": "West Coast Branch", "address": "888 Pacific Ave, Los Angeles, CA 90001", "lat": 34.0522, "lng": -118.2437},
    {"name": "East Coast Office", "address": "222 Atlantic Blvd, Miami, FL 33101", "lat": 25.7617, "lng": -80.1918},
    {"name": "Midwest Facility", "address": "777 Great Lakes Dr, Detroit, MI 48201", "lat": 42.3314, "lng": -83.0458},
    {"name": "Southwest Office", "address": "999 Desert View Rd, Phoenix, AZ 85001", "lat": 33.4484, "lng": -112.0740},
    {"name": "Northwest Branch", "address": "111 Rainy St, Seattle, WA 98101", "lat": 47.6062, "lng": -122.3321},
]

MEETING_TYPES = [
    "Team Standup",
    "Client Meeting",
    "Project Review",
    "Training Session",
    "All Hands",
    "Sprint Planning",
    "Retrospective",
    "One-on-One",
    "Department Meeting",
    "Board Meeting",
    "Workshop",
    "Conference Call",
    "Site Visit",
    "Field Work",
    "Compliance Check",
]


async def get_admin_user(db: AsyncSession) -> Contact:
    """Get the admin user"""
    result = await db.execute(
        select(Contact).where(Contact.email == "admin@admin.com")
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise Exception("Admin user not found! Please run create_admin_user.py first")
    return admin


async def create_meetings(db: AsyncSession, admin: Contact, count: int = 50) -> List[Meeting]:
    """Create various meetings with different scenarios"""
    meetings = []
    now = datetime.utcnow()
    
    print(f"Creating {count} meetings...")
    
    for i in range(count):
        location = random.choice(SAMPLE_LOCATIONS)
        meeting_type = random.choice(MEETING_TYPES)
        
        # Create different types of meetings
        if i < 10:
            # Past meetings (completed)
            start_time = now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 12))
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            is_active = False
        elif i < 20:
            # Upcoming meetings (future)
            start_time = now + timedelta(days=random.randint(1, 30), hours=random.randint(0, 12))
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            is_active = True
        elif i < 25:
            # Active meetings (happening now)
            start_time = now - timedelta(hours=random.randint(0, 2))
            end_time = now + timedelta(hours=random.randint(1, 3))
            is_active = True
        elif i < 30:
            # Meetings starting soon (within next hour)
            start_time = now + timedelta(minutes=random.randint(5, 60))
            end_time = start_time + timedelta(hours=random.randint(1, 3))
            is_active = True
        else:
            # Random mix
            if random.random() < 0.3:
                # Past
                start_time = now - timedelta(days=random.randint(1, 60))
                end_time = start_time + timedelta(hours=random.randint(1, 4))
                is_active = random.choice([True, False])
            else:
                # Future
                start_time = now + timedelta(days=random.randint(1, 60))
                end_time = start_time + timedelta(hours=random.randint(1, 4))
                is_active = True
        
        meeting = Meeting(
            name=f"{meeting_type} - {location['name']}",
            description=f"Meeting at {location['name']} for {meeting_type.lower()}",
            address=location['address'],
            lat=location['lat'] + random.uniform(-0.01, 0.01),  # Slight variation
            lng=location['lng'] + random.uniform(-0.01, 0.01),
            radius_meters=random.choice([50, 100, 150, 200]),
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
            created_by=str(admin.id),
        )
        
        db.add(meeting)
        meetings.append(meeting)
    
    await db.commit()
    for meeting in meetings:
        await db.refresh(meeting)
    
    print(f"✓ Created {len(meetings)} meetings")
    return meetings


async def create_sessions(
    db: AsyncSession,
    admin: Contact,
    meetings: List[Meeting],
    count_per_meeting: int = 1
) -> List[Session]:
    """Create sessions for meetings with various scenarios"""
    sessions = []
    now = datetime.utcnow()
    
    print(f"Creating sessions for meetings...")
    
    # Create sessions for past meetings (completed)
    past_meetings = [m for m in meetings if m.end_time and m.end_time < now]
    for meeting in past_meetings[:20]:  # Create sessions for first 20 past meetings
        # 70% chance of having a session for past meeting
        if random.random() < 0.7:
            session = Session(
                contact_id=str(admin.id),
                meeting_id=str(meeting.id),
                dest_name=meeting.name,
                dest_address=meeting.address,
                dest_lat=meeting.lat,
                dest_lng=meeting.lng,
                session_notes=f"Session for {meeting.name}",
                status=SessionStatus.COMPLETED,
                is_complete=True,
            )
            db.add(session)
            sessions.append(session)
    
    # Create sessions for active/upcoming meetings
    active_meetings = [m for m in meetings if m.is_active and (not m.end_time or m.end_time >= now)]
    for meeting in active_meetings[:10]:  # Create sessions for first 10 active meetings
        # 50% chance of having an active session
        if random.random() < 0.5:
            session = Session(
                contact_id=str(admin.id),
                meeting_id=str(meeting.id),
                dest_name=meeting.name,
                dest_address=meeting.address,
                dest_lat=meeting.lat,
                dest_lng=meeting.lng,
                session_notes=f"Active session for {meeting.name}",
                status=random.choice([SessionStatus.ACTIVE, SessionStatus.CHECKED_IN]),
                is_complete=False,
            )
            db.add(session)
            sessions.append(session)
    
    await db.commit()
    for session in sessions:
        await db.refresh(session)
    
    print(f"✓ Created {len(sessions)} sessions")
    return sessions


async def create_session_events(
    db: AsyncSession,
    sessions: List[Session]
) -> List[SessionEvent]:
    """Create check-in and check-out events for sessions"""
    events = []
    now = datetime.utcnow()
    
    print(f"Creating session events...")
    
    for session in sessions:
        # Get meeting to determine timing
        meeting = None
        if session.meeting_id:
            result = await db.execute(
                select(Meeting).where(Meeting.id == session.meeting_id)
            )
            meeting = result.scalar_one_or_none()
        
        # For completed sessions, create check-in and check-out
        if session.status == SessionStatus.COMPLETED:
            # Check-in event
            check_in_time = None
            if meeting and meeting.start_time:
                check_in_time = meeting.start_time + timedelta(minutes=random.randint(-15, 15))
            else:
                check_in_time = now - timedelta(days=random.randint(1, 30), hours=random.randint(1, 8))
            
            check_in_event = SessionEvent(
                session_id=str(session.id),
                type=EventType.CHECK_IN,
                ts_client=check_in_time,
                ts_server=check_in_time + timedelta(seconds=random.randint(1, 5)),
                lat=session.dest_lat + random.uniform(-0.0001, 0.0001),
                lng=session.dest_lng + random.uniform(-0.0001, 0.0001),
                accuracy=random.uniform(5, 50),
                location_flag=LocationFlag.GRANTED,
                notes="Checked in at meeting location",
            )
            db.add(check_in_event)
            events.append(check_in_event)
            
            # Check-out event
            check_out_time = None
            if meeting and meeting.end_time:
                check_out_time = meeting.end_time + timedelta(minutes=random.randint(-30, 30))
            else:
                check_out_time = check_in_time + timedelta(hours=random.randint(1, 4))
            
            check_out_event = SessionEvent(
                session_id=str(session.id),
                type=EventType.CHECK_OUT,
                ts_client=check_out_time,
                ts_server=check_out_time + timedelta(seconds=random.randint(1, 5)),
                lat=session.dest_lat + random.uniform(-0.0001, 0.0001),
                lng=session.dest_lng + random.uniform(-0.0001, 0.0001),
                accuracy=random.uniform(5, 50),
                location_flag=LocationFlag.GRANTED,
                notes="Checked out from meeting",
            )
            db.add(check_out_event)
            events.append(check_out_event)
        
        # For checked-in sessions, create check-in but no check-out
        elif session.status == SessionStatus.CHECKED_IN:
            check_in_time = None
            if meeting and meeting.start_time:
                check_in_time = meeting.start_time + timedelta(minutes=random.randint(-15, 15))
            else:
                check_in_time = now - timedelta(hours=random.randint(0, 4))
            
            check_in_event = SessionEvent(
                session_id=str(session.id),
                type=EventType.CHECK_IN,
                ts_client=check_in_time,
                ts_server=check_in_time + timedelta(seconds=random.randint(1, 5)),
                lat=session.dest_lat + random.uniform(-0.0001, 0.0001),
                lng=session.dest_lng + random.uniform(-0.0001, 0.0001),
                accuracy=random.uniform(5, 50),
                location_flag=LocationFlag.GRANTED,
                notes="Checked in at meeting location",
            )
            db.add(check_in_event)
            events.append(check_in_event)
        
        # For active sessions, maybe add some location updates
        elif session.status == SessionStatus.ACTIVE and random.random() < 0.3:
            update_time = now - timedelta(minutes=random.randint(5, 60))
            location_update = SessionEvent(
                session_id=str(session.id),
                type=EventType.LOCATION_UPDATE,
                ts_client=update_time,
                ts_server=update_time + timedelta(seconds=random.randint(1, 5)),
                lat=session.dest_lat + random.uniform(-0.001, 0.001),
                lng=session.dest_lng + random.uniform(-0.001, 0.001),
                accuracy=random.uniform(10, 100),
                location_flag=LocationFlag.GRANTED,
                notes="Location update",
            )
            db.add(location_update)
            events.append(location_update)
    
    await db.commit()
    print(f"✓ Created {len(events)} session events")
    return events


async def create_general_sessions(db: AsyncSession, admin: Contact, count: int = 5) -> List[Session]:
    """Create some general sessions (without meetings)"""
    sessions = []
    now = datetime.utcnow()
    
    print(f"Creating {count} general sessions...")
    
    for i in range(count):
        location = random.choice(SAMPLE_LOCATIONS)
        
        # Mix of active and completed general sessions
        if i < 2:
            status = SessionStatus.ACTIVE
            is_complete = False
        else:
            status = SessionStatus.COMPLETED
            is_complete = True
        
        session = Session(
            contact_id=str(admin.id),
            meeting_id=None,
            dest_name=f"General Session - {location['name']}",
            dest_address=location['address'],
            dest_lat=location['lat'],
            dest_lng=location['lng'],
            session_notes=f"General session created on {now.strftime('%Y-%m-%d')}",
            status=status,
            is_complete=is_complete,
        )
        db.add(session)
        sessions.append(session)
    
    await db.commit()
    for session in sessions:
        await db.refresh(session)
    
    print(f"✓ Created {len(sessions)} general sessions")
    return sessions


async def main():
    """Main function to generate all test data"""
    print("=" * 60)
    print("Generating Comprehensive Test Data")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # Get admin user
            print("1. Getting admin user...")
            admin = await get_admin_user(db)
            print(f"✓ Found admin user: {admin.email} (ID: {admin.id})")
            print()
            
            # Create meetings
            print("2. Creating meetings...")
            meetings = await create_meetings(db, admin, count=50)
            print()
            
            # Create sessions
            print("3. Creating sessions...")
            sessions = await create_sessions(db, admin, meetings)
            print()
            
            # Create general sessions
            print("4. Creating general sessions...")
            general_sessions = await create_general_sessions(db, admin, count=5)
            all_sessions = sessions + general_sessions
            print()
            
            # Create session events
            print("5. Creating session events...")
            events = await create_session_events(db, all_sessions)
            print()
            
            # Summary
            print("=" * 60)
            print("✅ TEST DATA GENERATION COMPLETE!")
            print("=" * 60)
            print()
            print("Summary:")
            print(f"  • Meetings created: {len(meetings)}")
            print(f"  • Sessions created: {len(all_sessions)}")
            print(f"  • Session events created: {len(events)}")
            print()
            print("Meeting breakdown:")
            past = len([m for m in meetings if m.end_time and m.end_time < datetime.utcnow()])
            upcoming = len([m for m in meetings if m.start_time and m.start_time > datetime.utcnow()])
            active = len([m for m in meetings if m.is_active])
            print(f"  • Past meetings: {past}")
            print(f"  • Upcoming meetings: {upcoming}")
            print(f"  • Active meetings: {active}")
            print()
            print("Session breakdown:")
            completed = len([s for s in all_sessions if s.status == SessionStatus.COMPLETED])
            checked_in = len([s for s in all_sessions if s.status == SessionStatus.CHECKED_IN])
            active_sessions = len([s for s in all_sessions if s.status == SessionStatus.ACTIVE])
            print(f"  • Completed sessions: {completed}")
            print(f"  • Checked-in sessions: {checked_in}")
            print(f"  • Active sessions: {active_sessions}")
            print()
            print("You can now test the application with this comprehensive data!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error generating test data: {e}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())



