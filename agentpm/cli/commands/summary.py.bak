"""
Summary Command Group

Hierarchical summary management for all entity types.
"""

import click
from rich.console import Console

from .summary.create import create_summary
from .summary.list import list_summaries
from .summary.show import show_summary
from .summary.search import search_summaries
from .summary.delete import delete_summary
from .summary.stats import summary_stats


@click.group()
@click.pass_context
def summary(ctx: click.Context):
    """
    📝 Hierarchical Summary Management
    
    Manage summaries across all entity types in the APM (Agent Project Manager) hierarchy:
    - Project summaries (strategic, milestone, retrospective)
    - Session summaries (handover, progress, error analysis)
    - Work item summaries (progress, milestone, decision)
    - Task summaries (completion, progress, blocker resolution)
    
    \b
    Common Commands:
      create    Create a new summary for any entity type
      list      List summaries with filtering options
      show      Display detailed summary information
      search    Search summaries by text content
      delete    Delete summaries with confirmation
      stats     Show summary statistics and analytics
    
    \b
    Examples:
      apm summary create --entity-type work-item --entity-id 42 \\
          --summary-type work-item-progress --text "Progress update..."
      
      apm summary list --entity-type project --limit 10
      
      apm summary search "database schema" --entity-type work-item
      
      apm summary stats --format table
    """
    pass


# Add subcommands
summary.add_command(create_summary, name='create')
summary.add_command(list_summaries, name='list')
summary.add_command(show_summary, name='show')
summary.add_command(search_summaries, name='search')
summary.add_command(delete_summary, name='delete')
summary.add_command(summary_stats, name='stats')
