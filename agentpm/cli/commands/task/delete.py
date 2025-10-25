"""
apm task delete - Delete task command
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import TaskAdapter


@click.command(name='delete')
@click.argument('task_id', type=int)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Force deletion without confirmation prompt'
)
@click.option(
    '--cascade',
    is_flag=True,
    help='Also delete dependent tasks (if any)'
)
@click.pass_context
def delete(ctx: click.Context, task_id: int, force: bool, cascade: bool):
    """
    Delete a task.

    Permanently removes a task from the database. This action cannot be undone.
    If the task has dependencies, you may need to use --cascade flag.

    \b
    Examples:
      apm task delete 5
      apm task delete 5 --force
      apm task delete 5 --cascade
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current task to show details
    task = TaskAdapter.get(db, task_id)

    if not task:
        console_err.print(f"\n❌ [red]Task not found:[/red] ID {task_id}\n")
        console_err.print("💡 [yellow]List tasks with:[/yellow]")
        console_err.print("   apm task list\n")
        raise click.Abort()

    # Show task details for confirmation
    console.print(f"\n📋 [cyan]Task to delete:[/cyan]")
    console.print(f"   ID: {task.id}")
    console.print(f"   Name: {task.name}")
    console.print(f"   Type: {task.type.value}")
    console.print(f"   Status: {task.status.value}")
    console.print(f"   Work Item: {task.work_item_id}")
    if task.assigned_to:
        console.print(f"   Assigned to: {task.assigned_to}")

    # Check for dependencies (if cascade not specified)
    if not cascade:
        from agentpm.core.database.methods import dependencies as dep_methods
        dependencies = dep_methods.get_task_dependencies(db, task_id)
        if dependencies:
            console_err.print(f"\n⚠️  [yellow]Task has {len(dependencies)} dependencies:[/yellow]")
            for dep in dependencies[:5]:  # Show first 5
                console_err.print(f"   • Task {dep.depends_on_task_id}")
            if len(dependencies) > 5:
                console_err.print(f"   • ... and {len(dependencies) - 5} more")
            console_err.print(f"\n💡 [cyan]Use --cascade to delete dependencies too:[/cyan]")
            console_err.print(f"   apm task delete {task_id} --cascade\n")
            raise click.Abort()

    # Confirmation prompt (unless --force)
    if not force:
        console.print(f"\n⚠️  [yellow]This will permanently delete the task.[/yellow]")
        if cascade:
            console.print(f"⚠️  [yellow]Dependencies will also be deleted.[/yellow]")
        
        if not click.confirm("Are you sure you want to delete this task?"):
            console.print("❌ [red]Deletion cancelled.[/red]\n")
            raise click.Abort()

    # Delete the task
    try:
        success = TaskAdapter.delete(db, task_id)
        
        if success:
            console.print(f"\n✅ [green]Task deleted successfully:[/green] #{task_id}")
            console.print(f"   Name: {task.name}")
            if cascade:
                console.print(f"   Dependencies: Also deleted")
            
            console.print(f"\n📚 [cyan]Next steps:[/cyan]")
            console.print(f"   apm task list --work-item-id={task.work_item_id}  # View remaining tasks")
            console.print(f"   apm work-item show {task.work_item_id}  # View work item\n")
        else:
            console_err.print(f"\n❌ [red]Failed to delete task:[/red] #{task_id}\n")
            raise click.Abort()

    except Exception as e:
        console_err.print(f"\n❌ [red]Delete failed:[/red] {e}\n")
        raise click.Abort()
