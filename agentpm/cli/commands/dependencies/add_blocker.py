"""
apm task add-blocker - Add blocker to task (internal task or external factor)
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command(name='add-blocker')
@click.argument('task_id', type=int)
@click.option(
    '--task', 'blocker_task_id',
    type=int,
    help='Task ID that is blocking this task'
)
@click.option(
    '--external',
    help='External blocker description (e.g., "Waiting on API approval")'
)
@click.option(
    '--reference',
    help='External reference (ticket ID, URL, etc.)'
)
@click.pass_context
def add_blocker(ctx: click.Context, task_id: int, blocker_task_id: int, external: str, reference: str):
    """
    Add blocker to task (internal task or external factor).

    \b
    Blocker types:
      --task: Another AIPM task is blocking this one
      --external: External factor (API approval, legal review, etc.)

    \b
    Examples:
      apm task add-blocker 5 --task 3                           # Task 3 blocks Task 5
      apm task add-blocker 5 --external "Waiting on API approval"
      apm task add-blocker 5 --external "Legal review" --reference "LEGAL-123"

    \b
    Workflow Impact:
      Task 5 cannot complete (→ REVIEW/DONE) until blocker resolved
      Use 'apm task resolve-blocker <id>' to mark blocker resolved
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate task exists
    validate_task_exists(db, task_id, ctx)
    task = task_methods.get_task(db, task_id)

    # Validate blocker type
    if not blocker_task_id and not external:
        console.print("\n❌ [red]Must specify --task or --external[/red]\n")
        console.print("💡 Examples:")
        console.print("   apm task add-blocker 5 --task 3")
        console.print("   apm task add-blocker 5 --external \"Waiting on approval\"\n")
        raise click.Abort()

    if blocker_task_id and external:
        console.print("\n❌ [red]Cannot specify both --task and --external[/red]\n")
        console.print("💡 Use one or the other:")
        console.print("   --task for internal blocker (another AIPM task)")
        console.print("   --external for external blocker (approval, review, etc.)\n")
        raise click.Abort()

    try:
        if blocker_task_id:
            # Internal task blocker
            validate_task_exists(db, blocker_task_id, ctx)
            blocker_task = task_methods.get_task(db, blocker_task_id)

            blocker = dep_methods.add_task_blocker(
                db,
                task_id,
                blocker_type='task',
                blocker_task_id=blocker_task_id
            )

            console.print(f"\n🚧 [yellow]Blocker added:[/yellow]")
            console.print(f"   Task #{task_id} '{task.name}'")
            console.print(f"   BLOCKED BY →")
            console.print(f"   Task #{blocker_task_id} '{blocker_task.name}'\n")

        else:
            # External blocker
            blocker = dep_methods.add_task_blocker(
                db,
                task_id,
                blocker_type='external',
                blocker_description=external,
                blocker_reference=reference
            )

            console.print(f"\n🚧 [yellow]External blocker added:[/yellow]")
            console.print(f"   Task #{task_id} '{task.name}'")
            console.print(f"   BLOCKED BY → {external}")
            if reference:
                console.print(f"   Reference: {reference}")
            console.print()

        console.print("⚠️  [yellow]Workflow Impact:[/yellow]")
        console.print(f"   Task #{task_id} cannot complete until blocker resolved")
        console.print(f"   Use 'apm task resolve-blocker {blocker.id}' when ready\n")

    except Exception as e:
        console.print(f"\n❌ [red]Error adding blocker:[/red] {e}\n")
        raise click.Abort()
