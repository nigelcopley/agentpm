"""
apm work-item validate - Validate work item and transition to validated status
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.enums import WorkItemStatus
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.workflow import WorkflowService, WorkflowError
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service


@click.command()
@click.argument('work_item_id', type=int)
@click.pass_context
def validate(ctx: click.Context, work_item_id: int):
    """
    Validate work item and transition to validated status.

    Checks all validation requirements and transitions if all pass:
    - Description ≥50 characters
    - Business context set
    - Required task types present (type-specific)
    - No forbidden task types (type-specific)

    \b
    Example:
      apm work-item validate 1
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)

    # Get work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        raise click.Abort()

    # Check if already validated or beyond
    if work_item.status.value in ['validated', 'accepted', 'in_progress', 'blocked', 'review', 'completed', 'archived']:
        console.print(f"\n✅ [green]Work item already validated[/green]")
        console.print(f"   Current status: {work_item.status.value}\n")
        return

    # Try to transition via WorkflowService
    try:
        updated_wi = workflow.transition_work_item(work_item_id, WorkItemStatus.READY)

        console.print(f"\n🔍 [cyan]Validating Work Item #{work_item_id}...[/cyan]\n")

        # Show validation checklist
        console.print("✅ [green]Basic Requirements:[/green]")
        console.print(f"   ✅ Description: {len(work_item.description or '')} characters (≥50 required)")
        console.print(f"   ✅ Type: {work_item.type.value}")

        # Show task type requirements
        tasks = task_methods.list_tasks(db, work_item_id=work_item_id)

        from agentpm.core.workflow.work_item_requirements import WORK_ITEM_TASK_REQUIREMENTS

        requirements = WORK_ITEM_TASK_REQUIREMENTS.get(work_item.type)

        if requirements and requirements.required:
            console.print(f"\n✅ [green]Required Tasks ({work_item.type.value} type):[/green]")
            task_types = {t.type for t in tasks}
            for req_type in requirements.required:
                matching = [t for t in tasks if t.type == req_type]
                if matching:
                    console.print(f"   ✅ {req_type.value.upper()} task: Task #{matching[0].id}")
                else:
                    console.print(f"   ❌ {req_type.value.upper()} task: Missing")

        if requirements and requirements.forbidden:
            console.print(f"\n✅ [green]Forbidden Tasks Check:[/green]")
            for forb_type in requirements.forbidden:
                matching = [t for t in tasks if t.type == forb_type]
                if matching:
                    console.print(f"   ❌ {forb_type.value.upper()} task found (forbidden for {work_item.type.value})")
                else:
                    console.print(f"   ✅ No {forb_type.value.upper()} tasks (good)")

        console.print(f"\n✅ [bold green]Work item validated successfully![/bold green]")
        console.print(f"   Status: {work_item.status.value} → {updated_wi.status.value}")

        console.print(f"\n📚 [cyan]Next step:[/cyan]")
        console.print(f"   apm work-item accept {work_item_id} --effort <hours>  # Accept with effort estimate\n")

    except WorkflowError as e:
        # Display the error message
        console.print(f"\n❌ [red]Validation failed:[/red] {e}\n")

        # Show helpful checklist
        console.print("📋 [yellow]Validation Requirements:[/yellow]\n")

        # Check description
        desc_len = len(work_item.description or '')
        if desc_len < 50:
            console.print(f"   ❌ Description: {desc_len} characters (need ≥50)")
        else:
            console.print(f"   ✅ Description: {desc_len} characters")

        # Check task types
        tasks = task_methods.list_tasks(db, work_item_id=work_item_id)
        task_types = {t.type for t in tasks}

        from agentpm.core.workflow.work_item_requirements import WORK_ITEM_TASK_REQUIREMENTS

        requirements = WORK_ITEM_TASK_REQUIREMENTS.get(work_item.type)

        if requirements and requirements.required:
            console.print(f"\n   Required task types for {work_item.type.value}:")
            for req_type in requirements.required:
                if req_type in task_types:
                    console.print(f"   ✅ {req_type.value.upper()} task")
                else:
                    console.print(f"   ❌ {req_type.value.upper()} task (missing)")

        if requirements and requirements.forbidden:
            console.print(f"\n   Forbidden task types:")
            for forb_type in requirements.forbidden:
                if forb_type in task_types:
                    console.print(f"   ❌ {forb_type.value.upper()} task found (remove this)")

        console.print(f"\n💡 [cyan]Fix the issues above, then run:[/cyan]")
        console.print(f"   apm work-item validate {work_item_id}\n")

        raise click.Abort()
