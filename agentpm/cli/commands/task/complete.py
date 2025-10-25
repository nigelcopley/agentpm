"""
apm task complete - Complete task command
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_workflow_service, get_database_service
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.database.enums import TaskStatus
from agentpm.core.workflow import WorkflowError


@click.command(name='complete')
@click.argument('task_id', type=int)
@click.pass_context
def complete(ctx: click.Context, task_id: int):
    """
    Mark task as completed (transition to completed status).

    Uses WorkflowService to enforce quality gates and blocker checks.
    Task cannot complete if it has unresolved blockers.

    \b
    Example:
      apm task complete 5
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)

    # Get task
    task = TaskAdapter.get(db, task_id)

    if not task:
        console_err.print(f"\n❌ [red]Task not found:[/red] ID {task_id}\n")
        raise click.Abort()

    # Try to transition via WorkflowService (enforces quality gates and blockers)
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.DONE)

        console.print(f"\n✅ [green]Task completed:[/green] {updated_task.name}")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")
        console.print(f"   Type: {updated_task.type.value}")

        if updated_task.effort_hours:
            console.print(f"   Effort: {updated_task.effort_hours}h")

        # Show what this unblocks
        from agentpm.core.database.methods import dependencies as dep_methods
        dependents = dep_methods.get_tasks_depending_on(db, task_id)

        if dependents:
            console.print(f"\n🔓 [cyan]This unblocks {len(dependents)} dependent task(s):[/cyan]")
            for dep in dependents[:3]:  # Show first 3
                dependent_task = TaskAdapter.get(db, dep.task_id)
                if dependent_task:
                    console.print(f"   • Task #{dep.task_id}: {dependent_task.name}")
            if len(dependents) > 3:
                console.print(f"   ... and {len(dependents) - 3} more")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm status  # View project progress")
        console.print(f"   apm work-item show {updated_task.work_item_id}  # View work item\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console_err.print(f"[red]{e}[/red]")

        # Check for blockers to provide additional context
        from agentpm.core.database.methods import dependencies as dep_methods
        blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=True)

        if blockers:
            console_err.print("\n⚠️  [yellow]Unresolved blockers prevent completion:[/yellow]")
            for blocker in blockers:
                if blocker.blocker_type == 'task':
                    blocker_task = TaskAdapter.get(db, blocker.blocker_task_id)
                    desc = f"Task #{blocker.blocker_task_id}: {blocker_task.name if blocker_task else 'Unknown'}"
                else:
                    desc = blocker.blocker_description
                console_err.print(f"   • {desc}")

            console_err.print(f"\n💡 [cyan]Resolve blockers first:[/cyan]")
            console_err.print(f"   apm task list-blockers {task_id}")
            console_err.print(f"   apm task resolve-blocker <id> --notes \"Resolution\"\n")

        raise click.Abort()
