"""
work-item-dependencies command group

Modular structure for work item dependency management.
Each subcommand in its own file for maintainability.

Commands:
- add-dependency: Add hard/soft dependency between work items
- list-dependencies: Show work item dependencies (prerequisites and dependents)
- remove-dependency: Remove work item dependency

Note: These commands are registered under the 'work-item' group for better UX
      (apm work-item add-dependency vs apm work-item-dependencies add-dependency)
"""

# Import all subcommands
from .add_dependency import add_dependency
from .list_dependencies import list_dependencies
from .remove_dependency import remove_dependency

# Export for registration in work-item group
__all__ = [
    'add_dependency',
    'list_dependencies',
    'remove_dependency'
]
