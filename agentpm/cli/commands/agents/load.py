"""
Agent Load Command

Loads agent definitions from YAML files to database.

Usage:
    apm agents load                           # Load all from .claude/agents/
    apm agents load --file=orchestrators.yaml # Load specific file
    apm agents load --validate-only           # Check without loading
    apm agents load --force                   # Overwrite existing agents
"""

import click
from pathlib import Path
from typing import Optional

from ....core.agents.loader import AgentLoader, LoadResult
from ....cli.utils.services import get_database_service


@click.command('load')
@click.option(
    '--file',
    type=click.Path(exists=True, path_type=Path),
    help='Load from specific YAML file'
)
@click.option(
    '--directory',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default='.claude/agents',
    help='Load all YAML files from directory (default: .claude/agents)'
)
@click.option(
    '--validate-only',
    is_flag=True,
    help='Validate YAML without loading to database'
)
@click.option(
    '--force',
    is_flag=True,
    help='Overwrite existing agents with same role'
)
@click.option(
    '--pattern',
    default='*.yaml',
    help='File pattern for directory loading (default: *.yaml)'
)
@click.pass_context
def load_agents(
    ctx,
    file: Optional[Path],
    directory: Path,
    validate_only: bool,
    force: bool,
    pattern: str
):
    """
    Load agent definitions from YAML files.

    Loads agent definitions into the database from YAML files.
    Validates schema, checks dependencies, and detects conflicts.

    Examples:

        # Load all agents from .claude/agents/
        apm agents load

        # Load specific file
        apm agents load --file=my-agent.yaml

        # Validate without loading
        apm agents load --validate-only

        # Force overwrite existing agents
        apm agents load --force

        # Load from custom directory
        apm agents load --directory=./config/agents

    YAML Format:

        Single agent:
            role: intent-triage
            display_name: Intent Triage Agent
            description: Classifies requests by type, domain, complexity
            tier: 1
            category: sub-agent
            sop_content: |
              You are the Intent Triage agent...
            capabilities:
              - request_classification
              - domain_mapping
            tools:
              - Read
              - Grep
            dependencies:
              - context-assembler
            triggers:
              - raw_request_received
            examples:
              - "Classify 'Add OAuth2 login' request"

        Multiple agents:
            agents:
              - role: intent-triage
                display_name: Intent Triage
                ...
              - role: context-assembler
                display_name: Context Assembler
                ...
    """
    from ....cli.utils.project import get_current_project_root
    project_root = get_current_project_root()
    db = get_database_service(project_root)

    # Get project_id
    project = db.get_current_project()
    if not project:
        click.echo("Error: No active project. Run 'apm init' first.", err=True)
        ctx.exit(1)

    # Initialize loader
    loader = AgentLoader(db, project_id=project.id)

    # Load agents
    try:
        if file:
            # Load single file
            click.echo(f"Loading agents from: {file}")
            result = loader.load_from_yaml(
                file,
                project_id=project.id,
                dry_run=validate_only,
                force=force
            )
        else:
            # Load directory
            if not directory.exists():
                click.echo(f"Error: Directory not found: {directory}", err=True)
                ctx.exit(1)

            click.echo(f"Loading agents from: {directory}")
            click.echo(f"  Pattern: {pattern}")
            result = loader.load_all(
                directory,
                project_id=project.id,
                dry_run=validate_only,
                force=force,
                pattern=pattern
            )

        # Display results
        _display_results(result, validate_only)

        # Exit with appropriate code
        if not result.success:
            ctx.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


def _display_results(result: LoadResult, validate_only: bool):
    """Display load results to user"""

    if validate_only:
        click.echo("\n=== VALIDATION RESULTS ===")
    else:
        click.echo("\n=== LOAD RESULTS ===")

    # Statistics
    if result.success:
        click.echo(click.style("✓ SUCCESS", fg='green', bold=True))
    else:
        click.echo(click.style("✗ FAILURE", fg='red', bold=True))

    click.echo(f"\nStatistics:")
    click.echo(f"  Loaded:  {result.loaded_count}")
    click.echo(f"  Skipped: {result.skipped_count}")
    click.echo(f"  Errors:  {result.error_count}")

    # Warnings
    if result.warnings:
        click.echo(f"\n{click.style('Warnings:', fg='yellow', bold=True)}")
        for warning in result.warnings:
            click.echo(f"  • {warning}")

    # Errors
    if result.errors:
        click.echo(f"\n{click.style('Errors:', fg='red', bold=True)}")
        for error in result.errors:
            # Multi-line errors need indentation
            lines = error.split('\n')
            click.echo(f"  • {lines[0]}")
            for line in lines[1:]:
                click.echo(f"    {line}")

    # Conflicts
    if result.conflicts:
        click.echo(f"\n{click.style('Conflicts:', fg='red', bold=True)}")
        for role, reasons in result.conflicts.items():
            click.echo(f"  {role}:")
            for reason in reasons:
                click.echo(f"    • {reason}")
        if not validate_only:
            click.echo("\nTip: Use --force to overwrite existing agents")

    # Dependency graph (validation mode only)
    if validate_only and result.dependency_graph:
        click.echo(f"\nDependency Graph:")
        for role, deps in result.dependency_graph.items():
            if deps:
                click.echo(f"  {role} → {', '.join(deps)}")

    # Loaded agents (validation mode only)
    if validate_only and result.agents:
        click.echo(f"\nAgents to be loaded:")
        for agent in result.agents:
            tier_label = {1: "Sub-Agent", 2: "Specialist", 3: "Orchestrator"}.get(
                agent.tier.value if agent.tier else 0,
                "Unknown"
            )
            click.echo(f"  • {agent.role} ({tier_label})")
            click.echo(f"    {agent.display_name}")
            if agent.capabilities:
                click.echo(f"    Capabilities: {', '.join(agent.capabilities[:3])}")
                if len(agent.capabilities) > 3:
                    click.echo(f"      ... and {len(agent.capabilities) - 3} more")

    # Success message
    if result.success:
        if validate_only:
            click.echo(f"\n{click.style('✓', fg='green')} Validation passed")
            click.echo(f"  Run without --validate-only to load {result.loaded_count} agents")
        else:
            click.echo(f"\n{click.style('✓', fg='green')} Successfully loaded {result.loaded_count} agents")
