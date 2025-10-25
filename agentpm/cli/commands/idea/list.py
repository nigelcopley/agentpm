"""
apm idea list - List ideas with filters command
"""

import click
from rich.table import Table
from agentpm.core.database.enums import IdeaStatus
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service


@click.command(name='list')
@click.option(
    '--status', '-s',
    type=click.Choice([s.value for s in IdeaStatus], case_sensitive=False),
    help='Filter by status (idea, research, design, accepted, converted, rejected)'
)
@click.option(
    '--tags', '-t',
    multiple=True,
    help='Filter by tags (OR condition - matches ANY tag)'
)
@click.option(
    '--limit', '-l',
    type=int,
    help='Maximum number of ideas to show'
)
@click.option(
    '--search',
    help='Search in idea titles and descriptions (case-insensitive)'
)
@click.option(
    '--show-rejected',
    is_flag=True,
    help='Include rejected ideas (excluded by default)'
)
@click.pass_context
def list_ideas(ctx: click.Context, status: str, tags: tuple, limit: int, search: str, show_rejected: bool):
    """
    List ideas with filtering and sorting.

    Ideas are sorted by votes (descending), then by creation date (newest first).
    Rejected ideas are excluded by default unless --show-rejected is specified.

    \b
    Examples:
      # All active ideas
      apm idea list

      # Top 10 most voted ideas
      apm idea list --limit 10

      # Ideas in specific status
      apm idea list --status=accepted
      apm idea list --status=research

      # Ideas by tags (OR condition)
      apm idea list --tags security --tags ux

      # Include rejected ideas
      apm idea list --show-rejected

      # Search in ideas
      apm idea list --search "oauth"
      
      # Combine filters
      apm idea list --status=design --tags backend --limit 5
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Convert status string to enum if provided
    status_enum = IdeaStatus(status) if status else None

    # Get ideas
    ideas = IdeaAdapter.list(
        db,
        project_id=project_id,
        status=status_enum,
        tags=list(tags) if tags else None
    )

    # Filter out rejected unless requested
    if not show_rejected:
        ideas = [idea for idea in ideas if idea.status != IdeaStatus.REJECTED]
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        ideas = [
            idea for idea in ideas 
            if search_lower in idea.title.lower() or 
               (idea.description and search_lower in idea.description.lower())
        ]

    if not ideas:
        console.print("\n[yellow]No ideas found.[/yellow]")
        console.print("\n💡 Create your first idea:")
        console.print('   apm idea create "Your idea title"\n')
        return

    # Create Rich table
    table = Table(title=f"Ideas ({len(ideas)} total)")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Votes", justify="right")
    table.add_column("Tags", style="dim")
    table.add_column("Source", style="dim")

    for idea in ideas:
        # Status styling
        status_style = {
            IdeaStatus.IDEA: "yellow",
            IdeaStatus.RESEARCH: "blue",
            IdeaStatus.DESIGN: "magenta",
            IdeaStatus.ACTIVE: "green",
            IdeaStatus.CONVERTED: "green bold",
            IdeaStatus.REJECTED: "red"
        }.get(idea.status, "white")

        tags_str = ", ".join(idea.tags[:3]) if idea.tags else ""
        if len(idea.tags) > 3:
            tags_str += f" +{len(idea.tags) - 3}"

        table.add_row(
            str(idea.id),
            idea.title[:50] + "..." if len(idea.title) > 50 else idea.title,
            f"[{status_style}]{idea.status.value}[/{status_style}]",
            str(idea.votes),
            tags_str,
            idea.source.value
        )

    console.print()
    console.print(table)
    console.print()

    # Show summary stats
    status_counts = {}
    for idea in ideas:
        status_counts[idea.status] = status_counts.get(idea.status, 0) + 1

    console.print("[cyan]Summary:[/cyan]")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        console.print(f"   {status.value}: {count}")

    # Show next actions
    console.print("\n📚 [cyan]Next actions:[/cyan]")
    console.print(f"   apm idea show <id>              # View details")
    console.print(f"   apm idea vote <id> --upvote     # Vote on idea")
    console.print(f"   apm idea transition <id> <state> # Progress workflow\n")
