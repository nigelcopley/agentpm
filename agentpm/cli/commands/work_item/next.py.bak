"""
Work Item Next Command - Unified Phase + Status Progression

This command intelligently progresses work items through BOTH phase and status
using the PhaseProgressionService for gate validation.

Pattern:
    1. If phase is NULL → Enter first phase for work item type
    2. If in phase → Validate current phase gate
       - Gate PASSES → Advance to next phase + update status
       - Gate FAILS → Show missing requirements (helpful, not blocking)
    3. Phase-Status Coupling → Status automatically derived from phase
    4. Type-Aware → FEATURE (6 phases), BUGFIX (I1→R1), RESEARCH (D1→P1)

Usage:
    apm work-item next <id>   # Automatic progression with gate validation
"""

import click
from rich.panel import Panel
from rich.table import Table

from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.workflow.phase_progression_service import PhaseProgressionService, PHASE_TO_STATUS
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('work_item_id', type=int)
@click.option('--force', is_flag=True, help='Skip gate validation (not recommended)')
@click.pass_context
def next(ctx: click.Context, work_item_id: int, force: bool):
    """
    Intelligently progress work item through phase and status.

    Automatically validates phase gates and advances when requirements are met.
    Shows helpful feedback about missing requirements when gates fail.

    Phase Progression (Type-Aware):
      FEATURE: D1→P1→I1→R1→O1→E1 (6 phases)
      BUGFIX: I1→R1 (2 phases)
      RESEARCH: D1→P1 (2 phases)

    Status Derived From Phase:
      NULL/D1 → draft
      P1 → ready
      I1 → active
      R1 → review
      O1 → done
      E1 → archived

    \b
    Examples:
      apm work-item next 1         # Validate gate → advance if passed
      apm work-item next 1 --force # Skip validation (use with caution)
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Load work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console.print(f"\n[red]❌ Error: Work item {work_item_id} not found[/red]\n")
        raise click.Abort()

    # Display work item info
    current_phase = work_item.phase.name if work_item.phase else "NULL"
    current_status = work_item.status.value

    console.print(f"\n[bold]Work Item #{work_item.id}:[/bold] {work_item.name}")
    console.print(f"[cyan]Type:[/cyan] {work_item.type.value}")
    console.print(f"[cyan]Current Phase:[/cyan] {current_phase}")
    console.print(f"[cyan]Current Status:[/cyan] {current_status}\n")

    # Initialize phase progression service
    progression_service = PhaseProgressionService(db)

    # Attempt to advance phase (with gate validation unless --force)
    if force:
        console.print("[yellow]⚠️  Skipping gate validation (--force)[/yellow]\n")
        # TODO: Implement force mode (direct phase update)
        console.print("[red]Force mode not yet implemented[/red]\n")
        raise click.Abort()

    # Validate and advance (normal path)
    result = progression_service.advance_to_next_phase(work_item_id)

    if not result.success:
        # Gate validation failed or error occurred
        if result.error:
            console.print(f"[red]❌ Error:[/red] {result.error}\n")
            raise click.Abort()

        # Gate failed - show helpful feedback
        _show_gate_failed_feedback(
            console,
            work_item,
            result,
            progression_service
        )
        raise click.Abort()

    # Success! Phase advanced
    _show_advancement_success(
        console,
        work_item,
        result,
        progression_service
    )


def _show_gate_failed_feedback(console, work_item, result, progression_service):
    """
    Show helpful feedback when gate validation fails.

    Displays:
        - What was being validated
        - Missing requirements with clear descriptions
        - Current metrics vs thresholds
        - Confidence score with color coding
        - Suggested fix commands
    """
    next_phase = progression_service.phase_validator.get_next_allowed_phase(work_item)
    current_phase_name = work_item.phase.name if work_item.phase else "NULL"

    console.print(f"[yellow]Checking {current_phase_name} phase gate requirements...[/yellow]\n")

    # Show current metrics vs thresholds (from metadata)
    if result.metadata:
        _show_requirements_table(console, result.metadata)

    # Show confidence score
    confidence_color = _get_confidence_color(result.confidence)
    confidence_label = _get_confidence_label(result.confidence)
    console.print(
        f"[{confidence_color}]Confidence: {result.confidence:.0%} ({confidence_label})[/{confidence_color}]\n"
    )

    # Gate failed banner
    console.print("[bold red]❌ Phase Gate: FAILED[/bold red]\n")

    # Show missing requirements
    if result.missing_requirements:
        console.print("[yellow]Missing Requirements:[/yellow]")
        for req in result.missing_requirements:
            console.print(f"  • {req}")
        console.print()

    # Show helpful fix suggestions
    console.print("[cyan]How to Fix:[/cyan]")
    _show_fix_suggestions(console, work_item, result.missing_requirements)

    # Show what will happen when gate passes
    if next_phase:
        console.print(f"\n[dim]When requirements are met:[/dim]")
        console.print(f"  Phase: {current_phase_name} → [yellow]{next_phase.name}[/yellow]")
        new_status = PHASE_TO_STATUS.get(next_phase)
        console.print(f"  Status: {work_item.status.value} → [blue]{new_status.value}[/blue]")

    console.print()


def _show_advancement_success(console, work_item, result, progression_service):
    """
    Show success feedback when phase advances.

    Displays:
        - Old phase → new phase
        - Old status → new status
        - Confidence score
        - Next phase requirements
        - Suggested next steps
    """
    old_phase = work_item.phase.name if work_item.phase else "NULL"

    console.print("[bold green]✅ Phase Gate: PASSED[/bold green]\n")

    # Show confidence
    confidence_color = _get_confidence_color(result.confidence)
    confidence_label = _get_confidence_label(result.confidence)
    console.print(
        f"[{confidence_color}]Confidence: {result.confidence:.0%} ({confidence_label})[/{confidence_color}]\n"
    )

    # Show progression
    console.print("[bold]Phase Progression:[/bold]")
    console.print(f"  {old_phase} → [yellow]{result.new_phase.name}[/yellow]")
    console.print(f"  {work_item.status.value} → [blue]{result.new_status.value}[/blue]\n")

    # Show next phase info
    next_phase = progression_service.phase_validator.get_next_allowed_phase(
        WorkItemAdapter.get(progression_service.db, work_item.id)  # Reload to get updated phase
    )

    if next_phase:
        requirements = progression_service.phase_validator.get_phase_requirements(
            result.new_phase,
            work_item.type
        )

        console.print(f"[bold cyan]Now in {result.new_phase.name} phase:[/bold cyan]")

        if requirements:
            console.print(f"[dim]{requirements.instructions}[/dim]\n")

            if requirements.required_tasks:
                console.print("[cyan]Required task types:[/cyan]")
                for task_type in requirements.required_tasks:
                    console.print(f"  • {task_type.value}")
                console.print()

        console.print("[cyan]Next Steps:[/cyan]")
        console.print(f"  apm task list --work-item-id={work_item.id}  # View tasks")

        if requirements and requirements.required_tasks:
            task_type = requirements.required_tasks[0].value
            console.print(f"  apm task create \"{task_type.title()}\" --work-item-id={work_item.id} --type={task_type}")

        console.print(f"  apm work-item next {work_item.id}  # Advance when {next_phase.name} requirements met")
    else:
        console.print(f"[green]✅ Work item has reached final phase ({result.new_phase.name})[/green]")
        console.print("[dim]No further phase advancement needed[/dim]")

    console.print()


def _show_requirements_table(console, metadata: dict):
    """Show current metrics vs thresholds in a table."""
    table = Table(show_header=True, header_style="bold cyan", show_edge=False)
    table.add_column("Requirement", style="cyan")
    table.add_column("Current", justify="right")
    table.add_column("Required", justify="right")
    table.add_column("Status", justify="center")

    # Extract metrics and thresholds
    thresholds = metadata.get('thresholds', {})

    # Business context
    if 'business_context_length' in metadata:
        current = metadata['business_context_length']
        required = thresholds.get('business_context', 50)
        status = "✅" if current >= required else "❌"
        table.add_row(
            "Business Context",
            f"{current} chars",
            f"{required}+ chars",
            status
        )

    # Acceptance criteria
    if 'acceptance_criteria_count' in metadata:
        current = metadata['acceptance_criteria_count']
        required = thresholds.get('acceptance_criteria', 3)
        status = "✅" if current >= required else "❌"
        table.add_row(
            "Acceptance Criteria",
            str(current),
            f"{required}+",
            status
        )

    # Risks
    if 'risks_count' in metadata:
        current = metadata['risks_count']
        required = thresholds.get('risks', 1)
        status = "✅" if current >= required else "❌"
        table.add_row(
            "Risks Identified",
            str(current),
            f"{required}+",
            status
        )

    # 6W confidence
    if 'six_w_confidence' in metadata and metadata['six_w_confidence'] is not None:
        current = metadata['six_w_confidence']
        required = thresholds.get('six_w', 0.70)
        status = "✅" if current >= required else "❌"
        table.add_row(
            "6W Context Quality",
            f"{current:.0%}",
            f"{required:.0%}+",
            status
        )

    if table.row_count > 0:
        console.print(table)
        console.print()


def _show_fix_suggestions(console, work_item, missing_requirements: list):
    """Show suggested fix commands based on missing requirements."""
    suggestions = []

    for req in missing_requirements:
        if "business_context" in req.lower():
            suggestions.append(
                f"  apm work-item update {work_item.id} --business-context=\"[detailed context]\""
            )
        elif "acceptance criteria" in req.lower():
            suggestions.append(
                f"  apm work-item update {work_item.id} --add-acceptance-criterion=\"[criterion]\""
            )
        elif "risk" in req.lower():
            suggestions.append(
                f"  apm work-item update {work_item.id} --add-risk=\"[risk description]\""
            )
        elif "task" in req.lower():
            suggestions.append(
                f"  apm task create \"Task Name\" --work-item-id={work_item.id} --type=implementation"
            )

    if not suggestions:
        suggestions.append(f"  apm work-item update {work_item.id} --help  # See available options")

    for suggestion in suggestions:
        console.print(suggestion)

    console.print(f"\n  # Try again after fixing requirements:")
    console.print(f"  apm work-item next {work_item.id}")


def _get_confidence_color(confidence: float) -> str:
    """Get color for confidence score."""
    if confidence < 0.50:
        return "red"
    elif confidence < 0.70:
        return "yellow"
    elif confidence < 0.85:
        return "blue"
    else:
        return "green"


def _get_confidence_label(confidence: float) -> str:
    """Get label for confidence score."""
    if confidence < 0.50:
        return "CRITICAL"
    elif confidence < 0.70:
        return "RED"
    elif confidence < 0.85:
        return "YELLOW"
    else:
        return "GREEN"
