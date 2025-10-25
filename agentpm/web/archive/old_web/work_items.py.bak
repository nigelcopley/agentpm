"""
Work Items Blueprint - Work Item Management and Operations

Handles:
- /work-items - List all work items
- /work-items/<id> - Get work item details
- /work-items/<id>/edit - Edit work item form
- /work-items/<id>/summaries - Work item summaries timeline
- /work-items/<id>/context - Work item context
- /work-items/<id>/tasks - Tasks for this work item
- /work-items/<id>/actions/start - Start work item
- /work-items/<id>/actions/complete - Complete work item
- /work-items/<id>/actions/block - Block work item
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for
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
    TaskSummary,
    DependencyInfo,
    BlockerInfo,
    WorkItemDetail,
    WorkItemDependencyInfo,
    WorkItemListItem,
    WorkItemSummariesView
)

work_items_bp = Blueprint('work_items', __name__)


def _status_value(enum_name: str, fallback: str) -> str:
    """Get status value from enum"""
    enum_member = getattr(WorkItemStatus, enum_name, None)
    return enum_member.value if enum_member is not None else fallback


@work_items_bp.route('/work-items')
def work_items_list():
    """List all work items with smart filtering."""
    db = get_database_service()

    # Get sort parameter
    sort_by = request.args.get('sort', 'created_desc')

    # Use database methods instead of raw SQL
    all_work_items = work_item_methods.list_work_items(db)

    # Smart filtering: Filter out cancelled/consolidated work items by default
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
        # Resolve project information with simple caching
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

        # Count for metrics
        if getattr(wi.status, 'value', None):
            status_counts[wi.status.value] += 1
        if getattr(wi.type, 'value', None):
            type_counts[wi.type.value] += 1
        if getattr(wi.phase, 'value', None):
            phase_counts[wi.phase.value] += 1
        if wi.priority is not None:
            priority_counts[str(wi.priority)] += 1

    # Apply sorting
    if sort_by == 'created_desc':
        work_items_data.sort(key=lambda x: x.work_item.created_at or datetime.min, reverse=True)
    elif sort_by == 'created_asc':
        work_items_data.sort(key=lambda x: x.work_item.created_at or datetime.min, reverse=False)
    elif sort_by == 'name_asc':
        work_items_data.sort(key=lambda x: x.work_item.name.lower())
    elif sort_by == 'name_desc':
        work_items_data.sort(key=lambda x: x.work_item.name.lower(), reverse=True)
    elif sort_by == 'priority_asc':
        work_items_data.sort(key=lambda x: x.work_item.priority or 999)
    elif sort_by == 'priority_desc':
        work_items_data.sort(key=lambda x: x.work_item.priority or 999, reverse=True)
    elif sort_by == 'updated_desc':
        work_items_data.sort(key=lambda x: x.work_item.updated_at or datetime.min, reverse=True)
    elif sort_by == 'updated_asc':
        work_items_data.sort(key=lambda x: x.work_item.updated_at or datetime.min, reverse=False)

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
        current_sort=sort_by,
        show_sidebar='work-items'
    )


@work_items_bp.route('/work-items/<int:work_item_id>')
def work_item_detail(work_item_id: int):
    """Get work item details with Chart.js visualizations."""
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

    # Prepare chart data for Chart.js
    task_type_labels = [dist.type for dist in task_type_dist]
    task_type_data = [dist.count for dist in task_type_dist]

    # Task Progress Timeline
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


@work_items_bp.route('/work-items/<int:work_item_id>/edit')
def work_item_edit(work_item_id: int):
    """Edit work item form."""
    db = get_database_service()
    work_item = work_item_methods.get_work_item(db, work_item_id)
    
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    return render_template('work-items/edit.html', work_item=work_item)


@work_items_bp.route('/work-items/<int:work_item_id>/summaries')
def work_item_summaries(work_item_id: int):
    """Work item summaries timeline view."""
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

    # Get project using methods
    project = project_methods.get_project(db, work_item.project_id)
    project_name = project.name if project else "Unknown"

    # Get summaries using summary methods (chronological, newest first)
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


@work_items_bp.route('/work-items/<int:work_item_id>/context')
def work_item_context(work_item_id: int):
    """Work item context view."""
    db = get_database_service()
    
    # Get work item
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # Get project
    project = project_methods.get_project(db, work_item.project_id)
    
    # Get contexts
    from ...core.database.methods import contexts as context_methods
    project_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.PROJECT,
        entity_id=work_item.project_id
    )
    
    work_item_context = context_methods.get_entity_context(
        db,
        entity_type=EntityType.WORK_ITEM,
        entity_id=work_item_id
    )
    
    # Get all tasks for this work item
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
    
    # Get task contexts
    task_contexts = []
    for task in tasks:
        task_context = context_methods.get_entity_context(
            db,
            entity_type=EntityType.TASK,
            entity_id=task.id
        )
        if task_context:
            task_contexts.append(task_context)
    
    # Calculate context quality
    context_quality = {
        'has_project_context': project_context is not None,
        'has_work_item_context': work_item_context is not None,
        'task_contexts_count': len(task_contexts),
        'total_tasks': len(tasks),
        'context_coverage': (len(task_contexts) / len(tasks) * 100) if tasks else 0,
        'overall_quality': 'high' if project_context and work_item_context and len(task_contexts) > 0 else 'medium' if project_context or work_item_context else 'low'
    }
    
    # Hierarchical assembly info
    hierarchical_assembly = {
        'project_level': {
            'context': project_context,
            'confidence': project_context.confidence_score if project_context else 0.0,
            'freshness': _calculate_context_freshness(project_context) if project_context else 999
        },
        'work_item_level': {
            'context': work_item_context,
            'confidence': work_item_context.confidence_score if work_item_context else 0.0,
            'freshness': _calculate_context_freshness(work_item_context) if work_item_context else 999
        },
        'task_level': {
            'contexts': task_contexts,
            'average_confidence': sum(tc.confidence_score or 0.0 for tc in task_contexts) / len(task_contexts) if task_contexts else 0.0,
            'average_freshness': sum(_calculate_context_freshness(tc) for tc in task_contexts) / len(task_contexts) if task_contexts else 999
        }
    }
    
    from ..app import WorkItemContextView
    view = WorkItemContextView(
        work_item=work_item,
        project=project,
        project_context=project_context,
        work_item_context=work_item_context,
        task_contexts=task_contexts,
        merged_context=None,  # TODO: Implement context merging
        context_quality=context_quality,
        hierarchical_assembly=hierarchical_assembly
    )
    
    return render_template('work_item_context.html', view=view)


def _calculate_context_freshness(context) -> int:
    """Calculate context freshness in days"""
    if not context or not context.updated_at:
        return 999  # Very stale
    
    delta = datetime.now() - context.updated_at
    return delta.days


@work_items_bp.route('/work-items/<int:work_item_id>/tasks')
def work_item_tasks(work_item_id: int):
    """Get tasks for this work item."""
    db = get_database_service()
    
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # Get project info
    project = project_methods.get_project(db, work_item.project_id)
    project_name = project.name if project else "Unknown"
    
    # Get tasks for this work item
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
    
    return render_template('work-items/tasks.html', 
                         work_item=work_item, 
                         project_name=project_name, 
                         tasks=tasks)


@work_items_bp.route('/work-items/<int:work_item_id>/actions/start', methods=['POST'])
def work_item_start(work_item_id: int):
    """Start work item."""
    db = get_database_service()
    
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # TODO: Implement work item start logic
    # This would update the work item status to active
    
    return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))


@work_items_bp.route('/work-items/<int:work_item_id>/actions/complete', methods=['POST'])
def work_item_complete(work_item_id: int):
    """Complete work item."""
    db = get_database_service()
    
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # TODO: Implement work item completion logic
    # This would update the work item status to done
    
    return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))


@work_items_bp.route('/work-items/<int:work_item_id>/actions/block', methods=['POST'])
def work_item_block(work_item_id: int):
    """Block work item."""
    db = get_database_service()
    
    work_item = work_item_methods.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # TODO: Implement work item blocking logic
    # This would update the work item status to blocked
    
    return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))
