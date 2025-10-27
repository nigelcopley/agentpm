"""
Agents Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for agents including:
- Create, Read, Update, Delete operations
- Agent configuration management
- Agent status updates
"""

import logging
from typing import Optional, List

from flask import request, jsonify, flash, redirect, url_for

from ....core.database.methods import agents
from ....core.database.models import Agent
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_agent():
    """Create a new agent."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'name': 'Agent name is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('agents.agents_list'))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        project_id = int(request.form.get('project_id', 1))
        capabilities = request.form.get('capabilities', '').strip()
        configuration = request.form.get('configuration', '').strip()
        
        # Parse capabilities if provided
        capabilities_list: List[str] = []
        if capabilities:
            capabilities_list = [cap.strip() for cap in capabilities.split(',') if cap.strip()]
        
        # Create agent
        agent = Agent(
            name=name,
            description=description if description else None,
            project_id=project_id,
            capabilities=capabilities_list if capabilities_list else None,
            configuration=configuration if configuration else None,
            is_active=True
        )
        
        created_agent = agents.create_agent(db, agent)
        
        flash(f'Agent "{created_agent.name}" created successfully', 'success')
        return redirect(url_for('agents.agent_detail', agent_id=created_agent.id))
        
    except Exception as e:
        return handle_error(e, 'Error creating agent', url_for('agents.agents_list'))

def update_agent(agent_id: int):
    """Update an existing agent."""
    try:
        db = get_database_service()
        
        agent = safe_get_entity(agents.get_agent, db, agent_id, "Agent")
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.agents_list'))
        
        # Validate required fields
        required_fields = {
            'name': 'Agent name is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('agents.edit_agent', agent_id=agent_id))
        
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        project_id = int(request.form.get('project_id', 1))
        capabilities = request.form.get('capabilities', '').strip()
        configuration = request.form.get('configuration', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Parse capabilities if provided
        capabilities_list: List[str] = []
        if capabilities:
            capabilities_list = [cap.strip() for cap in capabilities.split(',') if cap.strip()]
        
        # Update agent using the correct method signature
        updated_agent = agents.update_agent(db, agent_id,
                                           name=name,
                                           description=description if description else None,
                                           project_id=project_id,
                                           capabilities=capabilities_list if capabilities_list else None,
                                           configuration=configuration if configuration else None,
                                           is_active=is_active)
        
        flash(f'Agent "{updated_agent.name}" updated successfully', 'success')
        return redirect(url_for('agents.agent_detail', agent_id=agent_id))
        
    except Exception as e:
        return handle_error(e, 'Error updating agent', url_for('agents.edit_agent', agent_id=agent_id))

def delete_agent(agent_id: int):
    """Delete an agent."""
    try:
        db = get_database_service()
        
        agent = safe_get_entity(agents.get_agent, db, agent_id, "Agent")
        if not agent:
            flash('Agent not found', 'error')
            return redirect(url_for('agents.agents_list'))
        
        agent_name = agent.name
        agents.delete_agent(db, agent_id)
        
        flash(f'Agent "{agent_name}" deleted successfully', 'success')
        return redirect(url_for('agents.agents_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting agent', url_for('agents.agent_detail', agent_id=agent_id))
