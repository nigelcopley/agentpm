"""
Documents Blueprint for APM (Agent Project Manager) Web Application

Handles document management functionality including:
- Document listing and filtering
- Document creation and editing
- Document viewing and metadata
- Document search and organisation
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from datetime import datetime, timedelta
import logging
import os

from ...core.database.methods import document_references
from ...core.database.methods import projects as project_methods
from ...core.database.enums import EntityType, DocumentType
from ...core.database.methods import work_items as work_item_methods
from ...core.database.methods import tasks as task_methods

# Import helper functions from app
def get_database_service():
    """Get database service instance"""
    from ...core.database.service import DatabaseService
    import os
    
    # Try different database paths
    db_paths = [
        '.aipm/data/aipm.db',
        '../.aipm/data/aipm.db',
        '../../.aipm/data/aipm.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            return DatabaseService(db_path)
    
    # If no database found, return service with default path
    return DatabaseService('.aipm/data/aipm.db')

# Create documents blueprint
documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

logger = logging.getLogger(__name__)


@documents_bp.route('/')
def documents_list():
    """Documents list view with filtering and search capabilities."""
    try:
        db = get_database_service()
        
        # Get filter parameters
        project_id = request.args.get('project_id', type=int)
        document_type_str = request.args.get('document_type')
        sort_by = request.args.get('sort', 'created_desc')
        limit = request.args.get('limit', 50, type=int)
        search_query = request.args.get('search', '').strip()
        
        # Convert document_type string to enum if provided
        document_type = None
        if document_type_str:
            try:
                document_type = DocumentType(document_type_str)
            except ValueError:
                # Invalid document type, ignore filter
                document_type = None
        
        # Get document references
        documents_list = document_references.list_document_references(
            db,
            entity_type=EntityType.PROJECT if project_id else None,
            entity_id=project_id,
            document_type=document_type,
            limit=limit
        )
        
        # Apply search filter if provided
        if search_query:
            search_lower = search_query.lower()
            documents_list = [
                doc for doc in documents_list
                if (search_lower in (doc.title or '').lower() or
                    search_lower in (doc.description or '').lower() or
                    search_lower in (doc.file_path or '').lower())
            ]
        
        # Apply sorting
        if sort_by == 'created_desc':
            documents_list.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        elif sort_by == 'created_asc':
            documents_list.sort(key=lambda x: x.created_at or datetime.min, reverse=False)
        elif sort_by == 'title_asc':
            documents_list.sort(key=lambda x: (x.title or '').lower())
        elif sort_by == 'title_desc':
            documents_list.sort(key=lambda x: (x.title or '').lower(), reverse=True)
        elif sort_by == 'path_asc':
            documents_list.sort(key=lambda x: (x.file_path or '').lower())
        elif sort_by == 'path_desc':
            documents_list.sort(key=lambda x: (x.file_path or '').lower(), reverse=True)
        elif sort_by == 'type_asc':
            documents_list.sort(key=lambda x: (x.document_type or '').lower())
        elif sort_by == 'type_desc':
            documents_list.sort(key=lambda x: (x.document_type or '').lower(), reverse=True)
        
        # Get projects for filter dropdown
        projects = project_methods.list_projects(db)
        
        # Get document type distribution
        doc_types = {}
        for doc in documents_list:
            dtype = doc.document_type or 'unknown'
            doc_types[dtype] = doc_types.get(dtype, 0) + 1
        
        # Calculate metrics
        total_documents = len(documents_list)
        recent_documents = len([
            doc for doc in documents_list
            if doc.created_at and doc.created_at > datetime.now() - timedelta(days=7)
        ])
        
        return render_template(
            'documents/list.html',
            documents=documents_list,
            projects=projects,
            doc_types=doc_types,
            current_project_id=project_id,
            current_document_type=document_type_str,
            current_sort=sort_by,
            search_query=search_query,
            total_documents=total_documents,
            recent_documents=recent_documents,
            show_sidebar='documents'
        )
        
    except Exception as e:
        logger.error(f"Error in documents_list: {e}")
        flash(f"Error loading documents: {str(e)}", 'error')
        return render_template('documents/list.html', documents=[], projects=[], doc_types={})


@documents_bp.route('/<int:document_id>')
def document_detail(document_id: int):
    """Comprehensive document detail view showing all fields and content."""
    try:
        db = get_database_service()
        
        # Get document
        document = document_references.get_document_reference(db, document_id)
        
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        # Get related entities
        related_work_items = []
        related_tasks = []
        
        if document.entity_type and document.entity_id:
            if document.entity_type == EntityType.WORK_ITEM:
                work_item = work_item_methods.get_work_item(db, document.entity_id)
                if work_item:
                    related_work_items = [work_item]
            elif document.entity_type == EntityType.TASK:
                task = task_methods.get_task(db, document.entity_id)
                if task:
                    related_tasks = [task]
        
        # Check if file exists and get file info
        file_exists = False
        file_size = 0
        file_modified = None
        if document.file_path and os.path.exists(document.file_path):
            file_exists = True
            file_size = os.path.getsize(document.file_path)
            file_modified = datetime.fromtimestamp(os.path.getmtime(document.file_path))
        
        # Parse document content if not already stored
        document_content = document.content
        content_source = "database"
        
        if not document_content and file_exists:
            try:
                # Try to read file content
                with open(document.file_path, 'r', encoding='utf-8') as f:
                    document_content = f.read()
                content_source = "file"
            except Exception as e:
                logger.warning(f"Could not read file content for {document.file_path}: {e}")
                document_content = None
                content_source = "unavailable"
        
        # Parse document metadata
        parsed_path = None
        if document.file_path and document.file_path.startswith('docs/'):
            try:
                parsed_path = document.parse_path(document.file_path)
            except ValueError:
                parsed_path = None
        
        # Get document type labels for display
        document_type_label = None
        if document.document_type:
            try:
                document_type_label = DocumentType.labels().get(document.document_type.value, document.document_type.value.title())
            except:
                document_type_label = str(document.document_type.value).title() if document.document_type else None
        
        # Get format label
        format_label = None
        if document.format:
            format_label = document.format.value.upper()
        
        # Get storage mode label
        storage_mode_label = None
        if document.storage_mode:
            storage_mode_label = document.storage_mode.value.replace('_', ' ').title()
        
        # Get sync status label
        sync_status_label = None
        if document.sync_status:
            sync_status_label = document.sync_status.value.replace('_', ' ').title()
        
        return render_template(
            'documents/detail.html',
            document=document,
            related_work_items=related_work_items,
            related_tasks=related_tasks,
            file_exists=file_exists,
            file_size=file_size,
            file_modified=file_modified,
            document_content=document_content,
            content_source=content_source,
            parsed_path=parsed_path,
            document_type_label=document_type_label,
            format_label=format_label,
            storage_mode_label=storage_mode_label,
            sync_status_label=sync_status_label,
            show_sidebar='documents'
        )
        
    except Exception as e:
        logger.error(f"Error in document_detail: {e}")
        flash(f"Error loading document: {str(e)}", 'error')
        return redirect(url_for('documents.documents_list'))


@documents_bp.route('/create', methods=['GET', 'POST'])
def document_create():
    """Create new document reference."""
    try:
        db = get_database_service()
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            file_path = request.form.get('file_path', '').strip()
            document_type = request.form.get('document_type', '').strip()
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id', type=int)
            
            # Validation
            if not title:
                flash('Title is required', 'error')
                return render_template('documents/create.html', projects=project_methods.list_projects(db))
            
            if not file_path:
                flash('File path is required', 'error')
                return render_template('documents/create.html', projects=project_methods.list_projects(db))
            
            # Convert document_type to enum
            doc_type_enum = None
            if document_type:
                try:
                    doc_type_enum = DocumentType(document_type)
                except ValueError:
                    doc_type_enum = DocumentType.OTHER
            
            # Create document reference
            document_data = {
                'title': title,
                'description': description,
                'file_path': file_path,
                'document_type': doc_type_enum or DocumentType.OTHER,
                'entity_type': EntityType(entity_type) if entity_type else None,
                'entity_id': entity_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            document_id = document_references.create_document_reference(db, document_data)
            
            if document_id:
                flash(f'Document "{title}" created successfully', 'success')
                return redirect(url_for('documents.document_detail', document_id=document_id))
            else:
                flash('Failed to create document', 'error')
        
        # GET request - show form
        projects = project_methods.list_projects(db)
        return render_template('documents/create.html', projects=projects)
        
    except Exception as e:
        logger.error(f"Error in document_create: {e}")
        flash(f"Error creating document: {str(e)}", 'error')
        return redirect(url_for('documents.documents_list'))


@documents_bp.route('/<int:document_id>/edit', methods=['GET', 'POST'])
def document_edit(document_id: int):
    """Edit existing document reference."""
    try:
        db = get_database_service()
        
        # Get document
        document = document_references.get_document_reference(db, document_id)
        
        if not document:
            abort(404, description=f"Document {document_id} not found")
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            file_path = request.form.get('file_path', '').strip()
            document_type = request.form.get('document_type', '').strip()
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id', type=int)
            
            # Validation
            if not title:
                flash('Title is required', 'error')
                return render_template('documents/edit.html', document=document, projects=project_methods.list_projects(db))
            
            if not file_path:
                flash('File path is required', 'error')
                return render_template('documents/edit.html', document=document, projects=project_methods.list_projects(db))
            
            # Update document reference
            update_data = {
                'title': title,
                'description': description,
                'file_path': file_path,
                'document_type': document_type or 'general',
                'entity_type': EntityType(entity_type) if entity_type else None,
                'entity_id': entity_id,
                'updated_at': datetime.now()
            }
            
            success = document_references.update_document_reference(db, document_id, update_data)
            
            if success:
                flash(f'Document "{title}" updated successfully', 'success')
                return redirect(url_for('documents.document_detail', document_id=document_id))
            else:
                flash('Failed to update document', 'error')
        
        # GET request - show form
        projects = project_methods.list_projects(db)
        return render_template('documents/edit.html', document=document, projects=projects)
        
    except Exception as e:
        logger.error(f"Error in document_edit: {e}")
        flash(f"Error editing document: {str(e)}", 'error')
        return redirect(url_for('documents.documents_list'))


@documents_bp.route('/<int:document_id>/delete', methods=['POST'])
def document_delete(document_id: int):
    """Delete document reference."""
    try:
        db = get_database_service()
        
        # Get document for confirmation
        document = document_references.get_document_reference(db, document_id)
        
        if not document:
            flash('Document not found', 'error')
            return redirect(url_for('documents.documents_list'))
        
        # Delete document reference
        success = document_references.delete_document_reference(db, document_id)
        
        if success:
            flash(f'Document "{document.title}" deleted successfully', 'success')
        else:
            flash('Failed to delete document', 'error')
        
        return redirect(url_for('documents.documents_list'))
        
    except Exception as e:
        logger.error(f"Error in document_delete: {e}")
        flash(f"Error deleting document: {str(e)}", 'error')
        return redirect(url_for('documents.documents_list'))


@documents_bp.route('/search')
def document_search():
    """Advanced document search with multiple criteria."""
    try:
        db = get_database_service()
        
        # Get search parameters
        query = request.args.get('q', '').strip()
        document_type = request.args.get('type')
        project_id = request.args.get('project_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build search criteria
        search_criteria = {}
        if document_type:
            search_criteria['document_type'] = document_type
        if project_id:
            search_criteria['entity_type'] = EntityType.PROJECT
            search_criteria['entity_id'] = project_id
        
        # Get documents
        documents = document_references.list_document_references(db, **search_criteria)
        
        # Apply text search
        if query:
            query_lower = query.lower()
            documents = [
                doc for doc in documents
                if (query_lower in (doc.title or '').lower() or
                    query_lower in (doc.description or '').lower() or
                    query_lower in (doc.file_path or '').lower())
            ]
        
        # Apply date filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                documents = [doc for doc in documents if doc.created_at and doc.created_at >= from_date]
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                documents = [doc for doc in documents if doc.created_at and doc.created_at <= to_date]
            except ValueError:
                pass
        
        # Get projects for filter dropdown
        projects = project_methods.list_projects(db)
        
        # Get document types
        doc_types = set(doc.document_type for doc in documents if doc.document_type)
        
        return render_template(
            'documents/search.html',
            documents=documents,
            projects=projects,
            doc_types=doc_types,
            search_query=query,
            current_document_type=document_type,
            current_project_id=project_id,
            date_from=date_from,
            date_to=date_to,
            show_sidebar='documents'
        )
        
    except Exception as e:
        logger.error(f"Error in document_search: {e}")
        flash(f"Error searching documents: {str(e)}", 'error')
        return render_template('documents/search.html', documents=[], projects=[], doc_types=set())


@documents_bp.route('/api/documents')
def api_documents():
    """API endpoint for document data (for AJAX requests)."""
    try:
        db = get_database_service()
        
        # Get parameters
        project_id = request.args.get('project_id', type=int)
        document_type = request.args.get('document_type')
        limit = request.args.get('limit', 20, type=int)
        
        # Get documents
        documents = document_references.list_document_references(
            db,
            entity_type=EntityType.PROJECT if project_id else None,
            entity_id=project_id,
            document_type=document_type,
            limit=limit
        )
        
        # Convert to JSON-serializable format
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'file_path': doc.file_path,
                'document_type': doc.document_type,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'documents': documents_data,
            'total': len(documents_data)
        })
        
    except Exception as e:
        logger.error(f"Error in api_documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
