"""
Summary Types Command

Exposes summary-related Pydantic models and enums via CLI.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agentpm.core.database.enums import SummaryType, EntityType


@click.command()
@click.option('--type', 'type_filter', 
              type=click.Choice(['summary-type', 'entity-type', 'all']),
              default='all',
              help='Filter which types to display')
@click.option('--entity-type', 'entity_type_filter',
              type=click.Choice(['project', 'work-item', 'task', 'idea']),
              help='Filter summary types by entity type')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'list', 'json']),
              default='table',
              help='Output format')
@click.pass_context
def types(ctx: click.Context, type_filter: str, entity_type_filter: str, output_format: str):
    """
    📝 Show available summary types and entity types.
    
    Displays all valid values for summary-related enums that can be used
    in summary commands. Essential for AI agents and users to discover
    valid options without hardcoding values.
    
    \b
    Examples:
      apm summary types                                    # Show all types
      apm summary types --type=summary-type                # Show only summary types
      apm summary types --entity-type=project              # Show summary types for projects
      apm summary types --entity-type=work-item            # Show summary types for work items
      apm summary types --format=list                      # Simple list format
    """
    console = Console()
    
    if type_filter == 'all' or type_filter == 'summary-type':
        _show_summary_types(console, output_format, entity_type_filter)
    
    if type_filter == 'all' or type_filter == 'entity-type':
        _show_entity_types(console, output_format)


def _show_summary_types(console: Console, output_format: str, entity_type_filter: str = None):
    """Show summary types with descriptions."""
    # Filter summary types by entity type if specified
    if entity_type_filter:
        # Map CLI entity type to EntityType enum
        entity_type_mapping = {
            'project': EntityType.PROJECT,
            'work-item': EntityType.WORK_ITEM,
            'task': EntityType.TASK,
            'idea': EntityType.IDEA,
        }
        entity_type_enum = entity_type_mapping[entity_type_filter]
        summary_types = SummaryType.get_appropriate_types(entity_type_enum)
        title = f"📝 Summary Types for {entity_type_filter.title()}"
    else:
        summary_types = list(SummaryType)
        title = "📝 Summary Types"
    
    if output_format == 'table':
        table = Table(title=title, show_header=True, header_style="bold blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        labels = SummaryType.labels()
        for summary_type in summary_types:
            table.add_row(summary_type.value, labels.get(summary_type.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(summary_types)} summary types[/dim]")
        if entity_type_filter:
            console.print(f"[dim]Filtered for entity type: {entity_type_filter}[/dim]")
    
    elif output_format == 'list':
        console.print(Panel(title, style="bold blue"))
        labels = SummaryType.labels()
        for summary_type in summary_types:
            console.print(f"  • {summary_type.value}: {labels.get(summary_type.value, '')}")
        if entity_type_filter:
            console.print(f"\n[dim]Filtered for entity type: {entity_type_filter}[/dim]")
    
    elif output_format == 'json':
        import json
        labels = SummaryType.labels()
        types_data = {
            "summary_types": [
                {"value": summary_type.value, "description": labels.get(summary_type.value, "")}
                for summary_type in summary_types
            ]
        }
        if entity_type_filter:
            types_data["entity_type_filter"] = entity_type_filter
        console.print(json.dumps(types_data, indent=2))


def _show_entity_types(console: Console, output_format: str):
    """Show entity types with descriptions."""
    if output_format == 'table':
        table = Table(title="📝 Entity Types", show_header=True, header_style="bold blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        entity_descriptions = {
            EntityType.PROJECT.value: "Project-level entities",
            EntityType.WORK_ITEM.value: "Work item-level entities",
            EntityType.TASK.value: "Task-level entities",
            EntityType.IDEA.value: "Idea-level entities",
        }
        
        for entity_type in EntityType:
            table.add_row(entity_type.value, entity_descriptions.get(entity_type.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(EntityType)} entity types[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("📝 Entity Types", style="bold blue"))
        entity_descriptions = {
            EntityType.PROJECT.value: "Project-level entities",
            EntityType.WORK_ITEM.value: "Work item-level entities",
            EntityType.TASK.value: "Task-level entities",
            EntityType.IDEA.value: "Idea-level entities",
        }
        for entity_type in EntityType:
            console.print(f"  • {entity_type.value}: {entity_descriptions.get(entity_type.value, '')}")
    
    elif output_format == 'json':
        import json
        entity_descriptions = {
            EntityType.PROJECT.value: "Project-level entities",
            EntityType.WORK_ITEM.value: "Work item-level entities",
            EntityType.TASK.value: "Task-level entities",
            EntityType.IDEA.value: "Idea-level entities",
        }
        types_data = {
            "entity_types": [
                {"value": entity_type.value, "description": entity_descriptions.get(entity_type.value, "")}
                for entity_type in EntityType
            ]
        }
        console.print(json.dumps(types_data, indent=2))
