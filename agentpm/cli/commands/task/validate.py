"""
apm task validate - Validate task and transition to validated status
"""

import click
from agentpm.core.database.enums import TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service
# No additional formatters needed - using rich console directly


@click.command()
@click.argument('task_id', type=int)
@click.pass_context
def validate(ctx: click.Context, task_id: int):
    """
    Validate task and transition to validated status.

    Checks all validation requirements and transitions if all pass:
    - Description ≥50 characters
    - Effort hours set
    - Time-boxing limits (IMPLEMENTATION ≤4h, etc.)
    - Type-specific quality metadata

    \b
    Example:
      apm task validate 5
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

    # Check if already validated or beyond
    if task.status.value in ['validated', 'accepted', 'in_progress', 'blocked', 'review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Task already validated[/green]")
        console.print(f"   Current status: {task.status.value}\n")
        return

    # Try to transition via WorkflowService (enforces all quality gates)
    try:
        updated_task = workflow.transition_task(task_id, TaskStatus.READY)

        console.print(f"\n🔍 [cyan]Validating Task #{task_id}...[/cyan]\n")

        # Show validation checklist (all passed if we got here)
        console.print("✅ [green]Basic Requirements:[/green]")
        console.print(f"   ✅ Description: {len(task.description or '')} characters (≥50 required)")
        console.print(f"   ✅ Effort: {task.effort_hours}h")
        console.print(f"   ✅ Type: {task.type.value}")

        # Show time-boxing validation
        from agentpm.core.workflow.type_validators import TASK_TYPE_MAX_HOURS
        max_hours = TASK_TYPE_MAX_HOURS.get(task.type)
        if max_hours:
            console.print(f"\n✅ [green]Time-Boxing:[/green]")
            console.print(f"   ✅ {task.effort_hours}h ≤ {max_hours}h limit ({task.type.value})")

        # Show quality metadata validation (if applicable)
        if task.quality_metadata:
            console.print(f"\n✅ [green]Quality Metadata:[/green]")
            if task.type.value == 'implementation' and 'acceptance_criteria' in task.quality_metadata:
                criteria_count = len(task.quality_metadata['acceptance_criteria'])
                console.print(f"   ✅ Acceptance criteria: {criteria_count} criteria defined")
            elif task.type.value == 'bugfix' and 'reproduction_steps' in task.quality_metadata:
                console.print(f"   ✅ Reproduction steps: documented")
            elif task.type.value == 'testing' and 'coverage_percent' in task.quality_metadata:
                coverage = task.quality_metadata['coverage_percent']
                console.print(f"   ✅ Target coverage: {coverage}%")

        console.print(f"\n✅ [bold green]Task validated successfully![/bold green]")
        console.print(f"   Status: {task.status.value} → {updated_task.status.value}")

        console.print(f"\n📚 [cyan]Next step:[/cyan]")
        console.print(f"   apm task accept {task_id} --agent <agent>  # Accept and assign\n")

    except WorkflowError as e:
        # Display the error message
        console.print(f"\n❌ [red]Validation failed:[/red] {e}\n")

        # Show helpful checklist of what's missing
        console.print("📋 [yellow]Validation Requirements:[/yellow]\n")

        # Check description
        desc_len = len(task.description or '')
        if desc_len < 50:
            console.print(f"   ❌ Description: {desc_len} characters (need ≥50)")
        else:
            console.print(f"   ✅ Description: {desc_len} characters")

        # Check effort
        if task.effort_hours is None:
            console.print(f"   ❌ Effort: Not set")
        else:
            console.print(f"   ✅ Effort: {task.effort_hours}h")

            # Check time-boxing
            from agentpm.core.workflow.type_validators import TASK_TYPE_MAX_HOURS
            max_hours = TASK_TYPE_MAX_HOURS.get(task.type)
            if max_hours and task.effort_hours > max_hours:
                console.print(f"   ❌ Time-boxing: {task.effort_hours}h exceeds {max_hours}h limit ({task.type.value})")
            elif max_hours:
                console.print(f"   ✅ Time-boxing: {task.effort_hours}h ≤ {max_hours}h ({task.type.value})")

        # Check type-specific metadata
        if task.type.value == 'implementation':
            if not task.quality_metadata or 'acceptance_criteria' not in task.quality_metadata:
                console.print(f"   ❌ Acceptance criteria: Not defined (IMPLEMENTATION tasks require this)")
            else:
                criteria_count = len(task.quality_metadata['acceptance_criteria'])
                if criteria_count > 0:
                    console.print(f"   ✅ Acceptance criteria: {criteria_count} defined")
                else:
                    console.print(f"   ❌ Acceptance criteria: Empty (need ≥1)")

        elif task.type.value == 'bugfix':
            if not task.quality_metadata or 'reproduction_steps' not in task.quality_metadata:
                console.print(f"   ❌ Reproduction steps: Not defined (BUGFIX tasks require this)")
            else:
                console.print(f"   ✅ Reproduction steps: Documented")

        console.print(f"\n💡 [cyan]Fix the issues above, then run:[/cyan]")
        console.print(f"   apm task validate {task_id}\n")

        raise click.Abort()
