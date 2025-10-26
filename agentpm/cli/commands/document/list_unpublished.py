"""
apm document list-unpublished - List documents that are approved and ready to publish
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from agentpm.cli.utils.services import get_database_service
from agentpm.core.services.document_publisher import DocumentPublisher


@click.command(name='list-unpublished')
@click.option('--limit', 'limit',
              type=int,
              default=50,
              help='Maximum number of documents to show (default: 50)')
@click.option('--output-format', 'output_format',
              type=click.Choice(['table', 'json']),
              default='table',
              help='Output format (default: table)')
@click.pass_context
def list_unpublished(ctx: click.Context, limit: int, output_format: str):
    """
    List documents that are approved and ready to be published.

    Shows documents that meet publishing criteria:
    - Lifecycle stage: APPROVED
    - Visibility: PUBLIC
    - Not yet published to docs/ directory

    These documents are in the private workspace (.agentpm/docs/) and can be
    moved to the public documentation directory using the publish command.

    \b
    Examples:
      # List all unpublished documents
      apm document list-unpublished

      # List with custom limit
      apm document list-unpublished --limit=20

      # List in JSON format
      apm document list-unpublished --output-format=json

    \b
    Filters Applied:
      • lifecycle_stage = 'approved'
      • visibility = 'public'
      • Excludes already published documents

    \b
    Publishing Workflow:
      1. Document is created (lifecycle: DRAFT)
      2. Submit for review: apm document submit-review <id>
      3. Approve: apm document approve <id>
      4. Publish: apm document publish <id>

    \b
    See Also:
      apm document publish <id>     # Publish document to docs/
      apm document show <id>        # View document details
      apm document list             # List all documents
    """
    console = ctx.obj['console']
    db = ctx.obj['db_service']

    try:
        # Initialize publisher service
        publisher = DocumentPublisher(db)

        # Get unpublished documents
        documents = publisher.list_unpublished_documents()

        # Apply limit
        if limit and len(documents) > limit:
            documents = documents[:limit]

        if output_format == 'json':
            # JSON output for programmatic use
            import json
            doc_data = []
            for doc in documents:
                doc_data.append({
                    'id': doc.id,
                    'entity_type': doc.entity_type.value,
                    'entity_id': doc.entity_id,
                    'file_path': doc.file_path,
                    'category': doc.category,
                    'document_type': doc.document_type.value if doc.document_type else None,
                    'title': doc.title,
                    'description': doc.description,
                    'visibility': doc.visibility,
                    'lifecycle_stage': doc.lifecycle_stage,
                    'created_by': doc.created_by,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None,
                })
            console.print(json.dumps(doc_data, indent=2))
        else:
            # Rich table output for human consumption
            if not documents:
                console.print()
                console.print(Panel.fit(
                    "[yellow]No unpublished documents found[/yellow]\n\n"
                    "[dim]Documents must be APPROVED and have PUBLIC visibility to appear here.[/dim]",
                    title="📄 Unpublished Documents",
                    subtitle="Empty Results"
                ))
                console.print()
                console.print("💡 [cyan]Document lifecycle:[/cyan]")
                console.print("   1. Create document (DRAFT)")
                console.print("   2. Submit for review: [dim]apm document submit-review <id>[/dim]")
                console.print("   3. Approve: [dim]apm document approve <id>[/dim]")
                console.print("   4. Publish: [dim]apm document publish <id>[/dim]")
                console.print()
                return

            # Create table
            table = Table(title="📄 Unpublished Documents (Ready to Publish)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("Entity", style="blue", width=12)
            table.add_column("Title", style="green", width=30)
            table.add_column("Category", style="magenta", width=15)
            table.add_column("Type", style="yellow", width=15)
            table.add_column("Created By", style="dim", width=12)
            table.add_column("Created", style="dim", width=12)

            for doc in documents:
                # Format entity info
                entity_info = f"{doc.entity_type.value} #{doc.entity_id}"

                # Format title (truncate if too long)
                title = doc.title or "Untitled"
                if len(title) > 30:
                    title = title[:27] + "..."

                # Format category and type
                category = doc.category or "Unknown"
                doc_type = doc.document_type.value if doc.document_type else "Unknown"

                # Format created date
                created_str = doc.created_at.strftime('%Y-%m-%d') if doc.created_at else "Unknown"

                table.add_row(
                    str(doc.id),
                    entity_info,
                    title,
                    category,
                    doc_type,
                    doc.created_by or "Unknown",
                    created_str
                )

            console.print()
            console.print(table)
            console.print()

            # Show summary
            console.print(f"[dim]Showing {len(documents)} unpublished document(s)[/dim]")
            if len(documents) == limit:
                console.print(f"[dim]Results limited to {limit} documents. Use --limit to show more.[/dim]")
            console.print()

            # Show helpful commands
            console.print("💡 [cyan]Next steps:[/cyan]")
            console.print("   • Publish document: [dim]apm document publish <id>[/dim]")
            console.print("   • View details: [dim]apm document show <id>[/dim]")
            console.print("   • Publish all: [dim]for id in <list>; do apm document publish $id; done[/dim]")
            console.print()

    except Exception as e:
        console.print()
        console.print(f"❌ [red]Error listing unpublished documents: {e}[/red]")
        console.print()
        raise click.Abort()
