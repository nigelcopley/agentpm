"""
Rules Blueprint - Rules Management and Operations

Handles:
- /rules - List all rules
- /rules/<id> - Get rule details
- /rules/<id>/edit - Edit rule form
- /rules/<id>/actions/toggle - Toggle rule enforcement
"""

from flask import Blueprint, render_template, abort, request, make_response, redirect, url_for

from ...core.database.methods import rules as rule_methods
from ...core.database.enums import EnforcementLevel

# Import helper functions and models from app
from ..app import (
    get_database_service,
    add_toast,
    toast_response,
    redirect_with_toast,
    RuleInfo
)

# Import WebSocket broadcasting
from ..websocket import broadcast_rule_toggle

rules_bp = Blueprint('rules', __name__)


def _is_htmx_request() -> bool:
    """Return True when request originates from HTMX."""
    return request.headers.get('HX-Request') == 'true'


@rules_bp.route('/rules')
def rules_list():
    """List all rules."""
    db = get_database_service()

    # Use database methods instead of raw SQL
    all_rules = rule_methods.list_rules(db)

    rules_info = [
        RuleInfo(
            rule=rule,
            is_active=rule.enabled
        )
        for rule in all_rules
    ]

    return render_template('rules_list.html', rules=rules_info)


@rules_bp.route('/rules/<int:rule_id>')
def rule_detail(rule_id: int):
    """Get rule details."""
    db = get_database_service()
    
    rule = rule_methods.get_rule(db, rule_id)
    if not rule:
        abort(404, description=f"Rule {rule_id} not found")
    
    return render_template('rules/detail.html', rule=rule)


@rules_bp.route('/rules/<int:rule_id>/edit')
def rule_edit(rule_id: int):
    """Edit rule form."""
    db = get_database_service()
    rule = rule_methods.get_rule(db, rule_id)
    
    if not rule:
        abort(404, description=f"Rule {rule_id} not found")
    
    return render_template('rules/edit.html', rule=rule)


@rules_bp.route('/rules/<int:rule_id>/actions/toggle', methods=['POST', 'GET'])
def rules_toggle(rule_id: int):
    """Toggle rule enforcement between BLOCK (enabled) and GUIDE (disabled)."""
    if request.method == 'GET':
        abort(404, description=f"Rule {rule_id} not found")

    db = get_database_service()

    # Get rule
    rule = rule_methods.get_rule(db, rule_id)
    if not rule:
        if _is_htmx_request():
            return toast_response('Rule not found', 'error'), 404
        return redirect_with_toast(
            url_for('rules.rules_list'),
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

    # Broadcast WebSocket event for real-time updates
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
        url_for('rules.rules_list'),
        f'Rule {rule.rule_id} {"enabled" if new_level == EnforcementLevel.BLOCK else "disabled"}',
        'success'
    )
