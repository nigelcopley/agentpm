"""
apm init - Initialize APM project

Creates .agentpm directory structure, initializes database with schema,
runs plugin detection, and generates initial project context.

Performance Target: <5 seconds with progress feedback
"""

import click
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich.table import Table
from agentpm.core.database import DatabaseService
from agentpm.core.database.models import Project, Context, UnifiedSixW
from agentpm.core.database.enums import ProjectStatus, ContextType, EntityType
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import contexts as context_methods
from agentpm.cli.utils.validation import validate_project_path
from agentpm.core.plugins import PluginOrchestrator
from agentpm.core.detection.models import DetectionResult, TechnologyMatch
from agentpm.core.rules.questionnaire import QuestionnaireService
from agentpm.core.rules.generator import RuleGenerationService
from agentpm.core.services.agent_generator import AgentGeneratorService, AgentGenerationProgress
from typing import Any, Dict, List
import shutil


def _rollback_init(path: Path, console: Console, created_paths: List[Path]) -> None:
    """
    Rollback partial initialization by deleting created directories.
    Never raises exceptions - best effort cleanup.

    Args:
        path: Project root path
        console: Rich console for output
        created_paths: List of paths created during init (for tracking)
    """
    console.print("\n⚠️  [yellow]Rolling back initialization...[/yellow]")

    cleanup_errors = []

    # Delete tracked paths in reverse order
    for created_path in reversed(created_paths):
        try:
            if created_path.exists():
                if created_path.is_dir():
                    shutil.rmtree(created_path)
                    console.print(f"   [dim]Deleted: {created_path}[/dim]")
                else:
                    created_path.unlink()
                    console.print(f"   [dim]Deleted: {created_path}[/dim]")
        except Exception as e:
            error_msg = f"Failed to delete {created_path}: {e}"
            cleanup_errors.append(error_msg)

    # Always try to delete main directories even if not tracked
    main_dirs = [
        path / ".agentpm",
        path / ".claude"
    ]

    for directory in main_dirs:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                console.print(f"   [dim]Deleted: {directory}[/dim]")
            except Exception as e:
                error_msg = f"Failed to delete {directory}: {e}"
                cleanup_errors.append(error_msg)

    if cleanup_errors:
        console.print(f"\n⚠️  [yellow]Rollback completed with {len(cleanup_errors)} errors:[/yellow]")
        for error in cleanup_errors:
            console.print(f"   • {error}")
        console.print("\n💡 [dim]Manual cleanup may be required:[/dim]")
        console.print("   rm -rf .agentpm/")
        console.print("   rm -rf .claude/")
    else:
        console.print("\n✅ [green]Rollback complete - all artifacts removed[/green]")


def _create_rules_context(
    project_id: int,
    answers: Dict[str, Any],
    loaded_count: int
) -> Context:
    """Convert questionnaire answers to 6W context format.

    Args:
        project_id: Project database ID
        answers: Questionnaire answers dictionary
        loaded_count: Number of rules loaded

    Returns:
        Context object with 6W structure
    """
    six_w = UnifiedSixW()

    # WHO: Team composition
    six_w.who = [
        f"Team size: {answers.get('team_size', 'solo')}",
        f"Development stage: {answers.get('development_stage', 'prototype')}"
    ]

    # WHAT: Project characteristics
    six_w.what = [
        f"Project type: {answers.get('project_type', 'cli')}",
        f"Primary language: {answers.get('primary_language', 'python')}",
        f"Architecture: {answers.get('architecture_style', 'not specified')}"
    ]

    # WHERE: Technical environment
    tech_stack = []
    if answers.get('backend_framework'):
        tech_stack.append(f"Backend: {answers['backend_framework']}")
    if answers.get('frontend_framework'):
        tech_stack.append(f"Frontend: {answers['frontend_framework']}")
    if answers.get('database'):
        tech_stack.append(f"Database: {answers['database']}")
    six_w.where = tech_stack or ["No framework specified"]

    # WHEN: Development constraints
    six_w.when = [
        f"Expected task duration: {answers.get('time_boxing', 4)}h",
        f"Test coverage target: {answers.get('test_coverage', 90)}%"
    ]

    # WHY: Development philosophy
    six_w.why = [
        f"Development approach: {answers.get('development_approach', 'not specified')}",
        f"Code review required: {answers.get('code_review', True)}",
        f"Compliance needs: {answers.get('compliance_requirements', [])}"
    ]

    # HOW: Implementation standards
    six_w.how = [
        f"Rules preset selected: {answers.get('_selected_preset', 'standard')}",
        f"Rules loaded: {loaded_count}",
        f"Deployment: {answers.get('deployment_strategy', 'not specified')}"
    ]

    # Technical constraints from rules
    six_w.technical_constraints = [
        f"Test coverage >= {answers.get('test_coverage', 90)}%",
        f"Max task duration: {answers.get('time_boxing', 4)}h"
    ]

    return Context(
        project_id=project_id,
        context_type=ContextType.RULES_CONTEXT,
        entity_type=EntityType.PROJECT,
        entity_id=project_id,
        six_w=six_w,
        confidence_score=0.9,  # High confidence - user-provided
        confidence_factors={'source': 'questionnaire', 'answers': answers}
    )


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
    '--skip-questionnaire',
    is_flag=True,
    help='Skip rules questionnaire and use default preset'
)
@click.pass_context
def init(ctx: click.Context, project_name: str, path: Path, description: str, skip_questionnaire: bool):
    """
    Initialize APM project with database and plugin detection.

    \b
    Creates:
      • .agentpm/data/agentpm.db      - SQLite database with complete schema
      • .agentpm/contexts/          - Plugin-generated context files
      • .agentpm/cache/             - Temporary cache files

    \b
    Post-Init Setup:
      • Generate agent files: apm agents generate --all
      • Configure rules: apm rules configure
      • Create first work item: apm work-item create "Feature"

    \b
    Examples:
      # Initialize and generate agents
      apm init "My Project"
      apm agents generate --all

      # Initialize with description
      apm init "API Server" ./backend -d "E-commerce API"

      # Skip questionnaire
      apm init "Quick Project" --skip-questionnaire

    \b
    Performance:
      • Target: <5 seconds with progress feedback
      • Includes: Database creation + plugin detection + context generation
    """
    console = ctx.obj['console']

    # Check if already initialized
    aipm_dir = path / '.agentpm'
    if aipm_dir.exists():
        console.print(f"\n❌ [red]Project already initialized at {path}[/red]")
        console.print(f"\n💡 [yellow]To re-initialize, first remove .agentpm directory:[/yellow]")
        console.print(f"   rm -rf {aipm_dir}")
        raise click.Abort()

    console.print(f"\n🚀 [cyan]Initializing APM project:[/cyan] {project_name}")
    console.print(f"📁 [dim]Location:[/dim] {path.absolute()}\n")

    # Track created paths for rollback
    created_paths: List[Path] = []

    # Wrap initialization in try/except for automatic rollback on failure
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:

            # Task 1: Create directory structure
            task1 = progress.add_task("[cyan]Creating directory structure...", total=3)

            # Create .agentpm directory structure
            aipm_dir.mkdir()
            created_paths.append(aipm_dir)
            progress.update(task1, advance=1)

            data_dir = aipm_dir / 'data'
            data_dir.mkdir()
            progress.update(task1, advance=1)

            contexts_dir = aipm_dir / 'contexts'
            contexts_dir.mkdir()
            cache_dir = aipm_dir / 'cache'
            cache_dir.mkdir()
            progress.update(task1, advance=1, completed=3)

        # Task 2: Initialize database
        task2 = progress.add_task("[cyan]Initializing database schema...", total=2)

        db_path = data_dir / 'agentpm.db'
        db = DatabaseService(str(db_path))  # Schema initialized automatically
        progress.update(task2, advance=1)

        # Database schema is now initialized automatically by DatabaseService
        progress.update(task2, description="[cyan]Database schema up to date")

        progress.update(task2, advance=1, completed=2)

        # Task 3: Create project record
        task3 = progress.add_task("[cyan]Creating project record...", total=1)

        project = Project(
            name=project_name,
            description=description,
            path=str(path.absolute()),
            status=ProjectStatus.ACTIVE
        )
        created_project = project_methods.create_project(db, project)
        progress.update(task3, advance=1, completed=1)

        # Task 4: Run two-phase framework detection
        task4 = progress.add_task("[cyan]Detecting frameworks and tools...", total=3)

        from agentpm.core.detection import DetectionOrchestrator

        # Phase 1: Technology Detection (ADR-001)
        progress.update(task4, description="[cyan]Scanning project files...")
        try:
            detection_orchestrator = DetectionOrchestrator(min_confidence=0.6)
            detection_result = detection_orchestrator.detect_all(path)
            progress.update(task4, advance=1)
        except Exception as e:
            # Detection failure: create empty result (graceful degradation)
            console.print(f"[dim yellow]⚠️  Detection failed ({e}), continuing...[/dim yellow]")
            detection_result = DetectionResult(
                matches={},
                scan_time_ms=0.0,
                project_path=str(path.absolute())
            )
            progress.update(task4, advance=1)

        # Phase 2: Plugin Enrichment (generate amalgamation files)
        enrichment = None
        amalgamation_count = 0
        if detection_result.matches:
            progress.update(task4, description="[cyan]Generating code amalgamations...")
            try:
                plugin_orchestrator = PluginOrchestrator(min_confidence=0.5)
                enrichment = plugin_orchestrator.enrich_context(path, detection_result)

                # Count amalgamation files created
                if enrichment and enrichment.deltas:
                    for delta in enrichment.deltas:
                        if 'amalgamation_files' in delta.additions:
                            amalgamation_count += len(delta.additions['amalgamation_files'])

                progress.update(task4, advance=1)
            except Exception as e:
                # Plugin enrichment failure doesn't block init
                console.print(f"[dim yellow]⚠️  Plugin enrichment failed ({e})[/dim yellow]")
                progress.update(task4, advance=1)
        else:
            # No technologies detected, skip enrichment
            progress.update(task4, advance=1)

        # Phase 3: Store results in database
        progress.update(task4, description="[cyan]Storing detection results...")
        try:
            # Update project record with detection results
            detected_frameworks = [tech for tech in detection_result.matches.keys()]
            tech_stack = [
                f"{tech} (confidence: {match.confidence:.0%})"
                for tech, match in detection_result.matches.items()
            ]

            # Store in projects table using existing columns (use transaction for auto-commit)
            import json
            with db.transaction() as conn:
                conn.execute("""
                    UPDATE projects
                    SET detected_frameworks = ?,
                        tech_stack = ?
                    WHERE id = ?
                """, (
                    json.dumps(detected_frameworks),
                    json.dumps(tech_stack),
                    created_project.id
                ))

            progress.update(task4, advance=1, completed=3)
        except Exception as e:
            console.print(f"[dim yellow]⚠️  Failed to store detection results ({e})[/dim yellow]")
            progress.update(task4, advance=1, completed=3)

    # Task 5: Agent Generation (AUTOMATIC)
            # NOTE: Agents are stored in database (via migrations, e.g., migration_0029.py)
            # Now we automatically generate provider-specific agent files
            console.print("\n🤖 [cyan]Generating Agent Files...[/cyan]")

            # Create .claude directory for agent files
            claude_dir = path / ".claude"
            claude_agents_dir = claude_dir / "agents"
            claude_agents_dir.mkdir(parents=True, exist_ok=True)
            created_paths.append(claude_dir)

            try:
                # Initialize agent generator
                agent_generator = AgentGeneratorService(
                    db=db,
                    project_path=path,
                    project_id=created_project.id,
                    progress_callback=lambda prog: progress.update(
                        task5,
                        description=f"[cyan]Generating {prog.agent_role}... ({prog.current}/{prog.total})"
                    )
                )

                # Start agent generation task
                task5 = progress.add_task("[cyan]Generating agent files...", total=100)

                # Generate all agents
                agent_summary = agent_generator.generate_all()

                progress.update(task5, completed=100)

                console.print(f"\n✅ [green]Generated {agent_summary.total_generated} agent files[/green]")
                if agent_summary.total_failed > 0:
                    console.print(f"⚠️  [yellow]{agent_summary.total_failed} agents failed to generate[/yellow]")
                console.print(f"📁 [dim]Location:[/dim] {agent_summary.output_directory}\n")

            except Exception as e:
                console.print(f"\n⚠️  [yellow]Agent generation failed: {e}[/yellow]")
                console.print("   [dim]You can generate agents later with:[/dim]")
                console.print("   [green]apm agents generate --all[/green]\n")

    # Task 6: Store plugin facts in database (project context)
    if enrichment and enrichment.deltas:
        task6 = progress.add_task("[cyan]Storing project intelligence...", total=1)

        try:
            # Convert plugin facts to 6W format for storage
            plugin_facts = {
                'detected_technologies': {
                    tech: {
                        'confidence': match.confidence,
                        'plugin_id': next((d.plugin_id for d in enrichment.deltas if tech in d.plugin_id), None)
                    }
                    for tech, match in detection_result.matches.items()
                },
                'plugin_enrichment': {
                    delta.plugin_id: delta.additions
                    for delta in enrichment.deltas
                },
                'enrichment_metadata': {
                    'scan_time_ms': detection_result.scan_time_ms,
                    'total_plugins': enrichment.total_plugins,
                    'enriched_at': str(enrichment.enriched_at)
                }
            }

            # Create project context with plugin facts in technical_constraints
            six_w = UnifiedSixW()
            six_w.technical_constraints = [f"Plugin facts stored: {len(enrichment.deltas)} plugins"]
            six_w.existing_patterns = [f"{tech}: {match.confidence:.0%}" for tech, match in detection_result.matches.items()]

            project_context = Context(
                project_id=created_project.id,
                context_type=ContextType.PROJECT_CONTEXT,
                entity_type=EntityType.PROJECT,
                entity_id=created_project.id,
                six_w=six_w,
                confidence_score=sum(m.confidence for m in detection_result.matches.values()) / len(detection_result.matches) if detection_result.matches else 0.5,
                confidence_factors={'plugin_facts': plugin_facts}
            )

            context_methods.create_context(db, project_context)
            progress.update(task6, advance=1, completed=1)

        except Exception as e:
            # Context storage failure doesn't block init
            console.print(f"[dim yellow]⚠️  Context storage failed ({e})[/dim yellow]")
            progress.update(task6, advance=1, completed=1)

    # Task 7: Rules Configuration (optional)
    loaded_count = 0
    rules_answers = None

    if not skip_questionnaire:
        task7 = progress.add_task("[cyan]Configuring project rules...", total=3)

        try:
            # Step 1: Run questionnaire (WI-51: pass detection_result for smart defaults)
            questionnaire = QuestionnaireService(
                console=console,
                detection_result=detection_result  # WI-51: Smart questionnaire
            )
            progress.update(task7, description="[cyan]Running rules questionnaire...")
            rules_answers = questionnaire.run()
            progress.update(task7, advance=1)

            # Step 2: Generate and load rules
            progress.update(task7, description="[cyan]Loading rules into project...")
            generator = RuleGenerationService(db)
            loaded_rules = generator.generate(
                answers=rules_answers,
                project_id=created_project.id,
                overwrite=False
            )
            loaded_count = len(loaded_rules)
            progress.update(task7, advance=1)

            # Step 3: Store questionnaire answers as 6W context
            progress.update(task7, description="[cyan]Storing project configuration...")
            rules_context = _create_rules_context(
                project_id=created_project.id,
                answers=rules_answers,
                loaded_count=loaded_count
            )
            context_methods.create_context(db, rules_context)
            progress.update(task7, advance=1, completed=3)

        except Exception as e:
            # Non-blocking: questionnaire failure doesn't prevent init
            console.print(f"[dim yellow]⚠️  Rules configuration failed ({e})[/dim yellow]")
            console.print(f"[dim]You can configure rules later with: apm rules configure[/dim]")
            progress.update(task7, advance=3, completed=3)
    else:
        # Use default preset without questionnaire
        try:
            console.print("\n[dim]ℹ️  Skipping questionnaire, loading default rules...[/dim]")
            generator = RuleGenerationService(db)
            loaded_rules = generator.generate_with_preset(
                project_id=created_project.id,
                preset='standard',  # Default to standard preset
                overwrite=False
            )
            loaded_count = len(loaded_rules)
            console.print(f"[dim]✓ Loaded {loaded_count} default rules (standard preset)[/dim]\n")
        except Exception as e:
            console.print(f"[dim yellow]⚠️  Default rules failed ({e})[/dim yellow]")
            console.print(f"[dim]You can configure rules later with: apm rules configure[/dim]\n")

    # Task 8: Testing Configuration (optional)
    testing_config_installed = False
    try:
        from agentpm.core.testing import ensure_testing_config_installed
        
        # Install testing configuration
        testing_config_installed = ensure_testing_config_installed(str(path))
        
        if testing_config_installed:
            console.print("[dim]✓ Testing configuration installed[/dim]")
        else:
            console.print("[dim yellow]⚠️  Testing configuration installation failed[/dim yellow]")
            
    except Exception as e:
        console.print(f"[dim yellow]⚠️  Testing configuration failed ({e})[/dim yellow]")
        console.print("[dim]You can configure testing later[/dim]")

    # Show success message
    console.print("\n✅ [green]Project initialized successfully![/green]\n")

    # Show detection results if any technologies detected
    if detection_result.matches:
        table = Table(title="🔍 Detected Technologies")
        table.add_column("Technology", style="cyan")
        table.add_column("Confidence", justify="right", style="green")
        table.add_column("Plugin", style="dim")

        for tech, match in detection_result.matches.items():
            # Format confidence as percentage
            conf_pct = f"{match.confidence:.0%}"
            # Get plugin ID from enrichment deltas
            plugin_id = "N/A"
            if enrichment and enrichment.deltas:
                plugin_id = next(
                    (d.plugin_id for d in enrichment.deltas if tech in d.plugin_id),
                    "N/A"
                )
            table.add_row(tech.capitalize(), conf_pct, plugin_id)

        console.print(table)
        console.print(f"\n📊 [dim]Detected {len(detection_result.matches)} technologies in {detection_result.scan_time_ms:.0f}ms[/dim]")

        # Show amalgamation files count
        if amalgamation_count > 0:
            console.print(f"📁 [dim]Generated {amalgamation_count} code amalgamation files in .agentpm/contexts/[/dim]\n")
        else:
            console.print()
    else:
        console.print("📦 [cyan]Project setup complete[/cyan]")
        console.print("   ℹ️  No specific frameworks detected (generic project)\n")

    # Show rules summary if rules were loaded
    if loaded_count > 0:
        rules_table = Table(title="⚙️  Project Rules Configured")
        rules_table.add_column("Metric", style="cyan")
        rules_table.add_column("Value", justify="right", style="green")

        rules_table.add_row("Rules Loaded", str(loaded_count))

        if rules_answers:
            preset_name = rules_answers.get('_selected_preset', 'standard')
            coverage = rules_answers.get('test_coverage', 90)
            time_box = rules_answers.get('time_boxing', 4)

            rules_table.add_row("Preset", preset_name.replace('_', ' ').title())
            rules_table.add_row("Coverage Target", f"{coverage}%")
            rules_table.add_row("Max Task Duration", f"{time_box}h")
        else:
            rules_table.add_row("Preset", "Standard (default)")

        console.print(rules_table)
        console.print(f"\n📋 [dim]Manage rules: apm rules list | apm rules configure[/dim]\n")

    # Show next steps
    console.print("\n📚 [cyan]Next steps:[/cyan]")
    console.print("   apm agents generate --all           # Generate agent files")
    console.print("   apm status                          # View project dashboard")
    console.print("   apm work-item create \"My Feature\"  # Create work item")
    console.print("   apm task create \"My Task\"          # Create task\n")

    console.print(f"💾 [dim]Database:[/dim] {db_path}")
    console.print(f"📁 [dim]Project ID:[/dim] {created_project.id}\n")
