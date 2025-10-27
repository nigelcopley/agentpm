"""
Work Items Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for work items including:
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
from typing import Optional, List, Dict, Any

from flask import request, jsonify, flash, redirect, url_for, Response

from ....core.database.methods import work_items
from ....core.database.models import WorkItem
from ....core.database.enums import WorkItemType, WorkItemStatus
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_work_item():
    """Create a new work item."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'name': 'Work item name is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('work_items.work_items_list'))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        work_item_type = request.form.get('type', 'feature')
        priority = int(request.form.get('priority', 3))
        project_id = int(request.form.get('project_id', 1))
        parent_work_item_id = request.form.get('parent_work_item_id')
        parent_work_item_id = int(parent_work_item_id) if parent_work_item_id else None
        
        # Create work item
        work_item = WorkItem(
            name=name,
            description=description if description else None,
            type=WorkItemType(work_item_type),
            priority=priority,
            project_id=project_id,
            parent_work_item_id=parent_work_item_id,
            status=WorkItemStatus.DRAFT
        )
        
        created_work_item = work_items.create_work_item(db, work_item)
        
        flash(f'Work item "{created_work_item.name}" created successfully', 'success')
        return redirect(url_for('work_items.work_item_detail', work_item_id=created_work_item.id))
        
    except Exception as e:
        return handle_error(e, 'Error creating work item', url_for('work_items.work_items_list'))

def update_work_item(work_item_id: int):
    """Update an existing work item"""
    try:
        db = get_database_service()
        from ....core.database.methods import work_items
        from ....core.database.enums import WorkItemType
        
        work_item = safe_get_entity(work_items.get_work_item, db, work_item_id, "Work Item")
        if not work_item:
            flash('Work item not found', 'error')
            return redirect(url_for('work_items.work_items_list'))
        
        # Validate required fields
        required_fields = {
            'name': 'Work item name is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('work_items.edit_work_item', work_item_id=work_item_id))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        work_item_type = request.form.get('type', 'feature')
        priority = int(request.form.get('priority', 3))
        project_id = int(request.form.get('project_id', 1))
        parent_work_item_id = request.form.get('parent_work_item_id')
        parent_work_item_id = int(parent_work_item_id) if parent_work_item_id else None
        
        # Update work item using the correct method signature
        updated_work_item = work_items.update_work_item(db, work_item_id,
                                                        name=name,
                                                        description=description if description else None,
                                                        type=WorkItemType(work_item_type),
                                                        priority=priority,
                                                        project_id=project_id,
                                                        parent_work_item_id=parent_work_item_id)
        
        flash(f'Work item "{updated_work_item.name}" updated successfully', 'success')
        return redirect(url_for('work_items.work_item_detail', work_item_id=updated_work_item.id))
        
    except Exception as e:
        return handle_error(e, 'Error updating work item', url_for('work_items.edit_work_item', work_item_id=work_item_id))

def delete_work_item(work_item_id: int):
    """Delete a work item"""
    try:
        db = get_database_service()
        from ....core.database.methods import work_items
        
        work_item = safe_get_entity(work_items.get_work_item, db, work_item_id, "Work Item")
        if not work_item:
            flash('Work item not found', 'error')
            return redirect(url_for('work_items.work_items_list'))
        
        work_item_name = work_item.name
        work_items.delete_work_item(db, work_item_id)
        
        flash(f'Work item "{work_item_name}" deleted successfully', 'success')
        return redirect(url_for('work_items.work_items_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting work item', url_for('work_items.work_item_detail', work_item_id=work_item_id))

def update_work_item_status(work_item_id: int):
    """Update work item status via AJAX"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify(create_error_response('Status is required', 400))
        
        db = get_database_service()
        from ....core.database.methods import work_items
        from ....core.database.enums import WorkItemStatus
        
        work_item = safe_get_entity(work_items.get_work_item, db, work_item_id, "Work Item")
        if not work_item:
            return jsonify(create_error_response('Work item not found', 404))
        
        # Validate status
        try:
            new_status_enum = WorkItemStatus(new_status)
        except ValueError:
            return jsonify(create_error_response('Invalid status', 400))
        
        # Update status
        work_item.status = new_status_enum
        work_item.updated_at = datetime.now()
        
        updated_work_item = work_items.update_work_item(db, work_item)
        
        return jsonify(create_success_response(f'Work item status updated to {new_status}', {
            'status': new_status,
            'work_item_id': work_item_id
        }))
        
    except Exception as e:
        logger.error(f"Error updating work item status {work_item_id}: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def bulk_update_work_items():
    """Bulk update work items"""
    try:
        data = request.get_json()
        work_item_ids = data.get('work_item_ids', [])
        updates = data.get('updates', {})
        
        if not work_item_ids:
            return jsonify(create_error_response('No work items selected', 400))
        
        db = get_database_service()
        from ....core.database.methods import work_items
        from ....core.database.enums import WorkItemStatus, WorkItemType
        
        updated_count = 0
        errors = []
        
        for work_item_id in work_item_ids:
            try:
                work_item = work_items.get_work_item(db, work_item_id)
                if not work_item:
                    errors.append(f"Work item {work_item_id} not found")
                    continue
                
                # Apply updates
                if 'status' in updates:
                    try:
                        work_item.status = WorkItemStatus(updates['status'])
                    except ValueError:
                        errors.append(f"Invalid status for work item {work_item_id}")
                        continue
                
                if 'type' in updates:
                    try:
                        work_item.type = WorkItemType(updates['type'])
                    except ValueError:
                        errors.append(f"Invalid type for work item {work_item_id}")
                        continue
                
                if 'priority' in updates:
                    work_item.priority = int(updates['priority'])
                
                work_item.updated_at = datetime.now()
                work_items.update_work_item(db, work_item)
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Error updating work item {work_item_id}: {str(e)}")
        
        if errors:
            return jsonify(create_error_response(f"Updated {updated_count} work items, {len(errors)} errors", 400, {'errors': errors}))
        
        return jsonify(create_success_response(f'Successfully updated {updated_count} work items', {
            'updated_count': updated_count
        }))
        
    except Exception as e:
        logger.error(f"Error in bulk update work items: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def bulk_delete_work_items():
    """Bulk delete work items"""
    try:
        data = request.get_json()
        work_item_ids = data.get('work_item_ids', [])
        
        if not work_item_ids:
            return jsonify(create_error_response('No work items selected', 400))
        
        db = get_database_service()
        from ....core.database.methods import work_items
        
        deleted_count = 0
        errors = []
        
        for work_item_id in work_item_ids:
            try:
                work_item = work_items.get_work_item(db, work_item_id)
                if not work_item:
                    errors.append(f"Work item {work_item_id} not found")
                    continue
                
                work_items.delete_work_item(db, work_item_id)
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"Error deleting work item {work_item_id}: {str(e)}")
        
        if errors:
            return jsonify(create_error_response(f"Deleted {deleted_count} work items, {len(errors)} errors", 400, {'errors': errors}))
        
        return jsonify(create_success_response(f'Successfully deleted {deleted_count} work items', {
            'deleted_count': deleted_count
        }))
        
    except Exception as e:
        logger.error(f"Error in bulk delete work items: {e}")
        return jsonify(create_error_response('Internal server error', 500))

def export_work_items():
    """Export work items to CSV"""
    try:
        db = get_database_service()
        from ....core.database.methods import work_items, projects
        
        # Get all work items
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        work_items_list = work_items.list_work_items(db, project_id=project_id) or []
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Description', 'Type', 'Status', 'Priority', 'Project ID', 'Parent Work Item ID', 'Created At', 'Updated At'])
        
        # Write data
        for work_item in work_items_list:
            writer.writerow([
                work_item.id,
                work_item.name,
                work_item.description or '',
                work_item.type.value if work_item.type else '',
                work_item.status.value if work_item.status else '',
                work_item.priority,
                work_item.project_id,
                work_item.parent_work_item_id or '',
                work_item.created_at.isoformat() if work_item.created_at else '',
                work_item.updated_at.isoformat() if work_item.updated_at else ''
            ])
        
        # Prepare response
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        # Create response
        from flask import Response
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=work_items_export.csv'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting work items: {e}")
        flash(f"Error exporting work items: {str(e)}", 'error')
        return redirect(url_for('work_items.work_items_list'))
