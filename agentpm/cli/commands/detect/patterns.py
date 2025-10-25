"""
Architecture pattern detection CLI command.

Detects common architecture patterns: Hexagonal, Layered, DDD, CQRS, MVC.
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from agentpm.core.detection.patterns.service import PatternRecognitionService
from agentpm.core.database.enums.detection import ArchitecturePattern


@click.command(name='patterns')
@click.argument(
    'project_path',
    type=click.Path(exists=True, path_type=Path),
    default='.',
    required=False
)
@click.option(
    '--confidence',
    type=float,
    default=0.5,
    help='Minimum confidence threshold (0.0-1.0)'
)
@click.option(
    '--format',
    type=click.Choice(['table', 'json', 'yaml'], case_sensitive=False),
    default='table',
    help='Output format'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    help='Save output to file'
)
@click.option(
    '--show-evidence',
    is_flag=True,
    help='Show supporting evidence for pattern detection'
)
@click.option(
    '--show-violations',
    is_flag=True,
    help='Show pattern violations found'
)
@click.pass_context
def patterns(
    ctx,
    project_path: Path,
    confidence: float,
    format: str,
    output: Optional[Path],
    show_evidence: bool,
    show_violations: bool
):
    """
    Detect architecture patterns.

    Recognizes common patterns:
    - Hexagonal (Ports & Adapters)
    - Layered (N-tier)
    - Domain-Driven Design
    - CQRS
    - MVC

    \b
    Examples:
      apm detect patterns                      # Detect all patterns
      apm detect patterns /path/to/project     # Analyze specific project
      apm detect patterns --confidence 0.7     # High confidence only
      apm detect patterns --show-evidence      # Show evidence
      apm detect patterns --show-violations    # Show violations
      apm detect patterns --format json        # JSON output
    """
    console: Console = ctx.obj['console']

    # Resolve project path
    project_path = project_path.resolve()

    try:
        # Initialize service
        console.print(f"\n[cyan]🔍 Analyzing architecture patterns in:[/cyan] {project_path}\n")
        service = PatternRecognitionService(project_path)

        # Run pattern analysis
        analysis = service.analyze_patterns(confidence_threshold=confidence)

        # Format output
        if format == 'json':
            output_data = _format_json(analysis)
            if output:
                output.write_text(json.dumps(output_data, indent=2))
                console.print(f"[green]✓[/green] Saved to {output}")
            else:
                console.print(json.dumps(output_data, indent=2))

        elif format == 'yaml':
            import yaml
            output_data = _format_json(analysis)
            if output:
                output.write_text(yaml.dump(output_data, default_flow_style=False))
                console.print(f"[green]✓[/green] Saved to {output}")
            else:
                console.print(yaml.dump(output_data, default_flow_style=False))

        else:  # table format
            _display_table(
                console,
                analysis,
                show_evidence=show_evidence,
                show_violations=show_violations
            )

            if output:
                # Save table as markdown
                _save_markdown(output, analysis, show_evidence, show_violations)
                console.print(f"\n[green]✓[/green] Saved to {output}")

    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}")
        console.print_exception()
        ctx.exit(1)


def _display_table(
    console: Console,
    analysis,
    show_evidence: bool = False,
    show_violations: bool = False
) -> None:
    """Display pattern analysis as rich table."""

    # Summary header
    if analysis.primary_pattern:
        console.print(Panel(
            f"[bold green]Primary Pattern:[/bold green] {analysis.primary_pattern.value.upper()}",
            title="Analysis Summary",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[yellow]No clear architecture pattern detected[/yellow]",
            title="Analysis Summary",
            border_style="yellow"
        ))

    console.print()

    # Pattern matches table
    table = Table(title="Detected Patterns", show_header=True, header_style="bold cyan")
    table.add_column("Pattern", style="bold")
    table.add_column("Confidence", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Violations", justify="center")

    # Sort by confidence (descending)
    sorted_matches = analysis.get_sorted_matches()

    for match in sorted_matches:
        # Confidence bar
        confidence_pct = int(match.confidence * 100)
        confidence_str = f"{confidence_pct}%"

        # Status icon
        if match.confidence >= 0.7:
            status = "✓ [green]High[/green]"
        elif match.confidence >= 0.5:
            status = "~ [yellow]Medium[/yellow]"
        else:
            status = "✗ [dim]Low[/dim]"

        # Violations count
        violation_count = len(match.violations)
        if violation_count > 0:
            violations = f"[red]{violation_count}[/red]"
        else:
            violations = "[green]0[/green]"

        table.add_row(
            match.pattern.value.replace('_', ' ').title(),
            confidence_str,
            status,
            violations
        )

    console.print(table)
    console.print()

    # Show evidence if requested
    if show_evidence:
        high_confidence = analysis.get_high_confidence_patterns()
        if high_confidence:
            console.print("[bold cyan]Evidence:[/bold cyan]\n")
            for match in high_confidence:
                console.print(f"[bold]{match.pattern.value.upper()}[/bold] ({match.confidence:.0%})")
                for evidence in match.evidence:
                    console.print(f"  • {evidence}")
                console.print()

    # Show violations if requested
    if show_violations:
        patterns_with_violations = analysis.get_patterns_with_violations()
        if patterns_with_violations:
            console.print("[bold red]Violations:[/bold red]\n")
            for match in patterns_with_violations:
                console.print(f"[bold]{match.pattern.value.upper()}[/bold]")
                for violation in match.violations:
                    console.print(f"  • [red]{violation}[/red]")
                console.print()
        elif show_violations:
            console.print("[green]No violations found[/green]\n")

    # Show recommendations
    high_confidence = analysis.get_high_confidence_patterns()
    if high_confidence:
        for match in high_confidence:
            if match.recommendations:
                console.print("[bold cyan]Recommendations:[/bold cyan]\n")
                for rec in match.recommendations:
                    console.print(f"  • {rec}")
                console.print()
                break  # Only show recommendations once


def _format_json(analysis) -> dict:
    """Format analysis as JSON-serializable dict."""
    return {
        "project_path": analysis.project_path,
        "primary_pattern": analysis.primary_pattern.value if analysis.primary_pattern else None,
        "confidence_threshold": analysis.confidence_threshold,
        "analyzed_at": analysis.analyzed_at.isoformat(),
        "matches": [
            {
                "pattern": match.pattern.value,
                "confidence": round(match.confidence, 2),
                "evidence": match.evidence,
                "violations": match.violations,
                "recommendations": match.recommendations
            }
            for match in analysis.matches
        ]
    }


def _save_markdown(
    output_path: Path,
    analysis,
    show_evidence: bool,
    show_violations: bool
) -> None:
    """Save analysis as markdown file."""
    lines = []

    # Header
    lines.append("# Architecture Pattern Analysis")
    lines.append("")
    lines.append(f"**Project:** {analysis.project_path}")
    lines.append(f"**Analyzed:** {analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Confidence Threshold:** {analysis.confidence_threshold:.0%}")
    lines.append("")

    # Primary pattern
    if analysis.primary_pattern:
        lines.append(f"**Primary Pattern:** {analysis.primary_pattern.value.replace('_', ' ').title()}")
    else:
        lines.append("**Primary Pattern:** None detected")
    lines.append("")

    # Pattern table
    lines.append("## Detected Patterns")
    lines.append("")
    lines.append("| Pattern | Confidence | Status | Violations |")
    lines.append("|---------|------------|--------|------------|")

    for match in analysis.get_sorted_matches():
        pattern_name = match.pattern.value.replace('_', ' ').title()
        confidence = f"{match.confidence:.0%}"

        if match.confidence >= 0.7:
            status = "✓ High"
        elif match.confidence >= 0.5:
            status = "~ Medium"
        else:
            status = "✗ Low"

        violations = str(len(match.violations))

        lines.append(f"| {pattern_name} | {confidence} | {status} | {violations} |")

    lines.append("")

    # Evidence
    if show_evidence:
        high_confidence = analysis.get_high_confidence_patterns()
        if high_confidence:
            lines.append("## Evidence")
            lines.append("")
            for match in high_confidence:
                lines.append(f"### {match.pattern.value.upper()} ({match.confidence:.0%})")
                lines.append("")
                for evidence in match.evidence:
                    lines.append(f"- {evidence}")
                lines.append("")

    # Violations
    if show_violations:
        patterns_with_violations = analysis.get_patterns_with_violations()
        if patterns_with_violations:
            lines.append("## Violations")
            lines.append("")
            for match in patterns_with_violations:
                lines.append(f"### {match.pattern.value.upper()}")
                lines.append("")
                for violation in match.violations:
                    lines.append(f"- {violation}")
                lines.append("")

    # Write to file
    output_path.write_text("\n".join(lines))
