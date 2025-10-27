"""
Ideas Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for ideas management functionality.
Each module handles specific aspects of idea management.
"""

from flask import Blueprint
import logging

# Create ideas blueprint
ideas_bp = Blueprint('ideas', __name__, url_prefix='/ideas')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service, _is_htmx_request

# Import route modules
from . import list, detail, actions
