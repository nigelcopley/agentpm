"""
apm idea create - Create new idea command
"""

import click
from agentpm.core.database.models import Idea
from agentpm.core.database.enums import IdeaSource, IdeaStatus
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('title')
@click.option(
    '--description', '-d',
    help='Detailed description of the idea'
)
@click.option(
    '--source', '-s',
    type=click.Choice([
        'user',
        'ai_suggestion',
        'brainstorming_session',
        'customer_feedback',
        'competitor_analysis',
        'other'
    ], case_sensitive=False),
    default='user',
    help='Origin of the idea (default: user)'
)
@click.option(
    '--created-by',
    help='Creator identifier (username, email, agent name)'
)
@click.option(
    '--tags', '-t',
    multiple=True,
    help='Tags for categorization (can be specified multiple times)'
)
@click.pass_context
def create(ctx: click.Context, title: str, description: str, source: str,
           created_by: str, tags: tuple):
    """
    Create new idea for lightweight brainstorming.

    Ideas provide low-friction capture of concepts before committing to
    formal work items. They can be voted on, refined, and eventually
    converted to work items.

    \b
    Examples:
      # Simple idea
      apm idea create "Add OAuth2 authentication"

      # With description and tags
      apm idea create "Add OAuth2 authentication" \\
        --description "Support Google/GitHub sign-in for better UX" \\
        --tags security --tags ux --tags quick-win

      # From customer feedback
      apm idea create "Dark mode support" \\
        --source customer_feedback \\
        --created-by "jane@company.com" \\
        --tags ui --tags accessibility

      # AI suggestion
      apm idea create "Implement caching layer" \\
        --source ai_suggestion \\
        --created-by "aipm-architecture-agent" \\
        --tags performance --tags backend
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Create idea model
    idea = Idea(
        project_id=project_id,
        title=title,
        description=description,
        source=IdeaSource(source),
        created_by=created_by,
        tags=list(tags) if tags else [],
        status=IdeaStatus.IDEA,
        votes=0
    )

    # Create in database
    created_idea = IdeaAdapter.create(db, idea)

    # Success message with Rich formatting
    console.print(f"\n✅ [green]Idea created:[/green] {created_idea.title}")
    console.print(f"   ID: [cyan]{created_idea.id}[/cyan]")
    console.print(f"   Status: [yellow]{created_idea.status.value}[/yellow]")
    console.print(f"   Source: {created_idea.source.value}")
    console.print(f"   Votes: {created_idea.votes}")

    if created_idea.created_by:
        console.print(f"   Created by: {created_idea.created_by}")

    if created_idea.tags:
        tags_str = ", ".join(created_idea.tags)
        console.print(f"   Tags: {tags_str}")

    if created_idea.description:
        console.print(f"\n   {created_idea.description}")

    # Show next steps
    console.print(f"\n📚 [cyan]Next steps:[/cyan]")
    console.print(f"   • apm idea vote {created_idea.id} --upvote          # Upvote this idea")
    console.print(f"   • apm idea transition {created_idea.id} research   # Start research phase")
    console.print(f"   • apm idea list --status=idea                      # See all ideas\n")
