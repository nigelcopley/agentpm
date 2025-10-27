"""
Search Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for search functionality.
Each module handles specific aspects of search.
"""

from flask import Blueprint
import logging

# Create search blueprint
search_bp = Blueprint('search', __name__, url_prefix='/search')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service

# Import route modules
from . import search
