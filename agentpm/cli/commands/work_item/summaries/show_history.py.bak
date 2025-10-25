"""
apm work-item show-history - View session summaries for work item
"""

import click
import json
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.methods import work_item_summaries as summary_methods


@click.command(name='show-history')
@click.argument('work_item_id', type=int)
@click.option('--limit', '-n', type=int, default=10, help='Number of summaries to show (default: 10)')
@click.option('--type', 'summary_type',
              type=click.Choice(['session', 'milestone', 'decision', 'retrospective']),
              help='Filter by summary type')
@click.option('--full', is_flag=True, help='Show full summary text (not truncated)')
@click.pass_context
def show_history(
    ctx: click.Context,
    work_item_id: int,
    limit: int,
    summary_type: str,
    full: bool
):
    """
    View session summary history for work item.

    Displays chronological summaries with:
    - Session date and duration
    - Summary text (truncated or full)
    - Key decisions count
    - Tasks completed count

    \b
    Examples:
      # Recent summaries (default: last 10)
      apm work-item show-history 7

      # Last 5 summaries
      apm work-item show-history 7 --limit 5

      # Only milestone summaries
      apm work-item show-history 7 --type milestone

      # Full text (not truncated)
      apm work-item show-history 7 --full
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    try:
        # Get summaries
        summaries = summary_methods.list_summaries(
            db,
            work_item_id=work_item_id,
            summary_type=summary_type,
            limit=limit
        )

        if not summaries:
            console.print(f"\n📭 [yellow]No summaries found[/yellow] for work item #{work_item_id}")
            if summary_type:
                console.print(f"   (Type filter: {summary_type})")
            console.print(f"\n💡 [cyan]Add a summary:[/cyan]")
            console.print(f'   apm work-item add-summary {work_item_id} --text "Session summary..."\n')
            return

        # Display header
        console.print(f"\n📋 [bold]Session History:[/bold] Work Item #{work_item_id}")
        console.print(f"   Found {len(summaries)} summaries")
        if summary_type:
            console.print(f"   Filtered by: {summary_type}")
        console.print()

        # Display summaries (newest first)
        for idx, summary in enumerate(summaries, 1):
            # Summary header
            header_parts = [
                f"#{summary.id}",
                summary.session_date,
                summary.summary_type
            ]
            if summary.session_duration_hours:
                header_parts.append(f"{summary.session_duration_hours}h")

            header = " | ".join(header_parts)

            # Summary text (truncate unless --full)
            text = summary.summary_text
            if not full and len(text) > 200:
                text = text[:200] + "..."

            # Context metadata summary
            metadata_summary = []
            if summary.context_metadata:
                try:
                    meta = summary.context_metadata
                    if 'key_decisions' in meta and meta['key_decisions']:
                        metadata_summary.append(f"✓ {len(meta['key_decisions'])} decisions")
                    if 'tasks_completed' in meta and meta['tasks_completed']:
                        metadata_summary.append(f"✓ {len(meta['tasks_completed'])} tasks")
                    if 'blockers_resolved' in meta and meta['blockers_resolved']:
                        metadata_summary.append(f"✓ {len(meta['blockers_resolved'])} blockers")
                except (TypeError, AttributeError):
                    pass

            # Build panel content
            content_parts = [text]
            if metadata_summary:
                content_parts.append("\n" + " | ".join(metadata_summary))

            # Display panel
            panel = Panel(
                "\n".join(content_parts),
                title=f"[bold]{header}[/bold]",
                title_align="left",
                border_style="cyan" if summary.summary_type == "milestone" else "blue"
            )
            console.print(panel)

            # Separator except for last item
            if idx < len(summaries):
                console.print()

        # Footer
        console.print(f"\n📚 [cyan]Commands:[/cyan]")
        console.print(f"   apm work-item add-summary {work_item_id} --text \"...\"  # Add summary")
        console.print(f"   apm work-item show-history {work_item_id} --full         # Show full text\n")

    except Exception as e:
        console_err.print(f"\n❌ [red]Failed to retrieve history:[/red] {e}\n")
        raise click.Abort()
