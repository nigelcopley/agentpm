"""
apm task approve - Approve task completion
"""

import click
from datetime import datetime
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('task_id', type=int)
@click.option('--notes', type=str, help='Approval notes')
@click.pass_context
def approve(ctx: click.Context, task_id: int, notes: str = None):
    """
    Approve task and transition to completed status.

    Reviewer approves the work and marks task as complete.
    Checks acceptance criteria and blockers before approving.

    \b
    Examples:
      apm task approve 5
      apm task approve 5 --notes "Code looks good, tests passing"
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

    # Check if already completed
    if task.status.value in ['completed', 'archived']:
        console.print(f"\n✅ [green]Task already completed[/green]")
        console.print(f"   Current status: {task.status.value}\n")
        return

    # Store approval notes if provided
    if notes:
        quality_metadata = task.quality_metadata or {}
        quality_metadata['approval_notes'] = notes
        quality_metadata['approved_at'] = str(datetime.now())
        quality_metadata['review_approved'] = True
        task = TaskAdapter.update(db, task_id, quality_metadata=quality_metadata)

    # Try to transition via WorkflowService
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.DONE)

        console.print(f"\n✅ [cyan]Approving Task #{task_id}...[/cyan]\n")

        console.print("✅ [green]Validation:[/green]")
        console.print(f"   ✅ No blockers")

        # Show acceptance criteria if available
        if task.quality_metadata and 'acceptance_criteria' in task.quality_metadata:
            criteria = task.quality_metadata['acceptance_criteria']
            console.print(f"   ✅ Acceptance criteria: {len(criteria)} defined")

        if notes:
            console.print(f"\n📋 [cyan]Approval Notes:[/cyan]")
            console.print(f"   {notes}")

        console.print(f"\n✅ [bold green]Task approved and completed![/bold green]")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")
        console.print(f"   Type: {updated_task.type.value}")
        console.print(f"   Effort: {updated_task.effort_hours}h")

        # Check for dependent tasks that are now unblocked
        from agentpm.core.database.methods import dependencies as dep_methods
        dependents = dep_methods.get_tasks_depending_on(db, task_id)

        if dependents:
            console.print(f"\n🔓 [cyan]Impact:[/cyan]")
            console.print(f"   ✅ Unblocks {len(dependents)} dependent task(s):")
            for dep in dependents:
                # dep is a TaskDependency Pydantic model, not a dict
                dep_task = TaskAdapter.get(db, dep.task_id)
                if dep_task:
                    console.print(f"      • Task #{dep_task.id}: {dep_task.name}")

        # Check work item progress
        if task.work_item_id:
            from agentpm.core.database.methods import work_items as wi_methods
            work_item = wi_methods.get_work_item(db, task.work_item_id)
            if work_item:
                # Count completed tasks
                wi_tasks = TaskAdapter.list(db, work_item_id=task.work_item_id)
                completed = sum(1 for t in wi_tasks if t.status.value in ['completed', 'archived'])
                total = len(wi_tasks)
                completion_pct = (completed / total * 100) if total > 0 else 0

                console.print(f"\n📊 [cyan]Work Item Progress:[/cyan]")
                console.print(f"   Work Item #{work_item.id}: {work_item.name}")
                console.print(f"   {completed}/{total} tasks complete ({completion_pct:.0f}%)")

                if completion_pct >= 80:
                    console.print(f"   💡 Work item ready for review (≥80% complete)")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm status  # View project progress")
        if task.work_item_id:
            console.print(f"   apm work-item show {task.work_item_id}  # Check work item\n")
        else:
            console.print()

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")

        # Check for blockers to provide additional context
        from agentpm.core.database.methods import dependencies as dep_methods
        blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=True)

        if blockers:
            console.print("\n🚧 [yellow]Unresolved Blockers:[/yellow]\n")
            for blocker in blockers:
                console.print(f"   • Blocker #{blocker.id}: {blocker.blocker_description or 'Task blocker'}")
            console.print(f"\n💡 [cyan]Resolve blockers first[/cyan]\n")

        raise click.Abort()
