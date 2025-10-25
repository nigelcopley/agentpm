"""
apm session add-next-step - Add action item for next session
"""

import click

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command(name='add-next-step')
@click.argument('step')
@click.pass_context
def add_next_step(ctx: click.Context, step: str):
    """
    Add next step for upcoming session.

    Records action items to continue work in next session.

    \b
    Examples:
      apm session add-next-step "Integrate SessionEnd hook validation"
      apm session add-next-step "Test automatic metadata capture"
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current session
    session = SessionAdapter.get_current(db)

    if not session:
        console.print("\n❌ [red]No active session[/red]\n")
        raise click.Abort()

    # Add next step
    if step not in session.metadata.next_steps:
        session.metadata.next_steps.append(step)

    try:
        updated_session = SessionAdapter.update(db, session)

        console.print(f"\n✅ [green]Next step added![/green]\n")
        console.print(f"[bold]Step:[/bold] {step}")

        total_steps = len(updated_session.metadata.next_steps)
        console.print(f"\n📋 [cyan]Total next steps: {total_steps}[/cyan]")

        if total_steps > 1:
            console.print(f"\n[dim]All next steps:[/dim]")
            for i, s in enumerate(updated_session.metadata.next_steps, 1):
                console.print(f"  {i}. {s}")

        console.print()

    except Exception as e:
        console.print(f"\n❌ [red]Failed to add next step:[/red] {e}\n")
        raise click.Abort()
