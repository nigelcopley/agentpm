"""
Show Summary Command

Display detailed information about a specific summary.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
import json

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('summary_id', type=int)
@click.option(
    '--format',
    type=click.Choice(['rich', 'markdown', 'json']),
    default='rich',
    help='Output format (default: rich)'
)
@click.pass_context
def show_summary(
    ctx: click.Context,
    summary_id: int,
    format: str
):
    """Show detailed information about a summary."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get summary
        summary = summaries.get_summary(db_service, summary_id)
        
        if not summary:
            console.print(f"[red]✗[/red] Summary #{summary_id} not found")
            return
        
        # Display based on format
        if format == 'json':
            _display_json(console, summary)
        elif format == 'markdown':
            _display_markdown(console, summary)
        else:
            _display_rich(console, summary)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to show summary: {e}")


def _display_rich(console: Console, summary):
    """Display summary in rich format."""
    # Header
    title = f"Summary #{summary.id} - {summary.get_entity_reference()}"
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print("=" * len(title))
    
    # Basic info
    info_table = [
        ("Type", summary.summary_type.value.replace('_', ' ').title()),
        ("Entity", summary.get_entity_reference()),
        ("Author", summary.created_by),
        ("Created", summary.created_at.strftime('%Y-%m-%d %H:%M:%S') if summary.created_at else 'Unknown'),
    ]
    
    if summary.session_id:
        info_table.append(("Session", f"#{summary.session_id}"))
    if summary.session_date:
        info_table.append(("Session Date", summary.session_date))
    if summary.session_duration_hours:
        info_table.append(("Duration", f"{summary.session_duration_hours:.1f} hours"))
    
    for label, value in info_table:
        console.print(f"[bold]{label}:[/bold] {value}")
    
    console.print()
    
    # Content
    console.print("[bold]Content:[/bold]")
    console.print(Panel(
        summary.summary_text,
        title="Summary Text",
        border_style="green"
    ))
    
    # Metadata
    if summary.context_metadata:
        console.print("\n[bold]Metadata:[/bold]")
        metadata_json = json.dumps(summary.context_metadata, indent=2)
        syntax = Syntax(metadata_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(
            syntax,
            title="Context Metadata",
            border_style="yellow"
        ))


def _display_markdown(console: Console, summary):
    """Display summary in markdown format."""
    lines = [
        f"# Summary #{summary.id}",
        "",
        f"**Entity:** {summary.get_entity_reference()}",
        f"**Type:** {summary.summary_type.value.replace('_', ' ').title()}",
        f"**Author:** {summary.created_by}",
        f"**Created:** {summary.created_at.strftime('%Y-%m-%d %H:%M:%S') if summary.created_at else 'Unknown'}",
    ]
    
    if summary.session_id:
        lines.append(f"**Session:** #{summary.session_id}")
    if summary.session_date:
        lines.append(f"**Session Date:** {summary.session_date}")
    if summary.session_duration_hours:
        lines.append(f"**Duration:** {summary.session_duration_hours:.1f} hours")
    
    lines.extend([
        "",
        "## Content",
        "",
        summary.summary_text,
    ])
    
    if summary.context_metadata:
        lines.extend([
            "",
            "## Metadata",
            "",
            "```json",
            json.dumps(summary.context_metadata, indent=2),
            "```"
        ])
    
    console.print("\n".join(lines))


def _display_json(console: Console, summary):
    """Display summary in JSON format."""
    json_data = {
        'id': summary.id,
        'entity_type': summary.entity_type.value,
        'entity_id': summary.entity_id,
        'summary_type': summary.summary_type.value,
        'summary_text': summary.summary_text,
        'context_metadata': summary.context_metadata,
        'created_at': summary.created_at.isoformat() if summary.created_at else None,
        'created_by': summary.created_by,
        'session_id': summary.session_id,
        'session_date': summary.session_date,
        'session_duration_hours': summary.session_duration_hours
    }
    
    console.print(json.dumps(json_data, indent=2))


@click.command()
@click.argument('summary_id', type=int)
@click.pass_context
def show_summary_compact(
    ctx: click.Context,
    summary_id: int
):
    """Show summary in compact format."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get summary
        summary = summaries.get_summary(db_service, summary_id)
        
        if not summary:
            console.print(f"[red]✗[/red] Summary #{summary_id} not found")
            return
        
        # Compact display
        console.print(f"[cyan]#{summary.id}[/cyan] {summary.get_entity_reference()} - {summary.summary_type.value.replace('_', ' ').title()}")
        console.print(f"[dim]By {summary.created_by} on {summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'}[/dim]")
        
        # Show content preview
        preview = summary.summary_text[:200] + "..." if len(summary.summary_text) > 200 else summary.summary_text
        console.print(f"\n{preview}")
        
        # Show metadata if available
        if summary.context_metadata:
            console.print(f"\n[dim]Metadata: {len(summary.context_metadata)} fields[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to show summary: {e}")
