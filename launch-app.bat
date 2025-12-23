@echo off
echo Starting Verified Compliance App...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Flutter App...
cd frontend
flutter pub get
flutter run

pause
