"""
Memory CLI Commands

Commands for managing Claude's persistent memory files.
Provides interface to the memory file generation system (WI-114).

Pattern: Click commands with Rich formatting
"""

import click
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.memory import MemoryFileType, ValidationStatus
from agentpm.core.database.methods import memory_methods
from agentpm.services.memory.generator import MemoryGenerator
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service


@click.group()
def memory():
    """Manage Claude's persistent memory files."""
    pass


@memory.command()
@click.option(
    "--type",
    "file_type",
    type=click.Choice([t.value for t in MemoryFileType]),
    help="Specific memory type to generate"
)
@click.option(
    "--force",
    is_flag=True,
    help="Regenerate even if current"
)
@click.option(
    "--all",
    "generate_all",
    is_flag=True,
    help="Generate all memory types"
)
@click.pass_context
def generate(
    ctx: click.Context,
    file_type: Optional[str],
    force: bool,
    generate_all: bool
):
    """
    Generate memory files for Claude handover.

    Generates markdown files in .claude/ directory that provide Claude with
    always-current access to APM (Agent Project Manager) database content (rules, agents, workflow, etc.).

    \b
    Examples:
      apm memory generate --all              # Generate all memory files
      apm memory generate --type=rules       # Generate only RULES.md
      apm memory generate --force --all      # Force regenerate all files

    \b
    Memory File Types:
      - rules:       RULES.md - Governance rules system
      - principles:  PRINCIPLES.md - Development principles
      - workflow:    WORKFLOW.md - Quality-gated workflow
      - agents:      AGENTS.md - Agent system architecture
      - context:     CONTEXT.md - Context assembly system
      - project:     PROJECT.md - Project information
      - ideas:       IDEAS.md - Ideas analysis pipeline
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Initialize generator
    generator = MemoryGenerator(db, project_root)

    try:
        if generate_all:
            # Generate all memory files
            console.print("[blue]Generating all memory files...[/blue]\n")
            memory_files = generator.generate_all_memory_files(project_id)

            # Display results in table
            _display_generation_results(console, memory_files, project_root)

        elif file_type:
            # Generate specific file type
            console.print(f"[blue]Generating {file_type.upper()} memory file...[/blue]\n")
            memory_file_type = MemoryFileType(file_type)
            memory_file = generator.generate_memory_file(
                project_id,
                memory_file_type,
                force_regenerate=force
            )

            # Display single result
            _display_single_result(console, memory_file, project_root)

        else:
            console.print("[yellow]Please specify --type or --all[/yellow]")
            console.print("\nExamples:")
            console.print("  apm memory generate --all")
            console.print("  apm memory generate --type=rules")
            return

        console.print("\n[green]✓ Memory files generated successfully[/green]")

    except Exception as e:
        console.print(f"\n[red]✗ Error generating memory files: {e}[/red]")
        raise click.Abort()


@memory.command()
@click.pass_context
def status(ctx: click.Context):
    """
    Show status of memory files.

    Displays table of all memory files with:
    - File type
    - Last generated timestamp
    - Validation status
    - Staleness indicator
    - File size

    \b
    Examples:
      apm memory status    # Show all memory files status
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Get all memory files for project
    memory_files = memory_methods.list_memory_files(db, project_id=project_id)

    if not memory_files:
        console.print("[yellow]No memory files generated yet[/yellow]")
        console.print("\n💡 Generate memory files: [cyan]apm memory generate --all[/cyan]")
        return

    # Create status table
    table = Table(title="Memory Files Status", show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("File Path", style="dim")
    table.add_column("Last Generated", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Size", justify="right", style="green")

    for memory_file in memory_files:
        # Calculate file size
        file_size = _format_file_size(len(memory_file.content))

        # Format timestamp
        try:
            gen_time = datetime.fromisoformat(memory_file.generated_at)
            time_str = gen_time.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            time_str = memory_file.generated_at

        # Status with indicators
        status_str = memory_file.validation_status.value
        if memory_file.is_stale:
            status_str = f"[red]{status_str} (stale)[/red]"
        elif memory_file.is_expired:
            status_str = f"[yellow]{status_str} (expired)[/yellow]"
        else:
            status_str = f"[green]{status_str}[/green]"

        table.add_row(
            memory_file.file_type.value,
            memory_file.file_path,
            time_str,
            status_str,
            file_size
        )

    console.print()
    console.print(table)
    console.print()

    # Show summary
    stale_count = sum(1 for mf in memory_files if mf.is_stale)
    if stale_count > 0:
        console.print(f"[yellow]⚠️  {stale_count} file(s) need regeneration[/yellow]")
        console.print("💡 Regenerate: [cyan]apm memory generate --all --force[/cyan]\n")


@memory.command()
@click.option(
    "--type",
    "file_type",
    type=click.Choice([t.value for t in MemoryFileType]),
    help="Specific memory type to validate"
)
@click.pass_context
def validate(ctx: click.Context, file_type: Optional[str]):
    """
    Validate memory file accuracy against database.

    Checks if memory files are current and accurate by comparing:
    - File hash with database record
    - Expiration status
    - Staleness indicators

    \b
    Examples:
      apm memory validate                # Validate all memory files
      apm memory validate --type=rules   # Validate specific file
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Get memory files to validate
    if file_type:
        memory_file_type = MemoryFileType(file_type)
        memory_file = memory_methods.get_memory_file_by_type(db, project_id, memory_file_type)
        memory_files = [memory_file] if memory_file else []
    else:
        memory_files = memory_methods.list_memory_files(db, project_id=project_id)

    if not memory_files:
        console.print("[yellow]No memory files to validate[/yellow]")
        return

    # Validate each file
    console.print("\n[blue]Validating memory files...[/blue]\n")

    validation_results = []
    for memory_file in memory_files:
        result = _validate_memory_file(memory_file, project_root)
        validation_results.append(result)

    # Display results
    table = Table(title="Validation Results", show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("File Exists", justify="center")
    table.add_column("Hash Match", justify="center")
    table.add_column("Is Current", justify="center")
    table.add_column("Issues", style="yellow")

    for result in validation_results:
        table.add_row(
            result['type'],
            "✓" if result['file_exists'] else "✗",
            "✓" if result['hash_match'] else "✗",
            "✓" if result['is_current'] else "✗",
            ", ".join(result['issues']) if result['issues'] else "[green]None[/green]"
        )

    console.print(table)
    console.print()

    # Summary
    failed_count = sum(1 for r in validation_results if r['issues'])
    if failed_count > 0:
        console.print(f"[red]✗ {failed_count} file(s) have validation issues[/red]")
        console.print("💡 Regenerate: [cyan]apm memory generate --all --force[/cyan]\n")
    else:
        console.print("[green]✓ All memory files are valid[/green]\n")


# Helper functions

def _display_generation_results(console: Console, memory_files: list, project_root: Path):
    """Display table of generated memory files."""
    table = Table(title="Generated Memory Files", show_header=True)
    table.add_column("Type", style="cyan")
    table.add_column("File Path", style="dim")
    table.add_column("Quality", style="magenta")
    table.add_column("Duration", justify="right", style="yellow")

    for memory_file in memory_files:
        # Format quality score
        quality = f"{memory_file.confidence_score:.1%} / {memory_file.completeness_score:.1%}"

        # Format duration
        duration = f"{memory_file.generation_duration_ms}ms" if memory_file.generation_duration_ms else "N/A"

        table.add_row(
            memory_file.file_type.value,
            memory_file.file_path,
            quality,
            duration
        )

    console.print(table)


def _display_single_result(console: Console, memory_file, project_root: Path):
    """Display single memory file generation result."""
    console.print(Panel(
        f"[bold cyan]{memory_file.file_type.value.upper()}[/bold cyan]\n"
        f"[dim]📄 {memory_file.file_path}[/dim]\n\n"
        f"Confidence: {memory_file.confidence_score:.1%}\n"
        f"Completeness: {memory_file.completeness_score:.1%}\n"
        f"Duration: {memory_file.generation_duration_ms}ms\n"
        f"Status: {memory_file.validation_status.value}",
        title="Memory File Generated"
    ))


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"


def _validate_memory_file(memory_file, project_root: Path) -> dict:
    """
    Validate a memory file.

    Returns dict with validation results:
    - type: File type
    - file_exists: Whether file exists on disk
    - hash_match: Whether file hash matches database
    - is_current: Whether file is current (not stale/expired)
    - issues: List of validation issues
    """
    import hashlib

    issues = []

    # Check if file exists
    file_path = project_root / memory_file.file_path
    file_exists = file_path.exists()

    if not file_exists:
        issues.append("File missing on disk")

    # Check hash match
    hash_match = False
    if file_exists:
        file_content = file_path.read_text(encoding='utf-8')
        file_hash = hashlib.sha256(file_content.encode()).hexdigest()
        hash_match = (file_hash == memory_file.file_hash)

        if not hash_match:
            issues.append("Hash mismatch (file modified)")

    # Check if current
    is_current = not (memory_file.is_stale or memory_file.is_expired)

    if memory_file.is_stale:
        issues.append("Marked as stale")
    if memory_file.is_expired:
        issues.append("Expired")

    return {
        'type': memory_file.file_type.value,
        'file_exists': file_exists,
        'hash_match': hash_match,
        'is_current': is_current,
        'issues': issues
    }
