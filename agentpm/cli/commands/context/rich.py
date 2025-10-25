"""
apm context rich - Manage rich context for entities (ideas, work items, tasks)
"""

import click
import json
from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists, validate_work_item_exists
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import ideas as idea_methods
from agentpm.core.database.adapters import ContextAdapter
from agentpm.core.database.enums import EntityType, ContextType, DocumentType
from agentpm.core.context.assembly_service import ContextAssemblyService


@click.group()
def rich():
    """Manage rich context for entities (ideas, work items, tasks)."""
    pass


@rich.command()
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices()),
              required=True,
              help='Type of entity')
@click.option('--entity-id', 'entity_id',
              type=int,
              required=True,
              help='ID of the entity')
@click.option('--context-type', 'context_type',
              type=click.Choice([
                  'business_pillars_context',
                  'market_research_context', 
                  'competitive_analysis_context',
                  'quality_gates_context',
                  'stakeholder_context',
                  'technical_context',
                  'implementation_context',
                  'idea_context',
                  'idea_to_work_item_mapping'
              ]),
              required=True,
              help='Type of rich context to create')
@click.option('--data', 'context_data',
              type=str,
              required=True,
              help='Rich context data as JSON string')
@click.option('--confidence', 'confidence_score',
              type=float,
              help='Confidence score (0.0-1.0, auto-calculated if not provided)')
@click.pass_context
def create(ctx: click.Context, entity_type: str, entity_id: int, context_type: str, 
           context_data: str, confidence_score: float):
    """Create rich context for an entity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)

    try:
        db = get_database_service(project_root)
        # Parse context data
        data = json.loads(context_data)
        
        # Map entity type string to enum using safe conversion
        entity_type_enum = EntityType.from_string(entity_type)
        
        # Map context type string to enum
        context_type_map = {
            'business_pillars_context': ContextType.BUSINESS_PILLARS_CONTEXT,
            'market_research_context': ContextType.MARKET_RESEARCH_CONTEXT,
            'competitive_analysis_context': ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
            'quality_gates_context': ContextType.QUALITY_GATES_CONTEXT,
            'stakeholder_context': ContextType.STAKEHOLDER_CONTEXT,
            'technical_context': ContextType.TECHNICAL_CONTEXT,
            'implementation_context': ContextType.IMPLEMENTATION_CONTEXT,
            'idea_context': ContextType.IDEA_CONTEXT,
            'idea_to_work_item_mapping': ContextType.IDEA_TO_WORK_ITEM_MAPPING
        }

        # Create rich context
        created_context = ContextAdapter.create_rich_context(
            db=db,
            entity_type=entity_type_enum,
            entity_id=entity_id,
            context_type=context_type_map[context_type],
            context_data=data,
            confidence_score=confidence_score
        )

        console.print(f"✅ [green]Rich context created successfully[/green]")
        console.print(f"   Context ID: {created_context.id}")
        console.print(f"   Entity: {entity_type} #{entity_id}")
        console.print(f"   Type: {context_type}")
        console.print(f"   Confidence: {created_context.confidence_score:.0%}")

    except json.JSONDecodeError:
        console.print("❌ [red]Invalid JSON in context data[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"❌ [red]Error creating rich context: {e}[/red]")
        raise click.Abort()


@rich.command()
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices()),
              required=True,
              help='Type of entity')
@click.option('--entity-id', 'entity_id',
              type=int,
              required=True,
              help='ID of the entity')
@click.option('--context-types', 'context_types',
              type=str,
              help='Comma-separated list of context types to show (all if not specified)')
@click.option('--format', 'output_format',
              type=click.Choice(['rich', 'json']),
              default='rich',
              help='Output format')
@click.pass_context
def show(ctx: click.Context, entity_type: str, entity_id: int, context_types: str, output_format: str):
    """Show rich context for an entity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)

    try:
        db = get_database_service(project_root)
        # Map entity type string to enum using safe conversion
        entity_type_enum = EntityType.from_string(entity_type)

        # Parse context types if specified
        context_type_list = None
        if context_types:
            context_type_map = {
                'business_pillars_context': ContextType.BUSINESS_PILLARS_CONTEXT,
                'market_research_context': ContextType.MARKET_RESEARCH_CONTEXT,
                'competitive_analysis_context': ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
                'quality_gates_context': ContextType.QUALITY_GATES_CONTEXT,
                'stakeholder_context': ContextType.STAKEHOLDER_CONTEXT,
                'technical_context': ContextType.TECHNICAL_CONTEXT,
                'implementation_context': ContextType.IMPLEMENTATION_CONTEXT,
                'idea_context': ContextType.IDEA_CONTEXT,
                'idea_to_work_item_mapping': ContextType.IDEA_TO_WORK_ITEM_MAPPING
            }
            context_type_list = [context_type_map[ct.strip()] for ct in context_types.split(',')]

        # Get rich contexts
        rich_contexts = ContextAdapter.get_rich_contexts_by_entity(
            db=db,
            entity_type=entity_type_enum,
            entity_id=entity_id,
            context_types=context_type_list
        )

        if output_format == 'json':
            # JSON output for agents
            output = {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'contexts': {}
            }
            
            for context in rich_contexts:
                output['contexts'][context.context_type.value] = {
                    'context_data': context.context_data,
                    'confidence_score': context.confidence_score,
                    'confidence_band': context.confidence_band.value if context.confidence_band else None,
                    'created_at': context.created_at.isoformat() if context.created_at else None,
                    'updated_at': context.updated_at.isoformat() if context.updated_at else None
                }
            
            console.print(json.dumps(output, indent=2, default=str))
        else:
            # Rich human-readable output
            if not rich_contexts:
                console.print(f"ℹ️  [yellow]No rich context found for {entity_type} #{entity_id}[/yellow]")
                return

            console.print()
            console.print(Panel.fit(
                f"[bold cyan]{entity_type.title()} #{entity_id} Rich Context[/bold cyan]",
                title="📊 Rich Context",
                subtitle=f"{len(rich_contexts)} context(s) found"
            ))
            console.print()

            for context in rich_contexts:
                # Context header
                band_colors = {'GREEN': 'green', 'YELLOW': 'yellow', 'RED': 'red'}
                band_color = band_colors.get(context.confidence_band.value, 'white') if context.confidence_band else 'white'
                
                console.print(f"[bold cyan]─── {context.context_type.value.replace('_', ' ').title()} ───[/bold cyan]")
                console.print(f"  [dim]Confidence:[/dim] [{band_color}]{context.confidence_band.value}[/{band_color}] ({context.confidence_score:.0%})")
                
                if context.created_at:
                    console.print(f"  [dim]Created:[/dim] {context.created_at.strftime('%Y-%m-%d %H:%M')}")
                if context.updated_at:
                    console.print(f"  [dim]Updated:[/dim] {context.updated_at.strftime('%Y-%m-%d %H:%M')}")
                
                console.print()

                # Context data
                if context.context_data:
                    _display_context_data(console, context.context_data)
                else:
                    console.print("  [dim]No context data[/dim]")
                
                console.print()

    except Exception as e:
        console.print(f"❌ [red]Error showing rich context: {e}[/red]")
        raise click.Abort()


@rich.command()
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices()),
              required=True,
              help='Type of entity')
@click.option('--entity-id', 'entity_id',
              type=int,
              required=True,
              help='ID of the entity')
@click.option('--required-types', 'required_types',
              type=str,
              help='Comma-separated list of required context types (uses defaults if not specified)')
@click.pass_context
def validate(ctx: click.Context, entity_type: str, entity_id: int, required_types: str):
    """Validate completeness of rich context for an entity."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)

    try:
        db = get_database_service(project_root)
        # Map entity type string to enum using safe conversion
        entity_type_enum = EntityType.from_string(entity_type)

        # Parse required types if specified
        required_type_list = None
        if required_types:
            context_type_map = {
                'business_pillars_context': ContextType.BUSINESS_PILLARS_CONTEXT,
                'market_research_context': ContextType.MARKET_RESEARCH_CONTEXT,
                'competitive_analysis_context': ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
                'quality_gates_context': ContextType.QUALITY_GATES_CONTEXT,
                'stakeholder_context': ContextType.STAKEHOLDER_CONTEXT,
                'technical_context': ContextType.TECHNICAL_CONTEXT,
                'implementation_context': ContextType.IMPLEMENTATION_CONTEXT,
                'idea_context': ContextType.IDEA_CONTEXT,
                'idea_to_work_item_mapping': ContextType.IDEA_TO_WORK_ITEM_MAPPING
            }
            required_type_list = [context_type_map[ct.strip()] for ct in required_types.split(',')]

        # Validate completeness
        validation_result = ContextAdapter.validate_rich_context_completeness(
            db=db,
            entity_type=entity_type_enum,
            entity_id=entity_id,
            required_context_types=required_type_list
        )

        # Display results
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{entity_type.title()} #{entity_id} Context Validation[/bold cyan]",
            title="✅ Context Validation",
            subtitle=f"Completeness: {validation_result['completeness_score']:.0%}"
        ))
        console.print()

        # Completeness score
        score = validation_result['completeness_score']
        if score == 1.0:
            console.print("✅ [green]Context is complete[/green]")
        elif score >= 0.8:
            console.print("⚠️  [yellow]Context is mostly complete[/yellow]")
        elif score >= 0.5:
            console.print("⚠️  [yellow]Context is partially complete[/yellow]")
        else:
            console.print("❌ [red]Context is incomplete[/red]")

        console.print(f"   Score: {score:.0%} ({validation_result['total_present']}/{validation_result['total_required']})")
        console.print()

        # Present context types
        if validation_result['present_context_types']:
            console.print("[green]✅ Present Context Types:[/green]")
            for context_type in validation_result['present_context_types']:
                console.print(f"   • {context_type.replace('_', ' ').title()}")
            console.print()

        # Missing context types
        if validation_result['missing_context_types']:
            console.print("[red]❌ Missing Context Types:[/red]")
            for context_type in validation_result['missing_context_types']:
                console.print(f"   • {context_type.replace('_', ' ').title()}")
            console.print()

    except Exception as e:
        console.print(f"❌ [red]Error validating rich context: {e}[/red]")
        raise click.Abort()


@rich.command()
@click.option('--task-id', 'task_id',
              type=int,
              required=True,
              help='Task ID to assemble hierarchical context for')
@click.option('--include-idea', 'include_idea',
              is_flag=True,
              help='Include idea context if available')
@click.option('--format', 'output_format',
              type=click.Choice(['rich', 'json']),
              default='rich',
              help='Output format')
@click.pass_context
def assemble(ctx: click.Context, task_id: int, include_idea: bool, output_format: str):
    """Assemble hierarchical rich context from Idea → Work Item → Task."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)

    try:
        db = get_database_service(project_root)
        # Validate task exists
        validate_task_exists(db, task_id, ctx)

        # Assemble hierarchical context
        assembly_service = ContextAssemblyService(db, project_root)
        hierarchical_context = assembly_service.assemble_hierarchical_rich_context(
            task_id=task_id,
            include_idea_context=include_idea
        )

        if output_format == 'json':
            # JSON output for agents
            console.print(json.dumps(hierarchical_context, indent=2, default=str))
        else:
            # Rich human-readable output
            console.print()
            console.print(Panel.fit(
                f"[bold cyan]Task #{task_id} Hierarchical Rich Context[/bold cyan]",
                title="🔄 Context Assembly",
                subtitle=f"Include idea context: {'Yes' if include_idea else 'No'}"
            ))
            console.print()

            # Display each level
            for level, level_data in hierarchical_context.items():
                console.print(f"[bold cyan]─── {level.title()} Context ───[/bold cyan]")
                console.print(f"  [dim]ID:[/dim] {level_data['id']}")
                console.print(f"  [dim]Name:[/dim] {level_data['name']}")
                
                if level_data['context']:
                    console.print(f"  [dim]Context Types:[/dim] {len(level_data['context'])}")
                    for context_type, context_data in level_data['context'].items():
                        console.print(f"    • {context_type.replace('_', ' ').title()}")
                else:
                    console.print("  [dim]No rich context[/dim]")
                
                console.print()

    except Exception as e:
        console.print(f"❌ [red]Error assembling hierarchical context: {e}[/red]")
        raise click.Abort()


@rich.command()
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices()),
              required=True,
              help='Type of entity')
@click.option('--entity-id', 'entity_id',
              type=int,
              required=True,
              help='ID of the entity')
@click.option('--context-type', 'context_type',
              type=click.Choice([
                  'business_pillars_context',
                  'market_research_context', 
                  'competitive_analysis_context',
                  'quality_gates_context',
                  'stakeholder_context',
                  'technical_context',
                  'implementation_context',
                  'idea_context',
                  'idea_to_work_item_mapping'
              ]),
              required=True,
              help='Type of rich context to generate document from')
@click.option('--document-type', 'document_type',
              type=click.Choice([
                  'business_pillars_analysis',
                  'market_research_report',
                  'competitive_analysis',
                  'quality_gates_spec',
                  'stakeholder_analysis',
                  'technical_specification',
                  'implementation_plan'
              ]),
              required=True,
              help='Type of document to generate')
@click.option('--output', 'output_file',
              type=click.Path(),
              help='Output file path (prints to console if not specified)')
@click.pass_context
def generate_doc(ctx: click.Context, entity_type: str, entity_id: int, context_type: str,
                 document_type: str, output_file: str):
    """Generate document from rich context data."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)

    try:
        db = get_database_service(project_root)
        # Map entity type string to enum using safe conversion
        entity_type_enum = EntityType.from_string(entity_type)
        
        # Map context type string to enum
        context_type_map = {
            'business_pillars_context': ContextType.BUSINESS_PILLARS_CONTEXT,
            'market_research_context': ContextType.MARKET_RESEARCH_CONTEXT,
            'competitive_analysis_context': ContextType.COMPETITIVE_ANALYSIS_CONTEXT,
            'quality_gates_context': ContextType.QUALITY_GATES_CONTEXT,
            'stakeholder_context': ContextType.STAKEHOLDER_CONTEXT,
            'technical_context': ContextType.TECHNICAL_CONTEXT,
            'implementation_context': ContextType.IMPLEMENTATION_CONTEXT,
            'idea_context': ContextType.IDEA_CONTEXT,
            'idea_to_work_item_mapping': ContextType.IDEA_TO_WORK_ITEM_MAPPING
        }

        # Map document type string to enum
        document_type_map = {
            'business_pillars': DocumentType.BUSINESS_PILLARS,
            'market_research': DocumentType.MARKET_RESEARCH,
            'competitive_analysis': DocumentType.COMPETITIVE_ANALYSIS,
            'quality_gates_spec': DocumentType.QUALITY_GATES_SPEC,
            'stakeholder_analysis': DocumentType.STAKEHOLDER_ANALYSIS,
            'technical_specification': DocumentType.TECHNICAL_SPECIFICATION,
            'implementation_plan': DocumentType.IMPLEMENTATION_PLAN
        }

        # Generate document
        result = ContextAdapter.generate_documents_from_rich_context(
            db=db,
            entity_type=entity_type_enum,
            entity_id=entity_id,
            context_type=context_type_map[context_type],
            document_type=document_type_map[document_type]
        )

        if not result['success']:
            console.print(f"❌ [red]Error generating document: {result['error']}[/red]")
            raise click.Abort()

        # Output document
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(result['content'])
            console.print(f"✅ [green]Document generated: {output_path}[/green]")
        else:
            console.print()
            console.print(Panel(
                result['content'],
                title=f"📄 {document_type.replace('_', ' ').title()}",
                subtitle=f"From {entity_type} #{entity_id} - {context_type.replace('_', ' ').title()}"
            ))

    except Exception as e:
        console.print(f"❌ [red]Error generating document: {e}[/red]")
        raise click.Abort()


def _display_context_data(console: Console, context_data: dict, indent: int = 2):
    """Display context data in a readable format."""
    prefix = " " * indent
    
    for key, value in context_data.items():
        if isinstance(value, dict):
            console.print(f"{prefix}[cyan]{key.replace('_', ' ').title()}:[/cyan]")
            _display_context_data(console, value, indent + 2)
        elif isinstance(value, list):
            console.print(f"{prefix}[cyan]{key.replace('_', ' ').title()}:[/cyan]")
            for item in value:
                if isinstance(item, dict):
                    _display_context_data(console, item, indent + 4)
                else:
                    console.print(f"{prefix}  • {item}")
        else:
            console.print(f"{prefix}[cyan]{key.replace('_', ' ').title()}:[/cyan] {value}")


# Add the rich command group to the main context module
def register_rich_commands():
    """Register rich context commands with the main CLI."""
    from agentpm.cli.commands.context import __init__ as context_init
    
    # Add rich command group to context commands
    context_init.cli.add_command(rich, name='rich')


