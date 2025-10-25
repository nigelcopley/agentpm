"""
apm work-item add-summary - Add session summary to work item
"""

import click
from datetime import date
import json

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.models import WorkItemSummary
from agentpm.core.database.methods import work_item_summaries as summary_methods


@click.command(name='add-summary')
@click.argument('work_item_id', type=int)
@click.option('--text', '-t', required=True, help='Summary text (markdown format)')
@click.option('--date', '-d', 'session_date', help='Session date (YYYY-MM-DD, defaults to today)')
@click.option('--duration', type=float, help='Session duration in hours')
@click.option('--metadata', '-m', help='Context metadata (JSON string)')
@click.option('--type', 'summary_type',
              type=click.Choice(['session', 'milestone', 'decision', 'retrospective']),
              default='session',
              help='Summary type (default: session)')
@click.option('--created-by', help='Creator identifier (defaults to current user)')
@click.pass_context
def add_summary(
    ctx: click.Context,
    work_item_id: int,
    text: str,
    session_date: str,
    duration: float,
    metadata: str,
    summary_type: str,
    created_by: str
):
    """
    Add session summary to work item.

    Session summaries capture temporal context including:
    - Session narrative (what happened)
    - Key decisions made
    - Tasks completed
    - Blockers resolved
    - Lessons learned

    \b
    Examples:
      # Basic session summary
      apm work-item add-summary 7 --text "Completed design phase..."

      # With session date and duration
      apm work-item add-summary 7 \\
        --text "Implemented 3-layer pattern..." \\
        --date "2025-10-06" \\
        --duration 4.5

      # With structured metadata
      apm work-item add-summary 7 \\
        --text "# Session Summary..." \\
        --metadata '{"key_decisions": ["Use separate tables"], "tasks_completed": [17, 18]}'

      # Milestone summary
      apm work-item add-summary 7 \\
        --text "Phase 1 complete!" \\
        --type milestone
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Default session_date to today if not provided
    if not session_date:
        session_date = date.today().isoformat()

    # Validate date format
    try:
        date.fromisoformat(session_date)
    except ValueError:
        console_err.print(f"\n❌ [red]Invalid date format:[/red] {session_date}")
        console_err.print("💡 [yellow]Use YYYY-MM-DD format:[/yellow]")
        console_err.print("   --date 2025-10-06\n")
        raise click.Abort()

    # Parse metadata JSON if provided
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError as e:
            console_err.print(f"\n❌ [red]Invalid JSON:[/red] {e}\n")
            console_err.print("💡 [yellow]Provide valid JSON string:[/yellow]")
            console_err.print('   --metadata \'{"key_decisions": ["Decision 1"]}\'\n')
            raise click.Abort()

    # Create summary model
    summary = WorkItemSummary(
        work_item_id=work_item_id,
        session_date=session_date,
        session_duration_hours=duration,
        summary_text=text,
        context_metadata=metadata_dict,
        created_by=created_by,
        summary_type=summary_type
    )

    try:
        # Create summary
        created = summary_methods.create_summary(db, summary)

        # Success message
        console.print(f"\n✅ [green]Summary added:[/green] #{created.id}")
        console.print(f"   Work Item: #{work_item_id}")
        console.print(f"   Date: {session_date}")
        console.print(f"   Type: {summary_type}")
        if duration:
            console.print(f"   Duration: {duration}h")
        console.print(f"   Text: {text[:80]}...")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm work-item show-history {work_item_id}  # View all summaries\n")

    except Exception as e:
        console_err.print(f"\n❌ [red]Failed to add summary:[/red] {e}\n")
        if "does not exist" in str(e):
            console_err.print("💡 [yellow]Check work item ID:[/yellow]")
            console_err.print(f"   apm work-item list  # View all work items\n")
        raise click.Abort()
