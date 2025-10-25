"""
apm idea update - Update idea details command
"""

import click
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.option(
    '--title',
    help='Update title'
)
@click.option(
    '--description', '-d',
    help='Update description'
)
@click.option(
    '--add-tag',
    multiple=True,
    help='Add tags (can be specified multiple times)'
)
@click.option(
    '--remove-tag',
    multiple=True,
    help='Remove tags (can be specified multiple times)'
)
@click.option(
    '--created-by',
    help='Update creator identifier'
)
@click.pass_context
def update(ctx: click.Context, idea_id: int, title: str, description: str,
           add_tag: tuple, remove_tag: tuple, created_by: str):
    """
    Update idea details (title, description, tags, creator).

    Cannot update ideas in terminal states (converted/rejected).
    Use --add-tag and --remove-tag to modify tags incrementally.

    \b
    Examples:
      # Update title
      apm idea update 5 --title "Better title"

      # Update description
      apm idea update 5 --description "Detailed explanation..."

      # Add tags
      apm idea update 5 --add-tag security --add-tag ux

      # Remove tags
      apm idea update 5 --remove-tag old-tag

      # Update creator
      apm idea update 5 --created-by "jane@company.com"

      # Multiple updates
      apm idea update 5 \\
        --title "Improved title" \\
        --description "Better description" \\
        --add-tag quick-win \\
        --remove-tag wip
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Validate at least one update flag provided
    if not any([title, description, add_tag, remove_tag, created_by]):
        console.print("\n[red]❌ Error: Must specify at least one field to update[/red]")
        console.print("\nAvailable options:")
        console.print("  --title, --description, --add-tag, --remove-tag, --created-by\n")
        raise click.Abort()

    # Get idea
    idea = IdeaAdapter.get(db, idea_id)

    if not idea:
        console.print(f"\n[red]❌ Error: Idea {idea_id} not found[/red]\n")
        raise click.Abort()

    # Check if terminal
    if idea.is_terminal():
        console.print(f"\n[red]❌ Error: Cannot update idea in terminal state '{idea.status.value}'[/red]\n")
        raise click.Abort()

    # Apply updates
    updated_fields = []

    if title:
        idea.title = title
        updated_fields.append("title")

    if description is not None:  # Allow empty string to clear description
        idea.description = description
        updated_fields.append("description")

    if created_by:
        idea.created_by = created_by
        updated_fields.append("created_by")

    # Handle tags
    if add_tag:
        for tag in add_tag:
            if tag not in idea.tags:
                idea.tags.append(tag)
        updated_fields.append(f"added {len(add_tag)} tag(s)")

    if remove_tag:
        removed_count = 0
        for tag in remove_tag:
            if tag in idea.tags:
                idea.tags.remove(tag)
                removed_count += 1
        if removed_count > 0:
            updated_fields.append(f"removed {removed_count} tag(s)")

    # Update in database
    try:
        updated_idea = IdeaAdapter.update(db, idea)
    except ValueError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]\n")
        raise click.Abort()

    # Success message
    console.print(f"\n✅ [green]Idea updated:[/green] {updated_idea.title}")
    console.print(f"   ID: [cyan]{updated_idea.id}[/cyan]")

    if updated_fields:
        console.print(f"   Updated: {', '.join(updated_fields)}")

    if updated_idea.tags:
        tags_str = ", ".join(updated_idea.tags)
        console.print(f"   Tags: {tags_str}")

    console.print(f"\n📚 [cyan]Next actions:[/cyan]")
    console.print(f"   apm idea show {idea_id}              # View changes")
    console.print(f"   apm idea transition {idea_id} <state> # Progress workflow\n")
