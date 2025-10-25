"""
Redirect Blueprint - Backward Compatibility Routes

Handles legacy route redirects to maintain backward compatibility
while transitioning to the new RESTful structure.
"""

from flask import Blueprint, redirect, url_for, request

redirects_bp = Blueprint('redirects', __name__)


# ========================================
# Legacy Route Redirects
# ========================================

@redirects_bp.route('/project/<int:project_id>')
def legacy_project_detail(project_id: int):
    """Redirect legacy project detail route to new structure."""
    return redirect(url_for('projects.project_detail', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/context')
def legacy_project_context(project_id: int):
    """Redirect legacy project context route to new structure."""
    return redirect(url_for('projects.project_context', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings')
def legacy_project_settings(project_id: int):
    """Redirect legacy project settings route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/analytics')
def legacy_project_analytics(project_id: int):
    """Redirect legacy project analytics route to new structure."""
    return redirect(url_for('projects.project_analytics', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update', methods=['POST'])
def legacy_project_update(project_id: int):
    """Redirect legacy project update route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/work-item/<int:work_item_id>')
def legacy_work_item_detail(work_item_id: int):
    """Redirect legacy work item detail route to new structure."""
    return redirect(url_for('work_items.work_item_detail', work_item_id=work_item_id))


@redirects_bp.route('/work-item/<int:work_item_id>/summaries')
def legacy_work_item_summaries(work_item_id: int):
    """Redirect legacy work item summaries route to new structure."""
    return redirect(url_for('work_items.work_item_summaries', work_item_id=work_item_id))


@redirects_bp.route('/work-item/<int:work_item_id>/context')
def legacy_work_item_context(work_item_id: int):
    """Redirect legacy work item context route to new structure."""
    return redirect(url_for('work_items.work_item_context', work_item_id=work_item_id))


@redirects_bp.route('/task/<int:task_id>')
def legacy_task_detail(task_id: int):
    """Redirect legacy task detail route to new structure."""
    return redirect(url_for('tasks.task_detail', task_id=task_id))


@redirects_bp.route('/idea/<int:idea_id>')
def legacy_idea_detail(idea_id: int):
    """Redirect legacy idea detail route to new structure."""
    return redirect(url_for('ideas.idea_detail', idea_id=idea_id))


@redirects_bp.route('/idea/<int:idea_id>/vote', methods=['POST'])
def legacy_idea_vote(idea_id: int):
    """Redirect legacy idea vote route to new structure."""
    return redirect(url_for('ideas.vote_on_idea', idea_id=idea_id))


@redirects_bp.route('/idea/<int:idea_id>/transition', methods=['POST'])
def legacy_idea_transition(idea_id: int):
    """Redirect legacy idea transition route to new structure."""
    return redirect(url_for('ideas.transition_idea', idea_id=idea_id))


@redirects_bp.route('/idea/<int:idea_id>/convert-form')
def legacy_idea_convert_form(idea_id: int):
    """Redirect legacy idea convert form route to new structure."""
    return redirect(url_for('ideas.idea_edit', idea_id=idea_id))


@redirects_bp.route('/idea/<int:idea_id>/convert', methods=['POST'])
def legacy_idea_convert(idea_id: int):
    """Redirect legacy idea convert route to new structure."""
    return redirect(url_for('ideas.convert_idea_to_work_item', idea_id=idea_id))


@redirects_bp.route('/session/<session_id>')
def legacy_session_detail(session_id: str):
    """Redirect legacy session detail route to new structure."""
    return redirect(url_for('sessions.session_detail', session_id=session_id))


@redirects_bp.route('/context/<int:context_id>')
def legacy_context_detail(context_id: int):
    """Redirect legacy context detail route to new structure."""
    return redirect(url_for('contexts.context_detail', context_id=context_id))


@redirects_bp.route('/context/<int:context_id>/refresh', methods=['POST'])
def legacy_context_refresh(context_id: int):
    """Redirect legacy context refresh route to new structure."""
    return redirect(url_for('contexts.context_refresh', context_id=context_id))


@redirects_bp.route('/health')
def legacy_health():
    """Redirect legacy health route to new structure."""
    return redirect(url_for('system.system_health'))


@redirects_bp.route('/workflow')
def legacy_workflow():
    """Redirect legacy workflow route to new structure."""
    return redirect(url_for('system.workflow_visualization'))


@redirects_bp.route('/context-files')
def legacy_context_files():
    """Redirect legacy context files route to new structure."""
    return redirect(url_for('system.context_files'))


@redirects_bp.route('/context-files/preview/<path:filepath>')
def legacy_context_file_preview(filepath: str):
    """Redirect legacy context file preview route to new structure."""
    return redirect(url_for('system.context_file_preview', filepath=filepath))


@redirects_bp.route('/context-files/download/<path:filepath>')
def legacy_context_file_download(filepath: str):
    """Redirect legacy context file download route to new structure."""
    return redirect(url_for('system.context_file_download', filepath=filepath))


# ========================================
# Legacy Configuration Routes
# ========================================

@redirects_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
def legacy_rule_toggle(rule_id: int):
    """Redirect legacy rule toggle route to new structure."""
    return redirect(url_for('rules.rules_toggle', rule_id=rule_id))


@redirects_bp.route('/agents/<int:agent_id>/toggle', methods=['POST'])
def legacy_agent_toggle(agent_id: int):
    """Redirect legacy agent toggle route to new structure."""
    return redirect(url_for('agents.agents_toggle', agent_id=agent_id))


@redirects_bp.route('/agents/generate-form')
def legacy_agents_generate_form():
    """Redirect legacy agents generate form route to new structure."""
    return redirect(url_for('agents.agents_generate_form'))


@redirects_bp.route('/agents/generate', methods=['POST'])
def legacy_agents_generate():
    """Redirect legacy agents generate route to new structure."""
    return redirect(url_for('agents.agents_generate'))


# ========================================
# Legacy Project Settings Routes
# ========================================

@redirects_bp.route('/project/<int:project_id>/settings/name')
def legacy_project_settings_name(project_id: int):
    """Redirect legacy project settings name route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-name', methods=['POST'])
def legacy_project_update_name(project_id: int):
    """Redirect legacy project update name route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/description')
def legacy_project_settings_description(project_id: int):
    """Redirect legacy project settings description route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-description', methods=['POST'])
def legacy_project_update_description(project_id: int):
    """Redirect legacy project update description route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/philosophy')
def legacy_project_settings_philosophy(project_id: int):
    """Redirect legacy project settings philosophy route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-philosophy', methods=['POST'])
def legacy_project_update_philosophy(project_id: int):
    """Redirect legacy project update philosophy route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/type')
def legacy_project_settings_type(project_id: int):
    """Redirect legacy project settings type route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-type', methods=['POST'])
def legacy_project_update_type(project_id: int):
    """Redirect legacy project update type route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/domain')
def legacy_project_settings_domain(project_id: int):
    """Redirect legacy project settings domain route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-domain', methods=['POST'])
def legacy_project_update_domain(project_id: int):
    """Redirect legacy project update domain route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/business-description')
def legacy_project_settings_business_description(project_id: int):
    """Redirect legacy project settings business description route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-business-description', methods=['POST'])
def legacy_project_update_business_description(project_id: int):
    """Redirect legacy project update business description route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/settings/team')
def legacy_project_settings_team(project_id: int):
    """Redirect legacy project settings team route to new structure."""
    return redirect(url_for('projects.project_settings', project_id=project_id))


@redirects_bp.route('/project/<int:project_id>/update-team', methods=['POST'])
def legacy_project_update_team(project_id: int):
    """Redirect legacy project update team route to new structure."""
    return redirect(url_for('projects.project_update', project_id=project_id))
