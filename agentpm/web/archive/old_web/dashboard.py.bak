"""
Dashboard Blueprint - Main Dashboard and Overview Pages

Handles:
- Main dashboard (/)
- Dashboard overview (/dashboard)
- Project overview (/overview)
"""

from flask import Blueprint, render_template, abort
from pathlib import Path

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods
from ...core.database.methods import contexts as context_methods
from ...core.database.enums import TaskStatus, EntityType

# Import helper functions and models from app
from ..app import (
    get_database_service,
    calculate_status_distribution,
    calculate_time_boxing_metrics,
    ProjectDetail
)

dashboard_bp = Blueprint('dashboard', __name__)


def _render_project_detail(db, project):
    """Render project detail view (shared with main blueprint)"""
    project_id = project.id

    # Get work items using methods
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    total_work_items = len(work_items)

    # Get all tasks for this project
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    total_tasks = len(tasks)

    # Get agents (global, not project-specific in current schema)
    all_agents = agent_methods.list_agents(db)
    total_agents = len(all_agents)

    # Get rules for this project
    project_rules = rule_methods.list_rules(db, project_id=project_id)
    total_rules = len(project_rules)

    # Get comprehensive project context
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=project_id
    )

    # Get recent events and summaries for context
    from ...core.database.methods import events as event_methods
    from ...core.database.methods import summaries as summary_methods
    from datetime import datetime, timedelta
    
    # Get recent events from the last 7 days
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        recent_events = event_methods.get_events_by_time_range(db, start_time, end_time)[:10]
    except (AttributeError, Exception):
        recent_events = []
    
    # Get recent summaries for the project
    try:
        recent_summaries = summary_methods.get_summaries_for_entity(
            db, 
            entity_type=EntityType.PROJECT, 
            entity_id=project_id, 
            limit=5
        )
    except (AttributeError, Exception):
        recent_summaries = []

    # Calculate distributions
    work_item_status_dist = calculate_status_distribution(work_items, len(work_items))
    task_status_dist = calculate_status_distribution(tasks, len(tasks))

    # Calculate time-boxing compliance
    time_boxing_metrics = calculate_time_boxing_metrics(tasks)

    detail = ProjectDetail(
        project=project,
        total_work_items=total_work_items,
        total_tasks=total_tasks,
        total_agents=total_agents,
        total_rules=total_rules,
        work_item_status_dist=work_item_status_dist,
        task_status_dist=task_status_dist,
        # Enhanced context data
        project_context=project_context,
        recent_events=recent_events,
        recent_summaries=recent_summaries
    )

    # Prepare chart data for Chart.js
    wi_status_labels = [dist.status for dist in work_item_status_dist]
    wi_status_data = [dist.count for dist in work_item_status_dist]

    task_status_labels = [dist.status for dist in task_status_dist]
    task_status_data = [dist.count for dist in task_status_dist]

    compliance_rate = time_boxing_metrics.compliance_rate

    # Work Item Progress Chart (Horizontal Bar) - Top 10 by task count
    work_item_progress = []
    for wi in work_items[:10]:  # Limit to 10 for readability
        wi_tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        completed = sum(1 for t in wi_tasks if t.status == TaskStatus.DONE)
        total = len(wi_tasks)
        progress = (completed / total * 100) if total > 0 else 0
        work_item_progress.append({
            'name': wi.name[:30] + '...' if len(wi.name) > 30 else wi.name,
            'progress': round(progress, 1),
            'status': wi.status.value
        })

    wi_progress_labels = [item['name'] for item in work_item_progress]
    wi_progress_data = [item['progress'] for item in work_item_progress]

    return render_template(
        'projects/detail.html',
        detail=detail,
        wi_status_labels=wi_status_labels,
        wi_status_data=wi_status_data,
        task_status_labels=task_status_labels,
        task_status_data=task_status_data,
        compliance_rate=compliance_rate,
        wi_progress_labels=wi_progress_labels,
        wi_progress_data=wi_progress_data
    )


@dashboard_bp.route('/')
def dashboard():
    """Display the primary project overview on the landing page."""
    db = get_database_service()
    projects = project_methods.list_projects(db)

    if not projects:
        return render_template('no_project.html')

    return _render_project_detail(db, projects[0])


@dashboard_bp.route('/dashboard')
def dashboard_explicit():
    """Explicit dashboard route."""
    return dashboard()


@dashboard_bp.route('/overview')
def overview():
    """Project overview page."""
    return dashboard()
