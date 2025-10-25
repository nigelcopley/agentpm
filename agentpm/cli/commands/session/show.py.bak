"""
apm session show - Display session details
"""

import json
import click
from rich.table import Table
from rich.panel import Panel
from rich import box

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('session_id', required=False)
@click.pass_context
def show(ctx: click.Context, session_id: str):
    """
    Show complete session details.

    Displays session information including metadata, timing,
    work items touched, tasks completed, and decisions made.

    If no session ID provided, shows current active session.

    \b
    Examples:
      apm session show                               # Show current session
      apm session show abc-123-def-456               # Show specific session
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get session (current or specific)
    if not session_id:
        session = SessionAdapter.get_current(db)
        if not session:
            console.print("\n⚠️  [yellow]No active session[/yellow]\n")
            console.print("💡 [cyan]View past sessions with:[/cyan]")
            console.print("   apm session history\n")
            raise click.Abort()
    else:
        session = SessionAdapter.get(db, session_id)

    if not session:
        console.print(f"\n❌ [red]Session not found:[/red] {session_id}\n")
        console.print("💡 [yellow]List sessions with:[/yellow]")
        console.print("   apm session history\n")
        raise click.Abort()

    # Display session details
    console.print(f"\n📊 [bold cyan]Session Details[/bold cyan]\n")

    # Basic info table
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")

    info_table.add_row("Session ID", session.session_id)
    info_table.add_row("Tool", session.tool_name.value)
    info_table.add_row("LLM Model", session.llm_model or "Unknown")
    info_table.add_row("Tool Version", session.tool_version or "Unknown")
    info_table.add_row("Session Type", session.session_type.value)
    info_table.add_row("Started", session.start_time.strftime('%Y-%m-%d %H:%M:%S'))

    if session.end_time:
        info_table.add_row("Ended", session.end_time.strftime('%Y-%m-%d %H:%M:%S'))
        info_table.add_row("Duration", f"{session.duration_minutes} minutes")
        info_table.add_row("Status", "✅ Completed")
    else:
        info_table.add_row("Status", "🔄 Active")

    if session.exit_reason:
        info_table.add_row("Exit Reason", session.exit_reason)

    if session.developer_name:
        info_table.add_row("Developer", session.developer_name)

    if session.developer_email:
        info_table.add_row("Email", session.developer_email)

    console.print(info_table)

    # Metadata section
    if session.metadata:
        console.print(f"\n[bold]Session Metadata:[/bold]\n")

        # Work items touched
        if session.metadata.work_items_touched:
            console.print(f"[cyan]Work Items Touched ({len(session.metadata.work_items_touched)}):[/cyan]")
            for wi_id in session.metadata.work_items_touched:
                console.print(f"  • Work Item #{wi_id}")

        # Tasks completed
        if session.metadata.tasks_completed:
            console.print(f"\n[cyan]Tasks Completed ({len(session.metadata.tasks_completed)}):[/cyan]")
            for task_id in session.metadata.tasks_completed:
                console.print(f"  • Task #{task_id}")

        # Git commits
        if session.metadata.git_commits:
            console.print(f"\n[cyan]Git Commits ({len(session.metadata.git_commits)}):[/cyan]")
            for commit in session.metadata.git_commits:
                console.print(f"  • {commit}")

        # Decisions made
        if session.metadata.decisions_made:
            console.print(f"\n[cyan]Key Decisions ({len(session.metadata.decisions_made)}):[/cyan]")
            for decision in session.metadata.decisions_made:
                decision_text = decision.get('decision', 'No description')
                rationale = decision.get('rationale', '')
                console.print(f"  • {decision_text}")
                if rationale:
                    console.print(f"    [dim]Rationale: {rationale}[/dim]")

        # Blockers resolved
        if session.metadata.blockers_resolved:
            console.print(f"\n[cyan]Blockers Resolved ({len(session.metadata.blockers_resolved)}):[/cyan]")
            for blocker_id in session.metadata.blockers_resolved:
                console.print(f"  • Blocker #{blocker_id}")

        # Additional metadata (other fields)
        additional = {}
        for key, value in session.metadata.model_dump().items():
            if key not in ['work_items_touched', 'tasks_completed', 'git_commits',
                          'decisions_made', 'blockers_resolved'] and value:
                additional[key] = value

        if additional:
            console.print(f"\n[cyan]Additional Metadata:[/cyan]")
            for key, value in additional.items():
                console.print(f"  {key}: {value}")

    console.print()
