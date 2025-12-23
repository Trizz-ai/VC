#!/bin/bash

echo "========================================"
echo "  VERIFIED COMPLIANCE - FULL APP LAUNCH"
echo "========================================"
echo ""

echo "[1/4] Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.11+"
    exit 1
fi
echo "✓ Python found"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo "WARNING: Poetry not found! Trying pip instead..."
    USE_POETRY=0
else
    echo "✓ Poetry found"
    USE_POETRY=1
fi

# Check Flutter
if ! command -v flutter &> /dev/null; then
    echo "ERROR: Flutter not found! Please install Flutter SDK"
    exit 1
fi
echo "✓ Flutter found"

echo ""
echo "[2/4] Setting up backend..."
echo ""

cd backend || exit 1

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=*
EOF
    echo "✓ Created .env file"
fi

# Install backend dependencies
if [ $USE_POETRY -eq 1 ]; then
    echo "Installing backend dependencies with Poetry..."
    poetry install --no-interaction
else
    echo "Installing backend dependencies with pip..."
    pip3 install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings python-jose passlib python-multipart httpx geopy sendgrid
fi

cd ..

echo ""
echo "[3/4] Setting up frontend..."
echo ""

cd frontend || exit 1

echo "Installing frontend dependencies..."
flutter pub get

cd ..

echo ""
echo "[4/4] Starting services..."
echo ""

# Start backend in background
echo "Starting Backend Server on http://localhost:8000..."
if [ $USE_POETRY -eq 1 ]; then
    cd backend && poetry run python -m app.main > ../backend.log 2>&1 &
else
    cd backend && python3 -m app.main > ../backend.log 2>&1 &
fi
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend App..."
cd frontend || exit 1
flutter run -d chrome &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  ✅ APP LAUNCHED!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: Running in Chrome"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait



