"""
SBOM generation command

Generates Software Bill of Materials in various formats.

Layer: CLI Commands
Purpose: User-facing command for SBOM generation using SBOMService
User Journey: Step 7 - SBOM + License/Vulnerability checks
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentpm.core.detection.sbom import SBOMService, SBOM, SBOMComponent, LicenseType
from agentpm.cli.formatters.tables import build_generic_table


def _build_license_summary_table(license_summary: Dict[str, int], total: int) -> Table:
    """
    Build Rich table for license summary.

    Args:
        license_summary: Dict mapping license_type -> count
        total: Total number of components

    Returns:
        Rich Table with license distribution
    """
    table = Table(title="📜 License Summary", show_footer=True)
    table.add_column("License", style="cyan", no_wrap=True, footer="Total")
    table.add_column("Count", justify="right", style="bold", footer=str(total))
    table.add_column("Percentage", justify="right", style="yellow", footer="100%")

    # Sort by count (descending)
    sorted_licenses = sorted(license_summary.items(), key=lambda x: -x[1])

    for license_type, count in sorted_licenses:
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(
            license_type,
            str(count),
            f"{percentage:.1f}%"
        )

    return table


def _build_component_table(
    components: List[SBOMComponent],
    include_licenses: bool = True,
    limit: Optional[int] = None
) -> Table:
    """
    Build Rich table for SBOM components.

    Args:
        components: List of SBOM components
        include_licenses: Whether to show license column
        limit: Optional limit on number of rows to display

    Returns:
        Rich Table with component details
    """
    display_components = components[:limit] if limit else components
    title = f"📦 Components ({len(components)})"
    if limit and len(components) > limit:
        title += f" [dim](showing first {limit})[/dim]"

    table = Table(title=title)
    table.add_column("Component", style="bold", no_wrap=True)
    table.add_column("Version", style="cyan")
    if include_licenses:
        table.add_column("License", style="yellow")
    table.add_column("Type", style="magenta")

    for component in display_components:
        license_str = ""
        if include_licenses:
            if component.license:
                license_str = component.license.license_type.value
            else:
                license_str = "[dim]Unknown[/dim]"

        row = [
            component.name,
            component.version,
        ]
        if include_licenses:
            row.append(license_str)
        row.append(component.type)

        table.add_row(*row)

    return table


def _filter_by_license(
    components: List[SBOMComponent],
    license_filter: Optional[str] = None,
    exclude_license: Optional[str] = None
) -> List[SBOMComponent]:
    """
    Filter components by license type.

    Args:
        components: List of components to filter
        license_filter: License to include (e.g., "MIT")
        exclude_license: License to exclude (e.g., "GPL-3.0")

    Returns:
        Filtered list of components
    """
    filtered = components

    if license_filter:
        filtered = [
            c for c in filtered
            if c.license and c.license.license_type.value == license_filter
        ]

    if exclude_license:
        filtered = [
            c for c in filtered
            if not c.license or c.license.license_type.value != exclude_license
        ]

    return filtered


def _display_sbom_summary(console: Console, sbom: SBOM):
    """
    Display high-level SBOM summary.

    Args:
        console: Rich console instance
        sbom: SBOM to summarize
    """
    summary_text = f"""[bold]Project:[/bold] {sbom.project_name}
[bold]Version:[/bold] {sbom.project_version}
[bold]Generated:[/bold] {sbom.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
[bold]Total Components:[/bold] {sbom.total_components}"""

    # Count runtime vs dev dependencies
    runtime = [c for c in sbom.components if c.type == "library"]
    dev = [c for c in sbom.components if c.type == "development"]

    if dev:
        summary_text += f"""
[bold]Runtime Dependencies:[/bold] {len(runtime)}
[bold]Dev Dependencies:[/bold] {len(dev)}"""

    # Add runtime metadata if available
    if sbom.runtime_metadata:
        summary_text += f"""

[dim]Runtime Environment:[/dim]
[bold]Python:[/bold] {sbom.runtime_metadata.get('python_version', 'N/A')}"""

        venv = sbom.runtime_metadata.get('venv_path')
        if venv:
            summary_text += f"""
[bold]Virtual Env:[/bold] {venv}"""

        build_tools = sbom.runtime_metadata.get('build_tools', {})
        if build_tools:
            tools_str = ", ".join([f"{k} {v}" for k, v in build_tools.items()])
            summary_text += f"""
[bold]Build Tools:[/bold] {tools_str}"""

    panel = Panel(
        summary_text,
        title="🔍 SBOM Summary",
        border_style="green"
    )
    console.print(panel)


def _export_to_file(
    service: SBOMService,
    sbom: SBOM,
    output_path: Path,
    format_type: str,
    console: Console
) -> bool:
    """
    Export SBOM to file in specified format.

    Args:
        service: SBOMService instance
        sbom: SBOM to export
        output_path: Path to write output file
        format_type: Format type ('cyclonedx', 'cyclonedx-xml', 'spdx', 'json')
        console: Rich console for status messages

    Returns:
        True if export successful, False otherwise
    """
    try:
        if format_type == 'cyclonedx':
            content = service.export_cyclonedx(sbom, output_path, format="json")
            console.print(f"✓ CycloneDX JSON exported to: {output_path}")
        elif format_type == 'cyclonedx-xml':
            content = service.export_cyclonedx(sbom, output_path, format="xml")
            console.print(f"✓ CycloneDX XML exported to: {output_path}")
        elif format_type == 'spdx':
            content = service.export_spdx(sbom, output_path)
            console.print(f"✓ SPDX JSON exported to: {output_path}")
        elif format_type == 'json':
            # Simple JSON export
            sbom_dict = {
                "project_name": sbom.project_name,
                "project_version": sbom.project_version,
                "generated_at": sbom.generated_at.isoformat(),
                "total_components": sbom.total_components,
                "license_summary": sbom.license_summary,
                "components": [
                    {
                        "name": c.name,
                        "version": c.version,
                        "type": c.type,
                        "purl": c.purl,
                        "license": c.license.license_type.value if c.license else None,
                        "dependencies": c.dependencies,
                        "metadata": c.metadata
                    }
                    for c in sbom.components
                ]
            }

            # Include runtime metadata if present
            if sbom.runtime_metadata:
                sbom_dict["runtime_metadata"] = sbom.runtime_metadata

            content = json.dumps(sbom_dict, indent=2)
            output_path.write_text(content)
            console.print(f"✓ Simple JSON exported to: {output_path}")
        else:
            console.print(f"[red]✗ Unsupported format: {format_type}[/red]")
            return False

        # Show file size
        file_size = len(content)
        size_kb = file_size / 1024
        console.print(f"  Size: {size_kb:.1f} KB ({file_size:,} bytes)")
        return True

    except Exception as e:
        console.print(f"[red]✗ Export failed: {e}[/red]")
        return False


@click.command()
@click.argument(
    'project_path',
    type=click.Path(exists=True, path_type=Path),
    default='.',
    required=False
)
@click.option(
    '--format',
    type=click.Choice(['cyclonedx', 'cyclonedx-xml', 'spdx', 'json', 'table'], case_sensitive=False),
    default='table',
    help='SBOM format (default: table for display, use cyclonedx/spdx for files)'
)
@click.option(
    '--output',
    type=click.Path(path_type=Path),
    help='Output file path (default: display to console)'
)
@click.option(
    '--include-dev',
    is_flag=True,
    help='Include development dependencies'
)
@click.option(
    '--skip-licenses',
    is_flag=True,
    help='Skip license detection (faster)'
)
@click.option(
    '--licenses-only',
    is_flag=True,
    help='Show only license summary'
)
@click.option(
    '--license',
    type=str,
    help='Filter by license type (e.g., MIT, Apache-2.0)'
)
@click.option(
    '--exclude-license',
    type=str,
    help='Exclude specific license type (e.g., GPL-3.0)'
)
@click.option(
    '--runtime-only',
    is_flag=True,
    help='Exclude development dependencies (opposite of --include-dev)'
)
@click.option(
    '--limit',
    type=int,
    help='Limit number of components displayed in table view'
)
@click.option(
    '--runtime/--no-runtime',
    default=True,
    help='Include runtime environment overlay (default: enabled)'
)
@click.pass_context
def sbom(
    ctx,
    project_path: Path,
    format: str,
    output: Optional[Path],
    include_dev: bool,
    skip_licenses: bool,
    licenses_only: bool,
    license: Optional[str],
    exclude_license: Optional[str],
    runtime_only: bool,
    limit: Optional[int],
    runtime: bool
):
    """
    Generate Software Bill of Materials (SBOM).

    Creates SBOM in industry-standard formats:
    - CycloneDX 1.5 (JSON/XML)
    - SPDX 2.3 (JSON)

    Includes:
    - All project dependencies
    - License information
    - Package metadata
    - Dependency tree

    \b
    Examples:
      apm detect sbom                          # Display SBOM table
      apm detect sbom --format cyclonedx       # Generate CycloneDX SBOM
      apm detect sbom --format spdx            # Generate SPDX format
      apm detect sbom --output sbom.json       # Save to file
      apm detect sbom --licenses-only          # Show license summary only
      apm detect sbom --license MIT            # Filter MIT-licensed packages
      apm detect sbom --exclude-license GPL-3.0 # Exclude GPL packages
      apm detect sbom --include-dev            # Include dev dependencies
      apm detect sbom --runtime-only           # Runtime dependencies only
      apm detect sbom --no-runtime             # Disable runtime overlay (faster)

    \b
    Standard Formats:
      cyclonedx     - CycloneDX 1.5 JSON (industry standard)
      cyclonedx-xml - CycloneDX 1.5 XML
      spdx          - SPDX 2.3 JSON (Linux Foundation standard)
      json          - Simple JSON format
      table         - Rich table display (default for console)
    """
    console: Console = ctx.obj['console']

    try:
        # Handle conflicting options
        if runtime_only and include_dev:
            console.print("[yellow]⚠️  Warning: --runtime-only overrides --include-dev[/yellow]")
            include_dev = False

        # Initialize SBOM service
        service = SBOMService(project_path)

        # Generate SBOM
        with console.status("[bold green]Generating SBOM...", spinner="dots"):
            include_licenses_flag = not skip_licenses
            include_dev_flag = include_dev and not runtime_only

            sbom_data = service.generate_sbom(
                include_licenses=include_licenses_flag,
                include_dev_deps=include_dev_flag,
                include_runtime=runtime
            )

        if sbom_data.total_components == 0:
            console.print("\n[yellow]⚠️  No dependencies found in project[/yellow]")
            console.print("\n[dim]Make sure you have:")
            console.print("  - pyproject.toml, requirements.txt, or")
            console.print("  - package.json")
            console.print("  in your project directory.[/dim]\n")
            return

        # Apply license filters
        filtered_components = sbom_data.components
        if license or exclude_license:
            filtered_components = _filter_by_license(
                sbom_data.components,
                license_filter=license,
                exclude_license=exclude_license
            )

            if not filtered_components:
                console.print(f"\n[yellow]⚠️  No components found matching license filter[/yellow]\n")
                return

        # Export to file if output specified
        if output:
            # Determine format for export
            export_format = format if format != 'table' else 'cyclonedx'

            success = _export_to_file(
                service,
                sbom_data,
                output,
                export_format,
                console
            )

            if not success:
                ctx.exit(1)

        # Display to console
        if not output or format == 'table':
            console.print()  # Blank line

            # Show summary (unless licenses-only)
            if not licenses_only:
                _display_sbom_summary(console, sbom_data)
                console.print()  # Blank line

            # Show license summary
            if include_licenses_flag and sbom_data.license_summary:
                license_table = _build_license_summary_table(
                    sbom_data.license_summary,
                    sbom_data.total_components
                )
                console.print(license_table)
                console.print()  # Blank line

            # Show component table (unless licenses-only)
            if not licenses_only:
                component_table = _build_component_table(
                    filtered_components,
                    include_licenses=include_licenses_flag,
                    limit=limit
                )
                console.print(component_table)
                console.print()  # Blank line

            # Show filter info if applied
            if license or exclude_license:
                filter_msg = f"[dim]Filtered: {len(filtered_components)} of {sbom_data.total_components} components"
                if license:
                    filter_msg += f" (license={license})"
                if exclude_license:
                    filter_msg += f" (exclude={exclude_license})"
                filter_msg += "[/dim]"
                console.print(filter_msg)
                console.print()

        # Show helpful tips
        if not output and format == 'table':
            console.print("[dim]💡 Tip: Use --format=cyclonedx --output=sbom.json to export to file[/dim]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error generating SBOM: {e}[/red]\n")
        import traceback
        if ctx.obj.get('debug'):
            console.print(traceback.format_exc())
        ctx.exit(1)
