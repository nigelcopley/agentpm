"""
apm work-item list - List work items command
"""

import click
import json
from rich.table import Table
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import get_work_item_type_choices


@click.command(name='list')
@click.option(
    '--type', 'wi_type',
    type=click.Choice(get_work_item_type_choices(), case_sensitive=False),
    help='Filter by work item type'
)
@click.option(
    '--status',
    type=click.Choice(WorkItemStatus.choices(), case_sensitive=False),
    help='Filter by status'
)
@click.option(
    '--search', '-s',
    help='Search in work item names and descriptions (case-insensitive)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_work_items(ctx: click.Context, wi_type: str, status: str, search: str, format: str):
    """
    List work items with optional filters.

    \b
    Examples:
      apm work-item list                      # All work items
      apm work-item list --type=feature       # Features only
      apm work-item list --status=in_progress # Active work
      apm work-item list --search "oauth"     # Search in names/descriptions
      apm work-item list --format=json        # JSON output
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # THREE-LAYER PATTERN: Use adapter, not direct methods call
    work_items = WorkItemAdapter.list(db, project_id=project_id)

    # Apply filters
    if wi_type:
        work_items = [wi for wi in work_items if wi.type.value == wi_type]
    if status:
        work_items = [wi for wi in work_items if wi.status.value == status]
    if search:
        search_lower = search.lower()
        work_items = [
            wi for wi in work_items 
            if search_lower in wi.name.lower() or 
               (wi.description and search_lower in wi.description.lower())
        ]

    if not work_items:
        console.print("\nℹ️  [yellow]No work items found[/yellow]\n")
        console.print("💡 [cyan]Create one with:[/cyan]")
        console.print("   apm work-item create \"My Feature\" --type=feature\n")
        return

    if format == 'json':
        output = [
            {
                'id': wi.id,
                'name': wi.name,
                'type': wi.type.value,
                'status': wi.status.value,
                'priority': wi.priority
            }
            for wi in work_items
        ]
        console.print(json.dumps(output, indent=2))
    else:
        # Rich table
        table = Table(title=f"\n📋 Work Items ({len(work_items)})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Priority")

        for wi in work_items:
            table.add_row(
                str(wi.id),
                wi.name,
                wi.type.value,
                wi.status.value,
                str(wi.priority)
            )

        console.print(table)
        console.print()
