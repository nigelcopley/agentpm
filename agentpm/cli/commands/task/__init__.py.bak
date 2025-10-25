"""
task command group

Modular structure for task management commands.
Each subcommand in its own file for maintainability.

Commands:
- create: Create new task with time-box validation
- list: List tasks with filters
- show: Display task details
- start: Transition task to in_progress
- complete: Mark task as completed

Note: Dependency commands are imported separately from dependencies/ group
"""

import click

# Import all subcommands
from .create import create
from .list import list_tasks as list
from .show import show
from .validate import validate
from .accept import accept
from .start import start
from .submit_review import submit_review
from .approve import approve
from .request_changes import request_changes
from .complete import complete
from .update import update
from .next import next
from .types import types


@click.group()
def task():
    """
    Manage tasks with quality gates.

    Tasks are the atomic unit of work with strict time-boxing and
    quality metadata requirements enforced by the workflow system.

    \b
    Task Types & Time Limits:
      implementation - Code changes (≤4h STRICT)
      testing        - Test coverage (≤6h)
      design         - Architecture/design (≤8h)
      documentation  - Docs/guides (≤4h)
      bugfix         - Bug fixes (≤4h)

    \b
    Examples:
      apm task create "Add auth model" --work-item-id=1 --type=implementation --effort=3
      apm task list --work-item-id=1
      apm task start 5
    """
    pass


# Register subcommands
task.add_command(create)
task.add_command(list)
task.add_command(show)
task.add_command(validate)
task.add_command(accept)
task.add_command(start)
task.add_command(submit_review)
task.add_command(approve)
task.add_command(request_changes)
task.add_command(complete)
task.add_command(update)
task.add_command(next)
task.add_command(types)

# Import and add dependency management commands
from agentpm.cli.commands.dependencies import (
    add_dependency,
    add_blocker,
    list_dependencies,
    list_blockers,
    resolve_blocker
)

# Register dependency commands under task group
task.add_command(add_dependency)
task.add_command(add_blocker)
task.add_command(list_dependencies)
task.add_command(list_blockers)
task.add_command(resolve_blocker)
