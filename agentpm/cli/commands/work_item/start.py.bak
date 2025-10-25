"""
apm work-item start - Start working on work item (transition to in_progress)
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('work_item_id', type=int)
@click.pass_context
def start(ctx: click.Context, work_item_id: int):
    """
    Start working on work item (transition to in_progress).

    Transitions work item from accepted to in_progress status.
    Work item must be accepted before starting.

    \b
    Example:
      apm work-item start 7
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)

    # Get work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        raise click.Abort()

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.ACTIVE)

        console.print(f"\n✅ [green]Work item started:[/green] {updated_wi.name}")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")
        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Work on tasks")
        console.print(f"   apm task list --work-item-id={work_item_id}  # View tasks")
        console.print(f"   apm task start <task-id>  # Start a task")
        console.print(f"   # When all tasks done:")
        console.print(f"   apm work-item submit-review {work_item_id}\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")

        # Show helpful guidance for common cases
        if work_item.status.value == 'proposed':
            console.print("\n💡 [cyan]Tip: Work item must be validated and accepted first[/cyan]")
            console.print(f"   apm work-item validate {work_item_id}")
            console.print(f"   apm work-item accept {work_item_id}\n")
        elif work_item.status.value == 'validated':
            console.print("\n💡 [cyan]Tip: Work item must be accepted first[/cyan]")
            console.print(f"   apm work-item accept {work_item_id}\n")

        raise click.Abort()
