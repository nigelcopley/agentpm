"""
apm web - Web server management commands

Provides commands to start, stop, and manage the APM (Agent Project Manager) web frontend.
Integrates with the existing Flask application and database auto-detection.

Features:
- Start web server with automatic database detection
- Port conflict resolution and management
- Debug mode support
- Development environment integration
- Process management and status checking

Performance target: <2 seconds startup
"""

import click
import os
import subprocess
import signal
import sys
import time
import psutil
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Confirm

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.group()
@click.pass_context
def web(ctx: click.Context):
    """
    🌐 Web server management commands.
    
    Start, stop, and manage the APM (Agent Project Manager) web frontend with automatic
    database detection and port management.
    
    \b
    Examples:
      apm web start              # Start web server on default port
      apm web start --port 8080  # Start on specific port
      apm web start --debug      # Start in debug mode
      apm web status             # Check server status
      apm web stop               # Stop running server
    """
    ctx.ensure_object(dict)
    ctx.obj['console'] = Console()


@web.command()
@click.option('--port', '-p', type=int, default=5002, help='Port to run on (default: 5002)')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
@click.option('--dev', is_flag=True, help='Start full development environment (Vite + Flask)')
@click.option('--force', '-f', is_flag=True, help='Force start even if port is in use')
@click.pass_context
def start(ctx: click.Context, port: int, host: str, debug: bool, dev: bool, force: bool):
    """
    Start the APM (Agent Project Manager) web server.
    
    Automatically detects the project database and starts the Flask application
    with the specified configuration. Handles port conflicts gracefully.
    
    \b
    Examples:
      apm web start                    # Start on default port 5002
      apm web start --port 8080        # Start on port 8080
      apm web start --debug            # Start in debug mode
      apm web start --dev              # Start full dev environment
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    
    # Check if port is already in use
    if not force and is_port_in_use(port):
        console.print(f"[red]❌ Port {port} is already in use[/red]")
        
        # Find alternative port
        alt_port = find_available_port(port)
        if alt_port:
            if Confirm.ask(f"Use port {alt_port} instead?"):
                port = alt_port
            else:
                console.print("[yellow]Use --force to override or choose a different port[/yellow]")
                return
        else:
            console.print("[red]No available ports found. Use --force to override.[/red]")
            return
    
    # Set up environment variables
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development' if debug else 'production'
    env['FLASK_DEBUG'] = '1' if debug else '0'
    env['FLASK_PORT'] = str(port)
    
    # Auto-detect database path (same logic as web app)
    db_path = detect_database_path(project_root)
    if db_path:
        env['AIPM_DB_PATH'] = str(db_path)
        console.print(f"[green]✓[/green] Database detected: {db_path}")
    
    if dev:
        # Start full development environment
        start_dev_environment(console, port, host, env)
    else:
        # Start Flask server only
        start_flask_server(console, port, host, env, debug)


@web.command()
@click.pass_context
def status(ctx: click.Context):
    """
    Check the status of the APM (Agent Project Manager) web server.
    
    Shows information about running web server processes, ports in use,
    and database connections.
    """
    console = ctx.obj['console']
    
    # Find running Flask processes
    flask_processes = find_flask_processes()
    
    if not flask_processes:
        console.print("[yellow]No AIPM web servers are currently running[/yellow]")
        return
    
    # Create status table
    table = Table(title="🌐 AIPM Web Server Status")
    table.add_column("PID", style="cyan")
    table.add_column("Port", style="green")
    table.add_column("Host", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="magenta")
    
    for proc in flask_processes:
        try:
            # Get process info
            pid = proc.pid
            port = get_process_port(proc)
            host = get_process_host(proc)
            status = "Running" if proc.is_running() else "Stopped"
            started = time.strftime("%H:%M:%S", time.localtime(proc.create_time()))
            
            table.add_row(str(pid), str(port), host, status, started)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    console.print(table)
    
    # Show URLs
    console.print("\n[bold]🌐 Available URLs:[/bold]")
    for proc in flask_processes:
        try:
            port = get_process_port(proc)
            if port:
                console.print(f"  • http://127.0.0.1:{port}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


@web.command()
@click.option('--all', '-a', is_flag=True, help='Stop all running web servers')
@click.option('--port', '-p', type=int, help='Stop server on specific port')
@click.pass_context
def stop(ctx: click.Context, all: bool, port: Optional[int]):
    """
    Stop the APM (Agent Project Manager) web server.
    
    Gracefully stops running web server processes. Can stop all servers
    or target a specific port.
    
    \b
    Examples:
      apm web stop              # Stop all AIPM web servers
      apm web stop --port 5002  # Stop server on port 5002
    """
    console = ctx.obj['console']
    
    flask_processes = find_flask_processes()
    
    if not flask_processes:
        console.print("[yellow]No AIPM web servers are currently running[/yellow]")
        return
    
    # Filter processes by port if specified
    if port:
        flask_processes = [p for p in flask_processes if get_process_port(p) == port]
        if not flask_processes:
            console.print(f"[yellow]No web server found on port {port}[/yellow]")
            return
    
    # Stop processes
    stopped_count = 0
    for proc in flask_processes:
        try:
            proc_port = get_process_port(proc)
            console.print(f"[yellow]Stopping web server on port {proc_port}...[/yellow]")
            
            # Graceful shutdown
            proc.terminate()
            proc.wait(timeout=5)
            
            console.print(f"[green]✓[/green] Stopped web server on port {proc_port}")
            stopped_count += 1
            
        except psutil.TimeoutExpired:
            # Force kill if graceful shutdown fails
            proc.kill()
            console.print(f"[red]Force killed web server on port {proc_port}[/red]")
            stopped_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            console.print(f"[red]Error stopping process: {e}[/red]")
    
    if stopped_count > 0:
        console.print(f"[green]✓[/green] Stopped {stopped_count} web server(s)")


@web.command()
@click.option('--port', '-p', type=int, default=5002, help='Port to restart on (default: 5002)')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
@click.option('--debug', '-d', is_flag=True, help='Enable debug mode')
@click.pass_context
def restart(ctx: click.Context, port: int, host: str, debug: bool):
    """
    Restart the APM (Agent Project Manager) web server.
    
    Stops any running server on the specified port and starts a new one
    with the same configuration.
    
    \b
    Examples:
      apm web restart              # Restart on default port
      apm web restart --port 8080  # Restart on port 8080
    """
    console = ctx.obj['console']
    
    # Stop existing server on this port
    ctx.invoke(stop, port=port)
    
    # Wait a moment for cleanup
    time.sleep(1)
    
    # Start new server
    console.print(f"[green]Starting web server on port {port}...[/green]")
    ctx.invoke(start, port=port, host=host, debug=debug)


# Helper functions

def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None


def detect_database_path(project_root: Path) -> Optional[Path]:
    """
    Detect AIPM database path using the same logic as the web app.
    
    Detection Priority:
    1. Environment variable AIPM_DB_PATH (explicit override)
    2. Current directory .aipm/data/aipm.db (project context)
    3. Parent directories (walk up to find AIPM project)
    4. Home directory ~/.aipm/aipm.db (global fallback)
    """
    # 1. Check environment variable (explicit override)
    if 'AIPM_DB_PATH' in os.environ:
        return Path(os.environ['AIPM_DB_PATH'])
    
    # 2. Check current directory for project database
    project_db = project_root / '.aipm' / 'data' / 'aipm.db'
    if project_db.exists():
        return project_db
    
    # 3. Walk up parent directories to find AIPM project
    search_dir = project_root
    for _ in range(10):  # Limit search depth
        candidate_db = search_dir / '.aipm' / 'data' / 'aipm.db'
        if candidate_db.exists():
            return candidate_db
        
        # Move to parent directory
        parent = search_dir.parent
        if parent == search_dir:  # Reached filesystem root
            break
        search_dir = parent
    
    # 4. Fall back to global database
    global_db = Path.home() / '.aipm' / 'aipm.db'
    if global_db.exists():
        return global_db
    
    return None


def find_flask_processes() -> List[psutil.Process]:
    """Find running Flask processes related to AIPM."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if ('agentpm.web.app' in cmdline or 
                'flask --app agentpm.web.app' in cmdline):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def get_process_port(proc: psutil.Process) -> Optional[int]:
    """Extract port number from process command line."""
    try:
        cmdline = ' '.join(proc.info['cmdline'] or [])
        # Look for --port or FLASK_PORT
        import re
        port_match = re.search(r'--port\s+(\d+)', cmdline)
        if port_match:
            return int(port_match.group(1))
        
        # Check environment variables
        env = proc.environ()
        if 'FLASK_PORT' in env:
            return int(env['FLASK_PORT'])
            
        # Default Flask port
        return 5000
    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
        return None


def get_process_host(proc: psutil.Process) -> str:
    """Extract host from process command line."""
    try:
        cmdline = ' '.join(proc.info['cmdline'] or [])
        import re
        host_match = re.search(r'--host\s+([^\s]+)', cmdline)
        if host_match:
            return host_match.group(1)
        return '127.0.0.1'
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return '127.0.0.1'


def start_flask_server(console: Console, port: int, host: str, env: dict, debug: bool):
    """Start the Flask web server."""
    console.print(f"[green]🚀 Starting AIPM web server...[/green]")
    console.print(f"   Port: {port}")
    console.print(f"   Host: {host}")
    console.print(f"   Debug: {'Yes' if debug else 'No'}")
    
    # Build Flask command
    cmd = [
        sys.executable, '-m', 'flask', 
        '--app', 'agentpm.web.app', 
        'run',
        '--port', str(port),
        '--host', host
    ]
    
    if debug:
        cmd.append('--debug')
    
    console.print(f"\n[blue]🌐 Web server starting at: http://{host}:{port}[/blue]")
    console.print("[yellow]Press Ctrl+C to stop the server[/yellow]\n")
    
    try:
        # Start the server
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]Web server stopped by user[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to start web server: {e}[/red]")
        sys.exit(1)


def start_dev_environment(console: Console, port: int, host: str, env: dict):
    """Start the full development environment (Vite + Flask)."""
    console.print(f"[green]🚀 Starting AIPM development environment...[/green]")
    console.print(f"   Flask Port: {port}")
    console.print(f"   Vite Port: 3000")
    console.print(f"   Host: {host}")
    
    # Check if package.json exists
    if not Path('package.json').exists():
        console.print("[red]❌ package.json not found. Run from project root.[/red]")
        return
    
    # Check if node_modules exists
    if not Path('node_modules').exists():
        console.print("[yellow]Installing dependencies...[/yellow]")
        subprocess.run(['npm', 'install'], check=True)
    
    console.print(f"\n[blue]🌐 Development URLs:[/blue]")
    console.print(f"   • Flask App: http://{host}:{port}")
    console.print(f"   • Vite Dev Server: http://localhost:3000")
    console.print("[yellow]Press Ctrl+C to stop all services[/yellow]\n")
    
    try:
        # Start development environment using npm script
        subprocess.run(['npm', 'run', 'dev:full'], env=env, check=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]Development environment stopped by user[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to start development environment: {e}[/red]")
        sys.exit(1)