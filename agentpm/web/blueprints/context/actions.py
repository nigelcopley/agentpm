"""
Context Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for contexts including:
- Create, Read, Update, Delete operations
- Context validation and confidence scoring
- Rich context management
"""

import logging
from typing import Optional

from flask import request, jsonify, flash, redirect, url_for

from ....core.database.methods import contexts
from ....core.database.models import Context
from ....core.database.enums import ContextType, EntityType
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_context():
    """Create a new context."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'what': 'What field is required',
            'context_type': 'Context type is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('context.contexts_list'))
        
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
        return handle_error(e, 'Error creating context', url_for('context.contexts_list'))

def update_context(context_id: int):
    """Update an existing context"""
    try:
        db = get_database_service()
        from ....core.database.methods import contexts
        from ....core.database.enums import ContextType, EntityType
        
        context = safe_get_entity(contexts.get_context, db, context_id, "Context")
        if not context:
            flash('Context not found', 'error')
            return redirect(url_for('context.contexts_list'))
        
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
        
        # Update context using the correct method signature
        updated_context = contexts.update_context(db, context_id,
                                                 what=what,
                                                 why=why if why else None,
                                                 how=how if how else None,
                                                 context_type=ContextType(context_type),
                                                 entity_type=EntityType(entity_type) if entity_type else None,
                                                 entity_id=entity_id,
                                                 project_id=project_id,
                                                 file_path=file_path if file_path else None,
                                                 confidence_score=confidence_score)
        
        flash(f'Context "{updated_context.what}" updated successfully', 'success')
        return redirect(url_for('context.context_detail', context_id=context_id))
        
    except Exception as e:
        return handle_error(e, 'Error updating context', url_for('context.edit_context', context_id=context_id))

def delete_context(context_id: int):
    """Delete a context"""
    try:
        db = get_database_service()
        from ....core.database.methods import contexts
        
        context = safe_get_entity(contexts.get_context, db, context_id, "Context")
        if not context:
            flash('Context not found', 'error')
            return redirect(url_for('context.contexts_list'))
        
        context_what = context.what
        contexts.delete_context(db, context_id)
        
        flash(f'Context "{context_what}" deleted successfully', 'success')
        return redirect(url_for('context.contexts_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting context', url_for('context.context_detail', context_id=context_id))
