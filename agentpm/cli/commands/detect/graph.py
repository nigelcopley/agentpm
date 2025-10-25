"""
Dependency graph analysis CLI command.

Provides dependency graph building, cycle detection, and visualization
using DependencyGraphService.

Architecture Compliance:
- CLI Layer: User interface for Detection Services
- Uses Layer 3 DependencyGraphService
- Supports multiple output formats
- Performance: <1s for typical projects
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

from agentpm.core.detection.graphs import DependencyGraphService


def _get_severity_color(severity: str) -> str:
    """Get color for severity level."""
    return {
        "high": "red",
        "medium": "yellow",
        "low": "cyan"
    }.get(severity, "white")


def _get_instability_status(instability: float) -> tuple[str, str]:
    """
    Get status indicator for instability.

    Args:
        instability: Instability metric (0.0-1.0)

    Returns:
        Tuple of (status_text, color)
    """
    if instability <= 0.2:
        return "✓ Stable", "green"
    elif instability <= 0.5:
        return "✓ Balanced", "cyan"
    elif instability <= 0.8:
        return "⚠ Unstable", "yellow"
    else:
        return "✗ Very Unstable", "red"


def _render_summary_table(console: Console, analysis) -> None:
    """Render summary statistics table."""
    table = Table(title="📊 Dependency Graph Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Modules", str(analysis.total_modules))
    table.add_row("Dependencies", str(analysis.total_dependencies))
    table.add_row("Circular Deps", str(len(analysis.circular_dependencies)))
    table.add_row("Root Modules", str(len(analysis.root_modules)))
    table.add_row("Leaf Modules", str(len(analysis.leaf_modules)))
    table.add_row("Max Depth", str(analysis.max_depth))

    console.print(table)
    console.print()


def _render_cycles_table(console: Console, analysis) -> None:
    """Render circular dependencies table."""
    if not analysis.has_circular_dependencies:
        console.print("[green]✓ No circular dependencies detected![/green]\n")
        return

    console.print(f"[yellow]⚠ Found {len(analysis.circular_dependencies)} circular dependencies:[/yellow]\n")

    for idx, cycle in enumerate(analysis.circular_dependencies, 1):
        severity_color = _get_severity_color(cycle.severity)

        cycle_text = Text()
        cycle_text.append(f"{idx}. ", style="bold")
        cycle_text.append(f"[{cycle.severity.upper()}] ", style=f"{severity_color} bold")
        cycle_text.append(" → ".join(cycle.cycle))

        console.print(cycle_text)
        console.print(f"   [dim]Suggestion: {cycle.suggestion}[/dim]\n")


def _render_coupling_table(console: Console, analysis, show_all: bool = False) -> None:
    """Render coupling metrics table."""
    if not analysis.coupling_metrics:
        console.print("[yellow]No coupling metrics available[/yellow]\n")
        return

    table = Table(
        title="📈 Coupling Metrics",
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Module", style="bold", no_wrap=False)
    table.add_column("Ca", justify="right", style="cyan")
    table.add_column("Ce", justify="right", style="magenta")
    table.add_column("Instability", justify="right")
    table.add_column("Status")

    # Sort by instability (descending) to show most unstable first
    sorted_metrics = sorted(
        analysis.coupling_metrics,
        key=lambda m: m.instability,
        reverse=True
    )

    # Show top 20 or all if requested
    display_metrics = sorted_metrics if show_all else sorted_metrics[:20]

    for metrics in display_metrics:
        status_text, status_color = _get_instability_status(metrics.instability)

        table.add_row(
            metrics.module,
            str(metrics.afferent_coupling),
            str(metrics.efferent_coupling),
            f"{metrics.instability:.2f}",
            Text(status_text, style=status_color)
        )

    console.print(table)

    if not show_all and len(sorted_metrics) > 20:
        console.print(f"\n[dim]Showing top 20 of {len(sorted_metrics)} modules. Use --all to see all.[/dim]")

    console.print()


def _render_module_lists(console: Console, analysis, show_roots: bool, show_leaves: bool) -> None:
    """Render root and leaf module lists."""
    if show_roots and analysis.root_modules:
        console.print("[bold cyan]🌱 Root Modules[/bold cyan] (no incoming dependencies):")
        for module in analysis.root_modules[:10]:
            console.print(f"  • {module}")
        if len(analysis.root_modules) > 10:
            console.print(f"  [dim]... and {len(analysis.root_modules) - 10} more[/dim]")
        console.print()

    if show_leaves and analysis.leaf_modules:
        console.print("[bold cyan]🍃 Leaf Modules[/bold cyan] (no outgoing dependencies):")
        for module in analysis.leaf_modules[:10]:
            console.print(f"  • {module}")
        if len(analysis.leaf_modules) > 10:
            console.print(f"  [dim]... and {len(analysis.leaf_modules) - 10} more[/dim]")
        console.print()


def _render_module_detail(console: Console, service: DependencyGraphService, module_path: str) -> None:
    """Render detailed analysis for a specific module."""
    try:
        metrics = service.get_module_coupling(module_path)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    # Module header
    console.print(Panel(
        Text(f"📦 {module_path}", style="bold cyan"),
        border_style="cyan"
    ))

    # Coupling metrics
    status_text, status_color = _get_instability_status(metrics.instability)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Description")

    table.add_row(
        "Afferent Coupling (Ca)",
        str(metrics.afferent_coupling),
        "Modules that depend on this"
    )
    table.add_row(
        "Efferent Coupling (Ce)",
        str(metrics.efferent_coupling),
        "Modules this depends on"
    )
    table.add_row(
        "Instability (I)",
        f"{metrics.instability:.2f}",
        status_text
    )

    console.print(table)
    console.print()


def _export_json(analysis, output_path: Path) -> None:
    """Export analysis to JSON format."""
    data = {
        "project_path": analysis.project_path,
        "total_modules": analysis.total_modules,
        "total_dependencies": analysis.total_dependencies,
        "circular_dependencies": [
            {
                "cycle": cycle.cycle,
                "severity": cycle.severity,
                "suggestion": cycle.suggestion
            }
            for cycle in analysis.circular_dependencies
        ],
        "coupling_metrics": [
            {
                "module": m.module,
                "afferent_coupling": m.afferent_coupling,
                "efferent_coupling": m.efferent_coupling,
                "instability": m.instability
            }
            for m in analysis.coupling_metrics
        ],
        "root_modules": analysis.root_modules,
        "leaf_modules": analysis.leaf_modules,
        "max_depth": analysis.max_depth,
        "analyzed_at": analysis.analyzed_at.isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def _export_yaml(analysis, output_path: Path) -> None:
    """Export analysis to YAML format."""
    data = {
        "project_path": analysis.project_path,
        "total_modules": analysis.total_modules,
        "total_dependencies": analysis.total_dependencies,
        "circular_dependencies": [
            {
                "cycle": cycle.cycle,
                "severity": cycle.severity,
                "suggestion": cycle.suggestion
            }
            for cycle in analysis.circular_dependencies
        ],
        "coupling_metrics": [
            {
                "module": m.module,
                "afferent_coupling": m.afferent_coupling,
                "efferent_coupling": m.efferent_coupling,
                "instability": m.instability
            }
            for m in analysis.coupling_metrics
        ],
        "root_modules": analysis.root_modules,
        "leaf_modules": analysis.leaf_modules,
        "max_depth": analysis.max_depth,
        "analyzed_at": analysis.analyzed_at.isoformat()
    }

    with open(output_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


@click.command(name='graph')
@click.argument(
    'project_path',
    type=click.Path(exists=True, path_type=Path),
    default='.',
    required=False
)
@click.option(
    '--rebuild',
    is_flag=True,
    help='Force rebuild, ignore cache'
)
@click.option(
    '--detect-cycles',
    is_flag=True,
    help='Detect circular dependencies'
)
@click.option(
    '--cycles-only',
    is_flag=True,
    help='Show only cycles (skip other metrics)'
)
@click.option(
    '--visualize',
    is_flag=True,
    help='Generate Graphviz visualization'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    help='Output file path for visualization or export'
)
@click.option(
    '--highlight-cycles',
    is_flag=True,
    help='Highlight cycles in visualization (red edges)'
)
@click.option(
    '--module',
    type=str,
    help='Analyze specific module'
)
@click.option(
    '--coupling',
    is_flag=True,
    help='Show coupling metrics table'
)
@click.option(
    '--root-modules',
    is_flag=True,
    help='Show root modules (no incoming dependencies)'
)
@click.option(
    '--leaf-modules',
    is_flag=True,
    help='Show leaf modules (no outgoing dependencies)'
)
@click.option(
    '--all',
    'show_all',
    is_flag=True,
    help='Show all modules in coupling table (not just top 20)'
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json', 'yaml']),
    default='table',
    help='Output format (default: table)'
)
@click.pass_context
def graph(
    ctx,
    project_path: Path,
    rebuild: bool,
    detect_cycles: bool,
    cycles_only: bool,
    visualize: bool,
    output: Optional[Path],
    highlight_cycles: bool,
    module: Optional[str],
    coupling: bool,
    root_modules: bool,
    leaf_modules: bool,
    show_all: bool,
    output_format: str
):
    """
    Analyze project dependency graph.

    Builds dependency graphs showing:
    - Import relationships
    - Module dependencies
    - Circular dependencies (if any)
    - Coupling metrics

    \b
    Examples:
        apm detect graph                        # Build and show stats
        apm detect graph --detect-cycles        # Find circular deps
        apm detect graph --visualize            # Generate DOT file
        apm detect graph --module core/service.py  # Analyze specific module
        apm detect graph --coupling             # Show coupling metrics
        apm detect graph --format json          # JSON output
        apm detect graph --visualize --output deps.dot --highlight-cycles
    """
    console = ctx.obj['console']

    try:
        # Create service
        service = DependencyGraphService(project_path)

        # Handle module-specific analysis
        if module:
            _render_module_detail(console, service, module)
            return

        # Handle visualization
        if visualize:
            output_path = output or Path("dependency-graph.dot")
            console.print(f"[cyan]Generating Graphviz visualization...[/cyan]")

            dot_content = service.export_graphviz(
                output_path,
                highlight_cycles=highlight_cycles,
                include_metrics=coupling
            )

            console.print(f"[green]✓ Visualization saved to:[/green] {output_path}")
            console.print("\n[dim]Render with: dot -Tpng {} -o graph.png[/dim]".format(output_path))
            return

        # Run full analysis
        console.print("[cyan]Analyzing dependency graph...[/cyan]\n")
        analysis = service.analyze_dependencies(rebuild=rebuild)

        # Handle different output formats
        if output_format == 'json':
            output_path = output or Path("dependency-analysis.json")
            _export_json(analysis, output_path)
            console.print(f"[green]✓ Analysis exported to:[/green] {output_path}")
            return

        if output_format == 'yaml':
            output_path = output or Path("dependency-analysis.yaml")
            _export_yaml(analysis, output_path)
            console.print(f"[green]✓ Analysis exported to:[/green] {output_path}")
            return

        # Table format (default)
        if cycles_only:
            # Only show cycles
            _render_cycles_table(console, analysis)
        else:
            # Show summary
            _render_summary_table(console, analysis)

            # Show cycles if detected or requested
            if detect_cycles or analysis.has_circular_dependencies:
                _render_cycles_table(console, analysis)

            # Show coupling metrics if requested
            if coupling:
                _render_coupling_table(console, analysis, show_all=show_all)

            # Show root/leaf modules if requested
            if root_modules or leaf_modules:
                _render_module_lists(console, analysis, root_modules, leaf_modules)

        # Final recommendations
        if analysis.has_circular_dependencies and not cycles_only:
            console.print("[yellow]💡 Recommendation:[/yellow]")
            console.print("  Use --visualize --highlight-cycles to visualize circular dependencies")
            console.print("  Consider refactoring to break cycles and improve maintainability\n")

    except Exception as e:
        console.print(f"[red]Error analyzing dependencies:[/red] {e}")
        raise click.Abort()
