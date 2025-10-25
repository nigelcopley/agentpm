"""
APM (Agent Project Manager) Web Blueprints

Modular blueprint structure for the APM (Agent Project Manager) web application.
Each blueprint handles a specific domain of functionality.
"""

# Import individual blueprints
from .dashboard import dashboard_bp
from .ideas import ideas_bp
from .idea_elements import idea_elements_bp
from .work_items import work_items_bp
from .tasks import tasks_bp
from .context import context_bp
from .documents import documents_bp
from .agents import agents_bp
from .rules import rules_bp
from .system import system_bp
from .search import search_bp

__all__ = [
    'dashboard_bp',
    'ideas_bp',
    'idea_elements_bp',
    'work_items_bp',
    'tasks_bp',
    'context_bp',
    'documents_bp',
    'agents_bp',
    'rules_bp',
    'system_bp',
    'search_bp'
]