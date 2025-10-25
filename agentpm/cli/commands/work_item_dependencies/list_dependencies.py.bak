"""
apm work-item list-dependencies - Show work item dependencies
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_work_item_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import work_items as wi_methods


@click.command(name='list-dependencies')
@click.argument('work_item_id', type=int)
@click.option(
    '--format', 'output_format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format (table or json)'
)
@click.pass_context
def list_dependencies(ctx: click.Context, work_item_id: int, output_format: str):
    """
    Show work item dependencies (prerequisites and dependents).

    \b
    Examples:
      apm work-item list-dependencies 5
      apm work-item list-dependencies 5 --format json
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate work item exists
    validate_work_item_exists(db, work_item_id, ctx)

    # Get work item details
    work_item = wi_methods.get_work_item(db, work_item_id)

    # Get dependencies (prerequisites)
    dependencies = dep_methods.get_work_item_dependencies(db, work_item_id)

    # Get dependents (work items that depend on this one)
    dependents = dep_methods.get_work_item_dependents(db, work_item_id)

    if output_format == 'json':
        # JSON output
        import json
        result = {
            'work_item_id': work_item_id,
            'work_item_name': work_item.name,
            'prerequisites': [
                {
                    'work_item_id': dep.depends_on_work_item_id,
                    'dependency_type': dep.dependency_type,
                    'notes': dep.notes,
                    'created_at': dep.created_at.isoformat() if dep.created_at else None
                }
                for dep in dependencies
            ],
            'dependents': [
                {
                    'work_item_id': dep.work_item_id,
                    'dependency_type': dep.dependency_type,
                    'notes': dep.notes,
                    'created_at': dep.created_at.isoformat() if dep.created_at else None
                }
                for dep in dependents
            ]
        }
        console.print(json.dumps(result, indent=2))
    else:
        # Table output
        console.print(f"\n📊 [bold]Dependencies for Work Item #{work_item_id}: {work_item.name}[/bold]\n")

        # Prerequisites
        if dependencies:
            console.print("                     ⬆️  Prerequisites (must complete first)                     ")
            console.print("┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓")
            console.print("┃ Work Item ID ┃ Work Item Name                                        ┃ Type ┃ Status   ┃")
            console.print("┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩")
            
            for dep in dependencies:
                dep_wi = wi_methods.get_work_item(db, dep.depends_on_work_item_id)
                dep_type_icon = "🔒" if dep.dependency_type == 'hard' else "💡"
                console.print(f"│ {dep.depends_on_work_item_id:<11} │ {dep_wi.name[:50]:<50} │ {dep_type_icon} {dep.dependency_type:<4} │ {dep_wi.status.value:<9} │")
            
            console.print("└─────────┴──────────────────────────────────────────────────┴──────┴──────────┘")
        else:
            console.print("                     ⬆️  Prerequisites (must complete first)                     ")
            console.print("   [dim]No prerequisites[/dim]")

        # Dependents
        if dependents:
            console.print("\n                        ⬇️  Dependents (waiting on this)                         ")
            console.print("┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓")
            console.print("┃ Work Item ID ┃ Work Item Name                                        ┃ Type ┃ Status   ┃")
            console.print("┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩")
            
            for dep in dependents:
                dep_wi = wi_methods.get_work_item(db, dep.work_item_id)
                dep_type_icon = "🔒" if dep.dependency_type == 'hard' else "💡"
                console.print(f"│ {dep.work_item_id:<11} │ {dep_wi.name[:50]:<50} │ {dep_type_icon} {dep.dependency_type:<4} │ {dep_wi.status.value:<9} │")
            
            console.print("└─────────┴──────────────────────────────────────────────────┴──────┴──────────┘")
        else:
            console.print("\n                        ⬇️  Dependents (waiting on this)                         ")
            console.print("   [dim]No dependents[/dim]")

        console.print()
