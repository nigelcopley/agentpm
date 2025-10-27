"""
System Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for system administration functionality.
Each module handles specific aspects of system management.
"""

from flask import Blueprint
import logging

# Create system blueprint
system_bp = Blueprint('system', __name__, url_prefix='/system')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service

# Import route modules
from . import health, database
