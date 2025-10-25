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
    '--search', '-s',
    help='Search in task names and descriptions (case-insensitive)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_tasks(ctx: click.Context, work_item_id: int, status: str, task_type: str, search: str, format: str):
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
    if search:
        search_lower = search.lower()
        tasks = [
            t for t in tasks 
            if search_lower in t.name.lower() or 
               (t.description and search_lower in t.description.lower())
        ]

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
                'work_item_id': t.work_item_id
            }
            for t in tasks
        ]
        console.print(json.dumps(output, indent=2))
    else:
        # Rich table
        table = Table(title=f"\n📋 Tasks ({len(tasks)})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Effort")
        table.add_column("WI")

        for t in tasks:
            effort_str = f"{t.effort_hours}h" if t.effort_hours else "-"
            table.add_row(
                str(t.id),
                t.name,
                t.type.value,
                t.status.value,
                effort_str,
                str(t.work_item_id)
            )

        console.print(table)
        console.print()
