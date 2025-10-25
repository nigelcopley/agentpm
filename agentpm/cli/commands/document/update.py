"""
apm document update - Update document reference metadata
"""

import click
from rich.console import Console
from rich.panel import Panel
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.security import validate_file_path, calculate_content_hash
from agentpm.core.database.adapters import DocumentReferenceAdapter
from agentpm.core.database.models import DocumentReference
from agentpm.core.database.enums import DocumentType, DocumentFormat


@click.command()
@click.argument('document_id', type=int)
@click.option('--file-path', 'file_path',
              type=str,
              help='Update file path')
@click.option('--type', 'doc_type',
              type=click.Choice(DocumentType.choices()),
              help='Update document type')
@click.option('--title',
              type=str,
              help='Update document title')
@click.option('--description',
              type=str,
              help='Update document description')
@click.option('--format', 'doc_format',
              type=click.Choice(DocumentFormat.choices()),
              help='Update document format')
@click.option('--validate-file',
              is_flag=True,
              default=True,
              help='Validate that updated file exists and is readable')
@click.pass_context
def update(ctx: click.Context, document_id: int, file_path: str, doc_type: str,
           title: str, description: str, doc_format: str, validate_file: bool):
    """
    Update document reference metadata.
    
    Updates one or more fields of an existing document reference.
    Only specified fields will be updated; other fields remain unchanged.
    
    \b
    Examples:
      # Update document title
      apm document update 25 --title="Updated API Specification"
      
      # Update document type and description
      apm document update 25 --type=specification --description="Latest version of API spec"
      
      # Update file path
      apm document update 25 --file-path="docs/api/v2/specification.md"
      
      # Update multiple fields
      apm document update 25 --title="New Title" --type=design --description="Updated design"
    
    \b
    Updateable Fields:
      • --file-path: Relative path to document file
      • --type: Document type (architecture, design, specification, etc.)
      • --title: Document title
      • --description: Document description
      • --format: Document format (markdown, html, pdf, etc.)
    
    \b
    Notes:
      • Only specified fields will be updated
      • File validation is performed by default (use --no-validate-file to skip)
      • File size and content hash are recalculated if file path changes
    """
    console = ctx.obj['console']
    project_root = ctx.obj['project_root']
    db = ctx.obj['db_service']
    
    try:
        # Get existing document
        existing_doc = DocumentReferenceAdapter.get(db, document_id)
        
        if not existing_doc:
            console.print(f"❌ [red]Document not found: ID {document_id}[/red]")
            console.print()
            console.print("💡 [yellow]Available documents:[/yellow]")
            console.print("   apm document list")
            raise click.Abort()
        
        # SEC-001: Validate file path security if provided (prevent directory traversal)
        if file_path:
            is_valid, error_msg = validate_file_path(file_path, project_root)
            if not is_valid:
                console.print(f"❌ [red]Security error: {error_msg}[/red]")
                console.print()
                console.print("💡 [yellow]File path security requirements:[/yellow]")
                console.print("   • Path must be relative to project root")
                console.print("   • Path cannot contain '..' (directory traversal)")
                console.print("   • Path must resolve within project boundaries")
                raise click.Abort()

        # Validate file path if provided and validation is enabled
        if file_path and validate_file:
            abs_path = project_root / file_path
            if not abs_path.exists():
                console.print(f"❌ [red]File not found: {file_path}[/red]")
                console.print(f"   Expected at: {abs_path}")
                raise click.Abort()

            if not abs_path.is_file():
                console.print(f"❌ [red]Path is not a file: {file_path}[/red]")
                raise click.Abort()
        
        # Create updated document with only changed fields
        updated_doc = DocumentReference(
            id=existing_doc.id,
            entity_type=existing_doc.entity_type,
            entity_id=existing_doc.entity_id,
            file_path=file_path if file_path is not None else existing_doc.file_path,
            document_type=DocumentType(doc_type) if doc_type else existing_doc.document_type,
            title=title if title is not None else existing_doc.title,
            description=description if description is not None else existing_doc.description,
            file_size_bytes=existing_doc.file_size_bytes,  # Will be recalculated if needed
            content_hash=existing_doc.content_hash,  # Will be recalculated if needed
            format=DocumentFormat(doc_format) if doc_format else existing_doc.format,
            created_by=existing_doc.created_by,
            created_at=existing_doc.created_at,
            updated_at=existing_doc.updated_at
        )
        
        # Recalculate file metadata if file path changed
        if file_path and file_path != existing_doc.file_path:
            abs_path = project_root / file_path
            if abs_path.exists():
                updated_doc.file_size_bytes = abs_path.stat().st_size
                # SEC-003: Calculate content hash for integrity verification
                updated_doc.content_hash = calculate_content_hash(abs_path)
        
        # Update in database
        updated_doc = DocumentReferenceAdapter.update(db, updated_doc)
        
        # Display success message
        console.print()
        console.print(Panel.fit(
            f"[green]✅ Document reference updated successfully[/green]",
            title="📄 Document Updated",
            subtitle=f"ID: {updated_doc.id}"
        ))
        console.print()
        
        # Show what was updated
        changes = []
        if file_path and file_path != existing_doc.file_path:
            changes.append(f"File path: {existing_doc.file_path} → {updated_doc.file_path}")
        if doc_type and DocumentType(doc_type) != existing_doc.document_type:
            changes.append(f"Type: {existing_doc.document_type.value if existing_doc.document_type else 'None'} → {updated_doc.document_type.value}")
        if title and title != existing_doc.title:
            changes.append(f"Title: {existing_doc.title or 'None'} → {updated_doc.title}")
        if description and description != existing_doc.description:
            changes.append(f"Description: {existing_doc.description or 'None'} → {updated_doc.description}")
        if doc_format and DocumentFormat(doc_format) != existing_doc.format:
            changes.append(f"Format: {existing_doc.format.value if existing_doc.format else 'None'} → {updated_doc.format.value}")
        
        if changes:
            console.print("[bold cyan]Changes made:[/bold cyan]")
            for change in changes:
                console.print(f"  • {change}")
            console.print()
        else:
            console.print("[yellow]No changes were made (all values were the same)[/yellow]")
            console.print()
        
        # Show updated document details
        console.print("[bold cyan]Updated Document Details:[/bold cyan]")
        console.print(f"  [dim]ID:[/dim] {updated_doc.id}")
        console.print(f"  [dim]Entity:[/dim] {updated_doc.entity_type.value} #{updated_doc.entity_id}")
        console.print(f"  [dim]File Path:[/dim] {updated_doc.file_path}")
        console.print(f"  [dim]Type:[/dim] {updated_doc.document_type.value if updated_doc.document_type else 'Not specified'}")
        console.print(f"  [dim]Format:[/dim] {updated_doc.format.value if updated_doc.format else 'Not specified'}")
        console.print(f"  [dim]Title:[/dim] {updated_doc.title or 'Not specified'}")
        if updated_doc.description:
            console.print(f"  [dim]Description:[/dim] {updated_doc.description}")
        if updated_doc.file_size_bytes:
            console.print(f"  [dim]Size:[/dim] {_format_file_size(updated_doc.file_size_bytes)}")
        console.print(f"  [dim]Updated At:[/dim] {updated_doc.updated_at.strftime('%Y-%m-%d %H:%M:%S') if updated_doc.updated_at else 'Unknown'}")
        console.print()
        
        console.print("💡 [cyan]Next steps:[/cyan]")
        console.print(f"   • View document: [dim]apm document show {updated_doc.id}[/dim]")
        console.print(f"   • List entity documents: [dim]apm document list --entity-type={updated_doc.entity_type.value} --entity-id={updated_doc.entity_id}[/dim]")
        console.print(f"   • Delete document: [dim]apm document delete {updated_doc.id}[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error updating document reference: {e}[/red]")
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
