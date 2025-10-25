"""
apm agents generate-intelligent - Intelligently generate project-specific agents

Uses Claude AI to analyze project tech stack and create specialized agents
tailored to your exact frameworks, languages, and patterns.

Differences from 'apm agents generate':
- Analyzes project to decide which agents are needed
- Creates specialized variants (backend-impl, frontend-impl, api-impl)
- Embeds project-specific rules and patterns
- Dynamic: Different agents for different projects
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Dict, Any, List

from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.core.agents.generator import generate_and_store_agents
from agentpm.core.database.methods import rules as rule_methods

console = Console()


def build_project_context(db, project_id: int, project_root: Path) -> Dict[str, Any]:
    """
    Build project context for intelligent agent generation.

    Analyzes:
    1. Database (project metadata, rules)
    2. Filesystem (detect frameworks via plugins - future)
    3. Configuration files (pyproject.toml, package.json)

    Args:
        db: Database service
        project_id: Project ID
        project_root: Project root directory

    Returns:
        Project context dictionary for Claude analysis
    """
    # Get project from database
    with db.connect() as conn:
        cursor = conn.execute(
            "SELECT name, description, tech_stack FROM projects WHERE id = ?",
            (project_id,)
        )
        project_row = cursor.fetchone()

    if not project_row:
        raise ValueError(f"Project {project_id} not found")

    # Extract tech stack (stored as JSON)
    import json
    tech_stack_raw = project_row['tech_stack'] or '{}'
    tech_stack = json.loads(tech_stack_raw) if isinstance(tech_stack_raw, str) else tech_stack_raw

    # Build context
    context = {
        'business_domain': project_row['description'] or 'Software Development',
        'app_type': _infer_app_type(project_root, tech_stack),
        'languages': tech_stack.get('languages', ['Python']),
        'frameworks': tech_stack.get('frameworks', []),
        'database': tech_stack.get('database', 'SQLite'),
        'testing_frameworks': tech_stack.get('testing', ['pytest']),
        'methodology': 'APM Quality-Gated Development',
        'rules': _load_project_rules(db, project_id),
    }

    return context


def _infer_app_type(project_root: Path, tech_stack: Dict[str, Any]) -> str:
    """Infer application type from tech stack and project structure"""
    frameworks = tech_stack.get('frameworks', [])

    # Check frameworks
    if 'Django' in frameworks or 'Flask' in frameworks or 'FastAPI' in frameworks:
        return 'Web Application'
    if 'Click' in frameworks:
        return 'CLI Tool'
    if 'React' in frameworks or 'Vue' in frameworks or 'Angular' in frameworks:
        return 'Frontend Application'

    # Check project structure
    if (project_root / 'setup.py').exists() or (project_root / 'pyproject.toml').exists():
        return 'Python Package'
    if (project_root / 'package.json').exists():
        return 'Node.js Application'

    return 'Application'


def _load_project_rules(db, project_id: int) -> List[str]:
    """Load project rules for context"""
    rules = rule_methods.list_rules(db, project_id=project_id)

    # Format rules for context
    rule_strings = []
    for rule in rules:
        if rule.enforcement_level in ('BLOCK', 'LIMIT'):
            rule_strings.append(f"{rule.rule_id}: {rule.name} ({rule.enforcement_level})")

    return rule_strings[:10]  # Top 10 rules


def display_project_analysis(context: Dict[str, Any]) -> None:
    """Display project analysis before generation"""
    console.print("\n📊 Project Analysis", style="cyan bold")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Business Domain", context.get('business_domain', 'Unknown'))
    table.add_row("Application Type", context.get('app_type', 'Unknown'))
    table.add_row("Languages", ', '.join(context.get('languages', [])))
    table.add_row("Frameworks", ', '.join(context.get('frameworks', [])) or 'None detected')
    table.add_row("Database", context.get('database', 'Unknown'))
    table.add_row("Testing", ', '.join(context.get('testing_frameworks', [])))
    table.add_row("Active Rules", str(len(context.get('rules', []))))

    console.print(table)


def display_generation_results(agents: List) -> None:
    """Display generated agents in a table"""
    if not agents:
        console.print("\n⚠️  No agents generated", style="yellow")
        return

    console.print(f"\n✅ Generated {len(agents)} specialized agents", style="green bold")

    table = Table(title="Generated Agents", show_lines=True)
    table.add_column("Role", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Capabilities", style="dim")

    for agent in agents:
        capabilities = ', '.join(agent.capabilities[:3]) if agent.capabilities else 'General'
        if len(agent.capabilities) > 3:
            capabilities += f" +{len(agent.capabilities) - 3} more"

        table.add_row(
            agent.role,
            agent.agent_type,
            agent.display_name,
            capabilities
        )

    console.print(table)


@click.command('generate-intelligent')
@click.option(
    '--use-claude',
    is_flag=True,
    help='Use real Claude API (slower, requires API key)'
)
@click.option(
    '--template-dir',
    type=click.Path(exists=True),
    help='Custom template directory',
    default=None
)
@click.option(
    '--output-dir',
    type=click.Path(),
    help='Agent output directory (default: .claude/agents/)',
    default=None
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be generated without creating files'
)
@click.option(
    '--force',
    is_flag=True,
    help='Regenerate even if agents already exist'
)
@click.pass_context
def generate_intelligent(
    ctx: click.Context,
    use_claude: bool,
    template_dir: str,
    output_dir: str,
    dry_run: bool,
    force: bool
):
    """
    Intelligently generate project-specific agents using AI analysis.

    Analyzes your project's tech stack and creates specialized agents
    tailored to your frameworks, languages, and patterns.

    \b
    How it works:
      1. Analyzes project context (languages, frameworks, database)
      2. Uses AI to decide which agents are needed
      3. Creates specialized variants (e.g., backend-impl, frontend-impl)
      4. Embeds project-specific rules and patterns
      5. Generates agent SOP files in .claude/agents/

    \b
    Examples:
      # Generate agents (fast mock mode)
      apm agents generate-intelligent

      # Use real Claude API (slower, more intelligent)
      apm agents generate-intelligent --use-claude

      # Dry run (show what would be generated)
      apm agents generate-intelligent --dry-run

      # Force regeneration
      apm agents generate-intelligent --force

    \b
    Output:
      • Creates agents in database
      • Writes SOP files to .claude/agents/
      • Embeds project rules automatically
      • Ready to use via Task tool delegation
    """
    try:
        # Find project
        project_root = ensure_project_root(ctx)
        project_path = Path(project_root)
        db = get_database_service(project_root)
        project_id = get_current_project_id(ctx)

        console.print("\n🤖 Intelligent Agent Generation", style="cyan bold")
        console.print("─" * 50, style="dim")

        # Build project context
        with console.status("[cyan]Analyzing project...", spinner="dots"):
            context = build_project_context(db, project_id, project_path)

        # Display analysis
        display_project_analysis(context)

        # Confirm if not force
        if not force and not dry_run:
            # Check if agents already exist
            with db.connect() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM agents WHERE project_id = ?",
                    (project_id,)
                )
                existing_count = cursor.fetchone()['count']

            if existing_count > 0:
                console.print(f"\n⚠️  {existing_count} agents already exist in database", style="yellow")
                if not click.confirm("Regenerate agents? (This will replace existing agents)"):
                    console.print("❌ Cancelled", style="red")
                    return

        # Determine paths
        if template_dir:
            template_path = Path(template_dir)
        else:
            # Use default templates
            from importlib import resources
            try:
                # Python 3.9+
                template_path = Path(resources.files('agentpm.core.agents.templates'))
            except AttributeError:
                # Fallback for older Python
                import pkg_resources
                template_path = Path(pkg_resources.resource_filename(
                    'agentpm.core.agents',
                    'templates'
                ))

        if not template_path.exists():
            console.print(f"❌ Template directory not found: {template_path}", style="red")
            raise click.Abort()

        if output_dir:
            agent_output_path = Path(output_dir)
        else:
            agent_output_path = project_path / '.claude' / 'agents'

        if dry_run:
            console.print("\n[DRY RUN - No files will be written]", style="yellow bold")

        # Generate agents
        console.print(f"\n🔧 Generating agents...", style="cyan")
        if use_claude:
            console.print("   Using real Claude API (this may take 1-2 minutes)", style="dim")
        else:
            console.print("   Using intelligent mock generation (fast)", style="dim")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating agents...", total=None)

            # Delete existing agents if force
            if force and not dry_run:
                with db.connect() as conn:
                    conn.execute(
                        "DELETE FROM agents WHERE project_id = ?",
                        (project_id,)
                    )
                    conn.commit()

            if not dry_run:
                # Real generation
                agents = generate_and_store_agents(
                    db=db,
                    project_id=project_id,
                    project_context=context,
                    template_directory=template_path,
                    agent_output_dir=agent_output_path,
                    use_real_claude=use_claude
                )
            else:
                # Dry run - just generate specs without database
                from agentpm.core.agents.generator import generate_agents_with_claude
                agent_specs = generate_agents_with_claude(
                    project_context=context,
                    template_directory=template_path,
                    use_real_claude=use_claude
                )
                # Convert to mock Agent objects for display
                from agentpm.core.database.models import Agent
                agents = [
                    Agent(
                        id=i+1,
                        project_id=project_id,
                        role=spec['name'],
                        display_name=spec.get('description', spec['name']),
                        description=spec.get('specialization', ''),
                        capabilities=spec.get('tech_focus', []),
                        agent_type=spec.get('archetype', 'implementer'),
                        is_active=True
                    )
                    for i, spec in enumerate(agent_specs)
                ]

            progress.update(task, completed=100)

        # Display results
        display_generation_results(agents)

        if not dry_run:
            console.print(f"\n📁 Agent files written to: {agent_output_path}", style="cyan")
            console.print(f"📊 Database records created: {len(agents)}", style="cyan")

            # Show next steps
            panel = Panel(
                "[cyan]Next Steps:[/cyan]\n\n"
                "1. Review generated agents: [white]ls .claude/agents/[/white]\n"
                "2. List agents in database: [white]apm agents list[/white]\n"
                "3. View agent details: [white]apm agents show <role>[/white]\n"
                "4. Use agents via Task tool delegation in CLAUDE.md",
                title="✅ Generation Complete",
                border_style="green"
            )
            console.print(panel)
        else:
            console.print("\n💡 Dry run complete - no files or database records created", style="dim")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red bold")
        import traceback
        console.print("\n[dim]Traceback:[/dim]")
        console.print(traceback.format_exc(), style="dim")
        raise click.Abort()
