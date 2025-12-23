# Find Flutter Installation Script
Write-Host "🔍 Searching for Flutter..." -ForegroundColor Cyan
Write-Host ""

# Search common locations
$searchPaths = @(
    "C:\src\flutter\bin\flutter.exe",
    "C:\flutter\bin\flutter.exe",
    "D:\flutter\bin\flutter.exe",
    "E:\flutter\bin\flutter.exe",
    "$env:USERPROFILE\flutter\bin\flutter.exe",
    "$env:LOCALAPPDATA\flutter\bin\flutter.exe",
    "C:\Program Files\flutter\bin\flutter.exe",
    "C:\Program Files (x86)\flutter\bin\flutter.exe"
)

$found = $null

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $found = $path
        break
    }
}

# If not found, search all drives
if (-not $found) {
    Write-Host "Searching all drives for flutter folder..." -ForegroundColor Yellow
    Get-PSDrive -PSProvider FileSystem | ForEach-Object {
        $drive = $_.Root
        try {
            $flutterDirs = Get-ChildItem -Path $drive -Directory -Filter "flutter" -ErrorAction SilentlyContinue -Depth 2 | Select-Object -First 1
            foreach ($fd in $flutterDirs) {
                $flutterExe = Join-Path $fd.FullName "bin\flutter.exe"
                if (Test-Path $flutterExe) {
                    $found = $flutterExe
                    break
                }
            }
        } catch {
            # Skip inaccessible drives
        }
        if ($found) { break }
    }
}

if ($found) {
    Write-Host ""
    Write-Host "✅✅✅ FLUTTER FOUND! ✅✅✅" -ForegroundColor Green
    Write-Host "Path: $found" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Testing Flutter..." -ForegroundColor Yellow
    & $found --version
    Write-Host ""
    Write-Host "🚀 Starting frontend app..." -ForegroundColor Green
    Write-Host ""
    cd "$PSScriptRoot\frontend"
    & $found pub get
    Write-Host ""
    Write-Host "Launching app in Chrome..." -ForegroundColor Cyan
    & $found run -d chrome
} else {
    Write-Host ""
    Write-Host "❌ Flutter not found automatically" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Open File Explorer" -ForegroundColor White
    Write-Host "2. Search for flutter.exe" -ForegroundColor White
    Write-Host "3. Note the full path (should be in a bin folder)" -ForegroundColor White
    Write-Host "4. Then run:" -ForegroundColor White
    Write-Host "   cd X:\VC\frontend" -ForegroundColor Cyan
    Write-Host "   C:\path\to\flutter\bin\flutter.exe pub get" -ForegroundColor Cyan
    Write-Host "   C:\path\to\flutter\bin\flutter.exe run -d chrome" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or share the path and I will start it for you" -ForegroundColor Yellow
}
