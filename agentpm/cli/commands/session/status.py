"""
apm session status - Show current active session
"""

import click
from rich.table import Table
from rich import box

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.pass_context
def status(ctx: click.Context):
    """
    Show current active session status.

    Displays the session that is currently being tracked,
    including work items touched, tasks completed, and metadata.

    \b
    Examples:
      apm session status                             # Show current session
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current session
    session = SessionAdapter.get_current(db)

    if not session:
        console.print("\n⚠️  [yellow]No active session[/yellow]\n")
        console.print("💡 [cyan]Session tracking is automatic via hooks[/cyan]")
        console.print("   or manually start with: apm session start\n")
        return

    # Display current session
    console.print(f"\n🔄 [bold cyan]Current Active Session[/bold cyan]\n")

    # Basic info table
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")

    info_table.add_row("Session ID", session.session_id[:16] + "...")
    info_table.add_row("Type", session.session_type.value)
    info_table.add_row("Started", session.start_time.strftime('%Y-%m-%d %H:%M:%S'))

    # Calculate current duration
    from datetime import datetime
    current_duration = int((datetime.now() - session.start_time).total_seconds() / 60)
    info_table.add_row("Duration", f"{current_duration} minutes")

    if session.developer_name:
        info_table.add_row("Developer", session.developer_name)

    console.print(info_table)

    # Activity summary
    console.print(f"\n[bold]Activity Summary:[/bold]")
    console.print(f"  Work Items Touched: {len(session.metadata.work_items_touched)}")
    console.print(f"  Tasks Completed: {len(session.metadata.tasks_completed)}")
    console.print(f"  Git Commits: {len(session.metadata.git_commits)}")
    console.print(f"  Decisions Made: {len(session.metadata.decisions_made)}")
    console.print(f"  Blockers Resolved: {len(session.metadata.blockers_resolved)}")
    console.print(f"  Commands Executed: {session.metadata.commands_executed}")

    # Show recent activity
    if session.metadata.work_items_touched:
        console.print(f"\n[cyan]Recent Work Items:[/cyan]")
        for wi_id in session.metadata.work_items_touched[-3:]:
            console.print(f"  • WI-{wi_id}")

    if session.metadata.tasks_completed:
        console.print(f"\n[cyan]Recently Completed Tasks:[/cyan]")
        for task_id in session.metadata.tasks_completed[-3:]:
            console.print(f"  • Task #{task_id}")

    # Show validation status
    is_complete, missing = SessionAdapter.validate_completeness(session)
    if not is_complete:
        console.print(f"\n⚠️  [yellow]Session Completeness Warnings:[/yellow]")
        for item in missing:
            console.print(f"  • {item}")

    console.print(f"\n💡 [yellow]Commands:[/yellow]")
    console.print(f"   apm session add-decision \"...\" --rationale \"...\"")
    console.print(f"   apm session show {session.session_id}  # Full details\n")
