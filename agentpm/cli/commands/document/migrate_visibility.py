"""
Document Visibility Migration Command

CLI command for migrating document visibility settings.

Work Item: #164 - Auto-Generate Document File Paths
Task: #1084 - Create Document Migration Script
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service


@click.command()
@click.option('--dry-run', is_flag=True, default=False,
              help='Preview migration without making changes (default)')
@click.option('--execute', is_flag=True, default=False,
              help='Execute migration and apply changes')
@click.pass_context
def migrate_visibility(ctx: click.Context, dry_run: bool, execute: bool):
    """
    Migrate document visibility settings based on path and type.

    Auto-assigns visibility_scope to existing documents:

    \b
    Path-Based Assignment:
      .agentpm/docs/*  → private
      docs/*           → public

    \b
    Type-Based Override (always private):
      - Testing types (test_plan, test_report, coverage_report)
      - Research types (analysis_report, competitive_analysis)
      - Planning types (idea, requirements)

    \b
    Published State:
      - Public docs/ → published_date = created_at
      - Private      → published_date = NULL

    \b
    Safety Features:
      • Dry-run mode (default - preview only)
      • Transaction safety (atomic updates)
      • Validation after migration
      • Detailed statistics
      • Rollback on errors

    \b
    Examples:
      # Preview migration (default behavior)
      apm document migrate-visibility --dry-run

      # Execute migration (requires confirmation)
      apm document migrate-visibility --execute

      # Same as --dry-run
      apm document migrate-visibility

    \b
    Migration Logic:
      1. Analyze all documents in database
      2. Determine visibility from path and type
      3. Apply type-based overrides (force private)
      4. Set published_date for public docs
      5. Validate all changes
      6. Report statistics

    \b
    See Also:
      apm document list              # View documents
      apm document show <id>         # View document details
      apm document migrate-to-structure  # Migrate file paths
    """
    console = Console()

    # Get project context
    project_root = ensure_project_root(ctx)
    db_service = get_database_service(project_root)
    db_path = project_root / '.agentpm' / 'data' / 'agentpm.db'

    # Validate flags
    if not dry_run and not execute:
        # Default to dry-run if neither specified
        dry_run = True
        console.print("[yellow]No mode specified, defaulting to --dry-run (preview only)[/yellow]")
        console.print()

    if dry_run and execute:
        console.print("[yellow]Both --dry-run and --execute specified. Using --dry-run (safe mode).[/yellow]")
        console.print()
        execute = False
        dry_run = True

    # Import migration script
    from agentpm.migrations.scripts.migrate_document_visibility import (
        migrate_document_visibility,
        analyze_documents,
        validate_migration,
    )

    # Display header
    console.print()
    console.print(Panel(
        f"[bold]Document Visibility Migration[/bold]\n\n"
        f"Mode: {'🔍 DRY RUN (preview only)' if dry_run else '⚡ EXECUTE (applying changes)'}\n"
        f"Database: {db_path.relative_to(project_root)}",
        style="bold blue"
    ))
    console.print()

    # Confirmation for execute mode
    if execute:
        console.print("[bold yellow]⚠️  WARNING: This will update document visibility in the database.[/bold yellow]")
        console.print()
        console.print("Migration will:")
        console.print("  • Set visibility based on document path and type")
        console.print("  • Set published_date for public documents")
        console.print("  • Apply type-based overrides (force private for internal types)")
        console.print()

        if not click.confirm("Continue with migration?", default=False):
            console.print("[yellow]Migration cancelled by user[/yellow]")
            return

        console.print()

    # Run migration
    try:
        success = migrate_document_visibility(db_path, dry_run=dry_run)

        if success:
            if dry_run:
                console.print()
                console.print(Panel(
                    "[bold green]✓ Analysis Complete[/bold green]\n\n"
                    "To execute migration:\n"
                    "  apm document migrate-visibility --execute",
                    style="green"
                ))
            else:
                console.print()
                console.print(Panel(
                    "[bold green]✓ Migration Complete[/bold green]\n\n"
                    "All documents have been updated with correct visibility settings.",
                    style="green"
                ))
        else:
            console.print()
            console.print(Panel(
                "[bold red]✗ Migration Failed[/bold red]\n\n"
                "See error messages above for details.",
                style="red"
            ))
            ctx.exit(1)

    except Exception as e:
        console.print()
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        ctx.exit(1)
