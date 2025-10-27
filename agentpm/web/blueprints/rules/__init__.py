"""
Rules Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for rules management functionality.
Each module handles specific aspects of rules management.
"""

from flask import Blueprint
import logging

# Create rules blueprint
rules_bp = Blueprint('rules', __name__, url_prefix='/rules')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service

# Import route modules
from . import list, detail, actions
