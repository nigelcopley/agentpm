"""
Create Summary Command

Create summaries for any entity type in the APM (Agent Project Manager) hierarchy.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.summary import Summary
from agentpm.core.database.enums import EntityType, SummaryType
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    required=True,
    help='Type of entity this summary belongs to'
)
@click.option(
    '--entity-id',
    type=int,
    required=True,
    help='ID of the entity this summary belongs to'
)
@click.option(
    '--summary-type',
    type=click.Choice([s.value for s in SummaryType], case_sensitive=False),
    required=True,
    help='Type of summary to create'
)
@click.option(
    '--text',
    type=str,
    required=True,
    help='Summary text content (markdown format)'
)
@click.option(
    '--created-by',
    type=str,
    default=None,
    help='Creator identifier (default: current user from environment)'
)
@click.option(
    '--session-id',
    type=int,
    help='Optional session ID for traceability'
)
@click.option(
    '--session-date',
    type=str,
    help='Session date in YYYY-MM-DD format'
)
@click.option(
    '--session-duration',
    type=float,
    help='Session duration in hours'
)
@click.option(
    '--metadata',
    type=str,
    help='JSON metadata for structured data'
)
@click.pass_context
def create_summary(
    ctx: click.Context,
    entity_type: str,
    entity_id: int,
    summary_type: str,
    text: str,
    created_by: str,
    session_id: int,
    session_date: str,
    session_duration: float,
    metadata: str
):
    """Create a summary for any entity type."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    # Auto-detect created_by if not provided
    from agentpm.cli.utils.user import get_created_by_value
    created_by = get_created_by_value(created_by)
    
    try:
        # Parse enums
        entity_type_enum = EntityType(entity_type.lower())
        summary_type_enum = SummaryType(summary_type.lower())
        
        # Parse metadata if provided
        context_metadata = None
        if metadata:
            import json
            try:
                context_metadata = json.loads(metadata)
            except json.JSONDecodeError as e:
                console.print(f"[red]✗[/red] Invalid JSON metadata: {e}")
                return
        
        # Create summary model
        summary = Summary(
            entity_type=entity_type_enum,
            entity_id=entity_id,
            summary_type=summary_type_enum,
            summary_text=text,
            context_metadata=context_metadata,
            created_by=created_by,
            session_id=session_id,
            session_date=session_date,
            session_duration_hours=session_duration
        )
        
        # Create summary in database
        created_summary = summaries.create_summary(db_service, summary)
        
        # Display success
        console.print(f"[green]✓[/green] Summary created successfully")
        console.print(f"  ID: {created_summary.id}")
        console.print(f"  Entity: {created_summary.get_entity_reference()}")
        console.print(f"  Type: {created_summary.summary_type.value.replace('_', ' ').title()}")
        console.print(f"  Created: {created_summary.created_at.strftime('%Y-%m-%d %H:%M') if created_summary.created_at else 'Unknown'}")
        
        # Show preview
        preview_text = text[:200] + "..." if len(text) > 200 else text
        console.print(f"\n[dim]Preview:[/dim] {preview_text}")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create summary: {e}")


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice([e.value for e in EntityType], case_sensitive=False),
    required=True,
    help='Type of entity'
)
@click.option(
    '--entity-id',
    type=int,
    required=True,
    help='ID of the entity'
)
@click.option(
    '--summary-type',
    type=click.Choice([s.value for s in SummaryType], case_sensitive=False),
    help='Type of summary (optional)'
)
@click.option(
    '--text',
    prompt='Summary text (markdown format)',
    help='Summary text content'
)
@click.option(
    '--created-by',
    type=str,
    default=None,
    help='Creator identifier (default: current user from environment)'
)
@click.option(
    '--session-id',
    type=int,
    help='Optional session ID'
)
@click.option(
    '--session-date',
    type=str,
    help='Session date (YYYY-MM-DD)'
)
@click.option(
    '--session-duration',
    type=float,
    help='Session duration (hours)'
)
@click.pass_context
def create_summary_interactive(
    ctx: click.Context,
    entity_type: str,
    entity_id: int,
    summary_type: str,
    text: str,
    created_by: str,
    session_id: int,
    session_date: str,
    session_duration: float
):
    """Create a summary interactively with prompts."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    # Auto-detect created_by if not provided
    from agentpm.cli.utils.user import get_created_by_value
    created_by = get_created_by_value(created_by)
    
    try:
        # Parse enums
        entity_type_enum = EntityType(entity_type.lower())
        
        # Get appropriate summary types for entity
        appropriate_types = SummaryType.get_appropriate_types(entity_type_enum)
        
        if not summary_type:
            # Show available types
            console.print("\n[bold]Available summary types:[/bold]")
            for i, st in enumerate(appropriate_types, 1):
                console.print(f"  {i}. {st.value.replace('_', ' ').title()}")
            
            choice = click.prompt(f"\nSelect summary type (1-{len(appropriate_types)})", type=int)
            if 1 <= choice <= len(appropriate_types):
                summary_type_enum = appropriate_types[choice - 1]
            else:
                console.print("[red]✗[/red] Invalid choice")
                return
        else:
            summary_type_enum = SummaryType(summary_type.lower())
        
        # Create summary model
        summary = Summary(
            entity_type=entity_type_enum,
            entity_id=entity_id,
            summary_type=summary_type_enum,
            summary_text=text,
            created_by=created_by,
            session_id=session_id,
            session_date=session_date,
            session_duration_hours=session_duration
        )
        
        # Create summary in database
        created_summary = summaries.create_summary(db_service, summary)
        
        # Display success
        console.print(f"\n[green]✓[/green] Summary created successfully")
        console.print(f"  ID: {created_summary.id}")
        console.print(f"  Entity: {created_summary.get_entity_reference()}")
        console.print(f"  Type: {created_summary.summary_type.value.replace('_', ' ').title()}")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create summary: {e}")
