"""
Rules Blueprint for APM (Agent Project Manager) Web Application

Rules management functionality.
"""

from flask import Blueprint, render_template, redirect, url_for
import logging

# Create rules blueprint
rules_bp = Blueprint('rules', __name__, url_prefix='/rules')

logger = logging.getLogger(__name__)

@rules_bp.route('/')
def rules_list():
    """Rules list view"""
    from ...core.database.service import DatabaseService
    from ...core.database.methods import rules as rules_methods
    
    db = DatabaseService('.agentpm/data/agentpm.db')
    rules_list = rules_methods.list_rules(db) or []
    
    # Calculate metrics
    active_count = len([r for r in rules_list if r.enabled])
    blocking_count = len([r for r in rules_list if r.enabled and r.enforcement_level.value == 'BLOCK'])
    quality_gates_count = len([r for r in rules_list if r.category and 'quality' in r.category.lower()])
    
    # Create rules object with metrics
    rules_data = {
        'rules': rules_list,
        'total_rules': len(rules_list),
        'active_count': active_count,
        'quality_gates_count': quality_gates_count,
        'blocking_count': blocking_count
    }
    
    return render_template('rules/list.html', rules=rules_data)

@rules_bp.route('/<int:rule_id>')
def rule_detail(rule_id: int):
    """
    Comprehensive rule detail view.
    
    Shows all rule information in a single view:
    - Basic information (name, description, category, severity)
    - Rule logic and conditions
    - Validation results
    - Usage statistics
    - Related rules
    - History and changes
    """
    # For now, redirect to rules list until we create the detail template
    return redirect(url_for('rules.rules_list'))
