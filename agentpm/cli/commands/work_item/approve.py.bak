"""
apm work-item approve - Approve work item completion
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('work_item_id', type=int)
@click.option('--notes', type=str, help='Approval notes')
@click.pass_context
def approve(ctx: click.Context, work_item_id: int, notes: str = None):
    """
    Approve work item and transition to completed status.

    Reviewer validates quality and marks work item as complete.
    Checks that all required tasks are complete.

    \b
    Examples:
      apm work-item approve 7
      apm work-item approve 7 --notes "All deliverables met, quality excellent"
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)

    # Get work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console_err.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        raise click.Abort()

    # Check if already completed
    if work_item.status.value in ['completed', 'archived']:
        console.print(f"\n✅ [green]Work item already completed[/green]")
        console.print(f"   Current status: {work_item.status.value}\n")
        return

    # Get tasks for display
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
    completed_tasks = [t for t in tasks if t.status.value == 'completed']

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.DONE)

        console.print(f"\n✅ [cyan]Approving Work Item #{work_item_id}...[/cyan]\n")

        console.print("✅ [green]Validation:[/green]")
        console.print(f"   ✅ All required tasks complete ({len(completed_tasks)}/{len(tasks)})")

        if notes:
            console.print(f"\n📋 [cyan]Approval Notes:[/cyan]")
            console.print(f"   {notes}")

        console.print(f"\n✅ [bold green]Work item approved and completed![/bold green]")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")
        console.print(f"   Type: {updated_wi.type.value}")
        console.print(f"   Tasks: {len(completed_tasks)}/{len(tasks)} complete")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm status  # View project progress")
        console.print(f"   apm work-item add-summary {work_item_id} --type milestone  # Add completion summary\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console_err.print(f"[red]{e}[/red]")

        # Show additional context about task completion
        console_err.print(f"\n💡 [yellow]Current status:[/yellow]")
        console_err.print(f"   Work item: {work_item.status.value}")
        console_err.print(f"   Tasks complete: {len(completed_tasks)}/{len(tasks)}")
        console_err.print(f"\n📋 [cyan]View details:[/cyan]")
        console_err.print(f"   apm work-item show {work_item_id}")
        console_err.print(f"   apm task list --work-item-id={work_item_id}\n")
        raise click.Abort()
