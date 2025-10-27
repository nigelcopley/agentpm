"""
Rules Detail Module for APM (Agent Project Manager) Web Application

Handles all detail-related functionality for rules including:
- Individual rule detail views with comprehensive context
- Rule logic and conditions
- Validation results and usage statistics
- Related rules and dependencies
- Rule history and changes
"""

from flask import render_template, abort
import logging

from . import rules_bp
from ..utils import get_database_service, safe_get_entity

logger = logging.getLogger(__name__)

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
    - Enforcement details
    """
    # Fetch rule data
    db = get_database_service()
    from ....core.database.methods import rules as rules_methods
    
    rule = safe_get_entity(rules_methods.get_rule, db, rule_id, "Rule")
    
    if not rule:
        abort(404, description=f"Rule {rule_id} not found")
    
    # Get all rules for related rules analysis
    all_rules = rules_methods.list_rules(db) or []
    
    # Find related rules (same category or similar enforcement level)
    related_rules = []
    try:
        for other_rule in all_rules:
            if other_rule.id != rule_id:
                # Check if same category
                if rule.category and other_rule.category and rule.category == other_rule.category:
                    related_rules.append(other_rule)
                # Check if same enforcement level
                elif rule.enforcement_level and other_rule.enforcement_level and rule.enforcement_level == other_rule.enforcement_level:
                    related_rules.append(other_rule)
    except Exception as e:
        logger.warning(f"Error finding related rules: {e}")
    
    # Calculate rule statistics
    rule_stats = {
        'is_active': rule.enabled,
        'is_blocking': rule.enabled and rule.enforcement_level and rule.enforcement_level.value == 'BLOCK',
        'is_limiting': rule.enabled and rule.enforcement_level and rule.enforcement_level.value == 'LIMIT',
        'is_guiding': rule.enabled and rule.enforcement_level and rule.enforcement_level.value == 'GUIDE',
        'has_category': bool(rule.category),
        'has_description': bool(rule.description),
        'has_conditions': bool(getattr(rule, 'conditions', None)),
        'related_rules_count': len(related_rules),
    }
    
    # Get rule logic details
    rule_logic = {}
    if hasattr(rule, 'conditions') and rule.conditions:
        try:
            import json
            if isinstance(rule.conditions, str):
                rule_logic = json.loads(rule.conditions)
            else:
                rule_logic = rule.conditions
        except Exception as e:
            logger.warning(f"Error parsing rule conditions: {e}")
            rule_logic = {'raw': str(rule.conditions)}
    
    # Get enforcement details
    enforcement_details = {
        'level': rule.enforcement_level.value if rule.enforcement_level else 'unknown',
        'enabled': rule.enabled,
        'severity': getattr(rule, 'severity', 'medium'),
        'category': rule.category or 'uncategorized',
        'description': rule.description or 'No description available'
    }
    
    # Get usage statistics (placeholder - would need to be implemented)
    usage_stats = {
        'times_triggered': 0,  # Would need to track this
        'last_triggered': None,  # Would need to track this
        'success_rate': 100,  # Would need to track this
        'affected_entities': 0  # Would need to track this
    }
    
    return render_template('rules/detail.html', 
                         rule=rule, 
                         rule_id=rule_id,
                         related_rules=related_rules,
                         rule_stats=rule_stats,
                         rule_logic=rule_logic,
                         enforcement_details=enforcement_details,
                         usage_stats=usage_stats)
