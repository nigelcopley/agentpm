"""
Tasks Blueprint - Task Management and Operations

Handles:
- /tasks - List all tasks
- /tasks/<id> - Get task details
- /tasks/<id>/edit - Edit task form
- /tasks/<id>/dependencies - Task dependencies
- /tasks/<id>/blockers - Task blockers
- /tasks/<id>/actions/assign - Assign task
- /tasks/<id>/actions/start - Start task
- /tasks/<id>/actions/complete - Complete task
- /tasks/<id>/actions/block - Block task
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for
from datetime import datetime

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as work_item_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import dependencies as dep_methods
from ...core.database.enums import TaskStatus

# Import helper functions and models from app
from ..app import (
    get_database_service,
    TASK_TYPE_MAX_HOURS,
    TaskSummary,
    DependencyInfo,
    BlockerInfo,
    TaskDetail,
    TaskListItem
)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks')
def tasks_list():
    """List all tasks."""
    db = get_database_service()

    # Get sort parameter
    sort_by = request.args.get('sort', 'created_desc')

    # Get all work items to iterate through their tasks
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

    # Apply sorting
    if sort_by == 'created_desc':
        tasks_data.sort(key=lambda x: x.task.created_at or datetime.min, reverse=True)
    elif sort_by == 'created_asc':
        tasks_data.sort(key=lambda x: x.task.created_at or datetime.min, reverse=False)
    elif sort_by == 'name_asc':
        tasks_data.sort(key=lambda x: x.task.name.lower())
    elif sort_by == 'name_desc':
        tasks_data.sort(key=lambda x: x.task.name.lower(), reverse=True)
    elif sort_by == 'priority_asc':
        tasks_data.sort(key=lambda x: x.task.priority or 999)
    elif sort_by == 'priority_desc':
        tasks_data.sort(key=lambda x: x.task.priority or 999, reverse=True)
    elif sort_by == 'effort_asc':
        tasks_data.sort(key=lambda x: x.task.effort_hours or 0)
    elif sort_by == 'effort_desc':
        tasks_data.sort(key=lambda x: x.task.effort_hours or 0, reverse=True)

    return render_template('tasks/list.html', tasks=tasks_data, current_sort=sort_by, show_sidebar='tasks')


@tasks_bp.route('/tasks/<int:task_id>')
def task_detail(task_id: int):
    """Get task details."""
    db = get_database_service()

    # Use database methods instead of raw SQL
    task = task_methods.get_task(db, task_id)

    if not task:
        abort(404, description=f"Task {task_id} not found")

    # Get work item and project using methods
    work_item = work_item_methods.get_work_item(db, task.work_item_id)
    work_item_name = work_item.name if work_item else "Unknown"

    project = None
    project_name = "Unknown"
    if work_item:
        project = project_methods.get_project(db, work_item.project_id)
        project_name = project.name if project else "Unknown"

    # Get dependencies using dependency methods
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

    # Get dependents using dependency methods
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

    # Get blockers using dependency methods
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


@tasks_bp.route('/tasks/<int:task_id>/edit')
def task_edit(task_id: int):
    """Edit task form."""
    db = get_database_service()
    task = task_methods.get_task(db, task_id)
    
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    return render_template('tasks/edit.html', task=task)


@tasks_bp.route('/tasks/<int:task_id>/dependencies')
def task_dependencies(task_id: int):
    """Get task dependencies."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # Get dependencies
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
    
    return render_template('tasks/dependencies.html', 
                         task=task, 
                         dependencies=dependencies)


@tasks_bp.route('/tasks/<int:task_id>/blockers')
def task_blockers(task_id: int):
    """Get task blockers."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # Get blockers
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
    
    return render_template('tasks/blockers.html', 
                         task=task, 
                         blockers=blockers)


@tasks_bp.route('/tasks/<int:task_id>/actions/assign', methods=['POST'])
def task_assign(task_id: int):
    """Assign task."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # TODO: Implement task assignment logic
    # This would update the task assigned_to field
    
    return redirect(url_for('tasks.task_detail', task_id=task_id))


@tasks_bp.route('/tasks/<int:task_id>/actions/start', methods=['POST'])
def task_start(task_id: int):
    """Start task."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # TODO: Implement task start logic
    # This would update the task status to active
    
    return redirect(url_for('tasks.task_detail', task_id=task_id))


@tasks_bp.route('/tasks/<int:task_id>/actions/complete', methods=['POST'])
def task_complete(task_id: int):
    """Complete task."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # TODO: Implement task completion logic
    # This would update the task status to done
    
    return redirect(url_for('tasks.task_detail', task_id=task_id))


@tasks_bp.route('/tasks/<int:task_id>/actions/block', methods=['POST'])
def task_block(task_id: int):
    """Block task."""
    db = get_database_service()
    
    task = task_methods.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # TODO: Implement task blocking logic
    # This would update the task status to blocked
    
    return redirect(url_for('tasks.task_detail', task_id=task_id))
