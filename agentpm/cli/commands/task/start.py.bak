"""
apm task start - Start working on a task (transition to in_progress)
"""

import click
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('task_id', type=int)
@click.pass_context
def start(ctx: click.Context, task_id: int):
    """
    Start working on a task (transition to in_progress).

    Uses WorkflowService to enforce quality gates and state machine rules.

    \b
    Example:
      apm task start 5
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)

    # Get task
    task = TaskAdapter.get(db, task_id)

    if not task:
        console.print(f"\n❌ [red]Task not found:[/red] ID {task_id}\n")
        raise click.Abort()

    # Try to transition via WorkflowService (enforces quality gates)
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.ACTIVE)

        console.print(f"\n✅ [green]Task started:[/green] {updated_task.name}")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")
        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Work on the task")
        console.print(f"   apm task show {task_id}  # View details")
        console.print(f"   # When done:")
        console.print(f"   apm task complete {task_id}\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")
        raise click.Abort()
