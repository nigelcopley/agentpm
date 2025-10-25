"""
apm idea convert - Convert idea to work item command
"""

import click
from agentpm.core.database.enums import WorkItemType
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.option(
    '--type', 'wi_type',
    type=click.Choice([
        'feature',
        'bugfix',
        'research',
        'planning',
        'refactoring',
        'infrastructure',
        'enhancement'
    ], case_sensitive=False),
    default='feature',
    help='Work item type (default: feature)'
)
@click.option(
    '--priority', '-p',
    type=click.IntRange(1, 5),
    default=3,
    help='Priority (1=highest, 5=lowest, default=3)'
)
@click.option(
    '--business-context',
    help='Business justification and impact'
)
@click.option(
    '--start-phase',
    type=click.Choice([
        'D1_DISCOVERY',
        'P1_PLAN', 
        'I1_IMPLEMENTATION'
    ], case_sensitive=False),
    help='Phase to start work item in (auto-determined from idea status if not specified)'
)
@click.pass_context
def convert(ctx: click.Context, idea_id: int, wi_type: str, priority: int,
            business_context: str, start_phase: str):
    """
    Convert accepted idea to work item with full traceability and phase alignment.

    Only ideas in 'accepted' status can be converted. Conversion creates
    bidirectional links between idea and work item for traceability.

    Process:
    1. Validate idea is in 'accepted' state
    2. Create work item with idea content and enhanced metadata
    3. Auto-set work item phase based on idea status (or use --start-phase)
    4. Copy idea metadata (tags, source, votes) to work item
    5. Link work_item.originated_from_idea_id → idea.id
    6. Transition idea to 'converted' status
    7. Set idea.converted_to_work_item_id → work_item.id

    Phase Alignment:
      - idea/research → D1_DISCOVERY (discovery phase)
      - design/accepted → P1_PLAN (planning phase)
      - Use --start-phase to override auto-detection

    \b
    Examples:
      # Convert to feature (default, auto-phase)
      apm idea convert 5

      # Convert to bugfix with priority
      apm idea convert 12 --type=bugfix --priority=1

      # Convert with business context
      apm idea convert 8 --type=feature \\
        --priority=2 \\
        --business-context "Critical customer request from top 5 accounts"

      # Skip discovery phase (idea research/design already complete)
      apm idea convert 15 --start-phase=P1_PLAN

      # Start directly in implementation (idea fully planned)
      apm idea convert 20 --start-phase=I1_IMPLEMENTATION
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Convert idea to work item
    try:
        converted_idea, work_item = IdeaAdapter.convert_to_work_item(
            db,
            idea_id=idea_id,
            work_item_type=WorkItemType(wi_type),
            business_context=business_context,
            start_phase=start_phase
        )
    except ValueError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")

        # Show how to accept idea
        console.print(f"\n[yellow]💡 Hint:[/yellow]")
        console.print(f"   Ideas must be 'accepted' before conversion.")
        console.print(f"   Current workflow:")
        console.print(f"   1. apm idea transition {idea_id} research")
        console.print(f"   2. apm idea transition {idea_id} design")
        console.print(f"   3. apm idea transition {idea_id} accepted")
        console.print(f"   4. apm idea convert {idea_id}\n")
        raise click.Abort()

    # Success message
    console.print(f"\n✅ [green]Idea converted to work item![/green]")
    console.print()

    # Phase alignment information
    from agentpm.core.database.enums import IdeaStatus
    aligned_phase = IdeaStatus.get_aligned_phase(converted_idea.status)
    console.print(f"[cyan]🔄 Phase Alignment:[/cyan]")
    console.print(f"   Idea {converted_idea.status.value} → Work Item {work_item.phase.value if work_item.phase else 'DRAFT'}")
    if start_phase:
        console.print(f"   [dim]Override: Started in {start_phase} phase[/dim]")
    console.print()

    # Idea details
    console.print(f"[yellow]Idea #{converted_idea.id}:[/yellow]")
    console.print(f"   Title: {converted_idea.title}")
    console.print(f"   Status: [green bold]{converted_idea.status.value}[/green bold]")
    console.print(f"   Converted: {converted_idea.converted_at.strftime('%Y-%m-%d %H:%M') if converted_idea.converted_at else 'N/A'}")
    console.print()

    # Work item details
    console.print(f"[green]Work Item #{work_item.id}:[/green]")
    console.print(f"   Name: {work_item.name}")
    console.print(f"   Type: {work_item.type.value}")
    console.print(f"   Status: {work_item.status.value}")
    console.print(f"   Phase: {work_item.phase.value if work_item.phase else 'None'}")
    console.print(f"   Priority: {work_item.priority}")

    if work_item.business_context:
        console.print(f"   Business Context: ✓")

    console.print()

    # Traceability
    console.print(f"[cyan]🔗 Traceability Links:[/cyan]")
    console.print(f"   Idea #{converted_idea.id} → Work Item #{work_item.id}")
    console.print(f"   Work Item #{work_item.id} ← Idea #{converted_idea.id}")
    console.print()

    # Next steps with phase progression
    console.print(f"📚 [cyan]Next steps:[/cyan]")
    console.print(f"   • apm work-item show {work_item.id}")
    console.print(f"   • apm work-item phase-status {work_item.id}  # Check phase requirements")
    
    # Show phase-specific next steps
    if work_item.phase:
        phase_name = work_item.phase.value
        if phase_name == "D1_DISCOVERY":
            console.print(f"   • [dim]Current phase: Discovery - research and requirements gathering[/dim]")
        elif phase_name == "P1_PLAN":
            console.print(f"   • [dim]Current phase: Planning - design and task breakdown[/dim]")
        elif phase_name == "I1_IMPLEMENTATION":
            console.print(f"   • [dim]Current phase: Implementation - build and test[/dim]")

    # Show recommended tasks for work item type
    console.print(f"\n   [yellow]Recommended tasks for {work_item.type.value.upper()}:[/yellow]")
    if work_item.type == WorkItemType.FEATURE:
        console.print(f"   • DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION")
    elif work_item.type == WorkItemType.BUGFIX:
        console.print(f"   • ANALYSIS, BUGFIX, TESTING")
    elif work_item.type == WorkItemType.RESEARCH:
        console.print(f"   • ANALYSIS, DOCUMENTATION")
    elif work_item.type == WorkItemType.ENHANCEMENT:
        console.print(f"   • DESIGN, IMPLEMENTATION, TESTING")

    console.print()
