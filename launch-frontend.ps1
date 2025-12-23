# Frontend Launch Script
# Ensures we're in the correct directory before launching

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Launching Verified Compliance App" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$frontendDir = Join-Path $PSScriptRoot "frontend"
$flutterBin = "C:\flutter\bin"

# Verify we're in the project root
if (-not (Test-Path $frontendDir)) {
    Write-Host "Frontend directory not found: $frontendDir" -ForegroundColor Red
    Write-Host "  Current directory: $PWD" -ForegroundColor Yellow
    exit 1
}

# Verify pubspec.yaml exists
$pubspecPath = Join-Path $frontendDir "pubspec.yaml"
if (-not (Test-Path $pubspecPath)) {
    Write-Host "pubspec.yaml not found at: $pubspecPath" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend directory found: $frontendDir" -ForegroundColor Green
Write-Host "pubspec.yaml found" -ForegroundColor Green
Write-Host ""

# Add Flutter to PATH
if ($env:Path -notlike "*$flutterBin*") {
    $env:Path += ";$flutterBin"
    Write-Host "Flutter added to PATH" -ForegroundColor Green
}

# Verify Flutter is accessible
try {
    $flutterVersion = & flutter --version 2>&1 | Select-Object -First 1
    Write-Host "Flutter found: $flutterVersion" -ForegroundColor Green
} catch {
    Write-Host "Flutter not found in PATH" -ForegroundColor Red
    Write-Host "  Please ensure Flutter is installed at: $flutterBin" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Changing to frontend directory..." -ForegroundColor Cyan
Set-Location $frontendDir

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Verify we're in the right place
if (-not (Test-Path "pubspec.yaml")) {
    Write-Host "ERROR: pubspec.yaml not found in current directory!" -ForegroundColor Red
    Write-Host "  Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "Confirmed: pubspec.yaml exists in current directory" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Flutter app..." -ForegroundColor Cyan
Write-Host "  This will open Chrome automatically when build completes" -ForegroundColor Yellow
Write-Host "  First build takes 2-5 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Launch Flutter
flutter run -d chrome
