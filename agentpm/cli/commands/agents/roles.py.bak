"""
apm agents roles - Show all available agent roles
"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.command()
@click.pass_context
def roles(ctx: click.Context):
    """
    Show all available agent roles.

    Displays all agent archetypes that can be generated
    based on project technology stack.

    \b
    Example:
      apm agents roles
    """
    console.print("\n📚 [bold cyan]Available Agent Roles[/bold cyan]\n")

    # TODO: Implement dynamic role listing from AgentSelector
    # For now, show common roles
    roles_data = [
        ("python-developer", "Python Developer", "Python code implementation"),
        ("frontend-developer", "Frontend Developer", "UI/UX implementation"),
        ("backend-developer", "Backend Developer", "API and business logic"),
        ("database-developer", "Database Developer", "Schema and migrations"),
        ("testing-specialist", "Testing Specialist", "Test coverage and quality"),
        ("devops-specialist", "DevOps Specialist", "CI/CD and deployment"),
        ("security-specialist", "Security Specialist", "Security assessment"),
        ("documentation-specialist", "Documentation Specialist", "Technical writing"),
        ("requirements-analyst", "Requirements Analyst", "Business requirements"),
        ("architect", "Architect", "System design and architecture"),
    ]

    table = Table(title="Common Agent Roles")
    table.add_column("Role ID", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Focus", style="dim")

    for role_id, display_name, focus in roles_data:
        table.add_row(role_id, display_name, focus)

    console.print(table)

    console.print("\n💡 [dim]Actual agents generated depend on your project's tech stack[/dim]")
    console.print("   Run 'apm agents generate' to create project-specific agents\n")
