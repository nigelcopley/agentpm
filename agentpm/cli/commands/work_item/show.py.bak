"""
apm work-item show - Show work item details command
"""

import click
from agentpm.core.database.adapters import WorkItemAdapter
from agentpm.core.database.methods import ideas as idea_methods
from agentpm.core.database.enums import WorkItemType
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('work_item_id', type=int)
@click.pass_context
def show(ctx: click.Context, work_item_id: int):
    """
    Show complete work item details.

    Displays work item information, associated tasks, and quality gate status.

    \b
    Example:
      apm work-item show 123
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get work item
    work_item = WorkItemAdapter.get(db, work_item_id)

    if not work_item:
        console.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        console.print("💡 [yellow]List work items with:[/yellow]")
        console.print("   apm work-item list\n")
        raise click.Abort()

    # Display work item details
    console.print(f"\n📋 [bold cyan]Work Item #{work_item.id}[/bold cyan]\n")
    console.print(f"[bold]Name:[/bold] {work_item.name}")
    console.print(f"[bold]Type:[/bold] {work_item.type.value}")
    console.print(f"[bold]Status:[/bold] {work_item.status.value}")
    console.print(f"[bold]Priority:[/bold] {work_item.priority}")
    if getattr(work_item, 'is_continuous', False) or WorkItemType.is_continuous_type(work_item.type):
        console.print("[bold]Continuous Backlog:[/bold] Yes (remains open for ongoing intake)")

    if work_item.description:
        console.print(f"\n[bold]Description:[/bold]\n{work_item.description}")

    # Show idea origin if applicable
    if hasattr(work_item, 'originated_from_idea_id') and work_item.originated_from_idea_id:
        console.print(f"\n[bold cyan]💡 Origin:[/bold cyan]")
        console.print(f"   Originated from Idea #{work_item.originated_from_idea_id}")
        
        # Try to get the original idea details
        original_idea = idea_methods.get_idea(db, work_item.originated_from_idea_id)
        if original_idea:
            console.print(f"   Original title: {original_idea.title}")
            console.print(f"   Original votes: {original_idea.votes}")
            if original_idea.tags:
                tags_str = ", ".join(original_idea.tags)
                console.print(f"   Original tags: {tags_str}")
            console.print(f"   [dim]View original idea: apm idea show {work_item.originated_from_idea_id}[/dim]")
        else:
            console.print(f"   [dim]Original idea not found[/dim]")

    # Show associated tasks
    from agentpm.core.database.methods import tasks as task_methods
    tasks = task_methods.list_tasks(db, work_item_id=work_item_id)

    if tasks:
        console.print(f"\n[bold]Tasks ({len(tasks)}):[/bold]")
        for task in tasks:
            console.print(f"  • [{task.type.value}] {task.name} ({task.status.value})")
    else:
        console.print("\n⚠️  [yellow]No tasks yet[/yellow]")

    # Show quality gate status
    console.print(f"\n[bold]Quality Gates:[/bold]")
    task_types = {t.type for t in tasks}

    if getattr(work_item, 'is_continuous', False) or WorkItemType.is_continuous_type(work_item.type):
        console.print("  Continuous backlogs have no mandatory task mix. Focus on monitoring ongoing intake and SLA metrics.")
        console.print()
        return

    if work_item.type == WorkItemType.FEATURE:
        console.print("  FEATURE work items require:")
        console.print(f"    {'✅' if any(t.type.value == 'design' for t in tasks) else '❌'} DESIGN task")
        console.print(f"    {'✅' if any(t.type.value == 'implementation' for t in tasks) else '❌'} IMPLEMENTATION task")
        console.print(f"    {'✅' if any(t.type.value == 'testing' for t in tasks) else '❌'} TESTING task")
        console.print(f"    {'✅' if any(t.type.value == 'documentation' for t in tasks) else '❌'} DOCUMENTATION task")

    console.print()
