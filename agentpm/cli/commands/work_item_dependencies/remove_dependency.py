"""
apm work-item remove-dependency - Remove work item dependency
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.methods import dependencies as dep_methods


@click.command(name='remove-dependency')
@click.argument('dependency_id', type=int)
@click.option(
    '--confirm', is_flag=True,
    help='Skip confirmation prompt'
)
@click.pass_context
def remove_dependency(ctx: click.Context, dependency_id: int, confirm: bool):
    """
    Remove work item dependency.

    \b
    Examples:
      apm work-item remove-dependency 5
      apm work-item remove-dependency 5 --confirm
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get dependency details
    dependency = dep_methods.get_work_item_dependency(db, dependency_id)
    if not dependency:
        console.print(f"\n❌ [red]Dependency not found:[/red] #{dependency_id}\n")
        raise click.Abort()

    # Get work item names for display
    from agentpm.core.database.methods import work_items as wi_methods
    work_item = wi_methods.get_work_item(db, dependency.work_item_id)
    dep_work_item = wi_methods.get_work_item(db, dependency.depends_on_work_item_id)

    # Confirmation
    if not confirm:
        console.print(f"\n⚠️  [yellow]Remove dependency?[/yellow]")
        console.print(f"   Work Item #{dependency.work_item_id} '{work_item.name}'")
        console.print(f"   → NO LONGER DEPENDS ON →")
        console.print(f"   Work Item #{dependency.depends_on_work_item_id} '{dep_work_item.name}'")
        
        if not click.confirm("\n   Continue?"):
            console.print("   [dim]Cancelled[/dim]\n")
            return

    try:
        # Remove dependency
        success = dep_methods.remove_work_item_dependency(db, dependency_id)
        
        if success:
            console.print(f"\n✅ [green]Dependency removed:[/green]")
            console.print(f"   Work Item #{dependency.work_item_id} '{work_item.name}'")
            console.print(f"   → NO LONGER DEPENDS ON →")
            console.print(f"   Work Item #{dependency.depends_on_work_item_id} '{dep_work_item.name}'")
            console.print()
        else:
            console.print(f"\n❌ [red]Failed to remove dependency:[/red] #{dependency_id}\n")
            raise click.Abort()

    except Exception as e:
        console.print(f"\n❌ [red]Error removing dependency:[/red] {e}\n")
        raise click.Abort()
