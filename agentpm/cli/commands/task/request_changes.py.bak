"""
apm task request-changes - Request changes during review
"""

import click
from datetime import datetime
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command(name='request-changes')
@click.argument('task_id', type=int)
@click.option('--reason', type=str, required=True, help='Reason for requesting changes (required)')
@click.pass_context
def request_changes(ctx: click.Context, task_id: int, reason: str):
    """
    Request changes and return task to in_progress status.

    Reviewer requests modifications and sends task back for rework.
    Reason is required and will be recorded in audit trail.

    \b
    Example:
      apm task request-changes 5 --reason "Missing edge case tests"
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

    # Validate reason length
    if len(reason.strip()) < 20:
        console.print(f"\n❌ [red]Reason too short[/red]")
        console.print(f"   Please provide a detailed reason (≥20 characters)")
        console.print(f"   Current: {len(reason.strip())} characters\n")
        raise click.Abort()

    # Store rework request in quality metadata
    quality_metadata = task.quality_metadata or {}
    rework_reasons = quality_metadata.get('rework_reasons', [])
    rework_reasons.append({
        'reason': reason,
        'requested_at': str(datetime.now()),
        'from_status': task.status.value
    })
    quality_metadata['rework_reasons'] = rework_reasons
    task = TaskAdapter.update(db, task_id, quality_metadata=quality_metadata)

    # Try to transition via WorkflowService
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.ACTIVE)

        console.print(f"\n🔄 [cyan]Requesting changes for Task #{task_id}...[/cyan]\n")

        console.print("✅ [green]Rework Requested:[/green]")
        console.print(f"   Reason: {reason}")
        console.print(f"   Requested at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        console.print(f"\n✅ [bold green]Task returned for rework![/bold green]")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Developer addresses feedback:")
        console.print(f"   apm task show {task_id}  # See rework reason")
        console.print(f"   # After fixing:")
        console.print(f"   apm task submit-review {task_id} --notes \"Addressed feedback\"\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")
        raise click.Abort()
