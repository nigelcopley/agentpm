"""
apm agents list - List all agents with filtering
"""

import click
from rich.console import Console
from rich.table import Table

from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.enums import AgentTier
from agentpm.core.database.adapters import AgentAdapter

console = Console()


@click.command('list')
@click.option('--active-only', is_flag=True, help='Show only active agents')
@click.option('--tier', '-t', type=click.IntRange(1, 3), help='Filter by tier (1=sub-agent, 2=specialist, 3=master)')
@click.option('--type', 'agent_type', help='Filter by agent type (e.g., implementer, tester, orchestrator)')
@click.option('--stale', is_flag=True, help='Show only stale agents (>7 days old or never generated)')
@click.pass_context
def list_agents_cmd(ctx: click.Context, active_only: bool, tier: int, agent_type: str, stale: bool):
    """
    List all agents with filtering.

    Displays agents sorted by tier, then by role. Shows tier, type, status,
    and generation timestamp for each agent.

    \b
    Examples:
      # All agents
      apm agents list

      # Active agents only
      apm agents list --active-only

      # Filter by tier (1=sub-agent, 2=specialist, 3=master)
      apm agents list --tier 2

      # Filter by type
      apm agents list --type implementer

      # Show stale agents needing regeneration
      apm agents list --stale

      # Combine filters
      apm agents list --tier 2 --active-only
    """
    try:
        project_root = ensure_project_root(ctx)
        db = get_database_service(project_root)
        project_id = get_current_project_id(ctx)

        # List agents
        agents_list = AgentAdapter.list(db, project_id=project_id, active_only=active_only)

        if not agents_list:
            console.print("No agents found. Run 'apm agents generate' first.", style="yellow")
            return

        # Apply filters
        if tier:
            tier_enum = AgentTier(tier)
            agents_list = [a for a in agents_list if a.tier == tier_enum]

        if agent_type:
            agents_list = [a for a in agents_list if a.agent_type == agent_type]

        if stale:
            agents_list = [a for a in agents_list if a.is_stale()]

        if not agents_list:
            console.print("No agents match the specified filters.", style="yellow")
            return

        # Display table
        table = Table(title=f"Agents ({len(agents_list)} total)")
        table.add_column("Tier", justify="center", style="magenta")
        table.add_column("Role", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Generated", style="dim")
        table.add_column("File Path", style="dim")

        for agent in sorted(agents_list, key=lambda a: (a.tier.value if a.tier else 0, a.role)):
            tier_display = str(agent.tier.value) if agent.tier else "?"
            status = "🟢 Active" if agent.is_active else "⚫ Inactive"
            generated = agent.generated_at.strftime("%Y-%m-%d") if agent.generated_at else "Never"

            # Add stale indicator
            if agent.is_stale():
                generated += " ⚠️"

            file_path = agent.file_path if agent.file_path else "-"

            table.add_row(
                tier_display,
                agent.role,
                agent.agent_type or "-",
                status,
                generated,
                file_path
            )

        console.print(table)

        # Show summary stats
        tier_counts = {}
        type_counts = {}
        for agent in agents_list:
            tier_key = f"Tier {agent.tier.value}" if agent.tier else "No tier"
            tier_counts[tier_key] = tier_counts.get(tier_key, 0) + 1

            type_key = agent.agent_type or "No type"
            type_counts[type_key] = type_counts.get(type_key, 0) + 1

        console.print("\n[cyan]Summary:[/cyan]")
        console.print("  By Tier:")
        for tier_name, count in sorted(tier_counts.items()):
            console.print(f"    {tier_name}: {count}")

        console.print("  By Type:")
        for type_name, count in sorted(type_counts.items()):
            console.print(f"    {type_name}: {count}")

        # Show next actions
        console.print("\n📚 [cyan]Next actions:[/cyan]")
        console.print(f"   apm agents show <role>              # View details")
        console.print(f"   apm agents generate --all           # Regenerate all")
        console.print(f"   apm agents validate <role>          # Validate agent\n")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise click.Abort()
