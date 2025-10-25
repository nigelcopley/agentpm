"""
Search Summaries Command

Search summaries by text content with filtering options.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.enums import EntityType, SummaryType
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('search_text')
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    help='Filter by entity type'
)
@click.option(
    '--summary-type',
    type=click.Choice([s.value for s in SummaryType], case_sensitive=False),
    help='Filter by summary type'
)
@click.option(
    '--limit',
    type=int,
    default=20,
    help='Maximum number of results (default: 20)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'list', 'json']),
    default='table',
    help='Output format (default: table)'
)
@click.pass_context
def search_summaries(
    ctx: click.Context,
    search_text: str,
    entity_type: str,
    summary_type: str,
    limit: int,
    format: str
):
    """Search summaries by text content."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Parse enums if provided
        entity_type_enum = EntityType(entity_type.lower()) if entity_type else None
        summary_type_enum = SummaryType(summary_type.lower()) if summary_type else None
        
        # Search summaries
        results = summaries.search_summaries(
            db_service, search_text, entity_type_enum, summary_type_enum, limit
        )
        
        if not results:
            console.print(f"[yellow]No summaries found matching '{search_text}'[/yellow]")
            return
        
        # Display results
        if format == 'json':
            _display_json(console, results)
        elif format == 'list':
            _display_list(console, results, search_text)
        else:
            _display_table(console, results, search_text)
        
        # Show count
        console.print(f"\n[dim]Found {len(results)} summaries matching '{search_text}'[/dim]")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to search summaries: {e}")


def _display_table(console: Console, results, search_text: str):
    """Display search results in table format."""
    table = Table(title=f"Search Results for '{search_text}'")
    
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Entity", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Author", style="blue")
    table.add_column("Created", style="dim")
    table.add_column("Match", style="white")
    
    for summary in results:
        # Find and highlight match
        match_text = _highlight_match(summary.summary_text, search_text)
        
        table.add_row(
            str(summary.id),
            summary.get_entity_reference(),
            summary.summary_type.value.replace('_', ' ').title(),
            summary.created_by,
            summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown',
            match_text
        )
    
    console.print(table)


def _display_list(console: Console, results, search_text: str):
    """Display search results in list format."""
    for summary in results:
        # Create panel for each result
        title = f"Summary #{summary.id} - {summary.get_entity_reference()}"
        
        content_lines = [
            f"Type: {summary.summary_type.value.replace('_', ' ').title()}",
            f"Author: {summary.created_by}",
            f"Created: {summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'}",
            ""
        ]
        
        # Add session info if available
        if summary.session_id:
            content_lines.append(f"Session: #{summary.session_id}")
        if summary.session_date:
            content_lines.append(f"Session Date: {summary.session_date}")
        
        content_lines.extend([
            "",
            "Content (with match highlighted):",
            _highlight_match(summary.summary_text, search_text)
        ])
        
        panel = Panel(
            "\n".join(content_lines),
            title=title,
            border_style="blue"
        )
        
        console.print(panel)
        console.print()  # Add spacing


def _display_json(console: Console, results):
    """Display search results in JSON format."""
    import json
    
    json_data = []
    for summary in results:
        json_data.append({
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
        })
    
    console.print(json.dumps(json_data, indent=2))


def _highlight_match(text: str, search_text: str, context_chars: int = 50) -> str:
    """Highlight search text in context."""
    import re
    
    # Find all matches (case insensitive)
    pattern = re.compile(re.escape(search_text), re.IGNORECASE)
    matches = list(pattern.finditer(text))
    
    if not matches:
        # No matches found, return truncated text
        return text[:context_chars] + "..." if len(text) > context_chars else text
    
    # Get the first match
    match = matches[0]
    start = match.start()
    end = match.end()
    
    # Calculate context window
    context_start = max(0, start - context_chars)
    context_end = min(len(text), end + context_chars)
    
    # Extract context
    context = text[context_start:context_end]
    
    # Adjust match positions relative to context
    match_start = start - context_start
    match_end = end - context_start
    
    # Highlight the match
    highlighted = (
        context[:match_start] +
        f"[bold yellow]{context[match_start:match_end]}[/bold yellow]" +
        context[match_end:]
    )
    
    # Add ellipsis if needed
    if context_start > 0:
        highlighted = "..." + highlighted
    if context_end < len(text):
        highlighted = highlighted + "..."
    
    return highlighted


@click.command()
@click.argument('search_text')
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    help='Filter by entity type'
)
@click.option(
    '--limit',
    type=int,
    default=10,
    help='Maximum number of results'
)
@click.pass_context
def search_summaries_quick(
    ctx: click.Context,
    search_text: str,
    entity_type: str,
    limit: int
):
    """Quick search with compact results."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Parse enum if provided
        entity_type_enum = EntityType(entity_type.lower()) if entity_type else None
        
        # Search summaries
        results = summaries.search_summaries(
            db_service, search_text, entity_type_enum, None, limit
        )
        
        if not results:
            console.print(f"[yellow]No summaries found matching '{search_text}'[/yellow]")
            return
        
        # Compact display
        console.print(f"[bold]Found {len(results)} summaries matching '{search_text}':[/bold]\n")
        
        for summary in results:
            console.print(f"[cyan]#{summary.id}[/cyan] {summary.get_entity_reference()} - {summary.summary_type.value.replace('_', ' ').title()}")
            console.print(f"[dim]By {summary.created_by} on {summary.created_at.strftime('%Y-%m-%d') if summary.created_at else 'Unknown'}[/dim]")
            
            # Show match context
            match_context = _highlight_match(summary.summary_text, search_text, 30)
            console.print(f"  {match_context}")
            console.print()
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to search summaries: {e}")
