"""
apm agents show - Show detailed agent information
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from datetime import datetime
import json

from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.adapters import AgentAdapter

console = Console()


@click.command()
@click.argument('role')
@click.option('--sop', is_flag=True, help='Show full SOP content')
@click.pass_context
def show(ctx: click.Context, role: str, sop: bool):
    """
    Show detailed agent information.

    Displays agent metadata, tier, type, status, capabilities,
    generation info, and optionally the full SOP content.

    \b
    Examples:
      # Show agent details
      apm agents show aipm-database-developer

      # Show with full SOP content
      apm agents show aipm-database-developer --sop
    """
    try:
        project_root = ensure_project_root(ctx)
        db = get_database_service(project_root)
        project_id = get_current_project_id(ctx)

        # Get agent
        agent = AgentAdapter.get_by_role(db, project_id, role)

        if not agent:
            console.print(f"❌ Agent '{role}' not found", style="red")
            console.print("\n💡 Run 'apm agents list' to see available agents", style="dim")
            raise click.Abort()

        # Display header
        console.print()
        tier_name = {1: "Sub-Agent", 2: "Specialist", 3: "Master Orchestrator"}.get(
            agent.tier.value if agent.tier else 0, "Unknown"
        )
        header = f"[bold cyan]{agent.display_name}[/bold cyan] ({tier_name})"
        console.print(Panel(header, expand=False))

        # Core information
        console.print("\n[bold]Core Information[/bold]")
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value")

        info_table.add_row("Role", agent.role)
        info_table.add_row("Type", agent.agent_type or "Unknown")
        info_table.add_row("Tier", f"{agent.tier.value if agent.tier else '?'} ({tier_name})")
        info_table.add_row("Status", "🟢 Active" if agent.is_active else "⚫ Inactive")

        if agent.description:
            info_table.add_row("Description", agent.description)

        console.print(info_table)

        # File information
        if agent.file_path or agent.generated_at:
            console.print("\n[bold]File Information[/bold]")
            file_table = Table(show_header=False, box=None, padding=(0, 2))
            file_table.add_column("Field", style="cyan")
            file_table.add_column("Value")

            if agent.file_path:
                file_table.add_row("File Path", agent.file_path)

            if agent.generated_at:
                age_days = (datetime.utcnow() - agent.generated_at).days
                generated_str = f"{agent.generated_at.strftime('%Y-%m-%d %H:%M:%S')} ({age_days} days ago)"

                if agent.is_stale():
                    generated_str += " ⚠️ [yellow]STALE[/yellow]"

                file_table.add_row("Generated", generated_str)

            console.print(file_table)

        # Capabilities
        if agent.capabilities:
            console.print("\n[bold]Capabilities[/bold]")
            for capability in agent.capabilities:
                console.print(f"  • {capability}")

        # Metadata
        if agent.metadata and agent.metadata != '{}':
            try:
                metadata = json.loads(agent.metadata)
                if metadata:
                    console.print("\n[bold]Metadata[/bold]")
                    console.print(json.dumps(metadata, indent=2))
            except json.JSONDecodeError:
                pass

        # Usage tracking
        if agent.last_used_at:
            console.print("\n[bold]Usage[/bold]")
            usage_table = Table(show_header=False, box=None, padding=(0, 2))
            usage_table.add_column("Field", style="cyan")
            usage_table.add_column("Value")

            last_used_days = (datetime.utcnow() - agent.last_used_at).days
            usage_table.add_row("Last Used", f"{agent.last_used_at.strftime('%Y-%m-%d')} ({last_used_days} days ago)")

            console.print(usage_table)

        # SOP content (if requested)
        if sop and agent.sop_content:
            console.print("\n[bold]Standard Operating Procedure[/bold]")
            syntax = Syntax(agent.sop_content, "markdown", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, expand=True))

        # Recommendations
        console.print("\n[bold cyan]Recommendations[/bold cyan]")
        if agent.is_stale():
            console.print("  ⚠️  Agent is stale - run: [yellow]apm agents generate --role " + agent.role + "[/yellow]")
        if not agent.is_active:
            console.print("  ⚫ Agent is inactive - activate if needed")
        if not agent.has_sop():
            console.print("  ⚠️  No SOP content - agent may not function correctly")

        # Next actions
        console.print("\n📚 [cyan]Next actions:[/cyan]")
        console.print(f"   apm agents generate --role {agent.role}  # Regenerate")
        console.print(f"   apm agents validate {agent.role}         # Validate")
        console.print(f"   apm agents show {agent.role} --sop       # View SOP\n")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise click.Abort()
