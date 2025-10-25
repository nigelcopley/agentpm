"""
Hierarchical Summary Commands

Commands for managing polymorphic summaries across all entity types:
- Project summaries (strategic, milestone, retrospective)
- Session summaries (handover, progress, error analysis)
- Work item summaries (progress, milestone, decision)
- Task summaries (completion, progress, blocker resolution)
"""

import click

from .create import create_summary
from .list import list_summaries
from .show import show_summary
from .search import search_summaries
from .delete import delete_summary
from .stats import summary_stats
from .types import types


@click.group()
def summary():
    """Manage hierarchical summaries for projects, work items, tasks, and sessions."""
    pass


summary.add_command(create_summary, name='create')
summary.add_command(list_summaries, name='list')
summary.add_command(show_summary, name='show')
summary.add_command(search_summaries, name='search')
summary.add_command(delete_summary, name='delete')
summary.add_command(summary_stats, name='stats')
summary.add_command(types)

__all__ = [
    'summary',
    'create_summary',
    'list_summaries', 
    'show_summary',
    'search_summaries',
    'delete_summary',
    'summary_stats'
]
