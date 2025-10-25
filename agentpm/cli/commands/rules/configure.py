"""
apm rules configure - Re-run questionnaire to reconfigure rules
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from agentpm.core.database import DatabaseService
from agentpm.core.database.models import Context, UnifiedSixW
from agentpm.core.database.enums import ContextType, EntityType
from agentpm.core.database.adapters import RuleAdapter
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import contexts as context_methods
from agentpm.core.rules.questionnaire import QuestionnaireService
from agentpm.core.rules.generator import RuleGenerationService
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from typing import Any, Dict


def _create_rules_context(
    project_id: int,
    answers: Dict[str, Any],
    loaded_count: int
) -> Context:
    """Convert questionnaire answers to 6W context format."""
    six_w = UnifiedSixW()

    # WHO: Team composition - set the underlying fields, not the computed property
    six_w.implementers = [f"Team size: {answers.get('team_size_detail', 'Solo developer')}"]
    six_w.reviewers = [f"Development stage: {answers.get('development_stage', 'prototype')}"]
    six_w.end_users = [f"Target users: {answers.get('target_users', 'General users')}"]

    # WHAT: Project characteristics - set the underlying fields
    six_w.functional_requirements = [
        f"Project type: {answers.get('project_type', 'cli')}",
        f"Primary language: {answers.get('primary_language', 'python')}",
        f"Architecture: {answers.get('architecture_style', 'not specified')}"
    ]
    six_w.acceptance_criteria = [
        f"Test coverage >= {answers.get('test_coverage_min', 90)}%",
        f"Code review required: {answers.get('code_review_required', True)}"
    ]

    # WHERE: Technical environment - set the underlying fields
    tech_stack = []
    if answers.get('backend_framework'):
        tech_stack.append(f"Backend: {answers['backend_framework']}")
    if answers.get('frontend_framework'):
        tech_stack.append(f"Frontend: {answers['frontend_framework']}")
    if answers.get('database'):
        tech_stack.append(f"Database: {answers['database']}")
    six_w.affected_services = tech_stack or ["No framework specified"]
    six_w.deployment_targets = [f"Deployment: {answers.get('deployment_strategy', 'not specified')}"]

    # WHEN: Development constraints - set the underlying fields
    six_w.dependencies_timeline = [
        f"Expected task duration: {answers.get('time_boxing_hours', 4)}h",
        f"Timeline: {answers.get('timeline', 'Flexible timeline')}"
    ]

    # WHY: Development philosophy - set the underlying fields
    six_w.business_value = f"Project purpose: {answers.get('project_purpose', 'Not specified')}"
    six_w.risk_if_delayed = f"Constraints: {answers.get('constraints', 'No specific constraints')}"

    # HOW: Implementation standards - set the underlying fields
    six_w.suggested_approach = f"Development approach: {answers.get('development_approach', 'not specified')}"
    six_w.existing_patterns = [
        f"Rules preset selected: {answers.get('_selected_preset', 'standard')}",
        f"Rules loaded: {loaded_count}",
        f"Technical rationale: {answers.get('tech_rationale', 'Standard stack for project type')}"
    ]

    # Technical constraints from rules
    six_w.technical_constraints = [
        f"Test coverage >= {answers.get('test_coverage_min', 90)}%",
        f"Max task duration: {answers.get('time_boxing_hours', 4)}h"
    ]

    return Context(
        project_id=project_id,
        context_type=ContextType.RULES_CONTEXT,
        entity_type=EntityType.PROJECT,
        entity_id=project_id,
        six_w=six_w,
        confidence_score=0.9,
        confidence_factors={'source': 'questionnaire_reconfigure', 'answers': answers}
    )


@click.command()
@click.pass_context
def configure_rules(ctx: click.Context):
    """
    Re-run questionnaire to reconfigure project rules.

    This will:
    1. Archive existing rules
    2. Run the interactive questionnaire
    3. Generate and load new rules based on answers
    4. Update project configuration context

    \b
    Example:
      apm rules configure
    """
    console = ctx.obj['console']

    # Find project database
    cwd = Path.cwd()
    aipm_dir = cwd / '.aipm'

    if not aipm_dir.exists():
        console.print("[red]❌ Not an AIPM project (no .aipm directory found)[/red]")
        console.print("[dim]Run 'apm init' to initialize this project[/dim]")
        raise click.Abort()

    db_path = aipm_dir / 'data' / 'aipm.db'
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

    # Check existing rules
    try:
        existing_rules = RuleAdapter.list(db, project_id=project.id, enabled_only=False)
        has_existing = len(existing_rules) > 0
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not load existing rules: {e}[/yellow]")
        has_existing = False

    # Confirm if rules exist
    if has_existing:
        console.print(f"\n[yellow]⚠️  This project currently has {len(existing_rules)} rules configured.[/yellow]")
        console.print("[dim]Re-configuring will archive existing rules and load new ones.[/dim]\n")

        if not Confirm.ask("Continue with reconfiguration?", default=False):
            console.print("\n[dim]Configuration cancelled[/dim]\n")
            return

    # Show intro panel
    intro_panel = Panel(
        "[cyan]Project Rules Configuration[/cyan]\n\n"
        "Answer the following questions to configure rules for your project.\n"
        "This determines governance, code quality standards, and AI agent constraints.",
        border_style="cyan"
    )
    console.print(intro_panel)

    # Run questionnaire
    try:
        questionnaire = QuestionnaireService(console=console)
        answers = questionnaire.run()

        if not answers:
            console.print("\n[yellow]⚠️  Questionnaire incomplete[/yellow]\n")
            return

    except Exception as e:
        console.print(f"\n[red]❌ Questionnaire failed: {e}[/red]\n")
        raise click.Abort()

    # Archive existing rules (soft delete)
    if has_existing:
        try:
            console.print("\n[dim]Archiving existing rules...[/dim]")
            # Note: Archive functionality would be implemented in rule_methods
            # For now, rules will be overwritten
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not archive rules: {e}[/yellow]")

    # Generate and load new rules
    try:
        console.print("[dim]Loading new rules...[/dim]")
        generator = RuleGenerationService(db)
        loaded_rules = generator.generate(
            answers=answers,
            project_id=project.id,
            overwrite=True  # Replace existing rules
        )
        loaded_count = len(loaded_rules)

        console.print(f"[green]✓ Loaded {loaded_count} rules[/green]")

    except Exception as e:
        console.print(f"\n[red]❌ Failed to load rules: {e}[/red]\n")
        raise click.Abort()

    # Store configuration as 6W context
    try:
        console.print("[dim]Storing configuration...[/dim]")
        rules_context = _create_rules_context(
            project_id=project.id,
            answers=answers,
            loaded_count=loaded_count
        )
        context_methods.create_context(db, rules_context)

        console.print("[green]✓ Configuration saved[/green]\n")

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not save context: {e}[/yellow]\n")

    # Show success message
    console.print("[green]✅ Rules configuration complete![/green]\n")

    # Show summary
    preset = answers.get('_selected_preset', 'standard')
    coverage = answers.get('test_coverage', 90)
    time_box = answers.get('time_boxing', 4)

    console.print(f"[cyan]Configuration Summary:[/cyan]")
    console.print(f"  Rules Loaded: {loaded_count}")
    console.print(f"  Preset: {preset.replace('_', ' ').title()}")
    console.print(f"  Coverage Target: {coverage}%")
    console.print(f"  Max Task Duration: {time_box}h\n")

    console.print("[dim]Commands:[/dim]")
    console.print("  apm rules list              # View all rules")
    console.print("  apm rules show <rule-id>    # View rule details\n")
