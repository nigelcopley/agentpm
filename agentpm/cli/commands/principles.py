"""
Development Principles CLI Commands

Commands for working with the Pyramid of Software Development Principles.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ...core.database.enums.development_principles import (
    DevelopmentPrinciple,
    get_principle_definition,
    resolve_principle_conflict,
    get_principles_by_priority,
    get_principles_for_ai_agents,
    PrincipleCategory,
    PrinciplePriority,
)


@click.group()
def principles():
    """Development principles commands based on the Pyramid of Software Development Principles."""
    pass


@principles.command()
@click.option('--category', type=click.Choice(['foundation', 'core', 'quality', 'advanced']), 
              help='Filter by principle category')
@click.option('--priority', type=click.Choice(['critical', 'high', 'medium', 'low']), 
              help='Filter by priority level')
@click.option('--ai-agents', is_flag=True, help='Show only AI agent principles')
def list(category, priority, ai_agents):
    """List all development principles with their definitions."""
    console = Console()
    
    if ai_agents:
        principles_list = get_principles_for_ai_agents()
        title = "AI Agent Development Principles"
    elif category:
        principles_list = DevelopmentPrinciple.get_by_category(category.title())
        title = f"{category.title()} Development Principles"
    elif priority:
        # Filter by priority level
        all_principles = get_principles_by_priority()
        priority_map = {
            'critical': (1, 3),
            'high': (4, 6),
            'medium': (7, 9),
            'low': (10, 12)
        }
        min_priority, max_priority = priority_map[priority]
        principles_list = [
            p for p in all_principles
            if min_priority <= DevelopmentPrinciple.get_priority(p) <= max_priority
        ]
        title = f"{priority.title()} Priority Development Principles"
    else:
        principles_list = get_principles_by_priority()
        title = "All Development Principles (by Priority)"
    
    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Priority", style="cyan", width=8)
    table.add_column("Principle", style="green", width=20)
    table.add_column("Category", style="yellow", width=12)
    table.add_column("Description", style="white", width=50)
    
    for principle in principles_list:
        definition = get_principle_definition(principle)
        priority_level = PrinciplePriority.from_priority_number(definition.priority)
        
        table.add_row(
            str(definition.priority),
            definition.name,
            definition.category,
            definition.description
        )
    
    console.print(table)


@principles.command()
@click.argument('principle_name')
def show(principle_name):
    """Show detailed information about a specific principle."""
    console = Console()
    
    # Find principle by name (case insensitive)
    principle = None
    for p in DevelopmentPrinciple:
        definition = get_principle_definition(p)
        if principle_name.lower() in definition.name.lower():
            principle = p
            break
    
    if not principle:
        console.print(f"[red]Error:[/red] Principle '{principle_name}' not found.")
        console.print("Available principles:")
        for p in DevelopmentPrinciple:
            definition = get_principle_definition(p)
            console.print(f"  - {definition.name}")
        return
    
    definition = get_principle_definition(principle)
    priority_level = PrinciplePriority.from_priority_number(definition.priority)
    
    # Create detailed panel
    content = f"""
[bold]Description:[/bold] {definition.description}

[bold]Application:[/bold] {definition.application}

[bold]Priority:[/bold] {definition.priority} ({priority_level.value.title()})
[bold]Category:[/bold] {definition.category}

[bold]Examples:[/bold]
"""
    
    for i, example in enumerate(definition.examples, 1):
        content += f"  {i}. {example}\n"
    
    panel = Panel(
        content.strip(),
        title=f"[bold blue]{definition.name}[/bold blue]",
        border_style="blue"
    )
    
    console.print(panel)


@principles.command()
@click.argument('principle1')
@click.argument('principle2')
def conflict(principle1, principle2):
    """Resolve a conflict between two principles."""
    console = Console()
    
    # Find principles by name
    p1 = None
    p2 = None
    
    for p in DevelopmentPrinciple:
        def1 = get_principle_definition(p)
        if principle1.lower() in def1.name.lower():
            p1 = p
        if principle2.lower() in def1.name.lower():
            p2 = p
    
    if not p1:
        console.print(f"[red]Error:[/red] Principle '{principle1}' not found.")
        return
    
    if not p2:
        console.print(f"[red]Error:[/red] Principle '{principle2}' not found.")
        return
    
    # Resolve conflict
    winner = resolve_principle_conflict(p1, p2)
    winner_def = get_principle_definition(winner)
    loser_def = get_principle_definition(p2 if winner == p1 else p1)
    
    console.print(f"[bold]Conflict Resolution:[/bold]")
    console.print(f"[green]Winner:[/green] {winner_def.name} (Priority: {winner_def.priority})")
    console.print(f"[red]Loser:[/red] {loser_def.name} (Priority: {loser_def.priority})")
    console.print()
    console.print(f"[bold]Reason:[/bold] {winner_def.description}")


@principles.command()
def pyramid():
    """Show the complete pyramid of development principles."""
    console = Console()
    
    console.print("[bold blue]The Pyramid of Software Development Principles[/bold blue]")
    console.print("Based on Bartosz Krajka's work: https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/")
    console.print()
    console.print("[bold]Foundation Principle:[/bold] You shouldn't undermine lower layers at the expense of higher layers.")
    console.print("When principles conflict, choose the one lower on the pyramid.")
    console.print()
    
    # Create pyramid visualization
    principles_list = get_principles_by_priority()
    
    for i, principle in enumerate(principles_list, 1):
        definition = get_principle_definition(principle)
        priority_level = PrinciplePriority.from_priority_number(definition.priority)
        
        # Color based on priority level
        if priority_level == PrinciplePriority.CRITICAL:
            color = "red"
        elif priority_level == PrinciplePriority.HIGH:
            color = "yellow"
        elif priority_level == PrinciplePriority.MEDIUM:
            color = "blue"
        else:
            color = "green"
        
        # Create indentation for pyramid effect
        indent = "  " * (12 - i)
        
        console.print(f"{indent}[{color}]{i:2d}. {definition.name}[/{color}]")
        console.print(f"{indent}    {definition.description}")
        console.print()


@principles.command()
def ai_agents():
    """Show principles most important for AI agent enablement."""
    console = Console()
    
    console.print("[bold blue]AI Agent Development Principles[/bold blue]")
    console.print("These principles are most critical for enabling effective AI agent operation.")
    console.print()
    
    ai_principles = get_principles_for_ai_agents()
    
    for principle in ai_principles:
        definition = get_principle_definition(principle)
        
        panel = Panel(
            f"[bold]Description:[/bold] {definition.description}\n\n"
            f"[bold]Application:[/bold] {definition.application}\n\n"
            f"[bold]Why for AI Agents:[/bold] {_get_ai_agent_rationale(principle)}",
            title=f"[bold green]{definition.name}[/bold green] (Priority: {definition.priority})",
            border_style="green"
        )
        
        console.print(panel)
        console.print()


def _get_ai_agent_rationale(principle: DevelopmentPrinciple) -> str:
    """Get AI agent-specific rationale for a principle."""
    rationales = {
        DevelopmentPrinciple.MAKE_IT_WORK: "AI agents cannot operate with broken code. Functional correctness is the foundation for all agent operations.",
        DevelopmentPrinciple.PRINCIPLE_OF_LEAST_SURPRISE: "AI agents rely on predictable behavior to make correct decisions. Unpredictable code leads to agent confusion and errors.",
        DevelopmentPrinciple.BE_CONSISTENT: "Consistent patterns allow AI agents to learn and apply knowledge across different parts of the codebase effectively.",
        DevelopmentPrinciple.CLEAN_CODE: "Clean, readable code is essential for AI agents to understand context and make appropriate modifications."
    }
    return rationales.get(principle, "This principle supports overall code quality and maintainability.")


if __name__ == '__main__':
    principles()
