"""
Skills CLI Commands

Commands for managing Claude Code Skills integration with APM (Agent Project Manager).
Generates Skills from APM (Agent Project Manager) agents, workflows, and capabilities.

Pattern: Click commands with Rich formatting
"""

import click
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ...core.database.service import DatabaseService
from ...providers.anthropic.skills import ClaudeCodeSkillGenerator, SkillDefinition, SkillType
from ..utils.services import get_database_service
from ..utils.project import ensure_project_root, get_current_project_id


@click.group()
def skills():
    """Manage Claude Code Skills for APM (Agent Project Manager)."""
    pass


@skills.command()
@click.option(
    "--project-id", 
    type=int, 
    help="Project ID (defaults to current project)"
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path(".claude/skills"),
    help="Output directory for Skills (default: .claude/skills)"
)
@click.option(
    "--skill-type",
    type=click.Choice(["personal", "project", "plugin"]),
    default="project",
    help="Type of Skills to generate (default: project)"
)
@click.option(
    "--include-agents/--no-agents",
    default=True,
    help="Include agent specialization Skills"
)
@click.option(
    "--include-workflows/--no-workflows", 
    default=True,
    help="Include workflow Skills"
)
@click.option(
    "--include-frameworks/--no-frameworks",
    default=True, 
    help="Include framework-specific Skills"
)
@click.option(
    "--include-core/--no-core",
    default=True,
    help="Include core APM (Agent Project Manager) Skills"
)
@click.pass_context
def generate(
    ctx,
    project_id: Optional[int],
    output_dir: Path,
    skill_type: str,
    include_agents: bool,
    include_workflows: bool,
    include_frameworks: bool,
    include_core: bool
):
    """Generate Claude Code Skills from APM (Agent Project Manager) components."""
    console = ctx.obj['console']
    
    try:
        # Get project root and database service
        project_root = ensure_project_root(ctx)
        db_service = get_database_service(project_root)
        
        # Get project ID if not provided
        if not project_id:
            project_id = get_current_project_id(ctx)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize skill generator
        generator = ClaudeCodeSkillGenerator(db_service)
        
        console.print(f"[blue]Generating Claude Code Skills for project {project_id}...[/blue]")
        
        generated_skills = []
        
        # Generate core skills
        if include_core:
            console.print("[yellow]Generating core Skills...[/yellow]")
            core_skills = generator.generate_core_skills(
                project_id, output_dir, SkillType(skill_type)
            )
            generated_skills.extend(core_skills)
            console.print(f"[green]✓[/green] Generated {len(core_skills)} core Skills")
        
        # Generate agent skills
        if include_agents:
            console.print("[yellow]Generating agent Skills...[/yellow]")
            agent_skills = generator.generate_skills_from_agents(
                project_id, output_dir, SkillType(skill_type)
            )
            generated_skills.extend(agent_skills)
            console.print(f"[green]✓[/green] Generated {len(agent_skills)} agent Skills")
        
        # Generate workflow skills
        if include_workflows:
            console.print("[yellow]Generating workflow Skills...[/yellow]")
            workflow_skills = generator.generate_workflow_skills(
                project_id, output_dir, SkillType(skill_type)
            )
            generated_skills.extend(workflow_skills)
            console.print(f"[green]✓[/green] Generated {len(workflow_skills)} workflow Skills")
        
        # Generate framework skills
        if include_frameworks:
            console.print("[yellow]Generating framework Skills...[/yellow]")
            framework_skills = generator.generate_framework_skills(
                project_id, output_dir, SkillType(skill_type)
            )
            generated_skills.extend(framework_skills)
            console.print(f"[green]✓[/green] Generated {len(framework_skills)} framework Skills")
        
        # Display results
        _display_generation_results(console, generated_skills, output_dir)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating Skills: {e}")
        raise


@skills.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path(".claude/skills"),
    help="Skills directory to list (default: .claude/skills)"
)
@click.pass_context
def list_skills(ctx, output_dir: Path):
    """List generated Claude Code Skills."""
    console = ctx.obj['console']
    
    try:
        if not output_dir.exists():
            console.print(f"[yellow]No Skills directory found at {output_dir}[/yellow]")
            return
        
        # Find all Skills
        skill_dirs = [d for d in output_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        
        if not skill_dirs:
            console.print(f"[yellow]No Skills found in {output_dir}[/yellow]")
            return
        
        # Create table
        table = Table(title="Claude Code Skills")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Category", style="green")
        table.add_column("Directory", style="blue")
        
        for skill_dir in sorted(skill_dirs):
            skill_file = skill_dir / "SKILL.md"
            metadata_file = skill_dir / "metadata.json"
            
            # Read skill metadata
            name = skill_dir.name.replace("-", " ").title()
            description = "No description available"
            category = "Unknown"
            
            if metadata_file.exists():
                import json
                try:
                    metadata = json.loads(metadata_file.read_text())
                    name = metadata.get("name", name)
                    description = metadata.get("description", description)
                    category = metadata.get("category", category)
                except Exception:
                    pass
            
            table.add_row(name, description, category, skill_dir.name)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing Skills: {e}")
        raise


@skills.command()
@click.argument("skill_name")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path(".claude/skills"),
    help="Skills directory (default: .claude/skills)"
)
@click.pass_context
def show(ctx, skill_name: str, output_dir: Path):
    """Show details of a specific Skill."""
    console = ctx.obj['console']
    
    try:
        skill_dir = output_dir / skill_name
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "metadata.json"
        
        if not skill_file.exists():
            console.print(f"[red]✗[/red] Skill '{skill_name}' not found")
            return
        
        # Read and display skill content
        skill_content = skill_file.read_text()
        
        # Read metadata if available
        metadata = {}
        if metadata_file.exists():
            import json
            try:
                metadata = json.loads(metadata_file.read_text())
            except Exception:
                pass
        
        # Display skill
        console.print(Panel(
            skill_content,
            title=f"Skill: {metadata.get('name', skill_name)}",
            subtitle=f"Category: {metadata.get('category', 'Unknown')}",
            border_style="blue"
        ))
        
        # Display metadata
        if metadata:
            console.print("\n[bold]Metadata:[/bold]")
            for key, value in metadata.items():
                if key not in ["name", "description", "category"]:
                    console.print(f"  {key}: {value}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error showing Skill: {e}")
        raise


@skills.command()
@click.argument("skill_name")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path(".claude/skills"),
    help="Skills directory (default: .claude/skills)"
)
@click.confirmation_option(prompt="Are you sure you want to remove this Skill?")
@click.pass_context
def remove(ctx, skill_name: str, output_dir: Path):
    """Remove a specific Skill."""
    console = ctx.obj['console']
    
    try:
        skill_dir = output_dir / skill_name
        
        if not skill_dir.exists():
            console.print(f"[red]✗[/red] Skill '{skill_name}' not found")
            return
        
        # Remove skill directory
        import shutil
        shutil.rmtree(skill_dir)
        
        console.print(f"[green]✓[/green] Removed Skill '{skill_name}'")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error removing Skill: {e}")
        raise


@skills.command()
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path(".claude/skills"),
    help="Skills directory (default: .claude/skills)"
)
@click.confirmation_option(prompt="Are you sure you want to remove all Skills?")
@click.pass_context
def clear(ctx, output_dir: Path):
    """Remove all generated Skills."""
    console = ctx.obj['console']
    
    try:
        if not output_dir.exists():
            console.print(f"[yellow]No Skills directory found at {output_dir}[/yellow]")
            return
        
        # Remove all skill directories
        import shutil
        for skill_dir in output_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                shutil.rmtree(skill_dir)
        
        console.print(f"[green]✓[/green] Removed all Skills from {output_dir}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error clearing Skills: {e}")
        raise


def _display_generation_results(console: Console, skills: list[SkillDefinition], output_dir: Path):
    """Display skill generation results."""
    if not skills:
        console.print("[yellow]No Skills generated[/yellow]")
        return
    
    # Create results table
    table = Table(title="Generated Claude Code Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Directory", style="blue")
    table.add_column("Tools", style="yellow")
    
    for skill in skills:
        tools = ", ".join(skill.allowed_tools) if skill.allowed_tools else "All"
        table.add_row(
            skill.name,
            skill.category.value,
            skill.get_skill_directory_name(),
            tools
        )
    
    console.print(table)
    
    # Display usage instructions
    console.print(f"\n[bold]Skills written to:[/bold] {output_dir}")
    console.print("\n[bold]Usage in Claude Code:[/bold]")
    console.print("1. Restart Claude Code to discover new Skills")
    console.print("2. Ask Claude about project management or specific frameworks")
    console.print("3. Skills will be automatically invoked based on your requests")
    
    # Display skill categories
    categories = {}
    for skill in skills:
        cat = skill.category.value
        categories[cat] = categories.get(cat, 0) + 1
    
    console.print(f"\n[bold]Generated by category:[/bold]")
    for category, count in categories.items():
        console.print(f"  {category}: {count} Skills")
