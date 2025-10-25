"""
apm document show - Show document reference details
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import DocumentReferenceAdapter


@click.command()
@click.argument('document_id', type=int)
@click.option('--include-content', 'include_content',
              is_flag=True,
              help='Include document content preview (first 500 characters)')
@click.option('--format', 'output_format',
              type=click.Choice(['rich', 'json']),
              default='rich',
              help='Output format (default: rich)')
@click.pass_context
def show(ctx: click.Context, document_id: int, include_content: bool, output_format: str):
    """
    Show detailed information about a document reference.
    
    Displays comprehensive metadata about a document including file details,
    entity linkage, and optionally document content preview.
    
    \b
    Examples:
      # Show document details
      apm document show 25
      
      # Show with content preview
      apm document show 25 --include-content
      
      # Show in JSON format
      apm document show 25 --format=json
    
    \b
    Information Shown:
      • Document metadata (ID, title, description)
      • File details (path, size, format, hash)
      • Entity linkage (type and ID)
      • Creation info (creator, timestamps)
      • Content preview (if --include-content is used)
    """
    console = ctx.obj['console']
    project_root = ctx.obj['project_root']
    db = ctx.obj['db_service']
    
    try:
        # Get document from database
        document = DocumentReferenceAdapter.get(db, document_id)
        
        if not document:
            console.print(f"❌ [red]Document not found: ID {document_id}[/red]")
            console.print()
            console.print("💡 [yellow]Available documents:[/yellow]")
            console.print("   apm document list")
            raise click.Abort()
        
        if output_format == 'json':
            # JSON output for programmatic use
            import json
            doc_data = {
                'id': document.id,
                'entity_type': document.entity_type.value,
                'entity_id': document.entity_id,
                'file_path': document.file_path,
                'document_type': document.document_type.value if document.document_type else None,
                'title': document.title,
                'description': document.description,
                'file_size_bytes': document.file_size_bytes,
                'content_hash': document.content_hash,
                'format': document.format.value if document.format else None,
                'created_by': document.created_by,
                'created_at': document.created_at.isoformat() if document.created_at else None,
                'updated_at': document.updated_at.isoformat() if document.updated_at else None
            }
            
            if include_content:
                doc_data['content_preview'] = _get_content_preview(project_root, document)
            
            console.print(json.dumps(doc_data, indent=2))
        else:
            # Rich output for human consumption
            console.print()
            console.print(Panel.fit(
                f"[bold cyan]{document.title or 'Untitled Document'}[/bold cyan]",
                title="📄 Document Details",
                subtitle=f"ID: {document.id}"
            ))
            console.print()
            
            # Basic information table
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Field", style="cyan", width=20)
            info_table.add_column("Value", style="white", width=50)
            
            info_table.add_row("ID", str(document.id))
            info_table.add_row("Entity", f"{document.entity_type.value} #{document.entity_id}")
            info_table.add_row("File Path", document.file_path)
            info_table.add_row("Document Type", document.document_type.value if document.document_type else "Not specified")
            info_table.add_row("Format", document.format.value if document.format else "Not specified")
            info_table.add_row("Title", document.title or "Not specified")
            info_table.add_row("Description", document.description or "Not specified")
            info_table.add_row("File Size", _format_file_size(document.file_size_bytes) if document.file_size_bytes else "Unknown")
            info_table.add_row("Content Hash", document.content_hash or "Not calculated")
            info_table.add_row("Created By", document.created_by or "Unknown")
            info_table.add_row("Created At", document.created_at.strftime('%Y-%m-%d %H:%M:%S') if document.created_at else "Unknown")
            info_table.add_row("Updated At", document.updated_at.strftime('%Y-%m-%d %H:%M:%S') if document.updated_at else "Unknown")
            
            console.print(info_table)
            console.print()
            
            # File existence check
            abs_path = project_root / document.file_path
            if abs_path.exists():
                console.print("✅ [green]File exists and is accessible[/green]")
                console.print(f"   [dim]Absolute path: {abs_path}[/dim]")
            else:
                console.print("⚠️  [yellow]File not found or not accessible[/yellow]")
                console.print(f"   [dim]Expected at: {abs_path}[/dim]")
            console.print()
            
            # Content preview if requested
            if include_content:
                content_preview = _get_content_preview(project_root, document)
                if content_preview:
                    console.print("[bold cyan]Content Preview:[/bold cyan]")
                    console.print(Panel(
                        content_preview,
                        title="Document Content",
                        subtitle="First 500 characters"
                    ))
                    console.print()
                else:
                    console.print("⚠️  [yellow]Could not read document content[/yellow]")
                    console.print()
            
            # Related commands
            console.print("💡 [cyan]Related commands:[/cyan]")
            console.print(f"   • List entity documents: [dim]apm document list --entity-type={document.entity_type.value} --entity-id={document.entity_id}[/dim]")
            console.print(f"   • Update document: [dim]apm document update {document.id}[/dim]")
            console.print(f"   • Delete document: [dim]apm document delete {document.id}[/dim]")
            console.print(f"   • Show entity: [dim]apm {document.entity_type.value.replace('_', '-')} show {document.entity_id}[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error showing document: {e}[/red]")
        raise click.Abort()


def _get_content_preview(project_root, document, max_chars: int = 500) -> str:
    """Get content preview from document file."""
    try:
        abs_path = project_root / document.file_path
        if not abs_path.exists():
            return None
        
        # Read file content
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
        
        # Truncate if needed
        if len(content) == max_chars:
            content += "..."
        
        return content.strip()
    
    except Exception:
        return None


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
