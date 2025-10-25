"""
apm work-item add-dependency - Add dependency between work items
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_work_item_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import work_items as wi_methods


@click.command(name='add-dependency')
@click.argument('work_item_id', type=int)
@click.option(
    '--depends-on', 'depends_on_work_item_id',
    type=int,
    required=True,
    help='Work Item ID that this work item depends on (prerequisite)'
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
def add_dependency(ctx: click.Context, work_item_id: int, depends_on_work_item_id: int, dep_type: str, notes: str):
    """
    Add dependency between work items (work item depends on another work item).

    \b
    Hard dependency: Work item cannot start until prerequisite completes
    Soft dependency: Warning logged but work item can start

    \b
    Examples:
      apm work-item add-dependency 5 --depends-on 3              # Hard dependency
      apm work-item add-dependency 5 --depends-on 4 --type soft  # Soft dependency
      apm work-item add-dependency 5 --depends-on 3 --notes "Needs auth system first"

    \b
    Workflow Impact:
      With hard dependency: apm work-item start 5 → BLOCKED until work item 3 completes
      With soft dependency: apm work-item start 5 → Allowed (warning logged)
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate both work items exist
    validate_work_item_exists(db, work_item_id, ctx)
    validate_work_item_exists(db, depends_on_work_item_id, ctx)

    # Get work item details for display
    work_item = wi_methods.get_work_item(db, work_item_id)
    dep_work_item = wi_methods.get_work_item(db, depends_on_work_item_id)

    try:
        # Add dependency (with circular detection)
        dependency = dep_methods.add_work_item_dependency(
            db,
            work_item_id,
            depends_on_work_item_id,
            dependency_type=dep_type,
            notes=notes
        )

        # Success message
        console.print(f"\n✅ [green]Dependency added:[/green]")
        console.print(f"   Work Item #{work_item_id} '{work_item.name}'")
        console.print(f"   {'→ DEPENDS ON →' if dep_type == 'hard' else '→ soft depends on →'}")
        console.print(f"   Work Item #{depends_on_work_item_id} '{dep_work_item.name}'")

        if dep_type == 'hard':
            console.print(f"\n⚠️  [yellow]Workflow Impact:[/yellow]")
            console.print(f"   Work Item #{work_item_id} cannot start until Work Item #{depends_on_work_item_id} completes")
        else:
            console.print(f"\n💡 [cyan]Soft Dependency:[/cyan]")
            console.print(f"   Work Item #{work_item_id} can start (warning will be logged)")

        if notes:
            console.print(f"\n📝 [dim]Notes: {notes}[/dim]")

        console.print()

    except Exception as e:
        if "circular" in str(e).lower() or "cycle" in str(e).lower():
            console.print(f"\n❌ [red]Circular dependency detected![/red]")
            console.print(f"   Adding this dependency would create a cycle")
            console.print(f"\n💡 [yellow]Dependency chain would be circular:[/yellow]")
            console.print(f"   Work Item #{work_item_id} → Work Item #{depends_on_work_item_id} → ... → Work Item #{work_item_id}")
            console.print(f"\n   Break the cycle by removing a dependency in the chain\n")
            raise click.Abort()
        else:
            console.print(f"\n❌ [red]Error adding dependency:[/red] {e}\n")
            raise click.Abort()
