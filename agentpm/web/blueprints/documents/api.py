"""
Documents API Module for APM (Agent Project Manager) Web Application

Handles API-related functionality for documents including:
- RESTful API endpoints
- JSON responses for AJAX requests
"""

from flask import jsonify, request
import logging

from . import documents_bp
from ..utils import get_database_service, create_success_response, create_error_response

logger = logging.getLogger(__name__)

@documents_bp.route('/api/documents')
def api_documents():
    """API endpoint for documents list"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references, projects
        
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get documents
        documents = document_references.list_document_references(db, project_id=project_id) or []
        
        # Convert to JSON-serializable format
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'file_path': doc.file_path,
                'content': doc.content,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
            })
        
        return jsonify(create_success_response('Documents retrieved successfully', {
            'documents': documents_data,
            'total_count': len(documents_data)
        }))
    
    except Exception as e:
        logger.error(f"Error in API documents: {e}")
        return create_error_response('Error retrieving documents', 500)
