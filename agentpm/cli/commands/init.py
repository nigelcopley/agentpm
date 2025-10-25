"""
apm init - Initialize APM project with database, rules, and agents in one command.

Performance Target: <3 minutes with progress feedback
"""

import click
import shutil
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich.table import Table

from agentpm.core.models.init_models import InitConfig, InitMode, InitProgress
from agentpm.core.services.init_orchestrator import InitOrchestrator
from agentpm.cli.utils.validation import validate_project_path


@click.command()
@click.argument('project_name')
@click.argument(
    'path',
    type=click.Path(exists=False),
    default='.',
    callback=validate_project_path
)
@click.option(
    '--description',
    '-d',
    help='Project description',
    default=''
)
@click.option(
    '--reset',
    is_flag=True,
    help='Delete existing installation and reinitialize'
)
@click.option(
    '--skip-questionnaire',
    is_flag=True,
    help='Skip rules questionnaire and use default preset'
)
@click.pass_context
def init(
    ctx: click.Context,
    project_name: str,
    path: Path,
    description: str,
    reset: bool,
    skip_questionnaire: bool
):
    """
    Initialize APM project (database + agents + rules).

    \b
    Creates:
      • .agentpm/data/agentpm.db      - SQLite database with complete schema
      • .agentpm/contexts/            - Plugin-generated context files
      • .agentpm/logs/                - Log files
      • .agentpm/cache/               - Temporary cache files
      • .claude/agents/               - Agent definition directory

    \b
    Examples:
      apm init "My Project"           # Default mode with questionnaire
      apm init "My Project" --reset   # Reinitialize existing project
      apm init "My Project" --skip-questionnaire  # Auto mode (no questions)

    \b
    Performance:
      • Target: <3 minutes with progress feedback
      • Includes: Database + detection + rules + verification
    """
    console = ctx.obj['console']

    # Handle reset
    if reset:
        if not click.confirm(
            'This will delete .agentpm/ and .claude/agents/. Continue?'
        ):
            console.print("[yellow]Cancelled[/yellow]")
            return

        cleanup_existing_installation(path, console)
        console.print("✓ Existing installation removed\n")

    # Check if already initialized
    if (path / ".agentpm").exists() and not reset:
        console.print(
            "\n❌ [red]Project already initialized.[/red]\n"
            "   Use [green]'apm init --reset'[/green] to reinitialize."
        )
        raise click.Abort()

    console.print(f"\n🚀 [cyan]Initializing APM project:[/cyan] {project_name}")
    console.print(f"📁 [dim]Location:[/dim] {path.absolute()}\n")

    # Create InitConfig
    config = InitConfig(
        project_name=project_name,
        project_path=path,
        project_description=description,
        mode=InitMode.AUTO if skip_questionnaire else InitMode.WIZARD,
        skip_rules=skip_questionnaire,
        force_reset=reset
    )

    # Create orchestrator
    orchestrator = InitOrchestrator(
        config=config,
        console=console
    )

    # Run initialization with progress tracking
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            task = progress.add_task(
                "Initializing...",
                total=6
            )

            def update_progress(init_progress: InitProgress):
                """Update progress bar"""
                progress.update(
                    task,
                    completed=init_progress.current_step,
                    description=f"[cyan][{init_progress.current_step}/{init_progress.total_steps}] {init_progress.message}[/cyan]"
                )

            orchestrator.progress_callback = update_progress

            # Run orchestration
            result = orchestrator.orchestrate()

        # Display result
        if result.success:
            # Show success message
            console.print("\n✅ [green]Project initialized successfully![/green]\n")

            # Show summary table
            summary_table = Table(title="📦 Project Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")

            summary_table.add_row("Project Name", result.project_name)
            summary_table.add_row("Project ID", str(result.project_id) if result.project_id else "N/A")
            summary_table.add_row("Database", str(result.database_path))
            summary_table.add_row("Rules Loaded", str(result.rules_loaded))
            summary_table.add_row("Duration", f"{result.duration_ms/1000:.1f}s")

            if result.technologies_detected:
                tech_list = ", ".join(result.technologies_detected)
                summary_table.add_row("Technologies", tech_list)
            else:
                summary_table.add_row("Technologies", "None (generic project)")

            console.print(summary_table)
            console.print()

            # Show warnings if any
            if result.has_warnings():
                console.print("⚠️  [yellow]Warnings:[/yellow]")
                for warning in result.warnings or []:
                    console.print(f"  • {warning}")
                console.print()

            # Show next steps
            console.print("🚀 [cyan]Next steps:[/cyan]")
            console.print("  1. Generate agent files: [green]apm agents generate --all[/green]")
            console.print("  2. View project status: [green]apm status[/green]")
            console.print("  3. Create work item: [green]apm work-item create \"My Feature\"[/green]")
            console.print("  4. Get help: [green]apm --help[/green]")
            console.print()

        else:
            # Show error message
            console.print("\n❌ [red]Initialization failed[/red]\n")

            if result.has_errors():
                console.print("[red]Errors:[/red]")
                for error in result.errors or []:
                    console.print(f"  • {error}")
                console.print()

            if result.has_warnings():
                console.print("[yellow]Warnings:[/yellow]")
                for warning in result.warnings or []:
                    console.print(f"  • {warning}")
                console.print()

            console.print("💡 [cyan]For help:[/cyan]")
            console.print("  • Check logs: [dim].agentpm/logs/agentpm.log[/dim]")
            console.print("  • Run diagnostic: [green]apm repair[/green]")
            console.print("  • Get help: [green]apm --help[/green]")
            console.print()

            raise click.Abort()

    except KeyboardInterrupt:
        console.print("\n⚠️  [yellow]Initialization cancelled[/yellow]")
        orchestrator.rollback()
        console.print("✓ Rollback complete\n")
        raise click.Abort()

    except Exception as e:
        console.print(f"\n❌ [red]Initialization failed: {e}[/red]")
        raise


def cleanup_existing_installation(project_path: Path, console: Console):
    """Remove existing .agentpm and .claude directories"""
    dirs_to_remove = [
        project_path / ".agentpm",
        project_path / ".claude"
    ]

    for directory in dirs_to_remove:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                console.print(f"[dim]Removed: {directory}[/dim]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not remove {directory}: {e}[/yellow]")
