#!/bin/bash

echo "🚀 Starting Verified Compliance App..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start backend in background
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt || poetry install
    touch venv/.installed
fi

# Start backend server in background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}Backend server started (PID: $BACKEND_PID)${NC}"
echo "Backend available at: http://localhost:8000"
echo "API Docs at: http://localhost:8000/docs"
echo ""

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting Flutter App...${NC}"
cd ../frontend

# Install Flutter dependencies
flutter pub get

# Run Flutter app
echo -e "${GREEN}Launching Flutter app...${NC}"
flutter run

# Cleanup: kill backend when script exits
trap "kill $BACKEND_PID 2>/dev/null" EXIT
