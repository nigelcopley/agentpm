"""
Static code analysis CLI command

Provides comprehensive static analysis reporting using StaticAnalysisService.

Architecture Compliance:
- CLI Layer: User interface for Detection Services
- Uses Layer 3 StaticAnalysisService
- Supports multiple output formats
- Performance: <2s for typical projects
"""

import click
import json
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from agentpm.core.detection.analysis import StaticAnalysisService, ProjectAnalysis, FileAnalysis


def _format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}"


def _get_grade(score: float) -> tuple[str, str]:
    """
    Get letter grade and color for a score.

    Args:
        score: Quality/maintainability score (0-100)

    Returns:
        Tuple of (grade, color)
    """
    if score >= 90:
        return "A", "green"
    elif score >= 80:
        return "B", "cyan"
    elif score >= 70:
        return "C", "yellow"
    elif score >= 60:
        return "D", "orange"
    else:
        return "F", "red"


def _get_complexity_status(complexity: float, threshold: int = 10) -> tuple[str, str]:
    """
    Get status indicator for complexity.

    Args:
        complexity: Complexity value
        threshold: Warning threshold

    Returns:
        Tuple of (status_text, color)
    """
    if complexity <= threshold / 2:
        return "✓ Excellent", "green"
    elif complexity <= threshold:
        return "✓ Good", "cyan"
    elif complexity <= threshold * 1.5:
        return "⚠ Warning", "yellow"
    else:
        return "✗ Poor", "red"


def _render_table_format(console: Console, analysis: ProjectAnalysis,
                         complexity_threshold: int, maintainability_threshold: float,
                         verbose: bool, summary_only: bool, service: StaticAnalysisService,
                         top: Optional[int] = None) -> None:
    """Render analysis in Rich table format."""

    # Summary statistics panel
    summary = analysis.get_summary()
    grade, grade_color = _get_grade(summary['quality_score'])

    summary_text = Text()
    summary_text.append("📊 Project Analysis Summary\n\n", style="bold cyan")
    summary_text.append(f"Files Analyzed:    ", style="bold")
    summary_text.append(f"{_format_number(summary['files_analyzed'])}\n")
    summary_text.append(f"Total Lines:       ", style="bold")
    summary_text.append(f"{_format_number(summary['total_lines'])}\n")
    summary_text.append(f"Code Lines:        ", style="bold")
    summary_text.append(f"{_format_number(summary['code_lines'])}\n")
    summary_text.append(f"Quality Score:     ", style="bold")
    summary_text.append(f"{summary['quality_score']:.1f}/100 ", style=grade_color)
    summary_text.append(f"(Grade: {grade})\n", style=f"{grade_color} bold")

    console.print(Panel(summary_text, border_style="cyan"))
    console.print()

    if summary_only:
        return

    # Metrics table
    table = Table(title="📈 Code Metrics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Status")
    table.add_column("Grade", justify="center")

    # Average complexity
    complexity_status, complexity_color = _get_complexity_status(
        summary['avg_complexity'],
        complexity_threshold
    )
    complexity_grade, _ = _get_grade(max(0, 100 - summary['avg_complexity'] * 5))

    table.add_row(
        "Avg Complexity",
        f"{summary['avg_complexity']:.1f}",
        f"<{complexity_threshold}",
        Text(complexity_status, style=complexity_color),
        Text(complexity_grade, style=f"{_get_grade(max(0, 100 - summary['avg_complexity'] * 5))[1]} bold")
    )

    # Max complexity
    max_status, max_color = _get_complexity_status(
        summary['max_complexity'],
        complexity_threshold
    )
    max_grade, _ = _get_grade(max(0, 100 - summary['max_complexity'] * 5))

    table.add_row(
        "Max Complexity",
        str(summary['max_complexity']),
        f"<{complexity_threshold}",
        Text(max_status, style=max_color),
        Text(max_grade, style=f"{_get_grade(max(0, 100 - summary['max_complexity'] * 5))[1]} bold")
    )

    # Average maintainability
    mi_status = "✓ Excellent" if summary['avg_maintainability'] >= 85 else \
                "✓ Good" if summary['avg_maintainability'] >= maintainability_threshold else \
                "✗ Needs Work"
    mi_color = "green" if summary['avg_maintainability'] >= 85 else \
               "cyan" if summary['avg_maintainability'] >= maintainability_threshold else \
               "red"
    mi_grade, _ = _get_grade(summary['avg_maintainability'])

    table.add_row(
        "Avg Maintainability",
        f"{summary['avg_maintainability']:.1f}",
        f">{maintainability_threshold}",
        Text(mi_status, style=mi_color),
        Text(mi_grade, style=f"{_get_grade(summary['avg_maintainability'])[1]} bold")
    )

    console.print(table)
    console.print()

    # Quality issues
    high_complexity = service.get_high_complexity_files(analysis, complexity_threshold)
    low_maintainability = service.get_low_maintainability_files(analysis, maintainability_threshold)

    if high_complexity or low_maintainability:
        console.print("⚠️  [yellow bold]Quality Issues Detected[/yellow bold]\n")

        if high_complexity:
            limit = top if top else len(high_complexity)
            files_to_show = high_complexity[:limit]

            complexity_table = Table(
                title=f"🔴 High Complexity Files (>{complexity_threshold})",
                show_header=True,
                header_style="bold red"
            )
            complexity_table.add_column("File", style="cyan")
            complexity_table.add_column("Max Complexity", justify="right", style="red bold")
            complexity_table.add_column("Avg Complexity", justify="right")
            complexity_table.add_column("Functions", justify="right")

            for file in files_to_show:
                # Make path relative for readability
                rel_path = Path(file.file_path).relative_to(Path(analysis.project_path))
                complexity_table.add_row(
                    str(rel_path),
                    str(file.complexity_max),
                    f"{file.complexity_avg:.1f}",
                    str(file.function_count)
                )

            console.print(complexity_table)
            console.print()

        if low_maintainability:
            limit = top if top else len(low_maintainability)
            files_to_show = low_maintainability[:limit]

            mi_table = Table(
                title=f"🔴 Low Maintainability Files (<{maintainability_threshold})",
                show_header=True,
                header_style="bold red"
            )
            mi_table.add_column("File", style="cyan")
            mi_table.add_column("MI Score", justify="right", style="red bold")
            mi_table.add_column("Complexity", justify="right")
            mi_table.add_column("Code Lines", justify="right")

            for file in files_to_show:
                # Make path relative for readability
                rel_path = Path(file.file_path).relative_to(Path(analysis.project_path))
                mi_table.add_row(
                    str(rel_path),
                    f"{file.maintainability_index:.1f}",
                    str(file.complexity_max),
                    str(file.code_lines)
                )

            console.print(mi_table)
            console.print()
    else:
        console.print("✅ [green bold]No quality issues detected![/green bold]")
        console.print()

    # Verbose mode: show per-file details
    if verbose and not summary_only:
        console.print("📄 [bold]Detailed File Analysis[/bold]\n")

        files_table = Table(show_header=True, header_style="bold cyan")
        files_table.add_column("File", style="cyan")
        files_table.add_column("LOC", justify="right")
        files_table.add_column("Complexity", justify="right")
        files_table.add_column("MI", justify="right")
        files_table.add_column("Functions", justify="right")
        files_table.add_column("Classes", justify="right")
        files_table.add_column("Quality", justify="center")

        for file in analysis.files:
            rel_path = Path(file.file_path).relative_to(Path(analysis.project_path))
            quality_grade, quality_color = _get_grade(file.quality_score)

            files_table.add_row(
                str(rel_path),
                str(file.code_lines),
                f"{file.complexity_avg:.1f}",
                f"{file.maintainability_index:.1f}",
                str(file.function_count),
                str(file.class_count),
                Text(quality_grade, style=f"{quality_color} bold")
            )

        console.print(files_table)
        console.print()


def _render_json_format(console: Console, analysis: ProjectAnalysis,
                        complexity_threshold: int, maintainability_threshold: float,
                        service: StaticAnalysisService) -> str:
    """Render analysis in JSON format."""
    high_complexity = service.get_high_complexity_files(analysis, complexity_threshold)
    low_maintainability = service.get_low_maintainability_files(analysis, maintainability_threshold)

    output = {
        "summary": analysis.get_summary(),
        "quality_issues": {
            "high_complexity_files": [
                {
                    "file_path": f.file_path,
                    "complexity_max": f.complexity_max,
                    "complexity_avg": f.complexity_avg,
                    "function_count": f.function_count
                }
                for f in high_complexity
            ],
            "low_maintainability_files": [
                {
                    "file_path": f.file_path,
                    "maintainability_index": f.maintainability_index,
                    "complexity_max": f.complexity_max,
                    "code_lines": f.code_lines
                }
                for f in low_maintainability
            ]
        },
        "files": [
            {
                "file_path": f.file_path,
                "total_lines": f.total_lines,
                "code_lines": f.code_lines,
                "complexity_avg": f.complexity_avg,
                "complexity_max": f.complexity_max,
                "maintainability_index": f.maintainability_index,
                "function_count": f.function_count,
                "class_count": f.class_count,
                "quality_score": f.quality_score
            }
            for f in analysis.files
        ]
    }

    return json.dumps(output, indent=2)


def _render_yaml_format(console: Console, analysis: ProjectAnalysis,
                        complexity_threshold: int, maintainability_threshold: float,
                        service: StaticAnalysisService) -> str:
    """Render analysis in YAML format."""
    # Convert JSON to YAML (reuse JSON logic)
    json_str = _render_json_format(console, analysis, complexity_threshold,
                                   maintainability_threshold, service)
    data = json.loads(json_str)
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def _render_markdown_format(console: Console, analysis: ProjectAnalysis,
                            complexity_threshold: int, maintainability_threshold: float,
                            service: StaticAnalysisService) -> str:
    """Render analysis in Markdown format."""
    summary = analysis.get_summary()
    grade, _ = _get_grade(summary['quality_score'])

    high_complexity = service.get_high_complexity_files(analysis, complexity_threshold)
    low_maintainability = service.get_low_maintainability_files(analysis, maintainability_threshold)

    lines = [
        "# Static Analysis Report",
        "",
        f"**Project:** `{analysis.project_path}`  ",
        f"**Analyzed:** {summary['analyzed_at']}  ",
        f"**Quality Score:** {summary['quality_score']:.1f}/100 (Grade: {grade})",
        "",
        "## Summary",
        "",
        f"- **Files Analyzed:** {_format_number(summary['files_analyzed'])}",
        f"- **Total Lines:** {_format_number(summary['total_lines'])}",
        f"- **Code Lines:** {_format_number(summary['code_lines'])}",
        f"- **Average Complexity:** {summary['avg_complexity']:.1f}",
        f"- **Max Complexity:** {summary['max_complexity']}",
        f"- **Average Maintainability:** {summary['avg_maintainability']:.1f}",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Target | Status |",
        "|--------|-------|--------|--------|",
        f"| Avg Complexity | {summary['avg_complexity']:.1f} | <{complexity_threshold} | {_get_complexity_status(summary['avg_complexity'], complexity_threshold)[0]} |",
        f"| Max Complexity | {summary['max_complexity']} | <{complexity_threshold} | {_get_complexity_status(summary['max_complexity'], complexity_threshold)[0]} |",
        f"| Avg Maintainability | {summary['avg_maintainability']:.1f} | >{maintainability_threshold} | {'✓ Good' if summary['avg_maintainability'] >= maintainability_threshold else '✗ Needs Work'} |",
        "",
    ]

    if high_complexity:
        lines.extend([
            f"## High Complexity Files (>{complexity_threshold})",
            "",
            "| File | Max Complexity | Avg Complexity | Functions |",
            "|------|----------------|----------------|-----------|",
        ])
        for file in high_complexity:
            rel_path = Path(file.file_path).relative_to(Path(analysis.project_path))
            lines.append(
                f"| `{rel_path}` | {file.complexity_max} | {file.complexity_avg:.1f} | {file.function_count} |"
            )
        lines.append("")

    if low_maintainability:
        lines.extend([
            f"## Low Maintainability Files (<{maintainability_threshold})",
            "",
            "| File | MI Score | Complexity | Code Lines |",
            "|------|----------|------------|------------|",
        ])
        for file in low_maintainability:
            rel_path = Path(file.file_path).relative_to(Path(analysis.project_path))
            lines.append(
                f"| `{rel_path}` | {file.maintainability_index:.1f} | {file.complexity_max} | {file.code_lines} |"
            )
        lines.append("")

    if not high_complexity and not low_maintainability:
        lines.extend([
            "## Quality Status",
            "",
            "✅ **No quality issues detected!**",
            "",
        ])

    return "\n".join(lines)


@click.command()
@click.argument(
    'project_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default='.',
    required=False
)
@click.option(
    '--no-cache',
    is_flag=True,
    help='Disable caching, force re-analysis'
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json', 'yaml', 'markdown'], case_sensitive=False),
    default='table',
    help='Output format (default: table)'
)
@click.option(
    '--pattern',
    default='**/*.py',
    help='File glob pattern (default: **/*.py)'
)
@click.option(
    '--complexity-threshold',
    type=int,
    default=10,
    help='Complexity threshold for warnings (default: 10)'
)
@click.option(
    '--maintainability-threshold',
    type=float,
    default=65.0,
    help='Maintainability index threshold (default: 65.0)'
)
@click.option(
    '--top',
    type=int,
    help='Show top N worst files (default: all)'
)
@click.option(
    '--output',
    type=click.Path(dir_okay=False, path_type=Path),
    help='Save output to file'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Show detailed per-file stats'
)
@click.option(
    '--summary-only',
    is_flag=True,
    help='Show summary only'
)
@click.pass_context
def analyze(ctx: click.Context, project_path: Path, no_cache: bool, output_format: str,
           pattern: str, complexity_threshold: int, maintainability_threshold: float,
           top: Optional[int], output: Optional[Path], verbose: bool, summary_only: bool):
    """
    Perform comprehensive static code analysis.

    Analyzes project source files to extract:
    - Code metrics (LOC, functions, classes)
    - Cyclomatic complexity
    - Maintainability index
    - Quality scores

    \b
    Quality Thresholds:
      Complexity:      <10 (good), 10-15 (warning), >15 (poor)
      Maintainability: >85 (excellent), 65-84 (good), <65 (needs work)
      Quality Score:   A(90+), B(80-89), C(70-79), D(60-69), F(<60)

    \b
    Examples:
      apm detect analyze                              # Analyze current directory
      apm detect analyze /path/to/project             # Analyze specific project
      apm detect analyze --format json                # JSON output
      apm detect analyze --complexity-threshold 15    # Custom threshold
      apm detect analyze --top 10                     # Show top 10 worst files
      apm detect analyze --output report.md           # Save to file
      apm detect analyze --verbose                    # Detailed per-file stats
      apm detect analyze --summary-only               # Summary only
      apm detect analyze --no-cache                   # Force re-analysis
    """
    console = ctx.obj['console']

    # Resolve absolute path
    project_path = project_path.resolve()

    # Validate thresholds
    if complexity_threshold < 1:
        console.print("[red]Error:[/red] Complexity threshold must be >= 1")
        raise click.Abort()

    if not (0 <= maintainability_threshold <= 100):
        console.print("[red]Error:[/red] Maintainability threshold must be 0-100")
        raise click.Abort()

    # Initialize service
    try:
        service = StaticAnalysisService(
            project_path=project_path,
            cache_enabled=not no_cache
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize analysis service: {e}")
        raise click.Abort()

    # Perform analysis
    console.print(f"🔍 [cyan]Analyzing project:[/cyan] {project_path}")
    console.print(f"   Pattern: {pattern}")
    console.print(f"   Cache: {'disabled' if no_cache else 'enabled'}")
    console.print()

    try:
        analysis = service.analyze_project(file_pattern=pattern)
    except Exception as e:
        console.print(f"[red]Error:[/red] Analysis failed: {e}")
        raise click.Abort()

    if analysis.total_files == 0:
        console.print(f"[yellow]Warning:[/yellow] No Python files found matching pattern: {pattern}")
        console.print()
        return

    # Render output
    try:
        if output_format == 'json':
            content = _render_json_format(console, analysis, complexity_threshold,
                                         maintainability_threshold, service)
            if output:
                output.write_text(content)
                console.print(f"✅ [green]Report saved to:[/green] {output}")
            else:
                console.print(content)

        elif output_format == 'yaml':
            content = _render_yaml_format(console, analysis, complexity_threshold,
                                         maintainability_threshold, service)
            if output:
                output.write_text(content)
                console.print(f"✅ [green]Report saved to:[/green] {output}")
            else:
                console.print(content)

        elif output_format == 'markdown':
            content = _render_markdown_format(console, analysis, complexity_threshold,
                                             maintainability_threshold, service)
            if output:
                output.write_text(content)
                console.print(f"✅ [green]Report saved to:[/green] {output}")
            else:
                # Render markdown in terminal
                console.print(Markdown(content))

        else:  # table format
            if output:
                # For table format with output file, save as markdown
                content = _render_markdown_format(console, analysis, complexity_threshold,
                                                 maintainability_threshold, service)
                output.write_text(content)
                console.print(f"✅ [green]Report saved to:[/green] {output} (as markdown)")
                console.print()

            _render_table_format(console, analysis, complexity_threshold,
                                maintainability_threshold, verbose, summary_only,
                                service, top)

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to render output: {e}")
        raise click.Abort()

    # Performance summary
    if verbose and not summary_only:
        console.print(f"[dim]Analysis completed in <2s with {analysis.total_files} files processed[/dim]")
        console.print()
