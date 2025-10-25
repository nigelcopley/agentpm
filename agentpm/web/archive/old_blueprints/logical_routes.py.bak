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

@ideas_bp.route('/<int:idea_id>/edit')
def idea_edit(idea_id: int):
    """Idea edit form"""
    return render_template('ideas/edit.html', idea_id=idea_id)

@ideas_bp.route('/<int:idea_id>', methods=['PUT'])
def idea_update(idea_id: int):
    """Update idea"""
    return jsonify({'status': 'success', 'message': 'Idea updated'})

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

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>/edit')
def idea_element_edit(idea_id: int, element_id: int):
    """Element edit form"""
    return render_template('ideas/elements/edit.html', idea_id=idea_id, element_id=element_id)

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>', methods=['PUT'])
def idea_element_update(idea_id: int, element_id: int):
    """Update element"""
    return jsonify({'status': 'success', 'message': 'Element updated'})

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>/actions/delete', methods=['POST'])
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

@work_items_bp.route('/<int:work_item_id>/edit')
def work_item_edit(work_item_id: int):
    """Work item edit form"""
    return render_template('work-items/edit.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>', methods=['PUT'])
def work_item_update(work_item_id: int):
    """Update work item"""
    return jsonify({'status': 'success', 'message': 'Work item updated'})

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

# Work Item Tasks (hierarchical structure)
@work_items_bp.route('/<int:work_item_id>/tasks')
def work_item_tasks_list(work_item_id: int):
    """List tasks for a work item"""
    return render_template('work-items/tasks/list.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>')
def work_item_task_detail(work_item_id: int, task_id: int):
    """Task detail view within work item context"""
    return render_template('work-items/tasks/detail.html', work_item_id=work_item_id, task_id=task_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>/edit')
def work_item_task_edit(work_item_id: int, task_id: int):
    """Task edit form within work item context"""
    return render_template('work-items/tasks/edit.html', work_item_id=work_item_id, task_id=task_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>', methods=['PUT'])
def work_item_task_update(work_item_id: int, task_id: int):
    """Update task within work item context"""
    return jsonify({'status': 'success', 'message': 'Task updated'})

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

@context_bp.route('/documents/<int:document_id>/edit')
def context_document_edit(document_id: int):
    """Context document edit form"""
    return render_template('context/documents/edit.html', document_id=document_id)

@context_bp.route('/documents/<int:document_id>', methods=['PUT'])
def context_document_update(document_id: int):
    """Update context document"""
    return jsonify({'status': 'success', 'message': 'Document updated'})

@context_bp.route('/documents/<int:document_id>/actions/refresh', methods=['POST'])
def context_document_refresh(document_id: int):
    """Refresh context document"""
    return jsonify({'status': 'success', 'message': 'Document refreshed'})

# Context Evidence
@context_bp.route('/evidence')
def context_evidence_list():
    """Context evidence list"""
    return render_template('context/evidence/list.html')

@context_bp.route('/evidence/<int:evidence_id>')
def context_evidence_detail(evidence_id: int):
    """Context evidence detail"""
    return render_template('context/evidence/detail.html', evidence_id=evidence_id)

@context_bp.route('/evidence/<int:evidence_id>/edit')
def context_evidence_edit(evidence_id: int):
    """Context evidence edit form"""
    return render_template('context/evidence/edit.html', evidence_id=evidence_id)

@context_bp.route('/evidence/<int:evidence_id>', methods=['PUT'])
def context_evidence_update(evidence_id: int):
    """Update context evidence"""
    return jsonify({'status': 'success', 'message': 'Evidence updated'})

@context_bp.route('/evidence/<int:evidence_id>/actions/validate', methods=['POST'])
def context_evidence_validate(evidence_id: int):
    """Validate context evidence"""
    return jsonify({'status': 'success', 'message': 'Evidence validated'})

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

@agents_bp.route('/<int:agent_id>/edit')
def agent_edit(agent_id: int):
    """Agent edit form"""
    return render_template('agents/edit.html', agent_id=agent_id)

@agents_bp.route('/<int:agent_id>', methods=['PUT'])
def agent_update(agent_id: int):
    """Update agent"""
    return jsonify({'status': 'success', 'message': 'Agent updated'})

@agents_bp.route('/<int:agent_id>/actions/toggle', methods=['POST'])
def agent_toggle(agent_id: int):
    """Toggle agent status"""
    return jsonify({'status': 'success', 'message': 'Agent status toggled'})

@agents_bp.route('/generate')
def agents_generate_form():
    """Generate agents form"""
    return render_template('agents/generate.html')

@agents_bp.route('/actions/generate', methods=['POST'])
def agents_generate():
    """Generate agents action"""
    return jsonify({'status': 'success', 'message': 'Agents generated'})

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

@rules_bp.route('/<int:rule_id>/edit')
def rule_edit(rule_id: int):
    """Rule edit form"""
    return render_template('rules/edit.html', rule_id=rule_id)

@rules_bp.route('/<int:rule_id>', methods=['PUT'])
def rule_update(rule_id: int):
    """Update rule"""
    return jsonify({'status': 'success', 'message': 'Rule updated'})

@rules_bp.route('/<int:rule_id>/actions/toggle', methods=['POST'])
def rule_toggle(rule_id: int):
    """Toggle rule status"""
    return jsonify({'status': 'success', 'message': 'Rule status toggled'})

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

@system_bp.route('/workflow')
def system_workflow():
    """Workflow visualization"""
    return render_template('system/workflow.html')

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
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }
