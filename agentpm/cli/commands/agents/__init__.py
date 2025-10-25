"""
agents command group

Modular structure for agent management commands.
Each subcommand in its own file for maintainability.

Commands:
- list: List all agents with filtering
- show: Display detailed agent information
- generate: Generate agent .md files from database
- validate: Validate agent against rules
- roles: Show all available agent roles
- load: Load agent definitions from YAML files
"""

import click

# Import all subcommands
from .list import list_agents_cmd as list
from .show import show
from .generate import generate
from .validate import validate
from .roles import roles
from .load import load_agents as load
from .types import types


@click.group(name='agents')
def agents():
    """
    Manage AI agents for project specialization.

    Agents are project-specific AI assistants with specialized knowledge
    of your tech stack, patterns, and rules. They are generated from the
    database and stored as .md files in .claude/agents/{tier}/{role}.md.

    \b
    Agent Tiers:
      1 - Sub-agents (Research & Analysis)
      2 - Specialist agents (Implementation)
      3 - Master orchestrators (Routing & Delegation)

    \b
    Generation Flow:
      Database (agent metadata) → Jinja2 template → .md files

    \b
    Examples:
      # List all agents
      apm agents list

      # Filter by tier and status
      apm agents list --tier 2 --active-only

      # Show detailed agent info
      apm agents show aipm-database-developer

      # Generate all agent files
      apm agents generate --all --llm claude

      # Generate single agent
      apm agents generate --role aipm-python-cli-developer

      # Validate agent against rules
      apm agents validate aipm-testing-specialist

      # Load agents from YAML
      apm agents load --file=my-agent.yaml
      apm agents load --validate-only
    """
    pass


# Register subcommands
agents.add_command(list)
agents.add_command(show)
agents.add_command(generate)
agents.add_command(validate)
agents.add_command(roles)
agents.add_command(load)
agents.add_command(types)
