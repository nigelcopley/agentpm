# APM (Agent Project Manager) Development Guide

This guide covers the comprehensive development and debugging setup for APM (Agent Project Manager), including hot reloading, debugging, and monitoring tools.

## Quick Start

### Option 1: Using npm scripts (Recommended)

```bash
# Start full debugging environment with hot reload
npm run debug

# Start hot reload without debugger
npm run dev:hot

# Start individual services
npm run dev:flask-only    # Flask server only
npm run dev:vite-only     # Vite dev server only
npm run dev:css-only      # CSS watch mode only
```

### Option 2: Using the development script

```bash
# Make script executable (first time only)
chmod +x scripts/dev-debug.sh

# Start full debugging environment
./scripts/dev-debug.sh debug

# Start hot reload without debugger
./scripts/dev-debug.sh hot

# Show all available options
./scripts/dev-debug.sh help
```

## Development Environment

### Ports and Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Vite Dev Server | 3000 | http://localhost:3000 | Frontend development server with HMR |
| Vite HMR | 3001 | - | Hot Module Replacement WebSocket |
| Flask App | 5003 | http://localhost:5003 | Main Flask application (avoiding macOS AirPlay on 5000) |
| Python Debugger | 5678 | - | Debugpy server for IDE attachment |

### Environment Variables

```bash
FLASK_ENV=development      # Flask environment
FLASK_DEBUG=1             # Enable Flask debug mode
PYTHONPATH=/path/to/project # Python path for imports
AIPM_DB_PATH=/path/to/db  # Optional: override database path
```

## Debugging Setup

### VS Code Debugging

1. **Attach to running Flask app:**
   - Start the debug environment: `npm run debug`
   - In VS Code, go to Run and Debug (Ctrl+Shift+D)
   - Select "Debug Flask App" configuration
   - Click the play button to attach

2. **Launch Flask app directly:**
   - Select "Debug Flask App (Launch)" configuration
   - This will start Flask with debugger attached

3. **Debug tests:**
   - Select "Debug Tests" configuration
   - This will run pytest with debugger attached

4. **Debug CLI commands:**
   - Select "Debug CLI Command" configuration
   - Enter the CLI command when prompted

### PyCharm Debugging

1. Create a new "Python Debug Server" configuration
2. Set host to `localhost` and port to `5678`
3. Start the debug environment: `npm run debug`
4. Attach the debugger in PyCharm

### Command Line Debugging

```bash
# Start Flask with debugger waiting for attachment
npm run debug:flask

# Start Flask with debugger (no wait)
npm run debug:flask-no-wait

# Test database connection
npm run debug:db

# Show all Flask routes
npm run debug:routes
```

## Development Scripts

### Core Development Scripts

```bash
# Full debugging environment
npm run debug                    # Start everything with debugging
npm run debug:full              # Same as above (explicit)

# Hot reload without debugging
npm run dev:hot                 # Start with hot reload
npm run dev:hot-no-debug        # Same as above (explicit)

# Individual services
npm run dev:flask-only          # Flask server only
npm run dev:vite-only           # Vite dev server only
npm run dev:css-only            # CSS watch mode only
```

### Quality Assurance Scripts

```bash
# Testing
npm run debug:test              # Run tests with coverage
npm run debug:test              # Same as above

# Code Quality
npm run debug:lint              # Run ruff linter
npm run debug:format            # Check code formatting
npm run debug:format-fix        # Fix code formatting
npm run debug:type-check        # Run mypy type checking
npm run debug:security          # Run bandit security scanner
```

### Utility Scripts

```bash
# Environment and System
npm run debug:env               # Show environment variables
npm run debug:ports             # Check port usage
npm run debug:routes            # Show Flask routes
npm run debug:db                # Test database connection

# Cleanup and Restart
npm run debug:clean             # Kill all processes and clean files
npm run debug:restart           # Clean and restart debug environment
npm run clean                   # Clean build artifacts only
```

## Hot Reloading Features

### Frontend Hot Reloading

- **Vite Dev Server**: Automatic JavaScript/TypeScript reloading
- **CSS Watch Mode**: Automatic Tailwind CSS compilation
- **Source Maps**: Full source map support for debugging
- **HMR**: Hot Module Replacement for instant updates

### Backend Development

- **Flask Debug Mode**: Automatic reloading on code changes
- **Debugger Integration**: Full debugging support with breakpoints
- **Database Auto-detection**: Automatic database path detection
- **Error Pages**: Detailed error pages in development

## File Structure

```
agentpm/web/
├── src/
│   ├── js/                     # JavaScript source files
│   │   ├── main.js            # Main entry point
│   │   └── components/        # JavaScript components
│   └── styles/                # CSS source files
│       ├── brand-system.css   # Legacy Tailwind CSS source
│       ├── theme-system-v3.css # Tailwind v3 compatible theme system
│       └── components-v3.css  # Tailwind v3 compatible components
├── static/                    # Static assets (generated)
│   ├── css/                   # Compiled CSS
│   └── js/                    # Compiled JavaScript
├── templates/                 # Flask templates
└── app.py                     # Flask application
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   npm run debug:ports          # Check what's using ports
   npm run debug:clean          # Kill all processes
   ```

2. **Database connection issues:**
   ```bash
   npm run debug:db             # Test database connection
   ```

3. **Dependencies not installed:**
   ```bash
   npm install                  # Install npm dependencies
   pip install debugpy          # Install Python debugger
   ```

4. **Environment variables not set:**
   ```bash
   npm run debug:env            # Check environment variables
   ```

### Debugging Tips

1. **Use the development script for comprehensive debugging:**
   ```bash
   ./scripts/dev-debug.sh debug
   ```

2. **Check logs in the terminal output** - each service has colored output

3. **Use VS Code debugger** - attach to the running Flask process

4. **Monitor port usage** - ensure no conflicts with other services

5. **Test individual components** - use the individual service scripts

## Production Build

```bash
# Build for production
npm run build

# Clean build artifacts
npm run clean
```

## Additional Tools

### Database Management

```bash
# Test database connection
python -c "from agentpm.core.database.service import DatabaseService; print('DB OK:', DatabaseService().get_connection())"

# Show database info
apm status
```

### CLI Development

```bash
# Test CLI commands
apm --help
apm status
apm work-item list
```

## Contributing

1. Use the debugging environment for development
2. Run tests before committing: `npm run debug:test`
3. Check code quality: `npm run debug:lint`
4. Ensure formatting is correct: `npm run debug:format-fix`
5. Test security: `npm run debug:security`

## Support

For issues with the development environment:

1. Check this guide first
2. Run `./scripts/dev-debug.sh help` for script options
3. Check the troubleshooting section
4. Review the logs in the terminal output
