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
from ...utils.pagination import paginate_items, get_pagination_from_request, get_query_params_from_request
from ....core.database.enums import EntityType

logger = logging.getLogger(__name__)

@documents_bp.route('/')
def documents_list():
    """Documents list view with comprehensive metrics, search, and pagination"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references, projects
        
        # Get pagination parameters
        page, per_page = get_pagination_from_request(request, default_per_page=20)
        
        projects_list = projects.list_projects(db) or []
        
        # Get filter parameters
        search_query = request.args.get('search', '').strip()
        current_project_id = request.args.get('project_id', type=int)
        current_document_type = request.args.get('document_type', '')
        current_sort = request.args.get('sort', 'created_desc')
        
        # Get documents - filter by project if specified and project exists
        if current_project_id and projects_list:
            # Check if the requested project exists
            project_exists = any(p.id == current_project_id for p in projects_list)
            if project_exists:
                documents = document_references.list_document_references(
                    db, entity_type=EntityType.PROJECT, entity_id=current_project_id
                ) or []
            else:
                # Project doesn't exist, show all documents
                documents = document_references.list_document_references(db) or []
        else:
            # No project filter or no projects available, show all documents
            documents = document_references.list_document_references(db) or []
        
        # Apply search filter
        if search_query:
            documents = [
                doc for doc in documents
                if search_query.lower() in (doc.title or '').lower() or 
                   search_query.lower() in (doc.file_path or '').lower()
            ]
        
        # Apply document type filter
        if current_document_type:
            documents = [doc for doc in documents if doc.document_type == current_document_type]
        
        # Apply sorting
        if current_sort == 'created_desc':
            documents.sort(key=lambda x: x.created_at or '', reverse=True)
        elif current_sort == 'created_asc':
            documents.sort(key=lambda x: x.created_at or '')
        elif current_sort == 'title_asc':
            documents.sort(key=lambda x: (x.title or '').lower())
        elif current_sort == 'title_desc':
            documents.sort(key=lambda x: (x.title or '').lower(), reverse=True)
        elif current_sort == 'type_asc':
            documents.sort(key=lambda x: (x.document_type or '').lower())
        elif current_sort == 'type_desc':
            documents.sort(key=lambda x: (x.document_type or '').lower(), reverse=True)
        
        # Apply pagination
        paginated_documents, pagination = paginate_items(
            items=documents,
            page=page,
            per_page=per_page,
            base_url=request.path,
            query_params=get_query_params_from_request(request)
        )
        
        # Calculate document types
        doc_types = {}
        for doc in documents:
            doc_type = doc.document_type or 'Unknown'
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Calculate recent documents (last 7 days)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_documents = len([
            doc for doc in documents 
            if doc.created_at and doc.created_at >= seven_days_ago
        ])
        
        # Calculate metrics
        metrics = {
            'total_documents': len(documents),
            'documents_with_content': len([doc for doc in documents if doc.content]),
            'documents_without_content': len([doc for doc in documents if not doc.content]),
        }
        
        return render_template('documents/list.html', 
                             documents=paginated_documents,
                             metrics=metrics,
                             search_query=search_query,
                             projects=projects_list,
                             current_project_id=current_project_id,
                             current_document_type=current_document_type,
                             current_sort=current_sort,
                             doc_types=doc_types,
                             total_documents=len(documents),
                             recent_documents=recent_documents,
                             pagination=pagination)
    
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        flash(f"Error loading documents: {str(e)}", 'error')
        return render_template('documents/list.html', 
                             documents=[],
                             metrics={'total_documents': 0},
                             search_query='',
                             projects=[],
                             current_project_id=None,
                             current_document_type='',
                             current_sort='created_desc',
                             doc_types={},
                             total_documents=0,
                             recent_documents=0)

@documents_bp.route('/search')
def search_documents():
    """Search documents"""
    try:
        db = get_database_service()
        from ....core.database.methods import document_references, projects
        
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get filter parameters
        search_query = request.args.get('q', '').strip()
        current_project_id = request.args.get('project_id', type=int)
        current_document_type = request.args.get('type', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Get all documents for filtering
        documents = document_references.list_document_references(db) or []
        
        # Calculate document types for filter dropdown
        doc_types = set()
        for doc in documents:
            if doc.document_type:
                doc_types.add(doc.document_type)
        doc_types = sorted(list(doc_types))
        
        if not search_query and not current_document_type and not current_project_id and not date_from and not date_to:
            return render_template('documents/search.html', 
                                 documents=[],
                                 search_query='',
                                 total_results=0,
                                 projects=projects_list,
                                 current_project_id=current_project_id,
                                 current_document_type=current_document_type,
                                 doc_types=doc_types,
                                 date_from=date_from,
                                 date_to=date_to)
        
        # Apply filters
        search_results = documents
        
        # Apply search query filter
        if search_query:
            search_results = [
                doc for doc in search_results
                if search_query.lower() in (doc.title or '').lower() or 
                   search_query.lower() in (doc.content or '').lower() or
                   search_query.lower() in (doc.file_path or '').lower()
            ]
        
        # Apply document type filter
        if current_document_type:
            search_results = [doc for doc in search_results if doc.document_type == current_document_type]
        
        # Apply project filter
        if current_project_id:
            search_results = [doc for doc in search_results if doc.project_id == current_project_id]
        
        # Apply date filters
        if date_from:
            from datetime import datetime
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                search_results = [doc for doc in search_results if doc.created_at and doc.created_at.date() >= date_from_obj]
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if date_to:
            from datetime import datetime
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                search_results = [doc for doc in search_results if doc.created_at and doc.created_at.date() <= date_to_obj]
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        return render_template('documents/search.html', 
                             documents=search_results,
                             search_query=search_query,
                             total_results=len(search_results),
                             projects=projects_list,
                             current_project_id=current_project_id,
                             current_document_type=current_document_type,
                             doc_types=doc_types,
                             date_from=date_from,
                             date_to=date_to)
    
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        flash(f"Error searching documents: {str(e)}", 'error')
        return render_template('documents/search.html', 
                             documents=[],
                             search_query=request.args.get('q', ''),
                             total_results=0,
                             projects=[],
                             current_project_id=None,
                             current_document_type='',
                             doc_types=[],
                             date_from='',
                             date_to='')
