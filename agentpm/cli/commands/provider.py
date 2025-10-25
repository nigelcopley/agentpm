"""
apm provider - Provider Management Commands

Commands for managing IDE providers (Cursor, VS Code, Zed, etc.):
- install: Install provider for project
- uninstall: Remove provider
- verify: Check installation integrity
- sync-memories: Sync APM learnings with provider memories
- list: List installed providers
- status: Show provider installation status

Pattern: Rich CLI output with tables and panels
Database-first: All operations tracked in database
"""

import click
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.providers.cursor.provider import CursorProvider


@click.group()
@click.pass_context
def provider(ctx):
    """
    Manage IDE provider integrations.

    Supported providers:
    - cursor: Cursor IDE integration
    - vscode: VS Code integration (coming soon)
    - zed: Zed integration (coming soon)

    \b
    Examples:
      apm provider install cursor
      apm provider verify cursor
      apm provider sync-memories cursor
      apm provider list
    """
    # Ensure ctx.obj exists with console
    if ctx.obj is None:
        from rich.console import Console
        ctx.obj = {'console': Console()}


@provider.command()
@click.argument('provider_name', type=click.Choice(['cursor'], case_sensitive=False))
@click.option(
    '--tech-stack',
    multiple=True,
    help='Technology stack (e.g., Python, SQLite)'
)
@click.option(
    '--no-rules',
    is_flag=True,
    default=False,
    help='Skip rules installation'
)
@click.option(
    '--no-memories',
    is_flag=True,
    default=False,
    help='Skip memory sync'
)
@click.option(
    '--no-modes',
    is_flag=True,
    default=False,
    help='Skip custom modes'
)
@click.pass_context
def install(
    ctx: click.Context,
    provider_name: str,
    tech_stack: tuple,
    no_rules: bool,
    no_memories: bool,
    no_modes: bool,
):
    """
    Install IDE provider for current project.

    Installs provider files including:
    - Rules (6 consolidated rules from WI-118)
    - Indexing configuration (.cursorignore)
    - Custom modes (optional)
    - Memory templates (optional)

    \b
    Examples:
      apm provider install cursor
      apm provider install cursor --tech-stack Python --tech-stack SQLite
      apm provider install cursor --no-rules --no-memories
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()
    console.print(f"[bold cyan]Installing {provider_name} provider...[/bold cyan]")
    console.print()

    # Build configuration
    config = {
        "tech_stack": [*tech_stack],  # Convert tuple to list without calling list()
        "rules_enabled": not no_rules,
        "memory_sync_enabled": not no_memories,
        "modes_enabled": not no_modes,
        "indexing_enabled": True,
        "guardrails_enabled": True,
    }

    # Install provider
    if provider_name == 'cursor':
        provider = CursorProvider(db)
        result = provider.install(project_root, config)

        if result.success:
            # Success table
            table = Table(title="Installation Successful", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Provider", provider_name.title())
            table.add_row("Files installed", str(len(result.installed_files)))
            table.add_row("Installation ID", str(result.installation_id))

            console.print(table)
            console.print()

            # Installed files
            if result.installed_files:
                files_panel = Panel(
                    "\n".join(f"  • {f}" for f in result.installed_files[:10]),
                    title=f"Installed Files ({len(result.installed_files)} total)",
                    border_style="green",
                )
                console.print(files_panel)
                console.print()

            console.print("[green]✓[/green] Cursor provider installed successfully")
            console.print()
            console.print("[dim]Next steps:[/dim]")
            console.print("  1. Restart Cursor IDE")
            console.print("  2. Check rules in .cursor/rules/")
            console.print("  3. Run: apm provider verify cursor")
            console.print()

        else:
            console.print(f"[red]✗[/red] Installation failed: {result.message}")
            if result.errors:
                console.print()
                console.print("[yellow]Errors:[/yellow]")
                for error in result.errors:
                    console.print(f"  • {error}")
            console.print()
            ctx.exit(1)

    else:
        console.print(f"[red]✗[/red] Provider '{provider_name}' not yet implemented")
        ctx.exit(1)


@provider.command()
@click.argument('provider_name', type=click.Choice(['cursor'], case_sensitive=False))
@click.option(
    '--force',
    is_flag=True,
    default=False,
    help='Force uninstall without confirmation'
)
@click.pass_context
def uninstall(
    ctx: click.Context,
    provider_name: str,
    force: bool,
):
    """
    Uninstall IDE provider.

    Removes all provider files and database records.

    \b
    Examples:
      apm provider uninstall cursor
      apm provider uninstall cursor --force
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    if not force:
        console.print()
        console.print(f"[yellow]Warning:[/yellow] This will remove all {provider_name} files")
        if not click.confirm("Continue?"):
            console.print("Cancelled")
            ctx.exit(0)

    console.print()
    console.print(f"[bold cyan]Uninstalling {provider_name} provider...[/bold cyan]")

    if provider_name == 'cursor':
        provider = CursorProvider(db)
        success = provider.uninstall(project_root)

        if success:
            console.print(f"[green]✓[/green] {provider_name.title()} provider uninstalled")
        else:
            console.print(f"[red]✗[/red] Failed to uninstall {provider_name} provider")
            ctx.exit(1)

    console.print()


@provider.command()
@click.pass_context
def list(ctx: click.Context):
    """
    List installed providers.

    Shows all installed IDE providers and their status.

    \b
    Example:
      apm provider list
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()
    console.print("[bold cyan]Installed Providers[/bold cyan]")
    console.print()

    # Query installed providers
    with db.connect() as conn:
        rows = conn.execute(
            """
            SELECT provider_type, provider_version, status, installed_at, last_verified_at
            FROM provider_installations
            WHERE project_id = (SELECT id FROM projects WHERE path = ?)
            """,
            (str(project_root),)
        ).fetchall()

    if not rows:
        console.print("[dim]No providers installed[/dim]")
        console.print()
        console.print("[dim]Install a provider with:[/dim]")
        console.print("  apm provider install cursor")
        console.print()
        return

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="cyan")
    table.add_column("Version")
    table.add_column("Status")
    table.add_column("Installed At")
    table.add_column("Last Verified")

    for row in rows:
        status_style = {
            "installed": "green",
            "partial": "yellow",
            "failed": "red",
            "uninstalled": "dim",
        }.get(row["status"], "white")

        table.add_row(
            row["provider_type"].title(),
            row["provider_version"],
            f"[{status_style}]{row['status']}[/{status_style}]",
            row["installed_at"][:10],
            row["last_verified_at"][:10] if row["last_verified_at"] else "-",
        )

    console.print(table)
    console.print()


@provider.command()
@click.argument('provider_name', type=click.Choice(['cursor'], case_sensitive=False))
@click.pass_context
def verify(ctx: click.Context, provider_name: str):
    """
    Verify provider installation integrity.

    Checks:
    - All installed files exist
    - File hashes match (detect modifications)
    - Database records are consistent

    \b
    Examples:
      apm provider verify cursor
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()
    console.print(f"[bold cyan]Verifying {provider_name} provider...[/bold cyan]")
    console.print()

    if provider_name == 'cursor':
        provider = CursorProvider(db)
        result = provider.verify(project_root)

        if result.success:
            table = Table(title="Verification Successful", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Verified files", str(result.verified_files))
            table.add_row("Missing files", str(len(result.missing_files)))
            table.add_row("Modified files", str(len(result.modified_files)))

            console.print(table)
            console.print()
            console.print(f"[green]✓[/green] {result.message}")

        else:
            console.print(f"[red]✗[/red] {result.message}")
            console.print()

            if result.missing_files:
                console.print("[yellow]Missing files:[/yellow]")
                for file_path in result.missing_files:
                    console.print(f"  • {file_path}")
                console.print()

            if result.modified_files:
                console.print("[yellow]Modified files:[/yellow]")
                for file_path in result.modified_files:
                    console.print(f"  • {file_path}")
                console.print()

            console.print("[dim]To fix, run:[/dim]")
            console.print(f"  apm provider install {provider_name}")
            console.print()
            ctx.exit(1)

    console.print()


@provider.command()
@click.argument('provider_name', type=click.Choice(['cursor'], case_sensitive=False))
@click.option(
    '--direction',
    type=click.Choice(['to_cursor', 'from_cursor', 'bi_directional'], case_sensitive=False),
    default='to_cursor',
    help='Sync direction'
)
@click.pass_context
def sync_memories(
    ctx: click.Context,
    provider_name: str,
    direction: str,
):
    """
    Sync APM learnings with provider memories.

    Directions:
    - to_cursor: APM learnings → Cursor memories (default)
    - from_cursor: Cursor memories → APM learnings (coming soon)
    - bi_directional: Both directions (coming soon)

    \b
    Examples:
      apm provider sync-memories cursor
      apm provider sync-memories cursor --direction to_cursor
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()
    console.print(f"[bold cyan]Syncing memories ({direction})...[/bold cyan]")
    console.print()

    if provider_name == 'cursor':
        provider = CursorProvider(db)
        result = provider.sync_memories(project_root, direction)

        if result.success:
            table = Table(title="Memory Sync Successful", show_header=False)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            if result.synced_to_cursor > 0:
                table.add_row("Synced to Cursor", str(result.synced_to_cursor))
            if result.synced_from_cursor > 0:
                table.add_row("Synced from Cursor", str(result.synced_from_cursor))
            if result.skipped > 0:
                table.add_row("Skipped", str(result.skipped))

            console.print(table)
            console.print()
            console.print(f"[green]✓[/green] {result.message}")

        else:
            console.print(f"[red]✗[/red] {result.message}")
            if result.errors:
                console.print()
                console.print("[yellow]Errors:[/yellow]")
                for error in result.errors:
                    console.print(f"  • {error}")
            ctx.exit(1)

    console.print()


@provider.command()
@click.argument('provider_name', type=click.Choice(['cursor'], case_sensitive=False))
@click.pass_context
def status(ctx: click.Context, provider_name: str):
    """
    Show provider installation status.

    Displays detailed installation information including:
    - Installation status
    - Installed files count
    - Version information
    - Last verification timestamp

    \b
    Example:
      apm provider status cursor
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()

    if provider_name == 'cursor':
        provider = CursorProvider(db)
        status_data = provider.get_status(project_root)

        if status_data["status"] == "not_found":
            console.print("[red]✗[/red] Project not found")
            ctx.exit(1)

        if status_data["status"] == "not_installed":
            console.print(f"[yellow]![/yellow] {provider_name.title()} provider not installed")
            console.print()
            console.print("[dim]Install with:[/dim]")
            console.print(f"  apm provider install {provider_name}")
            console.print()
            return

        # Status table
        table = Table(title=f"{provider_name.title()} Provider Status", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        status_style = {
            "installed": "green",
            "partial": "yellow",
            "failed": "red",
        }.get(status_data["status"], "white")

        table.add_row("Status", f"[{status_style}]{status_data['status']}[/{status_style}]")
        table.add_row("Version", status_data["version"])
        table.add_row("Installed files", str(status_data["installed_files"]))
        table.add_row("Installed at", status_data["installed_at"][:10])
        table.add_row("Updated at", status_data["updated_at"][:10])
        if status_data.get("last_verified_at"):
            table.add_row("Last verified", status_data["last_verified_at"][:10])

        console.print(table)

    console.print()
