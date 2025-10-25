"""
apm session end - End the current active session
"""

from typing import Optional
import click

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option('--session-id', help='Specific session ID to end (optional, uses active if not provided)')
@click.option('--reason', help='Exit reason (e.g., "Complete", "Break", "Blocked")')
@click.pass_context
def end(ctx: click.Context, session_id: Optional[str], reason: Optional[str]):
    """
    End the current active session.

    Marks the session as complete, calculates duration, and updates
    the database record. If no session ID is provided, ends the currently
    active session.

    \b
    Examples:
      apm session end                                # End active session
      apm session end --reason "Complete"            # With exit reason
      apm session end --session-id abc-123           # End specific session
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # If no session ID provided, get active session
    if not session_id:
        active_sessions = SessionAdapter.get_active_sessions(db, project_id)

        if not active_sessions:
            console.print("\n❌ [red]No active session found[/red]\n")
            console.print("💡 [yellow]Start a session first:[/yellow]")
            console.print("   apm session start\n")
            raise click.Abort()

        if len(active_sessions) > 1:
            console.print("\n⚠️  [yellow]Multiple active sessions found:[/yellow]\n")
            for session in active_sessions:
                console.print(f"   {session.session_id} - Started {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            console.print("\n💡 [yellow]Specify which session to end:[/yellow]")
            console.print("   apm session end --session-id <id>\n")
            raise click.Abort()

        session_id = active_sessions[0].session_id

    # Get session to verify it exists
    session = SessionAdapter.get(db, session_id)
    if not session:
        console.print(f"\n❌ [red]Session not found:[/red] {session_id}\n")
        raise click.Abort()

    if not session.is_active:
        console.print(f"\n⚠️  [yellow]Session already ended[/yellow]\n")
        console.print(f"   Ended: {session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else 'Unknown'}")
        console.print(f"   Duration: {session.duration_minutes or 0} minutes\n")
        raise click.Abort()

    try:
        # End session
        updated_session = SessionAdapter.end(
            db,
            session_id=session_id,
            exit_reason=reason
        )

        console.print("\n✅ [green]Session ended successfully![/green]\n")
        console.print(f"[bold]Session ID:[/bold] {updated_session.session_id}")
        console.print(f"[bold]Started:[/bold] {updated_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"[bold]Ended:[/bold] {updated_session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"[bold]Duration:[/bold] {updated_session.duration_minutes} minutes")

        if reason:
            console.print(f"[bold]Exit Reason:[/bold] {reason}")

        console.print(f"\n📊 [cyan]Session statistics saved[/cyan]")
        console.print(f"\n💡 [yellow]View session details:[/yellow]")
        console.print(f"   apm session show {updated_session.session_id}\n")

    except ValueError as e:
        console.print(f"\n❌ [red]Failed to end session:[/red] {e}\n")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error:[/red] {e}\n")
        raise click.Abort()
