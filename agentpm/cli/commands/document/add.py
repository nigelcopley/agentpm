"""
apm document add - Add document reference to entity
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import validate_work_item_exists, validate_task_exists
from agentpm.cli.utils.security import validate_file_path, calculate_content_hash
from agentpm.core.database.adapters import DocumentReferenceAdapter
from agentpm.core.database.models import DocumentReference
from agentpm.core.database.enums import EntityType, DocumentType, DocumentFormat, DocumentCategory


# Category mapping for document types
CATEGORY_MAPPING = {
    # Planning documents
    'requirements': 'planning',
    'user_story': 'planning',
    'use_case': 'planning',
    'refactoring_guide': 'planning',
    'implementation_plan': 'planning',

    # Architecture documents
    'architecture': 'architecture',
    'design': 'architecture',
    'adr': 'architecture',
    'technical_specification': 'architecture',

    # Guide documents
    'user_guide': 'guides',
    'admin_guide': 'guides',
    'troubleshooting': 'guides',
    'migration_guide': 'guides',

    # Reference documents
    'specification': 'reference',
    'api_doc': 'reference',

    # Process documents
    'test_plan': 'processes',

    # Governance documents
    'quality_gates_spec': 'governance',

    # Operations documents
    'runbook': 'operations',

    # Communication documents
    'business_pillars_analysis': 'communication',
    'market_research_report': 'communication',
    'competitive_analysis': 'communication',
    'stakeholder_analysis': 'communication',
}


def _validate_and_guide_path(file_path: str, document_type: str, console: Console, strict: bool = False) -> str:
    """
    Validate path and provide guidance if non-compliant with standard structure.

    Args:
        file_path: User-provided file path
        document_type: Document type (used to infer category)
        console: Rich console for output
        strict: If True, reject non-compliant paths immediately (for automated/testing)

    Returns:
        str: Validated or corrected file path

    Raises:
        click.Abort: If path is invalid
    """
    # Check for absolute paths
    if Path(file_path).is_absolute():
        console.print()
        console.print("[red]❌ Absolute paths are not allowed[/red]")
        console.print()
        console.print(f"  Path provided: [yellow]{file_path}[/yellow]")
        console.print()
        console.print("💡 [cyan]Use relative paths from project root:[/cyan]")
        console.print("   [dim]docs/{category}/{document_type}/{filename}[/dim]")
        console.print()
        raise click.Abort()

    # Check if path starts with 'docs/'
    if not file_path.startswith('docs/'):
        console.print()
        console.print("[yellow]⚠️  Path does not follow standard structure[/yellow]")
        console.print()

        # Infer category from document_type
        category = CATEGORY_MAPPING.get(document_type, 'communication')

        # Generate suggested path
        filename = Path(file_path).name
        suggested = f"docs/{category}/{document_type}/{filename}"

        # Display guidance
        console.print("💡 [cyan]Recommended path structure:[/cyan]")
        console.print(f"   [bold]{suggested}[/bold]")
        console.print()
        console.print("📁 [cyan]Standard structure:[/cyan]")
        console.print("   [dim]docs/{category}/{document_type}/{filename}[/dim]")
        console.print()
        console.print("📂 [cyan]Valid categories:[/cyan]")
        console.print("   • architecture  - System design, technical architecture")
        console.print("   • planning      - Requirements, user stories, plans")
        console.print("   • guides        - User guides, tutorials, how-tos")
        console.print("   • reference     - API docs, specifications, references")
        console.print("   • processes     - Test plans, workflows, procedures")
        console.print("   • governance    - Quality gates, standards, policies")
        console.print("   • operations    - Runbooks, deployment, monitoring")
        console.print("   • communication - Reports, analyses, stakeholder docs")
        console.print()

        # In strict mode, reject immediately
        if strict:
            console.print("[red]❌ Path must start with 'docs/'[/red]")
            raise click.Abort()

        # Offer to use suggested path
        if click.confirm("Use recommended path?", default=True):
            console.print(f"✅ Using path: [green]{suggested}[/green]")
            console.print()
            return suggested
        elif not click.confirm("Continue with non-standard path?", default=False):
            console.print("[red]Aborted - path validation failed[/red]")
            raise click.Abort()
        else:
            console.print(f"⚠️  Proceeding with: [yellow]{file_path}[/yellow]")
            console.print()

    # Check if path has minimum required depth (docs/{category}/{type}/{file})
    parts = file_path.split('/')
    if len(parts) < 4:
        console.print()
        console.print("[red]❌ Path structure is incomplete[/red]")
        console.print()
        console.print(f"  Path provided: [yellow]{file_path}[/yellow]")
        console.print()
        console.print("💡 [cyan]Required structure:[/cyan]")
        console.print("   [dim]docs/{category}/{document_type}/{filename}[/dim]")
        console.print()
        console.print(f"  Example: [dim]docs/planning/requirements/feature-spec.md[/dim]")
        console.print()
        raise click.Abort()

    return file_path


def _normalize_entity_type(ctx, param, value):
    """Normalize entity type by replacing hyphens with underscores."""
    if value:
        value = value.replace('-', '_')
    return value


@click.command()
@click.option('--entity-type', 'entity_type',
              type=click.Choice(EntityType.choices() + ['work-item']),  # Accept both formats
              callback=_normalize_entity_type,
              required=True,
              help='Type of entity to link document to')
@click.option('--entity-id', 'entity_id',
              type=int,
              required=True,
              help='ID of the entity')
@click.option('--file-path', 'file_path',
              type=str,
              required=True,
              help='Relative path to document file from project root')
@click.option('--category', 'category',
              type=click.Choice(DocumentCategory.choices()),
              help='Document category (auto-detected from file path if not specified)')
@click.option('--type', 'doc_type',
              type=click.Choice(DocumentType.choices()),
              help='Document type (auto-detected from file path if not specified)')
@click.option('--title',
              type=str,
              help='Document title (auto-generated from file name if not specified)')
@click.option('--description',
              type=str,
              help='Document description')
@click.option('--format', 'doc_format',
              type=click.Choice(DocumentFormat.choices()),
              help='Document format (auto-detected from file extension if not specified)')
@click.option('--created-by', 'created_by',
              type=str,
              default=None,
              help='Creator identifier (default: current user from environment)')
@click.option('--content', 'content',
              type=str,
              help='Document content (creates database-first document)')
@click.option('--validate-file',
              is_flag=True,
              default=True,
              help='Validate that file exists and is readable')
@click.option('--no-validate-file',
              is_flag=True,
              default=False,
              help='Skip file validation (opposite of --validate-file)')
@click.option('--no-validate-entity',
              is_flag=True,
              default=False,
              help='Skip entity existence validation (for testing)')
@click.option('--strict-validation',
              is_flag=True,
              default=False,
              help='Enforce strict path validation (reject non-compliant paths immediately)')
@click.pass_context
def add(ctx: click.Context, entity_type: str, entity_id: int, file_path: str,
        category: str, doc_type: str, title: str, description: str, doc_format: str,
        created_by: str, content: str, validate_file: bool, no_validate_file: bool, no_validate_entity: bool,
        strict_validation: bool):
    """
    Add a document reference to an entity (work item, task, idea, or project).
    
    Links a document file to an entity and tracks document metadata.
    Supports both file-first and database-first workflows.
    
    \b
    Examples:
      # File-first workflow (existing file)
      apm document add --entity-type=work-item --entity-id=5 \\
          --file-path="docs/api-specification.md" \\
          --type=specification --title="API Specification"
      
      # Database-first workflow (create from content)
      apm document add --entity-type=work-item --entity-id=5 \\
          --file-path="docs/architecture/design/user-auth.md" \\
          --category=architecture --type=design_doc \\
          --title="User Authentication Design" \\
          --content="# User Authentication Design\\n\\n## Overview\\n..."
      
      # Add with auto-detection
      apm document add --entity-type=work-item --entity-id=5 \\
          --file-path="docs/architecture/system-overview.md"
    
    \b
    See Also:
      apm document types          # Show all available categories and types
      apm document types --help   # Show types command options
    
    \b
    Auto-Detection:
      • Document type: Inferred from file path patterns
      • Document format: Inferred from file extension
      • Title: Generated from file name (cleaned up)
      • File validation: Checks file exists and is readable (file-first only)
    
    \b
    File Path Rules:
      • Must be relative to project root
      • Cannot contain '..' (directory traversal)
      • Must point to existing file (file-first workflow only)
      • Follow structure: docs/{category}/{document_type}/{filename}
    """
    console = ctx.obj['console']
    project_root = ctx.obj['project_root']
    db = ctx.obj['db_service']
    
    # Auto-detect created_by if not provided
    from agentpm.cli.utils.user import get_created_by_value
    created_by = get_created_by_value(created_by)
    
    try:
        # Validate entity exists (unless validation is skipped)
        if not no_validate_entity:
            if entity_type == 'work_item':
                validate_work_item_exists(db, entity_id, ctx)
            elif entity_type == 'task':
                validate_task_exists(db, entity_id, ctx)
            # TODO: Add validation for idea and project entities
        
        # Auto-detect document type if not specified (needed for path validation)
        if not doc_type:
            doc_type = _detect_document_type(file_path)

        # Auto-detect category from path if not specified
        if not category:
            category = _detect_category_from_path(file_path)

        # STEP 1: Validate path structure (BEFORE file validation)
        file_path = _validate_and_guide_path(file_path, doc_type, console, strict=strict_validation)

        # STEP 2: SEC-001: Validate file path security (prevent directory traversal)
        is_valid, error_msg = validate_file_path(file_path, project_root)
        if not is_valid:
            console.print(f"❌ [red]Security error: {error_msg}[/red]")
            console.print()
            console.print("💡 [yellow]File path security requirements:[/yellow]")
            console.print("   • Path must be relative to project root")
            console.print("   • Path cannot contain '..' (directory traversal)")
            console.print("   • Path must resolve within project boundaries")
            raise click.Abort()

        # STEP 3: Validate file exists (if validation enabled and no content provided)
        if validate_file and not no_validate_file and not content:
            abs_path = project_root / file_path
            if not abs_path.exists():
                console.print(f"❌ [red]File not found: {file_path}[/red]")
                console.print(f"   Expected at: {abs_path}")
                console.print()
                console.print("💡 [cyan]To fix:[/cyan]")
                console.print("   • Create the file first")
                console.print("   • Use [dim]--no-validate-file[/dim] to skip validation")
                console.print("   • Use [dim]--content[/dim] to create database-first document")
                console.print("   • Check the file path is correct")
                console.print()
                raise click.Abort()

            if not abs_path.is_file():
                console.print(f"❌ [red]Path is not a file: {file_path}[/red]")
                raise click.Abort()

        # Validate category/type consistency if both are provided
        if category and doc_type:
            _validate_category_type_consistency(category, doc_type, file_path, console)

        # Auto-detect document format if not specified
        if not doc_format:
            doc_format = _detect_document_format(file_path)

        # Auto-generate title if not specified
        if not title:
            title = _generate_title_from_path(file_path)

        # Map string values to enums using safe conversion
        entity_type_enum = EntityType.from_string(entity_type)

        doc_type_enum = DocumentType(doc_type) if doc_type else None
        doc_format_enum = DocumentFormat(doc_format) if doc_format else None
        category_enum = DocumentCategory(category) if category else None
        
        # Handle database-first vs file-first workflow
        if content:
            # Database-first workflow: content provided, file will be generated
            console.print("[cyan]📝 Creating database-first document...[/cyan]")
            
            # Skip file validation for database-first workflow
            validate_file = False
            
            # Calculate content metadata
            content_hash = calculate_content_hash_from_string(content)
            file_size_bytes = len(content.encode('utf-8'))
            
            # Create document reference with content
            document = DocumentReference(
                entity_type=entity_type_enum,
                entity_id=entity_id,
                file_path=file_path,
                category=category,
                document_type=doc_type_enum,
                title=title,
                description=description,
                file_size_bytes=file_size_bytes,
                content_hash=content_hash,
                format=doc_format_enum,
                created_by=created_by,
                content=content,
                storage_mode="hybrid"  # Database-first with file sync
            )
            
            # Use content-aware creation method
            from agentpm.core.database.methods import document_references as doc_methods
            created_doc = doc_methods.create_document_with_content(db, document, content)
            
            # Generate physical file
            _generate_file_from_database(project_root, created_doc, console)
            
            # Update sync status to SYNCED after file generation
            from agentpm.core.database.methods import document_references as doc_methods
            doc_methods.mark_document_synced(db, created_doc.id)
            
        else:
            # File-first workflow: validate existing file
            file_size_bytes = None
            content_hash = None
            if validate_file and not no_validate_file:
                abs_path = project_root / file_path
                file_size_bytes = abs_path.stat().st_size
                # SEC-003: Calculate content hash for integrity verification
                content_hash = calculate_content_hash(abs_path)
            
            # Create document reference
            document = DocumentReference(
                entity_type=entity_type_enum,
                entity_id=entity_id,
                file_path=file_path,
                category=category,
                document_type=doc_type_enum,
                title=title,
                description=description,
                file_size_bytes=file_size_bytes,
                content_hash=content_hash,
                format=doc_format_enum,
                created_by=created_by
            )
            
            # THREE-LAYER PATTERN: Use adapter, not direct methods call
            created_doc = DocumentReferenceAdapter.create(db, document)
        
        # Display success message
        console.print()
        console.print(Panel.fit(
            f"[green]✅ Document reference added successfully[/green]",
            title="📄 Document Added",
            subtitle=f"ID: {created_doc.id}"
        ))
        console.print()
        
        # Show document details
        console.print("[bold cyan]Document Details:[/bold cyan]")
        console.print(f"  [dim]ID:[/dim] {created_doc.id}")
        console.print(f"  [dim]Entity:[/dim] {entity_type} #{entity_id}")
        console.print(f"  [dim]File Path:[/dim] {created_doc.file_path}")
        console.print(f"  [dim]Type:[/dim] {created_doc.document_type.value if created_doc.document_type else 'Auto-detected'}")
        console.print(f"  [dim]Format:[/dim] {created_doc.format.value if created_doc.format else 'Auto-detected'}")
        console.print(f"  [dim]Title:[/dim] {created_doc.title}")
        if created_doc.description:
            console.print(f"  [dim]Description:[/dim] {created_doc.description}")
        if created_doc.file_size_bytes:
            console.print(f"  [dim]Size:[/dim] {_format_file_size(created_doc.file_size_bytes)}")
        console.print(f"  [dim]Created By:[/dim] {created_doc.created_by}")
        console.print(f"  [dim]Created At:[/dim] {created_doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        console.print()
        
        console.print("💡 [cyan]Next steps:[/cyan]")
        console.print(f"   • View document: [dim]apm document show {created_doc.id}[/dim]")
        console.print(f"   • List entity documents: [dim]apm document list --entity-type={entity_type} --entity-id={entity_id}[/dim]")
        console.print(f"   • Update document: [dim]apm document update {created_doc.id}[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Error adding document reference: {e}[/red]")
        raise click.Abort()


def _detect_document_type(file_path: str) -> str:
    """Detect document type from file path patterns."""
    path_lower = file_path.lower()
    
    # ADRs - check first to avoid conflicts with architecture
    if any(pattern in path_lower for pattern in ['adr/', 'decision/', 'decisions/']):
        return 'adr'
    
    # Architecture documents
    if any(pattern in path_lower for pattern in ['architecture', 'arch/', 'system-design']):
        return 'architecture'
    
    # Design documents
    if any(pattern in path_lower for pattern in ['design/', 'designs/', 'mockup', 'wireframe']):
        return 'design'
    
    # API documentation
    if any(pattern in path_lower for pattern in ['api/', 'api-docs', 'swagger', 'openapi']):
        return 'api_doc'
    
    # User guides
    if any(pattern in path_lower for pattern in ['user-guide', 'user_guide', 'manual', 'tutorial']):
        return 'user_guide'
    
    # Test plans
    if any(pattern in path_lower for pattern in ['test-plan', 'test_plan', 'testing/', 'qa/']):
        return 'test_plan'
    
    # Troubleshooting
    if any(pattern in path_lower for pattern in ['troubleshooting', 'troubleshoot', 'debug', 'support']):
        return 'troubleshooting'
    
    # Requirements
    if any(pattern in path_lower for pattern in ['requirements', 'reqs/']):
        return 'requirements'
    
    # User stories
    if any(pattern in path_lower for pattern in ['user-story', 'user_story', 'stories/']):
        return 'user_story'
    
    # Specifications - check after requirements to avoid conflicts
    if any(pattern in path_lower for pattern in ['specs/', 'specification']):
        return 'specification'
    
    # Deployment guides - return 'other' since not in DocumentType enum
    if any(pattern in path_lower for pattern in ['deployment', 'deploy/', 'ops/', 'operations']):
        return 'other'
    
    # Changelog - return 'other' since not in DocumentType enum
    if any(pattern in path_lower for pattern in ['changelog', 'release-notes', 'version-history']):
        return 'other'
    
    # Default to specification
    return 'specification'


def _detect_document_format(file_path: str) -> str:
    """Detect document format from file extension."""
    ext = Path(file_path).suffix.lower()
    
    format_map = {
        '.md': 'markdown',
        '.html': 'html',
        '.htm': 'html',
        '.pdf': 'pdf',
        '.txt': 'text',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml'
    }
    
    return format_map.get(ext, 'other')


def _generate_title_from_path(file_path: str) -> str:
    """Generate a human-readable title from file path."""
    # Get filename without extension
    filename = Path(file_path).stem
    
    # Replace common separators with spaces
    title = filename.replace('-', ' ').replace('_', ' ')
    
    # Capitalize words
    title = ' '.join(word.capitalize() for word in title.split())
    
    return title


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


def _detect_category_from_path(file_path: str) -> str:
    """
    Auto-detect category from file path structure.

    Expected structure: docs/{category}/{document_type}/{filename}

    Args:
        file_path: File path to analyze

    Returns:
        str: Detected category or None
    """
    if not file_path.startswith('docs/'):
        return None

    # Split path and extract category (second component)
    parts = file_path.split('/')
    if len(parts) >= 2:
        category = parts[1]
        # Validate it's a known category
        valid_categories = DocumentCategory.choices()
        if category in valid_categories:
            return category

    return None


def _validate_category_type_consistency(category: str, doc_type: str, file_path: str, console: Console):
    """
    Validate that category and document_type are consistent with each other.

    Args:
        category: Document category
        doc_type: Document type
        file_path: File path (for error messages)
        console: Rich console for output

    Raises:
        click.Abort: If inconsistency detected
    """
    # Extract category from path if it exists
    path_category = None
    if file_path.startswith('docs/'):
        parts = file_path.split('/')
        if len(parts) >= 2:
            path_category = parts[1]

    # Check if category matches path
    if path_category and category != path_category:
        console.print()
        console.print(f"[red]❌ Category mismatch detected[/red]")
        console.print()
        console.print(f"  Path indicates: [yellow]{path_category}[/yellow]")
        console.print(f"  Flag specifies: [yellow]{category}[/yellow]")
        console.print()
        console.print("💡 [cyan]To fix:[/cyan]")
        console.print(f"   • Use [dim]--category={path_category}[/dim] to match path")
        console.print(f"   • Or update path to [dim]docs/{category}/...[/dim]")
        console.print()
        raise click.Abort()

    # Check if document_type matches path
    if file_path.startswith('docs/'):
        parts = file_path.split('/')
        if len(parts) >= 3:
            path_doc_type = parts[2]
            if doc_type != path_doc_type:
                console.print()
                console.print(f"[red]❌ Document type mismatch detected[/red]")
                console.print()
                console.print(f"  Path indicates: [yellow]{path_doc_type}[/yellow]")
                console.print(f"  Flag specifies: [yellow]{doc_type}[/yellow]")
                console.print()
                console.print("💡 [cyan]To fix:[/cyan]")
                console.print(f"   • Use [dim]--type={path_doc_type}[/dim] to match path")
                console.print(f"   • Or update path to [dim]docs/{category}/{doc_type}/...[/dim]")
                console.print()
                raise click.Abort()

    # Check if category/type mapping is logical
    expected_category = CATEGORY_MAPPING.get(doc_type)
    if expected_category and expected_category != category:
        console.print()
        console.print(f"[yellow]⚠️  Category and type may be inconsistent[/yellow]")
        console.print()
        console.print(f"  Document type: [cyan]{doc_type}[/cyan]")
        console.print(f"  Expected category: [cyan]{expected_category}[/cyan]")
        console.print(f"  Specified category: [cyan]{category}[/cyan]")
        console.print()
        console.print("💡 [cyan]Note:[/cyan] This is a recommendation, not an error")
        console.print()


def calculate_content_hash_from_string(content: str) -> str:
    """Calculate SHA256 hash from string content."""
    import hashlib
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _generate_file_from_database(project_root: Path, document, console: Console):
    """Generate physical file from database content."""
    try:
        # Create directory structure
        file_path = project_root / document.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        file_path.write_text(document.content, encoding='utf-8')
        
        console.print(f"[green]✅ Generated file: {document.file_path}[/green]")
        
        # Update sync status to SYNCED
        from agentpm.core.database.methods import document_references as doc_methods
        from agentpm.core.database.enums import SyncStatus
        from datetime import datetime
        
        # Get db service from context (need to pass it properly)
        # For now, we'll update sync status in the main function
        console.print(f"[cyan]📁 File created and ready for sync[/cyan]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to generate file: {e}[/red]")
        raise
