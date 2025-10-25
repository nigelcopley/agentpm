"""
dependencies command group

Modular structure for task dependency and blocker management.
Each subcommand in its own file for maintainability.

Commands:
- add-dependency: Add hard/soft dependency between tasks
- add-blocker: Add task or external blocker
- list-dependencies: Show task dependencies (prerequisites and dependents)
- list-blockers: Show task blockers (with resolution status)
- resolve-blocker: Mark blocker as resolved

Note: These commands are registered under the 'task' group for better UX
      (apm task add-dependency vs apm dependencies add-dependency)
"""

# Import all subcommands
from .add_dependency import add_dependency
from .add_blocker import add_blocker
from .list_dependencies import list_dependencies
from .list_blockers import list_blockers
from .resolve_blocker import resolve_blocker

# Export for registration in task group
__all__ = [
    'add_dependency',
    'add_blocker',
    'list_dependencies',
    'list_blockers',
    'resolve_blocker'
]
