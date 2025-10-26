"""
apm document unpublish - Remove document from public location
"""

import click
from rich.console import Console
from agentpm.cli.utils.services import get_database_service
from agentpm.core.services.document_publisher import DocumentPublisher, ValidationError


@click.command()
@click.argument('document_id', type=int)
@click.option('--reason', 'reason',
              help='Optional reason for unpublishing')
@click.pass_context
def unpublish(ctx: click.Context, document_id: int, reason: str):
    """
    Remove document from public location (docs/) and revert to approved state.

    Removes the document from the public docs/ directory while keeping the source
    in .agentpm/docs/. The document reverts to APPROVED lifecycle stage and can
    be republished later.

    \b
    Requirements:
      • Document must be in PUBLISHED lifecycle stage

    \b
    Actions Performed:
      1. Validates document is published
      2. Removes file from docs/ directory
      3. Updates lifecycle_stage to 'approved'
      4. Sets unpublished_date timestamp
      5. Creates audit log entry
      6. Source remains in .agentpm/docs/

    \b
    Examples:
      # Unpublish document
      apm document unpublish 25

      # Unpublish with reason
      apm document unpublish 25 --reason="Outdated content, needs revision"

    \b
    Notes:
      • The source document in .agentpm/docs/ is NOT deleted
      • Document can be republished after updates
      • Unpublishing does not change document content
      • Document reverts to APPROVED state (can be edited and republished)

    \b
    See Also:
      apm document publish <id>       # Publish to public location
      apm document list-unpublished   # Show publishable documents
      apm document show <id>          # View document details
    """
    console = ctx.obj['console']
    db = ctx.obj['db_service']

    try:
        # Initialize publisher service
        publisher = DocumentPublisher(db)

        # Attempt to unpublish
        console.print(f"\n📥 Unpublishing document {document_id}...")
        success = publisher.unpublish(
            document_id=document_id,
            reason=reason
        )

        if success:
            console.print()
            console.print(f"✅ [green]Document successfully unpublished![/green]")
            console.print()
            console.print(f"   [cyan]Document ID:[/cyan] {document_id}")
            if reason:
                console.print(f"   [cyan]Reason:[/cyan] {reason}")
            console.print()
            console.print("💡 [dim]The document has been removed from docs/ but remains in .agentpm/docs/[/dim]")
            console.print("💡 [dim]Document is now in APPROVED state and can be republished later[/dim]")
            console.print()
        else:
            console.print()
            console.print(f"❌ [red]Failed to unpublish document[/red]")
            console.print()
            raise click.Abort()

    except ValidationError as e:
        console.print()
        console.print(f"❌ [red]Validation error: {e}[/red]")
        console.print()
        console.print("💡 [yellow]Common issues:[/yellow]")
        console.print("   • Document must be in PUBLISHED state (use: apm document show <id>)")
        console.print("   • Document may already be unpublished")
        console.print()
        raise click.Abort()

    except Exception as e:
        console.print()
        console.print(f"❌ [red]Error unpublishing document: {e}[/red]")
        console.print()
        raise click.Abort()
