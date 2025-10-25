"""
apm work-item phase-status - Show current phase and gate requirements
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.workflow.phase_validator import PhaseValidator
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command('phase-status')
@click.argument('work_item_id', type=int)
@click.pass_context
def phase_status(ctx: click.Context, work_item_id: int):
    """
    Show current phase status and gate requirements.

    Displays:
    - Current phase and status
    - Next allowed phase
    - Phase requirements and completion status
    - Phase sequence for work item type

    \b
    Example:
      apm work-item phase-status 81
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        raise click.Abort()

    # Initialize phase validator
    validator = PhaseValidator()

    # Display work item info
    console.print(f"\n[bold]Work Item #{work_item.id}:[/bold] {work_item.name}")
    console.print(f"Type: [cyan]{work_item.type.value}[/cyan]")

    # Current phase and status
    current_phase = work_item.phase.name if work_item.phase else "NULL (not started)"
    console.print(f"Current Phase: [yellow]{current_phase}[/yellow]")
    console.print(f"Current Status: [blue]{work_item.status.value}[/blue]")

    # Next allowed phase
    next_phase = validator.get_next_allowed_phase(work_item)
    if next_phase:
        console.print(f"Next Phase: [green]{next_phase.name}[/green]")
    else:
        console.print("Next Phase: [dim]None (at final phase)[/dim]")

    # Phase sequence for this work item type
    allowed_phases = validator.get_allowed_phases(work_item.type)
    if allowed_phases:
        console.print("\n[bold]Phase Sequence for {type}:[/bold]".format(type=work_item.type.value.upper()))

        phase_progress = []
        for phase in allowed_phases:
            if work_item.phase == phase:
                phase_progress.append(f"→ [yellow bold]{phase.name}[/yellow bold] (current)")
            elif work_item.phase and allowed_phases.index(phase) < allowed_phases.index(work_item.phase):
                phase_progress.append(f"  [green]✓ {phase.name}[/green] (completed)")
            else:
                phase_progress.append(f"  [dim]{phase.name}[/dim] (future)")

        for progress_line in phase_progress:
            console.print(progress_line)

    # Phase requirements (if in a phase)
    if work_item.phase:
        requirements = validator.get_phase_requirements(work_item.phase, work_item.type)

        if requirements:
            console.print("\n[bold]Current Phase Requirements:[/bold]")
            console.print(f"[dim]{requirements.instructions}[/dim]\n")

            # Required task types
            if requirements.required_tasks:
                console.print("[cyan]Required Task Types:[/cyan]")
                for task_type in requirements.required_tasks:
                    console.print(f"  • {task_type.value}")

            # Completion criteria
            if requirements.completion_criteria:
                console.print("\n[cyan]Completion Criteria:[/cyan]")
                for criterion in requirements.completion_criteria:
                    status_icon = "⚠️" if criterion.required else "ℹ️"
                    evidence = " (evidence required)" if criterion.evidence_required else ""
                    console.print(f"  {status_icon} {criterion.name}{evidence}")
                    console.print(f"     [dim]{criterion.description}[/dim]")

            # Estimated duration
            if requirements.estimated_duration_hours:
                console.print(f"\n[cyan]Estimated Duration:[/cyan] {requirements.estimated_duration_hours}h")

    # Next phase requirements
    if next_phase:
        next_requirements = validator.get_phase_requirements(next_phase, work_item.type)

        if next_requirements:
            console.print(f"\n[bold]Next Phase ({next_phase.name}) Requirements:[/bold]")
            console.print(f"[dim]{next_requirements.instructions}[/dim]")

    # Next steps
    console.print("\n[bold cyan]Available Actions:[/bold cyan]")
    if next_phase:
        console.print(f"  apm work-item phase-validate {work_item_id}  # Check if ready to advance")
        console.print(f"  apm work-item next {work_item_id}   # Advance to next phase")
    else:
        console.print("  [dim]Work item at final phase - no further advancement[/dim]")

    console.print(f"  apm work-item show {work_item_id}              # View full details")
    console.print()
