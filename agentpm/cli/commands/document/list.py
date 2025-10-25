"""
apm document list - List document references for entity
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_work_item_exists, validate_task_exists
from agentpm.core.database.adapters import DocumentReferenceAdapter
from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat


@click.command(name='list')
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices()),
              help='Filter by entity type')
@click.option('--entity-id', 'entity_id',
              type=int,
              help='Filter by entity ID')
@click.option('--type', 'doc_type',
              type=click.Choice(DocumentType.choices()),
              help='Filter by document type')
@click.option('--format', 'doc_format',
              type=click.Choice(DocumentFormat.choices()),
              help='Filter by document format')
@click.option('--created-by', 'created_by',
              type=str,
              help='Filter by creator')
@click.option('--limit', 'limit',
              type=int,
              default=50,
              help='Maximum number of documents to show (default: 50)')
@click.option('--search',
              help='Search in document titles and descriptions (case-insensitive)')
@click.option('--output-format', 'output_format',
              type=click.Choice(['table', 'json']),
              default='table',
              help='Output format (default: table)')
@click.pass_context
def list_documents(ctx: click.Context, entity_type: str, entity_id: int, doc_type: str,
                   doc_format: str, created_by: str, limit: int, search: str, output_format: str):
    """
    List document references with optional filtering.
    
    Shows document references with their metadata and links to entities.
    Use filters to narrow down results by entity, type, format, or creator.
    
    \b
    Examples:
      # List all documents for a work item
      apm document list --entity-type=work-item --entity-id=5
      
      # List all design documents
      apm document list --type=design
      
      # List all markdown documents
      apm document list --format=markdown
      
      # List documents created by specific user
      apm document list --created-by=ai_agent
      
      # List with JSON output
      apm document list --entity-type=task --entity-id=12 --format=json
      
    # List with custom limit
    apm document list --limit=20
    
    # Search in documents
    apm document list --search "oauth"
    
    \b
    Filters:
      • --entity-type: Filter by entity type (work_item, task, idea, project)
      • --entity-id: Filter by specific entity ID
      • --type: Filter by document type (architecture, design, etc.)
      • --format: Filter by document format (markdown, html, pdf, etc.)
      • --created-by: Filter by creator identifier
      • --limit: Maximum number of results to show
    """
    console = ctx.obj['console']
    db = ctx.obj['db_service']
    
    try:
        # Validate entity exists if entity-type and entity-id are specified
        if entity_type and entity_id:
            if entity_type == 'work_item':
                validate_work_item_exists(db, entity_id, ctx)
            elif entity_type == 'task':
                validate_task_exists(db, entity_id, ctx)
            # TODO: Add validation for idea and project entities
        
        # Map string values to enums using safe conversion
        entity_type_enum = None
        if entity_type:
            entity_type_enum = EntityType.from_string(entity_type)
        
        # Get documents from database
        documents = DocumentReferenceAdapter.list(
            service=db,
            entity_type=entity_type_enum,
            entity_id=entity_id,
            document_type=doc_type,
            format=doc_format,
            created_by=created_by,
            limit=limit
        )
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            documents = [
                doc for doc in documents 
                if search_lower in doc.title.lower() or 
                   (doc.description and search_lower in doc.description.lower())
            ]
        
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
                    'document_type': doc.document_type.value if doc.document_type else None,
                    'title': doc.title,
                    'description': doc.description,
                    'file_size_bytes': doc.file_size_bytes,
                    'format': doc.format.value if doc.format else None,
                    'created_by': doc.created_by,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None,
                    'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
                })
            console.print(json.dumps(doc_data, indent=2))
        else:
            # Rich table output for human consumption
            if not documents:
                console.print()
                console.print(Panel.fit(
                    "[yellow]No documents found matching the specified criteria[/yellow]",
                    title="📄 Document List",
                    subtitle="Empty Results"
                ))
                console.print()
                return
            
            # Create table
            table = Table(title="📄 Document References")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("Entity", style="blue", width=12)
            table.add_column("File Path", style="green", width=30)
            table.add_column("Type", style="magenta", width=15)
            table.add_column("Format", style="yellow", width=8)
            table.add_column("Size", style="dim", width=8)
            table.add_column("Created By", style="dim", width=12)
            table.add_column("Created", style="dim", width=12)
            
            for doc in documents:
                # Format entity info
                entity_info = f"{doc.entity_type.value} #{doc.entity_id}"
                
                # Format file path (truncate if too long)
                file_path = doc.file_path
                if len(file_path) > 30:
                    file_path = "..." + file_path[-27:]
                
                # Format document type
                doc_type_str = doc.document_type.value if doc.document_type else "Unknown"
                
                # Format document format
                format_str = doc.format.value if doc.format else "Unknown"
                
                # Format file size
                size_str = _format_file_size(doc.file_size_bytes) if doc.file_size_bytes else "Unknown"
                
                # Format created date
                created_str = doc.created_at.strftime('%Y-%m-%d') if doc.created_at else "Unknown"
                
                table.add_row(
                    str(doc.id),
                    entity_info,
                    file_path,
                    doc_type_str,
                    format_str,
                    size_str,
                    doc.created_by or "Unknown",
                    created_str
                )
            
            console.print()
            console.print(table)
            console.print()
            
            # Show summary
            console.print(f"[dim]Showing {len(documents)} document(s)[/dim]")
            if len(documents) == limit:
                console.print(f"[dim]Results limited to {limit} documents. Use --limit to show more.[/dim]")
            console.print()
            
            # Show helpful commands
            console.print("💡 [cyan]Useful commands:[/cyan]")
            console.print("   • Show document details: [dim]apm document show <id>[/dim]")
            console.print("   • Add new document: [dim]apm document add --entity-type=<type> --entity-id=<id>[/dim]")
            console.print("   • Update document: [dim]apm document update <id>[/dim]")
            console.print("   • Delete document: [dim]apm document delete <id>[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error listing documents: {e}[/red]")
        raise click.Abort()


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
