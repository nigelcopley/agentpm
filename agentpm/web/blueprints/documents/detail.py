"""
Documents Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for documents including:
- Individual document detail views
- Document editing and deletion
- Document content management
"""

from flask import render_template, abort, request, redirect, url_for, flash
import logging

from . import documents_bp
from ..utils import get_database_service, safe_get_entity, validate_required_fields, handle_error

logger = logging.getLogger(__name__)

@documents_bp.route('/<int:document_id>')
def document_detail(document_id: int):
    """Document detail view"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references
        
        document = safe_get_entity(document_references.get_document_reference, db, document_id, "Document")
        
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        # Calculate document statistics
        document_stats = {
            'has_content': bool(document.content),
            'has_file_path': bool(document.file_path),
            'content_length': len(document.content) if document.content else 0,
            'word_count': len(document.content.split()) if document.content else 0,
        }
        
        return render_template('documents/detail.html', 
                             document=document,
                             document_id=document_id,
                             document_stats=document_stats)
    
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        abort(500, description="Error loading document")
