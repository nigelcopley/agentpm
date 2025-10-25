"""
Agents Blueprint - Agent Management and Operations

Handles:
- /agents - List all agents
- /agents/<id> - Get agent details
- /agents/<id>/edit - Edit agent form
- /agents/generate - Generate agents form
- /agents/actions/generate - Generate agents (POST)
- /agents/<id>/actions/toggle - Toggle agent status
"""

from flask import Blueprint, render_template, abort, request, redirect, url_for, make_response
from pathlib import Path

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.enums import TaskStatus
from ...core.database.models import Agent

# Import helper functions and models from app
from ..app import (
    get_database_service,
    add_toast,
    toast_response,
    redirect_with_toast,
    AgentInfo,
    AgentsDashboard
)

agents_bp = Blueprint('agents', __name__)


def _is_htmx_request() -> bool:
    """Return True when request originates from HTMX."""
    return request.headers.get('HX-Request') == 'true'


@agents_bp.route('/agents')
def agents_list():
    """List all agents."""
    db = get_database_service()

    # Use database methods instead of raw SQL
    all_agents = agent_methods.list_agents(db)

    # Get all tasks once for efficiency
    all_tasks = []
    work_items = wi_methods.list_work_items(db)
    for wi in work_items:
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        all_tasks.extend(tasks)

    # Calculate metrics
    agents_info = []
    total_assigned_tasks = 0
    total_active_tasks = 0
    active_agents_count = 0
    role_counts = {}  # Track role distribution

    for agent in all_agents:
        agent_data = agent.model_dump()

        # Filter tasks assigned to this agent (Agent uses 'role' field)
        assigned_tasks_list = [
            t for t in all_tasks if t.assigned_to == agent_data['role']
        ]
        assigned_count = len(assigned_tasks_list)

        # Count active tasks (in_progress or review)
        active_count = len([
            t for t in assigned_tasks_list
            if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)
        ])

        # Update totals
        total_assigned_tasks += assigned_count
        total_active_tasks += active_count
        if agent_data['is_active']:
            active_agents_count += 1

        # Track role distribution
        role = agent_data['role']
        if role not in role_counts:
            role_counts[role] = {'count': 0, 'tasks': 0}
        role_counts[role]['count'] += 1
        role_counts[role]['tasks'] += assigned_count

        # Capabilities stored as list via AgentAdapter; normalize empty to None
        capabilities_list = agent_data.get('capabilities') or None

        agents_info.append(
            AgentInfo(
                id=agent_data['id'],
                name=agent_data.get('display_name') or role,
                role=role,
                description=agent_data.get('description'),
                capabilities=capabilities_list,
                is_active=agent_data['is_active'],
                assigned_task_count=assigned_count,
                active_task_count=active_count,
                created_at=agent_data.get('created_at'),
                updated_at=agent_data.get('updated_at')
            )
        )

    # Create dashboard structure
    dashboard = AgentsDashboard(
        total_agents=len(all_agents),
        active_agents=active_agents_count,
        total_assigned_tasks=total_assigned_tasks,
        total_active_tasks=total_active_tasks,
        role_distribution=role_counts,
        agents_list=agents_info
    )

    return render_template('agents/list.html', agents=dashboard)


@agents_bp.route('/agents/<int:agent_id>')
def agent_detail(agent_id: int):
    """Get agent details."""
    db = get_database_service()
    
    agent = agent_methods.get_agent(db, agent_id)
    if not agent:
        abort(404, description=f"Agent {agent_id} not found")
    
    return render_template('agents/detail.html', agent=agent)


@agents_bp.route('/agents/<int:agent_id>/edit')
def agent_edit(agent_id: int):
    """Edit agent form."""
    db = get_database_service()
    agent = agent_methods.get_agent(db, agent_id)
    
    if not agent:
        abort(404, description=f"Agent {agent_id} not found")
    
    return render_template('agents/edit.html', agent=agent)


@agents_bp.route('/agents/generate')
def agents_generate_form():
    """Load agent generation modal with framework detection."""
    from ...core.plugins import PluginOrchestrator

    # Detect frameworks
    orchestrator = PluginOrchestrator()
    try:
        results = orchestrator.detect_all(Path('.'))
        detected_frameworks = [
            {'name': r.framework, 'version': r.metadata.get('version', 'unknown')}
            for r in results if r.confidence > 0.7
        ]
    except Exception as e:
        # Framework detection failed - show modal anyway
        detected_frameworks = []

    # Map frameworks to suggested agents
    framework_agent_map = {
        'Python': 'python-developer',
        'Flask': 'frontend-developer',
        'pytest': 'testing-specialist',
        'SQLite': 'database-developer',
        'Click': 'python-developer'  # CLI framework
    }

    # Get unique suggested agents
    suggested_set = set()
    for framework in detected_frameworks:
        agent_role = framework_agent_map.get(framework['name'])
        if agent_role:
            suggested_set.add(agent_role)

    suggested_agents = sorted(list(suggested_set))

    return render_template(
        'partials/agent_generate_modal.html',
        detected_frameworks=detected_frameworks,
        suggested_agents=suggested_agents
    )


@agents_bp.route('/agents/actions/generate', methods=['POST'])
def agents_generate():
    """Generate agents from form submission."""
    db = get_database_service()

    # Get selected roles from form
    selected_roles = request.form.getlist('agents[]')

    # Get project ID (assuming first project for now)
    projects = project_methods.list_projects(db)
    if not projects:
        if _is_htmx_request():
            return toast_response('No project found', 'error'), 404
        return redirect_with_toast(
            url_for('agents.agents_list'),
            'No project found',
            'error'
        )

    project_id = projects[0].id

    created_count = 0
    failed = []

    for role in selected_roles:
        try:
            # Check for duplicate
            existing = agent_methods.get_agent_by_role(db, project_id, role)
            if existing:
                failed.append(f'{role}: already exists')
                continue

            # Create agent with basic defaults
            display_name = role.replace('-', ' ').title()

            # Role-specific descriptions
            descriptions = {
                'python-developer': 'Python implementation specialist for backend development',
                'frontend-developer': 'Flask and web interface developer for UI components',
                'testing-specialist': 'Pytest testing and quality assurance expert',
                'database-developer': 'SQLite database and schema management specialist'
            }

            agent = Agent(
                project_id=project_id,
                role=role,
                display_name=display_name,
                description=descriptions.get(role, f'Auto-generated {role} agent'),
                is_active=True,
                capabilities=[]
            )

            agent_methods.create_agent(db, agent)
            created_count += 1

        except Exception as e:
            failed.append(f'{role}: {str(e)}')

    # Get updated agent list with task counts
    all_agents = agent_methods.list_agents(db)
    all_tasks = []
    work_items = wi_methods.list_work_items(db)
    for wi in work_items:
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        all_tasks.extend(tasks)

    agents_info = []
    for agent in all_agents:
        agent_data = agent.model_dump()

        assigned_tasks_list = [
            t for t in all_tasks if t.assigned_to == agent_data['role']
        ]
        assigned_count = len(assigned_tasks_list)
        active_count = len([
            t for t in assigned_tasks_list
            if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)
        ])

        capabilities_list = agent_data.get('capabilities') or None

        agents_info.append(
            AgentInfo(
                id=agent_data['id'],
                name=agent_data.get('display_name') or agent_data['role'],
                role=agent_data['role'],
                description=agent_data.get('description'),
                capabilities=capabilities_list,
                is_active=agent_data['is_active'],
                assigned_task_count=assigned_count,
                active_task_count=active_count,
                created_at=agent_data.get('created_at'),
                updated_at=agent_data.get('updated_at')
            )
        )

    # Return updated tbody with toast notification
    response = make_response(
        render_template('partials/agents_list_tbody.html', agents=agents_info)
    )

    # Build toast message
    message = f'Generated {created_count} agent{"s" if created_count != 1 else ""}'
    toast_type = 'success'

    if failed:
        message += f' ({len(failed)} skipped)'
        toast_type = 'warning' if created_count > 0 else 'error'

    add_toast(response, message, toast_type)

    # Close modal on success (HTMX trigger)
    if created_count > 0:
        response.headers['HX-Trigger'] = 'closeModal'

    if _is_htmx_request():
        return response

    return redirect_with_toast(
        url_for('agents.agents_list'),
        message,
        toast_type
    )


@agents_bp.route('/agents/<int:agent_id>/actions/toggle', methods=['POST'])
def agents_toggle(agent_id: int):
    """Toggle agent is_active status."""
    db = get_database_service()

    # Get agent
    agent = agent_methods.get_agent(db, agent_id)
    if not agent:
        if _is_htmx_request():
            return toast_response('Agent not found', 'error'), 404
        return redirect_with_toast(
            url_for('agents.agents_list'),
            'Agent not found',
            'error'
        )

    # Toggle is_active
    updated_agent = agent_methods.update_agent(db, agent_id, is_active=not agent.is_active)

    # Get task counts for the updated agent
    all_tasks = []
    work_items = wi_methods.list_work_items(db)
    for wi in work_items:
        tasks = task_methods.list_tasks(db, work_item_id=wi.id)
        all_tasks.extend(tasks)

    assigned_tasks_list = [
        t for t in all_tasks if t.assigned_to == updated_agent.role
    ]
    assigned_count = len(assigned_tasks_list)
    active_count = len([
        t for t in assigned_tasks_list
        if t.status in (TaskStatus.ACTIVE, TaskStatus.REVIEW)
    ])

    # Create AgentInfo for template
    agent_info = AgentInfo(
        id=updated_agent.id,
        name=updated_agent.display_name or updated_agent.role,
        role=updated_agent.role,
        description=updated_agent.description,
        capabilities=updated_agent.capabilities or None,
        is_active=updated_agent.is_active,
        assigned_task_count=assigned_count,
        active_task_count=active_count,
        created_at=updated_agent.created_at,
        updated_at=updated_agent.updated_at
    )

    # Return updated row HTML with toast notification
    response = make_response(
        render_template('partials/agent_row.html', agent=agent_info)
    )
    message = f'Agent {updated_agent.role} {"activated" if updated_agent.is_active else "deactivated"}'
    add_toast(
        response,
        message,
        'success'
    )
    if _is_htmx_request():
        return response
    return redirect_with_toast(
        url_for('agents.agents_list'),
        message,
        'success'
    )
