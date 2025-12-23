# Verified Compliance™ — Technical Handoff Document

## For Developers: Deep Architecture & Code Walkthrough

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Deep Dive](#backend-deep-dive)
3. [Frontend Deep Dive](#frontend-deep-dive)
4. [Database Architecture](#database-architecture)
5. [API Design Patterns](#api-design-patterns)
6. [Authentication & Security](#authentication--security)
7. [Code Patterns & Conventions](#code-patterns--conventions)
8. [Common Tasks & How-Tos](#common-tasks--how-tos)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                     │
├─────────────────────┬───────────────────────┬───────────────────────────┤
│   Flutter Mobile    │    Flutter Web        │    Professional Portal    │
│   (iOS/Android)     │    (Chrome)           │    (React - Future)       │
└─────────┬───────────┴───────────┬───────────┴───────────────┬───────────┘
          │                       │                           │
          │         HTTPS (TLS 1.3)                          │
          │                       │                           │
          ▼                       ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                            │
│                         /api/v1/*                                        │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    Auth     │  │  Sessions   │  │  Meetings   │  │   Admin     │    │
│  │  Endpoints  │  │  Endpoints  │  │  Endpoints  │  │  Endpoints  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Contact   │  │   Session   │  │   Meeting   │  │    GHL      │    │
│  │   Service   │  │   Service   │  │   Service   │  │   Service   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (SQLAlchemy)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Contact   │  │   Session   │  │   Meeting   │  │   Session   │    │
│  │    Model    │  │    Model    │  │    Model    │  │    Event    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL / SQLite Database                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Request Flow Example: Check-In

```
1. User taps "Check In" button in Flutter app
2. Flutter requests GPS coordinates from device
3. Flutter sends POST /api/v1/sessions/{id}/check-in with:
   - JWT token in Authorization header
   - Location data in body
4. FastAPI validates JWT token
5. SessionService.check_in() is called
6. LocationService.verify_location() checks proximity to meeting
7. SessionEvent is created with event_type=CHECK_IN
8. Session status updated to CHECKED_IN
9. GHL webhook triggered (async)
10. Response returned to Flutter
11. Flutter updates UI to show checked-in state
```

---

## Backend Deep Dive

### Directory Structure Explained

```
backend/
├── app/
│   ├── __init__.py              # Empty, marks as package
│   ├── main.py                  # FastAPI app initialization
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Main router aggregating all endpoints
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py      # Login, registration, token refresh
│   │           ├── contacts.py  # Contact CRUD
│   │           ├── meetings.py  # Meeting discovery & management
│   │           ├── sessions.py  # Session lifecycle (check-in/out)
│   │           ├── admin.py     # Admin-only endpoints
│   │           ├── public.py    # Public share pages
│   │           ├── offline.py   # Offline sync endpoints
│   │           ├── ai.py        # AI assistant endpoints
│   │           ├── biometric.py # Biometric capture (stub)
│   │           ├── payments.py  # Stripe integration (stub)
│   │           └── ghl_webhooks.py # GHL webhook handlers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings from environment
│   │   ├── database.py          # PostgreSQL connection
│   │   ├── database_sqlite.py   # SQLite for development
│   │   ├── auth.py              # JWT token handling
│   │   ├── exceptions.py        # Custom exception classes
│   │   └── logging.py           # Logging configuration
│   │
│   ├── models/
│   │   ├── __init__.py          # Exports all models
│   │   ├── base.py              # SQLAlchemy Base class
│   │   ├── contact.py           # User/Contact model
│   │   ├── meeting.py           # Meeting location model
│   │   ├── session.py           # Attendance session model
│   │   └── session_event.py     # Check-in/out events model
│   │
│   ├── schemas/
│   │   ├── __init__.py          # Exports all schemas
│   │   ├── auth.py              # Auth request/response schemas
│   │   ├── contact.py           # Contact schemas
│   │   ├── meeting.py           # Meeting schemas
│   │   ├── session.py           # Session schemas
│   │   └── offline.py           # Offline sync schemas
│   │
│   └── services/
│       ├── __init__.py
│       ├── contact_service.py   # Contact business logic
│       ├── session_service.py   # Session business logic
│       ├── meeting_service.py   # Meeting business logic
│       ├── location_service.py  # GPS verification logic
│       ├── ghl_service.py       # GoHighLevel integration
│       ├── email_service.py     # Email sending
│       ├── ai_service.py        # AI assistant logic
│       ├── biometric_service.py # Biometric processing (stub)
│       ├── payment_service.py   # Stripe integration (stub)
│       └── offline_service.py   # Offline sync logic
│
├── alembic/
│   ├── env.py                   # Migration environment
│   └── versions/                # Migration files
│       ├── 001_initial_migration.py
│       └── 002_add_password_hash.py
│
├── tests/                       # Test files
│   ├── conftest.py              # Pytest fixtures
│   └── test_*.py                # Test modules
│
├── pyproject.toml               # Dependencies (Poetry)
├── alembic.ini                  # Alembic configuration
└── Dockerfile                   # Container definition
```

### Key Files Walkthrough

#### `app/main.py` - Application Entry Point

```python
# This file initializes the FastAPI application
# Key things happening here:
# 1. Creates FastAPI app instance
# 2. Configures CORS middleware
# 3. Includes all API routers
# 4. Sets up exception handlers
# 5. Creates database tables on startup (dev mode)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="Verified Compliance API",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
)

# CORS - allows Flutter web to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix="/api/v1")
```

#### `app/core/database.py` - Database Connection

```python
# Database connection management
# Uses async SQLAlchemy for non-blocking database operations

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Engine created from DATABASE_URL environment variable
engine = create_async_engine(settings.DATABASE_URL)

# Session factory for creating database sessions
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency for FastAPI endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

#### `app/models/session.py` - Session Model Example

```python
# Models define database schema using SQLAlchemy ORM
# Key patterns:
# 1. String(36) for UUID primary keys
# 2. Enum for status fields
# 3. Relationships for related models
# 4. Properties for computed values

class Session(Base):
    __tablename__ = "sessions"
    
    # Primary key - UUID as string
    id = Column(String(36), primary_key=True, 
                default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    contact_id = Column(String(36), ForeignKey("contacts.id"), 
                       nullable=False, index=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id"), 
                       nullable=True, index=True)
    
    # Status tracking
    status = Column(String(20), default=SessionStatus.ACTIVE)
    
    # Relationships - use back_populates for bidirectional
    contact = relationship("Contact", back_populates="sessions")
    events = relationship("SessionEvent", back_populates="session")
    
    # Computed properties
    @property
    def is_checked_in(self) -> bool:
        return any(event.type == "check_in" for event in self.events)
```

#### `app/services/session_service.py` - Service Layer Example

```python
# Services contain business logic
# Key patterns:
# 1. Methods are async
# 2. Database session passed as parameter
# 3. Logging throughout
# 4. Error handling with specific exceptions

class SessionService:
    def __init__(self):
        self.location_service = LocationService()
    
    async def create_session(
        self,
        contact_id: str,
        meeting_id: str,
        db: AsyncSession
    ) -> Session:
        # 1. Validate meeting exists
        meeting = await self._get_meeting(meeting_id, db)
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")
        
        # 2. Check for existing active session
        existing = await self.get_active_session(contact_id, db)
        if existing:
            # End existing session
            existing.status = SessionStatus.ENDED
            await db.commit()
        
        # 3. Create new session
        session = Session(
            contact_id=contact_id,
            meeting_id=meeting_id,
            dest_name=meeting.name,
            dest_lat=meeting.lat,
            dest_lng=meeting.lng,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
```

### Adding a New Endpoint (Step-by-Step)

1. **Create/Update Schema** (`app/schemas/`)
   ```python
   # app/schemas/example.py
   from pydantic import BaseModel
   
   class ExampleCreate(BaseModel):
       name: str
       value: int
   
   class ExampleResponse(BaseModel):
       id: str
       name: str
       value: int
       
       class Config:
           from_attributes = True
   ```

2. **Create/Update Model** (`app/models/`)
   ```python
   # app/models/example.py
   class Example(Base):
       __tablename__ = "examples"
       id = Column(String(36), primary_key=True)
       name = Column(String(255))
       value = Column(Integer)
   ```

3. **Create Migration**
   ```bash
   cd backend
   alembic revision -m "add_example_table"
   # Edit generated file in alembic/versions/
   alembic upgrade head
   ```

4. **Create Service** (`app/services/`)
   ```python
   # app/services/example_service.py
   class ExampleService:
       async def create(self, data, db):
           example = Example(**data.dict())
           db.add(example)
           await db.commit()
           return example
   ```

5. **Create Endpoint** (`app/api/v1/endpoints/`)
   ```python
   # app/api/v1/endpoints/examples.py
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix="/examples", tags=["examples"])
   
   @router.post("/", response_model=ExampleResponse)
   async def create_example(
       data: ExampleCreate,
       db: AsyncSession = Depends(get_db)
   ):
       service = ExampleService()
       return await service.create(data, db)
   ```

6. **Register Router** (`app/api/v1/router.py`)
   ```python
   from app.api.v1.endpoints import examples
   
   api_router.include_router(examples.router)
   ```

---

## Frontend Deep Dive

### Directory Structure Explained

```
frontend/lib/
├── main.dart                    # App entry point
│
├── app/
│   ├── app.dart                 # MaterialApp configuration
│   ├── routes.dart              # Route definitions
│   └── admin_routes.dart        # Admin route definitions
│
├── core/
│   ├── constants/
│   │   └── api_constants.dart   # API URLs, endpoints
│   │
│   ├── models/
│   │   ├── contact.dart         # Contact data model
│   │   ├── meeting.dart         # Meeting data model
│   │   └── session.dart         # Session data model
│   │
│   ├── services/
│   │   ├── api_service.dart     # HTTP client wrapper
│   │   ├── auth_service.dart    # Authentication logic
│   │   ├── storage_service.dart # Secure storage
│   │   ├── location_service.dart # GPS handling
│   │   └── error_service.dart   # Error handling
│   │
│   ├── theme/
│   │   ├── app_theme.dart       # ThemeData configuration
│   │   ├── app_colors.dart      # Color constants
│   │   └── app_text_styles.dart # Text style constants
│   │
│   └── widgets/
│       ├── error_widget.dart    # Error display widget
│       └── skeleton_loader.dart # Loading placeholder
│
├── features/
│   ├── auth/
│   │   ├── providers/
│   │   │   └── auth_provider.dart    # Auth state management
│   │   └── screens/
│   │       ├── login_screen.dart
│   │       └── registration_screen.dart
│   │
│   ├── meetings/
│   │   ├── providers/
│   │   │   └── meeting_provider.dart  # Meeting state
│   │   └── screens/
│   │       └── meeting_list_screen.dart
│   │
│   ├── sessions/
│   │   ├── providers/
│   │   │   └── session_provider.dart  # Session state
│   │   └── screens/
│   │       ├── session_screen.dart
│   │       └── session_list_screen.dart
│   │
│   └── offline/
│       └── providers/
│           └── offline_provider.dart   # Offline queue
│
└── ui/
    ├── screens/                  # All screen widgets
    │   ├── auth/
    │   ├── checkin/
    │   ├── dashboard/
    │   ├── meetings/
    │   ├── reports/
    │   └── settings/
    │
    ├── theme/                    # Theme configuration
    │
    └── widgets/                  # Reusable widgets
        ├── vc_app_bar.dart
        ├── vc_button.dart
        ├── vc_card.dart
        ├── vc_text_field.dart
        └── widgets.dart          # Barrel export
```

### State Management Pattern

We use **Provider** for state management. Here's the pattern:

```dart
// 1. Create a ChangeNotifier provider
class SessionProvider extends ChangeNotifier {
  // Private state
  List<Session> _sessions = [];
  bool _isLoading = false;
  String? _error;
  
  // Public getters
  List<Session> get sessions => _sessions;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Actions that modify state
  Future<void> loadSessions(String contactId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();  // Triggers UI rebuild
    
    try {
      final response = await ApiService.getSessions(contactId);
      _sessions = response;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();  // Triggers UI rebuild
    }
  }
}

// 2. Provide it in the widget tree (main.dart or app.dart)
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => AuthProvider()),
    ChangeNotifierProvider(create: (_) => SessionProvider()),
    ChangeNotifierProvider(create: (_) => MeetingProvider()),
  ],
  child: MyApp(),
)

// 3. Consume in widgets
class SessionListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Watch for changes
    final provider = context.watch<SessionProvider>();
    
    if (provider.isLoading) {
      return CircularProgressIndicator();
    }
    
    if (provider.error != null) {
      return Text('Error: ${provider.error}');
    }
    
    return ListView.builder(
      itemCount: provider.sessions.length,
      itemBuilder: (context, index) {
        return SessionCard(session: provider.sessions[index]);
      },
    );
  }
}
```

### API Service Pattern

```dart
// core/services/api_service.dart
class ApiService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();
  
  // HTTP client with token injection
  Future<http.Response> _get(String endpoint) async {
    final token = await StorageService.getToken();
    return http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
    );
  }
  
  // Type-safe API methods
  static Future<List<Session>> getSessions(String contactId) async {
    final response = await _instance._get('/sessions?contact_id=$contactId');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Session.fromJson(json)).toList();
    }
    throw ApiException(response.statusCode, response.body);
  }
}
```

### Adding a New Screen (Step-by-Step)

1. **Create Screen Widget**
   ```dart
   // lib/ui/screens/example/example_screen.dart
   import 'package:flutter/material.dart';
   
   class ExampleScreen extends StatefulWidget {
     const ExampleScreen({super.key});
     
     @override
     State<ExampleScreen> createState() => _ExampleScreenState();
   }
   
   class _ExampleScreenState extends State<ExampleScreen> {
     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: const Text('Example')),
         body: const Center(child: Text('Example Screen')),
       );
     }
   }
   ```

2. **Add Route**
   ```dart
   // lib/app/routes.dart
   static const String example = '/example';
   
   // In route generator:
   case Routes.example:
     return MaterialPageRoute(builder: (_) => const ExampleScreen());
   ```

3. **Navigate to Screen**
   ```dart
   Navigator.pushNamed(context, Routes.example);
   ```

---

## Database Architecture

### Current Schema (ERD)

```
┌─────────────────┐       ┌─────────────────┐
│    contacts     │       │    meetings     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ email           │       │ name            │
│ phone           │       │ address         │
│ first_name      │       │ lat             │
│ last_name       │       │ lng             │
│ password_hash   │       │ radius_meters   │
│ consent_granted │       │ is_active       │
│ ghl_contact_id  │       │ created_by      │
│ created_at      │       │ created_at      │
│ updated_at      │       │ updated_at      │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │    ┌─────────────────┐  │
         └───►│    sessions     │◄─┘
              ├─────────────────┤
              │ id (PK)         │
              │ contact_id (FK) │
              │ meeting_id (FK) │
              │ status          │
              │ dest_name       │
              │ dest_address    │
              │ dest_lat        │
              │ dest_lng        │
              │ session_notes   │
              │ is_complete     │
              │ created_at      │
              │ updated_at      │
              └────────┬────────┘
                       │
                       ▼
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

### Running Migrations

```bash
cd backend

# Create new migration
alembic revision -m "description_of_change"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# See current migration status
alembic current

# See migration history
alembic history
```

---

## Authentication & Security

### JWT Token Flow

```
1. User registers/logs in
2. Backend validates credentials
3. Backend generates JWT with:
   - sub: contact_id
   - exp: expiration timestamp (15 min default)
4. Token returned to client
5. Client stores token securely (flutter_secure_storage)
6. Client includes token in all API requests:
   Authorization: Bearer <token>
7. Backend validates token on each request
8. If expired, client must re-authenticate
```

### Password Hashing

```python
# We use bcrypt via passlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
```

---

## Code Patterns & Conventions

### Python Conventions

```python
# 1. SINGLE-LINE IMPORTS ONLY (CRITICAL!)
import uuid
import logging
from datetime import datetime

# 2. Type hints on all functions
async def get_session(session_id: str, db: AsyncSession) -> Optional[Session]:
    pass

# 3. Docstrings for public methods
async def create_session(self, contact_id: str, meeting_id: str) -> Session:
    """
    Create a new attendance session.
    
    Args:
        contact_id: The contact's UUID
        meeting_id: The meeting's UUID
    
    Returns:
        The created Session object
    
    Raises:
        ValueError: If meeting not found or inactive
    """
    pass

# 4. Logging throughout
logger = logging.getLogger(__name__)
logger.info(f"Created session {session.id}")
logger.error(f"Failed to create session: {e}")

# 5. Error handling
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Dart Conventions

```dart
// 1. Use const constructors where possible
const MyWidget({super.key});

// 2. Private fields with underscore prefix
String _privateField;

// 3. Getters for computed properties
bool get isValid => _name.isNotEmpty && _value > 0;

// 4. Async/await for asynchronous operations
Future<void> loadData() async {
  try {
    final data = await apiService.fetch();
    setState(() => _data = data);
  } catch (e) {
    setState(() => _error = e.toString());
  }
}

// 5. Named parameters for clarity
Session({
  required this.id,
  required this.contactId,
  this.notes,
});
```

---

## Common Tasks & How-Tos

### How to Add a New Environment Variable

1. **Backend**
   ```python
   # 1. Add to app/core/config.py
   class Settings:
       NEW_VAR: str = os.getenv("NEW_VAR", "default_value")
   
   # 2. Add to env.example
   NEW_VAR=your_value_here
   
   # 3. Add to actual .env file
   ```

2. **Frontend**
   ```dart
   // Use compile-time constants
   const String newVar = String.fromEnvironment('NEW_VAR', defaultValue: 'default');
   ```

### How to Debug API Issues

1. **Check backend logs**
   ```bash
   # If running locally
   uvicorn app.main:app --reload --log-level debug
   ```

2. **Use FastAPI Swagger UI**
   - Open http://localhost:8000/docs
   - Test endpoints directly
   - Check request/response schemas

3. **Check network requests in Flutter**
   ```dart
   // Add logging to ApiService
   print('Request: $method $url');
   print('Response: ${response.statusCode} ${response.body}');
   ```

### How to Reset Development Database

```bash
cd backend

# Option 1: Delete SQLite file
rm test.db

# Option 2: Rollback and reapply all migrations
alembic downgrade base
alembic upgrade head

# Restart the server to recreate tables
uvicorn app.main:app --reload
```

---

## Troubleshooting Guide

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | `poetry install` |
| `sqlalchemy.exc.OperationalError` | Database not initialized | `alembic upgrade head` |
| CORS errors in browser | CORS not configured | Check `allow_origins` in main.py |
| 401 Unauthorized | Token expired/invalid | Re-login, check token storage |
| Flutter build fails | Dependencies outdated | `flutter pub get` |
| GPS not working | Permissions not granted | Check permission_handler setup |

### Debug Checklist

1. ✅ Backend running? (`uvicorn` process active)
2. ✅ Database migrated? (`alembic upgrade head`)
3. ✅ Environment variables set? (check `.env`)
4. ✅ Token valid? (check expiration)
5. ✅ Correct API URL? (check `api_constants.dart`)
6. ✅ Network accessible? (check firewall, CORS)

---

## Next Steps for New Developers

1. **Set up local environment** - Follow `HANDOFF_SETUP_GUIDE.md`
2. **Run the application** - Get both backend and frontend running
3. **Explore the codebase** - Trace a request from UI to database
4. **Make a small change** - Add a field to an existing model
5. **Write a test** - Understand the testing patterns
6. **Review epics** - Understand upcoming work in `epics_v2_enhanced_requirements.md`

---

**Questions? Check the other handoff documents or search the codebase for similar implementations.**

