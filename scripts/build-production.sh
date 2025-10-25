#!/bin/bash

# APM (Agent Project Manager) Production Build Script
# This script creates a production-ready build

set -e

echo "🏗️  Building APM (Agent Project Manager) for Production..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
npm run clean

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build CSS and JavaScript
echo "🔨 Building assets..."
npm run build

# Verify builds
echo "✅ Verifying builds..."

if [ -f "agentpm/web/static/css/brand-system.css" ]; then
    echo "   ✓ CSS build successful"
else
    echo "   ❌ CSS build failed"
    exit 1
fi

if [ -d "agentpm/web/static/js/dist" ]; then
    echo "   ✓ JavaScript build successful"
    echo "   📁 Built files:"
    ls -la agentpm/web/static/js/dist/
else
    echo "   ❌ JavaScript build failed"
    exit 1
fi

echo ""
echo "🎉 Production build complete!"
echo ""
echo "📁 Built assets:"
echo "   - CSS: agentpm/web/static/css/brand-system.css"
echo "   - JS: agentpm/web/static/js/dist/"
echo ""
echo "🚀 To run in production:"
echo "   export FLASK_ENV=production"
echo "   python -m agentpm.web.app"
echo ""
echo "📊 Build stats:"
echo "   - CSS size: $(du -h agentpm/web/static/css/brand-system.css | cut -f1)"
echo "   - JS size: $(du -sh agentpm/web/static/js/dist/ | cut -f1)"
