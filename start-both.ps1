# Launcher script to start both backend and frontend in separate windows

Write-Host "Starting Backend and Frontend..." -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Start Backend in new window
Write-Host "Opening Backend window..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", "cd '$scriptPath'; Write-Host 'Backend Window' -ForegroundColor Green; .\START_BACKEND_SIMPLE.ps1"
)

# Wait a moment
Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "Opening Frontend window..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", "cd '$scriptPath'; Write-Host 'Frontend Window' -ForegroundColor Green; .\launch-frontend.ps1"
)

Write-Host ""
Write-Host "Both windows should now be open!" -ForegroundColor Green
Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend: Will open in Chrome when ready" -ForegroundColor Yellow



