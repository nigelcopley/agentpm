"""
Context Files Module for APM (Agent Project Manager) Web Application

Handles file-related context functionality including:
- File listing and management
- File preview and download
- File-based context creation
"""

from flask import render_template, request, send_file, abort
import os
import logging

from . import context_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@context_bp.route('/documents')
def context_documents():
    """Documents context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get document contexts
    document_contexts = contexts.list_contexts(db, project_id=project_id) or []
    document_contexts = [ctx for ctx in document_contexts if ctx.context_type and ctx.context_type.value == 'resource_file']
    
    return render_template('context/documents.html', 
                         contexts=document_contexts,
                         total_documents=len(document_contexts))

@context_bp.route('/files')
def context_files():
    """Files context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get file contexts
    file_contexts = contexts.list_contexts(db, project_id=project_id) or []
    file_contexts = [ctx for ctx in file_contexts if ctx.file_path]
    
    # Group by file type
    file_types = {}
    for ctx in file_contexts:
        if ctx.file_path:
            ext = os.path.splitext(ctx.file_path)[1].lower()
            if ext not in file_types:
                file_types[ext] = []
            file_types[ext].append(ctx)
    
    return render_template('context/files.html', 
                         contexts=file_contexts,
                         file_types=file_types,
                         total_files=len(file_contexts))

@context_bp.route('/files/preview/<path:filepath>')
def preview_file(filepath: str):
    """Preview a file"""
    try:
        # Security check - ensure filepath is safe
        if '..' in filepath or filepath.startswith('/'):
            abort(403, description="Invalid file path")
        
        # For now, just return a placeholder
        # In a real implementation, you'd serve the file content
        return render_template('context/file_preview.html', 
                             filepath=filepath,
                             content="File preview not implemented yet")
        
    except Exception as e:
        logger.error(f"Error previewing file {filepath}: {e}")
        abort(500, description="Error previewing file")

@context_bp.route('/files/download/<path:filepath>')
def download_file(filepath: str):
    """Download a file"""
    try:
        # Security check - ensure filepath is safe
        if '..' in filepath or filepath.startswith('/'):
            abort(403, description="Invalid file path")
        
        # For now, just return a placeholder
        # In a real implementation, you'd serve the actual file
        abort(404, description="File download not implemented yet")
        
    except Exception as e:
        logger.error(f"Error downloading file {filepath}: {e}")
        abort(500, description="Error downloading file")
