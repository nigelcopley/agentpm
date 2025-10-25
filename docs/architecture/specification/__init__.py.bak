"""
session command group

Session management commands for tracking development sessions,
querying history, and analyzing productivity metrics.

Commands:
- status: Show current active session
- start: Start a new development session (manual)
- end: End the current session (manual)
- show: Display session details
- add-decision: Add decision to current session
- history: View session history and analytics
"""

import click

# Import all subcommands
from .status import status
from .update import update
from .add_next_step import add_next_step
from .add_decision import add_decision
from .show import show
from .history import history
from .start import start
from .end import end


@click.group(name='session')
def session():
    """
    Manage development sessions and history.

    Sessions are automatically tracked via hooks (SessionStart/SessionEnd).
    Use these commands to view, update, and query session data.

    \b
    Session Commands:
      status           - Show current active session with activity summary
      update           - Update session summary and priority
      add-decision     - Add key decision to current session
      add-next-step    - Add action item for next session
      show             - Display session details (current or specific)
      history          - View session history with filters
      start            - Manually start session (hooks do this automatically)
      end              - Manually end session (hooks do this automatically)

    \b
    Examples:
      apm session status                             # Current session
      apm session update --summary "..."             # Add summary
      apm session add-decision "Use Pydantic"        # Record decision
      apm session add-next-step "Integrate hooks"    # Next action
      apm session show                               # Current session details
      apm session show abc-123                       # Specific session
      apm session history --days 7                   # Last week
      apm session history --work-item 35             # Sessions on WI-35
      apm session history --search "pydantic"        # Search decisions
    """
    pass


# Register subcommands
session.add_command(status)
session.add_command(update)
session.add_command(add_decision)
session.add_command(add_next_step)
session.add_command(show)
session.add_command(history)
session.add_command(start)  # Manual override
session.add_command(end)    # Manual override
