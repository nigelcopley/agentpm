"""
work-item command group

Modular structure for work item management commands.
Each subcommand in its own file for maintainability.

Commands:
- create: Create new work item
- list: List work items with filters
- show: Display work item details
"""

import click

# Import all subcommands
from .create import create
from .list import list_work_items as list
from .show import show
from .validate import validate
from .accept import accept
from .update import update
from .delete import delete
from .bulk import bulk
from .start import start
from .submit_review import submit_review
from .approve import approve
from .request_changes import request_changes
from .summaries import add_summary, show_history
from .next import next
from .types import types

# Import phase commands (NEW)
from .phase_status import phase_status
from .phase_validate import phase_validate

# Import work item dependency commands
from agentpm.cli.commands.work_item_dependencies import (
    add_dependency,
    list_dependencies,
    remove_dependency
)


@click.group(name='work-item')
def work_item():
    """
    Manage work items (features, bugs, research).

    Work items are the primary organizational unit for delivering value.
    Each work item type has specific quality gates and required task types.

    \b
    Work Item Types:
      feature     - New functionality (requires DESIGN+IMPL+TEST+DOC)
      bugfix      - Bug fixes (requires ANALYSIS+BUGFIX+TESTING)
      research    - Investigation (requires ANALYSIS+DOCUMENTATION)
      planning    - Planning (forbids IMPLEMENTATION)
      refactoring - Code improvement (requires ANALYSIS+REFACTORING+TESTING)
      infrastructure - DevOps (requires DESIGN+DEPLOYMENT+TESTING+DOC)
      enhancement - Improvements (requires IMPLEMENTATION+TESTING)

    \b
    Examples:
      apm work-item create "User Authentication" --type=feature
      apm work-item list --type=feature --status=in_progress
      apm work-item show 123
    """
    pass


# Register subcommands
work_item.add_command(create)
work_item.add_command(list)
work_item.add_command(show)
work_item.add_command(validate)
work_item.add_command(accept)
work_item.add_command(start)
work_item.add_command(submit_review)
work_item.add_command(approve)
work_item.add_command(request_changes)
work_item.add_command(update)
work_item.add_command(delete)
work_item.add_command(bulk)
work_item.add_command(add_summary)
work_item.add_command(show_history)
work_item.add_command(next)
work_item.add_command(types)

# Register phase commands (NEW)
work_item.add_command(phase_status)
work_item.add_command(phase_validate)

# Register work item dependency commands
work_item.add_command(add_dependency)
work_item.add_command(list_dependencies)
work_item.add_command(remove_dependency)
