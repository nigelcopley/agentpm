"""
Configuration Blueprint - Rules, Agents, and Project Settings Routes

Handles:
- Rules list and toggle operations
- Agents list, toggle, and generation
- Project settings (inline editing)
"""

from flask import Blueprint, render_template, request, make_response, abort, url_for
from pathlib import Path

from ...core.database.methods import projects as project_methods
from ...core.database.methods import work_items as wi_methods
from ...core.database.methods import tasks as task_methods
from ...core.database.methods import agents as agent_methods
from ...core.database.methods import rules as rule_methods
from ...core.database.enums import EnforcementLevel, TaskStatus
from ...core.database.models import Agent

# Import helper functions and models from app
from ..app import (
    get_database_service,
    add_toast,
    toast_response,
    redirect_with_toast,
    RuleInfo,
    AgentInfo,
    AgentsDashboard
)

# Import WebSocket broadcasting
from ..websocket import broadcast_rule_toggle

config_bp = Blueprint('config', __name__)


# ========================================
# Rules Management
# ========================================

@config_bp.route('/rules')
def rules_list():
    """
    Rules list view.

    Returns:
        Rendered rules list template
    """
    db = get_database_service()

    # ✅ Use database methods instead of raw SQL
    all_rules = rule_methods.list_rules(db)

    rules_info = [
        RuleInfo(
            rule=rule,
            is_active=rule.enabled
        )
        for rule in all_rules
    ]

    return render_template('rules_list.html', rules=rules_info)


@config_bp.route('/rules/<int:rule_id>/toggle', methods=['POST', 'GET'])
def rules_toggle(rule_id: int):
    """
    Toggle rule enforcement between BLOCK (enabled) and GUIDE (disabled).

    HTMX endpoint that returns an updated rule row partial template.

    Args:
        rule_id: Rule database ID

    Returns:
        Updated rule_row.html partial with toast headers
    """
    if request.method == 'GET':
        abort(404, description=f"Rule {rule_id} not found")

    db = get_database_service()

    # Get rule
    rule = rule_methods.get_rule(db, rule_id)
    if not rule:
        if _is_htmx_request():
            return toast_response('Rule not found', 'error'), 404
        return redirect_with_toast(
            url_for('config.rules_list'),
            'Rule not found',
            'error'
        )

    # Critical rules that cannot be disabled (CI gates)
    CRITICAL_RULES = ['CI-001', 'CI-002', 'CI-003', 'CI-004', 'CI-005', 'CI-006']

    # Validate: Cannot disable critical rules
    if rule.rule_id in CRITICAL_RULES and rule.enforcement_level == EnforcementLevel.BLOCK:
        return toast_response(
            f'Cannot disable critical rule {rule.rule_id}',
            'error'
        ), 400

    # Toggle enforcement between BLOCK (enabled) and GUIDE (disabled)
    new_level = (
        EnforcementLevel.GUIDE
        if rule.enforcement_level == EnforcementLevel.BLOCK
        else EnforcementLevel.BLOCK
    )

    # Update in database
    updated_rule = rule_methods.update_rule(db, rule_id, enforcement_level=new_level)

    # Broadcast WebSocket event for real-time updates (WI-125)
    broadcast_rule_toggle(
        rule_id=updated_rule.id,
        project_id=updated_rule.project_id or 1,  # Default to project 1 if null
        enabled=updated_rule.enabled,
        rule_code=updated_rule.rule_id,
        category=updated_rule.category
    )

    # Create updated RuleInfo for template
    updated_rule_info = RuleInfo(
        rule=updated_rule,
        is_active=updated_rule.enabled
    )

    # Return updated row HTML with toast notification
    response = make_response(
        render_template('partials/rule_row.html', rule_info=updated_rule_info)
    )
    add_toast(
        response,
        f'Rule {rule.rule_id} {"enabled" if new_level == EnforcementLevel.BLOCK else "disabled"}',
        'success'
    )
    if _is_htmx_request():
        return response

    return redirect_with_toast(
        url_for('config.rules_list'),
        f'Rule {rule.rule_id} {"enabled" if new_level == EnforcementLevel.BLOCK else "disabled"}',
        'success'
    )


# ========================================
# Agents Management
# ========================================

@config_bp.route('/agents')
def agents_list():
    """
    Agents list view.

    Returns:
        Rendered agents list template
    """
    db = get_database_service()

    # ✅ Use database methods instead of raw SQL
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


@config_bp.route('/agents/<int:agent_id>/toggle', methods=['POST'])
def agents_toggle(agent_id: int):
    """
    Toggle agent is_active status.

    HTMX endpoint that returns an updated agent row partial template.

    Args:
        agent_id: Agent database ID

    Returns:
        Updated agent_row.html partial with toast headers
    """
    db = get_database_service()

    # Get agent
    agent = agent_methods.get_agent(db, agent_id)
    if not agent:
        if _is_htmx_request():
            return toast_response('Agent not found', 'error'), 404
        return redirect_with_toast(
            url_for('config.agents_list'),
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
        url_for('config.agents_list'),
        message,
        'success'
    )


@config_bp.route('/agents/generate-form', methods=['GET'])
def agents_generate_form():
    """
    Load agent generation modal with framework detection.

    Detects frameworks in the project and suggests appropriate agents.

    Returns:
        Rendered agent_generate_modal.html partial
    """
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


@config_bp.route('/agents/generate', methods=['POST'])
def agents_generate():
    """
    Generate agents from form submission.

    Creates selected agents in the database with default configurations.

    Returns:
        Updated agents tbody partial with toast notification
    """
    db = get_database_service()

    # Get selected roles from form
    selected_roles = request.form.getlist('agents[]')

    # Get project ID (assuming first project for now)
    projects = project_methods.list_projects(db)
    if not projects:
        if _is_htmx_request():
            return toast_response('No project found', 'error'), 404
        return redirect_with_toast(
            url_for('config.agents_list'),
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
        url_for('config.agents_list'),
        message,
        toast_type
    )


# ========================================
# Project Settings (Inline Editing)
# ========================================

@config_bp.route('/project/<int:project_id>/settings')
def project_settings(project_id: int):
    """
    Project settings page.

    Args:
        project_id: Project ID

    Returns:
        Rendered project settings template
    """
    db = get_database_service()

    project = project_methods.get_project(db, project_id)
    if not project:
        abort(404, description=f"Project {project_id} not found")

    return render_template('project_settings.html', project=project)


@config_bp.route('/project/<int:project_id>/settings/name', methods=['GET'])
def project_name_field(project_id: int):
    """
    Load project name field (display or edit mode).

    Args:
        project_id: Project ID

    Returns:
        Rendered partial template
    """
    db = get_database_service()
    project = project_methods.get_project(db, project_id)

    if not project:
        abort(404, description=f"Project {project_id} not found")

    edit_mode = request.args.get('edit') == 'true'
    return render_template(
        'partials/project_name_field.html',
        project=project,
        edit_mode=edit_mode
    )


@config_bp.route('/project/<int:project_id>/update-name', methods=['POST'])
def project_update_name(project_id: int):
    """
    Update project name (inline edit save).

    Args:
        project_id: Project ID

    Returns:
        Updated partial template with toast headers
    """
    db = get_database_service()
    new_name = request.form.get('name', '').strip()

    # Validation
    if not new_name or len(new_name) > 200:
        project = project_methods.get_project(db, project_id)
        response = make_response(
            render_template('partials/project_name_field.html',
                          project=project,
                          edit_mode=True,
                          error='Name required (max 200 chars)')
        )
        add_toast(response, 'Invalid project name', 'error')
        if _is_htmx_request():
            return response, 400
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Invalid project name',
            'error'
        )

    # Update project
    updated_project = project_methods.update_project(db, project_id, name=new_name)

    if not updated_project:
        if _is_htmx_request():
            response = make_response('')
            add_toast(response, 'Project not found', 'error')
            return response, 404
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Project not found',
            'error'
        )

    # Return display mode
    response = make_response(
        render_template('partials/project_name_field.html',
                      project=updated_project,
                      edit_mode=False)
    )
    add_toast(response, 'Project name updated', 'success')
    if _is_htmx_request():
        return response
    return redirect_with_toast(
        url_for('config.project_settings', project_id=project_id),
        'Project name updated',
        'success'
    )


@config_bp.route('/project/<int:project_id>/settings/description', methods=['GET'])
def project_description_field(project_id: int):
    """
    Load project description field (display or edit mode).

    Args:
        project_id: Project ID

    Returns:
        Rendered partial template
    """
    db = get_database_service()
    project = project_methods.get_project(db, project_id)

    if not project:
        abort(404, description=f"Project {project_id} not found")

    edit_mode = request.args.get('edit') == 'true'
    return render_template(
        'partials/project_description_field.html',
        project=project,
        edit_mode=edit_mode
    )


@config_bp.route('/project/<int:project_id>/update-description', methods=['POST'])
def project_update_description(project_id: int):
    """
    Update project description (inline edit save).

    Args:
        project_id: Project ID

    Returns:
        Updated partial template with toast headers
    """
    db = get_database_service()
    new_description = request.form.get('description', '').strip()

    # Validation
    if len(new_description) > 1000:
        project = project_methods.get_project(db, project_id)
        response = make_response(
            render_template('partials/project_description_field.html',
                          project=project,
                          edit_mode=True,
                          error='Description max 1000 chars')
        )
        add_toast(response, 'Description too long', 'error')
        if _is_htmx_request():
            return response, 400
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Description too long',
            'error'
        )

    # Update project (allow empty description)
    updated_project = project_methods.update_project(
        db, project_id, description=new_description if new_description else None
    )

    if not updated_project:
        if _is_htmx_request():
            response = make_response('')
            add_toast(response, 'Project not found', 'error')
            return response, 404
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Project not found',
            'error'
        )

    # Return display mode
    response = make_response(
        render_template('partials/project_description_field.html',
                      project=updated_project,
                      edit_mode=False)
    )
    add_toast(response, 'Description updated', 'success')
    if _is_htmx_request():
        return response
    return redirect_with_toast(
        url_for('config.project_settings', project_id=project_id),
        'Description updated',
        'success'
    )


@config_bp.route('/project/<int:project_id>/settings/tech-stack', methods=['GET'])
def project_tech_stack_field(project_id: int):
    """
    Load project tech stack field (display or edit mode).

    Args:
        project_id: Project ID

    Returns:
        Rendered partial template
    """
    db = get_database_service()
    project = project_methods.get_project(db, project_id)

    if not project:
        abort(404, description=f"Project {project_id} not found")

    edit_mode = request.args.get('edit') == 'true'
    return render_template(
        'partials/project_tech_stack_field.html',
        project=project,
        edit_mode=edit_mode
    )


@config_bp.route('/project/<int:project_id>/update-tech-stack', methods=['POST'])
def project_update_tech_stack(project_id: int):
    """
    Update project tech stack (inline edit save).

    Args:
        project_id: Project ID

    Returns:
        Updated partial template with toast headers
    """
    db = get_database_service()
    tech_stack_str = request.form.get('tech_stack', '').strip()

    # Validation
    if len(tech_stack_str) > 500:
        project = project_methods.get_project(db, project_id)
        response = make_response(
            render_template('partials/project_tech_stack_field.html',
                          project=project,
                          edit_mode=True,
                          error='Tech stack max 500 chars')
        )
        add_toast(response, 'Tech stack too long', 'error')
        if _is_htmx_request():
            return response, 400
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Tech stack too long',
            'error'
        )

    # Parse comma-separated tech stack into list
    tech_stack_list = []
    if tech_stack_str:
        tech_stack_list = [
            tech.strip() for tech in tech_stack_str.split(',')
            if tech.strip()
        ]

    # Update project
    updated_project = project_methods.update_project(
        db, project_id, tech_stack=tech_stack_list
    )

    if not updated_project:
        if _is_htmx_request():
            response = make_response('')
            add_toast(response, 'Project not found', 'error')
            return response, 404
        return redirect_with_toast(
            url_for('config.project_settings', project_id=project_id),
            'Project not found',
            'error'
        )

    # Return display mode
    response = make_response(
        render_template('partials/project_tech_stack_field.html',
                      project=updated_project,
                      edit_mode=False)
    )
    add_toast(response, 'Technology stack updated', 'success')
    if _is_htmx_request():
        return response
    return redirect_with_toast(
        url_for('config.project_settings', project_id=project_id),
        'Technology stack updated',
        'success'
    )


# HTMX detection helper
def _is_htmx_request() -> bool:
    """Return True when request originates from HTMX."""
    return request.headers.get('HX-Request') == 'true'
