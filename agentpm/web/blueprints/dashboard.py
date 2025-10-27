"""
Dashboard Blueprint for APM (Agent Project Manager) Web Application

Main dashboard and project overview functionality.
"""

import logging
from typing import Optional, Dict, Any, List

from flask import Blueprint, render_template, redirect, url_for, request, jsonify

from ...core.database.service import DatabaseService
from ...core.database.models import Context
from ...core.database.methods import (
    projects, work_items, tasks, agents, ideas, contexts, 
    rules, evidence_sources, events, document_references
)
from ...core.database.enums import EntityType, ContextType, WorkItemStatus, TaskStatus, IdeaStatus
from .utils import get_database_service

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')

logger = logging.getLogger(__name__)

@dashboard_bp.route('/')
def dashboard_home():
    """Dashboard home - comprehensive project portal with all project-level context."""
    db = get_database_service()
    
    # Get project data
    projects_list = projects.list_projects(db) or []
    if not projects_list:
        return render_template('no_project.html')
    
    project = projects_list[0]
    
    # Get comprehensive project data
    work_items_list = work_items.list_work_items(db, project_id=project.id) or []
    tasks_list = tasks.list_tasks(db) or []
    agents_list = agents.list_agents(db) or []
    ideas_list = ideas.list_ideas(db, project_id=project.id) or []
    
    # Get project contexts (business, technical, etc.)
    project_contexts = []
    business_context = None
    technical_context = None
    project_summary = None
    
    try:
        project_contexts = contexts.get_rich_contexts_by_entity(db, EntityType.PROJECT, project.id) or []
        for context in project_contexts:
            if context.context_type == ContextType.BUSINESS_CONTEXT:
                business_context = context
            elif context.context_type == ContextType.TECHNICAL_CONTEXT:
                technical_context = context
            elif context.context_type == ContextType.PROJECT_SUMMARY:
                project_summary = context
    except Exception as e:
        logger.warning(f"Error fetching project contexts: {e}")
    
    # Get project rules
    project_rules = []
    try:
        project_rules = rules.list_rules(db) or []
    except Exception as e:
        logger.warning(f"Error fetching rules: {e}")
    
    # Get evidence sources and events
    evidence_sources_list = []
    recent_events = []
    try:
        evidence_sources_list = evidence_sources.list_evidence_sources(db) or []
        recent_events = events.list_events(db) or []
        recent_events = sorted(recent_events, key=lambda x: x.created_at or '', reverse=True)[:10]
    except Exception as e:
        logger.warning(f"Error fetching evidence/events: {e}")
    
    # Get document references
    document_references_list = []
    try:
        document_references_list = document_references.list_document_references(db) or []
    except Exception as e:
        logger.warning(f"Error fetching document references: {e}")
    
    # Calculate comprehensive metrics
    work_item_status_counts = {}
    task_status_counts = {}
    idea_status_counts = {}
    
    for status in WorkItemStatus:
        work_item_status_counts[status.value] = len([wi for wi in work_items_list if wi.status and wi.status.value == status.value])
    
    for status in TaskStatus:
        task_status_counts[status.value] = len([t for t in tasks_list if t.status and t.status.value == status.value])
    
    for status in IdeaStatus:
        idea_status_counts[status.value] = len([i for i in ideas_list if i.status and i.status.value == status.value])
    
    # Calculate effort and progress metrics
    total_estimated_effort = sum(wi.effort_estimate_hours or 0 for wi in work_items_list)
    total_task_effort = sum(t.effort_hours or 0 for t in tasks_list)
    completed_task_effort = sum(t.effort_hours or 0 for t in tasks_list if t.status and t.status.value == 'done')
    
    # Get recent activity
    recent_work_items = sorted(work_items_list, key=lambda x: x.updated_at or x.created_at, reverse=True)[:10]
    recent_tasks = sorted(tasks_list, key=lambda x: x.updated_at or x.created_at, reverse=True)[:10]
    recent_ideas = sorted(ideas_list, key=lambda x: x.updated_at or x.created_at, reverse=True)[:5]
    
    # Get high-priority items
    high_priority_work_items = [wi for wi in work_items_list if wi.priority and wi.priority <= 2]
    blocked_work_items = [wi for wi in work_items_list if wi.status and wi.status.value == 'blocked']
    blocked_tasks = [t for t in tasks_list if t.status and t.status.value == 'blocked']
    
    # Create comprehensive dashboard data
    dashboard_data = {
        'project': project,
        
        # Core metrics
        'metrics': {
            'total_ideas': len(ideas_list),
            'total_work_items': len(work_items_list),
            'total_tasks': len(tasks_list),
            'total_agents': len(agents_list),
            'total_rules': len(project_rules),
            'total_evidence_sources': len(evidence_sources_list),
            'total_events': len(recent_events),
            'total_documents': len(document_references_list),
        },
        
        # Status distributions
        'work_item_status_counts': work_item_status_counts,
        'task_status_counts': task_status_counts,
        'idea_status_counts': idea_status_counts,
        
        # Effort and progress
        'effort_metrics': {
            'total_estimated_effort': total_estimated_effort,
            'total_task_effort': total_task_effort,
            'completed_task_effort': completed_task_effort,
            'progress_percentage': round((completed_task_effort / total_task_effort * 100), 1) if total_task_effort > 0 else 0
        },
        
        # Project context
        'project_contexts': project_contexts,
        'business_context': business_context,
        'technical_context': technical_context,
        'project_summary': project_summary,
        
        # Recent activity
        'recent_work_items': recent_work_items,
        'recent_tasks': recent_tasks,
        'recent_ideas': recent_ideas,
        'recent_events': recent_events,
        
        # Priority and blocked items
        'high_priority_work_items': high_priority_work_items,
        'blocked_work_items': blocked_work_items,
        'blocked_tasks': blocked_tasks,
        
        # Resources
        'agents': agents_list,
        'rules': project_rules[:10],  # Show top 10 rules
        'evidence_sources': evidence_sources_list[:10],  # Show top 10 evidence sources
        'document_references': document_references_list[:10],  # Show top 10 documents
    }
    
    return render_template('dashboard.html', **dashboard_data)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Main dashboard with project overview"""
    return dashboard_home()  # Reuse the same logic

@dashboard_bp.route('/overview')
def overview():
    """System overview with key metrics"""
    return dashboard_home()  # Reuse the same logic

@dashboard_bp.route('/settings')
def project_settings():
    """
    Project settings view.
    
    Since the main dashboard is essentially the project portal,
    this provides project-level configuration and settings.
    """
    # For now, redirect to the main dashboard until we create the settings template
    return redirect(url_for('dashboard.dashboard_home'))

@dashboard_bp.route('/update-context', methods=['POST'])
def update_project_context():
    """
    Update project context data.
    
    Allows updating project-level context information from the dashboard.
    """
    
    try:
        db = get_database_service()
        
        # Get project
        projects_list = projects.list_projects(db) or []
        if not projects_list:
            return jsonify({'error': 'No project found'}), 404
        
        project = projects_list[0]
        
        # Get form data
        context_type = request.form.get('context_type')
        context_data = request.form.get('context_data')
        
        if not context_type or not context_data:
            return jsonify({'error': 'Context type and data are required'}), 400
        
        # Update or create context
        try:
            context_type_enum = ContextType(context_type)
        except ValueError:
            return jsonify({'error': 'Invalid context type'}), 400
        
        # Check if context exists
        existing_context = contexts.get_context_by_entity_and_type(
            db, EntityType.PROJECT, project.id, context_type_enum
        )
        
        if existing_context:
            # Update existing context
            updated_context = contexts.update_context(
                db, existing_context.id, context_data=context_data
            )
        else:
            # Create new context
            new_context = Context(
                entity_type=EntityType.PROJECT,
                entity_id=project.id,
                context_type=context_type_enum,
                context_data=context_data,
                confidence_score=0.8  # Default confidence
            )
            updated_context = contexts.create_context(db, new_context)
        
        return jsonify({
            'success': True,
            'message': 'Project context updated successfully',
            'context_id': updated_context.id
        })
        
    except Exception as e:
        logger.error(f"Error updating project context: {e}")
        return jsonify({'error': 'Failed to update project context'}), 500
