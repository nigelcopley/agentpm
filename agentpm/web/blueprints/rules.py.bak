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
    # Create mock data for rules
    rules_data = {
        'total_rules': 0,
        'active_count': 0,
        'quality_gates_count': 0,
        'blocking_count': 0,
        'rules': []
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
