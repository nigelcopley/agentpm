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
    """Edit an existing document."""
    try:
        db = get_database_service()
        
        document = safe_get_entity(document_references.get_document_reference, db, document_id, "Document")
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        if request.method == 'GET':
            return render_template('documents/edit.html', document=document)
        
        elif request.method == 'POST':
            # Validate required fields
            required_fields = {
                'title': 'Document title is required',
                'file_path': 'File path is required'
            }
            
            error_message = validate_required_fields(required_fields, request.form)
            if error_message:
                flash(error_message, 'error')
                return redirect(url_for('documents.edit_document', document_id=document_id))
            
            # Get form data
            title = request.form.get('title', '').strip()
            file_path = request.form.get('file_path', '').strip()
            content = request.form.get('content', '').strip()
            
            # Update document
            document.title = title
            document.file_path = file_path
            document.content = content if content else None
            document.updated_at = datetime.now()
            
            updated_document = document_references.update_document_reference(db, document)
            
            flash(f'Document "{updated_document.title}" updated successfully', 'success')
            return redirect(url_for('documents.document_detail', document_id=document_id))
            
    except Exception as e:
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
