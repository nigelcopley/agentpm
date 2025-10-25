"""
context command group

Modular structure for context management commands.
Each subcommand in its own file for maintainability.

Commands:
- show: Display hierarchical context with confidence scoring
- refresh: Regenerate context (trigger plugin detection)
- status: Show context freshness and quality metrics
"""

import click

# Import all subcommands
from .show import show
from .refresh import refresh
from .status import status
from .rich import rich
from .wizard import wizard


@click.group()
def context():
    """
    Access hierarchical project context.

    Context flows from Project → Work Item → Task, providing AI agents
    with governance, business logic, and implementation details.

    \b
    Context Hierarchy:
      Project    - Governance, tech stack, standards
      Work Item  - Business requirements, acceptance criteria
      Task       - Implementation details, code files, patterns

    \b
    Examples:
      apm context show --task-id=5
      apm context show --work-item-id=1
      apm context show --project
      apm context refresh --task-id=5
    """
    pass


# Register subcommands
context.add_command(show)
context.add_command(refresh)
context.add_command(status)
context.add_command(rich)
context.add_command(wizard)
