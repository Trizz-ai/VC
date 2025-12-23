"""
Script to create fake meetings in multiple regions including NYC, Reno/Tahoe, and Nova Scotia
Creates dozens of meetings with wide variety of types and locations
"""

import asyncio
import sys
import random
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


# NYC locations (Manhattan, Brooklyn, Queens, etc.)
NYC_LOCATIONS = [
    # Manhattan
    {"name": "Times Square Conference Center", "address": "1560 Broadway, New York, NY 10036", "lat": 40.7580, "lng": -73.9855},
    {"name": "Central Park Meeting Hall", "address": "59th St & 5th Ave, New York, NY 10019", "lat": 40.7829, "lng": -73.9654},
    {"name": "Empire State Building Suite", "address": "350 5th Ave, New York, NY 10118", "lat": 40.7484, "lng": -73.9857},
    {"name": "Wall Street Business Center", "address": "120 Wall St, New York, NY 10005", "lat": 40.7074, "lng": -74.0113},
    {"name": "Chelsea Market Event Space", "address": "75 9th Ave, New York, NY 10011", "lat": 40.7420, "lng": -74.0048},
    {"name": "SoHo Gallery Meeting Room", "address": "110 Greene St, New York, NY 10012", "lat": 40.7231, "lng": -73.9988},
    {"name": "Upper East Side Club", "address": "1285 Madison Ave, New York, NY 10128", "lat": 40.7851, "lng": -73.9552},
    {"name": "Greenwich Village Community Center", "address": "99 University Pl, New York, NY 10003", "lat": 40.7328, "lng": -73.9960},
    {"name": "Financial District Hub", "address": "55 Water St, New York, NY 10041", "lat": 40.7040, "lng": -74.0087},
    {"name": "Midtown West Office Tower", "address": "1350 Avenue of the Americas, New York, NY 10019", "lat": 40.7614, "lng": -73.9776},
    
    # Brooklyn
    {"name": "Brooklyn Bridge Park Pavilion", "address": "334 Furman St, Brooklyn, NY 11201", "lat": 40.6981, "lng": -73.9972},
    {"name": "Williamsburg Co-Working Space", "address": "25 Broadway, Brooklyn, NY 11249", "lat": 40.7081, "lng": -73.9571},
    {"name": "DUMBO Event Center", "address": "55 Water St, Brooklyn, NY 11201", "lat": 40.7038, "lng": -73.9882},
    {"name": "Park Slope Community Hall", "address": "100 7th Ave, Brooklyn, NY 11215", "lat": 40.6681, "lng": -73.9802},
    {"name": "Prospect Park Meeting Room", "address": "95 Prospect Park West, Brooklyn, NY 11215", "lat": 40.6602, "lng": -73.9689},
    
    # Queens
    {"name": "Long Island City Conference Center", "address": "44-02 11th St, Long Island City, NY 11101", "lat": 40.7447, "lng": -73.9485},
    {"name": "Astoria Community Center", "address": "30-35 21st St, Astoria, NY 11106", "lat": 40.7698, "lng": -73.9258},
    {"name": "Flushing Town Hall", "address": "137-35 Northern Blvd, Flushing, NY 11354", "lat": 40.7627, "lng": -73.8300},
    
    # More Manhattan locations
    {"name": "Lincoln Center Event Space", "address": "70 Lincoln Center Plaza, New York, NY 10023", "lat": 40.7726, "lng": -73.9830},
    {"name": "High Line Meeting Room", "address": "820 Washington St, New York, NY 10014", "lat": 40.7480, "lng": -74.0048},
    {"name": "Tribeca Loft", "address": "120 Hudson St, New York, NY 10013", "lat": 40.7196, "lng": -74.0087},
    {"name": "Upper West Side Library", "address": "190 Amsterdam Ave, New York, NY 10023", "lat": 40.7772, "lng": -73.9816},
    {"name": "East Village Community Space", "address": "75 E 4th St, New York, NY 10003", "lat": 40.7265, "lng": -73.9896},
    {"name": "Hell's Kitchen Event Hall", "address": "750 9th Ave, New York, NY 10019", "lat": 40.7638, "lng": -73.9894},
    {"name": "Lower East Side Gallery", "address": "180 Orchard St, New York, NY 10002", "lat": 40.7189, "lng": -73.9888},
    {"name": "Harlem Cultural Center", "address": "215 W 125th St, New York, NY 10027", "lat": 40.8075, "lng": -73.9505},
    {"name": "Battery Park Conference Room", "address": "1 Battery Pl, New York, NY 10004", "lat": 40.7043, "lng": -74.0173},
    {"name": "Roosevelt Island Community Center", "address": "540 Main St, New York, NY 10044", "lat": 40.7614, "lng": -73.9496},
]

# Reno/Tahoe locations
RENO_TAHOE_LOCATIONS = [
    # Reno
    {"name": "Reno Convention Center", "address": "4590 S Virginia St, Reno, NV 89502", "lat": 39.5000, "lng": -119.8000},
    {"name": "Downtown Reno Event Space", "address": "100 N Virginia St, Reno, NV 89501", "lat": 39.5296, "lng": -119.8138},
    {"name": "Reno-Sparks Convention Center", "address": "4590 S Virginia St, Reno, NV 89502", "lat": 39.4950, "lng": -119.7900},
    {"name": "Peppermill Resort Meeting Room", "address": "2707 S Virginia St, Reno, NV 89502", "lat": 39.4800, "lng": -119.8100},
    {"name": "Atlantis Casino Conference Center", "address": "3800 S Virginia St, Reno, NV 89502", "lat": 39.4700, "lng": -119.8200},
    {"name": "Grand Sierra Resort Ballroom", "address": "2500 E 2nd St, Reno, NV 89595", "lat": 39.5200, "lng": -119.7800},
    {"name": "Reno Business District Hub", "address": "50 W Liberty St, Reno, NV 89501", "lat": 39.5250, "lng": -119.8150},
    {"name": "Reno Airport Plaza Hotel", "address": "1981 Terminal Way, Reno, NV 89502", "lat": 39.5100, "lng": -119.7700},
    {"name": "Reno City Hall Conference Room", "address": "1 E 1st St, Reno, NV 89501", "lat": 39.5300, "lng": -119.8140},
    {"name": "Reno Innovation Hub", "address": "100 W Liberty St, Reno, NV 89501", "lat": 39.5280, "lng": -119.8120},
    
    # Lake Tahoe Area
    {"name": "Lake Tahoe Resort Hotel", "address": "4130 Lake Tahoe Blvd, South Lake Tahoe, CA 96150", "lat": 38.9399, "lng": -119.9772},
    {"name": "Heavenly Village Conference Center", "address": "1001 Heavenly Village Way, South Lake Tahoe, CA 96150", "lat": 38.9556, "lng": -119.9406},
    {"name": "Squaw Valley Alpine Meadows", "address": "1960 Squaw Valley Rd, Olympic Valley, CA 96146", "lat": 39.1967, "lng": -120.2356},
    {"name": "Northstar California Resort", "address": "5001 Northstar Dr, Truckee, CA 96161", "lat": 39.2750, "lng": -120.1214},
    {"name": "Tahoe City Community Center", "address": "870 N Lake Blvd, Tahoe City, CA 96145", "lat": 39.1725, "lng": -120.1447},
    {"name": "Incline Village Conference Center", "address": "969 Tahoe Blvd, Incline Village, NV 89451", "lat": 39.2500, "lng": -119.9500},
    {"name": "Crystal Bay Casino Event Space", "address": "14 State Route 28, Crystal Bay, NV 89402", "lat": 39.2300, "lng": -120.0000},
    {"name": "Tahoe Vista Community Hall", "address": "8511 N Lake Blvd, Tahoe Vista, CA 96148", "lat": 39.2400, "lng": -120.0500},
    {"name": "Kings Beach Meeting Room", "address": "8318 N Lake Blvd, Kings Beach, CA 96143", "lat": 39.2375, "lng": -120.0264},
    {"name": "Homewood Mountain Resort", "address": "5145 West Lake Blvd, Homewood, CA 96141", "lat": 39.0800, "lng": -120.1600},
    
    # More Reno locations
    {"name": "Reno Technology Park", "address": "1055 Corporate Blvd, Reno, NV 89502", "lat": 39.4900, "lng": -119.8000},
    {"name": "Reno Innovation District", "address": "200 W Liberty St, Reno, NV 89501", "lat": 39.5270, "lng": -119.8110},
    {"name": "Reno Arts District Gallery", "address": "150 W Liberty St, Reno, NV 89501", "lat": 39.5260, "lng": -119.8100},
    {"name": "Reno Medical District", "address": "1155 Mill St, Reno, NV 89502", "lat": 39.5150, "lng": -119.8050},
    {"name": "Reno Sports Complex", "address": "2500 E 2nd St, Reno, NV 89595", "lat": 39.5180, "lng": -119.7820},
    
    # More Tahoe locations
    {"name": "Emerald Bay State Park Visitor Center", "address": "138 Emerald Bay Rd, South Lake Tahoe, CA 96150", "lat": 38.9544, "lng": -120.0978},
    {"name": "Tahoe Donner Conference Center", "address": "11509 Northwoods Blvd, Truckee, CA 96161", "lat": 39.3200, "lng": -120.1300},
    {"name": "Diamond Peak Ski Resort", "address": "1210 Ski Way, Incline Village, NV 89451", "lat": 39.2500, "lng": -119.9400},
    {"name": "Mount Rose Ski Resort", "address": "22222 Mt Rose Hwy, Reno, NV 89511", "lat": 39.3300, "lng": -119.8800},
    {"name": "Sand Harbor State Park", "address": "2005 NV-28, Incline Village, NV 89452", "lat": 39.1967, "lng": -119.9300},
]

# Nova Scotia locations (Halifax, Dartmouth, Sydney, etc.)
NOVA_SCOTIA_LOCATIONS = [
    # Halifax
    {"name": "Halifax Convention Centre", "address": "1650 Argyle St, Halifax, NS B3J 0E6", "lat": 44.6488, "lng": -63.5752},
    {"name": "Halifax Central Library", "address": "5440 Spring Garden Rd, Halifax, NS B3J 1E9", "lat": 44.6415, "lng": -63.5753},
    {"name": "Halifax Citadel National Historic Site", "address": "5425 Sackville St, Halifax, NS B3J 1Y1", "lat": 44.6488, "lng": -63.5806},
    {"name": "Halifax Waterfront Boardwalk", "address": "1595 Lower Water St, Halifax, NS B3J 1S3", "lat": 44.6444, "lng": -63.5714},
    {"name": "Dalhousie University Student Union", "address": "6136 University Ave, Halifax, NS B3H 4R2", "lat": 44.6368, "lng": -63.5914},
    {"name": "Halifax Public Gardens", "address": "5665 Spring Garden Rd, Halifax, NS B3J 1H6", "lat": 44.6408, "lng": -63.5803},
    {"name": "Halifax Seaport Farmers Market", "address": "1209 Marginal Rd, Halifax, NS B3H 4P8", "lat": 44.6400, "lng": -63.5678},
    {"name": "Halifax City Hall", "address": "1841 Argyle St, Halifax, NS B3J 2V1", "lat": 44.6480, "lng": -63.5750},
    {"name": "Halifax Discovery Centre", "address": "1593 Barrington St, Halifax, NS B3J 1Z7", "lat": 44.6465, "lng": -63.5758},
    {"name": "Halifax Forum Multi-Purpose Centre", "address": "2901 Windsor St, Halifax, NS B3K 5E5", "lat": 44.6550, "lng": -63.5900},
    {"name": "Halifax Shopping Centre", "address": "7001 Mumford Rd, Halifax, NS B3L 4N9", "lat": 44.6500, "lng": -63.6100},
    {"name": "Point Pleasant Park", "address": "5718 Point Pleasant Dr, Halifax, NS B3H 1B5", "lat": 44.6200, "lng": -63.5700},
    {"name": "Halifax Harbourfront", "address": "1675 Lower Water St, Halifax, NS B3J 1S3", "lat": 44.6430, "lng": -63.5700},
    {"name": "Halifax North End Community Centre", "address": "2305 Gottingen St, Halifax, NS B3K 3B5", "lat": 44.6550, "lng": -63.5850},
    {"name": "Halifax Commons", "address": "5816 Cogswell St, Halifax, NS B3H 1W3", "lat": 44.6480, "lng": -63.5850},
    
    # Dartmouth
    {"name": "Dartmouth Sportsplex", "address": "110 Wyse Rd, Dartmouth, NS B3A 1M2", "lat": 44.6800, "lng": -63.5700},
    {"name": "Alderney Landing", "address": "2 Ochterloney St, Dartmouth, NS B2Y 3Z3", "lat": 44.6700, "lng": -63.5700},
    {"name": "Dartmouth Crossing Shopping Centre", "address": "100 Shubie Dr, Dartmouth, NS B3B 1M2", "lat": 44.7000, "lng": -63.5500},
    {"name": "Dartmouth Heritage Museum", "address": "26 Newcastle St, Dartmouth, NS B2Y 3M5", "lat": 44.6700, "lng": -63.5750},
    {"name": "Dartmouth Community Centre", "address": "57 Highfield Park Dr, Dartmouth, NS B2V 1G1", "lat": 44.6800, "lng": -63.5600},
    {"name": "Lake Banook", "address": "123 Prince Albert Rd, Dartmouth, NS B2Y 1A1", "lat": 44.6750, "lng": -63.5650},
    {"name": "Dartmouth Ferry Terminal", "address": "88 Alderney Dr, Dartmouth, NS B2Y 4N8", "lat": 44.6700, "lng": -63.5700},
    {"name": "Dartmouth North Community Centre", "address": "105 Highfield Park Dr, Dartmouth, NS B2V 1G1", "lat": 44.6850, "lng": -63.5600},
    
    # Sydney
    {"name": "Sydney Marine Terminal", "address": "74 Esplanade, Sydney, NS B1P 1A1", "lat": 46.1400, "lng": -60.1900},
    {"name": "Cape Breton University", "address": "1250 Grand Lake Rd, Sydney, NS B1P 6L2", "lat": 46.1200, "lng": -60.2000},
    {"name": "Sydney Waterfront", "address": "74 Esplanade, Sydney, NS B1P 1A1", "lat": 46.1380, "lng": -60.1920},
    {"name": "Sydney Mines Community Centre", "address": "275 Main St, Sydney Mines, NS B1V 1A1", "lat": 46.2400, "lng": -60.2200},
    {"name": "Membertou Trade & Convention Centre", "address": "50 Maillard St, Membertou, NS B1S 3W3", "lat": 46.1300, "lng": -60.1800},
    
    # Other Nova Scotia locations
    {"name": "Lunenburg Academy", "address": "97 Kaulbach St, Lunenburg, NS B0J 2C0", "lat": 44.3800, "lng": -64.3100},
    {"name": "Peggy's Cove Lighthouse", "address": "Peggy's Cove, NS B3Z 3S2", "lat": 44.4925, "lng": -63.9167},
    {"name": "Wolfville Farmers Market", "address": "24 Elm Ave, Wolfville, NS B4P 1N4", "lat": 45.0900, "lng": -64.3600},
    {"name": "Acadia University", "address": "15 University Ave, Wolfville, NS B4P 2R6", "lat": 45.0850, "lng": -64.3650},
    {"name": "Annapolis Royal Historic Gardens", "address": "441 St George St, Annapolis Royal, NS B0S 1A0", "lat": 44.7400, "lng": -65.5200},
    {"name": "Truro Farmers Market", "address": "15 Young St, Truro, NS B2N 4E5", "lat": 45.3650, "lng": -63.2950},
    {"name": "Bridgewater Community Centre", "address": "30 Dominion St, Bridgewater, NS B4V 1G5", "lat": 44.3800, "lng": -64.5200},
    {"name": "Yarmouth Waterfront", "address": "400 Main St, Yarmouth, NS B5A 1K2", "lat": 43.8400, "lng": -66.1200},
    {"name": "Kentville Farmers Market", "address": "67 Cornwallis St, Kentville, NS B4N 2E3", "lat": 45.0800, "lng": -64.5000},
    {"name": "Amherst Community Centre", "address": "185 Church St, Amherst, NS B4H 3C4", "lat": 45.8300, "lng": -64.2100},
    {"name": "New Glasgow Community Centre", "address": "219 Stellarton Rd, New Glasgow, NS B2H 5E1", "lat": 45.5900, "lng": -62.6500},
    {"name": "Antigonish Farmers Market", "address": "350 Main St, Antigonish, NS B2G 2C3", "lat": 45.6200, "lng": -61.9900},
    {"name": "St. Francis Xavier University", "address": "1 West St, Antigonish, NS B2G 2W5", "lat": 45.6150, "lng": -61.9950},
]

MEETING_TYPES = [
    "Business Meeting",
    "Networking Event",
    "Training Session",
    "Workshop",
    "Conference",
    "Seminar",
    "Team Building",
    "Client Presentation",
    "Strategy Session",
    "Product Launch",
    "Community Gathering",
    "Annual Meeting",
    "Board Meeting",
    "Town Hall",
    "Focus Group",
    "AA Meeting",
    "NA Meeting",
    "Support Group",
    "Fitness Class",
    "Yoga Session",
    "Gym Workout",
    "Church Service",
    "Bible Study",
    "Community Service",
    "Volunteer Meeting",
    "Book Club",
    "Art Workshop",
    "Music Lesson",
    "Cooking Class",
    "Language Exchange",
    "Tech Meetup",
    "Startup Pitch",
    "Investor Meeting",
    "Real Estate Open House",
    "Educational Seminar",
    "Health & Wellness",
    "Meditation Group",
    "Running Club",
    "Cycling Group",
    "Hiking Group",
]

DESCRIPTIONS = [
    "Join us for an engaging discussion and networking opportunity.",
    "Professional development and skill-building session.",
    "Connect with industry leaders and peers.",
    "Learn about the latest trends and best practices.",
    "Collaborative workshop with hands-on activities.",
    "Strategic planning and goal-setting session.",
    "Informative presentation followed by Q&A.",
    "Interactive session with group activities.",
    "Networking mixer with refreshments provided.",
    "Educational seminar with expert speakers.",
]


def generate_meeting_name(location_name: str, meeting_type: str) -> str:
    """Generate a meeting name"""
    return f"{meeting_type} at {location_name}"


def generate_start_time() -> datetime:
    """Generate a random start time in the future"""
    days_ahead = random.randint(1, 90)  # 1-90 days in the future
    hours = random.randint(9, 17)  # Business hours
    minutes = random.choice([0, 15, 30, 45])
    
    start = datetime.now() + timedelta(days=days_ahead, hours=hours, minutes=minutes)
    return start.replace(second=0, microsecond=0)


def generate_end_time(start_time: datetime) -> datetime:
    """Generate an end time based on start time"""
    duration_hours = random.choice([1, 2, 3, 4, 6, 8])
    return start_time + timedelta(hours=duration_hours)


async def create_fake_meetings():
    """Create fake meetings in NYC and Reno/Tahoe"""
    
    # Create engine
    engine = create_engine_with_pool_config()
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Get admin user for created_by field
            result = await session.execute(
                select(Contact).where(Contact.email == "admin@admin.com")
            )
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                print("⚠️  Admin user not found. Creating meetings without creator...")
                admin_id = None
            else:
                admin_id = admin_user.id
            
            meetings_created = 0
            
            # Create NYC meetings (3-4 per location for variety)
            print("Creating NYC meetings...")
            for location in NYC_LOCATIONS:
                meetings_per_location = random.randint(3, 4)
                for _ in range(meetings_per_location):
                    meeting_type = random.choice(MEETING_TYPES)
                    name = generate_meeting_name(location["name"], meeting_type)
                    description = random.choice(DESCRIPTIONS)
                    
                    start_time = generate_start_time()
                    end_time = generate_end_time(start_time)
                    
                    # Add some variation to coordinates (within ~500m radius)
                    lat_offset = random.uniform(-0.005, 0.005)  # ~500m
                    lng_offset = random.uniform(-0.005, 0.005)
                    
                    meeting = Meeting(
                        name=name,
                        description=description,
                        address=location["address"],
                        lat=location["lat"] + lat_offset,
                        lng=location["lng"] + lng_offset,
                        radius_meters=random.choice([50, 100, 150, 200]),
                        start_time=start_time,
                        end_time=end_time,
                        is_active=True,
                        created_by=admin_id,
                    )
                    
                    session.add(meeting)
                    meetings_created += 1
            
            # Create Reno/Tahoe meetings (3-4 per location)
            print("Creating Reno/Tahoe meetings...")
            for location in RENO_TAHOE_LOCATIONS:
                meetings_per_location = random.randint(3, 4)
                for _ in range(meetings_per_location):
                    meeting_type = random.choice(MEETING_TYPES)
                    name = generate_meeting_name(location["name"], meeting_type)
                    description = random.choice(DESCRIPTIONS)
                    
                    start_time = generate_start_time()
                    end_time = generate_end_time(start_time)
                    
                    # Add some variation to coordinates
                    lat_offset = random.uniform(-0.005, 0.005)
                    lng_offset = random.uniform(-0.005, 0.005)
                    
                    meeting = Meeting(
                        name=name,
                        description=description,
                        address=location["address"],
                        lat=location["lat"] + lat_offset,
                        lng=location["lng"] + lng_offset,
                        radius_meters=random.choice([50, 100, 150, 200]),
                        start_time=start_time,
                        end_time=end_time,
                        is_active=True,
                        created_by=admin_id,
                    )
                    
                    session.add(meeting)
                    meetings_created += 1
            
            # Create Nova Scotia meetings (3-4 per location)
            print("Creating Nova Scotia meetings...")
            for location in NOVA_SCOTIA_LOCATIONS:
                meetings_per_location = random.randint(3, 4)
                for _ in range(meetings_per_location):
                    meeting_type = random.choice(MEETING_TYPES)
                    name = generate_meeting_name(location["name"], meeting_type)
                    description = random.choice(DESCRIPTIONS)
                    
                    start_time = generate_start_time()
                    end_time = generate_end_time(start_time)
                    
                    # Add some variation to coordinates
                    lat_offset = random.uniform(-0.005, 0.005)
                    lng_offset = random.uniform(-0.005, 0.005)
                    
                    meeting = Meeting(
                        name=name,
                        description=description,
                        address=location["address"],
                        lat=location["lat"] + lat_offset,
                        lng=location["lng"] + lng_offset,
                        radius_meters=random.choice([50, 100, 150, 200]),
                        start_time=start_time,
                        end_time=end_time,
                        is_active=True,
                        created_by=admin_id,
                    )
                    
                    session.add(meeting)
                    meetings_created += 1
            
            # Commit all meetings
            await session.commit()
            
            print("=" * 60)
            print(f"✅ SUCCESSFULLY CREATED {meetings_created} MEETINGS!")
            print("=" * 60)
            print()
            print(f"  NYC Area: ~{len(NYC_LOCATIONS) * 3} meetings")
            print(f"  Reno/Tahoe Area: ~{len(RENO_TAHOE_LOCATIONS) * 3} meetings")
            print(f"  Nova Scotia Area: ~{len(NOVA_SCOTIA_LOCATIONS) * 3} meetings")
            print()
            print("All meetings are:")
            print("  ✓ Active")
            print("  ✓ Have realistic addresses and coordinates")
            print("  ✓ Scheduled for future dates")
            print("  ✓ Have random meeting types and descriptions")
            print("  ✓ Include diverse types: AA, NA, Gym, Church, Business, etc.")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error creating meetings: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_fake_meetings())

