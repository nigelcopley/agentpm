"""
apm work-item request-changes - Request changes to work item
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command(name='request-changes')
@click.argument('work_item_id', type=int)
@click.option('--reason', type=str, required=True, help='Reason for requesting changes')
@click.pass_context
def request_changes(ctx: click.Context, work_item_id: int, reason: str):
    """
    Request changes to work item (transition back to in_progress).

    Reviewer rejects current work and requests changes.
    Work item returns to in_progress for rework.

    \b
    Examples:
      apm work-item request-changes 7 --reason "Missing user documentation"
      apm work-item request-changes 7 --reason "Need performance optimization"
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

    # Must be in review to request changes
    if work_item.status != WorkItemStatus.REVIEW:
        console_err.print(f"\n❌ [red]Work item not in review[/red]")
        console_err.print(f"   Current status: {work_item.status.value}")
        console_err.print(f"   Expected: review")
        console_err.print(f"\n💡 [yellow]Only work items in review can have changes requested[/yellow]\n")
        raise click.Abort()

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.ACTIVE)

        console.print(f"\n🔄 [cyan]Requesting Changes for Work Item #{work_item_id}...[/cyan]\n")

        console.print("📋 [yellow]Change Request:[/yellow]")
        console.print(f"   {reason}")

        console.print(f"\n✅ [green]Work item returned to in_progress[/green]")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Address the requested changes")
        console.print(f"   apm task list --work-item-id={work_item_id}  # View tasks")
        console.print(f"   # When ready:")
        console.print(f"   apm work-item submit-review {work_item_id}\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console_err.print(f"[red]{e}[/red]")
        raise click.Abort()
