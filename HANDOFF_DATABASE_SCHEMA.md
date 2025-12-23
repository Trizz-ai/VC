# Verified Compliance™ — Database Schema Reference

## Complete Database Documentation

---

## Overview

| Database | Development | Production |
|----------|-------------|------------|
| Engine | SQLite | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 (async) | SQLAlchemy 2.0 (async) |
| Migrations | Alembic | Alembic |

---

## Current Schema (ERD Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │    contacts     │
    ├─────────────────┤
    │ id (PK)         │──────────────────────────────────────────┐
    │ email           │                                          │
    │ phone           │                                          │
    │ first_name      │                                          │
    │ last_name       │                                          │
    │ password_hash   │                                          │
    │ ghl_contact_id  │                                          │
    │ consent_granted │                                          │
    │ consent_timestamp│                                         │
    │ is_active       │                                          │
    │ notes           │                                          │
    │ created_at      │                                          │
    │ updated_at      │                                          │
    └─────────────────┘                                          │
            │                                                     │
            │ 1:N                                                 │
            ▼                                                     │
    ┌─────────────────┐                    ┌─────────────────┐   │
    │    sessions     │                    │    meetings     │   │
    ├─────────────────┤                    ├─────────────────┤   │
    │ id (PK)         │                    │ id (PK)         │   │
    │ contact_id (FK) │◄───────────────────│                 │───┘
    │ meeting_id (FK) │───────────────────►│ name            │
    │ status          │                    │ description     │
    │ dest_name       │                    │ address         │
    │ dest_address    │                    │ lat             │
    │ dest_lat        │                    │ lng             │
    │ dest_lng        │                    │ radius_meters   │
    │ session_notes   │                    │ start_time      │
    │ is_complete     │                    │ end_time        │
    │ created_at      │                    │ is_active       │
    │ updated_at      │                    │ qr_code         │
    └─────────────────┘                    │ created_by      │
            │                              │ created_at      │
            │ 1:N                          │ updated_at      │
            ▼                              └─────────────────┘
    ┌─────────────────┐
    │ session_events  │
    ├─────────────────┤
    │ id (PK)         │
    │ session_id (FK) │
    │ type            │
    │ ts_client       │
    │ ts_server       │
    │ lat             │
    │ lng             │
    │ accuracy        │
    │ location_flag   │
    │ notes           │
    │ created_at      │
    └─────────────────┘
```

---

## Table Definitions

### contacts

Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY | UUID v4 |
| `email` | String(255) | UNIQUE, NOT NULL, INDEX | User email |
| `phone` | String(20) | INDEX | E.164 format |
| `first_name` | String(100) | NULLABLE | First name |
| `last_name` | String(100) | NULLABLE | Last name |
| `password_hash` | String(255) | NULLABLE | Bcrypt hash |
| `ghl_contact_id` | String(100) | UNIQUE, INDEX | GoHighLevel ID |
| `consent_granted` | Boolean | NOT NULL, DEFAULT false | GPS consent |
| `consent_timestamp` | DateTime(tz) | NULLABLE | When consent given |
| `notes` | Text | NULLABLE | Admin notes |
| `is_active` | Boolean | NOT NULL, DEFAULT true, INDEX | Account active |
| `created_at` | DateTime(tz) | NOT NULL, AUTO | Creation timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, AUTO | Update timestamp |

**Indexes:**
- `ix_contacts_email` (email)
- `ix_contacts_phone` (phone)
- `ix_contacts_ghl_contact_id` (ghl_contact_id)
- `ix_contacts_is_active` (is_active)

**SQLAlchemy Model:**
```python
class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=True)
    ghl_contact_id = Column(String(100), unique=True, nullable=True, index=True)
    consent_granted = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="contact")
```

---

### meetings

Stores meeting/location information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY | UUID v4 |
| `name` | String(255) | NOT NULL, INDEX | Meeting name |
| `description` | Text | NULLABLE | Description |
| `address` | String(500) | NOT NULL | Street address |
| `lat` | Float | NOT NULL | Latitude |
| `lng` | Float | NOT NULL | Longitude |
| `radius_meters` | Float | NOT NULL, DEFAULT 100 | Check-in radius |
| `start_time` | DateTime(tz) | NULLABLE | Scheduled start |
| `end_time` | DateTime(tz) | NULLABLE | Scheduled end |
| `is_active` | Boolean | NOT NULL, DEFAULT true, INDEX | Meeting active |
| `qr_code` | String(100) | UNIQUE, INDEX | QR code identifier |
| `created_by` | String(36) | NULLABLE | Admin who created |
| `created_at` | DateTime(tz) | NOT NULL, AUTO | Creation timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, AUTO | Update timestamp |

**Indexes:**
- `ix_meetings_name` (name)
- `ix_meetings_is_active` (is_active)
- `ix_meetings_qr_code` (qr_code)
- `ix_meetings_lat_lng` (lat, lng) - for geospatial queries

**SQLAlchemy Model:**
```python
class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    radius_meters = Column(Float, default=100.0, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    qr_code = Column(String(100), unique=True, nullable=True, index=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="meeting")
```

---

### sessions

Stores attendance sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY | UUID v4 |
| `contact_id` | String(36) | FK → contacts.id, NOT NULL, INDEX | User reference |
| `meeting_id` | String(36) | FK → meetings.id, NULLABLE, INDEX | Meeting reference |
| `status` | String(20) | NOT NULL, DEFAULT 'active', INDEX | Session status |
| `dest_name` | String(255) | NOT NULL | Destination name |
| `dest_address` | String(500) | NOT NULL | Destination address |
| `dest_lat` | Float | NOT NULL | Destination latitude |
| `dest_lng` | Float | NOT NULL | Destination longitude |
| `session_notes` | Text | NULLABLE | User notes |
| `is_complete` | Boolean | NOT NULL, DEFAULT false, INDEX | Completion flag |
| `created_at` | DateTime(tz) | NOT NULL, AUTO | Creation timestamp |
| `updated_at` | DateTime(tz) | NOT NULL, AUTO | Update timestamp |

**Status Values:**
- `active` - Session started, not checked in
- `checked_in` - User has checked in
- `completed` - User has checked out
- `ended` - Session manually ended

**Indexes:**
- `ix_sessions_contact_id` (contact_id)
- `ix_sessions_meeting_id` (meeting_id)
- `ix_sessions_status` (status)
- `ix_sessions_is_complete` (is_complete)
- `ix_sessions_created_at` (created_at)

**SQLAlchemy Model:**
```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=True, index=True)
    status = Column(String(20), default="active", nullable=False, index=True)
    dest_name = Column(String(255), nullable=False)
    dest_address = Column(String(500), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    session_notes = Column(Text, nullable=True)
    is_complete = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contact = relationship("Contact", back_populates="sessions")
    meeting = relationship("Meeting", back_populates="sessions")
    events = relationship("SessionEvent", back_populates="session")
```

---

### session_events

Stores check-in/check-out events.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String(36) | PRIMARY KEY | UUID v4 |
| `session_id` | String(36) | FK → sessions.id, NOT NULL, INDEX | Session reference |
| `type` | Enum | NOT NULL, INDEX | Event type |
| `ts_client` | DateTime(tz) | NOT NULL | Client timestamp |
| `ts_server` | DateTime(tz) | NOT NULL | Server timestamp |
| `lat` | Float | NOT NULL | Latitude |
| `lng` | Float | NOT NULL | Longitude |
| `accuracy` | Float | NULLABLE | GPS accuracy (meters) |
| `location_flag` | Enum | NOT NULL | Location status |
| `notes` | Text | NULLABLE | Event notes |
| `created_at` | DateTime(tz) | NOT NULL, AUTO | Creation timestamp |

**Event Type Values:**
- `check_in` - Arrival event
- `check_out` - Departure event
- `location_update` - Position update
- `status_change` - Status change event

**Location Flag Values:**
- `granted` - Location verified within range
- `denied` - Location outside allowed range
- `timeout` - GPS capture timed out

**Indexes:**
- `ix_session_events_session_id` (session_id)
- `ix_session_events_type` (type)
- `ix_session_events_ts_server` (ts_server)

**SQLAlchemy Model:**
```python
class SessionEvent(Base):
    __tablename__ = "session_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    type = Column(Enum(EventType), nullable=False, index=True)
    ts_client = Column(DateTime(timezone=True), nullable=False)
    ts_server = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    location_flag = Column(Enum(LocationFlag), nullable=False, default=LocationFlag.GRANTED)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="events")
```

---

## Relationships Diagram

```
contacts (1) ──────────────────► (N) sessions
    │                                   │
    │                                   │
    │                                   ▼
    │                           (1) ◄── sessions ──► (N) session_events
    │                                   │
    │                                   │
    │                                   ▼
    │                           (N) ◄── sessions ──► (1) meetings
    │                                   
    └───────────────────────────────────────────────► (N) meetings
                                        (through meeting_contacts - if needed)
```

---

## Migrations

### Current Migrations

| Version | Name | Description |
|---------|------|-------------|
| 001 | initial_migration | Creates all base tables |
| 002 | add_password_hash | Adds password_hash to contacts |

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade 001

# Check current version
alembic current

# View migration history
alembic history
```

### Creating New Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Migration File Template

```python
"""description

Revision ID: xxx
Revises: yyy
Create Date: 2024-12-23 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None

def upgrade():
    # Add table
    op.create_table(
        'table_name',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Add column
    op.add_column('existing_table', sa.Column('new_column', sa.String(100)))
    
    # Create index
    op.create_index('ix_table_column', 'table', ['column'])

def downgrade():
    op.drop_index('ix_table_column')
    op.drop_column('existing_table', 'new_column')
    op.drop_table('table_name')
```

---

## Query Examples

### Find Active Session for Contact

```python
from sqlalchemy import select, and_

async def get_active_session(contact_id: str, db: AsyncSession):
    result = await db.execute(
        select(Session).where(
            and_(
                Session.contact_id == contact_id,
                Session.status.in_(['active', 'checked_in'])
            )
        )
    )
    return result.scalar_one_or_none()
```

### Find Nearby Meetings

```python
from sqlalchemy import select, func
from math import radians, cos, sin, sqrt, atan2

async def find_nearby_meetings(lat: float, lng: float, radius_km: float, db: AsyncSession):
    # Haversine formula in SQL
    result = await db.execute(
        select(Meeting)
        .where(Meeting.is_active == True)
        .order_by(
            # Simplified distance calculation
            func.abs(Meeting.lat - lat) + func.abs(Meeting.lng - lng)
        )
        .limit(25)
    )
    return result.scalars().all()
```

### Get Session with Events

```python
from sqlalchemy.orm import selectinload

async def get_session_with_events(session_id: str, db: AsyncSession):
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.events))
        .where(Session.id == session_id)
    )
    return result.scalar_one_or_none()
```

---

## Planned Schema Changes (v2)

### New Tables Needed

```
consent_artifacts       # Consent records
verification_codes      # 2FA codes
user_identities        # Identity data
jurisdictions          # Policy jurisdictions
policy_versions        # Policy configurations
mandates               # Professional mandates
enrollment_tokens      # SMS enrollment tokens
review_artifacts       # Review decisions
audit_entries          # Audit log
selfie_artifacts       # Biometric captures
data_quality_signals   # Quality metrics
emergency_explanations # Explanation records
message_threads        # Messaging
messages               # Individual messages
verification_proofs    # Integrity proofs
subscriptions          # Stripe subscriptions
```

### Columns to Add

**contacts:**
- `phone_verified` Boolean
- `email_verified` Boolean
- `twofa_enabled` Boolean
- `totp_secret_encrypted` String

**session_events:**
- `selfie_artifact_id` FK
- `device_timestamp` DateTime
- `server_receipt_timestamp` DateTime
- `receipt_id` String
- `policy_version_id` FK

See `epics_v2_enhanced_requirements.md` for complete schema details.

---

## Database Best Practices

### DO:
- ✅ Use String(36) for all UUID primary keys
- ✅ Add indexes on frequently queried columns
- ✅ Use DateTime(timezone=True) for all timestamps
- ✅ Create foreign key constraints
- ✅ Use Enum types for status fields
- ✅ Add created_at/updated_at to all tables

### DON'T:
- ❌ Store sensitive data unencrypted
- ❌ Use auto-increment integers for IDs
- ❌ Skip migrations for schema changes
- ❌ Delete data without soft-delete consideration
- ❌ Query without proper indexes

---

## Backup & Recovery

### Development
- SQLite file: `backend/test.db`
- Simply copy file for backup

### Production
- Use managed PostgreSQL backup features
- Configure daily automated backups
- Test restore procedures regularly

---

**For migration assistance, see `HANDOFF_TECHNICAL.md` or the Alembic documentation.**

