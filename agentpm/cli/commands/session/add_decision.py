"""
apm session add-decision - Add decision to current session
"""

from datetime import datetime
import click

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command(name='add-decision')
@click.argument('decision')
@click.option('--rationale', help='Rationale for the decision')
@click.pass_context
def add_decision(ctx: click.Context, decision: str, rationale: str):
    """
    Add a key decision to the current session.

    Records important decisions made during the session for
    future reference and searchability.

    \b
    Examples:
      apm session add-decision "Use Pydantic for models"
      apm session add-decision "Use Pydantic" --rationale "Type safety"
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current session
    session = SessionAdapter.get_current(db)

    if not session:
        console.print("\n❌ [red]No active session[/red]\n")
        console.print("💡 [yellow]Start a session first:[/yellow]")
        console.print("   Sessions are created automatically by hooks\n")
        console.print("   Or manually: apm session start\n")
        raise click.Abort()

    # Create decision record
    decision_record = {
        'decision': decision,
        'rationale': rationale or '',
        'timestamp': datetime.now().isoformat()
    }

    try:
        # Update current session
        updated_session = SessionAdapter.update_current(
            db,
            decision=decision_record
        )

        console.print(f"\n✅ [green]Decision added to session[/green]\n")
        console.print(f"[bold]Decision:[/bold] {decision}")
        if rationale:
            console.print(f"[bold]Rationale:[/bold] {rationale}")
        console.print(f"[bold]Timestamp:[/bold] {decision_record['timestamp']}")

        total_decisions = len(updated_session.metadata.decisions_made)
        console.print(f"\n📊 [cyan]Total decisions in session: {total_decisions}[/cyan]")

        console.print(f"\n💡 [yellow]Search decisions later with:[/yellow]")
        console.print(f"   apm session history --search \"{decision.split()[0]}\"\n")

    except Exception as e:
        console.print(f"\n❌ [red]Failed to add decision:[/red] {e}\n")
        raise click.Abort()
