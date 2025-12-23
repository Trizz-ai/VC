# Generate Screenshots of All App Screens
# This script generates screenshots of all Flutter screens without running the app

Write-Host "Automated Screenshot Generator" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Flutter is available
$flutterPath = $null
$commonFlutterPaths = @(
    "C:\flutter\bin\flutter.bat",
    "C:\flutter\bin\flutter.exe",
    "C:\src\flutter\bin\flutter.bat",
    "C:\src\flutter\bin\flutter.exe",
    "$env:USERPROFILE\flutter\bin\flutter.bat",
    "$env:USERPROFILE\flutter\bin\flutter.exe",
    "$env:LOCALAPPDATA\flutter\bin\flutter.bat",
    "$env:LOCALAPPDATA\flutter\bin\flutter.exe"
)

foreach ($path in $commonFlutterPaths) {
    if (Test-Path $path) {
        $flutterPath = $path
        break
    }
}

if (-not $flutterPath) {
    # Try to find in PATH
    $flutterInPath = Get-Command flutter -ErrorAction SilentlyContinue
    if ($flutterInPath) {
        $flutterPath = $flutterInPath.Source
    }
}

if (-not $flutterPath) {
    Write-Host "[ERROR] Flutter not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Flutter or run the find-flutter.ps1 script first." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[OK] Flutter found at: $flutterPath" -ForegroundColor Green
Write-Host ""

# Navigate to frontend directory
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Host "[ERROR] Frontend directory not found at: $frontendPath" -ForegroundColor Red
    exit 1
}

Set-Location $frontendPath
Write-Host "[INFO] Working directory: $frontendPath" -ForegroundColor Cyan
Write-Host ""

# Create screenshots output directory
$screenshotsDir = Join-Path $PSScriptRoot "screenshots"
if (-not (Test-Path $screenshotsDir)) {
    New-Item -Path $screenshotsDir -ItemType Directory | Out-Null
    Write-Host "[OK] Created screenshots directory: $screenshotsDir" -ForegroundColor Green
} else {
    Write-Host "[INFO] Using existing screenshots directory: $screenshotsDir" -ForegroundColor Green
}
Write-Host ""

# Create test goldens directory
$goldensDir = Join-Path $frontendPath "test\screenshot_tests\goldens"
if (-not (Test-Path $goldensDir)) {
    New-Item -Path $goldensDir -ItemType Directory -Force | Out-Null
}

Write-Host "[STEP 1/4] Installing Flutter dependencies..." -ForegroundColor Cyan
& $flutterPath pub get
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "[STEP 2/4] Generating screenshots (this may take a few minutes)..." -ForegroundColor Cyan
Write-Host "            This will create golden file screenshots for all screens..." -ForegroundColor Gray
Write-Host ""

# Run the screenshot tests with update-goldens flag
& $flutterPath test test\screenshot_tests\screen_screenshots_test.dart --update-goldens

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Some tests failed, but golden files may have been generated" -ForegroundColor Yellow
    Write-Host "          This is normal if screens have missing dependencies" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "[OK] Screenshot tests completed successfully!" -ForegroundColor Green
}
Write-Host ""

# Copy golden files to screenshots directory with better naming
Write-Host "[STEP 3/4] Organizing screenshots..." -ForegroundColor Cyan
$goldenFiles = Get-ChildItem -Path $goldensDir -Filter "*.png" -ErrorAction SilentlyContinue

if ($goldenFiles) {
    $count = 0
    foreach ($file in $goldenFiles) {
        $newName = $file.Name
        $destination = Join-Path $screenshotsDir $newName
        Copy-Item -Path $file.FullName -Destination $destination -Force
        $count++
        Write-Host "            [OK] $newName" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "[OK] Copied $count screenshot(s) to screenshots directory" -ForegroundColor Green
} else {
    Write-Host "[WARNING] No golden files found. The tests may not have run correctly." -ForegroundColor Yellow
    Write-Host "          Check test output above for errors." -ForegroundColor Gray
}
Write-Host ""

# Create an index HTML file to view all screenshots
Write-Host "[STEP 4/4] Creating screenshot viewer..." -ForegroundColor Cyan

$htmlContent = @'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verified Compliance - App Screenshots</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 1rem;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 3rem;
            font-size: 1.1rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
        }
        .screenshot-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .screenshot-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
        .screenshot-card img {
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
        }
        .screenshot-card .title {
            padding: 1rem;
            font-weight: 600;
            color: #333;
            text-align: center;
            background: #f8f9fa;
            border-top: 2px solid #667eea;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            padding: 2rem;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }
        .modal img {
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
            border-radius: 8px;
        }
        .modal .close {
            position: absolute;
            top: 2rem;
            right: 2rem;
            font-size: 2rem;
            color: white;
            cursor: pointer;
            background: rgba(255,255,255,0.2);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.3s ease;
        }
        .modal .close:hover { background: rgba(255,255,255,0.3); }
        .stats {
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .stats strong { font-size: 1.5rem; color: #ffd700; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Verified Compliance App Screenshots</h1>
        <p class="subtitle">All app screens captured automatically</p>
        <div class="grid" id="grid"></div>
    </div>
    <div class="modal" id="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <img src="" alt="Full size" id="modal-img">
    </div>
    <script>
        const screenshots = [
            'onboarding_screen.png',
            'login_screen.png',
            'registration_screen.png',
            'dashboard_screen.png',
            'session_list_screen.png',
            'session_screen.png',
            'meeting_list_screen.png',
            'meeting_detail_screen.png',
            'settings_screen.png',
            'profile_edit_screen.png',
            'offline_queue_screen.png',
            'admin_dashboard_screen.png',
            'admin_user_management_screen.png',
            'admin_users_screen.png'
        ];
        
        const grid = document.getElementById('grid');
        let found = 0;
        
        screenshots.forEach(file => {
            const img = new Image();
            img.onload = function() {
                found++;
                const name = file.replace('.png', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                const card = document.createElement('div');
                card.className = 'screenshot-card';
                card.innerHTML = '<img src="' + file + '" alt="' + name + '" onclick="openModal(this.src)"><div class="title">' + name + '</div>';
                grid.appendChild(card);
                
                if (found === 1) {
                    const stats = document.createElement('div');
                    stats.className = 'stats';
                    stats.innerHTML = '<strong>' + screenshots.length + '</strong> screens captured';
                    grid.parentElement.insertBefore(stats, grid);
                }
            };
            img.src = file;
        });
        
        function openModal(src) {
            document.getElementById('modal').classList.add('active');
            document.getElementById('modal-img').src = src;
        }
        
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });
    </script>
</body>
</html>
'@

$indexPath = Join-Path $screenshotsDir "index.html"
$htmlContent | Out-File -FilePath $indexPath -Encoding UTF8
Write-Host "[OK] Created screenshot viewer at: $indexPath" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SCREENSHOT GENERATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Screenshots saved to: $screenshotsDir" -ForegroundColor White
Write-Host ""
Write-Host "To view all screenshots:" -ForegroundColor Cyan
Write-Host "  1. Open: $indexPath" -ForegroundColor White
Write-Host "  2. Or run: Start-Process '$indexPath'" -ForegroundColor White
Write-Host ""

# Ask if user wants to open the viewer
$response = Read-Host "Would you like to open the screenshot viewer now? (Y/n)"
if ($response -eq '' -or $response -match '^[Yy]') {
    Start-Process $indexPath
    Write-Host "Opening screenshot viewer in your browser..." -ForegroundColor Green
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
