"""
Context Blueprint for APM (Agent Project Manager) Web Application

Comprehensive context management functionality with CRUD operations.
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for, jsonify, flash
import logging
from datetime import datetime

def _is_htmx_request():
    """Check if request is from HTMX"""
    return request.headers.get('HX-Request') == 'true'

# Create context blueprint
context_bp = Blueprint('context', __name__, url_prefix='/context')

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

@context_bp.route('/')
def contexts_list():
    """Contexts list view with comprehensive metrics, filtering, and search"""
    db = get_database_service()
    
    # Get database methods
    from ...core.database.methods import contexts, projects
    from ...core.database.enums import ContextType, EntityType, ConfidenceBand
    
    # Get project ID for contexts
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')
    entity_type_filter = request.args.get('entity_type', '')
    confidence_filter = request.args.get('confidence', '')
    sort_by = request.args.get('sort', 'updated_desc')
    
    # Get all contexts
    contexts_list = contexts.list_contexts(db, project_id=project_id) or []
    
    # Apply filters
    filtered_contexts = contexts_list
    
    # Search filter
    if search_query:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if search_query.lower() in (ctx.what or '').lower() or 
               search_query.lower() in (ctx.why or '').lower() or
               search_query.lower() in (ctx.how or '').lower() or
               search_query.lower() in (str(ctx.context_data or '')).lower() or
               search_query.lower() in (ctx.file_path or '').lower() or
               search_query.lower() in (ctx.context_type.value if ctx.context_type else '').lower()
        ]
    
    # Type filter
    if type_filter:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if ctx.context_type and ctx.context_type.value == type_filter
        ]
    
    # Entity type filter
    if entity_type_filter:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if ctx.entity_type and ctx.entity_type.value == entity_type_filter
        ]
    
    # Confidence filter
    if confidence_filter:
        if confidence_filter == 'high':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and ctx.confidence_score >= 0.8
            ]
        elif confidence_filter == 'medium':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and 0.6 <= ctx.confidence_score < 0.8
            ]
        elif confidence_filter == 'low':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and ctx.confidence_score < 0.6
            ]
    
    # Apply sorting
    if sort_by == 'title_asc':
        filtered_contexts.sort(key=lambda x: (x.title or '').lower())
    elif sort_by == 'title_desc':
        filtered_contexts.sort(key=lambda x: (x.title or '').lower(), reverse=True)
    elif sort_by == 'type_asc':
        filtered_contexts.sort(key=lambda x: x.context_type.value if x.context_type else '')
    elif sort_by == 'type_desc':
        filtered_contexts.sort(key=lambda x: x.context_type.value if x.context_type else '', reverse=True)
    elif sort_by == 'confidence_asc':
        filtered_contexts.sort(key=lambda x: x.confidence_score or 0)
    elif sort_by == 'confidence_desc':
        filtered_contexts.sort(key=lambda x: x.confidence_score or 0, reverse=True)
    elif sort_by == 'created_asc':
        filtered_contexts.sort(key=lambda x: x.created_at or datetime.min)
    elif sort_by == 'created_desc':
        filtered_contexts.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    else:  # updated_desc (default)
        filtered_contexts.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
    
    # Calculate comprehensive metrics for the sidebar
    metrics = {
        # Basic counts
        'total_contexts': len(contexts_list),
        
        # Type-based counts
        'business_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'business_pillars_context']),
        'technical_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'technical_context']),
        'resource_files': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'resource_file']),
        'rules_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'rules_context']),
        'work_item_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'work_item_context']),
        
        # Entity type counts
        'work_item_entity_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'work_item']),
        'task_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'task']),
        'idea_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'idea']),
        'session_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'session']),
        
        # Confidence band counts
        'high_confidence': len([ctx for ctx in contexts_list if ctx.confidence_score and ctx.confidence_score >= 0.8]),
        'medium_confidence': len([ctx for ctx in contexts_list if ctx.confidence_score and 0.6 <= ctx.confidence_score < 0.8]),
        'low_confidence': len([ctx for ctx in contexts_list if ctx.confidence_score and ctx.confidence_score < 0.6]),
        'no_confidence': len([ctx for ctx in contexts_list if not ctx.confidence_score]),
    }
    
    # Get available filter options
    filter_options = {
        'types': [{'value': type_.value, 'label': type_.value.replace('_', ' ').title()} 
                 for type_ in ContextType],
        'entity_types': [{'value': type_.value, 'label': type_.value.replace('_', ' ').title()} 
                        for type_ in EntityType],
        'confidence_levels': [
            {'value': 'high', 'label': 'High (≥80%)'},
            {'value': 'medium', 'label': 'Medium (60-79%)'},
            {'value': 'low', 'label': 'Low (<60%)'},
        ],
        'sort_options': [
            {'value': 'updated_desc', 'label': 'Last Updated (Newest)'},
            {'value': 'updated_asc', 'label': 'Last Updated (Oldest)'},
            {'value': 'created_desc', 'label': 'Created (Newest)'},
            {'value': 'created_asc', 'label': 'Created (Oldest)'},
            {'value': 'title_asc', 'label': 'Title (A-Z)'},
            {'value': 'title_desc', 'label': 'Title (Z-A)'},
            {'value': 'type_asc', 'label': 'Type (A-Z)'},
            {'value': 'type_desc', 'label': 'Type (Z-A)'},
            {'value': 'confidence_asc', 'label': 'Confidence (Low to High)'},
            {'value': 'confidence_desc', 'label': 'Confidence (High to Low)'},
        ]
    }
    
    # Check if this is an HTMX request for dynamic filtering
    if _is_htmx_request():
        # Return only the content that should be updated
        return render_template('context/partials/contexts_content.html', 
                             contexts=filtered_contexts,
                             metrics=metrics,
                             filter_options=filter_options,
                             current_filters={
                                 'search': search_query,
                                 'type': type_filter,
                                 'entity_type': entity_type_filter,
                                 'confidence': confidence_filter,
                                 'sort': sort_by
                             })
    
    # Return full page for regular requests
    return render_template('context/list.html', 
                         contexts=filtered_contexts,
                         metrics=metrics,
                         filter_options=filter_options,
                         current_filters={
                             'search': search_query,
                             'type': type_filter,
                             'entity_type': entity_type_filter,
                             'confidence': confidence_filter,
                             'sort': sort_by
                         })

@context_bp.route('/<int:context_id>')
def context_detail(context_id: int):
    """
    Comprehensive context detail view.
    
    Shows all context information in a single view:
    - Basic information (title, type, confidence)
    - Context data and content
    - Related entity information
    - Confidence factors and scoring
    - Timeline and history
    """
    # Fetch context data
    db = get_database_service()
    from ...core.database.methods import contexts, work_items, tasks, ideas, agents
    
    context = contexts.get_context(db, context_id)
    
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    # Get related entity information
    related_entity = None
    if context.entity_type and context.entity_id:
        try:
            if context.entity_type.value == 'work_item':
                related_entity = work_items.get_work_item(db, context.entity_id)
            elif context.entity_type.value == 'task':
                related_entity = tasks.get_task(db, context.entity_id)
            elif context.entity_type.value == 'idea':
                related_entity = ideas.get_idea(db, context.entity_id)
            elif context.entity_type.value == 'agent':
                related_entity = agents.get_agent(db, context.entity_id)
        except Exception as e:
            logger.warning(f"Error fetching related entity: {e}")
    
    # Calculate context statistics
    context_stats = {
        'has_six_w': bool(context.six_w),
        'has_confidence_score': bool(context.confidence_score),
        'has_confidence_factors': bool(context.confidence_factors),
        'is_resource_file': context.is_resource_file(),
        'is_entity_context': context.is_entity_context(),
        'confidence_band': context.confidence_band.value if context.confidence_band else None,
    }
    
    return render_template('context/detail.html', 
                         context=context,
                         context_id=context_id,
                         related_entity=related_entity,
                         context_stats=context_stats)

@context_bp.route('/create', methods=['GET', 'POST'])
def create_context():
    """Create a new context"""
    if request.method == 'GET':
        # Show create form
        db = get_database_service()
        from ...core.database.methods import projects, work_items, tasks, ideas
        from ...core.database.enums import ContextType, EntityType
        
        projects_list = projects.list_projects(db) or []
        work_items_list = work_items.list_work_items(db) or []
        tasks_list = tasks.list_tasks(db) or []
        ideas_list = ideas.list_ideas(db) or []
        
        return render_template('context/create.html',
                             projects=projects_list,
                             work_items=work_items_list,
                             tasks=tasks_list,
                             ideas=ideas_list,
                             context_types=ContextType,
                             entity_types=EntityType)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            db = get_database_service()
            from ...core.database.methods import contexts
            from ...core.database.models import Context
            from ...core.database.enums import ContextType, EntityType, ResourceType
            
            # Get form data
            context_type = request.form.get('context_type', 'business_context')
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id')
            context_data = request.form.get('context_data', '').strip()
            file_path = request.form.get('file_path', '').strip()
            resource_type = request.form.get('resource_type')
            project_id = int(request.form.get('project_id', 1))
            
            # Validate required fields
            if not context_data and not file_path:
                flash('Context description or file path is required', 'error')
                return redirect(url_for('context.create_context'))
            
            # Create context
            context = Context(
                context_type=ContextType(context_type),
                entity_type=EntityType(entity_type) if entity_type else None,
                entity_id=int(entity_id) if entity_id else None,
                context_data=context_data if context_data else None,
                file_path=file_path if file_path else None,
                resource_type=ResourceType(resource_type) if resource_type else None,
                project_id=project_id
            )
            
            created_context = contexts.create_context(db, context)
            
            flash(f'Context created successfully', 'success')
            return redirect(url_for('context.context_detail', context_id=created_context.id))
            
        except Exception as e:
            logger.error(f"Error creating context: {e}")
            flash(f'Error creating context: {str(e)}', 'error')
            return redirect(url_for('context.create_context'))

@context_bp.route('/<int:context_id>/edit', methods=['GET', 'POST'])
def edit_context(context_id: int):
    """Edit an existing context"""
    db = get_database_service()
    from ...core.database.methods import contexts, projects, work_items, tasks, ideas
    from ...core.database.enums import ContextType, EntityType, ResourceType
    
    context = contexts.get_context(db, context_id)
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    if request.method == 'GET':
        # Show edit form
        projects_list = projects.list_projects(db) or []
        work_items_list = work_items.list_work_items(db) or []
        tasks_list = tasks.list_tasks(db) or []
        ideas_list = ideas.list_ideas(db) or []
        
        return render_template('context/edit.html',
                             context=context,
                             projects=projects_list,
                             work_items=work_items_list,
                             tasks=tasks_list,
                             ideas=ideas_list,
                             context_types=ContextType,
                             entity_types=EntityType)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            # Get form data
            context_type = request.form.get('context_type', 'business_context')
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id')
            context_data = request.form.get('context_data', '').strip()
            file_path = request.form.get('file_path', '').strip()
            resource_type = request.form.get('resource_type')
            project_id = int(request.form.get('project_id', 1))
            
            # Validate required fields
            if not context_data and not file_path:
                flash('Context description or file path is required', 'error')
                return redirect(url_for('context.edit_context', context_id=context_id))
            
            # Update context
            updates = {
                'context_type': ContextType(context_type),
                'entity_type': EntityType(entity_type) if entity_type else None,
                'entity_id': int(entity_id) if entity_id else None,
                'context_data': context_data if context_data else None,
                'file_path': file_path if file_path else None,
                'resource_type': ResourceType(resource_type) if resource_type else None,
                'project_id': project_id
            }
            
            updated_context = contexts.update_context(db, context_id, **updates)
            
            flash(f'Context updated successfully', 'success')
            return redirect(url_for('context.context_detail', context_id=updated_context.id))
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            flash(f'Error updating context: {str(e)}', 'error')
            return redirect(url_for('context.edit_context', context_id=context_id))

@context_bp.route('/<int:context_id>/delete', methods=['POST'])
def delete_context(context_id: int):
    """Delete a context"""
    try:
        db = get_database_service()
        from ...core.database.methods import contexts
        
        context = contexts.get_context(db, context_id)
        if not context:
            abort(404, description=f"Context {context_id} not found")
        
        contexts.delete_context(db, context_id)
        
        flash(f'Context deleted successfully', 'success')
        return redirect(url_for('context.contexts_list'))
        
    except Exception as e:
        logger.error(f"Error deleting context: {e}")
        flash(f'Error deleting context: {str(e)}', 'error')
        return redirect(url_for('context.context_detail', context_id=context_id))

@context_bp.route('/documents')
def context_documents_list():
    """Context documents list - resource files"""
    db = get_database_service()
    from ...core.database.methods import contexts, projects
    
    # Get project ID
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get resource files
    resource_files = contexts.list_resource_files(db, project_id=project_id) or []
    
    # Calculate metrics
    total_size = sum(file.file_size or 0 for file in resource_files)
    
    view = {
        'project': {'name': 'APM (Agent Project Manager) Project', 'id': project_id},
        'context_files': resource_files,
        'total_size': total_size,
        'total_files': len(resource_files)
    }
    
    return render_template('context/documents.html', view=view)

@context_bp.route('/evidence')
def context_evidence_list():
    """Context evidence list - decision and learning contexts"""
    db = get_database_service()
    from ...core.database.methods import contexts, projects
    from ...core.database.enums import ContextType
    
    # Get project ID
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get evidence contexts (decisions and learnings)
    evidence_contexts = []
    all_contexts = contexts.list_contexts(db, project_id=project_id) or []
    
    for ctx in all_contexts:
        if ctx.context_type in [ContextType.RULES_CONTEXT, ContextType.BUSINESS_PILLARS_CONTEXT]:
            evidence_contexts.append(ctx)
    
    return render_template('context/evidence.html', 
                         contexts=evidence_contexts,
                         total_evidence=len(evidence_contexts))

@context_bp.route('/events')
def context_events_list():
    """Context events list - timeline of context changes"""
    db = get_database_service()
    from ...core.database.methods import contexts, projects
    
    # Get project ID
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get all contexts sorted by creation/update time
    all_contexts = contexts.list_contexts(db, project_id=project_id) or []
    
    # Sort by most recent activity
    all_contexts.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
    
    return render_template('context/events.html', 
                         contexts=all_contexts,
                         total_events=len(all_contexts))

@context_bp.route('/sessions')
def context_sessions_list():
    """Context sessions list - agent session contexts"""
    db = get_database_service()
    from ...core.database.methods import contexts, projects
    from ...core.database.enums import EntityType
    
    # Get project ID
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get agent session contexts
    session_contexts = []
    all_contexts = contexts.list_contexts(db, project_id=project_id) or []
    
    for ctx in all_contexts:
        if ctx.entity_type == EntityType.SESSION:
            session_contexts.append(ctx)
    
    return render_template('context/sessions.html', 
                         contexts=session_contexts,
                         total_sessions=len(session_contexts))
