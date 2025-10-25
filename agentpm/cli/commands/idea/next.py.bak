"""
Idea Next Command - Automatic State Progression

This command automatically transitions an idea to its next logical state
in the idea lifecycle.
"""

import click
from agentpm.core.database.enums import IdeaStatus
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_workflow_service, get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.pass_context
def next(ctx: click.Context, idea_id: int):
    """
    Automatically transition idea to next logical state.
    
    Uses the idea lifecycle to determine the next state:
    idea → research → design → accepted → converted
    
    Terminal states (rejected, converted) do not have automatic next states.
    
    \b
    Examples:
      apm idea next 5
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)
    
    # Get idea
    idea = IdeaAdapter.get(db, idea_id)
    
    if not idea:
        console.print(f"\n[red]❌ Error: Idea {idea_id} not found[/red]\n")
        raise click.Abort()
    
    # Determine next state based on current state
    current_status = idea.status
    next_status = _get_next_state(current_status)
    
    if not next_status:
        console.print(f"\n[red]❌ Error: Idea {idea_id} is in '{current_status.value}' state which has no automatic next state[/red]")
        console.print(f"   Terminal states (rejected, converted) require manual action\n")
        raise click.Abort()
    
    # Try to transition via database method
    try:
        updated_idea = IdeaAdapter.transition(db, idea_id, next_status)
        
        console.print(f"\n✅ [green]Idea progressed:[/green] {updated_idea.title}")
        console.print(f"   Status: {current_status.value} → {updated_idea.status.value}")
        
        # Show next steps based on new state
        _show_next_steps(console, updated_idea.status, idea_id)
        
    except Exception as e:
        # Display the error message
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise click.Abort()


def _get_next_state(current_status: IdeaStatus) -> IdeaStatus | None:
    """
    Get the next logical state in the idea lifecycle.
    
    Returns None for terminal states that don't have automatic progression.
    """
    # Idea lifecycle progression
    progression = {
        IdeaStatus.IDEA: IdeaStatus.RESEARCH,
        IdeaStatus.RESEARCH: IdeaStatus.DESIGN,
        IdeaStatus.DESIGN: IdeaStatus.ACTIVE,  # ACTIVE = "accepted"
        IdeaStatus.ACTIVE: IdeaStatus.CONVERTED,
    }
    
    return progression.get(current_status)


def _show_next_steps(console, new_status: IdeaStatus, idea_id: int):
    """Show helpful next steps based on the new idea status."""
    
    if new_status == IdeaStatus.RESEARCH:
        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Idea is in research phase")
        console.print(f"   apm idea next {idea_id}  # Move to design phase")
        console.print(f"   apm idea show {idea_id}  # View idea details\n")
        
    elif new_status == IdeaStatus.DESIGN:
        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Idea is in design phase")
        console.print(f"   apm idea next {idea_id}  # Accept idea")
        console.print(f"   apm idea show {idea_id}  # View idea details\n")
        
    elif new_status == IdeaStatus.ACTIVE:  # ACTIVE = "accepted"
        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   # Idea is accepted and ready for conversion")
        console.print(f"   apm idea convert {idea_id}  # Convert to work item")
        console.print(f"   apm idea show {idea_id}  # View idea details\n")
        
    elif new_status == IdeaStatus.CONVERTED:
        console.print(f"\n📚 [cyan]Idea converted successfully![/cyan]")
        console.print(f"   # Idea has been converted to a work item")
        console.print(f"   apm work-item list  # View work items\n")
