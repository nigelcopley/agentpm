"""
apm work-item bulk - Bulk operations for work items
"""

import click
import json
from typing import List, Dict, Any
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus, WorkItemType, Phase


@click.group(name='bulk')
def bulk():
    """
    Bulk operations for work items.

    Perform operations on multiple work items at once.
    """
    pass


@bulk.command(name='update')
@click.option(
    '--work-item-ids',
    help='Comma-separated list of work item IDs (e.g., "1,2,3")'
)
@click.option(
    '--project-id',
    type=int,
    help='Update all work items in a project'
)
@click.option(
    '--status',
    type=click.Choice(WorkItemStatus.choices(), case_sensitive=False),
    help='Set status for all work items'
)
@click.option(
    '--priority',
    type=click.IntRange(1, 5),
    help='Set priority for all work items'
)
@click.option(
    '--phase',
    type=click.Choice(Phase.choices(), case_sensitive=False),
    help='Set phase for all work items'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be updated without making changes'
)
@click.pass_context
def bulk_update(ctx: click.Context, work_item_ids: str, project_id: int, status: str, priority: int, phase: str, dry_run: bool):
    """
    Bulk update multiple work items.

    \b
    Examples:
      apm work-item bulk update --work-item-ids="1,2,3" --status=in_progress
      apm work-item bulk update --project-id=1 --priority=1
      apm work-item bulk update --work-item-ids="1,2" --phase=P1 --dry-run
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Determine which work items to update
    work_items_to_update = []
    
    if work_item_ids:
        try:
            wi_id_list = [int(wid.strip()) for wid in work_item_ids.split(',')]
            for wi_id in wi_id_list:
                work_item = WorkItemAdapter.get(db, wi_id)
                if work_item:
                    work_items_to_update.append(work_item)
                else:
                    console_err.print(f"⚠️  [yellow]Work item not found:[/yellow] {wi_id}")
        except ValueError:
            console_err.print("❌ [red]Invalid work item IDs format. Use comma-separated numbers.[/red]")
            raise click.Abort()
    
    elif project_id:
        work_items_to_update = WorkItemAdapter.list(db, project_id=project_id)
        if not work_items_to_update:
            console_err.print(f"❌ [red]No work items found for project:[/red] {project_id}")
            raise click.Abort()
    
    else:
        console_err.print("❌ [red]Must specify either --work-item-ids or --project-id[/red]")
        raise click.Abort()

    if not work_items_to_update:
        console_err.print("❌ [red]No work items to update[/red]")
        raise click.Abort()

    # Check if any updates provided
    updates = {}
    if status:
        updates['status'] = WorkItemStatus(status)
    if priority:
        updates['priority'] = priority
    if phase:
        updates['phase'] = Phase(phase)

    if not updates:
        console_err.print("❌ [red]No updates specified. Use --status, --priority, or --phase[/red]")
        raise click.Abort()

    # Show what will be updated
    console.print(f"\n📋 [cyan]Work items to update:[/cyan] {len(work_items_to_update)}")
    for wi in work_items_to_update[:10]:  # Show first 10
        console.print(f"   • #{wi.id}: {wi.name}")
    if len(work_items_to_update) > 10:
        console.print(f"   • ... and {len(work_items_to_update) - 10} more")

    console.print(f"\n🔄 [cyan]Updates to apply:[/cyan]")
    for key, value in updates.items():
        console.print(f"   • {key}: {value}")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk update
    if not click.confirm(f"\n⚠️  [yellow]Update {len(work_items_to_update)} work items?[/yellow]"):
        console.print("❌ [red]Bulk update cancelled.[/red]")
        raise click.Abort()

    # Perform bulk update
    updated_count = 0
    failed_count = 0
    
    for work_item in work_items_to_update:
        try:
            WorkItemAdapter.update(db, work_item.id, **updates)
            updated_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to update work item {work_item.id}:[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk update complete:[/green]")
    console.print(f"   • Updated: {updated_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")


@bulk.command(name='delete')
@click.option(
    '--work-item-ids',
    help='Comma-separated list of work item IDs (e.g., "1,2,3")'
)
@click.option(
    '--project-id',
    type=int,
    help='Delete all work items in a project'
)
@click.option(
    '--status',
    type=click.Choice(WorkItemStatus.choices(), case_sensitive=False),
    help='Delete all work items with this status'
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
def bulk_delete(ctx: click.Context, work_item_ids: str, project_id: int, status: str, force: bool, dry_run: bool):
    """
    Bulk delete multiple work items.

    \b
    Examples:
      apm work-item bulk delete --work-item-ids="1,2,3"
      apm work-item bulk delete --project-id=1
      apm work-item bulk delete --status=draft --dry-run
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Determine which work items to delete
    work_items_to_delete = []
    
    if work_item_ids:
        try:
            wi_id_list = [int(wid.strip()) for wid in work_item_ids.split(',')]
            for wi_id in wi_id_list:
                work_item = WorkItemAdapter.get(db, wi_id)
                if work_item:
                    work_items_to_delete.append(work_item)
                else:
                    console_err.print(f"⚠️  [yellow]Work item not found:[/yellow] {wi_id}")
        except ValueError:
            console_err.print("❌ [red]Invalid work item IDs format. Use comma-separated numbers.[/red]")
            raise click.Abort()
    
    elif project_id:
        work_items_to_delete = WorkItemAdapter.list(db, project_id=project_id)
        if not work_items_to_delete:
            console_err.print(f"❌ [red]No work items found for project:[/red] {project_id}")
            raise click.Abort()
    
    elif status:
        # Get all work items and filter by status
        from agentpm.cli.utils.project import get_current_project_id
        current_project_id = get_current_project_id(ctx)
        all_work_items = WorkItemAdapter.list(db, project_id=current_project_id)
        work_items_to_delete = [wi for wi in all_work_items if wi.status.value == status]
    
    else:
        console_err.print("❌ [red]Must specify --work-item-ids, --project-id, or --status[/red]")
        raise click.Abort()

    if not work_items_to_delete:
        console_err.print("❌ [red]No work items to delete[/red]")
        raise click.Abort()

    # Count associated tasks
    from agentpm.core.database.adapters import TaskAdapter
    total_tasks = 0
    for wi in work_items_to_delete:
        tasks = TaskAdapter.list(db, work_item_id=wi.id)
        total_tasks += len(tasks)

    # Show what will be deleted
    console.print(f"\n🗑️  [red]Work items to delete:[/red] {len(work_items_to_delete)}")
    console.print(f"   Associated tasks: {total_tasks}")
    
    for wi in work_items_to_delete[:10]:  # Show first 10
        console.print(f"   • #{wi.id}: {wi.name} ({wi.status.value})")
    if len(work_items_to_delete) > 10:
        console.print(f"   • ... and {len(work_items_to_delete) - 10} more")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk deletion
    if not force:
        if not click.confirm(f"\n⚠️  [yellow]Permanently delete {len(work_items_to_delete)} work items and {total_tasks} tasks?[/yellow]"):
            console.print("❌ [red]Bulk deletion cancelled.[/red]")
            raise click.Abort()

    # Perform bulk deletion
    deleted_count = 0
    failed_count = 0
    
    for work_item in work_items_to_delete:
        try:
            success = WorkItemAdapter.delete(db, work_item.id)
            if success:
                deleted_count += 1
            else:
                failed_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to delete work item {work_item.id}:[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk deletion complete:[/green]")
    console.print(f"   • Deleted: {deleted_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")


@bulk.command(name='create')
@click.option(
    '--project-id',
    type=int,
    help='Project ID to create work items for (defaults to current project)'
)
@click.option(
    '--work-items-file',
    help='JSON file containing work item definitions'
)
@click.option(
    '--work-items-json',
    help='JSON string containing work item definitions'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be created without making changes'
)
@click.pass_context
def bulk_create(ctx: click.Context, project_id: int, work_items_file: str, work_items_json: str, dry_run: bool):
    """
    Bulk create multiple work items.

    \b
    Examples:
      apm work-item bulk create --work-items-json='[{"name":"Feature 1","type":"feature","priority":1}]'
      apm work-item bulk create --work-items-file=work_items.json
    """
    console = ctx.obj['console']
    console_err = ctx.obj['console_err']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get project ID
    if not project_id:
        from agentpm.cli.utils.project import get_current_project_id
        project_id = get_current_project_id(ctx)

    # Validate project exists
    from agentpm.core.database.adapters import ProjectAdapter
    project = ProjectAdapter.get(db, project_id)
    if not project:
        console_err.print(f"❌ [red]Project not found:[/red] {project_id}")
        raise click.Abort()

    # Get work item definitions
    work_item_definitions = []
    
    if work_items_file:
        try:
            with open(work_items_file, 'r') as f:
                work_item_definitions = json.load(f)
        except FileNotFoundError:
            console_err.print(f"❌ [red]File not found:[/red] {work_items_file}")
            raise click.Abort()
        except json.JSONDecodeError as e:
            console_err.print(f"❌ [red]Invalid JSON in file:[/red] {e}")
            raise click.Abort()
    
    elif work_items_json:
        try:
            work_item_definitions = json.loads(work_items_json)
        except json.JSONDecodeError as e:
            console_err.print(f"❌ [red]Invalid JSON string:[/red] {e}")
            raise click.Abort()
    
    else:
        console_err.print("❌ [red]Must specify either --work-items-file or --work-items-json[/red]")
        raise click.Abort()

    if not isinstance(work_item_definitions, list):
        console_err.print("❌ [red]Work item definitions must be a JSON array[/red]")
        raise click.Abort()

    if not work_item_definitions:
        console_err.print("❌ [red]No work item definitions provided[/red]")
        raise click.Abort()

    # Validate work item definitions
    from agentpm.core.database.models.work_item import WorkItem
    validated_work_items = []
    
    for i, wi_def in enumerate(work_item_definitions):
        try:
            # Set project_id
            wi_def['project_id'] = project_id
            
            # Create and validate work item
            work_item = WorkItem(**wi_def)
            validated_work_items.append(work_item)
        except Exception as e:
            console_err.print(f"❌ [red]Invalid work item definition {i+1}:[/red] {e}")
            raise click.Abort()

    # Show what will be created
    console.print(f"\n📋 [cyan]Work items to create:[/cyan] {len(validated_work_items)}")
    console.print(f"   Project: #{project_id} - {project.name}")
    
    for wi in validated_work_items:
        console.print(f"   • {wi.name} ({wi.type.value}, P{wi.priority})")

    if dry_run:
        console.print(f"\n✅ [green]Dry run complete. No changes made.[/green]")
        return

    # Confirm bulk creation
    if not click.confirm(f"\n⚠️  [yellow]Create {len(validated_work_items)} work items?[/yellow]"):
        console.print("❌ [red]Bulk creation cancelled.[/red]")
        raise click.Abort()

    # Perform bulk creation
    created_count = 0
    failed_count = 0
    created_work_items = []
    
    for work_item in validated_work_items:
        try:
            created_wi = WorkItemAdapter.create(db, work_item)
            created_work_items.append(created_wi)
            created_count += 1
        except Exception as e:
            console_err.print(f"❌ [red]Failed to create work item '{work_item.name}':[/red] {e}")
            failed_count += 1

    # Show results
    console.print(f"\n✅ [green]Bulk creation complete:[/green]")
    console.print(f"   • Created: {created_count}")
    if failed_count > 0:
        console.print(f"   • Failed: {failed_count}")
    
    if created_work_items:
        console.print(f"\n📚 [cyan]Created work items:[/cyan]")
        for wi in created_work_items:
            console.print(f"   • #{wi.id}: {wi.name}")
