"""
Delete Summary Command

Delete summaries with confirmation.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('summary_id', type=int)
@click.option(
    '--force',
    is_flag=True,
    help='Skip confirmation prompt'
)
@click.pass_context
def delete_summary(
    ctx: click.Context,
    summary_id: int,
    force: bool
):
    """Delete a summary."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get summary first to show what will be deleted
        summary = summaries.get_summary(db_service, summary_id)
        
        if not summary:
            console.print(f"[red]✗[/red] Summary #{summary_id} not found")
            return
        
        # Show summary details
        console.print(f"[bold]Summary to delete:[/bold]")
        console.print(f"  ID: {summary.id}")
        console.print(f"  Entity: {summary.get_entity_reference()}")
        console.print(f"  Type: {summary.summary_type.value.replace('_', ' ').title()}")
        console.print(f"  Author: {summary.created_by}")
        console.print(f"  Created: {summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'}")
        
        # Show content preview
        preview = summary.summary_text[:100] + "..." if len(summary.summary_text) > 100 else summary.summary_text
        console.print(f"  Content: {preview}")
        
        # Confirmation
        if not force:
            if not click.confirm(f"\nAre you sure you want to delete summary #{summary_id}?"):
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        # Delete summary
        success = summaries.delete_summary(db_service, summary_id)
        
        if success:
            console.print(f"[green]✓[/green] Summary #{summary_id} deleted successfully")
        else:
            console.print(f"[red]✗[/red] Failed to delete summary #{summary_id}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to delete summary: {e}")


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice(['project', 'session', 'work_item', 'task', 'idea'], case_sensitive=False),
    required=True,
    help='Entity type to delete summaries for'
)
@click.option(
    '--entity-id',
    type=int,
    required=True,
    help='Entity ID to delete summaries for'
)
@click.option(
    '--summary-type',
    type=str,
    help='Only delete summaries of this type'
)
@click.option(
    '--force',
    is_flag=True,
    help='Skip confirmation prompt'
)
@click.pass_context
def delete_entity_summaries(
    ctx: click.Context,
    entity_type: str,
    entity_id: int,
    summary_type: str,
    force: bool
):
    """Delete all summaries for a specific entity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        from agentpm.core.database.enums import EntityType, SummaryType
        
        entity_type_enum = EntityType(entity_type.lower())
        summary_type_enum = SummaryType(summary_type.lower()) if summary_type else None
        
        # Get summaries to be deleted
        summaries_list = summaries.get_summaries_for_entity(
            db_service, entity_type_enum, entity_id, None, summary_type_enum
        )
        
        if not summaries_list:
            console.print(f"[yellow]No summaries found for {entity_type} #{entity_id}[/yellow]")
            return
        
        # Show what will be deleted
        console.print(f"[bold]Summaries to delete for {entity_type} #{entity_id}:[/bold]")
        for summary in summaries_list:
            console.print(f"  #{summary.id} - {summary.summary_type.value.replace('_', ' ').title()} by {summary.created_by}")
        
        console.print(f"\n[bold]Total: {len(summaries_list)} summaries[/bold]")
        
        # Confirmation
        if not force:
            if not click.confirm(f"\nAre you sure you want to delete all {len(summaries_list)} summaries?"):
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        # Delete summaries
        deleted_count = 0
        for summary in summaries_list:
            if summaries.delete_summary(db_service, summary.id):
                deleted_count += 1
        
        if deleted_count == len(summaries_list):
            console.print(f"[green]✓[/green] Successfully deleted {deleted_count} summaries")
        else:
            console.print(f"[yellow]⚠[/yellow] Deleted {deleted_count} of {len(summaries_list)} summaries")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Validation error: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to delete summaries: {e}")


@click.command()
@click.option(
    '--older-than-days',
    type=int,
    default=30,
    help='Delete summaries older than this many days (default: 30)'
)
@click.option(
    '--entity-type',
    type=click.Choice(['project', 'session', 'work_item', 'task', 'idea'], case_sensitive=False),
    help='Only delete summaries for this entity type'
)
@click.option(
    '--summary-type',
    type=str,
    help='Only delete summaries of this type'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be deleted without actually deleting'
)
@click.option(
    '--force',
    is_flag=True,
    help='Skip confirmation prompt'
)
@click.pass_context
def delete_old_summaries(
    ctx: click.Context,
    older_than_days: int,
    entity_type: str,
    summary_type: str,
    dry_run: bool,
    force: bool
):
    """Delete old summaries based on age."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # This would require a new method in summaries.py
        # For now, show a placeholder
        console.print("[yellow]This feature requires additional database methods[/yellow]")
        console.print("Would delete summaries older than {older_than_days} days")
        
        if entity_type:
            console.print(f"  Entity type: {entity_type}")
        if summary_type:
            console.print(f"  Summary type: {summary_type}")
        
        if dry_run:
            console.print("  [dim]Dry run mode - no actual deletion[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to delete old summaries: {e}")
