"""
apm task list-blockers - List task blockers (what's blocking completion)
"""

import click
from rich.table import Table
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command(name='list-blockers')
@click.argument('task_id', type=int)
@click.option(
    '--unresolved-only',
    is_flag=True,
    help='Show only unresolved blockers'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_blockers(ctx: click.Context, task_id: int, unresolved_only: bool, format: str):
    """
    List task blockers (what's blocking completion).

    \b
    Blocker types:
      task: Another AIPM task blocking this one
      external: External factor (approval, review, etc.)

    \b
    Examples:
      apm task list-blockers 5                   # All blockers
      apm task list-blockers 5 --unresolved-only # Active blockers only
      apm task list-blockers 5 --format=json     # JSON output
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    validate_task_exists(db, task_id, ctx)
    task = task_methods.get_task(db, task_id)

    # Get blockers
    blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=unresolved_only)

    if format == 'json':
        import json
        output = {
            'task_id': task_id,
            'task_name': task.name,
            'blockers': [
                {
                    'id': b.id,
                    'type': b.blocker_type,
                    'blocker_task_id': b.blocker_task_id,
                    'description': b.blocker_description,
                    'reference': b.blocker_reference,
                    'resolved': b.is_resolved
                }
                for b in blockers
            ]
        }
        console.print(json.dumps(output, indent=2))
    else:
        # Rich table display
        filter_text = " (Unresolved Only)" if unresolved_only else ""
        console.print(f"\n🚧 [bold yellow]Blockers for Task #{task_id}: {task.name}{filter_text}[/bold yellow]\n")

        if not blockers:
            console.print("   ✅ [green]No blockers![/green]")
            if not unresolved_only:
                console.print("   Task can proceed to completion\n")
            return

        table = Table(title=f"{len(blockers)} Blocker(s)")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="bold")
        table.add_column("Status", style="yellow")

        for b in blockers:
            if b.blocker_type == 'task' and b.blocker_task_id:
                blocker_task = task_methods.get_task(db, b.blocker_task_id)
                desc = f"Task #{b.blocker_task_id}: {blocker_task.name if blocker_task else 'Unknown'}"
            else:
                desc = b.blocker_description
                if b.blocker_reference:
                    desc += f" ({b.blocker_reference})"

            status = "✅ Resolved" if b.is_resolved else "🚧 Unresolved"

            table.add_row(
                str(b.id),
                b.blocker_type,
                desc,
                status
            )

        console.print(table)
        console.print()

        unresolved_count = len([b for b in blockers if not b.is_resolved])
        if unresolved_count > 0:
            console.print(f"⚠️  [yellow]{unresolved_count} unresolved blocker(s) prevent task completion[/yellow]")
            console.print(f"💡 Resolve with: [cyan]apm task resolve-blocker <id> --notes \"Resolution\"[/cyan]\n")
