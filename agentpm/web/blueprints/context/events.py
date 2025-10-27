"""
Context Events Module for APM (Agent Project Manager) Web Application

Handles event-related context functionality including:
- Event listing and management
- Event timeline and history
"""

from flask import render_template
import logging
from datetime import datetime

from . import context_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@context_bp.route('/events')
def context_events():
    """Events context view"""
    db = get_database_service()
    from ....core.database.methods import contexts, projects
    
    projects_list = projects.list_projects(db) or []
    project_id = projects_list[0].id if projects_list else 1
    
    # Get event contexts
    event_contexts = contexts.list_contexts(db, project_id=project_id) or []
    event_contexts = [ctx for ctx in event_contexts if ctx.context_type and 'event' in ctx.context_type.value.lower()]
    
    # Sort by creation date
    event_contexts.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    
    # Calculate event metrics
    event_metrics = {
        'total_events': len(event_contexts),
        'recent_events': len([ctx for ctx in event_contexts if ctx.created_at and (datetime.now() - ctx.created_at).days <= 7]),
        'this_month_events': len([ctx for ctx in event_contexts if ctx.created_at and (datetime.now() - ctx.created_at).days <= 30]),
    }
    
    return render_template('context/events.html', 
                         contexts=event_contexts,
                         metrics=event_metrics)
