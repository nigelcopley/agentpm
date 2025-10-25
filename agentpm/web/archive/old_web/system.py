"""
System Blueprint - System Administration and Monitoring

Handles:
- /system/health - System health dashboard
- /system/database - Database metrics and management
- /system/workflow - Workflow visualization
- /system/context-files - Context file browser
- /system/context-files/preview/<path> - Preview context file
- /system/context-files/download/<path> - Download context file
"""

from flask import Blueprint, render_template, abort, request, send_file, jsonify
from pathlib import Path
import os
import json

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods

# Import helper functions from app
from ..app import get_database_service

system_bp = Blueprint('system', __name__)


@system_bp.route('/system/health')
def system_health():
    """System health dashboard."""
    db = get_database_service()

    # Get system metrics
    projects = project_methods.list_projects(db)
    work_items = wi_methods.list_work_items(db)
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    agents = agent_methods.list_agents(db)
    rules = rule_methods.list_rules(db)

    # Calculate health metrics
    health_metrics = {
        'total_projects': len(projects),
        'total_work_items': len(work_items),
        'total_tasks': len(tasks),
        'total_agents': len(agents),
        'total_rules': len(rules),
        'active_agents': sum(1 for a in agents if a.is_active),
        'enabled_rules': sum(1 for r in rules if r.enabled),
        'database_size': _get_database_size(db),
        'uptime': _get_system_uptime()
    }

    return render_template(
        'system/health.html',
        health_metrics=health_metrics,
        show_sidebar='system'
    )


@system_bp.route('/system/database')
def database_metrics():
    """Database metrics and management."""
    db = get_database_service()

    # Get database statistics
    db_stats = _get_database_statistics(db)

    # Get table sizes
    table_sizes = _get_table_sizes(db)

    # Get recent activity
    recent_activity = _get_recent_database_activity(db)

    return render_template(
        'system/database.html',
        db_stats=db_stats,
        table_sizes=table_sizes,
        recent_activity=recent_activity,
        show_sidebar='system'
    )


@system_bp.route('/system/workflow')
def workflow_visualization():
    """Workflow visualization."""
    db = get_database_service()

    # Get workflow data
    workflow_data = _get_workflow_data(db)

    return render_template(
        'system/workflow.html',
        workflow_data=workflow_data,
        show_sidebar='system'
    )


@system_bp.route('/system/context-files')
def context_files():
    """Context file browser."""
    # Get context files directory
    context_dir = Path('.aipm/contexts')
    
    if not context_dir.exists():
        return render_template(
            'system/context_files.html',
            files=[],
            current_path='',
            show_sidebar='system'
        )

    # Get current path from query param
    current_path = request.args.get('path', '')
    target_dir = context_dir / current_path if current_path else context_dir

    if not target_dir.exists() or not target_dir.is_dir():
        abort(404, description="Directory not found")

    # List files and directories
    files = []
    for item in sorted(target_dir.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            files.append({
                'name': item.name,
                'path': str(item.relative_to(context_dir)),
                'size': size,
                'size_formatted': _format_file_size(size),
                'is_file': True
            })
        elif item.is_dir():
            files.append({
                'name': item.name,
                'path': str(item.relative_to(context_dir)),
                'size': None,
                'size_formatted': None,
                'is_file': False
            })

    return render_template(
        'system/context_files.html',
        files=files,
        current_path=current_path,
        show_sidebar='system'
    )


@system_bp.route('/system/context-files/preview/<path:filepath>')
def context_file_preview(filepath: str):
    """Preview context file."""
    context_dir = Path('.aipm/contexts')
    file_path = context_dir / filepath

    if not file_path.exists() or not file_path.is_file():
        abort(404, description="File not found")

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        content = "Binary file - cannot preview"

    # Get file info
    file_info = {
        'name': file_path.name,
        'path': filepath,
        'size': file_path.stat().st_size,
        'size_formatted': _format_file_size(file_path.stat().st_size),
        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
    }

    return render_template(
        'system/context_file_preview.html',
        file_info=file_info,
        content=content
    )


@system_bp.route('/system/context-files/download/<path:filepath>')
def context_file_download(filepath: str):
    """Download context file."""
    context_dir = Path('.aipm/contexts')
    file_path = context_dir / filepath

    if not file_path.exists() or not file_path.is_file():
        abort(404, description="File not found")

    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_path.name
    )


def _get_database_size(db):
    """Get database file size."""
    try:
        db_path = db.db_path
        if os.path.exists(db_path):
            size_bytes = os.path.getsize(db_path)
            return _format_file_size(size_bytes)
    except Exception:
        pass
    return "Unknown"


def _get_system_uptime():
    """Get system uptime."""
    try:
        import psutil
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        return str(uptime).split('.')[0]  # Remove microseconds
    except ImportError:
        return "Unknown"


def _get_database_statistics(db):
    """Get database statistics."""
    stats = {}
    
    try:
        # Get table counts
        tables = ['projects', 'work_items', 'tasks', 'agents', 'rules', 'contexts']
        for table in tables:
            with db.connect() as conn:
                result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = result.fetchone()[0]
        
        # Get database version
        with db.connect() as conn:
            result = conn.execute("SELECT sqlite_version()")
            stats['sqlite_version'] = result.fetchone()[0]
        
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def _get_table_sizes(db):
    """Get table sizes."""
    sizes = []
    
    try:
        tables = ['projects', 'work_items', 'tasks', 'agents', 'rules', 'contexts']
        for table in tables:
            with db.connect() as conn:
                result = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.fetchone()[0]
                sizes.append({
                    'table': table,
                    'count': count
                })
    except Exception as e:
        sizes.append({'table': 'error', 'count': str(e)})
    
    return sizes


def _get_recent_database_activity(db):
    """Get recent database activity."""
    # This would typically query a log table or audit trail
    # For now, return empty list
    return []


def _get_workflow_data(db):
    """Get workflow data for visualization."""
    # Get workflow phases and their counts
    phases = ['D1_discovery', 'P1_plan', 'I1_implementation', 'R1_review', 'O1_operations', 'E1_evolution']
    phase_counts = {}
    
    for phase in phases:
        with db.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM work_items WHERE phase = ?", (phase,))
            phase_counts[phase] = result.fetchone()[0]
    
    return {
        'phases': phases,
        'phase_counts': phase_counts
    }


def _format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
