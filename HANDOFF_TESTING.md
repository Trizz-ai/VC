# Verified Compliance™ — Testing Guide

## Testing Strategy & Implementation

---

## Testing Philosophy

### Core Principles

1. **NO MOCKS** - All tests use real implementations with real data
2. **Real Database** - Tests run against actual SQLite/PostgreSQL
3. **Integration Focus** - Test complete flows, not just units
4. **Deterministic** - Tests produce same results every run

### Test Pyramid

```
         ╱╲
        ╱  ╲         E2E Tests (Few, Critical paths)
       ╱────╲
      ╱      ╲       Integration Tests (Moderate)
     ╱────────╲
    ╱          ╲     Unit Tests (Many, Fast)
   ╱────────────╲
```

---

## Backend Testing

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_api_integration.py  # API endpoint tests
├── test_core_auth.py        # Auth tests
├── test_core_config.py      # Config tests
├── test_core_database.py    # Database tests
├── test_models_contact.py   # Contact model tests
├── test_models_meeting.py   # Meeting model tests
├── test_models_session.py   # Session model tests
├── test_services_*.py       # Service tests
└── test_integration_e2e.py  # End-to-end tests
```

### Running Tests

```bash
cd backend

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_session_service.py -v

# Run specific test function
pytest tests/test_session_service.py::test_create_session -v

# Run with coverage report
pytest --cov=app --cov-report=html
# View: open htmlcov/index.html

# Run with print output visible
pytest -v -s

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_check"
```

### Test Fixtures (conftest.py)

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models import Contact, Meeting, Session

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="function")
async def db_session():
    """Create fresh database for each test"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def sample_contact(db_session):
    """Create sample contact for testing"""
    contact = Contact(
        email="test@example.com",
        phone="+15305551212",
        first_name="Test",
        last_name="User",
        consent_granted=True,
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)
    return contact

@pytest.fixture
async def sample_meeting(db_session):
    """Create sample meeting for testing"""
    meeting = Meeting(
        name="Test Meeting",
        address="123 Test St",
        lat=38.5816,
        lng=-121.4944,
        radius_meters=100,
        is_active=True,
    )
    db_session.add(meeting)
    await db_session.commit()
    await db_session.refresh(meeting)
    return meeting
```

### Example Tests

#### Model Test

```python
# backend/tests/test_models_contact.py
import pytest
from app.models.contact import Contact

@pytest.mark.asyncio
async def test_contact_creation(db_session):
    """Test creating a contact"""
    contact = Contact(
        email="newuser@example.com",
        first_name="New",
        last_name="User",
        consent_granted=True,
    )
    db_session.add(contact)
    await db_session.commit()
    
    assert contact.id is not None
    assert contact.email == "newuser@example.com"
    assert contact.is_active == True  # Default value

@pytest.mark.asyncio
async def test_contact_full_name(db_session):
    """Test full_name property"""
    contact = Contact(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
    )
    
    assert contact.full_name == "John Doe"

@pytest.mark.asyncio
async def test_contact_password(db_session):
    """Test password hashing"""
    contact = Contact(email="test@example.com")
    contact.set_password("securepassword123")
    
    assert contact.password_hash is not None
    assert contact.check_password("securepassword123") == True
    assert contact.check_password("wrongpassword") == False
```

#### Service Test

```python
# backend/tests/test_session_service.py
import pytest
from app.services.session_service import SessionService
from app.services.location_service import LocationData

@pytest.mark.asyncio
async def test_create_session(db_session, sample_contact, sample_meeting):
    """Test creating a session"""
    service = SessionService()
    
    session = await service.create_session(
        contact_id=sample_contact.id,
        meeting_id=sample_meeting.id,
        db=db_session
    )
    
    assert session is not None
    assert session.contact_id == sample_contact.id
    assert session.meeting_id == sample_meeting.id
    assert session.status == "active"
    assert session.dest_name == sample_meeting.name

@pytest.mark.asyncio
async def test_check_in_within_range(db_session, sample_contact, sample_meeting):
    """Test check-in when within range"""
    service = SessionService()
    
    # Create session
    session = await service.create_session(
        contact_id=sample_contact.id,
        meeting_id=sample_meeting.id,
        db=db_session
    )
    
    # Check in with location close to meeting
    location = LocationData(
        latitude=38.5816,  # Same as meeting
        longitude=-121.4944,
        accuracy=10.0
    )
    
    event = await service.check_in(
        session_id=session.id,
        location_data=location,
        db=db_session
    )
    
    assert event is not None
    assert event.type.value == "check_in"
    
    # Verify session status updated
    await db_session.refresh(session)
    assert session.status == "checked_in"

@pytest.mark.asyncio
async def test_check_in_outside_range(db_session, sample_contact, sample_meeting):
    """Test check-in when outside range"""
    service = SessionService()
    
    # Create session
    session = await service.create_session(
        contact_id=sample_contact.id,
        meeting_id=sample_meeting.id,
        db=db_session
    )
    
    # Check in with location far from meeting
    location = LocationData(
        latitude=39.0,  # Far away
        longitude=-122.0,
        accuracy=10.0
    )
    
    event = await service.check_in(
        session_id=session.id,
        location_data=location,
        db=db_session
    )
    
    # Should fail - returns None
    assert event is None
```

#### API Test

```python
# backend/tests/test_api_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_register_new_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
                "consent_granted": True,
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

@pytest.mark.asyncio
async def test_login(sample_contact):
    """Test user login"""
    # First set password
    sample_contact.set_password("testpassword")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Expected output:
# Name                              Stmts   Miss  Cover
# -----------------------------------------------------
# app/__init__.py                       0      0   100%
# app/main.py                          45      5    89%
# app/models/contact.py                68      3    96%
# app/services/session_service.py     124     12    90%
# -----------------------------------------------------
# TOTAL                              1247    125    90%
```

---

## Frontend Testing

### Test Structure

```
frontend/test/
├── unit_test_helper.dart    # Test utilities
├── widget_test.dart         # Basic widget tests
├── integration_test.dart    # Integration tests
└── screenshot_tests/
    └── screen_screenshots_test.dart
```

### Running Tests

```bash
cd frontend

# Run all tests
flutter test

# Run specific test file
flutter test test/widget_test.dart

# Run with coverage
flutter test --coverage

# Generate coverage report (requires lcov)
genhtml coverage/lcov.info -o coverage/html
# View: open coverage/html/index.html

# Run integration tests
flutter test integration_test/
```

### Example Tests

#### Widget Test

```dart
// test/widgets/vc_button_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:verified_compliance/ui/widgets/vc_button.dart';

void main() {
  group('VCButton', () {
    testWidgets('renders with label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VCButton(
              label: 'Test Button',
              onPressed: () {},
            ),
          ),
        ),
      );
      
      expect(find.text('Test Button'), findsOneWidget);
    });
    
    testWidgets('calls onPressed when tapped', (tester) async {
      bool pressed = false;
      
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VCButton(
              label: 'Tap Me',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );
      
      await tester.tap(find.text('Tap Me'));
      await tester.pump();
      
      expect(pressed, true);
    });
    
    testWidgets('shows loading indicator when loading', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VCButton(
              label: 'Loading',
              onPressed: () {},
              isLoading: true,
            ),
          ),
        ),
      );
      
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
```

#### Provider Test

```dart
// test/providers/session_provider_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:verified_compliance/features/sessions/providers/session_provider.dart';

void main() {
  group('SessionProvider', () {
    late SessionProvider provider;
    
    setUp(() {
      provider = SessionProvider();
    });
    
    test('initial state', () {
      expect(provider.sessions, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.error, isNull);
    });
    
    test('setLoading updates state', () {
      provider.setLoading(true);
      expect(provider.isLoading, true);
    });
    
    // Note: API tests should use real backend
    // or integration tests against test server
  });
}
```

#### Integration Test

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:verified_compliance/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  group('end-to-end test', () {
    testWidgets('complete login flow', (tester) async {
      app.main();
      await tester.pumpAndSettle();
      
      // Find login button
      expect(find.text('Login'), findsOneWidget);
      
      // Enter credentials
      await tester.enterText(
        find.byKey(Key('email_field')),
        'test@example.com',
      );
      await tester.enterText(
        find.byKey(Key('password_field')),
        'password123',
      );
      
      // Tap login
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle();
      
      // Should navigate to dashboard
      expect(find.text('Dashboard'), findsOneWidget);
    });
  });
}
```

### Golden Tests (Screenshot Comparison)

```dart
// test/screenshot_tests/screen_screenshots_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:verified_compliance/ui/screens/dashboard/dashboard_screen.dart';

void main() {
  testWidgets('DashboardScreen matches golden', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: DashboardScreen(),
      ),
    );
    
    await expectLater(
      find.byType(DashboardScreen),
      matchesGoldenFile('goldens/dashboard_screen.png'),
    );
  });
}

// Run with:
// flutter test --update-goldens test/screenshot_tests/
```

---

## Testing Best Practices

### DO:

✅ **Use real database connections**
```python
# Good - real database
async with AsyncSessionLocal() as session:
    result = await service.get_sessions(contact_id, session)
```

✅ **Test complete flows**
```python
# Good - full flow
session = await service.create_session(...)
event = await service.check_in(...)
await service.check_out(...)
```

✅ **Use fixtures for setup**
```python
# Good - reusable fixture
@pytest.fixture
async def sample_contact(db_session):
    contact = Contact(...)
    db_session.add(contact)
    await db_session.commit()
    return contact
```

✅ **Test edge cases**
```python
# Good - test invalid input
async def test_check_in_invalid_location():
    # Test behavior when location is outside range
```

### DON'T:

❌ **No mocks**
```python
# Bad - mock
mock_db = MagicMock()
mock_db.execute.return_value = []
```

❌ **No hardcoded data**
```python
# Bad - hardcoded response
def test_get_sessions():
    return [{"id": "fake-id"}]  # Never do this
```

❌ **No skipping tests**
```python
# Bad - skipping
@pytest.mark.skip
def test_important_feature():
    pass
```

---

## Test Data Management

### Creating Test Data

```python
# backend/scripts/generate_test_data.py
async def create_test_data():
    """Generate test data for development"""
    async with AsyncSessionLocal() as db:
        # Create contacts
        for i in range(10):
            contact = Contact(
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                consent_granted=True,
            )
            db.add(contact)
        
        # Create meetings
        for i in range(5):
            meeting = Meeting(
                name=f"Test Meeting {i}",
                address=f"{100+i} Main St",
                lat=38.5816 + (i * 0.01),
                lng=-121.4944 + (i * 0.01),
            )
            db.add(meeting)
        
        await db.commit()
```

### Cleaning Test Data

```python
# In conftest.py - automatic cleanup
@pytest.fixture(scope="function")
async def db_session():
    # ... setup ...
    yield session
    # Cleanup happens here
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

---

## CI/CD Testing

### GitHub Actions Test Job

```yaml
test:
  runs-on: ubuntu-latest
  
  services:
    postgres:
      image: postgres:15
      env:
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: test_db
      ports:
        - 5432:5432
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
      run: |
        poetry run pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## Debugging Failing Tests

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `asyncio.TimeoutError` | Slow test | Increase timeout or optimize |
| `IntegrityError` | Duplicate data | Clear database between tests |
| `AttributeError: NoneType` | Missing fixture | Check fixture dependencies |
| `AssertionError` | Wrong expectation | Review test logic |

### Debug Commands

```bash
# Run with verbose output
pytest -v -s

# Run single test with debug
pytest tests/test_session_service.py::test_check_in -v -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

---

## Test Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| Models | >90% | ~85% |
| Services | >80% | ~75% |
| API Endpoints | >80% | ~70% |
| **Overall** | **>80%** | **~75%** |

### Improving Coverage

1. Identify uncovered lines: `pytest --cov-report=term-missing`
2. Focus on critical paths first
3. Add edge case tests
4. Test error handling paths

---

**For more testing resources, see the pytest and Flutter testing documentation.**

