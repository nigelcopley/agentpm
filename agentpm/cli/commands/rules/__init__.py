"""
Rules CLI command group.

Provides commands for managing project rules:
- apm rules list: List all active rules
- apm rules show <rule-id>: Display rule details
- apm rules configure: Re-run questionnaire
"""

import click


@click.group()
def rules():
    """Manage project rules and configuration."""
    pass


# Import and register subcommands
from . import list, show, configure, create

rules.add_command(list.list_rules, name='list')
rules.add_command(show.show_rule, name='show')
rules.add_command(configure.configure_rules, name='configure')
rules.add_command(create.create_rule, name='create')
