"""
Rules List Module for APM (Agent Project Manager) Web Application

Handles all list-related functionality for rules including:
- Rules listing with comprehensive metrics
- Rule categories and enforcement levels
- Quality gates and governance metrics
"""

from flask import render_template
import logging

from . import rules_bp
from ..utils import get_database_service

logger = logging.getLogger(__name__)

@rules_bp.route('/')
def rules_list():
    """Rules list view with comprehensive metrics and governance information"""
    db = get_database_service()
    from ....core.database.methods import rules as rules_methods
    
    rules_list = rules_methods.list_rules(db) or []
    
    # Calculate comprehensive metrics
    active_count = len([r for r in rules_list if r.enabled])
    inactive_count = len([r for r in rules_list if not r.enabled])
    blocking_count = len([r for r in rules_list if r.enabled and r.enforcement_level.value == 'BLOCK'])
    limiting_count = len([r for r in rules_list if r.enabled and r.enforcement_level.value == 'LIMIT'])
    guiding_count = len([r for r in rules_list if r.enabled and r.enforcement_level.value == 'GUIDE'])
    
    # Calculate category distribution
    category_stats = {}
    for rule in rules_list:
        category = rule.category or 'uncategorized'
        category_stats[category] = category_stats.get(category, 0) + 1
    
    # Calculate enforcement level distribution
    enforcement_stats = {}
    for rule in rules_list:
        if rule.enabled:
            level = rule.enforcement_level.value if rule.enforcement_level else 'unknown'
            enforcement_stats[level] = enforcement_stats.get(level, 0) + 1
    
    # Quality gates and governance metrics
    quality_gates_count = len([r for r in rules_list if r.category and 'quality' in r.category.lower()])
    governance_count = len([r for r in rules_list if r.category and 'governance' in r.category.lower()])
    security_count = len([r for r in rules_list if r.category and 'security' in r.category.lower()])
    performance_count = len([r for r in rules_list if r.category and 'performance' in r.category.lower()])
    
    # Create comprehensive rules data
    rules_data = {
        'rules': rules_list,
        'total_rules': len(rules_list),
        'active_count': active_count,
        'inactive_count': inactive_count,
        'blocking_count': blocking_count,
        'limiting_count': limiting_count,
        'guiding_count': guiding_count,
        'category_stats': category_stats,
        'enforcement_stats': enforcement_stats,
        'quality_gates_count': quality_gates_count,
        'governance_count': governance_count,
        'security_count': security_count,
        'performance_count': performance_count,
        'metrics': {
            'total_rules': len(rules_list),
            'active_rules': active_count,
            'inactive_rules': inactive_count,
            'blocking_rules': blocking_count,
            'limiting_rules': limiting_count,
            'guiding_rules': guiding_count,
            'quality_gates': quality_gates_count,
            'governance_rules': governance_count,
            'security_rules': security_count,
            'performance_rules': performance_count,
            'most_common_category': max(category_stats.items(), key=lambda x: x[1])[0] if category_stats else None,
            'most_common_enforcement': max(enforcement_stats.items(), key=lambda x: x[1])[0] if enforcement_stats else None,
            'enforcement_distribution': {
                'block': blocking_count,
                'limit': limiting_count,
                'guide': guiding_count
            }
        }
    }
    
    return render_template('rules/list.html', rules=rules_data)
