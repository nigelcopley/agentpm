"""
apm task submit-review - Submit task for review
"""

import click
from datetime import datetime
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service
import subprocess
def _print_global_test_health(console, project_root, task_id: int) -> None:
    """Best-effort global test health check; prints guidance if failures detected."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-q", "--maxfail=1"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            console.print("\n⚠️  [yellow]Full test suite has failures outside this task's scope.[/yellow]")
            console.print("   This task moved to REVIEW based on scoped tests passing.")
            console.print("\n💡 [cyan]Suggested next steps to address global failures:[/cyan]")
            console.print(f"   1) Track the issue:")
            console.print(f"      apm idea create \"Issue: Failing tests for Task {task_id}\" --type=bugfix --priority=high")
            console.print(f"   2) Analyse:")
            console.print(f"      apm idea analyze <idea_id> --comprehensive")
            console.print(f"   3) Create bugfix work item:")
            console.print(f"      apm work-item create \"Fix: Failing tests for Task {task_id}\" --type=bugfix")
            console.print(f"   4) Add tasks:")
            console.print(f"      apm task create \"Analyze Issue\" --type=analysis --effort=4")
            console.print(f"      apm task create \"Fix Tests\" --type=bugfix --effort=4")
            console.print(f"      apm task create \"Test Fix\" --type=testing --effort=3\n")
    except Exception:
        # Silent fail - guidance is best-effort
        pass



@click.command(name='submit-review')
@click.argument('task_id', type=int)
@click.option('--notes', type=str, help='Submission notes for reviewer')
@click.pass_context
def submit_review(ctx: click.Context, task_id: int, notes: str = None):
    """
    Submit task for review (transition to review status).

    Developer indicates work is complete and ready for review.
    Checks for unresolved blockers before allowing submission.

    \b
    Examples:
      apm task submit-review 5
      apm task submit-review 5 --notes "All acceptance criteria met"
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

    # Check if already in review or beyond
    if task.status.value in ['review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Task already in review or completed[/green]")
        console.print(f"   Current status: {task.status.value}\n")
        # Still surface global test health guidance for transparency
        _print_global_test_health(console, project_root, task_id)
        return

    # Store submission notes in quality metadata if provided
    if notes:
        quality_metadata = task.quality_metadata or {}
        quality_metadata['submission_notes'] = notes
        quality_metadata['submitted_at'] = str(datetime.now())
        task = TaskAdapter.update(db, task_id, quality_metadata=quality_metadata)

    # Try to transition via WorkflowService
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.REVIEW)

        console.print(f"\n📝 [cyan]Submitting Task #{task_id} for review...[/cyan]\n")

        # Check for blockers (should pass if we got here)
        from agentpm.core.database.methods import dependencies as dep_methods
        blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=True)

        console.print("✅ [green]Validation:[/green]")
        console.print(f"   ✅ No unresolved blockers")

        if notes:
            console.print(f"\n📋 [cyan]Submission Notes:[/cyan]")
            console.print(f"   {notes}")

        console.print(f"\n✅ [bold green]Task submitted for review![/bold green]")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Reviewer actions:")
        console.print(f"   apm task approve {task_id}  # If approved")
        console.print(f"   apm task request-changes {task_id} --reason \"...\"  # If changes needed\n")

        # Optional: quick full-suite health check (does not block)
        _print_global_test_health(console, project_root, task_id)

    except WorkflowError as e:
        # Display the error message (includes fix command from WorkflowService)
        console.print(f"[red]{e}[/red]")

        # Provide actionable guidance when tests are failing
        msg = str(e).lower()
        if "failing tests" in msg or "coverage" in msg:
            console.print("\n💡 [cyan]Suggested next steps to handle failing tests:[/cyan]\n")
            console.print(f"   1) Create a tracking idea:")
            console.print(f"      apm idea create \"Issue: Failing tests for Task {task_id}\" --type=bugfix --priority=high")
            console.print(f"   2) Analyse the issue:")
            console.print(f"      apm idea analyze <idea_id> --comprehensive")
            console.print(f"   3) Create a bugfix work item:")
            console.print(f"      apm work-item create \"Fix: Failing tests for Task {task_id}\" --type=bugfix")
            console.print(f"   4) Add required tasks:")
            console.print(f"      apm task create \"Analyze Issue\" --type=analysis --effort=4")
            console.print(f"      apm task create \"Fix Tests\" --type=bugfix --effort=4")
            console.print(f"      apm task create \"Test Fix\" --type=testing --effort=3\n")

        # Check for blockers to provide additional context
        from agentpm.core.database.methods import dependencies as dep_methods
        blockers = dep_methods.get_task_blockers(db, task_id, unresolved_only=True)

        if blockers:
            console.print("\n🚧 [yellow]Unresolved Blockers:[/yellow]\n")
            for blocker in blockers:
                console.print(f"   • Blocker #{blocker.id}: {blocker.blocker_description or 'Task blocker'}")

            console.print(f"\n💡 [cyan]Resolve blockers first:[/cyan]")
            console.print(f"   apm task list-blockers {task_id}")
            console.print(f"   apm task resolve-blocker <id> --notes \"...\"\n")

        raise click.Abort()
