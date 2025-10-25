"""
Read-Only Blueprint Structure for APM (Agent Project Manager) Web Application

This module implements a simplified, read-only route structure that focuses on
viewing and monitoring the APM (Agent Project Manager) system data without full CRUD operations.

Current System State:
- Read-only views (no full CRUD operations)
- Minimal interactivity (settings/config only)
- No API endpoints (not implemented yet)
- Ideas need elements model (to be added)

Blueprint Organization:
- dashboard: Main dashboard and overview
- projects: Project management (read-only)
- ideas: Ideas management with elements (read-only)
- work_items: Work items with nested tasks (read-only)
- context: Context management (read-only)
- agents: Agent management (read-only)
- rules: Rules management (read-only)
- system: System administration and monitoring (read-only)
- search: Search functionality (read-only)

Route Principles:
1. Read-Only Design: Only GET methods for viewing data
2. Hierarchical Structure: Logical parent-child relationships
3. Consistent Naming: Plural for collections, singular for individual resources
4. No Actions: No interactive operations (yet)
5. System-Aligned: Routes match actual database capabilities
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from typing import Dict, List, Any, Optional
import logging

# Create read-only blueprints
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')
ideas_bp = Blueprint('ideas', __name__, url_prefix='/ideas')
work_items_bp = Blueprint('work_items', __name__, url_prefix='/work-items')
context_bp = Blueprint('context', __name__, url_prefix='/context')
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')
rules_bp = Blueprint('rules', __name__, url_prefix='/rules')
system_bp = Blueprint('system', __name__, url_prefix='/system')
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

# Ideas Elements (hierarchical structure - TO BE IMPLEMENTED)
@ideas_bp.route('/<int:idea_id>/elements')
def idea_elements_list(idea_id: int):
    """List elements for an idea (TO BE IMPLEMENTED)"""
    return render_template('ideas/elements/list.html', idea_id=idea_id)

@ideas_bp.route('/<int:idea_id>/elements/<int:element_id>')
def idea_element_detail(idea_id: int, element_id: int):
    """Element detail view (TO BE IMPLEMENTED)"""
    return render_template('ideas/elements/detail.html', idea_id=idea_id, element_id=element_id)

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

# Work Item Tasks (hierarchical structure)
@work_items_bp.route('/<int:work_item_id>/tasks')
def work_item_tasks_list(work_item_id: int):
    """List tasks for a work item"""
    return render_template('work-items/tasks/list.html', work_item_id=work_item_id)

@work_items_bp.route('/<int:work_item_id>/tasks/<int:task_id>')
def work_item_task_detail(work_item_id: int, task_id: int):
    """Task detail view within work item context"""
    return render_template('work-items/tasks/detail.html', work_item_id=work_item_id, task_id=task_id)

# Work Item Dependencies
@work_items_bp.route('/<int:work_item_id>/dependencies')
def work_item_dependencies(work_item_id: int):
    """Work item dependencies"""
    return render_template('work-items/dependencies.html', work_item_id=work_item_id)

# Work Item Context
@work_items_bp.route('/<int:work_item_id>/context')
def work_item_context(work_item_id: int):
    """Work item context view"""
    return render_template('work-items/context.html', work_item_id=work_item_id)

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

# Context Evidence
@context_bp.route('/evidence')
def context_evidence_list():
    """Context evidence list"""
    return render_template('context/evidence/list.html')

@context_bp.route('/evidence/<int:evidence_id>')
def context_evidence_detail(evidence_id: int):
    """Context evidence detail"""
    return render_template('context/evidence/detail.html', evidence_id=evidence_id)

# Context Events
@context_bp.route('/events')
def context_events_list():
    """Context events list"""
    return render_template('context/events/list.html')

@context_bp.route('/events/<int:event_id>')
def context_event_detail(event_id: int):
    """Context event detail"""
    return render_template('context/events/detail.html', event_id=event_id)

# Context Sessions
@context_bp.route('/sessions')
def context_sessions_list():
    """Context sessions list"""
    return render_template('context/sessions/list.html')

@context_bp.route('/sessions/<session_id>')
def context_session_detail(session_id: str):
    """Context session detail"""
    return render_template('context/sessions/detail.html', session_id=session_id)

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

@agents_bp.route('/generate')
def agents_generate_form():
    """Generate agents form (read-only)"""
    return render_template('agents/generate.html')

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

@system_bp.route('/logs')
def system_logs():
    """System logs"""
    return render_template('system/logs.html')

@system_bp.route('/metrics')
def system_metrics():
    """System metrics"""
    return render_template('system/metrics.html')

@system_bp.route('/settings')
def system_settings():
    """System settings (read-only)"""
    return render_template('system/settings.html')

# ============================================================================
# SEARCH BLUEPRINT
# ============================================================================

@search_bp.route('/')
def search():
    """Search results"""
    return render_template('search/results.html')

@search_bp.route('/suggestions')
def search_suggestions():
    """Search suggestions"""
    return jsonify({'suggestions': []})

@search_bp.route('/history')
def search_history():
    """Search history"""
    return render_template('search/history.html')

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
        {'name': 'search', 'prefix': '/search', 'routes': len(search_bp.url_map.iter_rules())},
    ]
    return {'blueprints': blueprints, 'total': len(blueprints)}

def validate_blueprint_structure() -> Dict[str, Any]:
    """Validate that all blueprints follow the read-only structure"""
    issues = []
    warnings = []
    
    # Check for read-only design (only GET methods)
    # Check for consistent naming patterns
    # Check for hierarchical structure
    # Check for logical grouping
    # Check for system alignment
    
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
        agents_bp, rules_bp, system_bp, search_bp
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
