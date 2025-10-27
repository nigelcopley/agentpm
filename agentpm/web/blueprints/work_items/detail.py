"""
Work Items Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for work items including:
- Individual work item detail views with comprehensive context
- Work item creation and editing
- Work item deletion
- Status updates
- Task management within work items
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from flask import render_template, abort, request, redirect, url_for, jsonify, flash

from ....core.database.methods import (
    work_items, tasks,
    agents,
    contexts,
    ideas,
    projects,
    document_references
)
from ....core.database.models import WorkItem, DocumentReference
from ....core.database.enums import (
    EntityType, 
    ContextType, 
    DocumentType, 
    DocumentCategory,
    Phase, 
    TaskType, 
    WorkItemType, 
    WorkItemStatus,
    DocumentFormat, 
    StorageMode
)
from ....core.context.unified_service import UnifiedContextService
from ....core.workflow.phase_validator import PhaseValidator
from ..utils import get_database_service
from . import work_items_bp

logger = logging.getLogger(__name__)

@work_items_bp.route('/<int:work_item_id>')
def work_item_detail(work_item_id: int):
    """
    Comprehensive work item detail view.
    
    Shows all work item information in a single view:
    - Basic information (name, description, status, priority)
    - Task summaries (progress, decisions, etc.)
    - Agent assignments
    - Timeline and history
    - Related work item context
    - Dependencies and relationships
    - Phase information and validation
    - Business and technical context
    """
    # Fetch work item data
    db = get_database_service()
    
    work_item = work_items.get_work_item(db, work_item_id)
    
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    # Get related data
    tasks_list = tasks.list_tasks(db, work_item_id=work_item_id) or []
    agents_list = agents.list_agents(db) or []
    
    # Get project information
    project = None
    if work_item.project_id:
        projects_list = projects.list_projects(db) or []
        project = next((p for p in projects_list if p.id == work_item.project_id), None)
    
    # Get comprehensive work item context using UnifiedContextService
    work_item_contexts = []
    unified_context = None
    context_payload = None
    
    try:
        # Get ALL contexts using the new method (including those without context_data)
        work_item_contexts = contexts.get_all_contexts_by_entity(
            db, EntityType.WORK_ITEM, work_item_id
        ) or []
        
        logger.info(f"Retrieved {len(work_item_contexts)} work item contexts")
        
        # Get unified context for comprehensive hierarchical context
        
        # Get project path for context service
        project_path = Path(project.path) if project and project.path else Path.cwd()
        context_service = UnifiedContextService(db, project_path)
        
        # Get comprehensive context payload
        context_payload = context_service.get_context(
            EntityType.WORK_ITEM,
            work_item_id=work_item_id,
            include_supporting=True,  # Include documents, evidence, events
            include_code=True         # Include plugin facts, amalgamations
        )
        
        logger.info(f"Retrieved unified context for work item {work_item_id}")
        
    except Exception as e:
        logger.warning(f"Error fetching work item contexts: {e}")
        logger.error(f"Context error traceback: {traceback.format_exc()}")
    
    # Get work item documents
    work_item_documents = []
    documents_by_type = {}
    documents_by_category = {}
    
    try:
        
        # Get all documents for this work item
        work_item_documents = document_references.get_documents_by_entity(
            db, EntityType.WORK_ITEM, work_item_id
        ) or []
        
        # Group documents by type and category for better organisation
        for doc in work_item_documents:
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
        
        logger.info(f"Retrieved {len(work_item_documents)} documents for work item {work_item_id}")
        
    except Exception as e:
        logger.warning(f"Error fetching work item documents: {e}")
        logger.error(f"Document error traceback: {traceback.format_exc()}")
    
    # Aggregate documents and context from child tasks
    child_task_documents = []
    child_task_contexts = []
    
    try:
        
        # Get task IDs for bulk queries
        task_ids = [task.id for task in tasks_list]
        
        # Efficiently get documents from all child tasks in one query
        if task_ids:
            child_task_documents = document_references.get_documents_by_entity_ids(
                db, EntityType.TASK, task_ids
            )
            
            # Efficiently get contexts from all child tasks in one query
            child_task_contexts = contexts.get_all_contexts_by_entity_ids(
                db, EntityType.TASK, task_ids
            )
        else:
            child_task_documents = []
            child_task_contexts = []
        
        # Merge child task documents with work item documents
        all_documents = work_item_documents + child_task_documents
        
        # Reorganize merged documents by type and category
        documents_by_type = {}
        documents_by_category = {}
        
        for doc in all_documents:
            # Group by document type
            doc_type = doc.document_type.value if doc.document_type else 'unknown'
            if doc_type not in documents_by_type:
                documents_by_type[doc_type] = []
            documents_by_type[doc_type].append(doc)
            
            # Group by category
            category = doc.category.value if doc.category else 'uncategorized'
            if category not in documents_by_category:
                documents_by_category[category] = []
            documents_by_category[category].append(doc)
        
        # Update the variables with merged data
        work_item_documents = all_documents
        
        # Merge child task contexts with work item contexts
        work_item_contexts.extend(child_task_contexts)
        
        logger.info(f"Aggregated {len(child_task_documents)} documents from {len(tasks_list)} child tasks")
        logger.info(f"Aggregated {len(child_task_contexts)} contexts from child tasks")
        logger.info(f"Total contexts after aggregation: {len(work_item_contexts)}")
        
    except Exception as e:
        logger.warning(f"Error aggregating child task documents and context: {e}")
        logger.error(f"Child task aggregation error traceback: {traceback.format_exc()}")
    
    # Get related idea if exists
    related_idea = None
    if work_item.originated_from_idea_id:
        try:
            related_idea = ideas.get_idea(db, work_item.originated_from_idea_id)
        except Exception as e:
            logger.warning(f"Error fetching related idea: {e}")
    
    # Get parent work item if exists
    parent_work_item = None
    if work_item.parent_work_item_id:
        try:
            parent_work_item = work_items.get_work_item(db, work_item.parent_work_item_id)
        except Exception as e:
            logger.warning(f"Error fetching parent work item: {e}")
    
    # Get child work items
    child_work_items = []
    try:
        all_work_items = work_items.list_work_items(db, project_id=work_item.project_id) or []
        child_work_items = [wi for wi in all_work_items if wi.parent_work_item_id == work_item_id]
    except Exception as e:
        logger.warning(f"Error fetching child work items: {e}")
    
    # Calculate task statistics
    tasks_count = len(tasks_list)
    completed_tasks = sum(1 for task in tasks_list if task.status and task.status.value == 'done')
    in_progress_tasks = sum(1 for task in tasks_list if task.status and task.status.value in ['in_progress', 'active'])
    blocked_tasks = sum(1 for task in tasks_list if task.status and task.status.value == 'blocked')
    pending_tasks = sum(1 for task in tasks_list if task.status and task.status.value in ['pending', 'ready'])
    
    # Calculate progress percentage
    progress_percentage = 0
    if tasks_count > 0:
        progress_percentage = round((completed_tasks / tasks_count) * 100, 1)
    
    # Get business and technical context
    business_context = None
    technical_context = None
    
    for context in work_item_contexts:
        if context.context_type == ContextType.BUSINESS_PILLARS_CONTEXT:
            business_context = context
        elif context.context_type == ContextType.TECHNICAL_CONTEXT:
            technical_context = context
    
    # Calculate effort statistics
    total_estimated_hours = sum(task.effort_hours or 0 for task in tasks_list)
    total_logged_hours = 0  # Task model doesn't have logged hours field yet
    
    # Get phase information and requirements
    phase_info = None
    phase_validation = None
    phase_content = {}
    
    try:
        
        # Get phase validator instance
        phase_validator = PhaseValidator()
        
        # Get phase requirements for this work item type
        phase_requirements = None
        if work_item.phase:
            phase_requirements = phase_validator.get_phase_requirements(work_item.phase, work_item.type)
        
        # Get all phases for this work item type
        all_phases = phase_validator.get_allowed_phases(work_item.type)
        
        # Get phase-specific content for each phase
        for phase in all_phases:
            try:
                phase_content[phase.value] = {
                    'tasks': [],
                    'contexts': [],
                    'deliverables': [],
                    'status': 'pending'
                }
                
                # Determine phase status
                if work_item.phase:
                    current_phase_index = all_phases.index(work_item.phase) if work_item.phase in all_phases else -1
                    phase_index = all_phases.index(phase)
                    
                    if phase_index < current_phase_index:
                        phase_content[phase.value]['status'] = 'completed'
                    elif phase_index == current_phase_index:
                        phase_content[phase.value]['status'] = 'current'
                    else:
                        phase_content[phase.value]['status'] = 'pending'
                
                # Get tasks for this phase (filter by task type that typically belongs to this phase)
                phase_task_types = _get_phase_task_types(phase)
                phase_tasks = [task for task in tasks_list if task.type in phase_task_types]
                phase_content[phase.value]['tasks'] = phase_tasks
                
                # Get contexts for this phase
                phase_contexts = _get_phase_contexts(work_item_contexts, phase)
                phase_content[phase.value]['contexts'] = phase_contexts
                
                # Get deliverables for this phase
                phase_deliverables = _get_phase_deliverables(phase, tasks_list, phase_contexts)
                phase_content[phase.value]['deliverables'] = phase_deliverables
                
            except Exception as phase_error:
                logger.error(f"Error processing phase {phase.value}: {phase_error}")
                # Continue with other phases
        
        # Create phase information structure
        phase_info = {
            'current_phase': work_item.phase,
            'all_phases': all_phases,
            'phase_requirements': phase_requirements,
            'phase_sequence': all_phases,
            'phase_content': phase_content
        }
        
        # Validate current phase if it exists
        if work_item.phase:
            validation_result = phase_validator.validate_phase_completion(work_item, work_item.phase)
            phase_validation = {
                'is_valid': validation_result.is_valid,
                'missing_requirements': validation_result.missing_requirements,
                'confidence_score': 0.0  # PhaseValidationResult doesn't have confidence_score
            }
        
    except Exception as e:
        logger.warning(f"Error fetching phase information: {e}")
        logger.error(f"Phase info error traceback: {traceback.format_exc()}")
    
    # Ensure phase_info is created even if there's an error
    if phase_info is None:
        logger.warning("Phase info is None, creating minimal structure")
        phase_info = {
            'current_phase': work_item.phase,
            'all_phases': [],
            'phase_requirements': None,
            'phase_sequence': [],
            'phase_content': {}
        }
    
    # Calculate work item statistics
    work_item_stats = {
        'is_active': work_item.status and work_item.status.value in ['active', 'in_progress'],
        'is_blocked': work_item.status and work_item.status.value == 'blocked',
        'is_complete': work_item.status and work_item.status.value == 'done',
        'can_start': work_item.status and work_item.status.value in ['ready', 'draft'],
        'days_since_created': (datetime.now() - work_item.created_at).days if work_item.created_at else None,
        'days_since_started': None,  # WorkItem doesn't have started_at
        'days_since_completed': None,  # WorkItem doesn't have completed_at
        'has_tasks': len(tasks_list) > 0,
        'has_contexts': len(work_item_contexts) > 0,
        'has_children': len(child_work_items) > 0,
        'has_parent': parent_work_item is not None,
        'has_related_idea': related_idea is not None,
    }
    
    return render_template('work-items/detail.html', 
                         work_item=work_item, 
                         work_item_id=work_item_id,
                         project=project,
                         tasks=tasks_list,
                         tasks_count=tasks_count,
                         completed_tasks=completed_tasks,
                         in_progress_tasks=in_progress_tasks,
                         blocked_tasks=blocked_tasks,
                         pending_tasks=pending_tasks,
                         progress_percentage=progress_percentage,
                         work_item_contexts=work_item_contexts,
                         context_payload=context_payload,
                         work_item_documents=work_item_documents,
                         documents_by_type=documents_by_type,
                         documents_by_category=documents_by_category,
                         business_context=business_context,
                         technical_context=technical_context,
                         related_idea=related_idea,
                         parent_work_item=parent_work_item,
                         child_work_items=child_work_items,
                         agents=agents_list,
                         total_estimated_hours=total_estimated_hours,
                         total_logged_hours=total_logged_hours,
                         phase_info=phase_info,
                         phase_validation=phase_validation,
                         work_item_stats=work_item_stats)

@work_items_bp.route('/create', methods=['GET', 'POST'])
def create_work_item():
    """Create a new work item"""
    if request.method == 'GET':
        # Show create form
        db = get_database_service()
        
        projects_list = projects.list_projects(db) or []
        ideas_list = ideas.list_ideas(db) or []
        
        return render_template('work-items/create.html',
                             projects=projects_list,
                             ideas=ideas_list,
                             work_item_types=WorkItemType,
                             work_item_statuses=WorkItemStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            db = get_database_service()
            
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            work_item_type = request.form.get('type', 'feature')
            priority = int(request.form.get('priority', 3))
            project_id = int(request.form.get('project_id', 1))
            originated_from_idea_id = request.form.get('originated_from_idea_id')
            originated_from_idea_id = int(originated_from_idea_id) if originated_from_idea_id else None
            
            # Validate required fields
            if not name:
                flash('Work item name is required', 'error')
                return redirect(url_for('work_items.create_work_item'))
            
            if not project_id:
                flash('Project is required', 'error')
                return redirect(url_for('work_items.create_work_item'))
            
            # Create work item
            work_item = WorkItem(
                name=name,
                description=description if description else None,
                type=WorkItemType(work_item_type),
                priority=priority,
                project_id=project_id,
                originated_from_idea_id=originated_from_idea_id,
                status=WorkItemStatus.DRAFT
            )
            
            created_work_item = work_items.create_work_item(db, work_item)
            
            flash(f'Work item "{created_work_item.name}" created successfully', 'success')
            return redirect(url_for('work_items.work_item_detail', work_item_id=created_work_item.id))
            
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            flash(f'Error creating work item: {str(e)}', 'error')
            return redirect(url_for('work_items.create_work_item'))

@work_items_bp.route('/<int:work_item_id>/edit', methods=['GET', 'POST'])
def edit_work_item(work_item_id: int):
    """Edit an existing work item"""
    db = get_database_service()
    
    work_item = work_items.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    if request.method == 'GET':
        # Show edit form
        projects_list = projects.list_projects(db) or []
        ideas_list = ideas.list_ideas(db) or []
        
        return render_template('work-items/edit.html',
                             work_item=work_item,
                             projects=projects_list,
                             ideas=ideas_list,
                             work_item_types=WorkItemType,
                             work_item_statuses=WorkItemStatus)
    
    elif request.method == 'POST':
        # Process form submission
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            work_item_type = request.form.get('type', 'feature')
            priority = int(request.form.get('priority', 3))
            project_id = int(request.form.get('project_id', 1))
            status = request.form.get('status', 'draft')
            originated_from_idea_id = request.form.get('originated_from_idea_id')
            originated_from_idea_id = int(originated_from_idea_id) if originated_from_idea_id else None
            
            # Validate required fields
            if not name:
                flash('Work item name is required', 'error')
                return redirect(url_for('work_items.edit_work_item', work_item_id=work_item_id))
            
            if not project_id:
                flash('Project is required', 'error')
                return redirect(url_for('work_items.edit_work_item', work_item_id=work_item_id))
            
            # Update work item
            work_item.name = name
            work_item.description = description if description else None
            work_item.type = WorkItemType(work_item_type)
            work_item.priority = priority
            work_item.project_id = project_id
            work_item.status = WorkItemStatus(status)
            work_item.originated_from_idea_id = originated_from_idea_id
            
            # Update timestamps based on status changes
            # WorkItem doesn't have started_at or completed_at fields
            # These are only available on Task model
            
            updated_work_item = work_items.update_work_item(db, work_item)
            
            flash(f'Work item "{updated_work_item.name}" updated successfully', 'success')
            return redirect(url_for('work_items.work_item_detail', work_item_id=updated_work_item.id))
            
        except Exception as e:
            logger.error(f"Error updating work item: {e}")
            flash(f'Error updating work item: {str(e)}', 'error')
            return redirect(url_for('work_items.edit_work_item', work_item_id=work_item_id))

@work_items_bp.route('/<int:work_item_id>/delete', methods=['POST'])
def delete_work_item(work_item_id: int):
    """Delete a work item"""
    try:
        db = get_database_service()
        
        work_item = work_items.get_work_item(db, work_item_id)
        if not work_item:
            abort(404, description=f"Work item {work_item_id} not found")
        
        work_items.delete_work_item(db, work_item_id)
        
        flash(f'Work item "{work_item.name}" deleted successfully', 'success')
        return redirect(url_for('work_items.work_items_list'))
        
    except Exception as e:
        logger.error(f"Error deleting work item: {e}")
        flash(f'Error deleting work item: {str(e)}', 'error')
        return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))

@work_items_bp.route('/<int:work_item_id>/documents/create', methods=['GET', 'POST'])
def create_work_item_document(work_item_id: int):
    """Create a new document for a work item"""
    db = get_database_service()
    
    work_item = work_items.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    if request.method == 'GET':
        # Show create document form
        return render_template('work-items/create_document.html',
                             work_item=work_item,
                             work_item_id=work_item_id,
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
                return redirect(url_for('work_items.create_work_item_document', work_item_id=work_item_id))
            
            if not filename:
                flash('Filename is required', 'error')
                return redirect(url_for('work_items.create_work_item_document', work_item_id=work_item_id))
            
            # Generate file path
            file_path = f"docs/{category or 'work-items'}/{document_type}/{filename}"
            if not file_path.endswith('.md') and format_type == 'markdown':
                file_path += '.md'
            
            # Create document reference
            document = DocumentReference(
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item_id,
                category=category if category else 'work-items',
                document_type=DocumentType(document_type),
                file_path=file_path,
                title=title,
                description=description if description else None,
                filename=filename,
                format=DocumentFormat(format_type),
                content=content if content else None,
                storage_mode=StorageMode.HYBRID,
                work_item_id=work_item_id
            )
            
            created_document = document_references.create_document_reference(db, document)
            
            flash(f'Document "{created_document.title}" created successfully', 'success')
            return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            flash(f'Error creating document: {str(e)}', 'error')
            return redirect(url_for('work_items.create_work_item_document', work_item_id=work_item_id))

@work_items_bp.route('/<int:work_item_id>/documents/<int:document_id>')
def view_work_item_document(work_item_id: int, document_id: int):
    """View a work item document"""
    db = get_database_service()
    
    work_item = work_items.get_work_item(db, work_item_id)
    if not work_item:
        abort(404, description=f"Work item {work_item_id} not found")
    
    document = document_references.get_document_reference(db, document_id)
    if not document:
        abort(404, description=f"Document {document_id} not found")
    
    # Verify document belongs to work item
    if document.entity_type.value != 'work_item' or document.entity_id != work_item_id:
        abort(404, description=f"Document {document_id} does not belong to work item {work_item_id}")
    
    return render_template('work-items/view_document.html',
                         work_item=work_item,
                         document=document,
                         work_item_id=work_item_id,
                         document_id=document_id)

@work_items_bp.route('/<int:work_item_id>/update-status', methods=['POST'])
def update_work_item_status(work_item_id: int):
    """Update work item status via AJAX"""
    try:
        db = get_database_service()
        
        work_item = work_items.get_work_item(db, work_item_id)
        if not work_item:
            return jsonify({'error': 'Work item not found'}), 404
        
        new_status = request.json.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        try:
            work_item.status = WorkItemStatus(new_status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update timestamps based on status changes
        # WorkItem doesn't have started_at or completed_at fields
        # These are only available on Task model
        
        updated_work_item = work_items.update_work_item(db, work_item)
        
        return jsonify({
            'success': True,
            'status': updated_work_item.status.value,
            'message': f'Status updated to {updated_work_item.status.value}'
        })
        
    except Exception as e:
        logger.error(f"Error updating work item status: {e}")
        return jsonify({'error': str(e)}), 500

# Helper functions for phase content
def _get_phase_task_types(phase):
    """Get task types that typically belong to each phase"""
    
    phase_task_mapping = {
        'D1_discovery': [TaskType.ANALYSIS, TaskType.RESEARCH, TaskType.DESIGN],
        'P1_plan': [TaskType.PLANNING, TaskType.DESIGN],
        'I1_implementation': [TaskType.IMPLEMENTATION, TaskType.TESTING, TaskType.DOCUMENTATION],
        'R1_review': [TaskType.REVIEW, TaskType.TESTING],
        'O1_operations': [TaskType.DEPLOYMENT, TaskType.DOCUMENTATION],
        'E1_evolution': [TaskType.ANALYSIS, TaskType.RESEARCH, TaskType.DOCUMENTATION]
    }
    return phase_task_mapping.get(phase.value, [])

def _get_phase_contexts(contexts, phase):
    """Get contexts that belong to each phase"""
    
    phase_context_mapping = {
        'D1_discovery': [ContextType.BUSINESS_PILLARS_CONTEXT, ContextType.MARKET_RESEARCH_CONTEXT, ContextType.STAKEHOLDER_CONTEXT],
        'P1_plan': [ContextType.TECHNICAL_CONTEXT, ContextType.QUALITY_GATES_CONTEXT],
        'I1_implementation': [ContextType.IMPLEMENTATION_CONTEXT, ContextType.TECHNICAL_CONTEXT],
        'R1_review': [ContextType.QUALITY_GATES_CONTEXT],
        'O1_operations': [ContextType.TECHNICAL_CONTEXT],
        'E1_evolution': [ContextType.BUSINESS_PILLARS_CONTEXT, ContextType.COMPETITIVE_ANALYSIS_CONTEXT]
    }
    
    phase_context_types = phase_context_mapping.get(phase.value, [])
    return [ctx for ctx in contexts if ctx.context_type in phase_context_types]

def _get_phase_deliverables(phase, tasks_list, contexts):
    """Get deliverables for each phase based on phase requirements"""
    deliverables = []
    
    if phase.value == 'D1_discovery':
        deliverables = [
            {'name': 'Requirements Document', 'status': 'pending', 'description': 'Functional and non-functional requirements'},
            {'name': 'Stakeholder Analysis', 'status': 'pending', 'description': 'Stakeholder identification and analysis'},
            {'name': 'Market Research', 'status': 'pending', 'description': 'Market analysis and competitive landscape'}
        ]
    elif phase.value == 'P1_plan':
        deliverables = [
            {'name': 'Technical Architecture', 'status': 'pending', 'description': 'System architecture and design'},
            {'name': 'Project Plan', 'status': 'pending', 'description': 'Detailed project timeline and milestones'},
            {'name': 'Quality Gates', 'status': 'pending', 'description': 'Quality criteria and validation points'}
        ]
    elif phase.value == 'I1_implementation':
        deliverables = [
            {'name': 'Implementation', 'status': 'pending', 'description': 'Core functionality implementation'},
            {'name': 'Testing Suite', 'status': 'pending', 'description': 'Comprehensive test coverage'},
            {'name': 'Documentation', 'status': 'pending', 'description': 'Technical and user documentation'}
        ]
    elif phase.value == 'R1_review':
        deliverables = [
            {'name': 'Code Review', 'status': 'pending', 'description': 'Peer review and quality assessment'},
            {'name': 'Testing Results', 'status': 'pending', 'description': 'Test execution and results'},
            {'name': 'Quality Validation', 'status': 'pending', 'description': 'Quality gate validation'}
        ]
    elif phase.value == 'O1_operations':
        deliverables = [
            {'name': 'Deployment', 'status': 'pending', 'description': 'Production deployment'},
            {'name': 'Operations Guide', 'status': 'pending', 'description': 'Operational procedures and monitoring'},
            {'name': 'User Training', 'status': 'pending', 'description': 'End-user training materials'}
        ]
    elif phase.value == 'E1_evolution':
        deliverables = [
            {'name': 'Evolution Plan', 'status': 'pending', 'description': 'Future enhancement roadmap'},
            {'name': 'Performance Analysis', 'status': 'pending', 'description': 'Performance metrics and analysis'},
            {'name': 'Feedback Integration', 'status': 'pending', 'description': 'User feedback incorporation'}
        ]
    
    # Update deliverable status based on tasks and contexts
    for deliverable in deliverables:
        # Simple heuristic: if we have related tasks or contexts, mark as in progress
        if any(task.name and deliverable['name'].lower() in task.name.lower() for task in tasks_list):
            deliverable['status'] = 'in_progress'
        elif any(ctx.name and deliverable['name'].lower() in ctx.name.lower() for ctx in contexts):
            deliverable['status'] = 'in_progress'
    
    return deliverables
