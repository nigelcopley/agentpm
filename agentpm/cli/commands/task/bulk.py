"""
apm task bulk - Bulk operations for tasks
"""

import click
import json
from typing import List, Dict, Any
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.database.enums import TaskStatus, TaskType


@click.group(name='bulk')
def bulk():
    """
    Bulk operations for tasks.

    Perform operations on multiple tasks at once.
    """
    pass


@bulk.command(name='update')
@click.option(
    '--task-ids',
    help='Comma-separated list of task IDs (e.g., "1,2,3")'
)
@click.option(
    '--work-item-id',
    type=int,
    help='Update all tasks in a work item'
)
@click.option(
    '--status',
    type=click.Choice(TaskStatus.choices(), case_sensitive=False),
    help='Set status for all tasks'
)
@click.option(
    '--priority',
    type=click.IntRange(1, 5),
    help='Set priority for all tasks'
)
@click.option(
    '--assigned-to',
    help='Assign all tasks to agent/user'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be updated without making changes'
)
@click.pass_context
def bulk_update(ctx: click.Context, task_ids: str, work_item_id: int, status: str, priority: int, assigned_to: str, dry_run: bool):
    """
    Bulk update multiple tasks.

    \b
    Examples:
      apm task bulk update --task-ids="1,2,3" --status=in_progress
      apm task bulk update --work-item-id=5 --priority=1
      apm task bulk update --task-ids="1,2" --assigned-to=backend-agent --dry-run
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Determine which tasks to update
    tasks_to_update = []
    
    if task_ids:
        try:
            task_id_list = [int(tid.strip()) for tid in task_ids.split(',')]
            for task_id in task_id_list:
                task = TaskAdapter.get(db, task_id)
                if task:
                    tasks_to_update.append(task)
                else:
                    console_err.print(f"⚠️  [yellow]Task not found:[/yellow] {task_id}")
        except ValueError:
            console_err.print("❌ [red]Invalid task IDs format. Use comma-separated numbers.[/red]")
            raise click.Abort()
    
    elif work_item_id:
        tasks_to_update = TaskAdapter.list(db, work_item_id=work_item_id)
        if not tasks_to_update:
            console_err.print(f"❌ [red]No tasks found for work item:[/red] {work_item_id}")
            raise click.Abort()
    
    else:
        console_err.print("❌ [red]Must specify either --task-ids or --work-item-id[/red]")
        raise click.Abort()

    if not tasks_to_update:
        console_err.print("❌ [red]No tasks to update[/red]")
        raise click.Abort()

    # Check if any updates provided
    updates = {}
    if status:
        updates['status'] = TaskStatus(status)
    if priority:
        updates['priority'] = priority
    if assigned_to:
        updates['assigned_to'] = assigned_to

    if not updates:
        console_err.print("❌ [red]No updates specified. Use --status, --priority, or --assigned-to[/red]")
        raise click.Abort()

    # Show what will be updated
    console.print(f"\n📋 [cyan]Tasks to update:[/cyan] {len(tasks_to_update)}")
    for task in tasks_to_update[:10]:  # Show first 10
        console.print(f"   • #{task.id}: {task.name}")
    if len(tasks_to_update) > 10:
        console.print(f"   • ... and {len(tasks_to_update) - 10} more")

    console.print(f"\n🔄 [cyan]Updates to apply:[/cyan]")
    for key, value in updates.items():
        console.print(f"   • {key}: {value}")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk update
    if not click.confirm(f"\n⚠️  [yellow]Update {len(tasks_to_update)} tasks?[/yellow]"):
        console.print("❌ [red]Bulk update cancelled.[/red]")
        raise click.Abort()

    # Perform bulk update
    updated_count = 0
    failed_count = 0
    
    for task in tasks_to_update:
        try:
            TaskAdapter.update(db, task.id, **updates)
            updated_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to update task {task.id}:[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk update complete:[/green]")
    console.print(f"   • Updated: {updated_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")


@bulk.command(name='delete')
@click.option(
    '--task-ids',
    help='Comma-separated list of task IDs (e.g., "1,2,3")'
)
@click.option(
    '--work-item-id',
    type=int,
    help='Delete all tasks in a work item'
)
@click.option(
    '--status',
    type=click.Choice(TaskStatus.choices(), case_sensitive=False),
    help='Delete all tasks with this status'
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Force deletion without confirmation'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be deleted without making changes'
)
@click.pass_context
def bulk_delete(ctx: click.Context, task_ids: str, work_item_id: int, status: str, force: bool, dry_run: bool):
    """
    Bulk delete multiple tasks.

    \b
    Examples:
      apm task bulk delete --task-ids="1,2,3"
      apm task bulk delete --work-item-id=5
      apm task bulk delete --status=draft --dry-run
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Determine which tasks to delete
    tasks_to_delete = []
    
    if task_ids:
        try:
            task_id_list = [int(tid.strip()) for tid in task_ids.split(',')]
            for task_id in task_id_list:
                task = TaskAdapter.get(db, task_id)
                if task:
                    tasks_to_delete.append(task)
                else:
                    console_err.print(f"⚠️  [yellow]Task not found:[/yellow] {task_id}")
        except ValueError:
            console_err.print("❌ [red]Invalid task IDs format. Use comma-separated numbers.[/red]")
            raise click.Abort()
    
    elif work_item_id:
        tasks_to_delete = TaskAdapter.list(db, work_item_id=work_item_id)
        if not tasks_to_delete:
            console_err.print(f"❌ [red]No tasks found for work item:[/red] {work_item_id}")
            raise click.Abort()
    
    elif status:
        # Get all tasks and filter by status
        from agentpm.cli.utils.project import get_current_project_id
        project_id = get_current_project_id(ctx)
        from agentpm.core.database.adapters import WorkItemAdapter
        work_items = WorkItemAdapter.list(db, project_id=project_id)
        
        for wi in work_items:
            tasks = TaskAdapter.list(db, work_item_id=wi.id)
            tasks_to_delete.extend([t for t in tasks if t.status.value == status])
    
    else:
        console_err.print("❌ [red]Must specify --task-ids, --work-item-id, or --status[/red]")
        raise click.Abort()

    if not tasks_to_delete:
        console_err.print("❌ [red]No tasks to delete[/red]")
        raise click.Abort()

    # Show what will be deleted
    console.print(f"\n🗑️  [red]Tasks to delete:[/red] {len(tasks_to_delete)}")
    for task in tasks_to_delete[:10]:  # Show first 10
        console.print(f"   • #{task.id}: {task.name} ({task.status.value})")
    if len(tasks_to_delete) > 10:
        console.print(f"   • ... and {len(tasks_to_delete) - 10} more")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk deletion
    if not force:
        if not click.confirm(f"\n⚠️  [yellow]Permanently delete {len(tasks_to_delete)} tasks?[/yellow]"):
            console.print("❌ [red]Bulk deletion cancelled.[/red]")
            raise click.Abort()

    # Perform bulk deletion
    deleted_count = 0
    failed_count = 0
    
    for task in tasks_to_delete:
        try:
            success = TaskAdapter.delete(db, task.id)
            if success:
                deleted_count += 1
            else:
                failed_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to delete task {task.id}:[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk deletion complete:[/green]")
    console.print(f"   • Deleted: {deleted_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")


@bulk.command(name='create')
@click.option(
    '--work-item-id',
    type=int,
    required=True,
    help='Work item ID to create tasks for'
)
@click.option(
    '--tasks-file',
    help='JSON file containing task definitions'
)
@click.option(
    '--tasks-json',
    help='JSON string containing task definitions'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be created without making changes'
)
@click.pass_context
def bulk_create(ctx: click.Context, work_item_id: int, tasks_file: str, tasks_json: str, dry_run: bool):
    """
    Bulk create multiple tasks.

    \b
    Examples:
      apm task bulk create --work-item-id=5 --tasks-json='[{"name":"Task 1","type":"implementation","effort":3}]'
      apm task bulk create --work-item-id=5 --tasks-file=tasks.json
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate work item exists
    from agentpm.core.database.adapters import WorkItemAdapter
    work_item = WorkItemAdapter.get(db, work_item_id)
    if not work_item:
        console_err.print(f"❌ [red]Work item not found:[/red] {work_item_id}")
        raise click.Abort()

    # Get task definitions
    task_definitions = []
    
    if tasks_file:
        try:
            with open(tasks_file, 'r') as f:
                task_definitions = json.load(f)
        except FileNotFoundError:
            console_err.print(f"❌ [red]File not found:[/red] {tasks_file}")
            raise click.Abort()
        except json.JSONDecodeError as e:
            console_err.print(f"❌ [red]Invalid JSON in file:[/red] {e}")
            raise click.Abort()
    
    elif tasks_json:
        try:
            task_definitions = json.loads(tasks_json)
        except json.JSONDecodeError as e:
            console_err.print(f"❌ [red]Invalid JSON string:[/red] {e}")
            raise click.Abort()
    
    else:
        console_err.print("❌ [red]Must specify either --tasks-file or --tasks-json[/red]")
        raise click.Abort()

    if not isinstance(task_definitions, list):
        console_err.print("❌ [red]Task definitions must be a JSON array[/red]")
        raise click.Abort()

    if not task_definitions:
        console_err.print("❌ [red]No task definitions provided[/red]")
        raise click.Abort()

    # Validate task definitions
    from agentpm.core.database.models.task import Task
    validated_tasks = []
    
    for i, task_def in enumerate(task_definitions):
        try:
            # Set work_item_id
            task_def['work_item_id'] = work_item_id
            
            # Create and validate task
            task = Task(**task_def)
            validated_tasks.append(task)
        except Exception as e:
            console_err.print(f"❌ [red]Invalid task definition {i+1}:[/red] {e}")
            raise click.Abort()

    # Show what will be created
    console.print(f"\n📋 [cyan]Tasks to create:[/cyan] {len(validated_tasks)}")
    console.print(f"   Work Item: #{work_item_id} - {work_item.name}")
    
    for task in validated_tasks:
        console.print(f"   • {task.name} ({task.type.value}, {task.effort_hours}h)")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk creation
    if not click.confirm(f"\n⚠️  [yellow]Create {len(validated_tasks)} tasks?[/yellow]"):
        console.print("❌ [red]Bulk creation cancelled.[/red]")
        raise click.Abort()

    # Perform bulk creation
    created_count = 0
    failed_count = 0
    created_tasks = []
    
    for task in validated_tasks:
        try:
            created_task = TaskAdapter.create(db, task)
            created_tasks.append(created_task)
            created_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to create task '{task.name}':[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk creation complete:[/green]")
    console.print(f"   • Created: {created_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")
    
    if created_tasks:
        console.print(f"\n📚 [cyan]Created tasks:[/cyan]")
        for task in created_tasks:
            console.print(f"   • #{task.id}: {task.name}")
