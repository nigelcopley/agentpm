"""
apm idea vote - Vote on ideas command
"""

import click
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.option(
    '--upvote',
    is_flag=True,
    help='Upvote the idea (+1)'
)
@click.option(
    '--downvote',
    is_flag=True,
    help='Downvote the idea (-1)'
)
@click.pass_context
def vote(ctx: click.Context, idea_id: int, upvote: bool, downvote: bool):
    """
    Vote on an idea (+1 upvote or -1 downvote).

    Votes help teams prioritize ideas democratically. Ideas with more
    votes rise to the top of the list and get more attention.

    Votes cannot make the total go below 0 (minimum is 0).
    Cannot vote on ideas in terminal states (converted/rejected).

    \b
    Examples:
      # Upvote
      apm idea vote 5 --upvote

      # Downvote
      apm idea vote 5 --downvote
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate flags
    if upvote and downvote:
        console.print("\n[red]❌ Error: Cannot specify both --upvote and --downvote[/red]\n")
        raise click.Abort()

    if not upvote and not downvote:
        console.print("\n[red]❌ Error: Must specify either --upvote or --downvote[/red]\n")
        raise click.Abort()

    # Determine delta
    delta = +1 if upvote else -1

    # Vote on idea
    try:
        updated_idea = IdeaAdapter.vote(db, idea_id, delta=delta)
    except ValueError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]\n")
        raise click.Abort()

    # Success message
    vote_type = "upvoted" if upvote else "downvoted"
    emoji = "👍" if upvote else "👎"

    console.print(f"\n✅ [green]Idea {vote_type} {emoji}[/green]")
    console.print(f"   {updated_idea.title}")
    console.print(f"   Total votes: [cyan]{updated_idea.votes}[/cyan]")

    # Show ranking context
    console.print(f"\n📊 [cyan]Use votes for prioritization:[/cyan]")
    console.print(f"   apm idea list --limit 10    # Top 10 voted ideas\n")
