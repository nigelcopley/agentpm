"""
Tasks Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for tasks including:
- Individual task detail views
- Task creation and editing
- Task deletion
- Status updates
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from flask import render_template, abort, request, redirect, url_for, jsonify, flash

from ....core.database.methods import (
    tasks, 
    work_items, 
    projects, 
    dependencies, 
    events,
    contexts,
    document_references,
    agents
)
from ....core.database.models import Task, DocumentReference
from ....core.database.enums import (
    EntityType, 
    TaskType, 
    TaskStatus,
    DocumentType, 
    DocumentCategory,
    DocumentFormat, 
    StorageMode
)
from ....core.context.unified_service import UnifiedContextService
from ..utils import get_database_service
from . import tasks_bp

logger = logging.getLogger(__name__)

@tasks_bp.route('/<int:task_id>')
def task_detail(task_id: int):
    """
    Comprehensive task detail view.
    
    Shows all task information in a single view:
    - Basic information (name, description, status, type, effort)
    - Work item context
    - Dependencies and blockers
    - Timeline and history
    - Quality metadata
    - Agent assignments
    """
    # Fetch task data
    db = get_database_service()
    
    task = tasks.get_task(db, task_id)
    
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    # Get related work item
    work_item = work_items.get_work_item(db, task.work_item_id) if task.work_item_id else None
    
    # Get project information
    project = None
    if work_item:
        projects_list = projects.list_projects(db) or []
        project = next((p for p in projects_list if p.id == work_item.project_id), None)
    
    # Get task dependencies
    task_dependencies = []
    try:
        task_dependencies = dependencies.get_task_dependencies(db, task_id)
    except Exception:
        pass  # Dependencies might not be implemented yet
    
    # Get task blockers
    task_blockers = []
    try:
        task_blockers = dependencies.get_task_blockers(db, task_id)
    except Exception:
        pass  # Blockers might not be implemented yet
    
    # Get comprehensive task context using UnifiedContextService
    task_contexts = []
    context_payload = None
    
    try:
        # Get rich contexts using the existing method
        
        task_contexts = contexts.get_rich_contexts_by_entity(
            db, EntityType.TASK, task_id
        ) or []
        
        # Get unified context for comprehensive hierarchical context
        
        # Get project path for context service
        project_path = Path(project.path) if project and project.path else Path.cwd()
        context_service = UnifiedContextService(db, project_path)
        
        # Get comprehensive context payload
        context_payload = context_service.get_context(
            EntityType.TASK,
            task_id=task_id,
            include_supporting=True,  # Include documents, evidence, events
            include_code=True         # Include plugin facts, amalgamations
        )
        
        logger.info(f"Retrieved unified context for task {task_id}")
        
    except Exception as e:
        logger.warning(f"Error fetching task contexts: {e}")
        logger.error(f"Task context error traceback: {traceback.format_exc()}")
    
    # Get task documents
    task_documents = []
    documents_by_type = {}
    documents_by_category = {}
    
    try:
        
        # Get all documents for this task
        task_documents = document_references.get_documents_by_entity(
            db, EntityType.TASK, task_id
        ) or []
        
        # Group documents by type and category for better organisation
        for doc in task_documents:
            # Group by document type
            doc_type = doc.document_type.value if doc.document_type else 'other'
            if doc_type not in documents_by_type:
                documents_by_type[doc_type] = []
            documents_by_type[doc_type].append(doc)
            
            # Group by category
            category = doc.category or 'uncategorised'
            if category not in documents_by_category:
                documents_by_category[category] = []
            documents_by_category[category].append(doc)
        
        logger.info(f"Retrieved {len(task_documents)} documents for task {task_id}")
        
    except Exception as e:
        logger.warning(f"Error fetching task documents: {e}")
        logger.error(f"Task document error traceback: {traceback.format_exc()}")
    
    # Get task events/timeline
    task_events = []
    try:
        task_events = events.get_events_for_task(db, task_id)
    except Exception:
        pass  # Events might not be implemented yet
    
    # Calculate task statistics
    task_stats = {
        'is_active': task.is_active(),
        'is_blocked': task.is_blocked(),
        'is_complete': task.is_complete(),
        'can_start': task.can_start(),
        'days_since_created': (datetime.now() - task.created_at).days if task.created_at else None,
        'days_since_started': (datetime.now() - task.started_at).days if task.started_at else None,
        'days_since_completed': (datetime.now() - task.completed_at).days if task.completed_at else None,
        'has_dependencies': len(task_dependencies) > 0,
        'has_blockers': len(task_blockers) > 0,
        'has_events': len(task_events) > 0,
        'has_contexts': len(task_contexts) > 0,
        'has_unified_context': context_payload is not None,
        'has_documents': len(task_documents) > 0,
    }
    
    return render_template('tasks/detail.html', 
                         task=task,
                         task_id=task_id,
                         work_item=work_item,
                         project=project,
                         task_dependencies=task_dependencies,
                         task_blockers=task_blockers,
                         task_events=task_events,
                         task_contexts=task_contexts,
                         context_payload=context_payload,
                         task_documents=task_documents,
                         documents_by_type=documents_by_type,
                         documents_by_category=documents_by_category,
                         task_stats=task_stats)

@tasks_bp.route('/create', methods=['GET', 'POST'])
def create_task():
    """Create a new task"""
    if request.method == 'GET':
        # Show create form
        db = get_database_service()
        
        work_items_list = work_items.list_work_items(db) or []
        
        # Get project ID for agents
        projects_list = projects.list_projects(db) or []
        project_id = projects_list[0].id if projects_list else 1
        
        # Get active agents for assignment dropdown
        agents_list = agents.list_agents(db, project_id=project_id, active_only=True) or []
        
        return render_template('tasks/create.html',
                             work_items=work_items_list,
                             agents=agents_list,
                             task_types=TaskType,
                             task_statuses=TaskStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            db = get_database_service()
            
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            task_type = request.form.get('type', 'implementation')
            effort_hours = request.form.get('effort_hours')
            effort_hours = float(effort_hours) if effort_hours else None
            priority = int(request.form.get('priority', 3))
            assigned_to = request.form.get('assigned_to', '').strip()
            work_item_id = int(request.form.get('work_item_id', 1))
            due_date = request.form.get('due_date')
            due_date = datetime.fromisoformat(due_date) if due_date else None
            
            # Validate required fields
            if not name:
                flash('Task name is required', 'error')
                return redirect(url_for('tasks.create_task'))
            
            if not work_item_id:
                flash('Work item is required', 'error')
                return redirect(url_for('tasks.create_task'))
            
            # Create task
            task = Task(
                name=name,
                description=description if description else None,
                type=TaskType(task_type),
                effort_hours=effort_hours,
                priority=priority,
                assigned_to=assigned_to if assigned_to else None,
                work_item_id=work_item_id,
                due_date=due_date,
                status=TaskStatus.DRAFT
            )
            
            created_task = tasks.create_task(db, task)
            
            flash(f'Task "{created_task.name}" created successfully', 'success')
            return redirect(url_for('tasks.task_detail', task_id=created_task.id))
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            flash(f'Error creating task: {str(e)}', 'error')
            return redirect(url_for('tasks.create_task'))

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id: int):
    """Edit an existing task"""
    db = get_database_service()
    
    task = tasks.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    if request.method == 'GET':
        # Show edit form
        work_items_list = work_items.list_work_items(db) or []
        
        return render_template('tasks/edit.html',
                             task=task,
                             work_items=work_items_list,
                             task_types=TaskType,
                             task_statuses=TaskStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            task_type = request.form.get('type', 'implementation')
            effort_hours = request.form.get('effort_hours')
            effort_hours = float(effort_hours) if effort_hours else None
            priority = int(request.form.get('priority', 3))
            assigned_to = request.form.get('assigned_to', '').strip()
            work_item_id = int(request.form.get('work_item_id', 1))
            status = request.form.get('status', 'draft')
            due_date = request.form.get('due_date')
            due_date = datetime.fromisoformat(due_date) if due_date else None
            blocked_reason = request.form.get('blocked_reason', '').strip()
            
            # Validate required fields
            if not name:
                flash('Task name is required', 'error')
                return redirect(url_for('tasks.edit_task', task_id=task_id))
            
            if not work_item_id:
                flash('Work item is required', 'error')
                return redirect(url_for('tasks.edit_task', task_id=task_id))
            
            # Update task
            task.name = name
            task.description = description if description else None
            task.type = TaskType(task_type)
            task.effort_hours = effort_hours
            task.priority = priority
            task.assigned_to = assigned_to if assigned_to else None
            task.work_item_id = work_item_id
            task.status = TaskStatus(status)
            task.due_date = due_date
            task.blocked_reason = blocked_reason if blocked_reason else None
            
            # Update timestamps based on status changes
            if status == 'in_progress' and not task.started_at:
                task.started_at = datetime.now()
            elif status in ['done', 'cancelled'] and not task.completed_at:
                task.completed_at = datetime.now()
            
            updated_task = tasks.update_task(db, task)
            
            flash(f'Task "{updated_task.name}" updated successfully', 'success')
            return redirect(url_for('tasks.task_detail', task_id=updated_task.id))
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            flash(f'Error updating task: {str(e)}', 'error')
            return redirect(url_for('tasks.edit_task', task_id=task_id))

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id: int):
    """Delete a task"""
    try:
        db = get_database_service()
        
        task = tasks.get_task(db, task_id)
        if not task:
            abort(404, description=f"Task {task_id} not found")
        
        tasks.delete_task(db, task_id)
        
        flash(f'Task "{task.name}" deleted successfully', 'success')
        return redirect(url_for('tasks.tasks_list'))
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        flash(f'Error deleting task: {str(e)}', 'error')
        return redirect(url_for('tasks.task_detail', task_id=task_id))

@tasks_bp.route('/<int:task_id>/documents/create', methods=['GET', 'POST'])
def create_task_document(task_id: int):
    """Create a new document for a task"""
    db = get_database_service()
    
    task = tasks.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    if request.method == 'GET':
        # Show create document form
        return render_template('tasks/create_document.html',
                             task=task,
                             task_id=task_id,
                             document_types=DocumentType,
                             document_formats=DocumentFormat)
    
    elif request.method == 'POST':
        # Process document creation
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            document_type = request.form.get('document_type', 'other')
            category = request.form.get('category', '').strip()
            content = request.form.get('content', '').strip()
            filename = request.form.get('filename', '').strip()
            format_type = request.form.get('format', 'markdown')
            
            # Validate required fields
            if not title:
                flash('Document title is required', 'error')
                return redirect(url_for('tasks.create_task_document', task_id=task_id))
            
            if not filename:
                flash('Filename is required', 'error')
                return redirect(url_for('tasks.create_task_document', task_id=task_id))
            
            # Generate file path
            file_path = f"docs/{category or 'tasks'}/{document_type}/{filename}"
            if not file_path.endswith('.md') and format_type == 'markdown':
                file_path += '.md'
            
            # Create document reference
            document = DocumentReference(
                entity_type=EntityType.TASK,
                entity_id=task_id,
                category=category if category else 'tasks',
                document_type=DocumentType(document_type),
                file_path=file_path,
                title=title,
                description=description if description else None,
                filename=filename,
                format=DocumentFormat(format_type),
                content=content if content else None,
                storage_mode=StorageMode.HYBRID,
                work_item_id=task.work_item_id
            )
            
            created_document = document_references.create_document_reference(db, document)
            
            flash(f'Document "{created_document.title}" created successfully', 'success')
            return redirect(url_for('tasks.task_detail', task_id=task_id))
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            flash(f'Error creating document: {str(e)}', 'error')
            return redirect(url_for('tasks.create_task_document', task_id=task_id))

@tasks_bp.route('/<int:task_id>/documents/<int:document_id>')
def view_task_document(task_id: int, document_id: int):
    """View a task document"""
    db = get_database_service()
    
    task = tasks.get_task(db, task_id)
    if not task:
        abort(404, description=f"Task {task_id} not found")
    
    document = document_references.get_document_reference(db, document_id)
    if not document:
        abort(404, description=f"Document {document_id} not found")
    
    # Verify document belongs to task
    if document.entity_type.value != 'task' or document.entity_id != task_id:
        abort(404, description=f"Document {document_id} does not belong to task {task_id}")
    
    return render_template('tasks/view_document.html',
                         task=task,
                         document=document,
                         task_id=task_id,
                         document_id=document_id)

@tasks_bp.route('/<int:task_id>/update-status', methods=['POST'])
def update_task_status(task_id: int):
    """Update task status via AJAX"""
    try:
        db = get_database_service()
        
        task = tasks.get_task(db, task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        new_status = request.json.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        try:
            task.status = TaskStatus(new_status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update timestamps based on status changes
        if new_status == 'in_progress' and not task.started_at:
            task.started_at = datetime.now()
        elif new_status in ['done', 'cancelled'] and not task.completed_at:
            task.completed_at = datetime.now()
        
        updated_task = tasks.update_task(db, task)
        
        return jsonify({
            'success': True,
            'status': updated_task.status.value,
            'message': f'Status updated to {updated_task.status.value}'
        })
        
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        return jsonify({'error': str(e)}), 500
