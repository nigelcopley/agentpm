"""
Summary Statistics Command

Display summary statistics and analytics.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import summaries
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option(
    '--format',
    type=click.Choice(['table', 'json']),
    default='table',
    help='Output format (default: table)'
)
@click.pass_context
def summary_stats(
    ctx: click.Context,
    format: str
):
    """Display summary statistics and analytics."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get statistics
        stats = summaries.get_summary_statistics(db_service)
        
        if format == 'json':
            _display_json(console, stats)
        else:
            _display_table(console, stats)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get summary statistics: {e}")


def _display_table(console: Console, stats):
    """Display statistics in table format."""
    # Overall stats
    console.print(f"\n[bold blue]Summary Statistics[/bold blue]")
    console.print("=" * 50)
    
    console.print(f"Total Summaries: [bold]{stats['total_summaries']}[/bold]")
    console.print(f"Recent (30 days): [bold]{stats['recent_30_days']}[/bold]")
    
    # By entity type
    if stats['by_entity_type']:
        console.print(f"\n[bold]By Entity Type:[/bold]")
        entity_table = Table()
        entity_table.add_column("Entity Type", style="cyan")
        entity_table.add_column("Count", style="green")
        entity_table.add_column("Percentage", style="yellow")
        
        total = stats['total_summaries']
        for entity_type, count in sorted(stats['by_entity_type'].items()):
            percentage = (count / total * 100) if total > 0 else 0
            entity_table.add_row(
                entity_type.replace('_', ' ').title(),
                str(count),
                f"{percentage:.1f}%"
            )
        
        console.print(entity_table)
    
    # By summary type
    if stats['by_summary_type']:
        console.print(f"\n[bold]By Summary Type:[/bold]")
        type_table = Table()
        type_table.add_column("Summary Type", style="cyan")
        type_table.add_column("Count", style="green")
        type_table.add_column("Percentage", style="yellow")
        
        total = stats['total_summaries']
        for summary_type, count in sorted(stats['by_summary_type'].items()):
            percentage = (count / total * 100) if total > 0 else 0
            type_table.add_row(
                summary_type.replace('_', ' ').title(),
                str(count),
                f"{percentage:.1f}%"
            )
        
        console.print(type_table)
    
    # Most active entities
    if stats['most_active_entities']:
        console.print(f"\n[bold]Most Active Entities:[/bold]")
        active_table = Table()
        active_table.add_column("Entity", style="cyan")
        active_table.add_column("Type", style="green")
        active_table.add_column("Summary Count", style="yellow")
        
        for entity in stats['most_active_entities']:
            active_table.add_row(
                f"#{entity['entity_id']}",
                entity['entity_type'].replace('_', ' ').title(),
                str(entity['summary_count'])
            )
        
        console.print(active_table)


def _display_json(console: Console, stats):
    """Display statistics in JSON format."""
    console.print(json.dumps(stats, indent=2))


@click.command()
@click.option(
    '--entity-type',
    type=click.Choice(['project', 'session', 'work_item', 'task', 'idea'], case_sensitive=False),
    help='Filter by entity type'
)
@click.option(
    '--limit',
    type=int,
    default=10,
    help='Number of top entities to show'
)
@click.pass_context
def top_entities(
    ctx: click.Context,
    entity_type: str,
    limit: int
):
    """Show entities with the most summaries."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get statistics
        stats = summaries.get_summary_statistics(db_service)
        
        # Filter by entity type if specified
        entities = stats['most_active_entities']
        if entity_type:
            entities = [e for e in entities if e['entity_type'] == entity_type]
        
        # Limit results
        entities = entities[:limit]
        
        if not entities:
            console.print(f"[yellow]No entities found[/yellow]")
            return
        
        # Display
        console.print(f"\n[bold blue]Top {len(entities)} Entities by Summary Count[/bold blue]")
        console.print("=" * 50)
        
        table = Table()
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Entity", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Summaries", style="blue")
        
        for i, entity in enumerate(entities, 1):
            table.add_row(
                str(i),
                f"#{entity['entity_id']}",
                entity['entity_type'].replace('_', ' ').title(),
                str(entity['summary_count'])
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get top entities: {e}")


@click.command()
@click.option(
    '--days',
    type=int,
    default=7,
    help='Number of days to look back (default: 7)'
)
@click.pass_context
def recent_activity(
    ctx: click.Context,
    days: int
):
    """Show recent summary activity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get recent summaries
        recent_summaries = summaries.get_recent_summaries(db_service, limit=20)
        
        if not recent_summaries:
            console.print(f"[yellow]No recent summaries found[/yellow]")
            return
        
        # Display
        console.print(f"\n[bold blue]Recent Summary Activity (Last {days} days)[/bold blue]")
        console.print("=" * 50)
        
        table = Table()
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Entity", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Author", style="blue")
        table.add_column("Created", style="dim")
        
        for summary in recent_summaries:
            table.add_row(
                str(summary.id),
                summary.get_entity_reference(),
                summary.summary_type.value.replace('_', ' ').title(),
                summary.created_by,
                summary.created_at.strftime('%Y-%m-%d %H:%M') if summary.created_at else 'Unknown'
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get recent activity: {e}")


@click.command()
@click.pass_context
def summary_health(
    ctx: click.Context
):
    """Check summary system health and data quality."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    
    try:
        # Get statistics
        stats = summaries.get_summary_statistics(db_service)
        
        console.print(f"\n[bold blue]Summary System Health Check[/bold blue]")
        console.print("=" * 50)
        
        # Overall health
        total = stats['total_summaries']
        recent = stats['recent_30_days']
        
        if total == 0:
            console.print("[yellow]⚠ No summaries found in system[/yellow]")
        elif recent == 0:
            console.print("[yellow]⚠ No recent summary activity (last 30 days)[/yellow]")
        else:
            console.print(f"[green]✓ System healthy with {total} total summaries[/green]")
            console.print(f"[green]✓ Recent activity: {recent} summaries in last 30 days[/green]")
        
        # Entity type distribution
        entity_types = stats['by_entity_type']
        if len(entity_types) < 2:
            console.print("[yellow]⚠ Limited entity type diversity[/yellow]")
        else:
            console.print(f"[green]✓ Good entity type diversity: {len(entity_types)} types[/green]")
        
        # Summary type distribution
        summary_types = stats['by_summary_type']
        if len(summary_types) < 3:
            console.print("[yellow]⚠ Limited summary type diversity[/yellow]")
        else:
            console.print(f"[green]✓ Good summary type diversity: {len(summary_types)} types[/green]")
        
        # Most active entities
        active_entities = stats['most_active_entities']
        if active_entities:
            top_entity = active_entities[0]
            console.print(f"[green]✓ Most active entity: {top_entity['entity_type']} #{top_entity['entity_id']} with {top_entity['summary_count']} summaries[/green]")
        
        console.print(f"\n[dim]Health check completed[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to check system health: {e}")
