"""
apm work-item phase-validate - Validate if work item can advance to next phase (dry-run)
"""

import click
from rich.console import Console

from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.workflow.phase_validator import PhaseValidator
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command('phase-validate')
@click.argument('work_item_id', type=int)
@click.pass_context
def phase_validate(ctx: click.Context, work_item_id: int):
    """
    Validate if work item is ready to advance to next phase (dry-run).

    Performs phase gate validation without actually advancing the phase.
    Shows missing requirements if validation fails.

    \b
    Example:
      apm work-item phase-validate 81
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
    console.print(f"\n[bold]Validating Work Item #{work_item.id}:[/bold] {work_item.name}")

    current_phase = work_item.phase.name if work_item.phase else "NULL"
    console.print(f"Current Phase: [yellow]{current_phase}[/yellow]")
    console.print(f"Current Status: [blue]{work_item.status.value}[/blue]\n")

    # Get next allowed phase
    next_phase = validator.get_next_allowed_phase(work_item)

    if not next_phase:
        console.print("✅ [green]Work item is at final phase - no further advancement needed[/green]\n")
        return

    console.print(f"[cyan]Validating transition:[/cyan] {current_phase} → {next_phase.name}\n")

    # Validate transition
    validation_result = validator.validate_transition(work_item, next_phase)

    if validation_result.is_valid:
        # Validation passed
        console.print("✅ [bold green]Phase gate validation PASSED[/bold green]")
        console.print(f"\n[cyan]Work item is ready to advance to {next_phase.name} phase[/cyan]")
        console.print(f"\nTo advance:")
        console.print(f"  apm work-item next {work_item_id}\n")

    else:
        # Validation failed
        console.print("❌ [bold red]Phase gate validation FAILED[/bold red]")
        console.print(f"\n[red]Cannot advance to {next_phase.name} phase[/red]")

        # Show error message
        if validation_result.error_message:
            console.print(f"\n[yellow]Reason:[/yellow]")
            console.print(f"{validation_result.error_message}")

        # Show missing requirements
        if validation_result.missing_requirements:
            console.print(f"\n[yellow]Missing Requirements:[/yellow]")
            for requirement in validation_result.missing_requirements:
                console.print(f"  • {requirement}")

        # Show helpful next steps
        console.print(f"\n[cyan]Next Steps:[/cyan]")
        console.print(f"  1. Review phase requirements:")
        console.print(f"     apm work-item phase-status {work_item_id}")
        console.print(f"  2. Complete missing requirements")
        console.print(f"  3. Re-validate:")
        console.print(f"     apm work-item phase-validate {work_item_id}\n")

        raise click.Abort()
