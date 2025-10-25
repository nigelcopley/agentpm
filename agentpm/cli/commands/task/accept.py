"""
apm task accept - Accept task and optionally assign agent
"""

import click
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('task_id', type=int)
@click.option('--agent', type=str, help='Agent to assign (optional)')
@click.pass_context
def accept(ctx: click.Context, task_id: int, agent: str = None):
    """
    Accept task and transition to accepted status.

    Optionally assigns an agent. Task must be in validated status first.

    \b
    Examples:
      apm task accept 5
      apm task accept 5 --agent backend-developer
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

    # Check if already accepted or beyond
    if task.status.value in ['accepted', 'in_progress', 'blocked', 'review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Task already accepted[/green]")
        console.print(f"   Current status: {task.status.value}\n")
        return

    # If agent provided, validate and assign it first
    if agent:
        from agentpm.cli.utils.validation import validate_agent_exists
        from agentpm.core.database.methods import work_items as wi_methods

        # Get work item to find project_id
        work_item = wi_methods.get_work_item(db, task.work_item_id)
        if not work_item:
            console.print(f"\n❌ [red]Work item not found:[/red] ID {task.work_item_id}\n")
            raise click.Abort()

        # Validate agent exists (CI-001 compliance)
        validate_agent_exists(db, work_item.project_id, agent, ctx)

        # Update task with validated agent
        task = TaskAdapter.update(db, task_id, assigned_to=agent)

    # Try to transition via WorkflowService
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.ACTIVE)

        console.print(f"\n🎯 [cyan]Accepting Task #{task_id}...[/cyan]\n")

        if agent:
            console.print("✅ [green]Agent Assignment:[/green]")
            console.print(f"   ✅ Agent: {agent}")

        console.print(f"\n✅ [bold green]Task accepted successfully![/bold green]")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")
        if updated_task.assigned_to:
            console.print(f"   Assigned to: {updated_task.assigned_to}")

        console.print(f"\n📚 [cyan]Next step:[/cyan]")
        console.print(f"   apm task start {task_id}  # Begin work\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")

        # Show helpful guidance for common cases
        if task.status.value == 'proposed':
            console.print("\n💡 [cyan]Tip: Task must be validated first[/cyan]")
            console.print(f"   apm task validate {task_id}\n")

        raise click.Abort()
