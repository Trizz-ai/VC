# Verified Compliance™ — Local Development Setup Guide

## Complete Step-by-Step Instructions

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

| Software | Version | Download Link | Verify Command |
|----------|---------|---------------|----------------|
| Python | 3.11+ | https://python.org | `python --version` |
| Flutter | 3.16+ | https://flutter.dev | `flutter --version` |
| Git | Latest | https://git-scm.com | `git --version` |
| VS Code | Latest | https://code.visualstudio.com | - |

### Recommended VS Code Extensions

- Python (Microsoft)
- Dart (Dart Code)
- Flutter (Dart Code)
- SQLite Viewer
- GitLens

---

## Step 1: Clone the Repository

```bash
# Navigate to your projects directory
cd C:\Projects  # or wherever you keep code

# Clone the repository
git clone <repository-url> VC
cd VC

# Verify structure
dir  # Windows
ls   # Mac/Linux
# Should see: backend/, frontend/, *.md files
```

---

## Step 2: Backend Setup

### 2.1 Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
.\venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### 2.2 Install Dependencies

```bash
# Install Poetry (package manager)
pip install poetry

# Install project dependencies
poetry install

# Alternative: use pip directly
pip install -r requirements.txt  # if requirements.txt exists
```

### 2.3 Configure Environment Variables

```bash
# Copy example environment file
copy env.example .env  # Windows
cp env.example .env    # Mac/Linux

# Edit .env file with your values
notepad .env  # Windows
nano .env     # Mac/Linux
```

**Required Environment Variables:**

```ini
# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./test.db

# For PostgreSQL (production):
# DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GoHighLevel (optional for local dev)
GHL_API_KEY=your-ghl-api-key
GHL_LOCATION_ID=your-location-id

# Google Maps (optional for local dev)
GOOGLE_MAPS_API_KEY=your-google-maps-key

# CORS (for local development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 2.4 Initialize Database

```bash
# Make sure you're in backend/ directory
cd backend

# Run database migrations
alembic upgrade head

# Verify database created
dir test.db  # Windows - should exist
ls test.db   # Mac/Linux
```

### 2.5 Start Backend Server

```bash
# Start development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Started reloader process
```

### 2.6 Verify Backend is Running

Open browser to: **http://localhost:8000/docs**

You should see the Swagger UI with all API endpoints listed.

**Test the health endpoint:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

---

## Step 3: Frontend Setup

### 3.1 Install Flutter Dependencies

```bash
# Open new terminal (keep backend running)
cd frontend

# Get Flutter dependencies
flutter pub get

# Verify Flutter setup
flutter doctor
# Fix any issues shown
```

### 3.2 Configure API URL

```dart
// Edit: frontend/lib/core/constants/api_constants.dart
class ApiConstants {
  // For local development:
  static const String baseUrl = 'http://localhost:8000';
  
  // For Android emulator use:
  // static const String baseUrl = 'http://10.0.2.2:8000';
  
  // For iOS simulator:
  // static const String baseUrl = 'http://localhost:8000';
}
```

### 3.3 Run Flutter App

**Option A: Run in Chrome (Web)**
```bash
flutter run -d chrome
```

**Option B: Run on Android Emulator**
```bash
# List available devices
flutter devices

# Run on specific device
flutter run -d <device-id>
```

**Option C: Run on iOS Simulator (Mac only)**
```bash
# Open iOS Simulator first
open -a Simulator

# Run Flutter
flutter run -d <simulator-name>
```

### 3.4 Verify Frontend is Working

1. App should launch in browser/emulator
2. You should see the login/registration screen
3. Try registering a new account
4. Check backend logs for API requests

---

## Step 4: Create Test Data

### 4.1 Create Admin User

```bash
cd backend
python create_admin_user.py
# Follow prompts to create admin account
```

### 4.2 Create Sample Meetings

```bash
cd backend
python create_fake_meetings.py
# Creates 10 sample meetings near default location
```

### 4.3 Verify Test Data

```bash
# Check meetings in database
python check_meetings.py
# Should list all created meetings
```

---

## Step 5: Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_session_service.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
# View report: open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
flutter test

# Run specific test file
flutter test test/widget_test.dart

# Run with coverage
flutter test --coverage
```

---

## Common Development Tasks

### Task: Make a Backend Code Change

1. Edit code in `backend/app/`
2. Uvicorn auto-reloads (if using `--reload`)
3. Test via Swagger UI or API client
4. Write/update tests
5. Run `pytest` to verify

### Task: Make a Frontend Code Change

1. Edit code in `frontend/lib/`
2. Hot reload automatically applies (press `r` in terminal if not)
3. Test in app
4. Write/update tests
5. Run `flutter test` to verify

### Task: Create a Database Migration

```bash
cd backend

# Create new migration
alembic revision -m "description_of_change"

# Edit the generated file in alembic/versions/
notepad alembic/versions/xxx_description.py

# Apply migration
alembic upgrade head

# Verify
alembic current
```

### Task: Reset Development Database

```bash
cd backend

# Delete SQLite database
del test.db  # Windows
rm test.db   # Mac/Linux

# Recreate all tables
alembic upgrade head

# Recreate test data
python create_fake_meetings.py
```

---

## Troubleshooting

### Issue: "Module not found" errors

```bash
# Ensure virtual environment is activated
# Windows:
.\venv\Scripts\activate

# Reinstall dependencies
poetry install
# or
pip install -e .
```

### Issue: Database errors

```bash
# Reset database
del test.db
alembic upgrade head
```

### Issue: CORS errors in browser

Check `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Flutter build errors

```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

### Issue: Android emulator can't reach backend

Use `10.0.2.2` instead of `localhost`:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

### Issue: Port 8000 already in use

```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
taskkill /PID <pid> /F

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

## Development Workflow

### Recommended Daily Workflow

1. **Start Backend**
   ```bash
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Start Frontend** (new terminal)
   ```bash
   cd frontend
   flutter run -d chrome
   ```

3. **Make Changes**
   - Edit code
   - Test manually
   - Write tests
   - Commit frequently

4. **Before Committing**
   ```bash
   # Backend
   pytest
   
   # Frontend
   flutter test
   flutter analyze
   ```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: description of change"

# Push to remote
git push origin feature/my-feature

# Create PR for review
```

---

## Quick Reference Commands

### Backend

| Task | Command |
|------|---------|
| Start server | `uvicorn app.main:app --reload` |
| Run tests | `pytest` |
| Run migrations | `alembic upgrade head` |
| Create migration | `alembic revision -m "name"` |
| Check migration status | `alembic current` |
| Format code | `black app/` |
| Lint code | `ruff check app/` |

### Frontend

| Task | Command |
|------|---------|
| Run app (Chrome) | `flutter run -d chrome` |
| Run app (any) | `flutter run` |
| Run tests | `flutter test` |
| Get dependencies | `flutter pub get` |
| Clean build | `flutter clean` |
| Analyze code | `flutter analyze` |
| Format code | `dart format lib/` |

---

## Next Steps

After completing setup:

1. ✅ Read `HANDOFF_TECHNICAL.md` for architecture details
2. ✅ Review `epics_v2_enhanced_requirements.md` for upcoming work
3. ✅ Explore the codebase - trace a check-in flow
4. ✅ Make a small change to verify your setup works
5. ✅ Run the test suites to ensure everything passes

---

**Setup complete! You're ready to start development.**

