#!/bin/bash

# APM (Agent Project Manager) Development Server Script
# This script starts the full development environment with hot reload

set -e

echo "🚀 Starting APM (Agent Project Manager) Development Server..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the development servers
echo "🔧 Starting development servers..."
echo "   - Vite dev server (port 3000)"
echo "   - CSS watch mode"
echo "   - Flask app (port 5002)"

# Start all services in background
npm run dev:full &

# Wait for services to start
sleep 3

echo ""
echo "✅ Development environment ready!"
echo ""
echo "🌐 URLs:"
echo "   - Flask App: http://localhost:5002"
echo "   - Vite Dev Server: http://localhost:3000"
echo ""
echo "📝 Features:"
echo "   - Hot reload for JavaScript"
echo "   - CSS watch mode"
echo "   - Source maps for debugging"
echo "   - Local Alpine.js and HTMX"
echo ""
echo "🛑 Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
