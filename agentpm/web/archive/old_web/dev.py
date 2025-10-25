"""
Development Blueprint - Development and Testing Routes (Dev Only)

Handles:
- /dev/test-toasts - Test toast notifications
- /dev/test-toast/<type> - Test specific toast type
- /dev/test/interactions - Test interactions
"""

from flask import Blueprint, render_template, request, make_response

# Import helper functions from app
from ..app import add_toast, toast_response

dev_bp = Blueprint('dev', __name__)


@dev_bp.route('/dev/test-toasts')
def test_toasts():
    """Test toast notifications."""
    return render_template('dev/test_toasts.html')


@dev_bp.route('/dev/test-toast/<toast_type>')
def test_toast(toast_type: str):
    """Test specific toast type."""
    valid_types = ['success', 'error', 'warning', 'info']
    
    if toast_type not in valid_types:
        return toast_response(f'Invalid toast type: {toast_type}', 'error'), 400
    
    message = f'This is a {toast_type} toast notification'
    return toast_response(message, toast_type)


@dev_bp.route('/dev/test/interactions')
def test_interactions():
    """Test interactions page."""
    return render_template('dev/test_interactions.html')
