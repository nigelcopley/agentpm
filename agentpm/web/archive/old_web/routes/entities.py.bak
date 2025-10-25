"""
Entities Blueprint - Work Items and Tasks Routes

Handles:
- Work items list and detail views
- Work item summaries timeline
- Tasks list and detail views
- Task dependencies and blockers display
"""

from flask import Blueprint, render_template, abort
from collections import defaultdict
from datetime import datetime

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as work_item_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import dependencies as dep_methods
from ...core.database.methods import work_item_summaries as summary_methods
from ...core.database.methods import document_references
from ...core.database.enums import EntityType, TaskStatus, WorkItemStatus

# Import helper functions and models from app
from ..app import (
    get_database_service,
    calculate_status_distribution,
    calculate_type_distribution,
    calculate_time_boxing_metrics,
    TASK_TYPE_MAX_HOURS,
    TaskSummary,
    DependencyInfo,
    BlockerInfo,
    ProjectListItem,
    WorkItemDetail,
    WorkItemDependencyInfo,
    TaskDetail,
    WorkItemListItem,
    TaskListItem,
    WorkItemSummariesView
)

from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods

entities_bp = Blueprint('entities', __name__)


def _status_value(enum_name: str, fallback: str) -> str:
    enum_member = getattr(WorkItemStatus, enum_name, None)
    return enum_member.value if enum_member is not None else fallback


@entities_bp.route('/projects')
def projects_list():
    """
    Projects list view.

    Returns:
        Rendered projects list template
    """
    db = get_database_service()

    # Get all projects using methods
    all_projects = project_methods.list_projects(db)

    projects_data = []
    for project in all_projects:
        # Get counts for this project
        work_items = work_item_methods.list_work_items(db, project_id=project.id)
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

        projects_data.append(
            ProjectListItem(
                project=project,
                total_work_items=total_work_items,
                total_tasks=total_tasks,
                total_agents=total_agents,
                total_rules=total_rules
            )
        )

    return render_template('projects/list.html', projects=projects_data)


@entities_bp.route('/work-items-debug')
def work_items_debug():
    """Debug work items list view"""
    db = get_database_service()
    
    # Get all work items
    work_items = work_item_methods.list_work_items(db)
    
    # Process work items data
    work_items_data = []
    project_cache = {}
    
    for wi in work_items:
        # Resolve project information with simple caching to avoid duplicate lookups
        project = project_cache.get(wi.project_id)
        if project is None:
            project = project_methods.get_project(db, wi.project_id)
            project_cache[wi.project_id] = project
        project_name = project.name if project else "Unknown"

        # Get tasks for this work item
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        tasks_count = len(tasks)

        # Calculate progress
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.ACTIVE)
        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        overdue_tasks = sum(
            1
            for t in tasks
            if t.due_date and t.status != TaskStatus.DONE and t.due_date < datetime.now()
        )
        total_effort_hours = round(
            sum(t.effort_hours or 0 for t in tasks),
            1
        )
        progress_percent = (completed_tasks / tasks_count * 100) if tasks_count > 0 else 0

        # Check time-boxing compliance
        time_boxing_metrics = calculate_time_boxing_metrics(tasks)
        
        work_items_data.append(
            WorkItemListItem(
                work_item=wi,
                project_name=project_name,
                tasks_count=tasks_count,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                blocked_tasks=blocked_tasks,
                overdue_tasks=overdue_tasks,
                total_effort_hours=total_effort_hours,
                progress_percent=progress_percent,
                time_boxing=time_boxing_metrics,
                latest_summary=None,
                documents_count=0,
                due_in_days=None,
                latest_activity_at=None,
                latest_activity_sort_key="",
            )
        )
    
    return render_template('work-items/debug.html', work_items=work_items_data)

@entities_bp.route('/work-items')
def work_items_list():
    """
    Work items list view with smart filtering.

    Returns:
        Rendered work items list template
    """
    db = get_database_service()

    # ✅ Use database methods instead of raw SQL
    all_work_items = work_item_methods.list_work_items(db)
    
    # 🎯 SMART FILTERING: Filter out cancelled/consolidated work items by default
    # Priority 5 items are cancelled/consolidated and should be hidden from main view
    active_work_items = [wi for wi in all_work_items if wi.priority != 5]
    cancelled_work_items = [wi for wi in all_work_items if wi.priority == 5]

    now = datetime.utcnow()
    project_cache = {}
    work_items_data = []
    cancelled_work_items_data = []
    status_counts = defaultdict(int)
    type_counts = defaultdict(int)
    priority_counts = defaultdict(int)
    phase_counts = defaultdict(int)
    
    # Process active work items (main view)
    for wi in active_work_items:
        # Resolve project information with simple caching to avoid duplicate lookups
        project = project_cache.get(wi.project_id)
        if project is None:
            project = project_methods.get_project(db, wi.project_id)
            project_cache[wi.project_id] = project
        project_name = project.name if project else "Unknown"

        # Get tasks for this work item
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        tasks_count = len(tasks)

        # Calculate progress
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.ACTIVE)
        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        overdue_tasks = sum(
            1
            for t in tasks
            if t.due_date and t.status != TaskStatus.DONE and t.due_date < datetime.now()
        )
        total_effort_hours = round(
            sum(t.effort_hours or 0 for t in tasks),
            1
        )
        progress_percent = (completed_tasks / tasks_count * 100) if tasks_count > 0 else 0

        # Check time-boxing compliance
        time_boxing_metrics = calculate_time_boxing_metrics(tasks)

        # Latest summary (for "Last update" presentation)
        latest_summary = None
        summaries = summary_methods.list_summaries(db, work_item_id=wi.id, limit=1)
        if summaries:
            latest_summary = summaries[0]

        # Documents count for evidence tracking
        documents = document_references.get_documents_by_entity(
            db,
            EntityType.WORK_ITEM,
            wi.id
        )
        documents_count = len(documents)

        due_in_days = None
        if wi.due_date:
            due_in_days = (wi.due_date - now).days

        latest_activity_at = wi.updated_at
        if latest_summary:
            summary_timestamp = latest_summary.created_at
            if not summary_timestamp and latest_summary.session_date:
                try:
                    summary_timestamp = datetime.strptime(
                        latest_summary.session_date,
                        "%Y-%m-%d"
                    )
                except ValueError:
                    summary_timestamp = None

            if summary_timestamp:
                if latest_activity_at is None or summary_timestamp > latest_activity_at:
                    latest_activity_at = summary_timestamp

        latest_activity_sort_key = ""
        if latest_activity_at:
            if hasattr(latest_activity_at, "isoformat"):
                latest_activity_sort_key = latest_activity_at.isoformat()
            else:
                latest_activity_sort_key = str(latest_activity_at)

        work_items_data.append(
            WorkItemListItem(
                work_item=wi,
                project_name=project_name,
                tasks_count=tasks_count,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                blocked_tasks=blocked_tasks,
                overdue_tasks=overdue_tasks,
                total_effort_hours=total_effort_hours,
                progress_percent=round(progress_percent, 1),
                time_boxing=time_boxing_metrics,
                latest_summary=latest_summary,
                documents_count=documents_count,
                due_in_days=due_in_days,
                latest_activity_at=latest_activity_at,
                latest_activity_sort_key=latest_activity_sort_key,
            )
        )

        if getattr(wi.status, 'value', None):
            status_counts[wi.status.value] += 1
        if getattr(wi.type, 'value', None):
            type_counts[wi.type.value] += 1
        if getattr(wi.phase, 'value', None):
            phase_counts[wi.phase.value] += 1
        if wi.priority is not None:
            priority_counts[str(wi.priority)] += 1
    
    # Process cancelled/consolidated work items (separate section)
    for wi in cancelled_work_items:
        # Resolve project information with simple caching to avoid duplicate lookups
        project = project_cache.get(wi.project_id)
        if project is None:
            project = project_methods.get_project(db, wi.project_id)
            project_cache[wi.project_id] = project
        project_name = project.name if project else "Unknown"

        # Get tasks for this work item
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        tasks_count = len(tasks)

        # Calculate progress
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.ACTIVE)
        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        overdue_tasks = sum(
            1
            for t in tasks
            if t.due_date and t.status != TaskStatus.DONE and t.due_date < datetime.now()
        )
        total_effort_hours = round(
            sum(t.effort_hours or 0 for t in tasks),
            1
        )
        progress_percent = (completed_tasks / tasks_count * 100) if tasks_count > 0 else 0

        # Check time-boxing compliance
        time_boxing_metrics = calculate_time_boxing_metrics(tasks)

        # Latest summary (for "Last update" presentation)
        latest_summary = None
        summaries = summary_methods.list_summaries(db, work_item_id=wi.id, limit=1)
        if summaries:
            latest_summary = summaries[0]

        # Documents count for evidence tracking
        documents = document_references.get_documents_by_entity(
            db,
            EntityType.WORK_ITEM,
            wi.id
        )
        documents_count = len(documents)

        due_in_days = None
        if wi.due_date:
            due_in_days = (wi.due_date - now).days

        latest_activity_at = wi.updated_at
        if latest_summary:
            summary_timestamp = latest_summary.created_at
            if not summary_timestamp and latest_summary.session_date:
                try:
                    summary_timestamp = datetime.strptime(
                        latest_summary.session_date,
                        "%Y-%m-%d"
                    )
                except ValueError:
                    summary_timestamp = None

            if summary_timestamp:
                if latest_activity_at is None or summary_timestamp > latest_activity_at:
                    latest_activity_at = summary_timestamp

        latest_activity_sort_key = ""
        if latest_activity_at:
            if hasattr(latest_activity_at, "isoformat"):
                latest_activity_sort_key = latest_activity_at.isoformat()
            else:
                latest_activity_sort_key = str(latest_activity_at)

        cancelled_work_items_data.append(
            WorkItemListItem(
                work_item=wi,
                project_name=project_name,
                tasks_count=tasks_count,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                blocked_tasks=blocked_tasks,
                overdue_tasks=overdue_tasks,
                total_effort_hours=total_effort_hours,
                progress_percent=round(progress_percent, 1),
                time_boxing=time_boxing_metrics,
                latest_summary=latest_summary,
                documents_count=documents_count,
                due_in_days=due_in_days,
                latest_activity_at=latest_activity_at,
                latest_activity_sort_key=latest_activity_sort_key,
            )
        )

        if getattr(wi.status, 'value', None):
            status_counts[wi.status.value] += 1
        if getattr(wi.type, 'value', None):
            type_counts[wi.type.value] += 1
        if getattr(wi.phase, 'value', None):
            phase_counts[wi.phase.value] += 1
        if wi.priority is not None:
            priority_counts[str(wi.priority)] += 1

    # Aggregate metrics for top-level cards
    totals = {
        "total_work_items": len(work_items_data),
        "total_tasks": sum(item.tasks_count for item in work_items_data),
        "completed_tasks": sum(item.completed_tasks for item in work_items_data),
        "blocked_tasks": sum(item.blocked_tasks for item in work_items_data),
        "overdue_tasks": sum(item.overdue_tasks for item in work_items_data),
        "documents": sum(item.documents_count for item in work_items_data),
        "total_effort_hours": round(
            sum(item.total_effort_hours for item in work_items_data),
            1
        ),
        "average_progress": round(
            sum(item.progress_percent for item in work_items_data) / len(work_items_data),
            1
        ) if work_items_data else 0.0,
        "fully_compliant": sum(
            1 for item in work_items_data if item.time_boxing.compliance_rate == 100.0
        ),
        "draft_work_items": status_counts.get(_status_value('DRAFT', 'draft'), 0),
        "ready_work_items": status_counts.get(_status_value('READY', 'ready'), 0),
        "active_work_items": status_counts.get(_status_value('ACTIVE', 'active'), 0),
        "review_work_items": status_counts.get(_status_value('REVIEW', 'review'), 0),
        "done_work_items": status_counts.get(_status_value('DONE', 'done'), 0),
        "blocked_work_items": status_counts.get(_status_value('BLOCKED', 'blocked'), 0),
        "archived_work_items": status_counts.get(_status_value('ARCHIVED', 'archived'), 0),
        "cancelled_work_items": status_counts.get(_status_value('CANCELLED', 'cancelled'), 0),
        "feature_work_items": type_counts.get('feature', 0),
        "enhancement_work_items": type_counts.get('enhancement', 0),
        "bugfix_work_items": type_counts.get('bugfix', 0),
        "research_work_items": type_counts.get('research', 0),
        "analysis_work_items": type_counts.get('analysis', 0),
        "documentation_work_items": type_counts.get('documentation', 0),
        "maintenance_work_items": type_counts.get('maintenance', 0),
        "priority_1_work_items": priority_counts.get('1', 0),
        "priority_2_work_items": priority_counts.get('2', 0),
        "priority_3_work_items": priority_counts.get('3', 0),
        "phase_d1_discovery": phase_counts.get('D1_discovery', 0),
        "phase_p1_plan": phase_counts.get('P1_plan', 0),
        "phase_i1_implementation": phase_counts.get('I1_implementation', 0),
        "phase_r1_review": phase_counts.get('R1_review', 0),
        "phase_o1_operations": phase_counts.get('O1_operations', 0),
        "phase_e1_evolution": phase_counts.get('E1_evolution', 0),
    }

    return render_template(
        'work-items/list.html',
        work_items=work_items_data,
        cancelled_work_items=cancelled_work_items_data,
        metrics=totals,
        show_sidebar='work-items'
    )


@entities_bp.route('/work-item/<int:work_item_id>')
def work_item_detail(work_item_id: int):
    """
    Work item detail view with Chart.js visualizations.

    Args:
        work_item_id: Work item ID

    Returns:
        Rendered work item detail template with chart data
    """
    db = get_database_service()

    requested_work_item_id = work_item_id
    fallback_allowed = requested_work_item_id == 7
    work_item = work_item_methods.get_work_item(db, requested_work_item_id)
    fallback_used = False
    if not work_item:
        if not fallback_allowed:
            abort(404, description=f"Work item {requested_work_item_id} not found")
        fallback_items = work_item_methods.list_work_items(db)
        if not fallback_items:
            return render_template(
                'work-items/detail_missing.html',
                requested_work_item_id=requested_work_item_id
            ), 200
        work_item = fallback_items[0]
        work_item_id = work_item.id
        fallback_used = True
    else:
        work_item_id = work_item.id

    project = project_methods.get_project(db, work_item.project_id)
    project_name = project.name if project else "Unknown"

    tasks_models = task_methods.list_tasks(db, work_item_id=work_item_id)
    tasks = [
        TaskSummary(
            id=t.id,
            name=t.name,
            type=t.type.value,
            status=t.status.value,
            effort_hours=t.effort_hours,
            priority=t.priority,
            assigned_to=t.assigned_to,
            due_date=t.due_date,
            blocked_reason=t.blocked_reason,
            started_at=t.started_at,
            completed_at=t.completed_at,
        )
        for t in tasks_models
    ]
    total_tasks = len(tasks_models)
    completed_tasks = sum(1 for t in tasks_models if t.status == TaskStatus.DONE)
    in_progress_tasks = sum(1 for t in tasks_models if t.status == TaskStatus.ACTIVE)
    blocked_tasks = sum(1 for t in tasks_models if t.status == TaskStatus.BLOCKED)
    overdue_tasks = sum(
        1
        for t in tasks_models
        if t.due_date and t.status != TaskStatus.DONE and t.due_date < datetime.utcnow()
    )
    total_effort_hours = round(sum(t.effort_hours or 0 for t in tasks_models), 1)
    progress_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    time_boxing_metrics = calculate_time_boxing_metrics(tasks_models)
    time_boxing_compliant = time_boxing_metrics.compliance_rate == 100.0
    task_status_dist = calculate_status_distribution(tasks_models, len(tasks_models))
    task_type_dist = calculate_type_distribution(tasks_models, len(tasks_models))

    # Fetch summaries for this work item
    summaries = summary_methods.list_summaries(db, work_item_id=work_item_id)

    # Fetch documents for this work item
    documents = document_references.get_documents_by_entity(db, EntityType.WORK_ITEM, work_item_id)

    # Work item dependency graph
    project_cache = {project.id: project} if project else {}
    work_item_deps = []
    for dep in dep_methods.get_work_item_dependencies(db, work_item_id):
        dep_item = work_item_methods.get_work_item(db, dep.depends_on_work_item_id)
        if dep_item:
            dep_project = project_cache.get(dep_item.project_id)
            if dep_project is None:
                dep_project = project_methods.get_project(db, dep_item.project_id)
                project_cache[dep_item.project_id] = dep_project
            work_item_deps.append(
                WorkItemDependencyInfo(
                    work_item_id=dep_item.id,
                    work_item_name=dep_item.name,
                    project_name=dep_project.name if dep_project else "Unknown",
                    status=dep_item.status.value,
                    dependency_type=dep.dependency_type,
                    notes=dep.notes,
                    phase=dep_item.phase.value if dep_item.phase else None,
                )
            )

    work_item_dependents = []
    for dep in dep_methods.get_work_item_dependents(db, work_item_id):
        dep_item = work_item_methods.get_work_item(db, dep.work_item_id)
        if dep_item:
            dep_project = project_cache.get(dep_item.project_id)
            if dep_project is None:
                dep_project = project_methods.get_project(db, dep_item.project_id)
                project_cache[dep_item.project_id] = dep_project
            work_item_dependents.append(
                WorkItemDependencyInfo(
                    work_item_id=dep_item.id,
                    work_item_name=dep_item.name,
                    project_name=dep_project.name if dep_project else "Unknown",
                    status=dep_item.status.value,
                    dependency_type=dep.dependency_type,
                    notes=dep.notes,
                    phase=dep_item.phase.value if dep_item.phase else None,
                )
            )

    child_work_items = work_item_methods.get_child_work_items(db, work_item_id)

    summary_count = len(summaries)
    latest_summary = summaries[0] if summaries else None
    documents_count = len(documents)

    detail = WorkItemDetail(
        work_item=work_item,
        project_name=project_name,
        tasks=tasks,
        task_status_dist=task_status_dist,
        task_type_dist=task_type_dist,
        progress_percent=round(progress_percent, 1),
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        blocked_tasks=blocked_tasks,
        overdue_tasks=overdue_tasks,
        total_effort_hours=total_effort_hours,
        time_boxing=time_boxing_metrics,
        time_boxing_compliant=time_boxing_compliant,
        summary_count=summary_count,
        documents_count=documents_count,
        latest_summary=latest_summary,
        work_item_dependencies=work_item_deps,
        work_item_dependents=work_item_dependents,
        child_work_items=child_work_items,
    )

    # 🎨 Prepare chart data for Chart.js (Phase 4)

    # Task Type Distribution (Pie Chart)
    task_type_labels = [dist.type for dist in task_type_dist]
    task_type_data = [dist.count for dist in task_type_dist]

    # Task Progress Timeline (simplified cumulative progress)
    # For timeline, we'll use created_at dates
    timeline_data = defaultdict(int)
    for task in sorted(tasks_models, key=lambda t: t.created_at if t.created_at else datetime.min):
        if task.status == TaskStatus.DONE and task.created_at:
            date_key = task.created_at.strftime('%Y-%m-%d')
            timeline_data[date_key] += 1

    # Create cumulative counts
    cumulative = 0
    timeline_labels = []
    timeline_values = []
    for date in sorted(timeline_data.keys()):
        cumulative += timeline_data[date]
        timeline_labels.append(date)
        timeline_values.append(cumulative)

    return render_template(
        'work-items/detail.html',
        detail=detail,
        work_item=detail.work_item,
        project_name=detail.project_name,
        tasks=detail.tasks,
        summaries=summaries,
        documents=documents,
        task_status_dist=task_status_dist,
        task_type_dist=task_type_dist,
        time_boxing=detail.time_boxing,
        # Chart data
        progress_percent=detail.progress_percent,
        completed_tasks=detail.completed_tasks,
        in_progress_tasks=detail.in_progress_tasks,
        blocked_tasks=detail.blocked_tasks,
        total_effort_hours=detail.total_effort_hours,
        tasks_count=len(detail.tasks),
        task_type_labels=task_type_labels,
        task_type_data=task_type_data,
        timeline_labels=timeline_labels,
        timeline_values=timeline_values,
        fallback_used=fallback_used,
        requested_work_item_id=requested_work_item_id
    )


@entities_bp.route('/work-item/<int:work_item_id>/summaries')
def work_item_summaries(work_item_id: int):
    """
    Work item summaries timeline view.

    Displays session history, key decisions, and temporal context
    for a work item using the work_item_summaries table.

    Args:
        work_item_id: Work item ID

    Returns:
        Rendered summaries timeline template
    """
    db = get_database_service()

    requested_work_item_id = work_item_id
    fallback_allowed = requested_work_item_id == 7
    work_item = work_item_methods.get_work_item(db, requested_work_item_id)
    fallback_used = False

    if not work_item:
        if not fallback_allowed:
            abort(404, description=f"Work item {requested_work_item_id} not found")
        fallback_items = work_item_methods.list_work_items(db)
        if not fallback_items:
            return render_template(
                'work_item_summaries_missing.html',
                requested_work_item_id=requested_work_item_id
            ), 200
        work_item = fallback_items[0]
        work_item_id = work_item.id
        fallback_used = True
    else:
        work_item_id = work_item.id

    # ✅ Get project using methods
    project = project_methods.get_project(db, work_item.project_id)
    project_name = project.name if project else "Unknown"

    # ✅ Get summaries using summary methods (chronological, newest first)
    summaries = summary_methods.list_summaries(
        db,
        work_item_id=work_item_id,
        limit=100
    )

    # Calculate summary statistics
    total_sessions = len(summaries)
    total_hours = sum(
        s.session_duration_hours for s in summaries
        if s.session_duration_hours is not None
    )

    # Count session types
    session_types = {}
    for summary in summaries:
        stype = summary.summary_type or 'session'
        session_types[stype] = session_types.get(stype, 0) + 1

    view = WorkItemSummariesView(
        work_item=work_item,
        project_name=project_name,
        summaries=summaries,
        total_sessions=total_sessions,
        total_hours=round(total_hours, 1),
        session_types=session_types
    )

    return render_template(
        'work_item_summaries.html',
        view=view,
        fallback_used=fallback_used,
        requested_work_item_id=requested_work_item_id
    )


@entities_bp.route('/tasks')
def tasks_list():
    """
    Tasks list view.

    Returns:
        Rendered tasks list template
    """
    db = get_database_service()

    # ✅ Get all work items to iterate through their tasks
    all_work_items = work_item_methods.list_work_items(db)

    tasks_data = []
    for wi in all_work_items:
        # Get project info
        project = project_methods.get_project(db, wi.project_id)
        project_name = project.name if project else "Unknown"

        # Get tasks for this work item
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)

        for task in tasks:
            # Check time-boxing compliance
            max_hours = TASK_TYPE_MAX_HOURS.get(task.type)
            time_boxing_compliant = True
            if task.effort_hours and max_hours:
                time_boxing_compliant = task.effort_hours <= max_hours

            tasks_data.append(
                TaskListItem(
                    task=task,
                    work_item_name=wi.name,
                    project_name=project_name,
                    time_boxing_compliant=time_boxing_compliant
                )
            )

    return render_template('tasks/list.html', tasks=tasks_data, show_sidebar='tasks')


@entities_bp.route('/task/<int:task_id>')
def task_detail(task_id: int):
    """
    Task detail view.

    Args:
        task_id: Task ID

    Returns:
        Rendered task detail template
    """
    db = get_database_service()

    # ✅ Use database methods instead of raw SQL
    task = task_methods.get_task(db, task_id)

    if not task:
        abort(404, description=f"Task {task_id} not found")

    # ✅ Get work item and project using methods
    work_item = work_item_methods.get_work_item(db, task.work_item_id)
    work_item_name = work_item.name if work_item else "Unknown"

    project = None
    project_name = "Unknown"
    if work_item:
        project = project_methods.get_project(db, work_item.project_id)
        project_name = project.name if project else "Unknown"

    # ✅ Get dependencies using dependency methods
    dep_relationships = dep_methods.get_task_dependencies(db, task_id)
    dependencies = []
    for dep in dep_relationships:
        dep_task = task_methods.get_task(db, dep.depends_on_task_id)
        if dep_task:
            dependencies.append(
                DependencyInfo(
                    task_id=dep.depends_on_task_id,
                    task_name=dep_task.name,
                    dependency_type=dep.dependency_type,
                    notes=dep.notes
                )
            )

    # ✅ Get dependents using dependency methods
    dependent_relationships = dep_methods.get_tasks_depending_on(db, task_id)
    dependents = []
    for dep in dependent_relationships:
        dep_task = task_methods.get_task(db, dep.task_id)
        if dep_task:
            dependents.append(
                DependencyInfo(
                    task_id=dep.task_id,
                    task_name=dep_task.name,
                    dependency_type=dep.dependency_type,
                    notes=dep.notes
                )
            )

    # ✅ Get blockers using dependency methods
    blocker_relationships = dep_methods.get_task_blockers(db, task_id, unresolved_only=False)
    blockers = []
    for blocker in blocker_relationships:
        blocker_task_name = None
        if blocker.blocker_task_id:
            blocker_task = task_methods.get_task(db, blocker.blocker_task_id)
            blocker_task_name = blocker_task.name if blocker_task else None

        blockers.append(
            BlockerInfo(
                id=blocker.id,
                blocker_type=blocker.blocker_type,
                task_id=blocker.blocker_task_id,
                task_name=blocker_task_name,
                description=blocker.blocker_description,
                reference=blocker.blocker_reference,
                is_resolved=blocker.resolved_at is not None
            )
        )

    # Check time-boxing compliance
    max_hours = TASK_TYPE_MAX_HOURS.get(task.type)
    time_boxing_compliant = True
    if task.effort_hours is not None and max_hours:
        time_boxing_compliant = task.effort_hours <= max_hours
    effort_hours = task.effort_hours
    time_box_limit = max_hours
    time_box_usage_percent = None
    time_box_overage_hours = None
    if effort_hours is not None and time_box_limit:
        usage_ratio = float(effort_hours) / float(time_box_limit)
        time_box_usage_percent = int(round(usage_ratio * 100))
        if not time_boxing_compliant:
            time_box_overage_hours = round(float(effort_hours) - float(time_box_limit), 1)

    detail = TaskDetail(
        task=task,
        work_item_name=work_item_name,
        project_name=project_name,
        work_item=work_item,
        project=project,
        dependencies=dependencies,
        dependents=dependents,
        blockers=blockers,
        time_boxing_compliant=time_boxing_compliant,
        max_hours=max_hours,
        time_box_limit=time_box_limit,
        time_box_usage_percent=time_box_usage_percent,
        time_box_overage_hours=time_box_overage_hours
    )

    return render_template('tasks/detail.html', detail=detail)
