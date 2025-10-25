"""
apm rules list - List all project rules
"""

import click
from pathlib import Path
from rich.table import Table
from rich.console import Console
from agentpm.core.database import DatabaseService
from agentpm.core.database.enums import EnforcementLevel
from agentpm.core.database.adapters import RuleAdapter
from agentpm.core.database.methods import projects as project_methods
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id


@click.command()
@click.option(
    '--enforcement',
    '-e',
    type=click.Choice(EnforcementLevel.choices(), case_sensitive=False),
    help='Filter by enforcement level'
)
@click.option(
    '--category',
    '-c',
    help='Filter by category (e.g., development_principles, code_quality)'
)
@click.option(
    '--include-inactive',
    is_flag=True,
    help='Include inactive/disabled rules'
)
@click.pass_context
def list_rules(ctx: click.Context, enforcement: str | None, category: str | None, include_inactive: bool):
    """
    List all active rules for the current project.

    \b
    Examples:
      apm rules list                     # All rules
      apm rules list -e BLOCK           # Only blocking rules
      apm rules list -c code_quality    # Quality rules only
    """
    console = ctx.obj['console']

    # Find project database
    cwd = Path.cwd()
    aipm_dir = cwd / '.agentpm'

    if not aipm_dir.exists():
        console.print("[red]❌ Not an APM project (no .agentpm directory found)[/red]")
        console.print("[dim]Run 'apm init' to initialize this project[/dim]")
        raise click.Abort()

    db_path = aipm_dir / 'data' / 'agentpm.db'
    if not db_path.exists():
        console.print("[red]❌ Project database not found[/red]")
        raise click.Abort()

    # Connect to database
    db = DatabaseService(str(db_path))

    # Get project
    try:
        project_id = get_current_project_id(ctx)
        project = project_methods.get_project(db, project_id)
        if not project:
            console.print("[red]❌ Project not found in database[/red]")
            raise click.Abort()
    except Exception as e:
        console.print(f"[red]❌ Error loading project: {e}[/red]")
        raise click.Abort()

    # Get all rules for project
    try:
        all_rules = RuleAdapter.list(
            db,
            project_id=project.id,
            enabled_only=not include_inactive  # If include_inactive, show all; else only enabled
        )
    except Exception as e:
        console.print(f"[red]❌ Error loading rules: {e}[/red]")
        raise click.Abort()

    if not all_rules:
        console.print("\n[yellow]ℹ️  No rules configured for this project[/yellow]")
        console.print("[dim]Run 'apm rules configure' to set up rules[/dim]\n")
        return

    # Apply filters
    filtered_rules = all_rules
    if enforcement:
        filtered_rules = [r for r in filtered_rules if r.enforcement_level.upper() == enforcement.upper()]
    if category:
        filtered_rules = [r for r in filtered_rules if r.category == category]

    # Show filtered results
    if not filtered_rules:
        console.print(f"\n[yellow]ℹ️  No rules match the filters[/yellow]")
        if enforcement:
            console.print(f"[dim]Enforcement level: {enforcement}[/dim]")
        if category:
            console.print(f"[dim]Category: {category}[/dim]")
        console.print()
        return

    # Create table
    table = Table(title=f"📋 Project Rules ({len(filtered_rules)} of {len(all_rules)})")
    table.add_column("Rule ID", style="cyan", width=10)
    table.add_column("Category", style="dim", width=20)
    table.add_column("Enforcement", style="yellow", width=12)
    table.add_column("Description", style="white")

    # Add rows
    for rule in filtered_rules:
        # Color-code enforcement levels
        enforcement_style = {
            'BLOCK': '[red]BLOCK[/red]',
            'LIMIT': '[yellow]LIMIT[/yellow]',
            'GUIDE': '[cyan]GUIDE[/cyan]',
            'ENHANCE': '[green]ENHANCE[/green]'
        }.get(rule.enforcement_level, rule.enforcement_level)

        # Handle optional description field
        desc_text = rule.description or "No description"
        desc = desc_text[:80] + "..." if len(desc_text) > 80 else desc_text

        # Handle optional category field
        category_display = rule.category.replace('_', ' ').title() if rule.category else "Uncategorized"

        table.add_row(
            rule.rule_id,
            category_display,
            enforcement_style,
            desc
        )

    console.print(table)

    # Show summary by enforcement level
    enforcement_counts = {}
    for rule in all_rules:
        level = rule.enforcement_level
        enforcement_counts[level] = enforcement_counts.get(level, 0) + 1

    summary_parts = [f"{level}: {count}" for level, count in sorted(enforcement_counts.items())]
    summary_text = " | ".join(summary_parts)
    console.print(f"\n[dim]Summary: {summary_text}[/dim]\n")

    # Show next steps
    console.print("[dim]Commands:[/dim]")
    console.print("  apm rules show <rule-id>    # View rule details")
    console.print("  apm rules configure         # Re-configure rules\n")
