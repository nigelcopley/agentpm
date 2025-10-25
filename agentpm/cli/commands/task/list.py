"""
apm task list - List tasks with optional filters
"""

import click
from rich.table import Table
from agentpm.core.database.adapters import TaskAdapter, WorkItemAdapter
from agentpm.core.database.enums import TaskStatus
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import (
    get_task_type_choices,
    validate_work_item_exists
)


@click.command(name='list')
@click.option(
    '--work-item-id', 'work_item_id',
    type=int,
    help='Filter by work item ID'
)
@click.option(
    '--status',
    type=click.Choice(TaskStatus.choices(), case_sensitive=False),
    help='Filter by status'
)
@click.option(
    '--type', 'task_type',
    type=click.Choice(get_task_type_choices(), case_sensitive=False),
    help='Filter by task type'
)
@click.option(
    '--assigned-to',
    help='Filter by assigned agent/user'
)
@click.option(
    '--priority',
    type=click.IntRange(1, 5),
    help='Filter by priority (1-5)'
)
@click.option(
    '--search', '-s',
    help='Search in task names and descriptions (case-insensitive)'
)
@click.option(
    '--sort',
    type=click.Choice(['id', 'name', 'status', 'priority', 'effort', 'created'], case_sensitive=False),
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
def list_tasks(ctx: click.Context, work_item_id: int, status: str, task_type: str, assigned_to: str, priority: int, search: str, sort: str, reverse: bool, limit: int, format: str):
    """
    List tasks with optional filters.

    \b
    Examples:
      apm task list                           # All tasks in project
      apm task list --work-item-id=1          # Tasks for specific work item
      apm task list --status=in_progress      # Active tasks
      apm task list --type=implementation     # Implementation tasks only
      apm task list --search "validation"     # Search in names/descriptions
      apm task list --format=json             # JSON output
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # THREE-LAYER PATTERN: Use adapters, not direct methods calls
    if work_item_id:
        validate_work_item_exists(db, work_item_id, ctx)
        tasks = TaskAdapter.list(db, work_item_id=work_item_id)
    else:
        # Get all tasks for project (need to get all work items first)
        project_id = get_current_project_id(ctx)
        work_items = WorkItemAdapter.list(db, project_id=project_id)

        tasks = []
        for wi in work_items:
            tasks.extend(TaskAdapter.list(db, work_item_id=wi.id))

    # Apply filters
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    if task_type:
        tasks = [t for t in tasks if t.type.value == task_type]
    if assigned_to:
        tasks = [t for t in tasks if t.assigned_to and assigned_to.lower() in t.assigned_to.lower()]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if search:
        search_lower = search.lower()
        tasks = [
            t for t in tasks 
            if search_lower in t.name.lower() or 
               (t.description and search_lower in t.description.lower())
        ]

    # Apply sorting
    if sort == 'name':
        tasks.sort(key=lambda t: t.name.lower(), reverse=reverse)
    elif sort == 'status':
        tasks.sort(key=lambda t: t.status.value, reverse=reverse)
    elif sort == 'priority':
        tasks.sort(key=lambda t: t.priority, reverse=reverse)
    elif sort == 'effort':
        tasks.sort(key=lambda t: t.effort_hours or 0, reverse=reverse)
    elif sort == 'created':
        tasks.sort(key=lambda t: t.created_at or '', reverse=reverse)
    else:  # default: id
        tasks.sort(key=lambda t: t.id or 0, reverse=reverse)

    # Apply limit
    if limit:
        tasks = tasks[:limit]

    if not tasks:
        console.print("\nℹ️  [yellow]No tasks found[/yellow]\n")
        console.print("💡 [cyan]Create one with:[/cyan]")
        console.print("   apm task create \"Task name\" --work-item-id=<id> --type=implementation --effort=3\n")
        return

    if format == 'json':
        import json
        output = [
            {
                'id': t.id,
                'name': t.name,
                'type': t.type.value,
                'status': t.status.value,
                'effort_hours': t.effort_hours,
                'priority': t.priority,
                'assigned_to': t.assigned_to,
                'work_item_id': t.work_item_id,
                'created_at': t.created_at.isoformat() if t.created_at else None
            }
            for t in tasks
        ]
        console.print(json.dumps(output, indent=2))
    elif format == 'csv':
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Type', 'Status', 'Priority', 'Effort', 'Assigned To', 'Work Item ID', 'Created'])
        for t in tasks:
            writer.writerow([
                t.id,
                t.name,
                t.type.value,
                t.status.value,
                t.priority,
                t.effort_hours or '',
                t.assigned_to or '',
                t.work_item_id,
                t.created_at.isoformat() if t.created_at else ''
            ])
        console.print(output.getvalue())
    else:
        # Rich table
        table = Table(title=f"\n📋 Tasks ({len(tasks)})")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Name", style="bold", width=30)
        table.add_column("Type", style="magenta", width=12)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Priority", style="blue", width=8)
        table.add_column("Effort", width=8)
        table.add_column("Assigned", width=15)
        table.add_column("WI", style="green", width=4)

        for t in tasks:
            effort_str = f"{t.effort_hours}h" if t.effort_hours else "-"
            priority_str = f"P{t.priority}" if t.priority else "-"
            assigned_str = t.assigned_to[:12] + "..." if t.assigned_to and len(t.assigned_to) > 15 else (t.assigned_to or "-")
            
            table.add_row(
                str(t.id),
                t.name[:27] + "..." if len(t.name) > 30 else t.name,
                t.type.value,
                t.status.value,
                priority_str,
                effort_str,
                assigned_str,
                str(t.work_item_id)
            )

        console.print(table)
        console.print()
