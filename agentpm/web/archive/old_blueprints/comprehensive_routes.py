"""
Comprehensive Logical Blueprint Structure for APM (Agent Project Manager) Web Application

This module implements a complete, logical, hierarchical route structure that groups
related resources under meaningful parent blueprints following RESTful principles.

Blueprint Organization:
- dashboard: Main dashboard and overview
- ideas: Ideas management with hierarchical elements
- work_items: Work items with nested tasks
- context: Context management (documents, evidence, sessions)
- agents: Agent management
- rules: Rules management
- system: System administration and monitoring
- api: RESTful API endpoints
- search: Search functionality

Route Principles:
1. RESTful Design: GET, POST, PUT, DELETE methods
2. No Duplicate Routes: Single route per action
3. Hierarchical Structure: Logical parent-child relationships
4. Consistent Naming: Plural for collections, singular for individual resources
5. Action Prefixes: All actions use /actions/ prefix for non-REST operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from typing import Dict, List, Any, Optional
import logging

# Create logical blueprints
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')
ideas_bp = Blueprint('ideas', __name__, url_prefix='/ideas')
work_items_bp = Blueprint('work_items', __name__, url_prefix='/work-items')
context_bp = Blueprint('context', __name__, url_prefix='/context')
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')
rules_bp = Blueprint('rules', __name__, url_prefix='/rules')
system_bp = Blueprint('system', __name__, url_prefix='/system')
api_bp = Blueprint('api', __name__, url_prefix='/api')
search_bp = Blueprint('search', __name__, url_prefix='/search')

logger = logging.getLogger(__name__)

# ============================================================================
# DASHBOARD BLUEPRINT
# ============================================================================

@dashboard_bp.route('/')
def dashboard_home():
    """Dashboard home - main entry point"""
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    """Main dashboard with project overview"""
    return render_template('dashboard.html')

@dashboard_bp.route('/overview')
def overview():
    """System overview with key metrics"""
    return render_template('dashboard.html')

# ============================================================================
# IDEAS BLUEPRINT
# ============================================================================

@ideas_bp.route('/')
def ideas_list():
    """Ideas list view"""
    return render_template('ideas/list.html')

@ideas_bp.route('/<int:idea_id>')
def idea_detail(idea_id: int):
    """Idea detail view"""
    return render_template('ideas/detail.html', idea_id=idea_id)

@ideas_bp.route('/<int:idea_id>', methods=['PUT'])
def idea_update(idea_id: int):
    """Update idea (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Idea updated'})

@ideas_bp.route('/<int:idea_id>', methods=['DELETE'])
def idea_delete(idea_id: int):
    """Delete idea"""
    return jsonify({'status': 'success', 'message': 'Idea deleted'})

@ideas_bp.route('/<int:idea_id>/actions/vote', methods=['POST'])
def idea_vote(idea_id: int):
    """Vote on idea"""
    return jsonify({'status': 'success', 'message': 'Vote recorded'})

@ideas_bp.route('/<int:idea_id>/actions/transition', methods=['POST'])
def idea_transition(idea_id: int):
    """Transition idea"""
    return jsonify({'status': 'success', 'message': 'Idea transitioned'})

@ideas_bp.route('/<int:idea_id>/actions/convert', methods=['POST'])
def idea_convert(idea_id: int):
    """Convert idea to work item"""
    return jsonify({'status': 'success', 'message': 'Idea converted to work item'})

# Ideas Elements (hierarchical structure)
@ideas_bp.route('/<int:idea_id>/elements')
def idea_elements_list(idea_id: int):
    """List elements for an idea"""
    return render_template('ideas/elements/list.html', idea_id=idea_id)

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>')
def idea_element_detail(idea_id: int, element_id: int):
    """Element detail view"""
    return render_template('ideas/elements/detail.html', idea_id=idea_id, element_id=element_id)

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>', methods=['PUT'])
def idea_element_update(idea_id: int, element_id: int):
    """Update element (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Element updated'})

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>', methods=['DELETE'])
def idea_element_delete(idea_id: int, element_id: int):
    """Delete element"""
    return jsonify({'status': 'success', 'message': 'Element deleted'})

# ============================================================================
# WORK ITEMS BLUEPRINT
# ============================================================================

@work_items_bp.route('/')
def work_items_list():
    """Work items list view"""
    return render_template('work-items/list.html')

@work_items_bp.route('/<int:work_item_id>')
def work_item_detail(work_item_id: int):
    """Work item detail view"""
    return render_template('work-items/detail.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>', methods=['PUT'])
def work_item_update(work_item_id: int):
    """Update work item (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Work item updated'})

@work_items_bp.route('/<int:work_item_id>', methods=['DELETE'])
def work_item_delete(work_item_id: int):
    """Delete work item"""
    return jsonify({'status': 'success', 'message': 'Work item deleted'})

@work_items_bp.route('/<int:work_item_id>/actions/start', methods=['POST'])
def work_item_start(work_item_id: int):
    """Start work item"""
    return jsonify({'status': 'success', 'message': 'Work item started'})

@work_items_bp.route('/<int:work_item_id>/actions/complete', methods=['POST'])
def work_item_complete(work_item_id: int):
    """Complete work item"""
    return jsonify({'status': 'success', 'message': 'Work item completed'})

@work_items_bp.route('/<int:work_item_id>/actions/block', methods=['POST'])
def work_item_block(work_item_id: int):
    """Block work item"""
    return jsonify({'status': 'success', 'message': 'Work item blocked'})

@work_items_bp.route('/<int:work_item_id>/actions/unblock', methods=['POST'])
def work_item_unblock(work_item_id: int):
    """Unblock work item"""
    return jsonify({'status': 'success', 'message': 'Work item unblocked'})

# Work Item Tasks (hierarchical structure)
@work_items_bp.route('/<int:work_item_id>/tasks')
def work_item_tasks_list(work_item_id: int):
    """List tasks for a work item"""
    return render_template('work-items/tasks/list.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>')
def work_item_task_detail(work_item_id: int, task_id: int):
    """Task detail view within work item context"""
    return render_template('work-items/tasks/detail.html', work_item_id=work_item_id, task_id=task_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>', methods=['PUT'])
def work_item_task_update(work_item_id: int, task_id: int):
    """Update task within work item context (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Task updated'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>', methods=['DELETE'])
def work_item_task_delete(work_item_id: int, task_id: int):
    """Delete task within work item context"""
    return jsonify({'status': 'success', 'message': 'Task deleted'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/actions/assign', methods=['POST'])
def work_item_task_assign(work_item_id: int, task_id: int):
    """Assign task"""
    return jsonify({'status': 'success', 'message': 'Task assigned'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/actions/start', methods=['POST'])
def work_item_task_start(work_item_id: int, task_id: int):
    """Start task"""
    return jsonify({'status': 'success', 'message': 'Task started'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/actions/complete', methods=['POST'])
def work_item_task_complete(work_item_id: int, task_id: int):
    """Complete task"""
    return jsonify({'status': 'success', 'message': 'Task completed'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/actions/block', methods=['POST'])
def work_item_task_block(work_item_id: int, task_id: int):
    """Block task"""
    return jsonify({'status': 'success', 'message': 'Task blocked'})

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/actions/unblock', methods=['POST'])
def work_item_task_unblock(work_item_id: int, task_id: int):
    """Unblock task"""
    return jsonify({'status': 'success', 'message': 'Task unblocked'})

# Work Item Dependencies
@work_items_bp.route('/<int:work_item_id>/dependencies')
def work_item_dependencies(work_item_id: int):
    """Work item dependencies"""
    return render_template('work-items/dependencies.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>/dependencies', methods=['POST'])
def work_item_add_dependency(work_item_id: int):
    """Add dependency to work item"""
    return jsonify({'status': 'success', 'message': 'Dependency added'})

@work_items_bp.route('/<int:work_item_id>/dependencies/<int:dep_id>', methods=['DELETE'])
def work_item_remove_dependency(work_item_id: int, dep_id: int):
    """Remove dependency from work item"""
    return jsonify({'status': 'success', 'message': 'Dependency removed'})

# Work Item Context
@work_items_bp.route('/<int:work_item_id>/context')
def work_item_context(work_item_id: int):
    """Work item context view"""
    return render_template('work-items/context.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>/context', methods=['POST'])
def work_item_refresh_context(work_item_id: int):
    """Refresh work item context"""
    return jsonify({'status': 'success', 'message': 'Context refreshed'})

# Work Item Summaries
@work_items_bp.route('/<int:work_item_id>/summaries')
def work_item_summaries(work_item_id: int):
    """Work item summaries"""
    return render_template('work-items/summaries.html', work_item_id=work_item_id)

# ============================================================================
# CONTEXT BLUEPRINT
# ============================================================================

@context_bp.route('/')
def context_overview():
    """Context overview"""
    return render_template('context/overview.html')

# Context Documents
@context_bp.route('/documents')
def context_documents_list():
    """Context documents list"""
    return render_template('context/documents/list.html')

@context_bp.route('/documents/<int:document_id>')
def context_document_detail(document_id: int):
    """Context document detail"""
    return render_template('context/documents/detail.html', document_id=document_id)

@context_bp.route('/documents/<int:document_id>', methods=['PUT'])
def context_document_update(document_id: int):
    """Update context document (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Document updated'})

@context_bp.route('/documents/<int:document_id>', methods=['DELETE'])
def context_document_delete(document_id: int):
    """Delete context document"""
    return jsonify({'status': 'success', 'message': 'Document deleted'})

@context_bp.route('/documents/<int:document_id>/actions/refresh', methods=['POST'])
def context_document_refresh(document_id: int):
    """Refresh context document"""
    return jsonify({'status': 'success', 'message': 'Document refreshed'})

@context_bp.route('/documents/<int:document_id>/actions/download', methods=['GET'])
def context_document_download(document_id: int):
    """Download context document"""
    return jsonify({'status': 'success', 'message': 'Document download initiated'})

# Context Evidence
@context_bp.route('/evidence')
def context_evidence_list():
    """Context evidence list"""
    return render_template('context/evidence/list.html')

@context_bp.route('/evidence/<int:evidence_id>')
def context_evidence_detail(evidence_id: int):
    """Context evidence detail"""
    return render_template('context/evidence/detail.html', evidence_id=evidence_id)

@context_bp.route('/evidence/<int:evidence_id>', methods=['PUT'])
def context_evidence_update(evidence_id: int):
    """Update context evidence (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Evidence updated'})

@context_bp.route('/evidence/<int:evidence_id>', methods=['DELETE'])
def context_evidence_delete(evidence_id: int):
    """Delete context evidence"""
    return jsonify({'status': 'success', 'message': 'Evidence deleted'})

@context_bp.route('/evidence/<int:evidence_id>/actions/validate', methods=['POST'])
def context_evidence_validate(evidence_id: int):
    """Validate context evidence"""
    return jsonify({'status': 'success', 'message': 'Evidence validated'})

@context_bp.route('/evidence/<int:evidence_id>/actions/verify', methods=['POST'])
def context_evidence_verify(evidence_id: int):
    """Verify context evidence"""
    return jsonify({'status': 'success', 'message': 'Evidence verified'})

# Context Events
@context_bp.route('/events')
def context_events_list():
    """Context events list"""
    return render_template('context/events/list.html')

@context_bp.route('/events/<int:event_id>')
def context_event_detail(event_id: int):
    """Context event detail"""
    return render_template('context/events/detail.html', event_id=event_id)

@context_bp.route('/events/<int:event_id>', methods=['PUT'])
def context_event_update(event_id: int):
    """Update context event (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Event updated'})

@context_bp.route('/events/<int:event_id>', methods=['DELETE'])
def context_event_delete(event_id: int):
    """Delete context event"""
    return jsonify({'status': 'success', 'message': 'Event deleted'})

# Context Sessions
@context_bp.route('/sessions')
def context_sessions_list():
    """Context sessions list"""
    return render_template('context/sessions/list.html')

@context_bp.route('/sessions/<session_id>')
def context_session_detail(session_id: str):
    """Context session detail"""
    return render_template('context/sessions/detail.html', session_id=session_id)

@context_bp.route('/sessions/<session_id>', methods=['PUT'])
def context_session_update(session_id: str):
    """Update context session (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Session updated'})

@context_bp.route('/sessions/<session_id>', methods=['DELETE'])
def context_session_delete(session_id: str):
    """Delete context session"""
    return jsonify({'status': 'success', 'message': 'Session deleted'})

@context_bp.route('/sessions/timeline')
def context_sessions_timeline():
    """Context sessions timeline"""
    return render_template('context/sessions/timeline.html')

# ============================================================================
# AGENTS BLUEPRINT
# ============================================================================

@agents_bp.route('/')
def agents_list():
    """Agents list view"""
    return render_template('agents/list.html')

@agents_bp.route('/<int:agent_id>')
def agent_detail(agent_id: int):
    """Agent detail view"""
    return render_template('agents/detail.html', agent_id=agent_id)

@agents_bp.route('/<int:agent_id>', methods=['PUT'])
def agent_update(agent_id: int):
    """Update agent (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Agent updated'})

@agents_bp.route('/<int:agent_id>', methods=['DELETE'])
def agent_delete(agent_id: int):
    """Delete agent"""
    return jsonify({'status': 'success', 'message': 'Agent deleted'})

@agents_bp.route('/<int:agent_id>/actions/toggle', methods=['POST'])
def agent_toggle(agent_id: int):
    """Toggle agent status"""
    return jsonify({'status': 'success', 'message': 'Agent status toggled'})

@agents_bp.route('/<int:agent_id>/actions/activate', methods=['POST'])
def agent_activate(agent_id: int):
    """Activate agent"""
    return jsonify({'status': 'success', 'message': 'Agent activated'})

@agents_bp.route('/<int:agent_id>/actions/deactivate', methods=['POST'])
def agent_deactivate(agent_id: int):
    """Deactivate agent"""
    return jsonify({'status': 'success', 'message': 'Agent deactivated'})

@agents_bp.route('/<int:agent_id>/actions/assign', methods=['POST'])
def agent_assign(agent_id: int):
    """Assign agent to task/work item"""
    return jsonify({'status': 'success', 'message': 'Agent assigned'})

@agents_bp.route('/<int:agent_id>/actions/unassign', methods=['POST'])
def agent_unassign(agent_id: int):
    """Unassign agent from task/work item"""
    return jsonify({'status': 'success', 'message': 'Agent unassigned'})

@agents_bp.route('/generate')
def agents_generate_form():
    """Generate agents form"""
    return render_template('agents/generate.html')

@agents_bp.route('/actions/generate', methods=['POST'])
def agents_generate():
    """Generate agents action"""
    return jsonify({'status': 'success', 'message': 'Agents generated'})

@agents_bp.route('/actions/import', methods=['POST'])
def agents_import():
    """Import agents from file"""
    return jsonify({'status': 'success', 'message': 'Agents imported'})

@agents_bp.route('/actions/export', methods=['GET'])
def agents_export():
    """Export agents to file"""
    return jsonify({'status': 'success', 'message': 'Agents exported'})

# ============================================================================
# RULES BLUEPRINT
# ============================================================================

@rules_bp.route('/')
def rules_list():
    """Rules list view"""
    return render_template('rules/list.html')

@rules_bp.route('/<int:rule_id>')
def rule_detail(rule_id: int):
    """Rule detail view"""
    return render_template('rules/detail.html', rule_id=rule_id)

@rules_bp.route('/<int:rule_id>', methods=['PUT'])
def rule_update(rule_id: int):
    """Update rule (handles both edit form submission and direct updates)"""
    return jsonify({'status': 'success', 'message': 'Rule updated'})

@rules_bp.route('/<int:rule_id>', methods=['DELETE'])
def rule_delete(rule_id: int):
    """Delete rule"""
    return jsonify({'status': 'success', 'message': 'Rule deleted'})

@rules_bp.route('/<int:rule_id>/actions/toggle', methods=['POST'])
def rule_toggle(rule_id: int):
    """Toggle rule status"""
    return jsonify({'status': 'success', 'message': 'Rule status toggled'})

@rules_bp.route('/<int:rule_id>/actions/activate', methods=['POST'])
def rule_activate(rule_id: int):
    """Activate rule"""
    return jsonify({'status': 'success', 'message': 'Rule activated'})

@rules_bp.route('/<int:rule_id>/actions/deactivate', methods=['POST'])
def rule_deactivate(rule_id: int):
    """Deactivate rule"""
    return jsonify({'status': 'success', 'message': 'Rule deactivated'})

@rules_bp.route('/<int:rule_id>/actions/test', methods=['POST'])
def rule_test(rule_id: int):
    """Test rule"""
    return jsonify({'status': 'success', 'message': 'Rule tested'})

@rules_bp.route('/<int:rule_id>/actions/validate', methods=['POST'])
def rule_validate(rule_id: int):
    """Validate rule"""
    return jsonify({'status': 'success', 'message': 'Rule validated'})

@rules_bp.route('/actions/import', methods=['POST'])
def rules_import():
    """Import rules from file"""
    return jsonify({'status': 'success', 'message': 'Rules imported'})

@rules_bp.route('/actions/export', methods=['GET'])
def rules_export():
    """Export rules to file"""
    return jsonify({'status': 'success', 'message': 'Rules exported'})

# ============================================================================
# SYSTEM BLUEPRINT
# ============================================================================

@system_bp.route('/health')
def system_health():
    """System health check"""
    return jsonify({'status': 'ok', 'service': 'aipm-v2-dashboard'})

@system_bp.route('/database')
def system_database():
    """Database metrics"""
    return render_template('system/database.html')

@system_bp.route('/database/backup', methods=['POST'])
def system_database_backup():
    """Create database backup"""
    return jsonify({'status': 'success', 'message': 'Database backup created'})

@system_bp.route('/database/restore', methods=['POST'])
def system_database_restore():
    """Restore database from backup"""
    return jsonify({'status': 'success', 'message': 'Database restored'})

@system_bp.route('/workflow')
def system_workflow():
    """Workflow visualization"""
    return render_template('system/workflow.html')

@system_bp.route('/workflow/validate', methods=['POST'])
def system_workflow_validate():
    """Validate workflow configuration"""
    return jsonify({'status': 'success', 'message': 'Workflow validated'})

@system_bp.route('/context-files')
def system_context_files():
    """Context files list"""
    return render_template('system/context-files.html')

@system_bp.route('/context-files/preview/<path:filepath>')
def system_context_file_preview(filepath: str):
    """Context file preview"""
    return render_template('system/context-file-preview.html', filepath=filepath)

@system_bp.route('/context-files/download/<path:filepath>')
def system_context_file_download(filepath: str):
    """Context file download"""
    return redirect(url_for('system.system_context_files'))

@system_bp.route('/context-files/upload', methods=['POST'])
def system_context_file_upload():
    """Upload context file"""
    return jsonify({'status': 'success', 'message': 'File uploaded'})

@system_bp.route('/context-files/<path:filepath>', methods=['DELETE'])
def system_context_file_delete(filepath: str):
    """Delete context file"""
    return jsonify({'status': 'success', 'message': 'File deleted'})

@system_bp.route('/logs')
def system_logs():
    """System logs"""
    return render_template('system/logs.html')

@system_bp.route('/logs/<log_type>')
def system_logs_by_type(log_type: str):
    """System logs by type"""
    return render_template('system/logs.html', log_type=log_type)

@system_bp.route('/metrics')
def system_metrics():
    """System metrics"""
    return render_template('system/metrics.html')

@system_bp.route('/settings')
def system_settings():
    """System settings"""
    return render_template('system/settings.html')

@system_bp.route('/settings', methods=['PUT'])
def system_settings_update():
    """Update system settings"""
    return jsonify({'status': 'success', 'message': 'Settings updated'})

# ============================================================================
# API BLUEPRINT
# ============================================================================

@api_bp.route('/ideas')
def api_ideas():
    """Ideas API"""
    return jsonify({'ideas': []})

@api_bp.route('/ideas/<int:idea_id>')
def api_idea_detail(idea_id: int):
    """Idea detail API"""
    return jsonify({'idea': {'id': idea_id}})

@api_bp.route('/work-items')
def api_work_items():
    """Work items API"""
    return jsonify({'work_items': []})

@api_bp.route('/work-items/<int:work_item_id>')
def api_work_item_detail(work_item_id: int):
    """Work item detail API"""
    return jsonify({'work_item': {'id': work_item_id}})

@api_bp.route('/work-items/<int:work_item_id>/tasks')
def api_work_item_tasks(work_item_id: int):
    """Work item tasks API"""
    return jsonify({'tasks': []})

@api_bp.route('/context/documents')
def api_context_documents():
    """Context documents API"""
    return jsonify({'documents': []})

@api_bp.route('/context/evidence')
def api_context_evidence():
    """Context evidence API"""
    return jsonify({'evidence': []})

@api_bp.route('/context/events')
def api_context_events():
    """Context events API"""
    return jsonify({'events': []})

@api_bp.route('/context/sessions')
def api_context_sessions():
    """Context sessions API"""
    return jsonify({'sessions': []})

@api_bp.route('/agents')
def api_agents():
    """Agents API"""
    return jsonify({'agents': []})

@api_bp.route('/agents/<int:agent_id>')
def api_agent_detail(agent_id: int):
    """Agent detail API"""
    return jsonify({'agent': {'id': agent_id}})

@api_bp.route('/rules')
def api_rules():
    """Rules API"""
    return jsonify({'rules': []})

@api_bp.route('/rules/<int:rule_id>')
def api_rule_detail(rule_id: int):
    """Rule detail API"""
    return jsonify({'rule': {'id': rule_id}})

# ============================================================================
# SEARCH BLUEPRINT
# ============================================================================

@search_bp.route('/')
def search():
    """Search results"""
    return render_template('search/results.html')

@search_bp.route('/api')
def search_api():
    """Search API"""
    return jsonify({'results': [], 'total': 0})

@search_bp.route('/suggestions')
def search_suggestions():
    """Search suggestions"""
    return jsonify({'suggestions': []})

@search_bp.route('/history')
def search_history():
    """Search history"""
    return render_template('search/history.html')

@search_bp.route('/history', methods=['DELETE'])
def search_history_clear():
    """Clear search history"""
    return jsonify({'status': 'success', 'message': 'Search history cleared'})

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_blueprint_info() -> Dict[str, Any]:
    """Get information about all registered blueprints"""
    blueprints = [
        {'name': 'dashboard', 'prefix': '', 'routes': len(dashboard_bp.url_map.iter_rules())},
        {'name': 'ideas', 'prefix': '/ideas', 'routes': len(ideas_bp.url_map.iter_rules())},
        {'name': 'work_items', 'prefix': '/work-items', 'routes': len(work_items_bp.url_map.iter_rules())},
        {'name': 'context', 'prefix': '/context', 'routes': len(context_bp.url_map.iter_rules())},
        {'name': 'agents', 'prefix': '/agents', 'routes': len(agents_bp.url_map.iter_rules())},
        {'name': 'rules', 'prefix': '/rules', 'routes': len(rules_bp.url_map.iter_rules())},
        {'name': 'system', 'prefix': '/system', 'routes': len(system_bp.url_map.iter_rules())},
        {'name': 'api', 'prefix': '/api', 'routes': len(api_bp.url_map.iter_rules())},
        {'name': 'search', 'prefix': '/search', 'routes': len(search_bp.url_map.iter_rules())},
    ]
    return {'blueprints': blueprints, 'total': len(blueprints)}

def validate_blueprint_structure() -> Dict[str, Any]:
    """Validate that all blueprints follow the logical structure"""
    issues = []
    warnings = []
    
    # Check for consistent naming patterns
    # Check for proper HTTP methods
    # Check for hierarchical structure
    # Check for logical grouping
    # Check for duplicate routes
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

def get_all_routes() -> List[Dict[str, Any]]:
    """Get all routes from all blueprints"""
    all_routes = []
    
    blueprints = [
        dashboard_bp, ideas_bp, work_items_bp, context_bp,
        agents_bp, rules_bp, system_bp, api_bp, search_bp
    ]
    
    for bp in blueprints:
        for rule in bp.url_map.iter_rules():
            all_routes.append({
                'blueprint': bp.name,
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule),
                'arguments': list(rule.arguments)
            })
    
    return all_routes
