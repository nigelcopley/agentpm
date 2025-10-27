"""
Documents Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for documents management functionality.
Each module handles specific aspects of document management.
"""

from flask import Blueprint
import logging

# Create documents blueprint
documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service, _is_htmx_request

# Import route modules
from . import list, detail, api
from . import actions
