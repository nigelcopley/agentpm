"""
apm session history - View session history and analytics
"""

from datetime import datetime, timedelta
from typing import Optional
import click
from rich.table import Table
from rich import box

from agentpm.core.database.adapters import SessionAdapter
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option('--days', type=int, default=7, help='Number of days to show (default: 7)')
@click.option('--limit', type=int, default=50, help='Maximum sessions to show (default: 50)')
@click.option('--work-item', 'work_item_id', type=int, help='Filter by work item ID')
@click.option('--developer', help='Filter by developer name/email')
@click.option('--search', help='Search decisions (case-insensitive)')
@click.option('--stats', is_flag=True, help='Show statistics instead of session list')
@click.option('--active-only', is_flag=True, help='Show only active sessions')
@click.pass_context
def history(ctx: click.Context, days: int, limit: int, work_item_id: Optional[int],
            developer: Optional[str], search: Optional[str], stats: bool, active_only: bool):
    """
    View session history with filters and analytics.

    Display recent sessions with various filtering options,
    or show aggregate statistics across time periods.

    \b
    Filter Options:
      --days N          Show last N days (default: 7)
      --limit N         Max sessions to show (default: 50)
      --work-item ID    Sessions that touched work item
      --developer NAME  Sessions by developer
      --search TEXT     Search in decisions
      --active-only     Only active sessions
      --stats           Show statistics summary

    \b
    Examples:
      apm session history                            # Last 7 days
      apm session history --days 30                  # Last 30 days
      apm session history --work-item 35             # Sessions on WI-35
      apm session history --developer "Jane"         # Jane's sessions
      apm session history --search "pydantic"        # Search decisions
      apm session history --stats --days 30          # 30-day stats
      apm session history --active-only              # Active sessions only
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Show statistics if requested
    if stats:
        _show_stats(console, db, project_id, days)
        return

    # Show decision search results if requested
    if search:
        _show_decision_search(console, db, project_id, search)
        return

    # Get sessions based on filters
    if work_item_id:
        sessions = SessionAdapter.get_by_work_item(db, work_item_id)
    elif developer:
        sessions = SessionAdapter.get_by_developer(db, developer, project_id=project_id)
    elif active_only:
        sessions = SessionAdapter.get_active_sessions(db, project_id)
    else:
        # Default: recent sessions
        sessions = SessionAdapter.list(db, project_id=project_id)

        # Filter by date range if specified
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            sessions = [s for s in sessions if s.started_at and datetime.fromisoformat(s.started_at) >= cutoff]

    if not sessions:
        console.print(f"\n⚠️  [yellow]No sessions found matching your criteria[/yellow]\n")
        console.print("💡 [cyan]Try:[/cyan]")
        console.print("   • Adjust --days parameter")
        console.print("   • Check --work-item ID")
        console.print("   • Remove filters\n")
        return

    # Display sessions table
    console.print(f"\n📊 [bold cyan]Session History[/bold cyan] ({len(sessions)} sessions)\n")

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Session ID", style="dim", width=12)
    table.add_column("Type", style="cyan")
    table.add_column("Started", style="green")
    table.add_column("Duration", justify="right")
    table.add_column("Status")
    table.add_column("Developer")

    for session in sessions:
        # Truncate session ID for display
        session_id_short = session.session_id[:8] + "..."

        # Format start time
        if session.started_at:
            start_display = datetime.fromisoformat(session.started_at).strftime('%Y-%m-%d %H:%M')
        else:
            start_display = "-"

        # Duration
        if session.duration_minutes:
            duration_display = f"{session.duration_minutes}m"
        else:
            duration_display = "-"

        # Status
        if session.is_active:
            status_display = "🔄 Active"
        else:
            status_display = "✅ Complete"

        # Developer
        dev_display = session.developer_name or "-"

        table.add_row(
            session_id_short,
            session.session_type.value,
            start_display,
            duration_display,
            status_display,
            dev_display
        )

    console.print(table)

    console.print(f"\n💡 [yellow]View details:[/yellow]")
    console.print(f"   apm session show <session-id>\n")


def _show_stats(console, db, project_id: int, days: int):
    """Show session statistics."""
    stats = SessionAdapter.get_stats(db, project_id=project_id)

    console.print(f"\n📊 [bold cyan]Session Statistics[/bold cyan] (Last {days} days)\n")

    # Create stats table
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Sessions", str(stats['total_sessions']))
    table.add_row("Active Sessions", str(stats['active_sessions']))
    table.add_row("Average Duration", f"{stats['avg_duration']}m")
    table.add_row("Total Time", f"{stats['total_duration']}m ({stats['total_duration'] / 60:.1f}h)")
    table.add_row("Sessions/Day", f"{stats['sessions_per_day']:.1f}")

    console.print(table)

    # Tool distribution
    if stats['tool_distribution']:
        console.print(f"\n[bold]Tool Distribution:[/bold]")
        for tool, count in stats['tool_distribution'].items():
            console.print(f"  {tool}: {count} sessions")

    # Session type distribution
    if stats['session_type_distribution']:
        console.print(f"\n[bold]Session Type Distribution:[/bold]")
        for stype, count in stats['session_type_distribution'].items():
            console.print(f"  {stype}: {count} sessions")

    console.print()


def _show_decision_search(console, db, project_id: int, query: str):
    """Show decision search results."""
    results = SessionAdapter.search_decisions(db, query, project_id=project_id)

    if not results:
        console.print(f"\n⚠️  [yellow]No decisions found matching:[/yellow] {query}\n")
        return

    console.print(f"\n🔍 [bold cyan]Decision Search Results[/bold cyan] ({len(results)} found)\n")

    for result in results:
        session_id_short = result['session_id'][:8] + "..."
        decision = result.get('decision', 'No description')
        rationale = result.get('rationale', '')

        console.print(f"[cyan]Session {session_id_short}:[/cyan]")
        console.print(f"  Decision: {decision}")
        if rationale:
            console.print(f"  Rationale: [dim]{rationale}[/dim]")
        console.print()

    console.print(f"💡 [yellow]View full session:[/yellow]")
    console.print(f"   apm session show <session-id>\n")
