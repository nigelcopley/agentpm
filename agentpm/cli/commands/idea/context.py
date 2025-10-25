"""
apm idea context - Show comprehensive idea context command
"""

import click
from agentpm.core.context.service import ContextService
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.pass_context
def context(ctx: click.Context, idea_id: int):
    """
    Show comprehensive context for an idea.

    Displays hierarchical context including:
    - Idea details (title, description, status, votes, tags)
    - Project context (inherited)
    - Phase alignment with work items
    - Conversion readiness assessment
    - Recommended next steps

    \b
    Examples:
      # Show context for idea
      apm idea context 5

      # Use with other commands
      apm idea context 12 && apm idea convert 12
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get idea context
    context_service = ContextService(db, project_root)
    context_data = context_service.get_idea_context(idea_id)

    if not context_data:
        console.print(f"\n[red]❌ Idea {idea_id} not found[/red]")
        raise click.Abort()

    # Display context with Rich formatting
    console.print(f"\n[bold blue]📋 Idea Context: #{idea_id}[/bold blue]")
    console.print()

    # Idea details
    idea = context_data['idea']
    console.print(f"[bold]Title:[/bold] {idea['title']}")
    if idea['description']:
        console.print(f"[bold]Description:[/bold] {idea['description']}")
    
    console.print(f"[bold]Status:[/bold] [yellow]{idea['status']}[/yellow]")
    console.print(f"[bold]Source:[/bold] {idea['source']}")
    console.print(f"[bold]Votes:[/bold] {idea['votes']}")
    
    if idea['tags']:
        tags_str = ", ".join(idea['tags'])
        console.print(f"[bold]Tags:[/bold] {tags_str}")
    
    if idea['created_by']:
        console.print(f"[bold]Created by:[/bold] {idea['created_by']}")
    
    console.print(f"[bold]Created:[/bold] {idea['created_at']}")
    console.print()

    # Phase alignment
    phase_align = context_data['phase_alignment']
    console.print(f"[bold cyan]🔄 Phase Alignment:[/bold cyan]")
    console.print(f"   {phase_align['alignment_note']}")
    console.print()

    # Conversion readiness
    readiness = context_data['conversion_readiness']
    if readiness['ready']:
        console.print(f"[bold green]✅ Conversion Ready:[/bold green] {readiness['message']}")
        if readiness['recommended_phase']:
            console.print(f"   Recommended phase: [cyan]{readiness['recommended_phase']}[/cyan]")
    else:
        console.print(f"[bold yellow]⚠️  Not Ready:[/bold yellow] {readiness['message']}")
        if readiness['recommended_phase']:
            console.print(f"   Recommended phase: [cyan]{readiness['recommended_phase']}[/cyan]")
    console.print()

    # Next steps
    next_steps = context_data['next_steps']
    if next_steps:
        console.print(f"[bold cyan]📚 Next Steps:[/bold cyan]")
        for step in next_steps:
            console.print(f"   • {step}")
        console.print()

    # Project context (summary)
    project = context_data.get('project', {})
    if project:
        console.print(f"[bold blue]🏗️  Project Context:[/bold blue]")
        console.print(f"   Project: {project.get('name', 'Unknown')}")
        console.print(f"   Tech Stack: {', '.join(project.get('tech_stack', []))}")
        if project.get('detected_frameworks'):
            console.print(f"   Frameworks: {', '.join(project['detected_frameworks'])}")
        console.print()

    # Confidence score
    confidence = context_data.get('idea_confidence', {})
    if confidence:
        score = confidence.get('score', 0.5)
        band = confidence.get('band', 'YELLOW')
        band_colors = {'GREEN': 'green', 'YELLOW': 'yellow', 'RED': 'red'}
        color = band_colors.get(band, 'yellow')
        console.print(f"[bold]Context Quality:[/bold] [{color}]{band}[/{color}] ({score:.2f})")
        console.print()

    # Conversion status
    if idea['converted_to_work_item_id']:
        console.print(f"[bold green]✅ Converted:[/bold green] Work Item #{idea['converted_to_work_item_id']}")
        console.print(f"   Converted at: {idea['converted_at']}")
        console.print(f"   [dim]View work item: apm work-item show {idea['converted_to_work_item_id']}[/dim]")
    elif idea['rejection_reason']:
        console.print(f"[bold red]❌ Rejected:[/bold red] {idea['rejection_reason']}")
    else:
        console.print(f"[bold yellow]🔄 Active:[/bold yellow] Ready for conversion or further development")
        console.print(f"   [dim]Convert: apm idea convert {idea_id}[/dim]")

    console.print()