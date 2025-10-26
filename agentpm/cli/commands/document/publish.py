"""
apm document publish - Publish document from private to public location
"""

import click
from rich.console import Console
from agentpm.cli.utils.services import get_database_service
from agentpm.core.services.document_publisher import DocumentPublisher, ValidationError


@click.command()
@click.argument('document_id', type=int)
@click.option('--actor', 'actor',
              default='system',
              help='User/agent performing publish (default: system)')
@click.option('--trigger', 'trigger',
              type=click.Choice(['manual', 'auto', 'phase_change']),
              default='manual',
              help='Trigger type (default: manual)')
@click.pass_context
def publish(ctx: click.Context, document_id: int, actor: str, trigger: str):
    """
    Publish document from private (.agentpm/docs/) to public (docs/) location.

    Moves approved documents from the private workspace to the public documentation
    directory. The document must be in APPROVED lifecycle stage and have PUBLIC
    visibility to be published.

    \b
    Requirements:
      • Document must be in APPROVED lifecycle stage
      • Document must have PUBLIC visibility
      • Document must have content

    \b
    Actions Performed:
      1. Validates document can be published
      2. Copies file from .agentpm/docs/ to docs/
      3. Updates lifecycle_stage to 'published'
      4. Sets published_path and published_date
      5. Creates audit log entry

    \b
    Examples:
      # Publish document manually
      apm document publish 25

      # Publish with custom actor
      apm document publish 25 --actor=john@example.com

      # Publish with trigger type
      apm document publish 25 --trigger=phase_change

    \b
    See Also:
      apm document unpublish <id>     # Remove from public location
      apm document list-unpublished   # Show publishable documents
      apm document show <id>          # View document details
    """
    console = ctx.obj['console']
    db = ctx.obj['db_service']

    try:
        # Initialize publisher service
        publisher = DocumentPublisher(db)

        # Attempt to publish
        console.print(f"\n📤 Publishing document {document_id}...")
        result = publisher.publish(
            document_id=document_id,
            actor=actor,
            trigger=trigger
        )

        if result.success:
            console.print()
            console.print(f"✅ [green]Document successfully published![/green]")
            console.print()
            console.print(f"   [cyan]Document ID:[/cyan] {result.document_id}")
            console.print(f"   [cyan]Source:[/cyan] {result.source_path}")
            console.print(f"   [cyan]Published to:[/cyan] {result.destination_path}")
            console.print(f"   [cyan]Lifecycle:[/cyan] {result.lifecycle_stage}")
            console.print()
            console.print("💡 [dim]The document is now publicly accessible in the docs/ directory[/dim]")
            console.print()
        else:
            console.print()
            console.print(f"❌ [red]Failed to publish document: {result.error}[/red]")
            console.print()
            raise click.Abort()

    except ValidationError as e:
        console.print()
        console.print(f"❌ [red]Validation error: {e}[/red]")
        console.print()
        console.print("💡 [yellow]Common issues:[/yellow]")
        console.print("   • Document must be in APPROVED state (use: apm document show <id>)")
        console.print("   • Document must have PUBLIC visibility")
        console.print("   • Document must have content to publish")
        console.print()
        raise click.Abort()

    except Exception as e:
        console.print()
        console.print(f"❌ [red]Error publishing document: {e}[/red]")
        console.print()
        raise click.Abort()
