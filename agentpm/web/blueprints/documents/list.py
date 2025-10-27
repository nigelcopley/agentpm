"""
Documents List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for documents including:
- Documents listing with filtering and search
- Document management and organization
"""

from flask import render_template, request, redirect, url_for, flash
import logging

from . import documents_bp
from ..utils import get_database_service, _is_htmx_request, validate_required_fields, handle_error

logger = logging.getLogger(__name__)

@documents_bp.route('/')
def documents_list():
    """Documents list view with comprehensive metrics and search"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references, projects
        
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get filter parameters
        search_query = request.args.get('search', '').strip()
        
        # Get documents
        documents = document_references.list_document_references(db, project_id=project_id) or []
        
        # Apply search filter
        if search_query:
            documents = [
                doc for doc in documents
                if search_query.lower() in (doc.title or '').lower() or 
                   search_query.lower() in (doc.file_path or '').lower()
            ]
        
        # Calculate metrics
        metrics = {
            'total_documents': len(documents),
            'documents_with_content': len([doc for doc in documents if doc.content]),
            'documents_without_content': len([doc for doc in documents if not doc.content]),
        }
        
        return render_template('documents/list.html', 
                             documents=documents,
                             metrics=metrics,
                             search_query=search_query)
    
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        flash(f"Error loading documents: {str(e)}", 'error')
        return render_template('documents/list.html', 
                             documents=[],
                             metrics={'total_documents': 0},
                             search_query='')

@documents_bp.route('/search')
def search_documents():
    """Search documents"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references, projects
        
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        search_query = request.args.get('q', '').strip()
        
        if not search_query:
            return render_template('documents/search.html', 
                                 documents=[],
                                 search_query='',
                                 total_results=0)
        
        # Search documents
        documents = document_references.list_document_references(db, project_id=project_id) or []
        search_results = [
            doc for doc in documents
            if search_query.lower() in (doc.title or '').lower() or 
               search_query.lower() in (doc.content or '').lower() or
               search_query.lower() in (doc.file_path or '').lower()
        ]
        
        return render_template('documents/search.html', 
                             documents=search_results,
                             search_query=search_query,
                             total_results=len(search_results))
    
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        flash(f"Error searching documents: {str(e)}", 'error')
        return render_template('documents/search.html', 
                             documents=[],
                             search_query=request.args.get('q', ''),
                             total_results=0)
