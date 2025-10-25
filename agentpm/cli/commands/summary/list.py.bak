"""
List Summaries Command

List summaries with filtering and sorting options.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Optional

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.enums import EntityType, SummaryType
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    help='Filter by entity type'
)
@click.option(
    '--entity-id',
    type=int,
    help='Filter by specific entity ID'
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
    help='Maximum number of summaries to show (default: 20)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'list', 'json']),
    default='table',
    help='Output format (default: table)'
)
@click.pass_context
def list_summaries(
    ctx: click.Context,
    entity_type: Optional[str],
    entity_id: Optional[int],
    summary_type: Optional[str],
    limit: int,
    format: str
):
    """List summaries with optional filtering."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Parse enums if provided
        entity_type_enum = EntityType(entity_type.lower()) if entity_type else None
        summary_type_enum = SummaryType(summary_type.lower()) if summary_type else None
        
        # Get summaries
        if entity_type_enum and entity_id:
            # Get summaries for specific entity
            summaries_list = summaries.get_summaries_for_entity(
                db_service, entity_type_enum, entity_id, limit, summary_type_enum
            )
        else:
            # Get recent summaries with filters
            summaries_list = summaries.get_recent_summaries(
                db_service, limit, entity_type_enum, summary_type_enum
            )
        
        if not summaries_list:
            console.print("[yellow]No summaries found[/yellow]")
            return
        
        # Display based on format
        if format == 'json':
            _display_json(console, summaries_list)
        elif format == 'list':
            _display_list(console, summaries_list)
        else:
            _display_table(console, summaries_list)
        
        # Show count
        console.print(f"\n[dim]Showing {len(summaries_list)} summaries[/dim]")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list summaries: {e}")


def _display_table(console: Console, summaries_list):
    """Display summaries in table format."""
    table = Table(title="Summaries")
    
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Entity", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Author", style="blue")
    table.add_column("Created", style="dim")
    table.add_column("Preview", style="white")
    
    for summary in summaries_list:
        # Truncate preview
        preview = summary.summary_text[:50] + "..." if len(summary.summary_text) > 50 else summary.summary_text
        
        table.add_row(
            str(summary.id),
            summary.get_entity_reference(),
            summary.summary_type.value.replace('_', ' ').title(),
            summary.created_by,
            summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown',
            preview
        )
    
    console.print(table)


def _display_list(console: Console, summaries_list):
    """Display summaries in list format."""
    for summary in summaries_list:
        # Create panel for each summary
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
        if summary.session_duration_hours:
            content_lines.append(f"Duration: {summary.session_duration_hours:.1f}h")
        
        content_lines.extend([
            "",
            "Content:",
            summary.summary_text[:200] + "..." if len(summary.summary_text) > 200 else summary.summary_text
        ])
        
        panel = Panel(
            "\n".join(content_lines),
            title=title,
            border_style="blue"
        )
        
        console.print(panel)
        console.print()  # Add spacing


def _display_json(console: Console, summaries_list):
    """Display summaries in JSON format."""
    import json
    
    json_data = []
    for summary in summaries_list:
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


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    required=True,
    help='Entity type to list summaries for'
)
@click.option(
    '--entity-id',
    type=int,
    required=True,
    help='Entity ID to list summaries for'
)
@click.option(
    '--limit',
    type=int,
    default=10,
    help='Maximum number of summaries to show'
)
@click.pass_context
def list_entity_summaries(
    ctx: click.Context,
    entity_type: str,
    entity_id: int,
    limit: int
):
    """List summaries for a specific entity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        entity_type_enum = EntityType(entity_type.lower())
        
        summaries_list = summaries.get_summaries_for_entity(
            db_service, entity_type_enum, entity_id, limit
        )
        
        if not summaries_list:
            console.print(f"[yellow]No summaries found for {entity_type} #{entity_id}[/yellow]")
            return
        
        console.print(f"[bold]Summaries for {entity_type} #{entity_id}:[/bold]\n")
        
        for summary in summaries_list:
            console.print(f"[cyan]#{summary.id}[/cyan] {summary.summary_type.value.replace('_', ' ').title()}")
            console.print(f"  [dim]By {summary.created_by} on {summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'}[/dim]")
            
            # Show preview
            preview = summary.summary_text[:100] + "..." if len(summary.summary_text) > 100 else summary.summary_text
            console.print(f"  {preview}")
            console.print()
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to list summaries: {e}")
