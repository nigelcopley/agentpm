"""
Tasks List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for tasks including:
- Task listing with filtering and search
- Bulk operations (update, delete)
- Export functionality
"""

import csv
import io
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import render_template, request, jsonify, Response

from ....core.database.methods import tasks, work_items, projects
from ....core.database.enums import TaskStatus, TaskType
from ..utils import get_database_service, _is_htmx_request
from . import tasks_bp

logger = logging.getLogger(__name__)

@tasks_bp.route('/')
def tasks_list():
    """Tasks list view with comprehensive metrics, filtering, and search."""
    db = get_database_service()
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    work_item_filter = request.args.get('work_item', '')
    assigned_filter = request.args.get('assigned', '')
    priority_filter = request.args.get('priority', '')
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
    
    # Priority filter
    if priority_filter:
        try:
            priority = int(priority_filter)
            filtered_tasks = [
                task for task in filtered_tasks
                if task.priority == priority
            ]
        except ValueError:
            pass
    
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
                                 'priority': priority_filter,
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
                             'priority': priority_filter,
                             'sort': sort_by
                         })

@tasks_bp.route('/bulk-update', methods=['POST'])
def bulk_update_tasks():
    """Bulk update tasks via AJAX"""
    try:
        db = get_database_service()
        from ....core.database.enums import TaskStatus, TaskType
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task_ids = data.get('task_ids', [])
        if not task_ids:
            return jsonify({'error': 'No task IDs provided'}), 400
        
        updates = {}
        
        # Process update fields
        if 'status' in data and data['status']:
            try:
                updates['status'] = TaskStatus(data['status'])
            except ValueError:
                return jsonify({'error': 'Invalid status'}), 400
        
        if 'priority' in data and data['priority']:
            try:
                priority = int(data['priority'])
                if priority < 1 or priority > 5:
                    return jsonify({'error': 'Priority must be between 1 and 5'}), 400
                updates['priority'] = priority
            except ValueError:
                return jsonify({'error': 'Invalid priority'}), 400
        
        if 'assigned_to' in data:
            updates['assigned_to'] = data['assigned_to'] if data['assigned_to'] else None
        
        if 'description' in data:
            updates['description'] = data['description'] if data['description'] else None
        
        if not updates:
            return jsonify({'error': 'No update fields provided'}), 400
        
        # Perform bulk updates
        updated_count = 0
        errors = []
        
        for task_id in task_ids:
            try:
                task = tasks.get_task(db, task_id)
                if not task:
                    errors.append(f"Task {task_id} not found")
                    continue
                
                # Apply updates
                for field, value in updates.items():
                    setattr(task, field, value)
                
                # Update timestamps based on status changes
                if 'status' in updates:
                    if updates['status'].value == 'in_progress' and not task.started_at:
                        task.started_at = datetime.now()
                    elif updates['status'].value in ['done', 'cancelled'] and not task.completed_at:
                        task.completed_at = datetime.now()
                
                tasks.update_task(db, task)
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Task {task_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'total_count': len(task_ids),
            'errors': errors,
            'message': f'Successfully updated {updated_count} of {len(task_ids)} tasks'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_tasks():
    """Bulk delete tasks via AJAX"""
    try:
        db = get_database_service()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task_ids = data.get('task_ids', [])
        if not task_ids:
            return jsonify({'error': 'No task IDs provided'}), 400
        
        # Perform bulk deletes
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
                errors.append(f"Task {task_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'total_count': len(task_ids),
            'errors': errors,
            'message': f'Successfully deleted {deleted_count} of {len(task_ids)} tasks'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/export')
def export_tasks():
    """Export tasks to CSV or JSON"""
    try:
        db = get_database_service()
        
        # Get filter parameters (same as list view)
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        type_filter = request.args.get('type', '')
        work_item_filter = request.args.get('work_item', '')
        assigned_filter = request.args.get('assigned', '')
        sort_by = request.args.get('sort', 'updated_desc')
        
        # Get all tasks and apply filters (reuse logic from tasks_list)
        tasks_list = tasks.list_tasks(db) or []
        
        # Apply same filtering logic as in tasks_list
        filtered_tasks = tasks_list
        
        if search_query:
            filtered_tasks = [
                task for task in filtered_tasks
                if search_query.lower() in (task.name or '').lower() or 
                   search_query.lower() in (task.description or '').lower()
            ]
        
        if status_filter:
            filtered_tasks = [
                task for task in filtered_tasks
                if task.status and task.status.value == status_filter
            ]
        
        if type_filter:
            filtered_tasks = [
                task for task in filtered_tasks
                if task.type and task.type.value == type_filter
            ]
        
        if work_item_filter:
            try:
                work_item_id = int(work_item_filter)
                filtered_tasks = [
                    task for task in filtered_tasks
                    if task.work_item_id == work_item_id
                ]
            except ValueError:
                pass
        
        if assigned_filter:
            filtered_tasks = [
                task for task in filtered_tasks
                if task.assigned_to and assigned_filter.lower() in task.assigned_to.lower()
            ]
        
        # Apply sorting (same as in tasks_list)
        if sort_by == 'name_asc':
            filtered_tasks.sort(key=lambda x: (x.name or '').lower())
        elif sort_by == 'name_desc':
            filtered_tasks.sort(key=lambda x: (x.name or '').lower(), reverse=True)
        elif sort_by == 'status_asc':
            filtered_tasks.sort(key=lambda x: x.status.value if x.status else '')
        elif sort_by == 'status_desc':
            filtered_tasks.sort(key=lambda x: x.status.value if x.status else '', reverse=True)
        elif sort_by == 'priority_asc':
            filtered_tasks.sort(key=lambda x: x.priority or 0)
        elif sort_by == 'priority_desc':
            filtered_tasks.sort(key=lambda x: x.priority or 0, reverse=True)
        else:  # updated_desc (default)
            filtered_tasks.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
        
        # Get export format
        export_format = request.args.get('format', 'csv').lower()
        
        if export_format == 'json':
            # Export as JSON
            # Convert tasks to dictionaries
            tasks_data = []
            for task in filtered_tasks:
                task_dict = {
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'type': task.type.value if task.type else None,
                    'status': task.status.value if task.status else None,
                    'priority': task.priority,
                    'effort_hours': task.effort_hours,
                    'assigned_to': task.assigned_to,
                    'work_item_id': task.work_item_id,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                }
                tasks_data.append(task_dict)
            
            response = Response(
                json.dumps(tasks_data, indent=2),
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=tasks_export.json'}
            )
            return response
        
        else:  # CSV format
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Name', 'Description', 'Type', 'Status', 'Priority', 
                'Effort Hours', 'Assigned To', 'Work Item ID', 'Due Date',
                'Created At', 'Updated At', 'Started At', 'Completed At'
            ])
            
            # Write data
            for task in filtered_tasks:
                writer.writerow([
                    task.id,
                    task.name or '',
                    task.description or '',
                    task.type.value if task.type else '',
                    task.status.value if task.status else '',
                    task.priority or '',
                    task.effort_hours or '',
                    task.assigned_to or '',
                    task.work_item_id or '',
                    task.due_date.strftime('%Y-%m-%d %H:%M:%S') if task.due_date else '',
                    task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else '',
                    task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else '',
                    task.started_at.strftime('%Y-%m-%d %H:%M:%S') if task.started_at else '',
                    task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else '',
                ])
            
            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=tasks_export.csv'}
            )
            return response
        
    except Exception as e:
        logger.error(f"Error exporting tasks: {e}")
        return jsonify({'error': str(e)}), 500
