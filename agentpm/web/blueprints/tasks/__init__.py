"""
Tasks Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for tasks management functionality.
Each module handles specific aspects of task management.
"""

from flask import Blueprint
import logging

# Create tasks blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service, _is_htmx_request

# Import route modules
from . import list, detail, actions

