"""
apm work-item submit-review - Submit work item for review
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command(name='submit-review')
@click.argument('work_item_id', type=int)
@click.option('--notes', type=str, help='Submission notes for reviewer')
@click.pass_context
def submit_review(ctx: click.Context, work_item_id: int, notes: str = None):
    """
    Submit work item for review (transition to review status).

    Indicates work is complete and ready for quality validation.
    Checks that all required tasks are complete.

    \b
    Examples:
      apm work-item submit-review 7
      apm work-item submit-review 7 --notes "All tasks complete, ready for release"
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

    # Check if already in review or beyond
    if work_item.status.value in ['review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Work item already in review or completed[/green]")
        console.print(f"   Current status: {work_item.status.value}\n")
        return

    # Get tasks for validation display
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
    completed_tasks = [t for t in tasks if t.status.value == 'completed']

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.REVIEW)

        console.print(f"\n📝 [cyan]Submitting Work Item #{work_item_id} for review...[/cyan]\n")

        console.print("✅ [green]Validation:[/green]")
        console.print(f"   ✅ {len(completed_tasks)}/{len(tasks)} tasks complete")

        if notes:
            console.print(f"\n📋 [cyan]Submission Notes:[/cyan]")
            console.print(f"   {notes}")

        console.print(f"\n✅ [green]Work item submitted for review![/green]")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Reviewer actions:")
        console.print(f"   apm work-item approve {work_item_id}  # If approved")
        console.print(f"   apm work-item request-changes {work_item_id} --reason \"...\"  # If changes needed\n")

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
