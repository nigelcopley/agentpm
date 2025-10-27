"""
Rules Actions Module for APM (Agent Project Manager) Web Application

Handles all CRUD operations and actions for rules including:
- Create, Read, Update, Delete operations
- Rule validation and enforcement
- Rule status management
"""

import logging
from datetime import datetime
from typing import Optional

from flask import request, jsonify, flash, redirect, url_for

from ....core.database.methods import rules
from ....core.database.models import Rule
from ....core.database.enums import EnforcementLevel
from ..utils import (
    get_database_service, 
    validate_required_fields, 
    handle_error, 
    create_success_response, 
    create_error_response, 
    safe_get_entity
)

logger = logging.getLogger(__name__)

def create_rule():
    """Create a new rule."""
    try:
        db = get_database_service()
        
        # Validate required fields
        required_fields = {
            'name': 'Rule name is required',
            'rule_id': 'Rule ID is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('rules.rules_list'))
        
        # Get form data
        name = request.form.get('name', '').strip()
        rule_id = request.form.get('rule_id', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        enforcement_level = request.form.get('enforcement_level', 'GUIDE')
        project_id = int(request.form.get('project_id', 1))
        enabled = request.form.get('enabled') == 'on'
        
        # Create rule
        rule = Rule(
            name=name,
            rule_id=rule_id,
            description=description if description else None,
            category=category if category else None,
            enforcement_level=EnforcementLevel(enforcement_level),
            project_id=project_id,
            enabled=enabled
        )
        
        created_rule = rules.create_rule(db, rule)
        
        flash(f'Rule "{created_rule.name}" created successfully', 'success')
        return redirect(url_for('rules.rule_detail', rule_id=created_rule.id))
        
    except Exception as e:
        return handle_error(e, 'Error creating rule', url_for('rules.rules_list'))

def update_rule(rule_id: int):
    """Update an existing rule"""
    try:
        db = get_database_service()
        from ....core.database.methods import rules
        from ....core.database.enums import EnforcementLevel
        
        rule = safe_get_entity(rules.get_rule, db, rule_id, "Rule")
        if not rule:
            flash('Rule not found', 'error')
            return redirect(url_for('rules.rules_list'))
        
        # Validate required fields
        required_fields = {
            'name': 'Rule name is required',
            'rule_id': 'Rule ID is required'
        }
        
        error_message = validate_required_fields(required_fields, request.form)
        if error_message:
            flash(error_message, 'error')
            return redirect(url_for('rules.edit_rule', rule_id=rule_id))
        
        # Get form data
        name = request.form.get('name', '').strip()
        rule_id_str = request.form.get('rule_id', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        enforcement_level = request.form.get('enforcement_level', 'GUIDE')
        project_id = int(request.form.get('project_id', 1))
        enabled = request.form.get('enabled') == 'on'
        
        # Update rule using the correct method signature
        updated_rule = rules.update_rule(db, rule_id,
                                        name=name,
                                        rule_id=rule_id_str,
                                        description=description if description else None,
                                        category=category if category else None,
                                        enforcement_level=EnforcementLevel(enforcement_level),
                                        project_id=project_id,
                                        enabled=enabled)
        
        flash(f'Rule "{updated_rule.name}" updated successfully', 'success')
        return redirect(url_for('rules.rule_detail', rule_id=rule_id))
        
    except Exception as e:
        return handle_error(e, 'Error updating rule', url_for('rules.edit_rule', rule_id=rule_id))

def delete_rule(rule_id: int):
    """Delete a rule"""
    try:
        db = get_database_service()
        from ....core.database.methods import rules
        
        rule = safe_get_entity(rules.get_rule, db, rule_id, "Rule")
        if not rule:
            flash('Rule not found', 'error')
            return redirect(url_for('rules.rules_list'))
        
        rule_name = rule.name
        rules.delete_rule(db, rule_id)
        
        flash(f'Rule "{rule_name}" deleted successfully', 'success')
        return redirect(url_for('rules.rules_list'))
        
    except Exception as e:
        return handle_error(e, 'Error deleting rule', url_for('rules.rule_detail', rule_id=rule_id))
