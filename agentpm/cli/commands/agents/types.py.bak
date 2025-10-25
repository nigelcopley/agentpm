"""
Agent Types Command

Exposes agent-related Pydantic models and enums via CLI.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agentpm.core.database.enums import AgentTier, ConfidenceBand


@click.command()
@click.option('--type', 'type_filter', 
              type=click.Choice(['tier', 'confidence-band', 'all']),
              default='all',
              help='Filter which types to display')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'list', 'json']),
              default='table',
              help='Output format')
@click.pass_context
def types(ctx: click.Context, type_filter: str, output_format: str):
    """
    🤖 Show available agent tiers and confidence bands.
    
    Displays all valid values for agent-related enums that can be used
    in agent commands. Essential for AI agents and users to discover
    valid options without hardcoding values.
    
    \b
    Examples:
      apm agents types                    # Show all types
      apm agents types --type=tier        # Show only agent tiers
      apm agents types --type=confidence-band  # Show confidence bands
      apm agents types --format=list      # Simple list format
    """
    console = Console()
    
    if type_filter == 'all' or type_filter == 'tier':
        _show_agent_tiers(console, output_format)
    
    if type_filter == 'all' or type_filter == 'confidence-band':
        _show_confidence_bands(console, output_format)


def _show_agent_tiers(console: Console, output_format: str):
    """Show agent tiers with descriptions."""
    if output_format == 'table':
        table = Table(title="🤖 Agent Tiers", show_header=True, header_style="bold blue")
        table.add_column("Tier", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        tier_descriptions = {
            AgentTier.TIER_1.value: "Universal specialists (work on any project)",
            AgentTier.TIER_2.value: "Tech stack specialists (language/framework specific)",
            AgentTier.TIER_3.value: "Domain specialists (business domain specific)",
        }
        
        for tier in AgentTier:
            table.add_row(str(tier.value), tier_descriptions.get(tier.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(AgentTier)} agent tiers[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("🤖 Agent Tiers", style="bold blue"))
        tier_descriptions = {
            AgentTier.TIER_1.value: "Universal specialists (work on any project)",
            AgentTier.TIER_2.value: "Tech stack specialists (language/framework specific)",
            AgentTier.TIER_3.value: "Domain specialists (business domain specific)",
        }
        for tier in AgentTier:
            console.print(f"  • Tier {tier.value}: {tier_descriptions.get(tier.value, '')}")
    
    elif output_format == 'json':
        import json
        tier_descriptions = {
            AgentTier.TIER_1.value: "Universal specialists (work on any project)",
            AgentTier.TIER_2.value: "Tech stack specialists (language/framework specific)",
            AgentTier.TIER_3.value: "Domain specialists (business domain specific)",
        }
        tiers_data = {
            "agent_tiers": [
                {"tier": tier.value, "description": tier_descriptions.get(tier.value, "")}
                for tier in AgentTier
            ]
        }
        console.print(json.dumps(tiers_data, indent=2))


def _show_confidence_bands(console: Console, output_format: str):
    """Show confidence bands with descriptions."""
    if output_format == 'table':
        table = Table(title="🤖 Confidence Bands", show_header=True, header_style="bold blue")
        table.add_column("Band", style="cyan", no_wrap=True)
        table.add_column("Score Range", style="yellow", no_wrap=True)
        table.add_column("Description", style="white")
        
        confidence_descriptions = {
            ConfidenceBand.RED.value: "< 0.5",
            ConfidenceBand.YELLOW.value: "0.5 - 0.8",
            ConfidenceBand.GREEN.value: "> 0.8",
        }
        
        band_descriptions = {
            ConfidenceBand.RED.value: "Insufficient context, agent cannot operate",
            ConfidenceBand.YELLOW.value: "Adequate context, agent can operate with limitations",
            ConfidenceBand.GREEN.value: "High-quality context, agent fully enabled",
        }
        
        for band in ConfidenceBand:
            table.add_row(
                band.value, 
                confidence_descriptions.get(band.value, ""),
                band_descriptions.get(band.value, "")
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(ConfidenceBand)} confidence bands[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("🤖 Confidence Bands", style="bold blue"))
        confidence_descriptions = {
            ConfidenceBand.RED.value: "< 0.5",
            ConfidenceBand.YELLOW.value: "0.5 - 0.8",
            ConfidenceBand.GREEN.value: "> 0.8",
        }
        
        band_descriptions = {
            ConfidenceBand.RED.value: "Insufficient context, agent cannot operate",
            ConfidenceBand.YELLOW.value: "Adequate context, agent can operate with limitations",
            ConfidenceBand.GREEN.value: "High-quality context, agent fully enabled",
        }
        
        for band in ConfidenceBand:
            score_range = confidence_descriptions.get(band.value, "")
            description = band_descriptions.get(band.value, "")
            console.print(f"  • {band.value} ({score_range}): {description}")
    
    elif output_format == 'json':
        import json
        confidence_descriptions = {
            ConfidenceBand.RED.value: "< 0.5",
            ConfidenceBand.YELLOW.value: "0.5 - 0.8",
            ConfidenceBand.GREEN.value: "> 0.8",
        }
        
        band_descriptions = {
            ConfidenceBand.RED.value: "Insufficient context, agent cannot operate",
            ConfidenceBand.YELLOW.value: "Adequate context, agent can operate with limitations",
            ConfidenceBand.GREEN.value: "High-quality context, agent fully enabled",
        }
        
        bands_data = {
            "confidence_bands": [
                {
                    "band": band.value, 
                    "score_range": confidence_descriptions.get(band.value, ""),
                    "description": band_descriptions.get(band.value, "")
                }
                for band in ConfidenceBand
            ]
        }
        console.print(json.dumps(bands_data, indent=2))

