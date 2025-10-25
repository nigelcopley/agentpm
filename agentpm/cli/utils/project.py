"""
Project Detection Utilities

Provides git-style project root detection by walking up the directory tree
looking for .aipm directories. Works from any subdirectory of a project.
"""

from pathlib import Path
from typing import Optional
import click


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find nearest .aipm project directory by walking up the tree.

    Similar to git's .git directory detection. Starts from current directory
    or specified path and walks up the tree until finding an .aipm directory
    or reaching the filesystem root.

    Args:
        start_path: Starting directory (defaults to current working directory)

    Returns:
        Path to project root containing .aipm directory, or None if not found

    Example:
        >>> # From /path/to/project/src/components
        >>> root = find_project_root()
        >>> # Returns /path/to/project (if .aipm exists there)
    """
    current = start_path or Path.cwd()

    # Walk up directory tree until finding .aipm or reaching root
    while current != current.parent:  # Stop at filesystem root
        aipm_dir = current / ".aipm"

        if aipm_dir.is_dir():
            return current

        current = current.parent

    return None


def ensure_project_root(ctx: click.Context) -> Path:
    """
    Get project root from context, or abort with helpful error.

    Used by commands that require an initialized project. Provides
    clear error messages with actionable next steps when not in a project.

    Args:
        ctx: Click context containing project_root

    Returns:
        Path to project root

    Raises:
        click.Abort: If not in an AIPM project (with helpful error message)

    Example:
        ```python
        @click.command()
        @click.pass_context
        def status(ctx):
            project_root = ensure_project_root(ctx)
            # ... use project_root
        ```
    """
    console_err = ctx.obj['console_err']
    project_root = ctx.obj.get('project_root')

    if not project_root:
        console_err.print("❌ [red]Not in an AIPM project[/red]\n")
        console_err.print("💡 [yellow]To initialize a new project:[/yellow]")
        console_err.print("   apm init \"My Project Name\"\n")
        console_err.print("📚 [cyan]Or navigate to an existing project directory[/cyan]")
        console_err.print("   cd /path/to/your/project")
        raise click.Abort()

    return project_root


def get_current_project_id(ctx: click.Context) -> int:
    """
    Get current project ID from database.

    Retrieves the project database record for the current project root.
    Ensures project is properly initialized in the database.

    Args:
        ctx: Click context

    Returns:
        Project ID from database

    Raises:
        click.Abort: If project not found in database (with recovery steps)

    Example:
        ```python
        @click.command()
        @click.pass_context
        def my_command(ctx):
            project_id = get_current_project_id(ctx)
            # ... use project_id
        ```
    """
    from pathlib import Path
    from agentpm.cli.utils.services import get_database_service
    from agentpm.core.database.methods import projects as project_methods

    project_root = ensure_project_root(ctx)
    
    # Respect injected db_service from tests; only derive if missing
    if 'db_service' not in ctx.obj or ctx.obj['db_service'] is None:
        db = get_database_service(Path(project_root))
    else:
        db = ctx.obj['db_service']

    # Query for project by path
    all_projects = project_methods.list_projects(db)
    project = None
    for p in all_projects:
        if Path(p.path) == Path(project_root):
            project = p
            break

    if not project:
        ctx.obj['console_err'].print(
            f"❌ [red]Project not found in database:[/red] {project_root}\n"
        )
        ctx.obj['console_err'].print(
            "💡 [yellow]Try re-initializing with:[/yellow]\n"
            "   apm init \"Project Name\""
        )
        raise click.Abort()

    return project.id
