"""
Main Blueprint - Dashboard and Project Overview Routes

Handles:
- Dashboard route (/)
- Project detail view
- Project context view
- Test routes (dev only)
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
    toast_response,
    ProjectDetail,
    ProjectContextView
)

main_bp = Blueprint('main', __name__)


def _render_project_detail(db, project):
    project_id = project.id

    # ✅ Get work items using methods
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    total_work_items = len(work_items)

    # ✅ Get all tasks for this project
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    total_tasks = len(tasks)

    # ✅ Get agents (global, not project-specific in current schema)
    all_agents = agent_methods.list_agents(db)
    total_agents = len(all_agents)

    # ✅ Get rules for this project
    project_rules = rule_methods.list_rules(db, project_id=project_id)
    total_rules = len(project_rules)

    # ✅ Get comprehensive project context
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=project_id
    )

    # ✅ Get recent events and summaries for context
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

    # 🎨 Prepare chart data for Chart.js (Phase 4)

    # Work Item Status Chart (Donut)
    wi_status_labels = [dist.status for dist in work_item_status_dist]
    wi_status_data = [dist.count for dist in work_item_status_dist]

    # Task Status Chart (Donut)
    task_status_labels = [dist.status for dist in task_status_dist]
    task_status_data = [dist.count for dist in task_status_dist]

    # Time-Boxing Compliance Gauge
    compliance_rate = time_boxing_metrics.compliance_rate

    # Work Item Progress Chart (Horizontal Bar) - Top 10 by task count
    work_item_progress = []
    for wi in work_items[:10]:  # Limit to 10 for readability
        wi_tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        completed = sum(1 for t in wi_tasks if t.status == TaskStatus.DONE)
        total = len(wi_tasks)
        progress = (completed / total * 100) if total > 0 else 0
        work_item_progress.append({
            'name': wi.name[:30] + '...' if len(wi.name) > 30 else wi.name,  # Truncate long names
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


@main_bp.route('/')
def dashboard():
    """Display the primary project overview on the landing page."""
    db = get_database_service()
    projects = project_methods.list_projects(db)

    if not projects:
        return render_template('no_project.html')

    return _render_project_detail(db, projects[0])


@main_bp.route('/project/<int:project_id>')
def project_detail(project_id: int):
    """Preserve project detail route for direct linking."""
    db = get_database_service()
    project = project_methods.get_project(db, project_id)

    if not project:
        abort(404, description=f"Project {project_id} not found")

    return _render_project_detail(db, project)


@main_bp.route('/project/<int:project_id>/context')
def project_context(project_id: int):
    """
    Project context view - 6W framework and project intelligence.

    Displays comprehensive project context including:
    - 6W framework (WHO/WHAT/WHERE/WHEN/WHY/HOW)
    - Context metadata (confidence, freshness)

    Args:
        project_id: Project ID

    Returns:
        Rendered project context template
    """
    db = get_database_service()

    # Get project
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")

    # Get context using context methods (entity_type='project')
    context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=project_id
    )

    # Extract metadata if context exists
    has_context = context is not None
    confidence_score = context.confidence_score if context else None
    confidence_band = context.confidence_band.value if (context and context.confidence_band) else None

    # Calculate freshness (days since last update)
    freshness_days = None
    if context and context.updated_at:
        from datetime import datetime
        delta = datetime.now() - context.updated_at
        freshness_days = delta.days

    # Create view model
    view = ProjectContextView(
        project=project,
        context=context,
        has_context=has_context,
        confidence_score=confidence_score,
        confidence_band=confidence_band,
        freshness_days=freshness_days
    )

    return render_template('project_context.html', view=view)


@main_bp.route('/test-toasts')
def test_toasts():
    """
    Test route for toast notifications (dev only).

    Displays a simple page with buttons to test all 4 toast types
    and HTMX integration.

    Returns:
        Rendered test page with toast triggers
    """
    return render_template('test_toasts.html')


@main_bp.route('/test-toast/<toast_type>', methods=['POST'])
def trigger_test_toast(toast_type: str):
    """
    HTMX endpoint to trigger test toasts.

    Args:
        toast_type: Toast type ('success', 'error', 'warning', 'info')

    Returns:
        Empty response with toast headers
    """
    messages = {
        'success': '✅ Success! Operation completed successfully.',
        'error': '❌ Error! Something went wrong.',
        'warning': '⚠️ Warning! Please review this action.',
        'info': 'ℹ️ Info: This is an informational message.'
    }

    message = messages.get(toast_type, 'Test toast notification')
    return toast_response(message, toast_type)


@main_bp.route('/test/interactions')
def test_interactions():
    """
    Test route for enhanced interactions and micro-interactions (dev only).
    
    Returns:
        Test page demonstrating all enhanced UX features
    """
    return render_template('test_interactions.html')
