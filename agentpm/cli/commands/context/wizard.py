"""
Interactive Context Wizard - User-Friendly 6W Population

Provides guided, interactive prompts to populate UnifiedSixW context for work items.
Makes context creation accessible and reduces adoption barriers.

Pattern: Click prompt-based interactive CLI with smart defaults and validation
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from typing import Optional, List
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models import Context, UnifiedSixW
from agentpm.core.database.enums import EntityType, ContextType, ConfidenceBand
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods
from agentpm.core.database.adapters import ContextAdapter
from agentpm.cli.utils.project import find_project_root
from agentpm.cli.utils.services import get_database_service

console = Console()


@click.command()
@click.argument('work_item_id', type=int)
@click.option('--minimal', is_flag=True, help='Only essential fields (WHO/WHAT/WHY)')
@click.option('--skip-existing', is_flag=True, help='Skip fields that already have values')
@click.pass_context
def wizard(ctx, work_item_id: int, minimal: bool, skip_existing: bool):
    """
    Interactive wizard to populate 6W context for work item.

    Guides users through all 15 UnifiedSixW fields with:
    - Smart defaults based on work item type
    - Examples and suggestions
    - Skip/back navigation
    - Real-time validation
    - Saves to contexts table

    Examples:
      apm context wizard 81           # Full 15-field wizard
      apm context wizard 81 --minimal  # Essential 3 fields only
      apm context wizard 81 --skip-existing  # Only populate missing fields
    """
    try:
        # Get database service
        project_root = find_project_root()
        if not project_root:
            console.print("[red]✗[/red] Not in an APM project directory")
            ctx.exit(1)

        db = get_database_service(project_root)

        # Load work item
        work_item = wi_methods.get_work_item(db, work_item_id)
        if not work_item:
            console.print(f"[red]✗[/red] Work item {work_item_id} not found")
            ctx.exit(1)

        # Show work item context
        console.print()
        console.print(Panel(
            f"[bold cyan]Work Item #{work_item.id}[/bold cyan]\n"
            f"Name: {work_item.name}\n"
            f"Type: {work_item.type.value}\n"
            f"Status: {work_item.status.value}",
            title="📋 Context Wizard",
            border_style="cyan"
        ))

        # Check for existing context
        existing = ContextAdapter.get_entity_context(
            db, EntityType.WORK_ITEM, work_item_id
        )

        if existing and existing.six_w:
            console.print("[yellow]ℹ[/yellow] Existing context found")
            if not Confirm.ask("Do you want to update it?", default=True):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Interactive prompts for each field
        six_w = _prompt_six_w_fields(
            db, work_item, existing.six_w if existing else None, minimal, skip_existing
        )

        # Calculate confidence
        confidence = _calculate_confidence(six_w)
        confidence_band = ConfidenceBand.from_score(confidence)

        # Show summary
        _show_summary(six_w, confidence, confidence_band)

        # Confirm save
        if not Confirm.ask("\nSave this context?", default=True):
            console.print("[yellow]Cancelled - context not saved[/yellow]")
            return

        # Save to database
        if existing:
            # Update existing context
            updated = ContextAdapter.update(
                db,
                existing.id,
                six_w=six_w,
                confidence_score=confidence,
                confidence_band=confidence_band
            )
            console.print(f"\n[green]✓[/green] Context updated with {confidence:.0%} confidence ({confidence_band.value})")
        else:
            # Create new context
            context = Context(
                project_id=work_item.project_id,
                context_type=ContextType.WORK_ITEM_CONTEXT,
                entity_type=EntityType.WORK_ITEM,
                entity_id=work_item_id,
                six_w=six_w,
                confidence_score=confidence,
                confidence_band=confidence_band
            )
            created = ContextAdapter.create(db, context)
            console.print(f"\n[green]✓[/green] Context created with {confidence:.0%} confidence ({confidence_band.value})")

        # Show next steps
        console.print()
        console.print(Panel(
            "[bold]Next Steps:[/bold]\n"
            "• View context: [cyan]apm context show --work-item-id={wi_id}[/cyan]\n"
            "• Check quality: [cyan]apm context status[/cyan]\n"
            "• Refresh detection: [cyan]apm context refresh --work-item-id={wi_id}[/cyan]".format(
                wi_id=work_item_id
            ),
            title="💡 Tips",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        ctx.exit(1)


def _prompt_six_w_fields(
    db: DatabaseService,
    work_item,
    existing: Optional[UnifiedSixW],
    minimal: bool,
    skip_existing: bool
) -> UnifiedSixW:
    """
    Prompt for each 6W field with smart defaults.

    Args:
        db: Database service
        work_item: Work item entity
        existing: Existing 6W data (if any)
        minimal: Only prompt for essential fields
        skip_existing: Skip fields that already have values

    Returns:
        Populated UnifiedSixW dataclass
    """
    console.print("\n[bold cyan]═══ WHO: People and Roles ═══[/bold cyan]\n")

    # WHO section
    end_users = _prompt_list_field(
        "Who are the end users?",
        _suggest_end_users(work_item),
        existing.end_users if existing else None,
        "Examples: Customers, Admin users, API consumers",
        skip_existing
    )

    implementers = _prompt_list_field(
        "Who will implement this?",
        _suggest_implementers(db, work_item),
        existing.implementers if existing else None,
        "Examples: @backend-team, @alice, Frontend developers",
        skip_existing
    )

    reviewers = _prompt_list_field(
        "Who will review this?",
        _suggest_reviewers(db, work_item),
        existing.reviewers if existing else None,
        "Examples: @tech-lead, @senior-dev, QA team",
        skip_existing
    )

    console.print("\n[bold cyan]═══ WHAT: Requirements ═══[/bold cyan]\n")

    # WHAT section
    functional_requirements = _prompt_list_field(
        "What functionality is required?",
        _extract_from_description(work_item.description) if work_item.description else [],
        existing.functional_requirements if existing else None,
        "Key features/capabilities",
        skip_existing
    )

    technical_constraints = _prompt_list_field(
        "What are the technical constraints?",
        [],
        existing.technical_constraints if existing else None,
        "Examples: Must use Python 3.9+, Cannot exceed 100ms response time",
        skip_existing
    )

    acceptance_criteria = _prompt_list_field(
        "What are the acceptance criteria?",
        work_item.acceptance_criteria if hasattr(work_item, 'acceptance_criteria') and work_item.acceptance_criteria else [],
        existing.acceptance_criteria if existing else None,
        "Success criteria for completion",
        skip_existing
    )

    # Minimal mode stops here
    if minimal:
        return UnifiedSixW(
            end_users=end_users,
            implementers=implementers,
            reviewers=reviewers,
            functional_requirements=functional_requirements,
            technical_constraints=technical_constraints,
            acceptance_criteria=acceptance_criteria
        )

    console.print("\n[bold cyan]═══ WHERE: Technical Context ═══[/bold cyan]\n")

    # WHERE section
    affected_services = _prompt_list_field(
        "Which services are affected?",
        [],
        existing.affected_services if existing else None,
        "Examples: auth-service, payment-api, frontend",
        skip_existing
    )

    repositories = _prompt_list_field(
        "Which repositories?",
        [],
        existing.repositories if existing else None,
        "Examples: github.com/org/repo, gitlab.com/project",
        skip_existing
    )

    deployment_targets = _prompt_list_field(
        "Where will this deploy?",
        [],
        existing.deployment_targets if existing else None,
        "Examples: production, staging, dev",
        skip_existing
    )

    console.print("\n[bold cyan]═══ WHEN: Timeline ═══[/bold cyan]\n")

    # WHEN section
    deadline_str = _prompt_single_field(
        "Deadline (YYYY-MM-DD)?",
        _suggest_deadline(work_item),
        existing.deadline.strftime("%Y-%m-%d") if existing and existing.deadline else None,
        "Format: 2025-12-31",
        skip_existing
    )

    deadline = None
    if deadline_str and deadline_str.strip():
        try:
            deadline = datetime.strptime(deadline_str.strip(), "%Y-%m-%d")
        except ValueError:
            console.print("[yellow]⚠ Invalid date format, skipping deadline[/yellow]")

    dependencies_timeline = _prompt_list_field(
        "What dependencies affect timing?",
        [],
        existing.dependencies_timeline if existing else None,
        "Examples: Waiting for API spec, Backend must complete first",
        skip_existing
    )

    console.print("\n[bold cyan]═══ WHY: Value Proposition ═══[/bold cyan]\n")

    # WHY section
    business_value = _prompt_single_field(
        "What's the business value?",
        "",
        existing.business_value if existing else None,
        "Why this matters to the business",
        skip_existing
    )

    risk_if_delayed = _prompt_single_field(
        "What's the risk if delayed?",
        "",
        existing.risk_if_delayed if existing else None,
        "Impact of not delivering on time",
        skip_existing
    )

    console.print("\n[bold cyan]═══ HOW: Approach ═══[/bold cyan]\n")

    # HOW section
    suggested_approach = _prompt_single_field(
        "What's the suggested approach?",
        "",
        existing.suggested_approach if existing else None,
        "High-level implementation strategy",
        skip_existing
    )

    existing_patterns = _prompt_list_field(
        "What existing patterns should be used?",
        [],
        existing.existing_patterns if existing else None,
        "Examples: Repository pattern, MVC architecture",
        skip_existing
    )

    return UnifiedSixW(
        end_users=end_users,
        implementers=implementers,
        reviewers=reviewers,
        functional_requirements=functional_requirements,
        technical_constraints=technical_constraints,
        acceptance_criteria=acceptance_criteria,
        affected_services=affected_services,
        repositories=repositories,
        deployment_targets=deployment_targets,
        deadline=deadline,
        dependencies_timeline=dependencies_timeline,
        business_value=business_value or None,
        risk_if_delayed=risk_if_delayed or None,
        suggested_approach=suggested_approach or None,
        existing_patterns=existing_patterns
    )


def _prompt_list_field(
    prompt: str,
    default: List[str],
    existing: Optional[List[str]],
    help_text: str,
    skip_existing: bool
) -> List[str]:
    """
    Prompt for a list field with comma-separated input.

    Args:
        prompt: Field prompt
        default: Default suggestion
        existing: Existing value (if any)
        help_text: Help text
        skip_existing: Skip if existing has values

    Returns:
        List of values
    """
    # Skip if existing has values
    if skip_existing and existing and len(existing) > 0:
        console.print(f"[dim]{prompt}[/dim] [green](using existing)[/green]")
        return existing

    # Show existing value
    if existing and len(existing) > 0:
        console.print(f"[dim]Current: {', '.join(existing)}[/dim]")

    # Show default suggestion
    default_str = ", ".join(default) if default else ""
    if default_str:
        console.print(f"[dim]Suggestion: {default_str}[/dim]")

    # Show help
    console.print(f"[dim italic]{help_text}[/dim italic]")

    # Prompt for input
    value = Prompt.ask(
        f"[cyan]{prompt}[/cyan]",
        default=default_str if default_str else (", ".join(existing) if existing else "")
    )

    # Parse comma-separated list
    if not value or value.strip() == "":
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def _prompt_single_field(
    prompt: str,
    default: str,
    existing: Optional[str],
    help_text: str,
    skip_existing: bool
) -> str:
    """
    Prompt for a single field.

    Args:
        prompt: Field prompt
        default: Default suggestion
        existing: Existing value (if any)
        help_text: Help text
        skip_existing: Skip if existing has value

    Returns:
        Field value
    """
    # Skip if existing has value
    if skip_existing and existing:
        console.print(f"[dim]{prompt}[/dim] [green](using existing)[/green]")
        return existing

    # Show existing value
    if existing:
        console.print(f"[dim]Current: {existing}[/dim]")

    # Show help
    console.print(f"[dim italic]{help_text}[/dim italic]")

    # Prompt for input
    value = Prompt.ask(
        f"[cyan]{prompt}[/cyan]",
        default=existing if existing else default
    )

    return value.strip() if value else ""


def _suggest_end_users(work_item) -> List[str]:
    """Suggest end users based on work item type."""
    suggestions = {
        'feature': ["End users", "Customers"],
        'bugfix': ["Affected users"],
        'infrastructure': ["Development team", "DevOps"],
        'research': ["Technical team", "Stakeholders"],
        'documentation': ["Developers", "Users"],
        'security': ["All users", "Security team"],
    }
    return suggestions.get(work_item.type.value, ["End users"])


def _suggest_implementers(db: DatabaseService, work_item) -> List[str]:
    """Suggest implementers from tasks."""
    tasks = task_methods.list_tasks(db, work_item_id=work_item.id)
    assignees = [t.assigned_to for t in tasks if t.assigned_to]
    return list(set(assignees)) if assignees else []


def _suggest_reviewers(db: DatabaseService, work_item) -> List[str]:
    """Suggest reviewers from tasks."""
    tasks = task_methods.list_tasks(db, work_item_id=work_item.id)
    reviewers = [t.reviewed_by for t in tasks if hasattr(t, 'reviewed_by') and t.reviewed_by]
    return list(set(reviewers)) if reviewers else []


def _extract_from_description(description: str) -> List[str]:
    """Extract key points from description."""
    if not description or len(description) < 10:
        return []

    # Simple extraction - take first sentence or first 100 chars
    first_part = description.split('.')[0].strip()
    if len(first_part) > 100:
        first_part = first_part[:100] + "..."

    return [first_part] if first_part else []


def _suggest_deadline(work_item) -> str:
    """Suggest deadline based on work item."""
    if hasattr(work_item, 'target_date') and work_item.target_date:
        return work_item.target_date.strftime("%Y-%m-%d")
    return ""


def _calculate_confidence(six_w: UnifiedSixW) -> float:
    """
    Calculate confidence score based on completeness.

    Scoring:
    - Essential fields (WHO/WHAT): 60% weight
    - Context fields (WHERE/WHEN): 20% weight
    - Value fields (WHY/HOW): 20% weight

    Returns:
        Confidence score 0.0-1.0
    """
    score = 0.0

    # Essential fields (60%)
    who_score = 0.0
    if six_w.end_users: who_score += 0.33
    if six_w.implementers: who_score += 0.34
    if six_w.reviewers: who_score += 0.33

    what_score = 0.0
    if six_w.functional_requirements: what_score += 0.4
    if six_w.technical_constraints: what_score += 0.3
    if six_w.acceptance_criteria: what_score += 0.3

    score += (who_score * 0.3) + (what_score * 0.3)  # 60% total

    # Context fields (20%)
    where_score = 0.0
    if six_w.affected_services: where_score += 0.33
    if six_w.repositories: where_score += 0.33
    if six_w.deployment_targets: where_score += 0.34

    when_score = 0.0
    if six_w.deadline: when_score += 0.5
    if six_w.dependencies_timeline: when_score += 0.5

    score += (where_score * 0.1) + (when_score * 0.1)  # 20% total

    # Value fields (20%)
    why_score = 0.0
    if six_w.business_value: why_score += 0.5
    if six_w.risk_if_delayed: why_score += 0.5

    how_score = 0.0
    if six_w.suggested_approach: how_score += 0.5
    if six_w.existing_patterns: how_score += 0.5

    score += (why_score * 0.1) + (how_score * 0.1)  # 20% total

    return min(score, 1.0)


def _show_summary(six_w: UnifiedSixW, confidence: float, confidence_band: ConfidenceBand):
    """Show summary of populated context."""
    table = Table(title="📊 Context Summary", show_header=True, header_style="bold cyan")
    table.add_column("Dimension", style="cyan")
    table.add_column("Fields Populated", justify="right")
    table.add_column("Status")

    # WHO
    who_count = sum([
        1 if six_w.end_users else 0,
        1 if six_w.implementers else 0,
        1 if six_w.reviewers else 0
    ])
    who_status = "✓" if who_count >= 2 else "⚠"
    table.add_row("WHO", f"{who_count}/3", who_status)

    # WHAT
    what_count = sum([
        1 if six_w.functional_requirements else 0,
        1 if six_w.technical_constraints else 0,
        1 if six_w.acceptance_criteria else 0
    ])
    what_status = "✓" if what_count >= 2 else "⚠"
    table.add_row("WHAT", f"{what_count}/3", what_status)

    # WHERE
    where_count = sum([
        1 if six_w.affected_services else 0,
        1 if six_w.repositories else 0,
        1 if six_w.deployment_targets else 0
    ])
    where_status = "✓" if where_count >= 1 else "○"
    table.add_row("WHERE", f"{where_count}/3", where_status)

    # WHEN
    when_count = sum([
        1 if six_w.deadline else 0,
        1 if six_w.dependencies_timeline else 0
    ])
    when_status = "✓" if when_count >= 1 else "○"
    table.add_row("WHEN", f"{when_count}/2", when_status)

    # WHY
    why_count = sum([
        1 if six_w.business_value else 0,
        1 if six_w.risk_if_delayed else 0
    ])
    why_status = "✓" if why_count >= 1 else "○"
    table.add_row("WHY", f"{why_count}/2", why_status)

    # HOW
    how_count = sum([
        1 if six_w.suggested_approach else 0,
        1 if six_w.existing_patterns else 0
    ])
    how_status = "✓" if how_count >= 1 else "○"
    table.add_row("HOW", f"{how_count}/2", how_status)

    console.print()
    console.print(table)

    # Overall confidence
    band_color = {
        "RED": "red",
        "YELLOW": "yellow",
        "GREEN": "green"
    }[confidence_band.value]

    console.print()
    console.print(
        f"[bold]Overall Confidence:[/bold] "
        f"[{band_color}]{confidence:.0%} ({confidence_band.value})[/{band_color}]"
    )
