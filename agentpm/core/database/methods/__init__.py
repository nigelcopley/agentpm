"""
Database CRUD Methods

Type-safe CRUD operations for all entity types.

Each method module follows the pattern:
- Accepts Pydantic models as input
- Returns Pydantic models as output
- Uses adapters for model � database conversion
- Validates dependencies before creation

Usage:
    from agentpm.core.database.methods import projects, work_items, tasks

    project = projects.create_project(service, Project(name="AIPM", path="/path"))
    work_item = work_items.create_work_item(service, WorkItem(...))
"""

from . import projects
from . import work_items
from . import tasks
from . import ideas
from . import idea_elements
from . import agents
from . import rules
from . import contexts
from . import sessions
from . import dependencies
from . import evidence_sources
from . import events
from . import document_references
from . import summaries
from . import provider_methods

__all__ = [
    "projects",
    "work_items",
    "tasks",
    "ideas",
    "idea_elements",
    "agents",
    "rules",
    "contexts",
    "sessions",
    "dependencies",
    "evidence_sources",
    "events",
    "document_references",
    "summaries",
    # Provider methods
    "provider_methods",
]