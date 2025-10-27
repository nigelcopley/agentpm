"""
Context Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for context management functionality.
Each module handles specific aspects of context management.
"""

from flask import Blueprint
import logging

# Create context blueprint
context_bp = Blueprint('context', __name__, url_prefix='/context')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service, _is_htmx_request

# Import route modules
from . import list, detail, files, evidence, events, sessions, actions
