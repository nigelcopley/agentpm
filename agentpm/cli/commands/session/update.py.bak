"""
apm session update - Update current session metadata
"""

import click

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option('--summary', help='Session summary (what was accomplished)')
@click.option('--priority', help='Next session priority (main focus area)')
@click.option('--current-status', help='Current project status (STATUS.md equivalent) - REQUIRED for session end')
@click.option('--next-session', help='Next session context and priorities - REQUIRED for session end')
@click.pass_context
def update(ctx: click.Context, summary: str, priority: str, current_status: str, next_session: str):
    """
    Update current session metadata.

    Add summary and set next session priority.

    \b
    Examples:
      apm session update --summary "Implemented session CLI commands"
      apm session update --priority "Complete WI-35 hook integration"
      apm session update --summary "..." --priority "..."
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current session
    session = SessionAdapter.get_current(db)

    if not session:
        console.print("\n❌ [red]No active session[/red]\n")
        raise click.Abort()

    # Update fields
    updates = {}

    if summary:
        session.metadata.session_summary = summary
        updates['summary'] = True

    if priority:
        session.metadata.next_session_priority = priority
        updates['priority'] = True

    if current_status:
        session.metadata.current_status = current_status
        updates['current_status'] = True

    if next_session:
        session.metadata.next_session = next_session
        updates['next_session'] = True

    if not updates:
        console.print("\n⚠️  [yellow]No updates specified[/yellow]\n")
        console.print("💡 [cyan]Provide --summary, --priority, --current-status, or --next-session[/cyan]\n")
        raise click.Abort()

    try:
        # Save to database
        updated_session = SessionAdapter.update(db, session)

        console.print("\n✅ [green]Session updated![/green]\n")

        if summary:
            console.print(f"[bold]Summary:[/bold] {summary}")

        if priority:
            console.print(f"[bold]Next Priority:[/bold] {priority}")

        if current_status:
            console.print(f"[bold]Current Status:[/bold] {current_status[:100]}...")

        if next_session:
            console.print(f"[bold]Next Session:[/bold] {next_session[:100]}...")

        console.print(f"\n📊 [cyan]Session {updated_session.session_id[:8]}... updated[/cyan]\n")

    except Exception as e:
        console.print(f"\n❌ [red]Update failed:[/red] {e}\n")
        raise click.Abort()
