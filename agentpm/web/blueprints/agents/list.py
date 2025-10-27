"""
Agents List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for agents including:
- Agents listing with metrics
- Agent statistics and capabilities
"""

import logging
from typing import Dict, Any, List

from flask import render_template

from ....core.database.methods import agents
from ..utils import get_database_service
from . import agents_bp

logger = logging.getLogger(__name__)

@agents_bp.route('/')
def agents_list():
    """Agents list view with comprehensive metrics."""
    db = get_database_service()
    
    agents_list_data = agents.list_agents(db) or []
    
    # Calculate comprehensive metrics
    active_count = len([a for a in agents_list_data if a.is_active])
    inactive_count = len([a for a in agents_list_data if not a.is_active])
    total_capabilities = sum(len(a.capabilities or []) for a in agents_list_data)
    
    # Calculate capability distribution
    capability_stats: Dict[str, int] = {}
    for agent in agents_list_data:
        if agent.capabilities:
            for capability in agent.capabilities:
                capability_stats[capability] = capability_stats.get(capability, 0) + 1
    
    # Get agent types distribution
    agent_types: Dict[str, int] = {}
    for agent in agents_list_data:
        agent_type = getattr(agent, 'type', 'unknown')
        agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
    
    # Create comprehensive agents data
    agents_data: Dict[str, Any] = {
        'agents': agents_list_data,
        'total_agents': len(agents_list_data),
        'active_count': active_count,
        'inactive_count': inactive_count,
        'total_capabilities': total_capabilities,
        'capability_stats': capability_stats,
        'agent_types': agent_types,
        'metrics': {
            'total_agents': len(agents_list_data),
            'active_agents': active_count,
            'inactive_agents': inactive_count,
            'total_capabilities': total_capabilities,
            'avg_capabilities_per_agent': round(total_capabilities / len(agents_list_data), 1) if agents_list_data else 0,
            'most_common_capability': max(capability_stats.items(), key=lambda x: x[1])[0] if capability_stats else None,
            'most_common_type': max(agent_types.items(), key=lambda x: x[1])[0] if agent_types else None
        }
    }
    
    return render_template('agents/list.html', agents=agents_data)
