"""
Work Items Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for work items management functionality.
Each module handles specific aspects of work item management.
"""

from flask import Blueprint
import logging

# Create work items blueprint
work_items_bp = Blueprint('work_items', __name__, url_prefix='/work-items')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service, _is_htmx_request

# Import route modules
from . import list, detail, actions
