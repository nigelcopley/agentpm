"""
Work Items List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for work items including:
- Work items listing with filtering and search
- Bulk operations (update, delete)
- Export functionality
"""

from flask import render_template, request, jsonify, Response
from datetime import datetime
import logging
import csv
import json
import io

from . import work_items_bp
from ..utils import get_database_service, _is_htmx_request
from ...utils.pagination import paginate_items, get_pagination_from_request, get_query_params_from_request

# Core imports
from ....core.database.methods import projects, work_items, tasks
from ....core.database.enums import WorkItemStatus, WorkItemType, Phase

logger = logging.getLogger(__name__)

@work_items_bp.route('/')
def work_items_list():
    """Work items list view with comprehensive metrics, filtering, search, and pagination"""
    db = get_database_service()
    
    # Get pagination parameters
    page, per_page = get_pagination_from_request(request, default_per_page=20)
    
    # Get project ID for work items
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    priority_filter = request.args.get('priority', '')
    sort_by = request.args.get('sort', 'updated_desc')
    
    # Get work items and tasks
    work_items_list = work_items.list_work_items(db, project_id=project_id) or []
    tasks_list = tasks.list_tasks(db) or []
    
    # Apply filters
    filtered_work_items = work_items_list
    
    # Search filter
    if search_query:
        filtered_work_items = [
            wi for wi in filtered_work_items
            if search_query.lower() in (wi.name or '').lower() or 
               search_query.lower() in (wi.description or '').lower()
        ]
    
    # Status filter
    if status_filter:
        filtered_work_items = [
            wi for wi in filtered_work_items
            if wi.status and wi.status.value == status_filter
        ]
    
    # Type filter
    if type_filter:
        filtered_work_items = [
            wi for wi in filtered_work_items
            if wi.type and wi.type.value == type_filter
        ]
    
    # Priority filter
    if priority_filter:
        try:
            priority = int(priority_filter)
            filtered_work_items = [
                wi for wi in filtered_work_items
                if wi.priority == priority
            ]
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'name_asc':
        filtered_work_items.sort(key=lambda x: (x.name or '').lower())
    elif sort_by == 'name_desc':
        filtered_work_items.sort(key=lambda x: (x.name or '').lower(), reverse=True)
    elif sort_by == 'status_asc':
        filtered_work_items.sort(key=lambda x: x.status.value if x.status else '')
    elif sort_by == 'status_desc':
        filtered_work_items.sort(key=lambda x: x.status.value if x.status else '', reverse=True)
    elif sort_by == 'priority_asc':
        filtered_work_items.sort(key=lambda x: x.priority or 0)
    elif sort_by == 'priority_desc':
        filtered_work_items.sort(key=lambda x: x.priority or 0, reverse=True)
    elif sort_by == 'created_asc':
        filtered_work_items.sort(key=lambda x: x.created_at or datetime.min)
    elif sort_by == 'created_desc':
        filtered_work_items.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    else:  # updated_desc (default)
        filtered_work_items.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
    
    # Apply pagination
    paginated_work_items, pagination = paginate_items(
        items=filtered_work_items,
        page=page,
        per_page=per_page,
        base_url=request.path,
        query_params=get_query_params_from_request(request)
    )
    
    # Calculate comprehensive metrics for the sidebar
    metrics = {
        # Basic counts
        'total_work_items': len(work_items_list),
        'total_tasks': len(tasks_list),
        
        # Status-based counts
        'draft_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'draft']),
        'ready_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'ready']),
        'active_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'active']),
        'review_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'review']),
        'blocked_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'blocked']),
        'done_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'done']),
        'archived_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'archived']),
        'cancelled_work_items': len([wi for wi in work_items_list if wi.status and wi.status.value == 'cancelled']),
        
        # Phase-based counts (simplified mapping)
        'phase_d1_discovery': len([wi for wi in work_items_list if wi.status and wi.status.value in ['draft']]),
        'phase_p1_plan': len([wi for wi in work_items_list if wi.status and wi.status.value in ['ready']]),
        'phase_i1_implementation': len([wi for wi in work_items_list if wi.status and wi.status.value in ['active']]),
        'phase_r1_review': len([wi for wi in work_items_list if wi.status and wi.status.value in ['review']]),
        'phase_o1_operations': len([wi for wi in work_items_list if wi.status and wi.status.value in ['done']]),
        'phase_e1_evolution': 0,  # No specific phase for evolution
        
        # Type-based counts
        'feature_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'feature']),
        'enhancement_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'enhancement']),
        'bugfix_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'bugfix']),
        'analysis_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'analysis']),
        'research_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'research']),
        'documentation_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'documentation']),
        'maintenance_work_items': len([wi for wi in work_items_list if wi.type and wi.type.value == 'maintenance']),
        
        # Priority-based counts
        'priority_1_work_items': len([wi for wi in work_items_list if wi.priority == 1]),
        'priority_2_work_items': len([wi for wi in work_items_list if wi.priority == 2]),
        'priority_3_work_items': len([wi for wi in work_items_list if wi.priority == 3]),
    }
    
    # Get available filter options
    filter_options = {
        'statuses': [{'value': status.value, 'label': status.value.replace('_', ' ').title()} 
                    for status in WorkItemStatus],
        'types': [{'value': type_.value, 'label': type_.value.replace('_', ' ').title()} 
                 for type_ in WorkItemType],
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
            {'value': 'priority_asc', 'label': 'Priority (Low to High)'},
            {'value': 'priority_desc', 'label': 'Priority (High to Low)'},
        ]
    }
    
    # Check if this is an HTMX request for dynamic filtering
    if _is_htmx_request():
        # Return only the content that should be updated
        return render_template('work-items/partials/work_items_content.html', 
                             work_items=paginated_work_items,
                             metrics=metrics,
                             filter_options=filter_options,
                             pagination=pagination,
                             current_filters={
                                 'search': search_query,
                                 'status': status_filter,
                                 'type': type_filter,
                                 'priority': priority_filter,
                                 'sort': sort_by
                             })
    
    # Return full page for regular requests
    return render_template('work-items/list.html', 
                         work_items=paginated_work_items,
                         metrics=metrics,
                         filter_options=filter_options,
                         pagination=pagination,
                         current_filters={
                             'search': search_query,
                             'status': status_filter,
                             'type': type_filter,
                             'priority': priority_filter,
                             'sort': sort_by
                         })

@work_items_bp.route('/bulk-update', methods=['POST'])
def bulk_update_work_items():
    """Bulk update work items via AJAX"""
    try:
        db = get_database_service()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        work_item_ids = data.get('work_item_ids', [])
        if not work_item_ids:
            return jsonify({'error': 'No work item IDs provided'}), 400
        
        updates = {}
        
        # Process update fields
        if 'status' in data and data['status']:
            try:
                updates['status'] = WorkItemStatus(data['status'])
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
        
        if 'phase' in data and data['phase']:
            try:
                updates['phase'] = Phase(data['phase'])
            except ValueError:
                return jsonify({'error': 'Invalid phase'}), 400
        
        if 'description' in data:
            updates['description'] = data['description'] if data['description'] else None
        
        if not updates:
            return jsonify({'error': 'No update fields provided'}), 400
        
        # Perform bulk updates
        updated_count = 0
        errors = []
        
        for work_item_id in work_item_ids:
            try:
                work_item = work_items.get_work_item(db, work_item_id)
                if not work_item:
                    errors.append(f"Work item {work_item_id} not found")
                    continue
                
                # Apply updates
                for field, value in updates.items():
                    setattr(work_item, field, value)
                
                work_items.update_work_item(db, work_item)
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Work item {work_item_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'total_count': len(work_item_ids),
            'errors': errors,
            'message': f'Successfully updated {updated_count} of {len(work_item_ids)} work items'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return jsonify({'error': str(e)}), 500

@work_items_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete_work_items():
    """Bulk delete work items via AJAX"""
    try:
        db = get_database_service()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        work_item_ids = data.get('work_item_ids', [])
        if not work_item_ids:
            return jsonify({'error': 'No work item IDs provided'}), 400
        
        # Perform bulk deletes
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
                errors.append(f"Work item {work_item_id}: {str(e)}")
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'total_count': len(work_item_ids),
            'errors': errors,
            'message': f'Successfully deleted {deleted_count} of {len(work_item_ids)} work items'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        return jsonify({'error': str(e)}), 500

@work_items_bp.route('/export')
def export_work_items():
    """Export work items to CSV or JSON"""
    try:
        db = get_database_service()
        
        # Get filter parameters (same as list view)
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        type_filter = request.args.get('type', '')
        priority_filter = request.args.get('priority', '')
        sort_by = request.args.get('sort', 'updated_desc')
        
        # Get project ID for work items
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get all work items and apply filters (reuse logic from work_items_list)
        work_items_list = work_items.list_work_items(db, project_id=project_id) or []
        
        # Apply same filtering logic as in work_items_list
        filtered_work_items = work_items_list
        
        if search_query:
            filtered_work_items = [
                wi for wi in filtered_work_items
                if search_query.lower() in (wi.name or '').lower() or 
                   search_query.lower() in (wi.description or '').lower()
            ]
        
        if status_filter:
            filtered_work_items = [
                wi for wi in filtered_work_items
                if wi.status and wi.status.value == status_filter
            ]
        
        if type_filter:
            filtered_work_items = [
                wi for wi in filtered_work_items
                if wi.type and wi.type.value == type_filter
            ]
        
        if priority_filter:
            try:
                priority = int(priority_filter)
                filtered_work_items = [
                    wi for wi in filtered_work_items
                    if wi.priority == priority
                ]
            except ValueError:
                pass
        
        # Apply sorting (same as in work_items_list)
        if sort_by == 'name_asc':
            filtered_work_items.sort(key=lambda x: (x.name or '').lower())
        elif sort_by == 'name_desc':
            filtered_work_items.sort(key=lambda x: (x.name or '').lower(), reverse=True)
        elif sort_by == 'status_asc':
            filtered_work_items.sort(key=lambda x: x.status.value if x.status else '')
        elif sort_by == 'status_desc':
            filtered_work_items.sort(key=lambda x: x.status.value if x.status else '', reverse=True)
        elif sort_by == 'priority_asc':
            filtered_work_items.sort(key=lambda x: x.priority or 0)
        elif sort_by == 'priority_desc':
            filtered_work_items.sort(key=lambda x: x.priority or 0, reverse=True)
        else:  # updated_desc (default)
            filtered_work_items.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
        
        # Get export format
        export_format = request.args.get('format', 'csv').lower()
        
        if export_format == 'json':
            # Export as JSON
            # Convert work items to dictionaries
            work_items_data = []
            for wi in filtered_work_items:
                wi_dict = {
                    'id': wi.id,
                    'name': wi.name,
                    'description': wi.description,
                    'type': wi.type.value if wi.type else None,
                    'status': wi.status.value if wi.status else None,
                    'priority': wi.priority,
                    'phase': wi.phase.value if wi.phase else None,
                    'project_id': wi.project_id,
                    'created_at': wi.created_at.isoformat() if wi.created_at else None,
                    'updated_at': wi.updated_at.isoformat() if wi.updated_at else None,
                }
                work_items_data.append(wi_dict)
            
            response = Response(
                json.dumps(work_items_data, indent=2),
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=work_items_export.json'}
            )
            return response
        
        else:  # CSV format
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Name', 'Description', 'Type', 'Status', 'Priority', 
                'Phase', 'Project ID', 'Created At', 'Updated At'
            ])
            
            # Write data
            for wi in filtered_work_items:
                writer.writerow([
                    wi.id,
                    wi.name or '',
                    wi.description or '',
                    wi.type.value if wi.type else '',
                    wi.status.value if wi.status else '',
                    wi.priority or '',
                    wi.phase.value if wi.phase else '',
                    wi.project_id or '',
                    wi.created_at.strftime('%Y-%m-%d %H:%M:%S') if wi.created_at else '',
                    wi.updated_at.strftime('%Y-%m-%d %H:%M:%S') if wi.updated_at else '',
                ])
            
            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=work_items_export.csv'}
            )
            return response
        
    except Exception as e:
        logger.error(f"Error exporting work items: {e}")
        return jsonify({'error': str(e)}), 500
