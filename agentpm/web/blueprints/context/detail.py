"""
Context Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for contexts including:
- Individual context detail views with comprehensive context
- Context creation and editing
- Context deletion
- Context validation and confidence scoring
"""

from flask import render_template, abort, request, redirect, url_for, flash
from datetime import datetime
import logging

from . import context_bp
from ..utils import get_database_service, safe_get_entity, validate_required_fields, handle_error

logger = logging.getLogger(__name__)

@context_bp.route('/<int:context_id>')
def context_detail(context_id: int):
    """
    Comprehensive context detail view.
    
    Shows all context information in a single view:
    - Basic information (what, why, how, confidence)
    - Context type and entity relationships
    - File associations and metadata
    - Related contexts and dependencies
    - Usage statistics and validation
    - Project and entity context
    """
    # Fetch context data
    db = get_database_service()
    from ....core.database.methods import contexts, projects, work_items, tasks, ideas, agents
    
    context = safe_get_entity(contexts.get_context, db, context_id, "Context")
    
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    # Get project information
    project = None
    if context.project_id:
        projects_list = projects.list_projects(db) or []
        project = next((p for p in projects_list if p.id == context.project_id), None)
    
    # Get related entity information
    related_entity = None
    if context.entity_id and context.entity_type:
        try:
            if context.entity_type.value == 'project':
                related_entity = project
            elif context.entity_type.value == 'work_item':
                related_entity = work_items.get_work_item(db, context.entity_id)
            elif context.entity_type.value == 'task':
                related_entity = tasks.get_task(db, context.entity_id)
            elif context.entity_type.value == 'idea':
                related_entity = ideas.get_idea(db, context.entity_id)
            elif context.entity_type.value == 'agent':
                related_entity = agents.get_agent(db, context.entity_id)
        except Exception as e:
            logger.warning(f"Error fetching related entity: {e}")
    
    # Get related contexts (same entity or similar type)
    related_contexts = []
    try:
        all_contexts = contexts.list_contexts(db, project_id=context.project_id) or []
        for other_context in all_contexts:
            if other_context.id != context_id:
                # Same entity
                if context.entity_id and other_context.entity_id == context.entity_id:
                    related_contexts.append(other_context)
                # Same context type
                elif context.context_type and other_context.context_type == context.context_type:
                    related_contexts.append(other_context)
    except Exception as e:
        logger.warning(f"Error fetching related contexts: {e}")
    
    # Calculate context statistics
    context_stats = {
        'has_file': bool(context.file_path),
        'has_confidence': bool(context.confidence_score),
        'has_entity': bool(context.entity_id),
        'has_what': bool(context.what),
        'has_why': bool(context.why),
        'has_how': bool(context.how),
        'has_context_data': bool(context.context_data),
        'confidence_level': 'high' if context.confidence_score and context.confidence_score >= 0.8 else 'medium' if context.confidence_score and context.confidence_score >= 0.6 else 'low' if context.confidence_score else 'none',
        'related_contexts_count': len(related_contexts),
        'days_since_created': (datetime.now() - context.created_at).days if context.created_at else None,
        'days_since_updated': (datetime.now() - context.updated_at).days if context.updated_at else None,
    }
    
    # Get context metadata
    context_metadata = {
        'file_info': {
            'path': context.file_path,
            'exists': False,  # Would need to check file system
            'size': 0,  # Would need to check file system
            'modified': None  # Would need to check file system
        } if context.file_path else None,
        'context_data': context.context_data,
        'validation_status': 'valid' if context.confidence_score and context.confidence_score >= 0.6 else 'needs_review',
        'completeness_score': _calculate_completeness_score(context)
    }
    
    return render_template('context/detail.html', 
                         context=context, 
                         context_id=context_id,
                         project=project,
                         related_entity=related_entity,
                         related_contexts=related_contexts,
                         context_stats=context_stats,
                         context_metadata=context_metadata)

@context_bp.route('/create', methods=['GET', 'POST'])
def create_context():
    """Create a new context"""
    if request.method == 'GET':
        # Show create form
        db = get_database_service()
        from ....core.database.methods import projects
        from ....core.database.enums import ContextType, EntityType
        
        projects_list = projects.list_projects(db) or []
        
        return render_template('context/create.html',
                             projects=projects_list,
                             context_types=ContextType,
                             entity_types=EntityType)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            db = get_database_service()
            from ....core.database.methods import contexts
            from ....core.database.models import Context
            from ....core.database.enums import ContextType, EntityType
            
            # Validate required fields
            required_fields = {
                'what': 'What field is required',
                'context_type': 'Context type is required'
            }
            
            error_message = validate_required_fields(required_fields, request.form)
            if error_message:
                flash(error_message, 'error')
                return redirect(url_for('context.create_context'))
            
            # Get form data
            what = request.form.get('what', '').strip()
            why = request.form.get('why', '').strip()
            how = request.form.get('how', '').strip()
            context_type = request.form.get('context_type')
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id')
            entity_id = int(entity_id) if entity_id else None
            project_id = int(request.form.get('project_id', 1))
            file_path = request.form.get('file_path', '').strip()
            confidence_score = request.form.get('confidence_score')
            confidence_score = float(confidence_score) if confidence_score else None
            
            # Create context
            context = Context(
                what=what,
                why=why if why else None,
                how=how if how else None,
                context_type=ContextType(context_type),
                entity_type=EntityType(entity_type) if entity_type else None,
                entity_id=entity_id,
                project_id=project_id,
                file_path=file_path if file_path else None,
                confidence_score=confidence_score
            )
            
            created_context = contexts.create_context(db, context)
            
            flash(f'Context "{created_context.what}" created successfully', 'success')
            return redirect(url_for('context.context_detail', context_id=created_context.id))
            
        except Exception as e:
            return handle_error(e, 'Error creating context', url_for('context.create_context'))

@context_bp.route('/<int:context_id>/edit', methods=['GET', 'POST'])
def edit_context(context_id: int):
    """Edit an existing context"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    from ....core.database.enums import ContextType, EntityType
    
    context = safe_get_entity(contexts.get_context, db, context_id, "Context")
    if not context:
        abort(404, description=f"Context {context_id} not found")
    
    if request.method == 'GET':
        # Show edit form
        projects_list = projects.list_projects(db) or []
        
        return render_template('context/edit.html',
                             context=context,
                             projects=projects_list,
                             context_types=ContextType,
                             entity_types=EntityType)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            # Validate required fields
            required_fields = {
                'what': 'What field is required',
                'context_type': 'Context type is required'
            }
            
            error_message = validate_required_fields(required_fields, request.form)
            if error_message:
                flash(error_message, 'error')
                return redirect(url_for('context.edit_context', context_id=context_id))
            
            # Get form data
            what = request.form.get('what', '').strip()
            why = request.form.get('why', '').strip()
            how = request.form.get('how', '').strip()
            context_type = request.form.get('context_type')
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id')
            entity_id = int(entity_id) if entity_id else None
            project_id = int(request.form.get('project_id', 1))
            file_path = request.form.get('file_path', '').strip()
            confidence_score = request.form.get('confidence_score')
            confidence_score = float(confidence_score) if confidence_score else None
            
            # Update context
            context.what = what
            context.why = why if why else None
            context.how = how if how else None
            context.context_type = ContextType(context_type)
            context.entity_type = EntityType(entity_type) if entity_type else None
            context.entity_id = entity_id
            context.project_id = project_id
            context.file_path = file_path if file_path else None
            context.confidence_score = confidence_score
            context.updated_at = datetime.now()
            
            updated_context = contexts.update_context(db, context)
            
            flash(f'Context "{updated_context.what}" updated successfully', 'success')
            return redirect(url_for('context.context_detail', context_id=updated_context.id))
            
        except Exception as e:
            return handle_error(e, 'Error updating context', url_for('context.edit_context', context_id=context_id))

@context_bp.route('/<int:context_id>/delete', methods=['POST'])
def delete_context(context_id: int):
    """Delete a context"""
    try:
        db = get_database_service()
        from ....core.database.methods import contexts
        
        context = safe_get_entity(contexts.get_context, db, context_id, "Context")
        if not context:
            abort(404, description=f"Context {context_id} not found")
        
        contexts.delete_context(db, context_id)
        
        flash(f'Context "{context.what}" deleted successfully', 'success')
        return redirect(url_for('context.contexts_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting context', url_for('context.context_detail', context_id=context_id))

def _calculate_completeness_score(context):
    """Calculate completeness score for a context"""
    score = 0
    total_fields = 6  # what, why, how, context_type, entity_type, confidence_score
    
    if context.what:
        score += 1
    if context.why:
        score += 1
    if context.how:
        score += 1
    if context.context_type:
        score += 1
    if context.entity_type:
        score += 1
    if context.confidence_score:
        score += 1
    
    return round((score / total_fields) * 100, 1)
