"""
apm work-item delete - Delete work item command
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import WorkItemAdapter, TaskAdapter


@click.command(name='delete')
@click.argument('work_item_id', type=int)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Force deletion without confirmation prompt'
)
@click.option(
    '--cascade',
    is_flag=True,
    help='Also delete child work items (if any)'
)
@click.pass_context
def delete(ctx: click.Context, work_item_id: int, force: bool, cascade: bool):
    """
    Delete a work item.

    Permanently removes a work item and all its associated tasks from the database.
    This action cannot be undone. If the work item has child work items, you may
    need to use --cascade flag.

    \b
    Examples:
      apm work-item delete 5
      apm work-item delete 5 --force
      apm work-item delete 5 --cascade
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current work item to show details
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console_err.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        console_err.print("💡 [yellow]List work items with:[/yellow]")
        console_err.print("   apm work-item list\n")
        raise click.Abort()

    # Get associated tasks count
    tasks = TaskAdapter.list(db, work_item_id=work_item_id)
    task_count = len(tasks)

    # Check for child work items (if cascade not specified)
    child_work_items = []
    if not cascade:
        from agentpm.core.database.methods import work_items as wi_methods
        child_work_items = wi_methods.get_child_work_items(db, work_item_id)

    # Show work item details for confirmation
    console.print(f"\n📋 [cyan]Work item to delete:[/cyan]")
    console.print(f"   ID: {work_item.id}")
    console.print(f"   Name: {work_item.name}")
    console.print(f"   Type: {work_item.type.value}")
    console.print(f"   Status: {work_item.status.value}")
    console.print(f"   Project: {work_item.project_id}")
    console.print(f"   Tasks: {task_count} associated tasks")
    
    if child_work_items:
        console_err.print(f"\n⚠️  [yellow]Work item has {len(child_work_items)} child work items:[/yellow]")
        for child in child_work_items[:5]:  # Show first 5
            console_err.print(f"   • Work Item {child.id}: {child.name}")
        if len(child_work_items) > 5:
            console_err.print(f"   • ... and {len(child_work_items) - 5} more")
        console_err.print(f"\n💡 [cyan]Use --cascade to delete child work items too:[/cyan]")
        console_err.print(f"   apm work-item delete {work_item_id} --cascade\n")
        raise click.Abort()

    # Confirmation prompt (unless --force)
    if not force:
        console.print(f"\n⚠️  [yellow]This will permanently delete:[/yellow]")
        console.print(f"   • Work item: {work_item.name}")
        console.print(f"   • {task_count} associated tasks")
        if cascade and child_work_items:
            console.print(f"   • {len(child_work_items)} child work items")
        
        if not click.confirm("Are you sure you want to delete this work item?"):
            console.print("❌ [red]Deletion cancelled.[/red]\n")
            raise click.Abort()

    # Delete the work item (this will cascade delete tasks automatically)
    try:
        success = WorkItemAdapter.delete(db, work_item_id)
        
        if success:
            console.print(f"\n✅ [green]Work item deleted successfully:[/green] #{work_item_id}")
            console.print(f"   Name: {work_item.name}")
            console.print(f"   Tasks deleted: {task_count}")
            if cascade and child_work_items:
                console.print(f"   Child work items deleted: {len(child_work_items)}")
            
            console.print(f"\n📚 [cyan]Next steps:[/cyan]")
            console.print(f"   apm work-item list --project-id={work_item.project_id}  # View remaining work items")
            console.print(f"   apm project show {work_item.project_id}  # View project\n")
        else:
            console_err.print(f"\n❌ [red]Failed to delete work item:[/red] #{work_item_id}\n")
            raise click.Abort()

    except Exception as e:
        console_err.print(f"\n❌ [red]Delete failed:[/red] {e}\n")
        raise click.Abort()
