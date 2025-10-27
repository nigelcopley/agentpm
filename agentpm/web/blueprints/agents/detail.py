"""
Agents Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for agents including:
- Individual agent detail views with comprehensive context
- Agent capabilities and configuration
- Agent performance metrics
- Agent usage history
"""

import json
import logging
from typing import Optional, Dict, Any, List

from flask import render_template, abort

from ....core.database.methods import agents, projects, work_items, tasks
from ..utils import get_database_service, safe_get_entity
from . import agents_bp

logger = logging.getLogger(__name__)

@agents_bp.route('/<int:agent_id>')
def agent_detail(agent_id: int):
    """
    Comprehensive agent detail view.
    
    Shows all agent information in a single view:
    - Basic information (name, description, status, type)
    - Capabilities and configuration
    - Generation tracking
    - Performance metrics
    - Configuration details
    - Usage history
    - Project context
    - Related work items and tasks
    """
    # Fetch agent data
    db = get_database_service()
    
    agent = safe_get_entity(agents.get_agent, db, agent_id, "Agent")
    
    if not agent:
        abort(404, description=f"Agent {agent_id} not found")
    
    # Get project information
    project: Optional[Any] = None
    if agent.project_id:
        projects_list = projects.list_projects(db) or []
        project = next((p for p in projects_list if p.id == agent.project_id), None)
    
    # Get related work items and tasks
    related_work_items: List[Any] = []
    related_tasks: List[Any] = []
    
    try:
        # Get work items where this agent might be involved
        all_work_items = work_items.list_work_items(db, project_id=agent.project_id) or []
        # Note: Work items don't have direct agent assignment, but we can show project context
        
        # Get tasks assigned to this agent
        all_tasks = tasks.list_tasks(db) or []
        related_tasks = [task for task in all_tasks if task.assigned_to and agent.name.lower() in task.assigned_to.lower()]
        
    except Exception as e:
        logger.warning(f"Error fetching related work items/tasks: {e}")
    
    # Calculate agent statistics
    agent_stats: Dict[str, Any] = {
        'is_active': agent.is_active,
        'has_capabilities': len(agent.capabilities or []) > 0,
        'capability_count': len(agent.capabilities or []),
        'has_configuration': bool(agent.configuration),
        'has_generation_tracking': bool(getattr(agent, 'generation_tracking', None)),
        'related_tasks_count': len(related_tasks),
        'related_work_items_count': len(related_work_items),
    }
    
    # Get capability details
    capability_details: List[Dict[str, str]] = []
    if agent.capabilities:
        for capability in agent.capabilities:
            capability_details.append({
                'name': capability,
                'description': f"Agent has {capability} capability",
                'status': 'active' if agent.is_active else 'inactive'
            })
    
    # Get configuration details
    configuration_details: Dict[str, Any] = {}
    if agent.configuration:
        try:
            if isinstance(agent.configuration, str):
                configuration_details = json.loads(agent.configuration)
            else:
                configuration_details = agent.configuration
        except Exception as e:
            logger.warning(f"Error parsing agent configuration: {e}")
            configuration_details = {'raw': str(agent.configuration)}
    
    return render_template('agents/detail.html', 
                         agent=agent, 
                         agent_id=agent_id,
                         project=project,
                         related_work_items=related_work_items,
                         related_tasks=related_tasks,
                         agent_stats=agent_stats,
                         capability_details=capability_details,
                         configuration_details=configuration_details)
