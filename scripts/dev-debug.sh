#!/bin/bash

# APM (Agent Project Manager) Development & Debugging Script
# Comprehensive development environment with debugging, hot reload, and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
}

print_header() {
    echo -e "${MAGENTA}================================${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    if port_in_use $port; then
        print_warning "Killing processes on port $port"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to show help
show_help() {
    echo "APM (Agent Project Manager) Development & Debugging Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  debug           Start full debugging environment (default)"
    echo "  hot             Start hot reload without debugger"
    echo "  flask-only      Start only Flask server"
    echo "  vite-only       Start only Vite dev server"
    echo "  css-only        Start only CSS watch mode"
    echo "  test            Run tests with coverage"
    echo "  lint            Run linting checks"
    echo "  format          Check code formatting"
    echo "  format-fix      Fix code formatting"
    echo "  type-check      Run type checking"
    echo "  security        Run security checks"
    echo "  db-test         Test database connection"
    echo "  routes          Show all Flask routes"
    echo "  env             Show environment variables"
    echo "  ports           Check port usage"
    echo "  clean           Clean up processes and files"
    echo "  restart         Clean and restart debug environment"
    echo "  help            Show this help message"
    echo ""
    echo "Debug Ports:"
    echo "  - Vite Dev Server: 3000"
    echo "  - Vite HMR: 3001"
    echo "  - Flask App: 5000"
    echo "  - Flask Debug: 5002"
    echo "  - Python Debugger: 5678"
    echo ""
    echo "Examples:"
    echo "  $0 debug         # Start full debugging environment"
    echo "  $0 hot           # Start hot reload without debugger"
    echo "  $0 test          # Run tests"
    echo "  $0 clean         # Clean up everything"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check npm
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check if debugpy is available
    if ! python3 -c "import debugpy" 2>/dev/null; then
        print_warning "debugpy not found. Installing debugpy for debugging support..."
        pip3 install debugpy
    fi
    
    print_status "All prerequisites satisfied"
}

# Function to install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install
    else
        print_status "npm dependencies already installed"
    fi
    
    # Check if concurrently is installed
    if ! npm list concurrently >/dev/null 2>&1; then
        print_status "Installing concurrently for parallel process management..."
        npm install --save-dev concurrently
    fi
}

# Function to set up environment
setup_environment() {
    print_header "Setting Up Environment"
    
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    print_status "Environment variables set:"
    print_debug "FLASK_ENV: $FLASK_ENV"
    print_debug "FLASK_DEBUG: $FLASK_DEBUG"
    print_debug "PYTHONPATH: $PYTHONPATH"
}

# Function to start debugging environment
start_debug() {
    print_header "Starting Debug Environment"
    
    # Kill any existing processes
    kill_port 3000
    kill_port 3001
    kill_port 5000
    kill_port 5002
    kill_port 5678
    
    print_status "Starting services with debugging enabled..."
    print_debug "Vite Dev Server: http://localhost:3000"
    print_debug "Flask App: http://localhost:5000"
    print_debug "Python Debugger: localhost:5678 (attach your IDE)"
    
    # Start all services with debugging
    npm run debug:full
}

# Function to start hot reload environment
start_hot_reload() {
    print_header "Starting Hot Reload Environment"
    
    # Kill any existing processes
    kill_port 3000
    kill_port 3001
    kill_port 5000
    kill_port 5002
    
    print_status "Starting services with hot reload..."
    print_debug "Vite Dev Server: http://localhost:3000"
    print_debug "Flask App: http://localhost:5000"
    
    # Start all services without debugging
    npm run dev:hot-no-debug
}

# Function to start individual services
start_flask_only() {
    print_header "Starting Flask Server Only"
    setup_environment
    print_status "Starting Flask server on http://localhost:5000"
    npm run dev:flask-only
}

start_vite_only() {
    print_header "Starting Vite Dev Server Only"
    print_status "Starting Vite dev server on http://localhost:3000"
    npm run dev:vite-only
}

start_css_only() {
    print_header "Starting CSS Watch Mode Only"
    print_status "Starting CSS watch mode"
    npm run dev:css-only
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    print_status "Running pytest with coverage..."
    npm run debug:test
}

# Function to run linting
run_lint() {
    print_header "Running Linting"
    print_status "Running ruff linter..."
    npm run debug:lint
}

# Function to check formatting
check_format() {
    print_header "Checking Code Formatting"
    print_status "Running black formatter check..."
    npm run debug:format
}

# Function to fix formatting
fix_format() {
    print_header "Fixing Code Formatting"
    print_status "Running black formatter..."
    npm run debug:format-fix
}

# Function to run type checking
run_type_check() {
    print_header "Running Type Checking"
    print_status "Running mypy type checker..."
    npm run debug:type-check
}

# Function to run security checks
run_security() {
    print_header "Running Security Checks"
    print_status "Running bandit security scanner..."
    npm run debug:security
}

# Function to test database
test_database() {
    print_header "Testing Database Connection"
    print_status "Testing database connection..."
    npm run debug:db
}

# Function to show routes
show_routes() {
    print_header "Flask Routes"
    print_status "Listing all Flask routes..."
    npm run debug:routes
}

# Function to show environment
show_environment() {
    print_header "Environment Variables"
    npm run debug:env
}

# Function to check ports
check_ports() {
    print_header "Port Usage Check"
    print_status "Checking port usage..."
    npm run debug:ports
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up"
    print_status "Killing all development processes..."
    npm run debug:clean
    print_status "Cleanup complete"
}

# Function to restart
restart() {
    print_header "Restarting Debug Environment"
    cleanup
    sleep 2
    start_debug
}

# Main script logic
main() {
    local command=${1:-debug}
    
    case $command in
        debug)
            check_prerequisites
            install_dependencies
            setup_environment
            start_debug
            ;;
        hot)
            check_prerequisites
            install_dependencies
            setup_environment
            start_hot_reload
            ;;
        flask-only)
            check_prerequisites
            setup_environment
            start_flask_only
            ;;
        vite-only)
            check_prerequisites
            install_dependencies
            start_vite_only
            ;;
        css-only)
            check_prerequisites
            install_dependencies
            start_css_only
            ;;
        test)
            check_prerequisites
            run_tests
            ;;
        lint)
            check_prerequisites
            run_lint
            ;;
        format)
            check_prerequisites
            check_format
            ;;
        format-fix)
            check_prerequisites
            fix_format
            ;;
        type-check)
            check_prerequisites
            run_type_check
            ;;
        security)
            check_prerequisites
            run_security
            ;;
        db-test)
            check_prerequisites
            test_database
            ;;
        routes)
            check_prerequisites
            show_routes
            ;;
        env)
            show_environment
            ;;
        ports)
            check_ports
            ;;
        clean)
            cleanup
            ;;
        restart)
            restart
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
