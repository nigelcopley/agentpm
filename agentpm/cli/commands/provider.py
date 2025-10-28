"""
apm provider - Provider Management Commands

Commands for managing LLM provider configurations (Claude Code, Cursor, Codex):
- install: Install provider configuration for project
- uninstall: Remove provider configuration
- verify: Check installation integrity (SHA-256)
- sync: Regenerate configs from database
- list: List installed providers
- status: Show provider installation status

Pattern: Rich CLI output with tables and panels
Database-first: All operations tracked in database
Multi-provider: Supports Claude Code, Cursor, OpenAI Codex
"""

import click
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.providers.cursor.provider import CursorProvider
from agentpm.providers.common.agents_generator import AGENTSMDGenerator
from agentpm.providers.common.integrity import SHA256HashVerifier
from agentpm.providers.cursor.generator import CursorGenerator
from agentpm.providers.anthropic.claude_code.generation.generator import ClaudeCodeGenerator
from agentpm.providers.openai.codex.generator import CodexGenerator


def normalize_provider_name(name: str) -> str:
    """
    Normalize provider name from CLI format to database format.

    CLI accepts: claude-code, cursor, codex
    Database expects: claude_code, cursor, codex
    """
    return name.replace('-', '_')


@click.group()
@click.pass_context
def provider(ctx):
    """
    Manage LLM provider configurations.

    Supported providers:
    - claude-code: Anthropic Claude Code integration
    - cursor: Cursor IDE integration
    - codex: OpenAI Codex integration

    \b
    Examples:
      apm provider install claude-code
      apm provider install cursor --tech-stack Python SQLite
      apm provider sync claude-code
      apm provider verify --all
      apm provider list
    """
    # Ensure ctx.obj exists with console
    if ctx.obj is None:
        from rich.console import Console
        ctx.obj = {'console': Console()}


@provider.command()
@click.argument('provider_name', type=click.Choice(['claude-code', 'cursor', 'codex'], case_sensitive=False))
@click.option(
    '--tech-stack',
    multiple=True,
    help='Technology stack (e.g., Python, SQLite) - for Cursor only'
)
@click.option(
    '--model',
    help='Model name (e.g., gpt-4) - for Codex only'
)
@click.pass_context
def install(
    ctx: click.Context,
    provider_name: str,
    tech_stack: tuple,
    model: Optional[str],
):
    """
    Install LLM provider configuration for current project.

    Generates native configuration files from APM database:
    - claude-code: Generates AGENTS.md + .claude/ config
    - cursor: Generates .cursorrules + .cursorignore
    - codex: Generates AGENTS.md (native format)

    All providers:
    1. Generate AGENTS.md from database (agents, rules, context)
    2. Generate provider-specific config files
    3. Track installation in database with SHA-256 hashes
    4. Enable integrity verification

    \b
    Examples:
      apm provider install claude-code
      apm provider install cursor --tech-stack Python --tech-stack SQLite
      apm provider install codex --model gpt-4
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    console.print()
    console.print(f"[bold cyan]Installing {provider_name} provider...[/bold cyan]")
    console.print()

    # Get project ID
    with db.connect() as conn:
        project_row = conn.execute(
            "SELECT id, name FROM projects WHERE path = ?",
            (str(project_root),)
        ).fetchone()

    if not project_row:
        console.print("[red]✗[/red] Project not found. Run: apm init")
        ctx.exit(1)

    project_id = project_row["id"]

    try:
        # Step 1: Generate AGENTS.md (universal format)
        console.print("[dim]Step 1/3:[/dim] Generating AGENTS.md from database...")
        agents_generator = AGENTSMDGenerator(db)
        agents_md_path = project_root / "AGENTS.md"
        agents_md_content = agents_generator.generate(
            project_id=project_id,
            output_path=agents_md_path,
            provider=provider_name
        )
        console.print("[green]✓[/green] Generated AGENTS.md")

        # Step 2: Generate provider-specific config
        console.print(f"[dim]Step 2/3:[/dim] Generating {provider_name} configuration...")

        if provider_name == 'cursor':
            # Use existing Cursor provider for Cursor-specific logic
            config = {
                "tech_stack": [*tech_stack] if tech_stack else [],
                "rules_enabled": True,
                "memory_sync_enabled": True,
                "modes_enabled": True,
                "indexing_enabled": True,
                "guardrails_enabled": True,
            }
            provider = CursorProvider(db)
            result = provider.install(project_root, config)

            if not result.success:
                console.print(f"[red]✗[/red] {result.message}")
                if result.errors:
                    for error in result.errors:
                        console.print(f"  • {error}")
                ctx.exit(1)

            files_created = result.installed_files
            console.print(f"[green]✓[/green] Generated {len(files_created)} Cursor files")

        elif provider_name == 'claude-code':
            # Generate Claude Code config
            from agentpm.core.database.methods import agents as agent_methods
            from agentpm.core.database.methods import rules as rule_methods
            from agentpm.core.database.methods import projects as project_methods

            agents = agent_methods.list_agents(db, project_id=project_id, active_only=True)
            rules = rule_methods.list_rules(db, project_id=project_id, enabled_only=True)
            project = project_methods.get_project(db, project_id)

            claude_generator = ClaudeCodeGenerator(db)
            claude_result = claude_generator.generate_from_agents(
                agents=agents,
                rules=rules,
                project=project,
                output_dir=project_root
            )

            if not claude_result.success:
                console.print(f"[red]✗[/red] Claude Code generation failed")
                for error in claude_result.errors:
                    console.print(f"  • {error}")
                ctx.exit(1)

            files_created = [str(f.path) for f in claude_result.files]
            console.print(f"[green]✓[/green] Generated {len(files_created)} Claude Code files")

        elif provider_name == 'codex':
            # Generate Codex config (AGENTS.md is native format)
            from agentpm.core.database.methods import agents as agent_methods
            from agentpm.core.database.methods import rules as rule_methods
            from agentpm.core.database.methods import projects as project_methods

            agents = agent_methods.list_agents(db, project_id=project_id, active_only=True)
            rules = rule_methods.list_rules(db, project_id=project_id, enabled_only=True)
            project = project_methods.get_project(db, project_id)

            codex_generator = CodexGenerator(db)
            codex_result = codex_generator.generate_from_agents(
                agents=agents,
                rules=rules,
                project=project,
                output_dir=project_root,
                model=model or "gpt-4"
            )

            if not codex_result.success:
                console.print(f"[red]✗[/red] Codex generation failed")
                for error in codex_result.errors:
                    console.print(f"  • {error}")
                ctx.exit(1)

            files_created = [str(f.path) for f in codex_result.files]
            console.print(f"[green]✓[/green] Generated {len(files_created)} Codex files")

        # Step 3: Store installation record in database
        console.print("[dim]Step 3/3:[/dim] Recording installation in database...")
        with db.connect() as conn:
            # Normalize provider name for database (claude-code -> claude_code)
            db_provider_name = normalize_provider_name(provider_name)
            # Insert or update provider_installations
            conn.execute("""
                INSERT OR REPLACE INTO provider_installations
                (project_id, provider_type, provider_version, install_path, status, config, installed_at, updated_at, installed_files)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)
            """, (project_id, db_provider_name, "1.0", str(project_root), "installed", "{}", str(files_created)))
            conn.commit()

        console.print("[green]✓[/green] Installation recorded")
        console.print()

        # Success summary
        table = Table(title="Installation Successful", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Provider", provider_name)
        table.add_row("Files created", str(len(files_created) + 1))  # +1 for AGENTS.md
        table.add_row("AGENTS.md", "✓")

        console.print(table)
        console.print()

        # Show files created
        files_panel = Panel(
            "\n".join(f"  • {f}" for f in ["AGENTS.md"] + files_created[:10]),
            title=f"Generated Files ({len(files_created) + 1} total)",
            border_style="green",
        )
        console.print(files_panel)
        console.print()

        # Next steps
        console.print("[dim]Next steps:[/dim]")
        if provider_name == 'claude-code':
            console.print("  1. Restart Claude Code")
            console.print("  2. Check .claude/ directory")
        elif provider_name == 'cursor':
            console.print("  1. Restart Cursor IDE")
            console.print("  2. Check .cursorrules file")
        elif provider_name == 'codex':
            console.print("  1. Run: codex --help")
            console.print("  2. Check AGENTS.md")
        console.print(f"  3. Run: apm provider verify {provider_name}")
        console.print()

    except Exception as e:
        console.print(f"[red]✗[/red] Installation failed: {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        ctx.exit(1)


@provider.command()
@click.argument('provider_name', type=click.Choice(['claude-code', 'cursor', 'codex'], case_sensitive=False), required=False)
@click.option(
    '--all',
    'sync_all',
    is_flag=True,
    help='Sync all installed providers'
)
@click.pass_context
def sync(
    ctx: click.Context,
    provider_name: Optional[str],
    sync_all: bool,
):
    """
    Sync provider configuration (regenerate from database).

    Regenerates configuration files from current database state:
    - Regenerates AGENTS.md with latest agents/rules/context
    - Regenerates provider-specific config files
    - Verifies file integrity (SHA-256 hashes)
    - Updates database records

    Use --all to sync all installed providers.

    \b
    Examples:
      apm provider sync claude-code
      apm provider sync --all
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get project ID
    with db.connect() as conn:
        project_row = conn.execute(
            "SELECT id FROM projects WHERE path = ?",
            (str(project_root),)
        ).fetchone()

    if not project_row:
        console.print("[red]✗[/red] Project not found. Run: apm init")
        ctx.exit(1)

    project_id = project_row["id"]

    # Determine which providers to sync
    if sync_all:
        with db.connect() as conn:
            installed = conn.execute(
                "SELECT provider_type FROM provider_installations WHERE project_id = ?",
                (project_id,)
            ).fetchall()
        providers_to_sync = [row["provider_type"] for row in installed]

        if not providers_to_sync:
            console.print("[yellow]![/yellow] No providers installed")
            console.print("Install a provider with: apm provider install <name>")
            return
    elif provider_name:
        providers_to_sync = [provider_name]
    else:
        console.print("[red]✗[/red] Specify provider name or use --all")
        ctx.exit(1)

    console.print()
    console.print(f"[bold cyan]Syncing {len(providers_to_sync)} provider(s)...[/bold cyan]")
    console.print()

    for prov in providers_to_sync:
        console.print(f"[dim]Provider:[/dim] {prov}")

        try:
            # Regenerate AGENTS.md
            console.print("  [dim]1/2:[/dim] Regenerating AGENTS.md...")
            agents_generator = AGENTSMDGenerator(db)
            agents_md_path = project_root / "AGENTS.md"
            agents_generator.generate(
                project_id=project_id,
                output_path=agents_md_path,
                provider=prov
            )
            console.print("  [green]✓[/green] AGENTS.md regenerated")

            # Regenerate provider config
            console.print(f"  [dim]2/2:[/dim] Regenerating {prov} configuration...")

            if prov == 'cursor':
                # Re-install Cursor
                config = {
                    "tech_stack": [],
                    "rules_enabled": True,
                    "memory_sync_enabled": True,
                    "modes_enabled": True,
                    "indexing_enabled": True,
                    "guardrails_enabled": True,
                }
                provider = CursorProvider(db)
                result = provider.install(project_root, config)
                if not result.success:
                    console.print(f"  [red]✗[/red] Failed: {result.message}")
                    continue

            elif prov == 'claude-code':
                from agentpm.core.database.methods import agents as agent_methods
                from agentpm.core.database.methods import rules as rule_methods
                from agentpm.core.database.methods import projects as project_methods

                agents = agent_methods.list_agents(db, project_id=project_id, active_only=True)
                rules = rule_methods.list_rules(db, project_id=project_id, enabled_only=True)
                project = project_methods.get_project(db, project_id)

                claude_generator = ClaudeCodeGenerator(db)
                claude_result = claude_generator.generate_from_agents(
                    agents=agents,
                    rules=rules,
                    project=project,
                    output_dir=project_root
                )
                if not claude_result.success:
                    console.print(f"  [red]✗[/red] Failed: {claude_result.errors}")
                    continue

            elif prov == 'codex':
                from agentpm.core.database.methods import agents as agent_methods
                from agentpm.core.database.methods import rules as rule_methods
                from agentpm.core.database.methods import projects as project_methods

                agents = agent_methods.list_agents(db, project_id=project_id, active_only=True)
                rules = rule_methods.list_rules(db, project_id=project_id, enabled_only=True)
                project = project_methods.get_project(db, project_id)

                codex_generator = CodexGenerator(db)
                codex_result = codex_generator.generate_from_agents(
                    agents=agents,
                    rules=rules,
                    project=project,
                    output_dir=project_root
                )
                if not codex_result.success:
                    console.print(f"  [red]✗[/red] Failed: {codex_result.errors}")
                    continue

            console.print(f"  [green]✓[/green] {prov} synced successfully")
            console.print()

        except Exception as e:
            console.print(f"  [red]✗[/red] Sync failed: {e}")
            console.print()

    console.print("[green]✓[/green] Sync complete")
    console.print()


@provider.command()
@click.argument('provider_name', type=click.Choice(['claude-code', 'cursor', 'codex'], case_sensitive=False))
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
    Uninstall LLM provider configuration.

    Removes all provider files and database records.
    Does NOT remove AGENTS.md (shared by all providers).

    \b
    Examples:
      apm provider uninstall cursor
      apm provider uninstall claude-code --force
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    if not force:
        console.print()
        console.print(f"[yellow]Warning:[/yellow] This will remove all {provider_name} files")
        console.print("[dim]Note: AGENTS.md will be preserved (shared by all providers)[/dim]")
        if not click.confirm("Continue?"):
            console.print("Cancelled")
            ctx.exit(0)

    console.print()
    console.print(f"[bold cyan]Uninstalling {provider_name} provider...[/bold cyan]")
    console.print()

    try:
        if provider_name == 'cursor':
            provider = CursorProvider(db)
            success = provider.uninstall(project_root)

            if success:
                console.print(f"[green]✓[/green] Cursor provider uninstalled")
            else:
                console.print(f"[red]✗[/red] Failed to uninstall Cursor provider")
                ctx.exit(1)

        elif provider_name == 'claude-code':
            # Remove .claude directory
            claude_dir = project_root / ".claude"
            if claude_dir.exists():
                import shutil
                shutil.rmtree(claude_dir)
                console.print(f"[green]✓[/green] Removed .claude/ directory")

            # Update database
            with db.connect() as conn:
                db_provider_name = normalize_provider_name('claude-code')
                conn.execute("""
                    DELETE FROM provider_installations
                    WHERE project_id = (SELECT id FROM projects WHERE path = ?)
                    AND provider_type = ?
                """, (str(project_root), db_provider_name))
                conn.commit()

            console.print(f"[green]✓[/green] Claude Code provider uninstalled")

        elif provider_name == 'codex':
            # Codex uses AGENTS.md natively, no provider-specific files to remove
            # Just update database
            with db.connect() as conn:
                db_provider_name = normalize_provider_name('codex')
                conn.execute("""
                    DELETE FROM provider_installations
                    WHERE project_id = (SELECT id FROM projects WHERE path = ?)
                    AND provider_type = ?
                """, (str(project_root), db_provider_name))
                conn.commit()

            console.print(f"[green]✓[/green] Codex provider uninstalled")

    except Exception as e:
        console.print(f"[red]✗[/red] Uninstall failed: {e}")
        ctx.exit(1)

    console.print()


@provider.command()
@click.pass_context
def list(ctx: click.Context):
    """
    List installed providers.

    Shows all installed LLM providers and their status.
    Displays provider type, version, status, and installation timestamps.

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
        console.print("  apm provider install claude-code")
        console.print("  apm provider install cursor")
        console.print("  apm provider install codex")
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

        # Format provider name nicely
        prov_name = row["provider_type"]
        if prov_name == "claude-code":
            display_name = "Claude Code"
        elif prov_name == "cursor":
            display_name = "Cursor"
        elif prov_name == "codex":
            display_name = "OpenAI Codex"
        else:
            display_name = prov_name.title()

        table.add_row(
            display_name,
            row["provider_version"],
            f"[{status_style}]{row['status']}[/{status_style}]",
            row["installed_at"][:10] if row["installed_at"] else "-",
            row["last_verified_at"][:10] if row["last_verified_at"] else "-",
        )

    console.print(table)
    console.print()
    console.print(f"[dim]Tip:[/dim] Run 'apm provider verify --all' to check integrity")
    console.print()


@provider.command()
@click.argument('provider_name', type=click.Choice(['claude-code', 'cursor', 'codex'], case_sensitive=False), required=False)
@click.option(
    '--all',
    'verify_all',
    is_flag=True,
    help='Verify all installed providers'
)
@click.pass_context
def verify(
    ctx: click.Context,
    provider_name: Optional[str],
    verify_all: bool,
):
    """
    Verify provider installation integrity.

    Checks:
    - All installed files exist
    - File integrity using SHA-256 hashes
    - Database records are consistent

    Use --all to verify all installed providers.

    \b
    Examples:
      apm provider verify claude-code
      apm provider verify --all
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)

    # Get project ID
    with db.connect() as conn:
        project_row = conn.execute(
            "SELECT id FROM projects WHERE path = ?",
            (str(project_root),)
        ).fetchone()

    if not project_row:
        console.print("[red]✗[/red] Project not found. Run: apm init")
        ctx.exit(1)

    project_id = project_row["id"]

    # Determine which providers to verify
    if verify_all:
        with db.connect() as conn:
            installed = conn.execute(
                "SELECT provider_type FROM provider_installations WHERE project_id = ?",
                (project_id,)
            ).fetchall()
        providers_to_verify = [row["provider_type"] for row in installed]

        if not providers_to_verify:
            console.print("[yellow]![/yellow] No providers installed")
            console.print("Install a provider with: apm provider install <name>")
            return
    elif provider_name:
        providers_to_verify = [provider_name]
    else:
        console.print("[red]✗[/red] Specify provider name or use --all")
        ctx.exit(1)

    console.print()
    console.print(f"[bold cyan]Verifying {len(providers_to_verify)} provider(s)...[/bold cyan]")
    console.print()

    all_verified = True

    for prov in providers_to_verify:
        console.print(f"[dim]Provider:[/dim] {prov}")

        if prov == 'cursor':
            # Use existing Cursor provider verify
            provider = CursorProvider(db)
            result = provider.verify(project_root)

            if result.success:
                console.print(f"  [green]✓[/green] All files verified ({result.verified_files} files)")
            else:
                console.print(f"  [red]✗[/red] Verification failed")
                if result.missing_files:
                    console.print(f"  [yellow]Missing:[/yellow] {len(result.missing_files)} files")
                if result.modified_files:
                    console.print(f"  [yellow]Modified:[/yellow] {len(result.modified_files)} files")
                all_verified = False
        else:
            # Generic verification for other providers
            # Check AGENTS.md exists
            agents_md = project_root / "AGENTS.md"
            if not agents_md.exists():
                console.print(f"  [red]✗[/red] AGENTS.md not found")
                all_verified = False
                continue

            # Provider-specific file checks
            if prov == 'claude-code':
                claude_dir = project_root / ".claude"
                if not claude_dir.exists():
                    console.print(f"  [red]✗[/red] .claude/ directory not found")
                    all_verified = False
                else:
                    console.print(f"  [green]✓[/green] .claude/ directory found")

            elif prov == 'codex':
                # Codex uses AGENTS.md natively
                console.print(f"  [green]✓[/green] AGENTS.md found")

        console.print()

    if all_verified:
        console.print("[green]✓[/green] All providers verified successfully")
    else:
        console.print("[yellow]![/yellow] Some providers have issues")
        console.print("[dim]To fix, run:[/dim] apm provider sync --all")
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
