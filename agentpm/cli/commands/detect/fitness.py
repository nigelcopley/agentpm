"""
Architecture fitness testing CLI command.

Validates project against architecture policies for CI/CD gate enforcement.
"""

import click
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Optional

from agentpm.core.detection.fitness.engine import FitnessEngine
from agentpm.core.database.enums.detection import PolicyLevel
from agentpm.core.detection.fitness.presets import list_presets_summary


@click.command(name='fitness')
@click.argument(
    'project_path',
    type=click.Path(exists=True, path_type=Path),
    default='.',
    required=False
)
@click.option(
    '--preset',
    type=click.Choice(['strict', 'balanced', 'lenient', 'startup', 'security_focused'], case_sensitive=False),
    help='Use predefined policy preset (strict, balanced, lenient, startup, security_focused)'
)
@click.option(
    '--list-presets',
    is_flag=True,
    help='List available presets and exit'
)
@click.option(
    '--fail-on-error',
    is_flag=True,
    help='Exit with error code if violations found'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json', 'yaml'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.option(
    '--errors-only',
    is_flag=True,
    help='Show ERROR level violations only'
)
@click.option(
    '--warnings-only',
    is_flag=True,
    help='Show WARNING level violations only'
)
@click.option(
    '--show-suggestions',
    is_flag=True,
    help='Include fix suggestions for violations'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    help='Save output to file'
)
@click.pass_context
def fitness(
    ctx,
    project_path: Path,
    preset: Optional[str],
    list_presets: bool,
    fail_on_error: bool,
    format: str,
    errors_only: bool,
    warnings_only: bool,
    show_suggestions: bool,
    output: Optional[Path]
):
    """
    Run architecture fitness tests.

    Validates project against architecture policies:
    - No circular dependencies
    - Maximum complexity limits
    - Layering rules
    - Code standards

    Exit codes:
        0 - All tests passed
        1 - Violations found (with --fail-on-error)

    \b
    Examples:
      apm detect fitness                       # Run all tests
      apm detect fitness --preset strict       # Use strict preset
      apm detect fitness --preset balanced     # Use balanced preset
      apm detect fitness --list-presets        # Show available presets
      apm detect fitness /path/to/project      # Test specific project
      apm detect fitness --fail-on-error       # CI/CD mode
      apm detect fitness --errors-only         # Critical violations
      apm detect fitness --show-suggestions    # Include fix hints
      apm detect fitness --format json         # JSON output
    """
    console: Console = ctx.obj['console']

    # Handle --list-presets flag
    if list_presets:
        console.print("\n" + list_presets_summary())
        ctx.exit(0)

    # Resolve project path
    project_path = project_path.resolve()

    try:
        # Initialize engine
        console.print(f"\n[cyan]🏋️  Running fitness tests on:[/cyan] {project_path}\n")
        engine = FitnessEngine(project_path)

        # Load policies (from preset or default)
        if preset:
            preset_lower = preset.lower()
            console.print(f"[cyan]Using preset:[/cyan] {preset_lower}\n")
            policies = engine.load_preset(preset_lower)
        else:
            policies = engine.load_default_policies()

        console.print(f"[dim]Loaded {len(policies)} policies[/dim]\n")

        # Run tests
        result = engine.run_tests(policies)

        # Format output
        if format == 'json':
            output_data = _format_json(result)
            if output:
                output.write_text(json.dumps(output_data, indent=2))
                console.print(f"[green]✓[/green] Saved to {output}")
            else:
                console.print(json.dumps(output_data, indent=2))

        elif format == 'yaml':
            import yaml
            output_data = _format_json(result)
            if output:
                output.write_text(yaml.dump(output_data, default_flow_style=False))
                console.print(f"[green]✓[/green] Saved to {output}")
            else:
                console.print(yaml.dump(output_data, default_flow_style=False))

        else:  # table format
            _display_table(
                console,
                result,
                errors_only=errors_only,
                warnings_only=warnings_only,
                show_suggestions=show_suggestions
            )

            if output:
                # Save as markdown
                _save_markdown(output, result, show_suggestions)
                console.print(f"\n[green]✓[/green] Saved to {output}")

        # Exit with error code if requested and violations found
        if fail_on_error and not result.is_passing():
            ctx.exit(1)

    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}")
        console.print_exception()
        ctx.exit(1)


def _display_table(
    console: Console,
    result,
    errors_only: bool = False,
    warnings_only: bool = False,
    show_suggestions: bool = False
) -> None:
    """Display fitness results as rich table."""

    # Summary header
    summary_text = result.get_summary()

    if result.is_passing():
        console.print(Panel(
            f"[bold green]{summary_text}[/bold green]",
            title="Fitness Test Results",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red]{summary_text}[/bold red]",
            title="Fitness Test Results",
            border_style="red"
        ))

    console.print()

    # Filter violations
    violations = result.violations
    if errors_only:
        violations = result.get_violations_by_level(PolicyLevel.ERROR)
    elif warnings_only:
        violations = result.get_violations_by_level(PolicyLevel.WARNING)

    if not violations:
        console.print("[green]✓ No violations found[/green]\n")
        return

    # Violations table
    table = Table(title="Violations", show_header=True, header_style="bold cyan")
    table.add_column("Level", style="bold", width=8)
    table.add_column("Policy", style="cyan", width=25)
    table.add_column("Violation", style="white")
    table.add_column("Location", style="dim", width=30)

    for violation in violations:
        # Level styling
        if violation.level == PolicyLevel.ERROR:
            level_str = "[red]ERROR[/red]"
        elif violation.level == PolicyLevel.WARNING:
            level_str = "[yellow]WARNING[/yellow]"
        else:
            level_str = "[blue]INFO[/blue]"

        # Truncate long messages
        message = violation.message
        if len(message) > 60:
            message = message[:57] + "..."

        # Truncate long locations
        location = violation.location
        if len(location) > 30:
            location = "..." + location[-27:]

        table.add_row(
            level_str,
            violation.policy_id,
            message,
            location
        )

    console.print(table)
    console.print()

    # Show suggestions if requested
    if show_suggestions:
        console.print("[bold cyan]Suggestions:[/bold cyan]\n")
        shown_suggestions = set()
        for violation in violations:
            if violation.suggestion and violation.suggestion not in shown_suggestions:
                console.print(f"• {violation.suggestion}")
                shown_suggestions.add(violation.suggestion)
        console.print()

    # Summary stats
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Passed: [green]{result.passed_count}[/green]")
    console.print(f"  Warnings: [yellow]{result.warning_count}[/yellow]")
    console.print(f"  Errors: [red]{result.error_count}[/red]")
    console.print(f"  Compliance: [cyan]{result.compliance_score:.0%}[/cyan]")
    console.print()

    # Final status
    if result.is_passing():
        console.print("[green]✓ PASSED[/green] - All critical checks passed\n")
    else:
        console.print(f"[red]✗ FAILED[/red] - {result.error_count} critical violation(s) found\n")


def _format_json(result) -> dict:
    """Format fitness result as JSON-serializable dict."""
    return {
        "passed_count": result.passed_count,
        "warning_count": result.warning_count,
        "error_count": result.error_count,
        "compliance_score": round(result.compliance_score, 2),
        "tested_at": result.tested_at.isoformat(),
        "is_passing": result.is_passing(),
        "violations": [
            {
                "policy_id": v.policy_id,
                "level": v.level.value,
                "message": v.message,
                "location": v.location,
                "suggestion": v.suggestion
            }
            for v in result.violations
        ]
    }


def _save_markdown(
    output_path: Path,
    result,
    show_suggestions: bool
) -> None:
    """Save fitness results as markdown file."""
    lines = []

    # Header
    lines.append("# Architecture Fitness Test Results")
    lines.append("")
    lines.append(f"**Tested:** {result.tested_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Status:** {'✓ PASSED' if result.is_passing() else '✗ FAILED'}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Passed:** {result.passed_count}")
    lines.append(f"- **Warnings:** {result.warning_count}")
    lines.append(f"- **Errors:** {result.error_count}")
    lines.append(f"- **Compliance Score:** {result.compliance_score:.0%}")
    lines.append("")

    # Violations
    if result.violations:
        lines.append("## Violations")
        lines.append("")
        lines.append("| Level | Policy | Violation | Location |")
        lines.append("|-------|--------|-----------|----------|")

        for violation in result.violations:
            level = violation.level.value.upper()
            policy = violation.policy_id
            message = violation.message.replace("|", "\\|")
            location = violation.location.replace("|", "\\|")

            lines.append(f"| {level} | {policy} | {message} | {location} |")

        lines.append("")

        # Suggestions
        if show_suggestions:
            lines.append("## Suggestions")
            lines.append("")
            shown_suggestions = set()
            for violation in result.violations:
                if violation.suggestion and violation.suggestion not in shown_suggestions:
                    lines.append(f"- {violation.suggestion}")
                    shown_suggestions.add(violation.suggestion)
            lines.append("")
    else:
        lines.append("## Violations")
        lines.append("")
        lines.append("No violations found.")
        lines.append("")

    # Write to file
    output_path.write_text("\n".join(lines))
