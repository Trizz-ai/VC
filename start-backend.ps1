# Backend Startup Script
# Starts the Verified Compliance backend server

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Verified Compliance Backend Server" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$backendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendDir)) {
    Write-Host "✗ Backend directory not found: $backendDir" -ForegroundColor Red
    exit 1
}

Set-Location $backendDir

Write-Host "[1/3] Checking Python..." -ForegroundColor Green

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/3] Checking dependencies..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    Write-Host "  Activating..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  No virtual environment found" -ForegroundColor Yellow
    Write-Host "  Installing dependencies globally..." -ForegroundColor Cyan
    
    # Install required packages
    $packages = @(
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic-settings",
        "python-jose",
        "passlib",
        "python-multipart",
        "httpx",
        "geopy"
    )
    
    foreach ($package in $packages) {
        Write-Host "  Installing $package..." -ForegroundColor Cyan
        pip install $package -q
    }
    
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Starting Backend Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs  (API Documentation)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Start the backend server
try {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host ""
    Write-Host "✗ Failed to start backend server" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}



