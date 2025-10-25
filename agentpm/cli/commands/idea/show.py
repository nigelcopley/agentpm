"""
apm idea show - Display idea details command
"""

import click
from rich.panel import Panel
from rich.table import Table
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.enums import IdeaStatus
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.pass_context
def show(ctx: click.Context, idea_id: int):
    """
    Display detailed information about an idea.

    Shows idea metadata, description, tags, votes, lifecycle state,
    and conversion status (if applicable).

    \b
    Examples:
      apm idea show 5
      apm idea show 12
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get idea
    idea = IdeaAdapter.get(db, idea_id)

    if not idea:
        console.print(f"\n[red]❌ Error: Idea {idea_id} not found[/red]\n")
        raise click.Abort()

    # Status styling
    status_style = {
        "idea": "yellow",
        "research": "blue",
        "design": "magenta",
        "accepted": "green",
        "converted": "green bold",
        "rejected": "red"
    }.get(idea.status.value, "white")

    # Build panel content
    content = []
    content.append(f"[bold]Title:[/bold] {idea.title}")
    content.append(f"[bold]Status:[/bold] [{status_style}]{idea.status.value}[/{status_style}]")
    content.append(f"[bold]Votes:[/bold] {idea.votes} 👍")
    content.append(f"[bold]Source:[/bold] {idea.source.value}")

    if idea.created_by:
        content.append(f"[bold]Created by:[/bold] {idea.created_by}")

    if idea.tags:
        tags_str = ", ".join(idea.tags)
        content.append(f"[bold]Tags:[/bold] {tags_str}")

    content.append(f"[bold]Created:[/bold] {idea.created_at.strftime('%Y-%m-%d %H:%M') if idea.created_at else 'N/A'}")
    content.append(f"[bold]Updated:[/bold] {idea.updated_at.strftime('%Y-%m-%d %H:%M') if idea.updated_at else 'N/A'}")

    # Show rejection reason if rejected
    if idea.status.value == "rejected" and idea.rejection_reason:
        content.append(f"\n[bold red]Rejection Reason:[/bold red]")
        content.append(f"[red]{idea.rejection_reason}[/red]")

    # Show conversion info if converted
    if idea.status.value == "converted" and idea.converted_to_work_item_id:
        content.append(f"\n[bold green]Converted to Work Item:[/bold green]")
        content.append(f"[green]Work Item ID: {idea.converted_to_work_item_id}[/green]")
        if idea.converted_at:
            content.append(f"[green]Converted: {idea.converted_at.strftime('%Y-%m-%d %H:%M')}[/green]")

        # Try to get work item details
        work_item = wi_methods.get_work_item(db, idea.converted_to_work_item_id)
        if work_item:
            content.append(f"[green]Work Item: {work_item.name} ({work_item.type.value})[/green]")
            content.append(f"[green]Status: {work_item.status.value}[/green]")

    panel_content = "\n".join(content)

    # Display panel
    console.print()
    console.print(Panel(
        panel_content,
        title=f"💡 Idea #{idea.id}",
        border_style="cyan"
    ))

    # Show description if present
    if idea.description:
        console.print(f"\n[bold]Description:[/bold]")
        console.print(f"{idea.description}")

    # Phase alignment information
    aligned_phase = IdeaStatus.get_aligned_phase(idea.status)
    console.print(f"\n[bold cyan]🔄 Phase Alignment:[/bold cyan]")
    if aligned_phase:
        console.print(f"   Idea {idea.status.value} → Work Item {aligned_phase}")
    else:
        console.print(f"   Idea {idea.status.value} (no work item phase alignment)")
    console.print()

    # Conversion readiness
    readiness = IdeaStatus.get_conversion_readiness(idea.status)
    console.print(f"[bold cyan]📋 Conversion Readiness:[/bold cyan]")
    if readiness['ready']:
        console.print(f"   [green]✅ {readiness['message']}[/green]")
        if readiness['recommended_phase']:
            console.print(f"   Recommended phase: [cyan]{readiness['recommended_phase']}[/cyan]")
    else:
        console.print(f"   [yellow]⚠️  {readiness['message']}[/yellow]")
        if readiness['recommended_phase']:
            console.print(f"   Recommended phase: [cyan]{readiness['recommended_phase']}[/cyan]")
    console.print()

    # Show workflow state machine
    if not idea.is_terminal():
        console.print(f"[cyan]Allowed Transitions:[/cyan]")
        allowed = idea.get_allowed_transitions()
        for status in allowed:
            console.print(f"   • {status.value}")

        console.print(f"\n📚 [cyan]Next actions:[/cyan]")
        if "research" in [s.value for s in allowed]:
            console.print(f"   apm idea transition {idea_id} research")
        if "design" in [s.value for s in allowed]:
            console.print(f"   apm idea transition {idea_id} design")
        if "accepted" in [s.value for s in allowed]:
            console.print(f"   apm idea transition {idea_id} accepted")
        if idea.can_convert():
            console.print(f"   apm idea convert {idea_id} --type=feature")
        console.print(f"   apm idea vote {idea_id} --upvote")
        console.print(f"   apm idea update {idea_id} --description=\"...\"")
        console.print(f"   apm idea reject {idea_id} \"Reason...\"")
        console.print(f"   apm idea context {idea_id}  # Show comprehensive context")
    else:
        console.print(f"\n[yellow]⚠️  Idea is in terminal state (no further transitions allowed)[/yellow]")

    console.print()
