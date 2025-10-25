"""
apm task list-dependencies - List task dependencies (prerequisites and dependents)
"""

import click
from rich.table import Table
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_task_exists
from agentpm.core.database.methods import dependencies as dep_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command(name='list-dependencies')
@click.argument('task_id', type=int)
@click.option(
    '--format',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.pass_context
def list_dependencies(ctx: click.Context, task_id: int, format: str):
    """
    List task dependencies (what it depends on and what depends on it).

    \b
    Shows bidirectional relationships:
      Prerequisites: Tasks that must complete before this can start
      Dependents: Tasks that depend on this completing

    \b
    Example:
      apm task list-dependencies 5
      apm task list-dependencies 5 --format=json
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    validate_task_exists(db, task_id, ctx)
    task = task_methods.get_task(db, task_id)

    # Get dependencies (what this task depends on)
    prerequisites = dep_methods.get_task_dependencies(db, task_id)

    # Get dependents (what depends on this task)
    dependents = dep_methods.get_tasks_depending_on(db, task_id)

    if format == 'json':
        import json
        output = {
            'task_id': task_id,
            'task_name': task.name,
            'prerequisites': [
                {
                    'depends_on_task_id': d.depends_on_task_id,
                    'type': d.dependency_type,
                    'notes': d.notes
                }
                for d in prerequisites
            ],
            'dependents': [
                {
                    'dependent_task_id': d.task_id,
                    'type': d.dependency_type
                }
                for d in dependents
            ]
        }
        console.print(json.dumps(output, indent=2))
    else:
        # Rich table display
        console.print(f"\n📊 [bold cyan]Dependencies for Task #{task_id}: {task.name}[/bold cyan]\n")

        # Prerequisites table
        if prerequisites:
            table = Table(title="⬆️  Prerequisites (must complete first)")
            table.add_column("Task ID", style="cyan")
            table.add_column("Task Name", style="bold")
            table.add_column("Type", style="magenta")
            table.add_column("Status", style="yellow")

            for dep in prerequisites:
                dep_task = task_methods.get_task(db, dep.depends_on_task_id)
                if dep_task:
                    table.add_row(
                        str(dep.depends_on_task_id),
                        dep_task.name,
                        dep.dependency_type,
                        dep_task.status.value
                    )

            console.print(table)
            console.print()
        else:
            console.print("   [dim]No prerequisites[/dim]\n")

        # Dependents table
        if dependents:
            table = Table(title="⬇️  Dependents (waiting on this)")
            table.add_column("Task ID", style="cyan")
            table.add_column("Task Name", style="bold")
            table.add_column("Type", style="magenta")
            table.add_column("Status", style="yellow")

            for dep in dependents:
                dependent_task = task_methods.get_task(db, dep.task_id)
                if dependent_task:
                    table.add_row(
                        str(dep.task_id),
                        dependent_task.name,
                        dep.dependency_type,
                        dependent_task.status.value
                    )

            console.print(table)
            console.print()
        else:
            console.print("   [dim]No dependent tasks[/dim]\n")
