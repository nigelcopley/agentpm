"""
apm task add-dependency - Add dependency between tasks
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command(name='add-dependency')
@click.argument('task_id', type=int)
@click.option(
    '--depends-on', 'depends_on_task_id',
    type=int,
    required=True,
    help='Task ID that this task depends on (prerequisite)'
)
@click.option(
    '--type', 'dep_type',
    type=click.Choice(['hard', 'soft'], case_sensitive=False),
    default='hard',
    help='Dependency type (hard blocks start, soft warns only)'
)
@click.option(
    '--notes',
    help='Optional notes about this dependency'
)
@click.pass_context
def add_dependency(ctx: click.Context, task_id: int, depends_on_task_id: int, dep_type: str, notes: str):
    """
    Add dependency between tasks (task depends on another task).

    \b
    Hard dependency: Task cannot start until prerequisite completes
    Soft dependency: Warning logged but task can start

    \b
    Examples:
      apm task add-dependency 5 --depends-on 3              # Hard dependency
      apm task add-dependency 5 --depends-on 4 --type soft  # Soft dependency
      apm task add-dependency 5 --depends-on 3 --notes "Needs auth schema first"

    \b
    Workflow Impact:
      With hard dependency: apm task start 5 → BLOCKED until task 3 completes
      With soft dependency: apm task start 5 → Allowed (warning logged)
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate both tasks exist
    validate_task_exists(db, task_id, ctx)
    validate_task_exists(db, depends_on_task_id, ctx)

    # Get task details for display
    task = task_methods.get_task(db, task_id)
    dep_task = task_methods.get_task(db, depends_on_task_id)

    try:
        # Add dependency (with circular detection)
        dependency = dep_methods.add_task_dependency(
            db,
            task_id,
            depends_on_task_id,
            dependency_type=dep_type,
            notes=notes
        )

        # Success message
        console.print(f"\n✅ [green]Dependency added:[/green]")
        console.print(f"   Task #{task_id} '{task.name}'")
        console.print(f"   {'→ DEPENDS ON →' if dep_type == 'hard' else '→ soft depends on →'}")
        console.print(f"   Task #{depends_on_task_id} '{dep_task.name}'")

        if dep_type == 'hard':
            console.print(f"\n⚠️  [yellow]Workflow Impact:[/yellow]")
            console.print(f"   Task #{task_id} cannot start until Task #{depends_on_task_id} completes")
        else:
            console.print(f"\n💡 [cyan]Soft Dependency:[/cyan]")
            console.print(f"   Task #{task_id} can start (warning will be logged)")

        if notes:
            console.print(f"\n📝 [dim]Notes: {notes}[/dim]")

        console.print()

    except Exception as e:
        if "circular" in str(e).lower() or "cycle" in str(e).lower():
            console.print(f"\n❌ [red]Circular dependency detected![/red]")
            console.print(f"   Adding this dependency would create a cycle")
            console.print(f"\n💡 [yellow]Dependency chain would be circular:[/yellow]")
            console.print(f"   Task #{task_id} → Task #{depends_on_task_id} → ... → Task #{task_id}")
            console.print(f"\n   Break the cycle by removing a dependency in the chain\n")
            raise click.Abort()
        else:
            console.print(f"\n❌ [red]Error adding dependency:[/red] {e}\n")
            raise click.Abort()
