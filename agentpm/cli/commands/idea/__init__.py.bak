"""
idea command group

Modular structure for idea management commands.
Each subcommand in its own file for maintainability.

Commands:
- create: Create new idea
- list: List ideas with filters
- show: Display idea details
- vote: Vote on ideas (+1/-1)
- update: Update idea details
- transition: Move idea through workflow
- reject: Reject idea with reason
- convert: Convert idea to work item
"""

import click

# Import all subcommands
from .create import create
from .list import list_ideas as list
from .show import show
from .vote import vote
from .update import update
from .transition import transition
from .reject import reject
from .convert import convert
from .context import context
from .next import next
from .elements import elements


@click.group(name='idea')
def idea():
    """
    Manage ideas (lightweight brainstorming before work items).

    Ideas support a simple 6-state lifecycle for low-friction capture
    of concepts that can be voted on, refined, and converted to work items.

    \b
    Idea Lifecycle:
      idea → research → design → accepted → converted (terminal)
      any state → rejected (terminal)

    \b
    Benefits:
      • Low-friction capture before formal work items
      • Democratic voting for prioritization
      • Research/design phases for validation
      • Full traceability to work items

    \b
    Examples:
      apm idea create "Add OAuth2 authentication"
      apm idea list --status=accepted
      apm idea vote 5 --upvote
      apm idea convert 5 --type=feature
    """
    pass


# Register subcommands
idea.add_command(create)
idea.add_command(list)
idea.add_command(show)
idea.add_command(vote)
idea.add_command(update)
idea.add_command(transition)
idea.add_command(reject)
idea.add_command(convert)
idea.add_command(context)
idea.add_command(next)
idea.add_command(elements)
