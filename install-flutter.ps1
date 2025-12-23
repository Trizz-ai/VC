# Flutter SDK Installation Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Flutter SDK Installation for Windows" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  WARNING: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may not work properly" -ForegroundColor Yellow
    Write-Host ""
}

# Define installation directory
$flutterDir = "C:\src\flutter"
$flutterBin = "$flutterDir\bin"

Write-Host "[1/5] Checking for existing Flutter installation..." -ForegroundColor Green

# Check if Flutter is already in PATH
$flutterCommand = Get-Command flutter -ErrorAction SilentlyContinue
if ($flutterCommand) {
    Write-Host "✓ Flutter already installed at: $($flutterCommand.Source)" -ForegroundColor Green
    flutter --version
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "[2/5] Downloading Flutter SDK..." -ForegroundColor Green
Write-Host "   This will download ~800MB. Please be patient..." -ForegroundColor Yellow

# Flutter SDK download URL (latest stable)
$flutterUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_stable.zip"
$flutterZip = "$env:TEMP\flutter_windows.zip"

# Download Flutter SDK
try {
    Write-Host "   Downloading from: $flutterUrl" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $flutterUrl -OutFile $flutterZip -UseBasicParsing
    Write-Host "✓ Download complete!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to download Flutter SDK" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually from:" -ForegroundColor Yellow
    Write-Host "https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "[3/5] Extracting Flutter SDK..." -ForegroundColor Green

# Create installation directory
if (-not (Test-Path "C:\src")) {
    New-Item -Path "C:\src" -ItemType Directory -Force | Out-Null
}

# Extract Flutter SDK
try {
    Write-Host "   Extracting to: $flutterDir" -ForegroundColor Cyan
    Write-Host "   This may take several minutes..." -ForegroundColor Yellow
    Expand-Archive -Path $flutterZip -DestinationPath "C:\src" -Force
    Write-Host "✓ Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to extract Flutter SDK" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Clean up zip file
Remove-Item $flutterZip -Force

Write-Host ""
Write-Host "[4/5] Adding Flutter to PATH..." -ForegroundColor Green

# Get current user PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

# Check if Flutter bin is already in PATH
if ($currentPath -notlike "*$flutterBin*") {
    try {
        # Add Flutter to user PATH
        $newPath = $currentPath + ";$flutterBin"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        
        # Also add to current session
        $env:Path += ";$flutterBin"
        
        Write-Host "✓ Flutter added to PATH!" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to add Flutter to PATH" -ForegroundColor Red
        Write-Host "  Please add manually: $flutterBin" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ Flutter already in PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/5] Running Flutter Doctor..." -ForegroundColor Green
Write-Host ""

# Refresh environment variables in current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Run flutter doctor
try {
    & "$flutterBin\flutter.bat" doctor
} catch {
    Write-Host "✗ Failed to run flutter doctor" -ForegroundColor Red
    Write-Host "  Please restart PowerShell and run: flutter doctor" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Close and reopen PowerShell" -ForegroundColor White
Write-Host "2. Run: flutter doctor" -ForegroundColor White
Write-Host "3. Accept Android licenses: flutter doctor --android-licenses" -ForegroundColor White
Write-Host "4. Navigate to your project: cd X:\VC\frontend" -ForegroundColor White
Write-Host "5. Install dependencies: flutter pub get" -ForegroundColor White
Write-Host "6. Run your app: flutter run -d chrome" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see: QUICK_START_GUIDE.md" -ForegroundColor Cyan
Write-Host ""



