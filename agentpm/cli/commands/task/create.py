"""
apm task create - Create new task with time-box validation
"""

import json
from copy import deepcopy

import click
from agentpm.core.database.models import Task
from agentpm.core.database.enums import TaskType, TaskStatus
from agentpm.core.database.adapters import TaskAdapter
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.cli.utils.validation import (
    get_task_type_choices,
    validate_effort_hours,
    validate_work_item_exists
)
from agentpm.cli.utils.templates import load_template


# Default time-box limits (fallback if no rules loaded)
DEFAULT_TIME_BOX_LIMITS = {
    'implementation': 4.0,
    'testing': 6.0,
    'design': 8.0,
    'analysis': 6.0,
    'documentation': 4.0,
    'review': 2.0,
    'deployment': 4.0,
    'refactoring': 6.0,
    'bugfix': 4.0,
    'research': 8.0
}

TASK_TEMPLATE_BY_TYPE = {
    'implementation': 'tasks/implementation',
    'bugfix': 'tasks/bugfix',
    'testing': 'tasks/testing',
    'design': 'tasks/design',
}


@click.command()
@click.argument('name')
@click.option(
    '--work-item-id', 'work_item_id',
    type=int,
    required=False,
    help='Work item ID this task belongs to'
)
@click.option(
    '--type', 'task_type',
    type=click.Choice(get_task_type_choices(), case_sensitive=False),
    required=True,
    help='Task type (implementation, testing, design, etc.)'
)
@click.option(
    '--effort', 'effort_hours',
    type=float,
    callback=validate_effort_hours,
    help='Estimated effort in hours (max 8h, IMPLEMENTATION max 4h)'
)
@click.option(
    '--description', '-d',
    default='',
    help='Task description'
)
@click.option(
    '--priority', '-p',
    type=click.IntRange(1, 5),
    default=3,
    help='Priority (1=highest, 5=lowest)'
)
@click.option(
    '--acceptance-criteria',
    help='JSON array of acceptance criteria (e.g., \'["All tests pass", "Code coverage >90%"]\')'
)
@click.option(
    '--implementation-notes',
    help='Implementation guidance (patterns to follow, files to reference, etc.)'
)
@click.option(
    '--test-requirements',
    help='JSON object with test requirements (e.g., \'{"min_coverage": 0.95, "test_types": ["unit", "integration"]}\')'
)
@click.option(
    '--quality-template',
    default='none',
    show_default=True,
    help='Seed quality metadata from template ID. Use "auto" to pick based on task type, or "none" to disable.'
)
@click.pass_context
def create(ctx: click.Context, name: str, work_item_id: int, task_type: str, effort_hours: float,
           description: str, priority: int, acceptance_criteria: str, implementation_notes: str,
           test_requirements: str, quality_template: str):
    """
    Create new task with time-box validation.

    Supports acceptance criteria, implementation notes, and test requirements
    for comprehensive task definition.

    \b
    Time-Boxing (STRICT):
      IMPLEMENTATION tasks: ≤4 hours (forces proper decomposition)
      TESTING tasks: ≤6 hours
      DESIGN tasks: ≤8 hours

    Tasks exceeding limits will be REJECTED with guidance to break into smaller tasks.

    \b
    Examples:
      # Basic task
      apm task create "Design auth schema" --work-item-id=1 --type=design --effort=3

      # With acceptance criteria
      apm task create "Implement User model" \\
        --work-item-id=1 \\
        --type=implementation \\
        --effort=3.5 \\
        --acceptance-criteria '["User model created", "Migrations generated", "Tests passing"]'

      # With implementation notes
      apm task create "Add JWT endpoint" \\
        --work-item-id=1 \\
        --type=implementation \\
        --effort=3 \\
        --acceptance-criteria '["Returns valid JWT", "Rate limited"]' \\
        --implementation-notes "Follow src/auth/views.py pattern. Use djangorestframework-simplejwt library."

      # With test requirements
      apm task create "Write auth tests" \\
        --work-item-id=1 \\
        --type=testing \\
        --effort=4 \\
        --test-requirements '{"min_coverage": 0.95, "test_types": ["unit", "integration"]}'
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    project_id = get_current_project_id(ctx)

    task_type_enum = TaskType(task_type)

    if work_item_id is None:
        if task_type_enum != TaskType.BUGFIX:
            console.print("\n❌ [red]Missing --work-item-id:[/red] Non-bug tasks must target a specific work item.\n")
            raise click.Abort()
        backlog = wi_methods.ensure_bug_backlog(db, project_id)
        work_item_id = backlog.id
        console.print(
            f"\n🔄 [cyan]Auto-attached bugfix to continuous backlog[/cyan] "
            f"(Work Item #{work_item_id})\n"
        )
    else:
        validate_work_item_exists(db, work_item_id, ctx)

    # Time-box validation (STRICT)
    if effort_hours:
        max_hours = DEFAULT_TIME_BOX_LIMITS.get(task_type, 8.0)
        if effort_hours > max_hours:
            console.print(f"\n❌ [red]Time-box violation:[/red] {task_type.upper()} tasks limited to {max_hours}h\n")
            console.print(f"   Your estimate: {effort_hours}h (exceeds limit by {effort_hours - max_hours}h)\n")
            console.print("💡 [yellow]Solution: Break into smaller tasks:[/yellow]")
            console.print(f"   1. Create first task: ≤{max_hours}h")
            console.print(f"   2. Create additional task(s) for remaining work")
            console.print(f"\n   This enforces proper decomposition and prevents over-engineering.\n")
            raise click.Abort()

    # Parse and validate JSON inputs
    quality_metadata = {}
    template_choice = (quality_template or '').strip().lower()
    if template_choice not in ('', 'none', 'off'):
        if template_choice in ('auto', 'default'):
            template_id = TASK_TEMPLATE_BY_TYPE.get(task_type, 'tasks/generic')
        else:
            template_id = quality_template
        try:
            template_data = load_template(template_id, project_root=project_root)
        except FileNotFoundError:
            console.print(
                f"[red]❌ Error: Quality template '{template_id}' not found[/red]"
            )
            console.print("   Use `apm template list` to view available templates.")
            raise click.Abort()
        if not isinstance(template_data, dict):
            console.print(
                f"[red]❌ Error: Template '{template_id}' must be a JSON object[/red]"
            )
            raise click.Abort()
        quality_metadata = deepcopy(template_data)

    if acceptance_criteria:
        try:
            criteria = json.loads(acceptance_criteria)
            if not isinstance(criteria, list):
                console.print("[red]❌ Error: --acceptance-criteria must be a JSON array[/red]")
                raise click.Abort()
            quality_metadata['acceptance_criteria'] = criteria
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --acceptance-criteria: {e}[/red]")
            raise click.Abort()

    if implementation_notes:
        quality_metadata['implementation_notes'] = implementation_notes

    if test_requirements:
        try:
            test_req = json.loads(test_requirements)
            if not isinstance(test_req, dict):
                console.print("[red]❌ Error: --test-requirements must be a JSON object[/red]")
                raise click.Abort()
            quality_metadata['test_requirements'] = test_req
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Error: Invalid JSON in --test-requirements: {e}[/red]")
            raise click.Abort()

    # Create task with quality_metadata (as dict, not JSON string)
    task = Task(
        name=name,
        description=description,
        type=task_type_enum,
        status=TaskStatus.DRAFT,
        work_item_id=work_item_id,
        effort_hours=effort_hours,
        priority=priority,
        quality_metadata=quality_metadata if quality_metadata else None
    )

    # THREE-LAYER PATTERN: Use adapter, not direct methods call
    created_task = TaskAdapter.create(db, task)

    # Warn if template was applied with placeholder content
    if quality_metadata and '[TODO:' in json.dumps(quality_metadata):
        console.print("[yellow]⚠️  Template applied - ensure criteria match your task[/yellow]\n")

    # Success message
    console.print(f"\n✅ [green]Task created:[/green] {created_task.name}")
    console.print(f"   ID: {created_task.id}")
    console.print(f"   Type: {created_task.type.value}")
    console.print(f"   Status: {created_task.status.value}")
    if created_task.effort_hours:
        console.print(f"   Effort: {created_task.effort_hours}h")
    console.print(f"   Priority: {created_task.priority}")

    # Show new fields if provided
    if quality_metadata.get('acceptance_criteria'):
        console.print(f"   Acceptance Criteria: {len(quality_metadata['acceptance_criteria'])} items")

    if quality_metadata.get('implementation_notes'):
        console.print(f"   Implementation Notes: ✓")

    if quality_metadata.get('test_requirements'):
        console.print(f"   Test Requirements: ✓")

    console.print()

    # Show next steps
    console.print("📚 [cyan]Next steps:[/cyan]")
    console.print(f"   apm task list --work-item-id={work_item_id}  # View all tasks")
    console.print(f"   apm task start {created_task.id}              # Start working on this task")
    console.print(f"   apm work-item show {work_item_id}             # Check quality gates\n")
