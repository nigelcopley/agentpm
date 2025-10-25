"""
Flask Dashboard Application - APM (Agent Project Manager) Project Status

Minimal Flask app serving localhost:5000 with read-only project status dashboard.

Architecture:
- Flask app with modular blueprint organization
- DatabaseService integration (existing three-layer pattern)
- Pydantic models for type safety
- Bootstrap 5 for professional styling
- Automatic database detection (no configuration needed!)

Usage:
    # From APM project directory (auto-detects .agentpm/data/agentpm.db)
    flask --app agentpm.web.app run

    # Or specify explicit database path
    agentpm.db_PATH=/path/to/agentpm.db flask --app agentpm.web.app run

Database Detection Priority:
    1. agentpm.db_PATH environment variable (explicit override)
    2. Current directory .agentpm/data/agentpm.db (project context)
    3. Parent directories (walks up to find APM project)
    4. Home directory ~/.agentpm/agentpm.db (global fallback)

Example:
    # Run from project root - auto-detects project database
    cd /path/to/aipm-v2
    flask --app agentpm.web.app run
    open http://localhost:5000
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

from flask import Flask, make_response, render_template
from flask_wtf.csrf import CSRFProtect
from pydantic import BaseModel

from .config import config

from ..core.database.service import DatabaseService
from ..core.database.models import Project, WorkItem, Task, Agent, Rule, WorkItemSummary
from ..core.database.enums import TaskType

# Import database methods (three-layer pattern)
from ..core.database.methods import projects as project_methods

# Pydantic models for dashboard data (no Dict[str, Any] in public APIs)

class StatusDistribution(BaseModel):
    """Status distribution metrics"""
    status: str
    count: int
    percentage: float


class TypeDistribution(BaseModel):
    """Type distribution metrics"""
    type: str
    count: int
    percentage: float


class TimeBoxingMetrics(BaseModel):
    """Time-boxing compliance metrics"""
    total_tasks: int
    compliant_tasks: int
    non_compliant_tasks: int
    compliance_rate: float
    violations: List[Dict[str, Any]]  # Task violations with details


class DashboardMetrics(BaseModel):
    """Complete dashboard metrics"""
    project_name: str
    project_status: str
    total_work_items: int
    total_tasks: int
    work_item_status_dist: List[StatusDistribution]
    work_item_type_dist: List[TypeDistribution]
    task_status_dist: List[StatusDistribution]
    task_type_dist: List[TypeDistribution]
    time_boxing: TimeBoxingMetrics


# Detail view models

class TaskSummary(BaseModel):
    """Lightweight task summary for listings"""
    id: int
    name: str
    type: str
    status: str
    effort_hours: Optional[float]
    priority: int
    assigned_to: Optional[str]
    due_date: Optional[Any]
    blocked_reason: Optional[str]
    started_at: Optional[Any]
    completed_at: Optional[Any]


class DependencyInfo(BaseModel):
    """Dependency relationship information"""
    task_id: int
    task_name: str
    dependency_type: str
    notes: Optional[str]


class WorkItemDependencyInfo(BaseModel):
    """Work item level dependency relationship information"""
    work_item_id: int
    work_item_name: str
    project_name: str
    status: str
    dependency_type: str
    notes: Optional[str]
    phase: Optional[str]


class BlockerInfo(BaseModel):
    """Blocker information"""
    id: int
    blocker_type: str
    task_id: Optional[int]
    task_name: Optional[str]
    description: Optional[str]
    reference: Optional[str]
    is_resolved: bool


class ProjectListItem(BaseModel):
    """Project for list view"""
    project: Project
    total_work_items: int
    total_tasks: int
    total_agents: int
    total_rules: int


class ProjectDetail(BaseModel):
    """Detailed project view with comprehensive context"""
    project: Project
    total_work_items: int
    total_tasks: int
    total_agents: int
    total_rules: int
    work_item_status_dist: List[StatusDistribution]
    task_status_dist: List[StatusDistribution]
    # Enhanced context data
    project_context: Optional[Any] = None  # Context model
    recent_events: List[Any] = []  # Recent events
    recent_summaries: List[Any] = []  # Recent summaries


class WorkItemDetail(BaseModel):
    """Detailed work item view"""
    work_item: WorkItem
    project_name: str
    tasks: List[TaskSummary]
    task_status_dist: List[StatusDistribution]
    task_type_dist: List[TypeDistribution]
    progress_percent: float
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    total_effort_hours: float
    time_boxing: TimeBoxingMetrics
    time_boxing_compliant: bool
    summary_count: int
    documents_count: int
    latest_summary: Optional[WorkItemSummary]
    work_item_dependencies: List[WorkItemDependencyInfo]
    work_item_dependents: List[WorkItemDependencyInfo]
    child_work_items: List[WorkItem]


class TaskDetail(BaseModel):
    """Detailed task view"""
    task: Task
    work_item_name: str
    project_name: str
    work_item: Optional[WorkItem] = None
    project: Optional[Project] = None
    dependencies: List[DependencyInfo]
    dependents: List[DependencyInfo]
    blockers: List[BlockerInfo]
    time_boxing_compliant: bool
    max_hours: Optional[float]
    time_box_limit: Optional[float] = None
    time_box_usage_percent: Optional[int] = None
    time_box_overage_hours: Optional[float] = None


class AgentInfo(BaseModel):
    """Agent summary information"""
    id: int
    name: str
    role: str
    description: Optional[str]
    capabilities: Optional[List[str]]
    is_active: bool
    assigned_task_count: int
    active_task_count: int
    created_at: Optional[Any]
    updated_at: Optional[Any]


class AgentsDashboard(BaseModel):
    """Agents dashboard data structure"""
    total_agents: int
    active_agents: int
    total_assigned_tasks: int
    total_active_tasks: int
    role_distribution: Dict[str, Any]
    agents_list: List[AgentInfo]


class RuleInfo(BaseModel):
    """Rule summary information"""
    rule: Rule
    is_active: bool


class WorkItemListItem(BaseModel):
    """Work item for list view"""
    work_item: WorkItem
    project_name: str
    tasks_count: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    total_effort_hours: float
    progress_percent: float
    time_boxing: TimeBoxingMetrics
    latest_summary: Optional[WorkItemSummary]
    documents_count: int
    due_in_days: Optional[int]
    latest_activity_at: Optional[Any]
    latest_activity_sort_key: str


class TaskListItem(BaseModel):
    """Task for list view"""
    task: Task
    work_item_name: str
    project_name: str
    time_boxing_compliant: bool

    @property
    def id(self) -> int:
        return self.task.id

    @property
    def name(self) -> str:
        return self.task.name

    @property
    def type(self) -> TaskType:
        return self.task.type

    @property
    def status(self):
        return self.task.status

    @property
    def work_item_id(self) -> int:
        return self.task.work_item_id

    @property
    def effort_hours(self) -> Optional[float]:
        return self.task.effort_hours

    @property
    def created_at(self):
        return getattr(self.task, 'created_at', None)

    @property
    def assigned_to(self):
        return getattr(self.task, 'assigned_to', None)

    @property
    def priority(self):
        return getattr(self.task, 'priority', None)


class WorkItemSummariesView(BaseModel):
    """Work item summaries timeline view"""
    work_item: WorkItem
    project_name: str
    summaries: List[WorkItemSummary]
    total_sessions: int
    total_hours: float
    session_types: Dict[str, int]


class ProjectContextView(BaseModel):
    """Project context view with 6W framework"""
    project: Project
    context: Optional[Any]  # Context model from database
    has_context: bool
    confidence_score: Optional[float]
    confidence_band: Optional[str]
    freshness_days: Optional[int]


class ContextFileInfo(BaseModel):
    """Context file metadata"""
    name: str
    path: str  # Relative to .agentpm/contexts/
    size_bytes: int
    size_human: str  # e.g., "15.2 KB"
    modified: Any
    file_type: str  # e.g., ".txt", ".md", ".json"


class ContextFilesView(BaseModel):
    """Context files list view"""
    project: Optional[Project]
    files: List[ContextFileInfo]
    total_files: int
    total_size: int  # Total size in bytes


class ContextFilePreview(BaseModel):
    """Context file preview view"""
    filename: str
    filepath: str
    content: str
    is_truncated: bool
    size_bytes: int
    modified: Any


class WorkflowState(BaseModel):
    """Workflow state information"""
    name: str
    description: str
    allowed_transitions: List[str]
    requirements: List[str]


class WorkflowVisualization(BaseModel):
    """Workflow state machine view"""
    states: List[WorkflowState]
    time_boxing_rules: Dict[str, float]  # TaskType -> max hours
    required_tasks_by_work_item: Dict[str, List[str]]  # WorkItemType -> required TaskTypes


class TableInfo(BaseModel):
    """Database table information"""
    name: str
    row_count: int
    column_count: int
    index_count: int


class DatabaseMetrics(BaseModel):
    """Database metrics view"""
    total_tables: int
    total_indexes: int
    total_triggers: int
    total_projects: int
    total_work_items: int
    total_tasks: int
    total_agents: int
    total_rules: int
    total_contexts: int
    tables: List[TableInfo]


# Flask application

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Flask-WTF CSRF Protection (WI-36)
# app.config['SECRET_KEY'] is now set by config class
# Temporarily disable CSRF for testing
# csrf = CSRFProtect(app)

# Register markdown and enum filters
from .utils.markdown import render_markdown, markdown_to_text, format_enum_display

# Helper function to find latest built files
def get_latest_built_files():
    """Find the latest built JavaScript files from Vite"""
    import os
    import glob
    from pathlib import Path
    
    dist_dir = Path(app.static_folder) / 'js' / 'dist'
    
    if not dist_dir.exists():
        return {
            'main_js': None,
            'main_legacy_js': None,
            'vendor_js': None,
            'vendor_legacy_js': None
        }
    
    # Find files by pattern
    main_files = list(dist_dir.glob('main.*.js'))
    main_legacy_files = list(dist_dir.glob('main-legacy.*.js'))
    vendor_files = list(dist_dir.glob('vendor.*.js'))
    vendor_legacy_files = list(dist_dir.glob('vendor-legacy.*.js'))
    
    # Get the most recent files (by modification time)
    def get_latest(files):
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime).name
    
    return {
        'main_js': get_latest(main_files),
        'main_legacy_js': get_latest(main_legacy_files),
        'vendor_js': get_latest(vendor_files),
        'vendor_legacy_js': get_latest(vendor_legacy_files)
    }

# Template context processor for development vs production
@app.context_processor
def inject_config():
    return {
        'use_dev_template': app.config.get('USE_DEV_TEMPLATE', False),
        'vite_dev_server_url': app.config.get('VITE_DEV_SERVER_URL', 'http://localhost:3000'),
        'built_files': get_latest_built_files()
    }
app.jinja_env.filters['markdown'] = render_markdown
app.jinja_env.filters['markdown_to_text'] = markdown_to_text
app.jinja_env.filters['enum_display'] = format_enum_display


# ========================================
# Toast Notification Helpers (WI-36 Task #180)
# ========================================

def add_toast(response, message: str, toast_type: str = 'info', duration: int = 5000):
    """
    Add toast notification headers to a Flask response.

    This helper function adds X-Toast-Message and X-Toast-Type headers
    to any Flask response object, which are automatically picked up by
    the JavaScript toast system.

    Args:
        response: Flask response object (from make_response())
        message: Toast message text
        toast_type: Toast type ('success', 'error', 'warning', 'info')
        duration: Auto-dismiss duration in milliseconds (default: 5000)

    Returns:
        Modified response object with toast headers

    Example:
        response = make_response(redirect(url_for('dashboard')))
        add_toast(response, 'Settings saved successfully', 'success')
        return response
    """
    response.headers['X-Toast-Message'] = message
    response.headers['X-Toast-Type'] = toast_type
    response.headers['X-Toast-Duration'] = str(duration)
    return response


def toast_response(message: str, toast_type: str = 'info', status_code: int = 204, duration: int = 5000):
    """
    Create an HTMX-compatible empty response with toast headers.

    This is useful for HTMX POST requests that don't need to return
    any content (hx-swap="none" pattern), but want to show user feedback.

    Args:
        message: Toast message text
        toast_type: Toast type ('success', 'error', 'warning', 'info')
        status_code: HTTP status code (default: 204 No Content)
        duration: Auto-dismiss duration in milliseconds (default: 5000)

    Returns:
        Flask response with toast headers and empty body

    Example:
        @app.route('/tailwind-v4-test')
        def tailwind_v4_test():
            return render_template('tailwind-v4-test.html')

        @app.route('/rules/<int:rule_id>/toggle', methods=['POST'])
        def toggle_rule(rule_id):
            # ... toggle logic ...
            return toast_response(f'Rule {rule_id} enabled', 'success')
    """
    response = make_response('', status_code)
    response.headers['X-Toast-Message'] = message
    response.headers['X-Toast-Type'] = toast_type
    response.headers['X-Toast-Duration'] = str(duration)
    return response


def redirect_with_toast(location: str, message: str, toast_type: str = 'info', duration: int = 5000):
    """
    Create a redirect response with toast notification headers.

    Combines Flask's redirect() with toast headers for HTMX or standard redirects.

    Args:
        location: URL to redirect to (use url_for() for route names)
        message: Toast message text
        toast_type: Toast type ('success', 'error', 'warning', 'info')
        duration: Auto-dismiss duration in milliseconds (default: 5000)

    Returns:
        Flask redirect response with toast headers

    Example:
        return redirect_with_toast(
            url_for('rules_list'),
            'Rule created successfully',
            'success'
        )
    """
    from flask import redirect
    response = make_response(redirect(location))
    response.headers['X-Toast-Message'] = message
    response.headers['X-Toast-Type'] = toast_type
    response.headers['X-Toast-Duration'] = str(duration)
    return response


# Time-boxing limits (from workflow/type_validators.py)
TASK_TYPE_MAX_HOURS = {
    TaskType.IMPLEMENTATION: 4.0,
    TaskType.TESTING: 6.0,
    TaskType.DESIGN: 8.0,
    TaskType.BUGFIX: 2.0,
    TaskType.REFACTORING: 6.0,
    TaskType.DOCUMENTATION: 4.0,
    TaskType.DEPLOYMENT: 4.0,
    TaskType.REVIEW: 2.0,
    TaskType.ANALYSIS: 8.0,
    TaskType.SIMPLE: 1.0,
}


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.

    Args:
        size_bytes: File size in bytes

    Returns:
        Human-readable size string (e.g., "15.2 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

# Register the format_file_size filter
app.jinja_env.filters['format_file_size'] = format_file_size


def get_database_service() -> DatabaseService:
    """
    Get DatabaseService instance with automatic database detection.

    Detection Priority:
    1. Environment variable agentpm.db_PATH (explicit override)
    2. Current directory .agentpm/data/agentpm.db (project context)
    3. Parent directories (walk up to find APM project)
    4. Home directory ~/.agentpm/agentpm.db (global fallback)

    Returns:
        DatabaseService configured with detected AIPM database path
    """
    # 1. Check environment variable (explicit override)
    if 'agentpm.db_PATH' in os.environ:
        return DatabaseService(os.environ['agentpm.db_PATH'])

    # 2. Check current directory for project database
    current_dir = Path.cwd()
    project_db = current_dir / '.agentpm' / 'data' / 'agentpm.db'
    if project_db.exists():
        return DatabaseService(str(project_db))

    # 3. Walk up parent directories to find APM project
    search_dir = current_dir
    for _ in range(10):  # Limit search depth to prevent infinite loops
        candidate_db = search_dir / '.agentpm' / 'data' / 'agentpm.db'
        if candidate_db.exists():
            return DatabaseService(str(candidate_db))

        # Move to parent directory
        parent = search_dir.parent
        if parent == search_dir:  # Reached filesystem root
            break
        search_dir = parent

    # 4. Fall back to global database
    return DatabaseService('~/.agentpm/agentpm.db')


def calculate_status_distribution(
    items: List[Any],
    total: int
) -> List[StatusDistribution]:
    """
    Calculate status distribution from list of items.

    Args:
        items: List of Task or WorkItem models
        total: Total count for percentage calculation

    Returns:
        List of StatusDistribution models
    """
    if total == 0:
        return []

    counter = Counter(item.status.value for item in items)

    return [
        StatusDistribution(
            status=status,
            count=count,
            percentage=round((count / total) * 100, 1)
        )
        for status, count in counter.most_common()
    ]


def calculate_type_distribution(
    items: List[Any],
    total: int
) -> List[TypeDistribution]:
    """
    Calculate type distribution from list of items.

    Args:
        items: List of Task or WorkItem models
        total: Total count for percentage calculation

    Returns:
        List of TypeDistribution models
    """
    if total == 0:
        return []

    counter = Counter(item.type.value for item in items)

    return [
        TypeDistribution(
            type=type_,
            count=count,
            percentage=round((count / total) * 100, 1)
        )
        for type_, count in counter.most_common()
    ]


def calculate_time_boxing_metrics(tasks: List[Task]) -> TimeBoxingMetrics:
    """
    Calculate time-boxing compliance metrics.

    Checks each task against TaskType-specific hour limits.

    Args:
        tasks: List of Task models

    Returns:
        TimeBoxingMetrics with compliance data
    """
    total = len(tasks)
    violations = []

    for task in tasks:
        if task.effort_hours is None:
            continue

        max_hours = TASK_TYPE_MAX_HOURS.get(task.type)
        if max_hours and task.effort_hours > max_hours:
            violations.append({
                'task_id': task.id,
                'task_name': task.name,
                'task_type': task.type.value,
                'effort_hours': task.effort_hours,
                'max_hours': max_hours,
                'overage': round(task.effort_hours - max_hours, 1)
            })

    compliant = total - len(violations)
    compliance_rate = (compliant / total * 100) if total > 0 else 100.0

    return TimeBoxingMetrics(
        total_tasks=total,
        compliant_tasks=compliant,
        non_compliant_tasks=len(violations),
        compliance_rate=round(compliance_rate, 1),
        violations=violations
    )


# ========================================
# Blueprint Registration - New Modular Structure
# ========================================

# Import consolidated blueprint structure
from .blueprints import (
    dashboard_bp,
    ideas_bp,
    idea_elements_bp,
    work_items_bp,
    tasks_bp,
    context_bp,
    documents_bp,
    agents_bp,
    rules_bp,
    system_bp,
    search_bp
)

# Register consolidated blueprints (30+ routes total)
app.register_blueprint(dashboard_bp)
app.register_blueprint(ideas_bp)
app.register_blueprint(idea_elements_bp)
app.register_blueprint(work_items_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(context_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(agents_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(system_bp)
app.register_blueprint(search_bp)

# Legacy blueprints have been archived - using only new modular structure


# ========================================
# WebSocket Integration (WI-125)
# ========================================
# IMPORTANT: Initialize WebSocket AFTER blueprint imports to avoid circular imports
# Routes may import from app.py, so we must complete all app setup first

# WebSocket functionality has been archived - using simple HTTP-only structure


if __name__ == '__main__':
    # Run the Flask app directly
    port = int(os.environ.get('FLASK_PORT', 5002))
    app.run(debug=True, host='127.0.0.1', port=port)
