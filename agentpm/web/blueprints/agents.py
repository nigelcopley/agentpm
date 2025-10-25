"""
Agents Blueprint for APM (Agent Project Manager) Web Application

Agent management functionality.
"""

from flask import Blueprint, render_template, abort
import logging

# Create agents blueprint
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

logger = logging.getLogger(__name__)

def get_database_service():
    """Get database service instance"""
    from ...core.database.service import DatabaseService
    return DatabaseService('.agentpm/data/agentpm.db')

@agents_bp.route('/')
def agents_list():
    """Agents list view"""
    db = get_database_service()
    from ...core.database.methods import agents
    
    agents_list = agents.list_agents(db) or []
    
    # Calculate metrics
    active_count = len([a for a in agents_list if a.is_active])
    inactive_count = len([a for a in agents_list if not a.is_active])
    total_capabilities = sum(len(a.capabilities or []) for a in agents_list)
    
    # Create agents object with metrics
    agents_data = {
        'agents': agents_list,
        'total_agents': len(agents_list),
        'active_count': active_count,
        'inactive_count': inactive_count,
        'total_capabilities': total_capabilities
    }
    
    return render_template('agents/list.html', agents=agents_data)

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
    """
    # Fetch agent data
    db = get_database_service()
    from ...core.database.methods import agents
    
    agent = agents.get_agent(db, agent_id)
    
    if not agent:
        abort(404, description=f"Agent {agent_id} not found")
    
    return render_template('agents/detail.html', agent=agent, agent_id=agent_id)
