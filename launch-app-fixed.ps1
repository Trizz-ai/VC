# Verified Compliance - App Launcher
Write-Host "========================================"
Write-Host "  VERIFIED COMPLIANCE - APP LAUNCH"
Write-Host "========================================"
Write-Host ""

# Add Flutter to PATH
$env:Path = "C:\flutter\bin;" + $env:Path

Write-Host "[1/3] Starting Backend Server..."
Write-Host ""

# Start backend in background
$backendJob = Start-Job -ScriptBlock {
    Set-Location "X:\VC\backend"
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

Write-Host "✓ Backend starting on http://localhost:8000"
Write-Host ""

# Wait for backend to initialize
Start-Sleep -Seconds 3

Write-Host "[2/3] Starting Frontend..."
Write-Host ""

# Start frontend in background
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "X:\VC\frontend"
    $env:Path = "C:\flutter\bin;" + $env:Path
    flutter run -d chrome --web-port=3000
}

Write-Host "✓ Frontend compiling and starting on http://localhost:3000"
Write-Host ""

Write-Host "[3/3] Services Status"
Write-Host "========================================"
Write-Host "Backend:  http://localhost:8000"
Write-Host "API Docs: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000 (compiling...)"
Write-Host "========================================"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services"
Write-Host ""

# Keep script running and monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if jobs are still running
        if ($backendJob.State -ne "Running") {
            Write-Host "⚠ Backend stopped!"
        }
        if ($frontendJob.State -ne "Running") {
            Write-Host "⚠ Frontend stopped!"
        }
    }
}
finally {
    Write-Host ""
    Write-Host "Stopping services..."
    Stop-Job $backendJob, $frontendJob
    Remove-Job $backendJob, $frontendJob
    Write-Host "✓ Services stopped"
}



