"""
apm document delete - Delete document reference
"""

import click
from rich.console import Console
from rich.panel import Panel
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import DocumentReferenceAdapter


@click.command()
@click.argument('document_id', type=int)
@click.option('--force', 'force',
              is_flag=True,
              help='Delete without confirmation prompt')
@click.option('--delete-file', 'delete_file',
              is_flag=True,
              help='Also delete the actual file from filesystem')
@click.pass_context
def delete(ctx: click.Context, document_id: int, force: bool, delete_file: bool):
    """
    Delete a document reference from the database.
    
    Removes the document reference from the database. By default, this only
    removes the database record; the actual file is not deleted unless
    --delete-file is specified.
    
    \b
    Examples:
      # Delete document reference (keep file)
      apm document delete 25
      
      # Delete document reference and file
      apm document delete 25 --delete-file
      
      # Delete without confirmation
      apm document delete 25 --force
    
    \b
    Options:
      • --force: Delete without confirmation prompt
      • --delete-file: Also delete the actual file from filesystem
    
    \b
    Warning:
      • This action cannot be undone
      • Use --delete-file with caution as it permanently removes files
      • Consider backing up important documents before deletion
    """
    console = ctx.obj['console']
    project_root = ctx.obj['project_root']
    db = ctx.obj['db_service']
    
    try:
        # Get document to show details before deletion
        document = DocumentReferenceAdapter.get(db, document_id)
        
        if not document:
            console.print(f"❌ [red]Document not found: ID {document_id}[/red]")
            console.print()
            console.print("💡 [yellow]Available documents:[/yellow]")
            console.print("   apm document list")
            raise click.Abort()
        
        # Show document details
        console.print()
        console.print(Panel.fit(
            f"[bold red]Delete Document Reference[/bold red]",
            title="⚠️  Confirmation Required",
            subtitle=f"ID: {document.id}"
        ))
        console.print()
        
        console.print("[bold cyan]Document Details:[/bold cyan]")
        console.print(f"  [dim]ID:[/dim] {document.id}")
        console.print(f"  [dim]Entity:[/dim] {document.entity_type.value} #{document.entity_id}")
        console.print(f"  [dim]File Path:[/dim] {document.file_path}")
        console.print(f"  [dim]Type:[/dim] {document.document_type.value if document.document_type else 'Not specified'}")
        console.print(f"  [dim]Title:[/dim] {document.title or 'Not specified'}")
        console.print(f"  [dim]Created By:[/dim] {document.created_by or 'Unknown'}")
        console.print(f"  [dim]Created At:[/dim] {document.created_at.strftime('%Y-%m-%d %H:%M:%S') if document.created_at else 'Unknown'}")
        console.print()
        
        # Check if file exists
        abs_path = project_root / document.file_path
        if abs_path.exists():
            console.print("✅ [green]File exists on filesystem[/green]")
            console.print(f"   [dim]Location: {abs_path}[/dim]")
        else:
            console.print("⚠️  [yellow]File not found on filesystem[/yellow]")
            console.print(f"   [dim]Expected at: {abs_path}[/dim]")
        console.print()
        
        # Show what will be deleted
        console.print("[bold red]This will delete:[/bold red]")
        console.print("  • Document reference from database")
        if delete_file and abs_path.exists():
            console.print("  • File from filesystem")
        elif delete_file and not abs_path.exists():
            console.print("  • File from filesystem (file not found)")
        else:
            console.print("  • File will be kept on filesystem")
        console.print()
        
        # Confirmation prompt
        if not force:
            console.print("[bold yellow]This action cannot be undone![/bold yellow]")
            if not click.confirm("Are you sure you want to delete this document reference?"):
                console.print("❌ [yellow]Deletion cancelled[/yellow]")
                return
        
        # Delete document reference
        DocumentReferenceAdapter.delete(db, document_id)
        
        # Delete file if requested
        file_deleted = False
        if delete_file and abs_path.exists():
            try:
                abs_path.unlink()
                file_deleted = True
            except Exception as e:
                console.print(f"⚠️  [yellow]Could not delete file: {e}[/yellow]")
        
        # Display success message
        console.print()
        console.print(Panel.fit(
            f"[green]✅ Document reference deleted successfully[/green]",
            title="📄 Document Deleted",
            subtitle=f"ID: {document_id}"
        ))
        console.print()
        
        # Show what was deleted
        console.print("[bold cyan]Deleted:[/bold cyan]")
        console.print("  • Document reference from database")
        if delete_file:
            if file_deleted:
                console.print("  • File from filesystem")
            else:
                console.print("  • File deletion attempted (may have failed)")
        else:
            console.print("  • File kept on filesystem")
        console.print()
        
        console.print("💡 [cyan]Next steps:[/cyan]")
        console.print(f"   • List entity documents: [dim]apm document list --entity-type={document.entity_type.value} --entity-id={document.entity_id}[/dim]")
        console.print("   • List all documents: [dim]apm document list[/dim]")
        console.print(f"   • Show entity: [dim]apm {document.entity_type.value.replace('_', '-')} show {document.entity_id}[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error deleting document reference: {e}[/red]")
        raise click.Abort()
