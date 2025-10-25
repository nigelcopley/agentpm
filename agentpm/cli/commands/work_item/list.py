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
    '--priority',
    type=click.IntRange(1, 5),
    help='Filter by priority (1-5)'
)
@click.option(
    '--phase',
    help='Filter by phase (D1, P1, I1, R1, O1, E1)'
)
@click.option(
    '--search', '-s',
    help='Search in work item names and descriptions (case-insensitive)'
)
@click.option(
    '--sort',
    type=click.Choice(['id', 'name', 'status', 'priority', 'type', 'created'], case_sensitive=False),
    default='id',
    help='Sort by field'
)
@click.option(
    '--reverse', '-r',
    is_flag=True,
    help='Reverse sort order'
)
@click.option(
    '--limit', '-l',
    type=int,
    help='Limit number of results'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json', 'csv'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_work_items(ctx: click.Context, wi_type: str, status: str, priority: int, phase: str, search: str, sort: str, reverse: bool, limit: int, format: str):
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
    if priority:
        work_items = [wi for wi in work_items if wi.priority == priority]
    if phase:
        work_items = [wi for wi in work_items if wi.phase and wi.phase.value == phase]
    if search:
        search_lower = search.lower()
        work_items = [
            wi for wi in work_items 
            if search_lower in wi.name.lower() or 
               (wi.description and search_lower in wi.description.lower())
        ]

    # Apply sorting
    if sort == 'name':
        work_items.sort(key=lambda wi: wi.name.lower(), reverse=reverse)
    elif sort == 'status':
        work_items.sort(key=lambda wi: wi.status.value, reverse=reverse)
    elif sort == 'priority':
        work_items.sort(key=lambda wi: wi.priority, reverse=reverse)
    elif sort == 'type':
        work_items.sort(key=lambda wi: wi.type.value, reverse=reverse)
    elif sort == 'created':
        work_items.sort(key=lambda wi: wi.created_at or '', reverse=reverse)
    else:  # default: id
        work_items.sort(key=lambda wi: wi.id or 0, reverse=reverse)

    # Apply limit
    if limit:
        work_items = work_items[:limit]

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
                'priority': wi.priority,
                'phase': wi.phase.value if wi.phase else None,
                'effort_estimate_hours': wi.effort_estimate_hours,
                'created_at': wi.created_at.isoformat() if wi.created_at else None
            }
            for wi in work_items
        ]
        console.print(json.dumps(output, indent=2))
    elif format == 'csv':
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Type', 'Status', 'Priority', 'Phase', 'Effort Estimate', 'Created'])
        for wi in work_items:
            writer.writerow([
                wi.id,
                wi.name,
                wi.type.value,
                wi.status.value,
                wi.priority,
                wi.phase.value if wi.phase else '',
                wi.effort_estimate_hours or '',
                wi.created_at.isoformat() if wi.created_at else ''
            ])
        console.print(output.getvalue())
    else:
        # Rich table
        table = Table(title=f"\n📋 Work Items ({len(work_items)})")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Name", style="bold", width=35)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Priority", style="blue", width=8)
        table.add_column("Phase", style="green", width=6)
        table.add_column("Effort", width=8)

        for wi in work_items:
            priority_str = f"P{wi.priority}" if wi.priority else "-"
            phase_str = wi.phase.value if wi.phase else "-"
            effort_str = f"{wi.effort_estimate_hours}h" if wi.effort_estimate_hours else "-"
            
            table.add_row(
                str(wi.id),
                wi.name[:32] + "..." if len(wi.name) > 35 else wi.name,
                wi.type.value,
                wi.status.value,
                priority_str,
                phase_str,
                effort_str
            )

        console.print(table)
        console.print()
