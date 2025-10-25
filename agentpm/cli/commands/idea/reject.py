"""
apm idea reject - Reject idea with reason command
"""

import click
from agentpm.core.database.adapters import IdeaAdapter
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.argument('idea_id', type=int)
@click.argument('reason')
@click.pass_context
def reject(ctx: click.Context, idea_id: int, reason: str):
    """
    Reject idea with reason (terminal state).

    Rejection is terminal - idea cannot be reopened. Rejection reason
    is required for audit trail and learning (minimum 10 characters).

    Ideas can be rejected from any non-terminal state.

    \b
    Examples:
      apm idea reject 5 "Duplicate of existing work item #15"
      apm idea reject 12 "Out of scope for current roadmap"
      apm idea reject 8 "Technical complexity too high vs business value"
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Reject idea with reason
    try:
        rejected_idea = IdeaAdapter.reject(db, idea_id, reason)
    except ValueError as e:
        console.print(f"\n[red]❌ Error: {e}[/red]\n")
        raise click.Abort()

    # Success message
    console.print(f"\n✅ [yellow]Idea rejected:[/yellow] {rejected_idea.title}")
    console.print(f"   ID: [cyan]{rejected_idea.id}[/cyan]")
    console.print(f"   Status: [red]{rejected_idea.status.value}[/red]")

    console.print(f"\n[yellow]Rejection Reason:[/yellow]")
    console.print(f"   {rejected_idea.rejection_reason}")

    # Show audit trail
    console.print(f"\n📋 [cyan]Rejection recorded in audit trail[/cyan]")
    console.print(f"   • Idea remains in database for learning")
    console.print(f"   • Use --show-rejected flag to view rejected ideas")
    console.print(f"   • apm idea list --show-rejected")
    console.print(f"   • apm idea show {idea_id}\n")
