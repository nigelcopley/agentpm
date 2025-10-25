"""
apm agents validate - Validate agent against database rules
"""

import click
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import AgentAdapter

console = Console()


@click.command()
@click.argument('role')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation results')
@click.pass_context
def validate(ctx: click.Context, role: str, verbose: bool):
    """
    Validate agent against database rules.

    Checks agent for:
    - Existence and active status (CI-001)
    - SOP content completeness
    - File path validity
    - Staleness (>7 days)
    - Tier assignment
    - Rule compliance

    \b
    Examples:
      # Validate agent
      apm agents validate aipm-database-developer

      # Verbose validation
      apm agents validate aipm-database-developer --verbose
    """
    try:
        project_root = ensure_project_root(ctx)
        db = get_database_service(project_root)
        project_id = get_current_project_id(ctx)

        # Get agent
        agent = AgentAdapter.get_by_role(db, project_id, role)

        if not agent:
            console.print(f"[red]Agent '{role}' not found[/red]")
            console.print("\nRun 'apm agents list' to see available agents", style="dim")
            raise click.Abort()

        # Validation checks
        issues = []
        warnings = []
        passes = []

        # Check 1: Agent exists and active (CI-001)
        if not agent.is_active:
            issues.append("[red]Agent is not active (CI-001: Agent Validation)[/red]")
        else:
            passes.append("[green]Agent is active (CI-001)[/green]")

        # Check 2: SOP content exists
        if not agent.has_sop():
            issues.append("[red]No SOP content - agent cannot function correctly[/red]")
        else:
            sop_length = len(agent.sop_content) if agent.sop_content else 0
            if sop_length < 100:
                warnings.append(f"[yellow]SOP content very short ({sop_length} chars) - may be incomplete[/yellow]")
            else:
                passes.append(f"[green]SOP content exists ({sop_length} chars)[/green]")

        # Check 3: File path exists
        if agent.file_path:
            file_path = project_root / agent.file_path
            if not file_path.exists():
                issues.append(f"[red]File does not exist: {agent.file_path}[/red]")
            else:
                passes.append(f"[green]File exists: {agent.file_path}[/green]")
        else:
            warnings.append("[yellow]No file path recorded[/yellow]")

        # Check 4: Staleness
        if agent.is_stale():
            warnings.append("[yellow]Agent is stale (>7 days) - consider regeneration[/yellow]")
        else:
            passes.append("[green]Agent is fresh (<7 days)[/green]")

        # Check 5: Tier assignment
        if not agent.tier:
            warnings.append("[yellow]No tier assigned[/yellow]")
        else:
            tier_name = {1: "Sub-Agent", 2: "Specialist", 3: "Master Orchestrator"}.get(
                agent.tier.value, "Unknown"
            )
            passes.append(f"[green]Tier {agent.tier.value} ({tier_name})[/green]")

        # Check 6: Agent type
        if not agent.agent_type:
            warnings.append("[yellow]No agent type assigned[/yellow]")
        else:
            passes.append(f"[green]Agent type: {agent.agent_type}[/green]")

        # Check 7: Capabilities
        if not agent.capabilities:
            warnings.append("[yellow]No capabilities defined[/yellow]")
        else:
            passes.append(f"[green]{len(agent.capabilities)} capabilities defined[/green]")

        # Display results
        console.print()
        header = f"Validation Results: {agent.role}"
        console.print(Panel(header, style="bold cyan", expand=False))

        # Summary
        total_checks = len(issues) + len(warnings) + len(passes)
        status_color = "red" if issues else ("yellow" if warnings else "green")
        status_text = "FAILED" if issues else ("WARNING" if warnings else "PASSED")

        console.print(f"\n[{status_color} bold]Status: {status_text}[/{status_color} bold]")
        console.print(f"Total Checks: {total_checks}")
        console.print(f"  Passed: {len(passes)}")
        console.print(f"  Warnings: {len(warnings)}")
        console.print(f"  Failed: {len(issues)}")

        # Issues (blocking)
        if issues:
            console.print("\n[bold red]Critical Issues (Blocking)[/bold red]")
            for issue in issues:
                console.print(f"  {issue}")

        # Warnings (non-blocking)
        if warnings:
            console.print("\n[bold yellow]Warnings (Non-Blocking)[/bold yellow]")
            for warning in warnings:
                console.print(f"  {warning}")

        # Passes (verbose mode)
        if verbose and passes:
            console.print("\n[bold green]Passed Checks[/bold green]")
            for check in passes:
                console.print(f"  {check}")

        # Recommendations
        if issues or warnings:
            console.print("\n[bold cyan]Recommendations[/bold cyan]")
            if not agent.is_active:
                console.print("  - Activate agent or assign work to active agent")
            if not agent.has_sop():
                console.print(f"  - Regenerate agent: apm agents generate --role {role}")
            if agent.file_path and not (project_root / agent.file_path).exists():
                console.print(f"  - Regenerate agent file: apm agents generate --role {role}")
            if agent.is_stale():
                console.print(f"  - Refresh agent: apm agents generate --role {role}")
            if not agent.tier or not agent.agent_type:
                console.print("  - Update agent metadata in database")

        # Return code
        console.print()
        if issues:
            console.print("[red]Validation failed - critical issues found[/red]\n")
            raise click.Abort()
        elif warnings:
            console.print("[yellow]Validation passed with warnings[/yellow]\n")
        else:
            console.print("[green]Validation passed - agent is ready[/green]\n")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
