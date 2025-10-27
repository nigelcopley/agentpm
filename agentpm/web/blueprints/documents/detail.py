"""
Documents Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for documents including:
- Individual document detail views
- Document editing and deletion
- Document content management
"""

from flask import render_template, abort, request, redirect, url_for, flash
import logging
import os
from pathlib import Path
from datetime import datetime

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
        
        # File metadata calculation
        file_size = 0
        file_modified = None
        file_exists = False
        
        if document.file_path:
            try:
                file_path = Path(document.file_path)
                if file_path.exists():
                    file_exists = True
                    stat = file_path.stat()
                    file_size = stat.st_size
                    file_modified = datetime.fromtimestamp(stat.st_mtime)
            except Exception as e:
                logger.warning(f"Error reading file metadata for {document.file_path}: {e}")
        
        # Document content processing - prioritize file content over database content
        document_content = None
        content_source = "database"
        
        # First try to read from file if it exists (file is source of truth)
        if document.file_path and file_exists:
            try:
                with open(document.file_path, 'r', encoding='utf-8') as f:
                    document_content = f.read()
                content_source = "file"
            except Exception as e:
                logger.warning(f"Error reading file content from {document.file_path}: {e}")
                # Fall back to database content if file read fails
                if document.content:
                    document_content = document.content
                    content_source = "database (fallback)"
        elif document.content:
            # Use database content if no file or file doesn't exist
            document_content = document.content
            content_source = "database"
        
        # Document type and format labels
        document_type_label = None
        if document.document_type:
            document_type_label = document.document_type.value.replace('_', ' ').title()
        
        format_label = None
        if document.format:
            format_label = document.format.value.upper()
        
        # Path structure parsing
        parsed_path = None
        if document.file_path:
            try:
                path_parts = Path(document.file_path).parts
                if len(path_parts) >= 3:
                    parsed_path = {
                        'category': path_parts[-3] if len(path_parts) >= 3 else None,
                        'document_type': path_parts[-2] if len(path_parts) >= 2 else None,
                        'filename': path_parts[-1] if path_parts else None
                    }
            except Exception as e:
                logger.warning(f"Error parsing path structure for {document.file_path}: {e}")
        
        return render_template('documents/detail.html', 
                             document=document,
                             document_id=document_id,
                             document_stats=document_stats,
                             file_size=file_size,
                             file_modified=file_modified,
                             file_exists=file_exists,
                             document_content=document_content,
                             content_source=content_source,
                             document_type_label=document_type_label,
                             format_label=format_label,
                             parsed_path=parsed_path)
    
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        abort(500, description="Error loading document")
