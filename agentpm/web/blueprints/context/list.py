"""
Context List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for contexts including:
- Contexts listing with filtering and search
- Comprehensive metrics and analytics
- Context type distribution
- Confidence score analysis
"""

from flask import render_template, request
from datetime import datetime
import logging

from . import context_bp
from ..utils import get_database_service, _is_htmx_request

logger = logging.getLogger(__name__)

@context_bp.route('/')
def contexts_list():
    """Contexts list view with comprehensive metrics, filtering, and search"""
    db = get_database_service()
    
    # Get database methods
    from ....core.database.methods import contexts, projects
    from ....core.database.enums import ContextType, EntityType, ConfidenceBand
    
    # Get project ID for contexts
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')
    entity_type_filter = request.args.get('entity_type', '')
    confidence_filter = request.args.get('confidence', '')
    sort_by = request.args.get('sort', 'updated_desc')
    
    # Get all contexts
    contexts_list = contexts.list_contexts(db, project_id=project_id) or []
    
    # Apply filters
    filtered_contexts = contexts_list
    
    # Search filter
    if search_query:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if search_query.lower() in (ctx.what or '').lower() or 
               search_query.lower() in (ctx.why or '').lower() or
               search_query.lower() in (ctx.how or '').lower() or
               search_query.lower() in (str(ctx.context_data or '')).lower() or
               search_query.lower() in (ctx.file_path or '').lower() or
               search_query.lower() in (ctx.context_type.value if ctx.context_type else '').lower()
        ]
    
    # Type filter
    if type_filter:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if ctx.context_type and ctx.context_type.value == type_filter
        ]
    
    # Entity type filter
    if entity_type_filter:
        filtered_contexts = [
            ctx for ctx in filtered_contexts
            if ctx.entity_type and ctx.entity_type.value == entity_type_filter
        ]
    
    # Confidence filter
    if confidence_filter:
        if confidence_filter == 'high':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and ctx.confidence_score >= 0.8
            ]
        elif confidence_filter == 'medium':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and 0.6 <= ctx.confidence_score < 0.8
            ]
        elif confidence_filter == 'low':
            filtered_contexts = [
                ctx for ctx in filtered_contexts
                if ctx.confidence_score and ctx.confidence_score < 0.6
            ]
    
    # Apply sorting
    if sort_by == 'title_asc':
        filtered_contexts.sort(key=lambda x: (x.title or '').lower())
    elif sort_by == 'title_desc':
        filtered_contexts.sort(key=lambda x: (x.title or '').lower(), reverse=True)
    elif sort_by == 'type_asc':
        filtered_contexts.sort(key=lambda x: x.context_type.value if x.context_type else '')
    elif sort_by == 'type_desc':
        filtered_contexts.sort(key=lambda x: x.context_type.value if x.context_type else '', reverse=True)
    elif sort_by == 'confidence_asc':
        filtered_contexts.sort(key=lambda x: x.confidence_score or 0)
    elif sort_by == 'confidence_desc':
        filtered_contexts.sort(key=lambda x: x.confidence_score or 0, reverse=True)
    elif sort_by == 'created_asc':
        filtered_contexts.sort(key=lambda x: x.created_at or datetime.min)
    elif sort_by == 'created_desc':
        filtered_contexts.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    else:  # updated_desc (default)
        filtered_contexts.sort(key=lambda x: x.updated_at or x.created_at or datetime.min, reverse=True)
    
    # Calculate comprehensive metrics for the sidebar
    metrics = {
        # Basic counts
        'total_contexts': len(contexts_list),
        
        # Type-based counts
        'business_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'business_pillars_context']),
        'technical_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'technical_context']),
        'resource_files': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'resource_file']),
        'rules_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'rules_context']),
        'quality_gates_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'quality_gates_context']),
        'implementation_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'implementation_context']),
        'market_research_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'market_research_context']),
        'stakeholder_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'stakeholder_context']),
        'competitive_analysis_contexts': len([ctx for ctx in contexts_list if ctx.context_type and ctx.context_type.value == 'competitive_analysis_context']),
        
        # Entity type counts
        'project_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'project']),
        'work_item_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'work_item']),
        'task_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'task']),
        'idea_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'idea']),
        'agent_contexts': len([ctx for ctx in contexts_list if ctx.entity_type and ctx.entity_type.value == 'agent']),
        
        # Confidence-based counts
        'high_confidence_contexts': len([ctx for ctx in contexts_list if ctx.confidence_score and ctx.confidence_score >= 0.8]),
        'medium_confidence_contexts': len([ctx for ctx in contexts_list if ctx.confidence_score and 0.6 <= ctx.confidence_score < 0.8]),
        'low_confidence_contexts': len([ctx for ctx in contexts_list if ctx.confidence_score and ctx.confidence_score < 0.6]),
        'no_confidence_contexts': len([ctx for ctx in contexts_list if not ctx.confidence_score]),
        
        # File-based counts
        'file_contexts': len([ctx for ctx in contexts_list if ctx.file_path]),
        'non_file_contexts': len([ctx for ctx in contexts_list if not ctx.file_path]),
    }
    
    # Get available filter options
    filter_options = {
        'types': [{'value': type_.value, 'label': type_.value.replace('_', ' ').title()} 
                 for type_ in ContextType],
        'entity_types': [{'value': entity_type.value, 'label': entity_type.value.replace('_', ' ').title()} 
                        for entity_type in EntityType],
        'confidence_levels': [
            {'value': 'high', 'label': 'High Confidence (0.8+)'},
            {'value': 'medium', 'label': 'Medium Confidence (0.6-0.8)'},
            {'value': 'low', 'label': 'Low Confidence (<0.6)'}
        ],
        'sort_options': [
            {'value': 'updated_desc', 'label': 'Last Updated (Newest)'},
            {'value': 'updated_asc', 'label': 'Last Updated (Oldest)'},
            {'value': 'created_desc', 'label': 'Created (Newest)'},
            {'value': 'created_asc', 'label': 'Created (Oldest)'},
            {'value': 'title_asc', 'label': 'Title (A-Z)'},
            {'value': 'title_desc', 'label': 'Title (Z-A)'},
            {'value': 'type_asc', 'label': 'Type (A-Z)'},
            {'value': 'type_desc', 'label': 'Type (Z-A)'},
            {'value': 'confidence_asc', 'label': 'Confidence (Low to High)'},
            {'value': 'confidence_desc', 'label': 'Confidence (High to Low)'},
        ]
    }
    
    # Check if this is an HTMX request for dynamic filtering
    if _is_htmx_request():
        # Return only the content that should be updated
        return render_template('context/partials/contexts_content.html', 
                             contexts=filtered_contexts,
                             metrics=metrics,
                             filter_options=filter_options,
                             current_filters={
                                 'search': search_query,
                                 'type': type_filter,
                                 'entity_type': entity_type_filter,
                                 'confidence': confidence_filter,
                                 'sort': sort_by
                             })
    
    # Return full page for regular requests
    return render_template('context/list.html', 
                         contexts=filtered_contexts,
                         metrics=metrics,
                         filter_options=filter_options,
                         current_filters={
                             'search': search_query,
                             'type': type_filter,
                             'entity_type': entity_type_filter,
                             'confidence': confidence_filter,
                             'sort': sort_by
                         })
