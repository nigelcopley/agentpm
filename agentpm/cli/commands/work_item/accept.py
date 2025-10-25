"""
apm work-item accept - Accept work item with effort estimate
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
@click.option('--effort', type=float, required=True, help='Total effort estimate in hours (required)')
@click.pass_context
def accept(ctx: click.Context, work_item_id: int, effort: float):
    """
    Accept work item and transition to accepted status.

    Sets effort estimate (should match sum of task estimates).
    Work item must be in validated status first.

    \b
    Example:
      apm work-item accept 1 --effort 15.5
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

    # Check if already accepted or beyond
    if work_item.status.value in ['accepted', 'in_progress', 'blocked', 'review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Work item already accepted[/green]")
        console.print(f"   Current status: {work_item.status.value}\n")
        return

    # Update effort estimate
    work_item = WorkItemAdapter.update(db, work_item_id, effort_estimate_hours=effort)

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.ACTIVE)

        console.print(f"\n🎯 [cyan]Accepting Work Item #{work_item_id}...[/cyan]\n")

        # Calculate task sum and compare
        tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
        task_sum = sum(t.effort_hours or 0 for t in tasks)

        console.print("✅ [green]Effort Estimate:[/green]")
        console.print(f"   Specified: {effort}h")
        console.print(f"   Task sum: {task_sum}h ({len(tasks)} tasks)")

        diff_pct = abs(effort - task_sum) / effort * 100 if effort > 0 else 0
        if diff_pct > 20:
            console.print(f"   ⚠️  Mismatch: {diff_pct:.0f}% difference (consider adjusting)")
        else:
            console.print(f"   ✅ Match")

        # Check task status
        task_statuses = [t.status.value for t in tasks]
        proposed_count = sum(1 for s in task_statuses if s == 'proposed')
        if proposed_count > 0:
            console.print(f"\n⚠️  [yellow]Task Status Warning:[/yellow]")
            console.print(f"   {proposed_count}/{len(tasks)} tasks still DRAFT")
            console.print(f"   Consider validating tasks first:")
            for t in tasks:
                if t.status.value == 'proposed':
                    console.print(f"   apm task validate {t.id}")

        console.print(f"\n✅ [bold green]Work item accepted![/bold green]")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")
        console.print(f"   Effort: {effort}h")

        console.print(f"\n📚 [cyan]Next step:[/cyan]")
        console.print(f"   apm work-item start {work_item_id}  # Begin work\n")

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")

        # Show helpful guidance for common cases
        if work_item.status.value == 'proposed':
            console.print("\n💡 [cyan]Tip: Work item must be validated first[/cyan]")
            console.print(f"   apm work-item validate {work_item_id}\n")

        raise click.Abort()
