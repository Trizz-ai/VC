"""
Script to create the AYA Demo Meet meeting
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.meeting import Meeting
from app.models.contact import Contact
from app.core.database import create_engine_with_pool_config


async def create_aya_demo_meeting():
    """Create the AYA Demo Meet meeting with all features"""
    
    # Create engine using the same method as the app
    engine = create_engine_with_pool_config()
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if meeting already exists
            result = await session.execute(
                select(Meeting).where(Meeting.name == "AYA Demo Meet")
            )
            existing_meeting = result.scalar_one_or_none()
            
            if existing_meeting:
                print("Meeting 'AYA Demo Meet' already exists!")
                print(f"  ID: {existing_meeting.id}")
                print(f"  Address: {existing_meeting.address}")
                print(f"  Active: {existing_meeting.is_active}")
                # Update it to ensure it has all features
                existing_meeting.is_active = True
                existing_meeting.description = "A comprehensive demo meeting showcasing all AYA system features including GPS verification, session tracking, and attendance management."
                existing_meeting.radius_meters = 100.0
                # Set start time to tomorrow at 10 AM
                existing_meeting.start_time = datetime.now() + timedelta(days=1)
                existing_meeting.start_time = existing_meeting.start_time.replace(hour=10, minute=0, second=0, microsecond=0)
                # Set end time to 4 hours later
                existing_meeting.end_time = existing_meeting.start_time + timedelta(hours=4)
                await session.commit()
                print("✅ Updated existing meeting with all features!")
                return
            
            # Get admin user to set as creator
            admin_result = await session.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            admin_user = admin_result.scalar_one_or_none()
            
            if not admin_user:
                print("❌ Admin user not found! Please create admin user first.")
                return
            
            # Coordinates for 440 Irving St, Brooklyn, NY 11237
            # Approximate coordinates (you may want to geocode for exact)
            lat = 40.7000  # Brooklyn, NY approximate
            lng = -73.9200  # Brooklyn, NY approximate
            
            # Try to get more accurate coordinates - for now using approximate
            # In production, you'd use a geocoding service
            print("📍 Using approximate coordinates for 440 Irving St, Brooklyn, NY 11237")
            print(f"   Latitude: {lat}, Longitude: {lng}")
            
            # Create meeting with all features
            meeting = Meeting(
                name="AYA Demo Meet",
                description="A comprehensive demo meeting showcasing all AYA system features including GPS verification, session tracking, and attendance management. This meeting demonstrates the full capabilities of the Verified Compliance platform.",
                address="440 Irving St, Brooklyn, NY 11237",
                lat=lat,
                lng=lng,
                radius_meters=100.0,  # 100 meter radius for GPS verification
                start_time=datetime.now() + timedelta(days=1),  # Tomorrow
                end_time=datetime.now() + timedelta(days=1, hours=4),  # 4 hours later
                is_active=True,
                created_by=str(admin_user.id),
            )
            
            # Set specific start/end times
            meeting.start_time = meeting.start_time.replace(hour=10, minute=0, second=0, microsecond=0)
            meeting.end_time = meeting.start_time + timedelta(hours=4)
            
            session.add(meeting)
            await session.commit()
            await session.refresh(meeting)
            
            print("=" * 60)
            print("✅ AYA DEMO MEET CREATED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print("Meeting Details:")
            print(f"  ID:          {meeting.id}")
            print(f"  Name:        {meeting.name}")
            print(f"  Description: {meeting.description}")
            print(f"  Address:     {meeting.address}")
            print(f"  Location:    {meeting.lat}, {meeting.lng}")
            print(f"  Radius:      {meeting.radius_meters} meters")
            print(f"  Start Time:  {meeting.start_time}")
            print(f"  End Time:    {meeting.end_time}")
            print(f"  Active:       {meeting.is_active}")
            print(f"  Created By:  {admin_user.email}")
            print()
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error creating meeting: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_aya_demo_meeting())



