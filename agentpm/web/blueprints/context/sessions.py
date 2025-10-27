"""
Context Sessions Module for APM (Agent Project Manager) Web Application

Handles session-related context functionality including:
- Session listing and management
- Session context and history
"""

from flask import render_template
import logging

from . import context_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@context_bp.route('/sessions')
def context_sessions():
    """Sessions context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get session contexts
    session_contexts = contexts.list_contexts(db, project_id=project_id) or []
    session_contexts = [ctx for ctx in session_contexts if ctx.context_type and 'session' in ctx.context_type.value.lower()]
    
    # Sort by creation date
    session_contexts.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Calculate session metrics
    session_metrics = {
        'total_sessions': len(session_contexts),
        'active_sessions': len([ctx for ctx in session_contexts if ctx.created_at and (datetime.now() - ctx.created_at).days <= 1]),
        'recent_sessions': len([ctx for ctx in session_contexts if ctx.created_at and (datetime.now() - ctx.created_at).days <= 7]),
    }
    
    return render_template('context/sessions.html', 
                         contexts=session_contexts,
                         metrics=session_metrics)
