@echo off
echo ========================================
echo   VERIFIED COMPLIANCE - FULL APP LAUNCH
echo ========================================
echo.

echo [1/4] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)
echo ✓ Python found

REM Check Poetry
poetry --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Poetry not found! Trying pip instead...
    set USE_POETRY=0
) else (
    echo ✓ Poetry found
    set USE_POETRY=1
)

REM Check Flutter
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flutter not found! Please install Flutter SDK
    pause
    exit /b 1
)
echo ✓ Flutter found

echo.
echo [2/4] Setting up backend...
echo.

cd backend

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    (
        echo ENVIRONMENT=development
        echo DEBUG=true
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo DATABASE_URL=sqlite:///./test.db
        echo REDIS_URL=redis://localhost:6379/0
        echo CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
        echo ALLOWED_HOSTS=*
    ) > .env
    echo ✓ Created .env file
)

REM Install backend dependencies if needed
if %USE_POETRY%==1 (
    echo Installing backend dependencies with Poetry...
    poetry install --no-interaction
) else (
    echo Installing backend dependencies with pip...
    pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings python-jose passlib python-multipart httpx geopy sendgrid
)

cd ..

echo.
echo [3/4] Setting up frontend...
echo.

cd frontend

echo Installing frontend dependencies...
flutter pub get

cd ..

echo.
echo [4/4] Starting services...
echo.

REM Start backend in new window
echo Starting Backend Server on http://localhost:8000...
start "Verified Compliance Backend" cmd /k "cd backend && if %USE_POETRY%==1 (poetry run python -m app.main) else (python -m app.main)"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend App...
start "Verified Compliance Frontend" cmd /k "cd frontend && flutter run -d chrome"

echo.
echo ========================================
echo   ✅ APP LAUNCHED!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: Running in Chrome
echo.
echo Both services are running in separate windows.
echo Close the windows to stop the services.
echo.
pause



