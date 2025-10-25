"""
apm session - Session management commands

Commands for managing development sessions, including starting, ending,
tracking progress, and maintaining session continuity.
"""

import click
from agentpm.cli.commands.session.start import start
from agentpm.cli.commands.session.end import end
from agentpm.cli.commands.session.show import show
from agentpm.cli.commands.session.status import status
from agentpm.cli.commands.session.history import history
from agentpm.cli.commands.session.update import update
from agentpm.cli.commands.session.add_decision import add_decision
from agentpm.cli.commands.session.add_next_step import add_next_step


@click.group()
def session():
    """
    Session management commands.
    
    Manage development sessions to maintain context and continuity
    across coding sessions. Sessions help track progress, decisions,
    and next steps for effective handovers.
    
    \b
    Examples:
      apm session start                    # Start new session
      apm session show                     # Show current session
      apm session end                      # End current session
      apm session history                  # List past sessions
    """
    pass


# Add all subcommands
session.add_command(start)
session.add_command(end)
session.add_command(show)
session.add_command(status)
session.add_command(history)
session.add_command(update)
session.add_command(add_decision)
session.add_command(add_next_step)
