"""
Agents Blueprint Module for APM (Agent Project Manager) Web Application

Modular blueprint structure for agents management functionality.
Each module handles specific aspects of agent management.
"""

from flask import Blueprint
import logging

# Create agents blueprint
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

logger = logging.getLogger(__name__)

# Import shared utilities
from ..utils import get_database_service

# Import route modules
from . import list, detail, actions
