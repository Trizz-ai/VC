#!/bin/bash
# Generate Screenshots of All App Screens
# This script generates screenshots of all Flutter screens without running the app

echo "🎨 Automated Screenshot Generator"
echo "================================="
echo ""

# Check if Flutter is available
FLUTTER_PATH=""
COMMON_FLUTTER_PATHS=(
    "$HOME/flutter/bin/flutter"
    "/usr/local/flutter/bin/flutter"
    "/opt/flutter/bin/flutter"
)

for path in "${COMMON_FLUTTER_PATHS[@]}"; do
    if [ -f "$path" ]; then
        FLUTTER_PATH="$path"
        break
    fi
done

if [ -z "$FLUTTER_PATH" ]; then
    # Try to find in PATH
    if command -v flutter &> /dev/null; then
        FLUTTER_PATH=$(which flutter)
    fi
fi

if [ -z "$FLUTTER_PATH" ]; then
    echo "❌ Flutter not found!"
    echo ""
    echo "Please install Flutter first."
    echo "Visit: https://docs.flutter.dev/get-started/install"
    echo ""
    exit 1
fi

echo "✅ Flutter found at: $FLUTTER_PATH"
echo ""

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_PATH="$SCRIPT_DIR/frontend"

if [ ! -d "$FRONTEND_PATH" ]; then
    echo "❌ Frontend directory not found at: $FRONTEND_PATH"
    exit 1
fi

cd "$FRONTEND_PATH"
echo "📁 Working directory: $FRONTEND_PATH"
echo ""

# Create screenshots output directory
SCREENSHOTS_DIR="$SCRIPT_DIR/screenshots"
if [ ! -d "$SCREENSHOTS_DIR" ]; then
    mkdir -p "$SCREENSHOTS_DIR"
    echo "📁 Created screenshots directory: $SCREENSHOTS_DIR"
else
    echo "📁 Using existing screenshots directory: $SCREENSHOTS_DIR"
fi
echo ""

# Create test goldens directory
GOLDENS_DIR="$FRONTEND_PATH/test/screenshot_tests/goldens"
mkdir -p "$GOLDENS_DIR"

echo "🔄 Step 1: Installing Flutter dependencies..."
$FLUTTER_PATH pub get
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

echo "📸 Step 2: Generating screenshots (this may take a few minutes)..."
echo "   This will create golden file screenshots for all screens..."
echo ""

# Run the screenshot tests with update-goldens flag
$FLUTTER_PATH test test/screenshot_tests/screen_screenshots_test.dart --update-goldens

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some tests failed, but golden files may have been generated"
    echo "    This is normal if screens have missing dependencies"
else
    echo ""
    echo "✅ Screenshot tests completed successfully!"
fi
echo ""

# Copy golden files to screenshots directory
echo "📋 Step 3: Organizing screenshots..."
COUNT=0
if [ -d "$GOLDENS_DIR" ]; then
    for file in "$GOLDENS_DIR"/*.png; do
        if [ -f "$file" ]; then
            basename=$(basename "$file")
            cp "$file" "$SCREENSHOTS_DIR/$basename"
            echo "   ✓ $basename"
            ((COUNT++))
        fi
    done
fi

if [ $COUNT -gt 0 ]; then
    echo ""
    echo "✅ Copied $COUNT screenshot(s) to screenshots directory"
else
    echo "⚠️  No golden files found. The tests may not have run correctly."
    echo "   Check test output above for errors."
fi
echo ""

# Create an index HTML file to view all screenshots
echo "🌐 Step 4: Creating screenshot viewer..."
INDEX_PATH="$SCREENSHOTS_DIR/index.html"

cat > "$INDEX_PATH" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verified Compliance - App Screenshots</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
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
        .stats {
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .stats strong {
            font-size: 1.5rem;
            color: #ffd700;
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
        .modal.active {
            display: flex;
        }
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
        .modal .close:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Verified Compliance App Screenshots</h1>
        <p class="subtitle">All app screens captured automatically</p>
        <div class="grid" id="screenshot-grid">
        </div>
    </div>
    
    <div class="modal" id="modal" onclick="closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <img src="" alt="Full size" id="modal-img">
    </div>
    
    <script>
        // Load screenshots dynamically
        async function loadScreenshots() {
            const grid = document.getElementById('screenshot-grid');
            const screenshots = [];
            
            // Try to load common screenshot names
            const screenNames = [
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
            
            for (const fileName of screenNames) {
                try {
                    const response = await fetch(fileName, { method: 'HEAD' });
                    if (response.ok) {
                        screenshots.push(fileName);
                    }
                } catch (e) {
                    // File doesn't exist, skip
                }
            }
            
            if (screenshots.length === 0) {
                grid.innerHTML = '<div style="color: white; text-align: center; padding: 4rem;">No screenshots found. Please run the generation script first.</div>';
                return;
            }
            
            // Add stats
            const stats = document.createElement('div');
            stats.className = 'stats';
            stats.innerHTML = '<strong>' + screenshots.length + '</strong> screens captured';
            grid.parentElement.insertBefore(stats, grid);
            
            // Add screenshots to grid
            screenshots.forEach(fileName => {
                const screenName = fileName
                    .replace('.png', '')
                    .replace(/_/g, ' ')
                    .replace('screen', '')
                    .trim()
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                
                const card = document.createElement('div');
                card.className = 'screenshot-card';
                card.innerHTML = `
                    <img src="${fileName}" alt="${screenName}" onclick="openModal(this.src)">
                    <div class="title">${screenName}</div>
                `;
                grid.appendChild(card);
            });
        }
        
        function openModal(src) {
            document.getElementById('modal').classList.add('active');
            document.getElementById('modal-img').src = src;
        }
        
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
        
        loadScreenshots();
    </script>
</body>
</html>
EOF

echo "✅ Created screenshot viewer at: $INDEX_PATH"
echo ""

# Summary
echo "════════════════════════════════════════"
echo "✅ SCREENSHOT GENERATION COMPLETE!"
echo "════════════════════════════════════════"
echo ""
echo "📸 Screenshots saved to: $SCREENSHOTS_DIR"
echo ""
echo "🌐 To view all screenshots:"
echo "   Open: $INDEX_PATH"
echo ""

# Try to open the viewer
if command -v xdg-open &> /dev/null; then
    read -p "Would you like to open the screenshot viewer now? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        xdg-open "$INDEX_PATH"
        echo "🎉 Opening screenshot viewer in your browser..."
    fi
elif command -v open &> /dev/null; then
    read -p "Would you like to open the screenshot viewer now? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        open "$INDEX_PATH"
        echo "🎉 Opening screenshot viewer in your browser..."
    fi
fi

echo ""
echo "✨ Done!"



