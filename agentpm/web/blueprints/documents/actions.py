"""
Documents Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for documents including:
- Create, Read, Update, Delete operations
- Document content management
- Document search and filtering
"""

import logging
from datetime import datetime
from typing import Optional

from flask import request, flash, redirect, url_for, render_template, abort

from ....core.database.methods import document_references, projects
from ....core.database.models import DocumentReference
from ....core.database.enums import EntityType
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    safe_get_entity
)
from . import documents_bp

logger = logging.getLogger(__name__)

@documents_bp.route('/create', methods=['GET', 'POST'])
def create_document():
    """Create a new document."""
    if request.method == 'GET':
        return render_template('documents/create.html')
    
    elif request.method == 'POST':
        try:
            db = get_database_service()
            
            # Validate required fields
            required_fields = {
                'title': 'Document title is required',
                'file_path': 'File path is required'
            }
            
            error_message = validate_required_fields(required_fields, request.form)
            if error_message:
                flash(error_message, 'error')
                return redirect(url_for('documents.create_document'))
            
            # Get form data
            title = request.form.get('title', '').strip()
            file_path = request.form.get('file_path', '').strip()
            content = request.form.get('content', '').strip()
            
            # Get project context
            projects_list = projects.list_projects(db) or []
            project_id = projects_list[0].id if projects_list else 1
            
            # Create document
            document = DocumentReference(
                title=title,
                file_path=file_path,
                content=content if content else None,
                project_id=project_id
            )
            
            created_document = document_references.create_document_reference(db, document)
            
            flash(f'Document "{created_document.title}" created successfully', 'success')
            return redirect(url_for('documents.document_detail', document_id=created_document.id))
            
        except Exception as e:
            return handle_error(e, 'Error creating document', url_for('documents.create_document'))

@documents_bp.route('/<int:document_id>/edit', methods=['GET', 'POST'])
def edit_document(document_id: int):
    """Edit an existing document with enhanced validation and features."""
    try:
        db = get_database_service()
        
        document = safe_get_entity(document_references.get_document_reference, db, document_id, "Document")
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        if request.method == 'GET':
            # Get available entities for suggestions with error handling
            try:
                from ....core.database.methods import work_items, tasks, projects
                
                # Get recent work items, tasks, and projects for entity suggestions
                all_work_items = work_items.list_work_items(db) or []
                all_tasks = tasks.list_tasks(db) or []
                projects_list = projects.list_projects(db) or []
                
                # Limit to recent items (take first 10 due to ordering)
                recent_work_items = all_work_items[:10]
                recent_tasks = all_tasks[:10]
                
                # Get current entity details if associated
                current_entity = None
                if document.entity_type and document.entity_id:
                    try:
                        if document.entity_type == EntityType.WORK_ITEM:
                            current_entity = work_items.get_work_item(db, document.entity_id)
                        elif document.entity_type == EntityType.TASK:
                            current_entity = tasks.get_task(db, document.entity_id)
                        elif document.entity_type == EntityType.PROJECT:
                            current_entity = next((p for p in projects_list if p.id == document.entity_id), None)
                    except Exception as e:
                        logger.warning(f"Error fetching current entity: {e}")
                
                return render_template('documents/edit.html', 
                                     document=document,
                                     current_entity=current_entity,
                                     recent_work_items=recent_work_items,
                                     recent_tasks=recent_tasks,
                                     projects_list=projects_list)
            except Exception as e:
                logger.error(f"Error loading entity suggestions: {e}")
                # Fallback to simple version if entity loading fails
                return render_template('documents/edit.html', document=document)
        
        elif request.method == 'POST':
            # Enhanced validation
            required_fields = {
                'title': 'Document title is required',
                'file_path': 'File path is required'
            }
            
            error_message = validate_required_fields(required_fields, request.form)
            if error_message:
                flash(error_message, 'error')
                return redirect(url_for('documents.edit_document', document_id=document_id))
            
            # Get form data with enhanced processing
            title = request.form.get('title', '').strip()
            file_path = request.form.get('file_path', '').strip()
            content = request.form.get('content', '').strip()
            description = request.form.get('description', '').strip()
            entity_type = request.form.get('entity_type', '').strip()
            entity_id = request.form.get('entity_id', '').strip()
            
            # Security checks for content and file path changes
            content_changed = content != (document.content or '')
            file_path_changed = file_path != (document.file_path or '')
            confirm_content_change = request.form.get('confirm_content_change') == 'on'
            
            # Require confirmation for content changes
            if content_changed and document.file_path and not confirm_content_change:
                flash('❌ Content changes require confirmation. Please check the confirmation box to proceed.', 'error')
                return redirect(url_for('documents.edit_document', document_id=document_id))
            
            # Warn about content changes
            if content_changed and document.file_path:
                flash('⚠️ Content has been modified. This will overwrite the file content. Consider editing the file directly instead.', 'warning')
            
            # Warn about file path changes
            if file_path_changed:
                flash('⚠️ File path has been changed. This may break existing associations and references.', 'warning')
            
            # Validate file path format
            if file_path and not file_path.startswith(('.', '/', 'docs/')):
                flash('File path should start with ".", "/", or "docs/" for proper organisation', 'warning')
            
            # Validate entity association
            entity_validation_error = None
            if entity_type and entity_id:
                try:
                    entity_type_enum = EntityType(entity_type)
                    entity_id_int = int(entity_id)
                    
                    # Verify entity exists
                    entity_exists = False
                    if entity_type_enum == EntityType.WORK_ITEM:
                        entity_exists = work_items.get_work_item(db, entity_id_int) is not None
                    elif entity_type_enum == EntityType.TASK:
                        entity_exists = tasks.get_task(db, entity_id_int) is not None
                    elif entity_type_enum == EntityType.PROJECT:
                        entity_exists = any(p.id == entity_id_int for p in projects.list_projects(db) or [])
                    
                    if not entity_exists:
                        entity_validation_error = f"{entity_type_enum.value.replace('_', ' ').title()} #{entity_id_int} does not exist"
                        
                except (ValueError, TypeError) as e:
                    entity_validation_error = f"Invalid entity association: {e}"
            
            if entity_validation_error:
                flash(entity_validation_error, 'error')
                return redirect(url_for('documents.edit_document', document_id=document_id))
            
            # Update document with enhanced fields
            document.title = title
            document.file_path = file_path
            document.content = content if content else None
            document.description = description if description else None
            document.updated_at = datetime.now()
            
            # Update entity association
            if entity_type and entity_id:
                try:
                    document.entity_type = EntityType(entity_type)
                    document.entity_id = int(entity_id)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid entity association: {e}")
                    flash(f"Invalid entity association: {e}", 'warning')
            else:
                # Clear association if not provided
                document.entity_type = None
                document.entity_id = None
            
            # Update document in database
            updated_document = document_references.update_document_reference(db, document)
            
            # Success message with entity context
            if updated_document.entity_type and updated_document.entity_id:
                entity_name = updated_document.entity_type.value.replace('_', ' ').title()
                flash(f'Document "{updated_document.title}" updated successfully and associated with {entity_name} #{updated_document.entity_id}', 'success')
            else:
                flash(f'Document "{updated_document.title}" updated successfully', 'success')
            
            return redirect(url_for('documents.document_detail', document_id=document_id))
            
    except Exception as e:
        logger.error(f"Error in edit_document: {e}")
        return handle_error(e, 'Error updating document', url_for('documents.edit_document', document_id=document_id))

@documents_bp.route('/<int:document_id>/delete', methods=['POST'])
def delete_document(document_id: int):
    """Delete a document."""
    try:
        db = get_database_service()
        
        document = safe_get_entity(document_references.get_document_reference, db, document_id, "Document")
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        document_title = document.title
        document_references.delete_document_reference(db, document_id)
        
        flash(f'Document "{document_title}" deleted successfully', 'success')
        return redirect(url_for('documents.documents_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting document', url_for('documents.document_detail', document_id=document_id))
