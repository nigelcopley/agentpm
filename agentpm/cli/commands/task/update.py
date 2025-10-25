"""
apm task update - Update task fields command
"""

import click
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.database.enums import TaskType
from agentpm.core.workflow.type_validators import TypeSpecificValidators, TASK_TYPE_MAX_HOURS


@click.command(name='update')
@click.argument('task_id', type=int)
@click.option('--name', help='Update task name')
@click.option('--description', '-d', help='Update task description')
@click.option('--effort', type=float, help='Update effort estimate (validates against type limit)')
@click.option('--priority', '-p', type=click.IntRange(1, 5), help='Update priority (1-5)')
@click.option('--assigned-to', help='Update assigned agent')
@click.option('--quality-metadata', help='Update quality metadata (JSON string)')
@click.pass_context
def update(ctx: click.Context, task_id: int, name: str, description: str,
           effort: float, priority: int, assigned_to: str, quality_metadata: str):
    """
    Update task fields.

    Updates one or more task fields. Time-box validation is enforced
    if effort is changed. Only specified fields are updated.

    \b
    Examples:
      apm task update 5 --name "New task name"
      apm task update 5 --effort 3.5
      apm task update 5 --description "Updated description" --priority 1
      apm task update 5 --assigned-to backend-agent
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get current task
    task = TaskAdapter.get(db, task_id)

    if not task:
        console_err.print(f"\n❌ [red]Task not found:[/red] ID {task_id}\n")
        console_err.print("💡 [yellow]List tasks with:[/yellow]")
        console_err.print("   apm task list\n")
        raise click.Abort()

    # Check if any updates provided
    if not any([name, description, effort is not None, priority, assigned_to, quality_metadata]):
        console_err.print("\n⚠️  [yellow]No updates specified[/yellow]\n")
        console_err.print("💡 [cyan]Specify at least one field to update:[/cyan]")
        console_err.print("   --name, --description, --effort, --priority, --assigned-to, --quality-metadata\n")
        console_err.print("Example:")
        console_err.print(f"   apm task update {task_id} --effort 3.5 --priority 1\n")
        raise click.Abort()

    # Validate effort if changing (time-box enforcement)
    if effort is not None:
        validation = TypeSpecificValidators.validate_time_box(task.type, effort)
        if not validation.valid:
            max_hours = TASK_TYPE_MAX_HOURS.get(task.type, 8.0)
            console_err.print(f"\n❌ [red]Validation Error:[/red] {validation.reason}")
            console_err.print(f"\n💡 [yellow]Suggestions:[/yellow]")
            console_err.print(f"   • Reduce effort to ≤{max_hours}h for {task.type.value} tasks")
            console_err.print(f"   • Current effort: {task.effort_hours}h")
            console_err.print(f"   • You specified: {effort}h\n")
            raise click.Abort()

    # Validate agent if changing
    if assigned_to:
        from agentpm.cli.utils.validation import validate_agent_exists
        from agentpm.core.database.methods import work_items as wi_methods

        # Get work item to find project_id
        work_item = wi_methods.get_work_item(db, task.work_item_id)
        if not work_item:
            console_err.print(f"\n❌ [red]Work item not found:[/red] ID {task.work_item_id}\n")
            raise click.Abort()

        # Validate agent exists (CI-001 compliance)
        validate_agent_exists(db, work_item.project_id, assigned_to, ctx)

    # Build updates dictionary
    updates = {}
    if name:
        updates['name'] = name
    if description:
        updates['description'] = description
    if effort is not None:
        updates['effort_hours'] = effort
    if priority:
        updates['priority'] = priority
    if assigned_to:
        updates['assigned_to'] = assigned_to
    if quality_metadata:
        # Validate JSON format and convert to dict
        import json
        try:
            metadata_dict = json.loads(quality_metadata)  # Parse JSON to dict
            updates['quality_metadata'] = metadata_dict  # Store as dict, not string
        except json.JSONDecodeError as e:
            console_err.print(f"\n❌ [red]Invalid JSON:[/red] {e}\n")
            console_err.print("💡 [yellow]Provide valid JSON string:[/yellow]")
            console_err.print('   --quality-metadata \'{"key": "value"}\'')
            raise click.Abort()

    # Update task
    try:
        # Use update_task method with keyword arguments
        updated_task = TaskAdapter.update(db, task_id, **updates)

        # Show what changed
        console.print(f"\n✅ [green]Task updated:[/green] #{updated_task.id} {updated_task.name}")

        if name:
            console.print(f"   Name: → {name}")
        if description:
            console.print(f"   Description: → {description[:50]}...")
        if effort is not None:
            max_hours = TASK_TYPE_MAX_HOURS.get(task.type, 8.0)
            console.print(f"   Effort: → {effort}h / {max_hours}h max ✓")
        if priority:
            console.print(f"   Priority: → P{priority}")
        if assigned_to:
            console.print(f"   Assigned to: → {assigned_to}")
        if quality_metadata:
            console.print(f"   Quality metadata: → Updated ✓")

        console.print(f"\n📚 [cyan]Next steps:[/cyan]")
        console.print(f"   apm task show {task_id}  # View updated details\n")

    except Exception as e:
        console_err.print(f"\n❌ [red]Update failed:[/red] {e}\n")
        raise click.Abort()
