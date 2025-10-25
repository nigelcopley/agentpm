"""
apm task resolve-blocker - Mark blocker as resolved
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command(name='resolve-blocker')
@click.argument('blocker_id', type=int)
@click.option(
    '--notes',
    required=True,
    help='Resolution notes (required - explain how blocker was resolved)'
)
@click.pass_context
def resolve_blocker(ctx: click.Context, blocker_id: int, notes: str):
    """
    Mark blocker as resolved.

    Records resolution timestamp and notes for audit trail.
    If blocker was a task, this is often done automatically when
    the blocker task completes (auto-resolution trigger).

    \b
    Examples:
      apm task resolve-blocker 123 --notes "API was approved"
      apm task resolve-blocker 456 --notes "Legal review complete, contract signed"

    \b
    Workflow Impact:
      Task can now proceed to completion (blocker removed from validation)
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get blocker details
    blocker = dep_methods.get_task_blocker(db, blocker_id)

    if not blocker:
        console.print(f"\n❌ [red]Blocker not found:[/red] ID {blocker_id}\n")
        console.print("💡 List blockers with:")
        console.print("   apm task list-blockers <task-id>\n")
        raise click.Abort()

    if blocker.is_resolved:
        console.print(f"\n⚠️  [yellow]Blocker already resolved[/yellow]")
        console.print(f"   Resolved at: {blocker.resolved_at}")
        console.print(f"   Notes: {blocker.resolution_notes}\n")
        return

    # Resolve blocker
    try:
        resolved = dep_methods.resolve_task_blocker(db, blocker_id, notes)

        task = task_methods.get_task(db, blocker.task_id)

        console.print(f"\n✅ [green]Blocker resolved![/green]")
        console.print(f"   Blocker ID: {blocker_id}")
        console.print(f"   Blocked task: #{task.id} '{task.name}'")

        if blocker.blocker_type == 'task':
            console.print(f"   Blocker was: Task #{blocker.blocker_task_id}")
        else:
            console.print(f"   Blocker was: {blocker.blocker_description}")

        console.print(f"\n📝 [dim]Resolution: {notes}[/dim]")

        # Check if task has other unresolved blockers
        remaining = dep_methods.get_task_blockers(db, task.id, unresolved_only=True)
        if remaining:
            console.print(f"\n⚠️  [yellow]Task still has {len(remaining)} unresolved blocker(s)[/yellow]")
        else:
            console.print(f"\n✅ [green]No remaining blockers - task can now complete![/green]")

        console.print()

    except Exception as e:
        console.print(f"\n❌ [red]Error resolving blocker:[/red] {e}\n")
        raise click.Abort()
