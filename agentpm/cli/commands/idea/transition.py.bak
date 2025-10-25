"""
apm idea transition - Move idea through workflow command
"""

import click
from agentpm.core.database.enums import IdeaStatus
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.argument(
    'new_status',
    type=click.Choice(['research', 'design', 'accepted'], case_sensitive=False)
)
@click.pass_context
def transition(ctx: click.Context, idea_id: int, new_status: str):
    """
    Transition idea to new status (state machine validation).

    Valid transitions follow the idea lifecycle:
      idea → research → design → accepted → converted (via convert command)
      any state → rejected (via reject command)

    \b
    Examples:
      # Start research phase
      apm idea transition 5 research

      # Progress to design
      apm idea transition 5 design

      # Accept idea (ready for conversion)
      apm idea transition 5 accepted

    Note: Use 'apm idea reject' for rejection and 'apm idea convert' for conversion.
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get idea
    idea = IdeaAdapter.get(db, idea_id)

    if not idea:
        console.print(f"\n[red]❌ Error: Idea {idea_id} not found[/red]\n")
        raise click.Abort()

    # Convert status string to enum
    target_status = IdeaStatus(new_status)

    # Transition with state machine validation
    try:
        updated_idea = IdeaAdapter.transition(db, idea_id, target_status)
    except ValueError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")

        # Show allowed transitions
        allowed = idea.get_allowed_transitions()
        if allowed:
            console.print(f"\n[yellow]Allowed transitions from '{idea.status.value}':[/yellow]")
            for status in allowed:
                console.print(f"   • {status.value}")
        else:
            console.print(f"\n[yellow]Idea is in terminal state '{idea.status.value}' (no transitions allowed)[/yellow]")

        console.print()
        raise click.Abort()

    # Success message
    status_emoji = {
        "research": "🔬",
        "design": "🎨",
        "accepted": "✅"
    }.get(new_status, "📋")

    console.print(f"\n✅ [green]Idea transitioned:[/green] {updated_idea.title}")
    console.print(f"   Status: [yellow]{idea.status.value}[/yellow] → [green]{updated_idea.status.value}[/green] {status_emoji}")

    # Show next steps based on new status
    console.print(f"\n📚 [cyan]Next actions:[/cyan]")

    if updated_idea.status == IdeaStatus.RESEARCH:
        console.print(f"   • Conduct research and gather requirements")
        console.print(f"   • apm idea update {idea_id} --description=\"Research findings...\"")
        console.print(f"   • apm idea transition {idea_id} design  # Move to design phase")

    elif updated_idea.status == IdeaStatus.DESIGN:
        console.print(f"   • Create design specifications")
        console.print(f"   • apm idea update {idea_id} --description=\"Design approach...\"")
        console.print(f"   • apm idea transition {idea_id} accepted  # Accept for implementation")

    elif updated_idea.status == IdeaStatus.ACTIVE:
        console.print(f"   • Ready to convert to work item!")
        console.print(f"   • apm idea convert {idea_id} --type=feature")
        console.print(f"   • apm idea convert {idea_id} --type=bugfix")

    console.print()
