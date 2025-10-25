"""
Projects Blueprint - Project Management and CRUD Operations

Handles:
- /projects - List all projects
- /projects/<id> - Get project details
- /projects/<id>/edit - Edit project form
- /projects/<id>/settings - Project settings
- /projects/<id>/analytics - Project analytics
- /projects/<id>/context - Project context (6W)
- /projects/<id>/actions/update - Update project (PUT)
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods
from ...core.database.methods import contexts as context_methods
from ...core.database.methods import sessions as session_methods
from ...core.database.enums import ProjectStatus, ProjectType, DevelopmentPhilosophy, TaskStatus, EntityType

# Import helper functions from app
from ..app import get_database_service, calculate_status_distribution, calculate_time_boxing_metrics

projects_bp = Blueprint('projects', __name__)


# ========================================
# Pydantic Models for View Data
# ========================================

class ProjectDetailView(BaseModel):
    """Complete project detail view with all fields"""
    project: Any  # Project model
    work_items: List[Any]
    tasks: List[Any]
    agents: List[Any]
    rules: List[Any]
    recent_sessions: List[Any]
    project_context: Optional[Any]
    
    # Analytics
    total_work_items: int
    total_tasks: int
    total_agents: int
    total_rules: int
    total_sessions: int
    
    # Distributions
    work_item_status_dist: List[Any]
    task_status_dist: List[Any]
    time_boxing_metrics: Any
    
    # Project metadata
    pm_philosophy: str
    project_type: str
    tech_stack: List[str]
    detected_frameworks: List[str]
    business_domain: Optional[str]
    business_description: Optional[str]
    team: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Quality indicators
    context_quality: Dict[str, Any]
    project_health: Dict[str, Any]


class ProjectSettingsView(BaseModel):
    """Project settings view"""
    project: Any
    available_philosophies: List[str]
    available_types: List[str]
    current_settings: Dict[str, Any]
    validation_errors: List[str]


class ProjectAnalyticsView(BaseModel):
    """Project analytics view"""
    project: Any
    
    # Time-based analytics
    work_items_over_time: Dict[str, List[Any]]
    tasks_over_time: Dict[str, List[Any]]
    sessions_over_time: Dict[str, List[Any]]
    
    # Performance metrics
    average_task_duration: float
    time_boxing_compliance: float
    context_freshness: float
    
    # Quality metrics
    work_item_completion_rate: float
    task_success_rate: float
    agent_utilization: float


# ========================================
# Helper Functions
# ========================================

def _get_project_analytics(db, project_id: int) -> Dict[str, Any]:
    """Get project analytics data"""
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
    task_success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    time_boxing_metrics = calculate_time_boxing_metrics(tasks)
    average_duration = 0.0  # TODO: Calculate from task completion times
    
    return {
        'total_work_items': len(work_items),
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'task_success_rate': round(task_success_rate, 1),
        'time_boxing_compliance': time_boxing_metrics.compliance_rate,
        'average_task_duration': average_duration
    }


def _get_project_health(db, project_id: int) -> Dict[str, Any]:
    """Get project health indicators"""
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=project_id
    )
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_sessions = session_methods.get_sessions_by_date_range(
        db,
        project_id=project_id,
        start=start_date,
        end=end_date
    )[:10]  # Limit to 10
    
    context_quality = 'high' if project_context and (project_context.confidence_score or 0) > 0.8 else 'medium' if project_context else 'low'
    recent_activity = len(recent_sessions) > 0
    context_freshness = _calculate_context_freshness(project_context)
    
    return {
        'context_quality': context_quality,
        'recent_activity': recent_activity,
        'context_freshness': context_freshness,
        'overall_health': 'healthy' if context_quality == 'high' and recent_activity else 'warning' if context_quality == 'medium' else 'critical'
    }


def _calculate_context_freshness(context) -> str:
    """Calculate context freshness"""
    if not context or not context.updated_at:
        return 'stale'
    
    days_old = (datetime.now() - context.updated_at).days
    if days_old <= 1:
        return 'fresh'
    elif days_old <= 7:
        return 'recent'
    elif days_old <= 30:
        return 'stale'
    else:
        return 'very_stale'


# ========================================
# Routes
# ========================================

@projects_bp.route('/projects')
def projects_list():
    """List all projects."""
    db = get_database_service()
    all_projects = project_methods.list_projects(db)

    projects_data = []
    for project in all_projects:
        # Get counts for this project
        work_items = wi_methods.list_work_items(db, project_id=project.id)
        total_work_items = len(work_items)

        # Count all tasks across work items
        total_tasks = 0
        for wi in work_items:
            tasks = task_methods.list_tasks(db, work_item_id=wi.id)
            total_tasks += len(tasks)

        # Count agents
        agents = agent_methods.list_agents(db, project_id=project.id)
        total_agents = len(agents)

        # Count rules
        rules = rule_methods.list_rules(db, project_id=project.id)
        total_rules = len(rules)

        projects_data.append({
            'project': project,
            'total_work_items': total_work_items,
            'total_tasks': total_tasks,
            'total_agents': total_agents,
            'total_rules': total_rules
        })

    return render_template('projects/list.html', projects=projects_data)


@projects_bp.route('/projects/<int:project_id>')
def project_detail(project_id: int):
    """Get project details."""
    db = get_database_service()
    
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    # Get related data
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    
    agents = agent_methods.list_agents(db, project_id=project_id)
    rules = rule_methods.list_rules(db, project_id=project_id)
    
    # Get recent sessions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_sessions = session_methods.get_sessions_by_date_range(
        db,
        project_id=project_id,
        start=start_date,
        end=end_date
    )[:10]  # Limit to 10
    
    # Get project context
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=project_id
    )
    
    # Calculate distributions
    work_item_status_dist = calculate_status_distribution(work_items, len(work_items))
    task_status_dist = calculate_status_distribution(tasks, len(tasks))
    time_boxing_metrics = calculate_time_boxing_metrics(tasks)
    
    # Get analytics and health
    analytics = _get_project_analytics(db, project_id)
    project_health = _get_project_health(db, project_id)
    
    # Context quality
    context_quality = {
        'has_context': project_context is not None,
        'confidence_score': project_context.confidence_score if project_context else 0.0,
        'confidence_band': project_context.confidence_band.value if project_context and project_context.confidence_band else 'unknown',
        'freshness': _calculate_context_freshness(project_context),
        'last_updated': project_context.updated_at if project_context else None
    }
    
    view = ProjectDetailView(
        project=project,
        work_items=work_items,
        tasks=tasks,
        agents=agents,
        rules=rules,
        recent_sessions=recent_sessions,
        project_context=project_context,
        
        # Analytics
        total_work_items=analytics['total_work_items'],
        total_tasks=analytics['total_tasks'],
        total_agents=len(agents),
        total_rules=len(rules),
        total_sessions=len(recent_sessions),
        
        # Distributions
        work_item_status_dist=work_item_status_dist,
        task_status_dist=task_status_dist,
        time_boxing_metrics=time_boxing_metrics,
        
        # Project metadata
        pm_philosophy='unknown',  # Not stored in Project model
        project_type=project.project_type.value if project.project_type else 'unknown',
        tech_stack=project.tech_stack or [],
        detected_frameworks=project.detected_frameworks or [],
        business_domain=project.business_domain,
        business_description=project.business_description,
        team=project.team,
        
        # Timestamps
        created_at=project.created_at or datetime.now(),
        updated_at=project.updated_at or datetime.now(),
        
        # Quality indicators
        context_quality=context_quality,
        project_health=project_health
    )
    
    # Prepare chart data for Chart.js
    wi_status_labels = [dist.status for dist in work_item_status_dist]
    wi_status_data = [dist.count for dist in work_item_status_dist]

    task_status_labels = [dist.status for dist in task_status_dist]
    task_status_data = [dist.count for dist in task_status_dist]

    compliance_rate = time_boxing_metrics.compliance_rate

    return render_template(
        'projects/detail.html',
        detail=view,
        wi_status_labels=wi_status_labels,
        wi_status_data=wi_status_data,
        task_status_labels=task_status_labels,
        task_status_data=task_status_data,
        compliance_rate=compliance_rate
    )


@projects_bp.route('/projects/<int:project_id>/edit')
def project_edit(project_id: int):
    """Edit project form."""
    db = get_database_service()
    project = project_methods.get_project(db, project_id)
    
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    return render_template('projects/edit.html', project=project)


@projects_bp.route('/projects/<int:project_id>/settings')
def project_settings(project_id: int):
    """Project settings view."""
    db = get_database_service()
    
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    # Available options
    available_philosophies = [phil.value for phil in DevelopmentPhilosophy]
    available_types = [ptype.value for ptype in ProjectType]
    
    # Current settings
    current_settings = {
        'pm_philosophy': None,  # Not stored in Project model
        'project_type': project.project_type.value if project.project_type else None,
        'business_domain': project.business_domain,
        'business_description': project.business_description,
        'team': project.team,
        'tech_stack': project.tech_stack or [],
        'detected_frameworks': project.detected_frameworks or []
    }
    
    view = ProjectSettingsView(
        project=project,
        available_philosophies=available_philosophies,
        available_types=available_types,
        current_settings=current_settings,
        validation_errors=[]
    )
    
    return render_template('project_settings.html', view=view)


@projects_bp.route('/projects/<int:project_id>/analytics')
def project_analytics(project_id: int):
    """Project analytics view."""
    db = get_database_service()
    
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    # Get analytics data
    analytics = _get_project_analytics(db, project_id)
    
    # Time-based data (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get work items over time
    work_items = wi_methods.list_work_items(db, project_id=project_id)
    work_items_over_time = {
        'dates': [],
        'created': [],
        'completed': []
    }
    
    # Get tasks over time
    tasks = []
    for wi in work_items:
        tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))
    
    tasks_over_time = {
        'dates': [],
        'created': [],
        'completed': []
    }
    
    # Get sessions over time
    try:
        sessions = session_methods.get_sessions_by_date_range(
            db,
            project_id,
            start_date,
            end_date
        )
    except Exception:
        sessions = []
    
    sessions_over_time = {
        'dates': [],
        'sessions': [],
        'duration': []
    }
    
    view = ProjectAnalyticsView(
        project=project,
        work_items_over_time=work_items_over_time,
        tasks_over_time=tasks_over_time,
        sessions_over_time=sessions_over_time,
        average_task_duration=analytics['average_task_duration'],
        time_boxing_compliance=analytics['time_boxing_compliance'],
        context_freshness=0.0,  # TODO: Calculate from context data
        work_item_completion_rate=analytics['task_success_rate'],
        task_success_rate=analytics['task_success_rate'],
        agent_utilization=0.0  # TODO: Calculate agent utilization
    )
    
    return render_template('projects/analytics.html', view=view)


@projects_bp.route('/projects/<int:project_id>/context')
def project_context(project_id: int):
    """Project context view - 6W framework and project intelligence."""
    db = get_database_service()

    # Get project
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")

    # Get context using context methods
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
        delta = datetime.now() - context.updated_at
        freshness_days = delta.days

    # Create view model
    from ..app import ProjectContextView
    view = ProjectContextView(
        project=project,
        context=context,
        has_context=has_context,
        confidence_score=confidence_score,
        confidence_band=confidence_band,
        freshness_days=freshness_days
    )

    return render_template('project_context.html', view=view)


@projects_bp.route('/projects/<int:project_id>/actions/update', methods=['PUT', 'POST'])
def project_update(project_id: int):
    """Update project settings."""
    db = get_database_service()
    
    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")
    
    # Get form data
    pm_philosophy = request.form.get('pm_philosophy')
    project_type = request.form.get('project_type')
    business_domain = request.form.get('business_domain')
    business_description = request.form.get('business_description')
    team = request.form.get('team')
    
    # Update project
    try:
        # TODO: Implement project update logic
        # This would use the project methods to update the project
        
        return redirect(url_for('projects.project_detail', project_id=project_id))
    except Exception as e:
        # Handle validation errors
        return redirect(url_for('projects.project_settings', project_id=project_id, error=str(e)))
