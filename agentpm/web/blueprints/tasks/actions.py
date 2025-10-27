"""
Tasks Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for tasks including:
- Create, Read, Update, Delete operations
- Status updates and transitions
- Bulk operations
- Export functionality
"""

import csv
import io
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from flask import request, jsonify, flash, redirect, url_for, Response

from ....core.database.methods import tasks
from ....core.database.models import Task
from ....core.database.enums import TaskStatus
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_task():
    """Create a new task."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'name': 'Task name is required',
            'work_item_id': 'Work item is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('tasks.tasks_list'))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        work_item_id = int(request.form.get('work_item_id'))
        assigned_to = request.form.get('assigned_to', '').strip()
        priority = int(request.form.get('priority', 3))
        estimated_hours = request.form.get('estimated_hours')
        estimated_hours = float(estimated_hours) if estimated_hours else None
        
        # Create task
        task = Task(
            name=name,
            description=description if description else None,
            work_item_id=work_item_id,
            assigned_to=assigned_to if assigned_to else None,
            priority=priority,
            estimated_hours=estimated_hours,
            status=TaskStatus.PENDING
        )
        
        created_task = tasks.create_task(db, task)
        
        flash(f'Task "{created_task.name}" created successfully', 'success')
        return redirect(url_for('tasks.task_detail', task_id=created_task.id))
        
    except Exception as e:
        return handle_error(e, 'Error creating task', url_for('tasks.tasks_list'))

def update_task(task_id: int):
    """Update an existing task."""
    try:
        db = get_database_service()
        
        task = safe_get_entity(tasks.get_task, db, task_id, "Task")
        if not task:
            flash('Task not found', 'error')
            return redirect(url_for('tasks.tasks_list'))
        
        # Validate required fields
        required_fields = {
            'name': 'Task name is required',
            'work_item_id': 'Work item is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('tasks.edit_task', task_id=task_id))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        work_item_id = int(request.form.get('work_item_id'))
        assigned_to = request.form.get('assigned_to', '').strip()
        priority = int(request.form.get('priority', 3))
        estimated_hours = request.form.get('estimated_hours')
        estimated_hours = float(estimated_hours) if estimated_hours else None
        
        # Update task using the correct method signature
        updated_task = tasks.update_task(db, task_id, 
                                        name=name,
                                        description=description if description else None,
                                        work_item_id=work_item_id,
                                        assigned_to=assigned_to if assigned_to else None,
                                        priority=priority,
                                        estimated_hours=estimated_hours)
        
        flash(f'Task "{updated_task.name}" updated successfully', 'success')
        return redirect(url_for('tasks.task_detail', task_id=updated_task.id))
        
    except Exception as e:
        return handle_error(e, 'Error updating task', url_for('tasks.edit_task', task_id=task_id))

def delete_task(task_id: int):
    """Delete a task."""
    try:
        db = get_database_service()
        
        task = safe_get_entity(tasks.get_task, db, task_id, "Task")
        if not task:
            flash('Task not found', 'error')
            return redirect(url_for('tasks.tasks_list'))
        
        task_name = task.name
        tasks.delete_task(db, task_id)
        
        flash(f'Task "{task_name}" deleted successfully', 'success')
        return redirect(url_for('tasks.tasks_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting task', url_for('tasks.task_detail', task_id=task_id))

def update_task_status(task_id: int):
    """Update task status via AJAX."""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify(create_error_response('Status is required', 400))
        
        db = get_database_service()
        
        task = safe_get_entity(tasks.get_task, db, task_id, "Task")
        if not task:
            return jsonify(create_error_response('Task not found', 404))
        
        # Validate status
        try:
            new_status_enum = TaskStatus(new_status)
        except ValueError:
            return jsonify(create_error_response('Invalid status', 400))
        
        # Update status
        task.status = new_status_enum
        task.updated_at = datetime.now()
        
        updated_task = tasks.update_task(db, task)
        
        return jsonify(create_success_response(f'Task status updated to {new_status}', {
            'status': new_status,
            'task_id': task_id
        }))
        
    except Exception as e:
        logger.error(f"Error updating task status {task_id}: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def bulk_update_tasks():
    """Bulk update tasks."""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        updates = data.get('updates', {})
        
        if not task_ids:
            return jsonify(create_error_response('No tasks selected', 400))
        
        db = get_database_service()
        
        updated_count = 0
        errors = []
        
        for task_id in task_ids:
            try:
                task = tasks.get_task(db, task_id)
                if not task:
                    errors.append(f"Task {task_id} not found")
                    continue
                
                # Apply updates
                if 'status' in updates:
                    try:
                        task.status = TaskStatus(updates['status'])
                    except ValueError:
                        errors.append(f"Invalid status for task {task_id}")
                        continue
                
                if 'priority' in updates:
                    task.priority = int(updates['priority'])
                
                if 'assigned_to' in updates:
                    task.assigned_to = updates['assigned_to']
                
                task.updated_at = datetime.now()
                tasks.update_task(db, task)
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Error updating task {task_id}: {str(e)}")
        
        if errors:
            return jsonify(create_error_response(f"Updated {updated_count} tasks, {len(errors)} errors", 400, {'errors': errors}))
        
        return jsonify(create_success_response(f'Successfully updated {updated_count} tasks', {
            'updated_count': updated_count
        }))
        
    except Exception as e:
        logger.error(f"Error in bulk update tasks: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def bulk_delete_tasks():
    """Bulk delete tasks."""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify(create_error_response('No tasks selected', 400))
        
        db = get_database_service()
        
        deleted_count = 0
        errors = []
        
        for task_id in task_ids:
            try:
                task = tasks.get_task(db, task_id)
                if not task:
                    errors.append(f"Task {task_id} not found")
                    continue
                
                tasks.delete_task(db, task_id)
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"Error deleting task {task_id}: {str(e)}")
        
        if errors:
            return jsonify(create_error_response(f"Deleted {deleted_count} tasks, {len(errors)} errors", 400, {'errors': errors}))
        
        return jsonify(create_success_response(f'Successfully deleted {deleted_count} tasks', {
            'deleted_count': deleted_count
        }))
        
    except Exception as e:
        logger.error(f"Error in bulk delete tasks: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def export_tasks():
    """Export tasks to CSV."""
    try:
        db = get_database_service()
        
        # Get all tasks
        tasks_list = tasks.list_tasks(db) or []
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Description', 'Status', 'Priority', 'Assigned To', 'Work Item ID', 'Estimated Hours', 'Created At', 'Updated At'])
        
        # Write data
        for task in tasks_list:
            writer.writerow([
                task.id,
                task.name,
                task.description or '',
                task.status.value if task.status else '',
                task.priority,
                task.assigned_to or '',
                task.work_item_id,
                task.estimated_hours or '',
                task.created_at.isoformat() if task.created_at else '',
                task.updated_at.isoformat() if task.updated_at else ''
            ])
        
        # Prepare response
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        # Create response
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=tasks_export.csv'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting tasks: {e}")
        flash(f"Error exporting tasks: {str(e)}", 'error')
        return redirect(url_for('tasks.tasks_list'))
