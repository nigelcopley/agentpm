"""
Tasks Blueprint for APM (Agent Project Manager) Web Application

Comprehensive tasks management functionality with CRUD operations.
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for, jsonify, flash
import logging
from datetime import datetime

def _is_htmx_request():
    """Check if request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'

# Create tasks blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

logger = logging.getLogger(__name__)

def get_database_service():
    """Get database service instance with robust path resolution"""
    from ...core.database.service import DatabaseService
    import os
    
    # Try different database paths
    db_paths = [
        '.agentpm/data/agentpm.db',
        '../.agentpm/data/agentpm.db',
        '../../.agentpm/data/agentpm.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            return DatabaseService(db_path)
    
    # If no database found, return service with default path
    return DatabaseService('.agentpm/data/agentpm.db')

@tasks_bp.route('/')
def tasks_list():
    """Tasks list view with comprehensive metrics, filtering, and search"""
    db = get_database_service()
    
    # Get database methods
    from ...core.database.methods import tasks, work_items, projects
    from ...core.database.enums import TaskStatus, TaskType
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    work_item_filter = request.args.get('work_item', '')
    assigned_filter = request.args.get('assigned', '')
    sort_by = request.args.get('sort', 'updated_desc')
    
    # Get all tasks
    tasks_list = tasks.list_tasks(db) or []
    
    # Get work items for filtering
    work_items_list = work_items.list_work_items(db) or []
    
    # Apply filters
    filtered_tasks = tasks_list
    
    # Search filter
    if search_query:
        filtered_tasks = [
            task for task in filtered_tasks
            if search_query.lower() in (task.name or '').lower() or 
               search_query.lower() in (task.description or '').lower()
        ]
    
    # Status filter
    if status_filter:
        filtered_tasks = [
            task for task in filtered_tasks
            if task.status and task.status.value == status_filter
        ]
    
    # Type filter
    if type_filter:
        filtered_tasks = [
            task for task in filtered_tasks
            if task.type and task.type.value == type_filter
        ]
    
    # Work item filter
    if work_item_filter:
        try:
            work_item_id = int(work_item_filter)
            filtered_tasks = [
                task for task in filtered_tasks
                if task.work_item_id == work_item_id
            ]
        except ValueError:
            pass
    
    # Assigned filter
    if assigned_filter:
        filtered_tasks = [
            task for task in filtered_tasks
            if task.assigned_to and assigned_filter.lower() in task.assigned_to.lower()
        ]
    
    # Apply sorting
    if sort_by == 'name_asc':
        filtered_tasks.sort(key=lambda x: (x.name or '').lower())
    elif sort_by == 'name_desc':
        filtered_tasks.sort(key=lambda x: (x.name or '').lower(), reverse=True)
    elif sort_by == 'status_asc':
        filtered_tasks.sort(key=lambda x: x.status.value if x.status else '')
    elif sort_by == 'status_desc':
        filtered_tasks.sort(key=lambda x: x.status.value if x.status else '', reverse=True)
    elif sort_by == 'type_asc':
        filtered_tasks.sort(key=lambda x: x.type.value if x.type else '')
    elif sort_by == 'type_desc':
        filtered_tasks.sort(key=lambda x: x.type.value if x.type else '', reverse=True)
    elif sort_by == 'priority_asc':
        filtered_tasks.sort(key=lambda x: x.priority or 0)
    elif sort_by == 'priority_desc':
        filtered_tasks.sort(key=lambda x: x.priority or 0, reverse=True)
    elif sort_by == 'effort_asc':
        filtered_tasks.sort(key=lambda x: x.effort_hours or 0)
    elif sort_by == 'effort_desc':
        filtered_tasks.sort(key=lambda x: x.effort_hours or 0, reverse=True)
    elif sort_by == 'created_asc':
        filtered_tasks.sort(key=lambda x: x.created_at or datetime.min)
    elif sort_by == 'created_desc':
        filtered_tasks.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    else:  # updated_desc (default)
        filtered_tasks.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
    
    # Calculate comprehensive metrics for the sidebar
    metrics = {
        # Basic counts
        'total_tasks': len(tasks_list),
        
        # Status-based counts
        'draft_tasks': len([task for task in tasks_list if task.status and task.status.value == 'draft']),
        'ready_tasks': len([task for task in tasks_list if task.status and task.status.value == 'ready']),
        'active_tasks': len([task for task in tasks_list if task.status and task.status.value == 'active']),
        'in_progress_tasks': len([task for task in tasks_list if task.status and task.status.value == 'in_progress']),
        'review_tasks': len([task for task in tasks_list if task.status and task.status.value == 'review']),
        'blocked_tasks': len([task for task in tasks_list if task.status and task.status.value == 'blocked']),
        'done_tasks': len([task for task in tasks_list if task.status and task.status.value == 'done']),
        'cancelled_tasks': len([task for task in tasks_list if task.status and task.status.value == 'cancelled']),
        
        # Type-based counts
        'implementation_tasks': len([task for task in tasks_list if task.type and task.type.value == 'implementation']),
        'testing_tasks': len([task for task in tasks_list if task.type and task.type.value == 'testing']),
        'design_tasks': len([task for task in tasks_list if task.type and task.type.value == 'design']),
        'bugfix_tasks': len([task for task in tasks_list if task.type and task.type.value == 'bugfix']),
        'refactoring_tasks': len([task for task in tasks_list if task.type and task.type.value == 'refactoring']),
        'documentation_tasks': len([task for task in tasks_list if task.type and task.type.value == 'documentation']),
        'deployment_tasks': len([task for task in tasks_list if task.type and task.type.value == 'deployment']),
        'analysis_tasks': len([task for task in tasks_list if task.type and task.type.value == 'analysis']),
        'simple_tasks': len([task for task in tasks_list if task.type and task.type.value == 'simple']),
        
        # Priority-based counts
        'priority_1_tasks': len([task for task in tasks_list if task.priority == 1]),
        'priority_2_tasks': len([task for task in tasks_list if task.priority == 2]),
        'priority_3_tasks': len([task for task in tasks_list if task.priority == 3]),
        'priority_4_tasks': len([task for task in tasks_list if task.priority == 4]),
        'priority_5_tasks': len([task for task in tasks_list if task.priority == 5]),
        
        # Effort statistics
        'total_estimated_hours': sum(task.effort_hours or 0 for task in tasks_list),
        'tasks_with_effort': len([task for task in tasks_list if task.effort_hours]),
        'tasks_without_effort': len([task for task in tasks_list if not task.effort_hours]),
    }
    
    # Get available filter options
    filter_options = {
        'statuses': [{'value': status.value, 'label': status.value.replace('_', ' ').title()} 
                    for status in TaskStatus],
        'types': [{'value': type_.value, 'label': type_.value.replace('_', ' ').title()} 
                 for type_ in TaskType],
        'work_items': [{'value': str(wi.id), 'label': wi.name} for wi in work_items_list],
        'priorities': [{'value': str(i), 'label': f'Priority {i}'} for i in range(1, 6)],
        'sort_options': [
            {'value': 'updated_desc', 'label': 'Last Updated (Newest)'},
            {'value': 'updated_asc', 'label': 'Last Updated (Oldest)'},
            {'value': 'created_desc', 'label': 'Created (Newest)'},
            {'value': 'created_asc', 'label': 'Created (Oldest)'},
            {'value': 'name_asc', 'label': 'Name (A-Z)'},
            {'value': 'name_desc', 'label': 'Name (Z-A)'},
            {'value': 'status_asc', 'label': 'Status (A-Z)'},
            {'value': 'status_desc', 'label': 'Status (Z-A)'},
            {'value': 'type_asc', 'label': 'Type (A-Z)'},
            {'value': 'type_desc', 'label': 'Type (Z-A)'},
            {'value': 'priority_asc', 'label': 'Priority (Low to High)'},
            {'value': 'priority_desc', 'label': 'Priority (High to Low)'},
            {'value': 'effort_asc', 'label': 'Effort (Low to High)'},
            {'value': 'effort_desc', 'label': 'Effort (High to Low)'},
        ]
    }
    
    # Check if this is an HTMX request for dynamic filtering
    if _is_htmx_request():
        # Return only the content that should be updated
        return render_template('tasks/partials/tasks_content.html', 
                             tasks=filtered_tasks,
                             work_items=work_items_list,
                             metrics=metrics,
                             filter_options=filter_options,
                             current_filters={
                                 'search': search_query,
                                 'status': status_filter,
                                 'type': type_filter,
                                 'work_item': work_item_filter,
                                 'assigned': assigned_filter,
                                 'sort': sort_by
                             })
    
    # Return full page for regular requests
    return render_template('tasks/list.html', 
                         tasks=filtered_tasks,
                         work_items=work_items_list,
                         metrics=metrics,
                         filter_options=filter_options,
                         current_filters={
                             'search': search_query,
                             'status': status_filter,
                             'type': type_filter,
                             'work_item': work_item_filter,
                             'assigned': assigned_filter,
                             'sort': sort_by
                         })

@tasks_bp.route('/<int:task_id>')
def task_detail(task_id: int):
    """
    Comprehensive task detail view.
    
    Shows all task information in a single view:
    - Basic information (name, description, status, type, effort)
    - Work item context
    - Dependencies and blockers
    - Timeline and history
    - Quality metadata
    - Agent assignments
    """
    # Fetch task data
    db = get_database_service()
    from ...core.database.methods import tasks, work_items, projects, dependencies, events
    
    task = tasks.get_task(db, task_id)
    
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # Get related work item
    work_item = work_items.get_work_item(db, task.work_item_id) if task.work_item_id else None
    
    # Get project information
    project = None
    if work_item:
        projects_list = projects.list_projects(db) or []
        project = next((p for p in projects_list if p.id == work_item.project_id), None)
    
    # Get task dependencies
    task_dependencies = []
    try:
        task_dependencies = dependencies.get_task_dependencies(db, task_id)
    except Exception:
        pass  # Dependencies might not be implemented yet
    
    # Get task blockers
    task_blockers = []
    try:
        task_blockers = dependencies.get_task_blockers(db, task_id)
    except Exception:
        pass  # Blockers might not be implemented yet
    
    # Get task events/timeline
    task_events = []
    try:
        task_events = events.get_events_for_task(db, task_id)
    except Exception:
        pass  # Events might not be implemented yet
    
    # Calculate task statistics
    task_stats = {
        'is_active': task.is_active(),
        'is_blocked': task.is_blocked(),
        'is_complete': task.is_complete(),
        'can_start': task.can_start(),
        'days_since_created': (datetime.now() - task.created_at).days if task.created_at else None,
        'days_since_started': (datetime.now() - task.started_at).days if task.started_at else None,
        'days_since_completed': (datetime.now() - task.completed_at).days if task.completed_at else None,
        'has_dependencies': len(task_dependencies) > 0,
        'has_blockers': len(task_blockers) > 0,
        'has_events': len(task_events) > 0,
    }
    
    return render_template('tasks/detail.html', 
                         task=task,
                         task_id=task_id,
                         work_item=work_item,
                         project=project,
                         task_dependencies=task_dependencies,
                         task_blockers=task_blockers,
                         task_events=task_events,
                         task_stats=task_stats)

@tasks_bp.route('/create', methods=['GET', 'POST'])
def create_task():
    """Create a new task"""
    if request.method == 'GET':
        # Show create form
        db = get_database_service()
        from ...core.database.methods import work_items, agents
        from ...core.database.enums import TaskType, TaskStatus
        
        work_items_list = work_items.list_work_items(db) or []
        
        # Get project ID for agents
        from ...core.database.methods import projects
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get active agents for assignment dropdown
        agents_list = agents.list_agents(db, project_id=project_id, active_only=True) or []
        
        return render_template('tasks/create.html',
                             work_items=work_items_list,
                             agents=agents_list,
                             task_types=TaskType,
                             task_statuses=TaskStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            db = get_database_service()
            from ...core.database.methods import tasks
            from ...core.database.models import Task
            from ...core.database.enums import TaskType, TaskStatus
            
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            task_type = request.form.get('type', 'implementation')
            effort_hours = request.form.get('effort_hours')
            effort_hours = float(effort_hours) if effort_hours else None
            priority = int(request.form.get('priority', 3))
            assigned_to = request.form.get('assigned_to', '').strip()
            work_item_id = int(request.form.get('work_item_id', 1))
            due_date = request.form.get('due_date')
            due_date = datetime.fromisoformat(due_date) if due_date else None
            
            # Validate required fields
            if not name:
                flash('Task name is required', 'error')
                return redirect(url_for('tasks.create_task'))
            
            if not work_item_id:
                flash('Work item is required', 'error')
                return redirect(url_for('tasks.create_task'))
            
            # Create task
            task = Task(
                name=name,
                description=description if description else None,
                type=TaskType(task_type),
                effort_hours=effort_hours,
                priority=priority,
                assigned_to=assigned_to if assigned_to else None,
                work_item_id=work_item_id,
                due_date=due_date,
                status=TaskStatus.DRAFT
            )
            
            created_task = tasks.create_task(db, task)
            
            flash(f'Task "{created_task.name}" created successfully', 'success')
            return redirect(url_for('tasks.task_detail', task_id=created_task.id))
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            flash(f'Error creating task: {str(e)}', 'error')
            return redirect(url_for('tasks.create_task'))

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id: int):
    """Edit an existing task"""
    db = get_database_service()
    from ...core.database.methods import tasks, work_items
    from ...core.database.enums import TaskType, TaskStatus
    
    task = tasks.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    if request.method == 'GET':
        # Show edit form
        work_items_list = work_items.list_work_items(db) or []
        
        return render_template('tasks/edit.html',
                             task=task,
                             work_items=work_items_list,
                             task_types=TaskType,
                             task_statuses=TaskStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            task_type = request.form.get('type', 'implementation')
            effort_hours = request.form.get('effort_hours')
            effort_hours = float(effort_hours) if effort_hours else None
            priority = int(request.form.get('priority', 3))
            assigned_to = request.form.get('assigned_to', '').strip()
            work_item_id = int(request.form.get('work_item_id', 1))
            status = request.form.get('status', 'draft')
            due_date = request.form.get('due_date')
            due_date = datetime.fromisoformat(due_date) if due_date else None
            blocked_reason = request.form.get('blocked_reason', '').strip()
            
            # Validate required fields
            if not name:
                flash('Task name is required', 'error')
                return redirect(url_for('tasks.edit_task', task_id=task_id))
            
            if not work_item_id:
                flash('Work item is required', 'error')
                return redirect(url_for('tasks.edit_task', task_id=task_id))
            
            # Update task
            task.name = name
            task.description = description if description else None
            task.type = TaskType(task_type)
            task.effort_hours = effort_hours
            task.priority = priority
            task.assigned_to = assigned_to if assigned_to else None
            task.work_item_id = work_item_id
            task.status = TaskStatus(status)
            task.due_date = due_date
            task.blocked_reason = blocked_reason if blocked_reason else None
            
            # Update timestamps based on status changes
            if status == 'in_progress' and not task.started_at:
                task.started_at = datetime.now()
            elif status in ['done', 'cancelled'] and not task.completed_at:
                task.completed_at = datetime.now()
            
            updated_task = tasks.update_task(db, task)
            
            flash(f'Task "{updated_task.name}" updated successfully', 'success')
            return redirect(url_for('tasks.task_detail', task_id=updated_task.id))
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            flash(f'Error updating task: {str(e)}', 'error')
            return redirect(url_for('tasks.edit_task', task_id=task_id))

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id: int):
    """Delete a task"""
    try:
        db = get_database_service()
        from ...core.database.methods import tasks
        
        task = tasks.get_task(db, task_id)
        if not task:
            abort(404, description=f"Task {task_id} not found")
        
        tasks.delete_task(db, task_id)
        
        flash(f'Task "{task.name}" deleted successfully', 'success')
        return redirect(url_for('tasks.tasks_list'))
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        flash(f'Error deleting task: {str(e)}', 'error')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

@tasks_bp.route('/<int:task_id>/update-status', methods=['POST'])
def update_task_status(task_id: int):
    """Update task status via AJAX"""
    try:
        db = get_database_service()
        from ...core.database.methods import tasks
        from ...core.database.enums import TaskStatus
        
        task = tasks.get_task(db, task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        new_status = request.json.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        try:
            task.status = TaskStatus(new_status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update timestamps based on status changes
        if new_status == 'in_progress' and not task.started_at:
            task.started_at = datetime.now()
        elif new_status in ['done', 'cancelled'] and not task.completed_at:
            task.completed_at = datetime.now()
        
        updated_task = tasks.update_task(db, task)
        
        return jsonify({
            'success': True,
            'status': updated_task.status.value,
            'message': f'Status updated to {updated_task.status.value}'
        })
        
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        return jsonify({'error': str(e)}), 500
