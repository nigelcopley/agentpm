"""
Input Validation Utilities - CI-005 Compliance

Validates CLI inputs at the boundary before reaching business logic.
Three-layer validation strategy:
1. Click parameter validators (type, range, choice)
2. Custom callbacks (business logic, entity existence)
3. Service-level validation (database constraints, workflow rules)

Security:
- Path sanitization prevents directory traversal
- Range validation prevents overflow attacks
- Entity validation prevents injection
"""

from pathlib import Path
from typing import Optional
import click
from agentpm.core.database import DatabaseService
from agentpm.core.database.enums import TaskType, WorkItemType


# ============================================================================
# PATH VALIDATION (Security: CI-005)
# ============================================================================

def validate_project_path(ctx, param, value) -> Path:
    """
    Validate project path exists and is a directory.

    Security checks:
    - Resolves symlinks and normalizes path
    - Prevents directory traversal (..)
    - Blocks sensitive system paths
    - Validates existence and directory type

    Args:
        ctx: Click context
        param: Click parameter
        value: Path string to validate

    Returns:
        Validated and normalized Path object

    Raises:
        click.BadParameter: If path is invalid or suspicious
    """
    if not value:
        return Path.cwd()

    try:
        path = Path(value).resolve()  # Resolve symlinks, normalize
    except Exception as e:
        raise click.BadParameter(f"Invalid path: {e}")

    # Security: Check existence
    if not path.exists():
        raise click.BadParameter(f"Path does not exist: {value}")

    # Security: Verify it's a directory
    if not path.is_dir():
        raise click.BadParameter(f"Not a directory: {value}")

    # Security: Block suspicious patterns
    path_str = str(path)
    if '..' in path_str or path_str.startswith('/etc') or path_str.startswith('/sys'):
        raise click.BadParameter(f"Suspicious path detected: {value}")

    return path


# ============================================================================
# NUMERIC VALIDATION
# ============================================================================

def validate_effort_hours(ctx, param, value) -> Optional[float]:
    """
    Validate effort hours within acceptable range.

    Enforces absolute maximum of 8 hours per database constraint.
    Prevents negative values and overflow attacks.

    Args:
        ctx: Click context
        param: Click parameter
        value: Effort hours (float or None)

    Returns:
        Validated effort hours or None

    Raises:
        click.BadParameter: If effort is invalid
    """
    if value is None:
        return None

    if value < 0:
        raise click.BadParameter("Effort cannot be negative")

    if value > 8:
        raise click.BadParameter(
            "Effort cannot exceed 8 hours (database constraint).\n"
            "💡 For larger tasks, break into multiple sub-tasks."
        )

    return value


def validate_priority(ctx, param, value) -> int:
    """
    Validate priority within 1-5 range.

    Args:
        ctx: Click context
        param: Click parameter
        value: Priority (1-5, or None for default)

    Returns:
        Validated priority (defaults to 3 if None)

    Raises:
        click.BadParameter: If priority out of range
    """
    if value is None:
        return 3  # Default priority

    if not (1 <= value <= 5):
        raise click.BadParameter(
            "Priority must be between 1-5\n"
            "  1 = Highest (critical)\n"
            "  3 = Medium (default)\n"
            "  5 = Lowest (nice-to-have)"
        )

    return value


# ============================================================================
# ENTITY EXISTENCE VALIDATION (CI-001 Compliance)
# ============================================================================

def validate_agent_exists(db: DatabaseService, project_id: int, agent_role: str, ctx: click.Context) -> bool:
    """
    Validate agent exists in database (CI-001 compliance).

    Required by CI-001 gate before assigning tasks to agents.
    Prevents orphaned task assignments.

    Args:
        db: DatabaseService instance
        project_id: Project ID
        agent_role: Agent role identifier to validate
        ctx: Click context for console access

    Returns:
        True if agent exists

    Raises:
        click.Abort: If agent doesn't exist (with helpful suggestions)

    Example:
        ```python
        if not validate_agent_exists(db, project_id, "aipm-developer", ctx):
            # Won't reach here - raises click.Abort
            pass
        ```
    """
    from agentpm.core.database.methods import agents as agent_methods

    console_err = ctx.obj['console_err']

    # Query database for agent
    agent = agent_methods.get_agent_by_role(db, project_id, agent_role)

    if not agent:
        console_err.print(f"\n❌ [red]Agent not found:[/red] {agent_role}\n")
        console_err.print("💡 [yellow]Available agents:[/yellow]")

        # Show available agents
        agents = agent_methods.list_agents(db)
        if agents:
            for a in agents[:10]:  # Show first 10
                console_err.print(f"   • {a.role}")
        else:
            console_err.print("   (No agents registered)")

        console_err.print("\n📚 [cyan]Or add agent first with:[/cyan]")
        console_err.print(f"   apm agent add {agent_role}")

        raise click.Abort()

    return True


def validate_work_item_exists(db: DatabaseService, work_item_id: int, ctx: click.Context) -> bool:
    """
    Validate work item exists in database.

    Args:
        db: DatabaseService instance
        work_item_id: Work item ID to validate
        ctx: Click context

    Returns:
        True if work item exists

    Raises:
        click.Abort: If work item doesn't exist
    """
    from agentpm.core.database.methods import work_items as wi_methods

    console_err = ctx.obj['console_err']

    work_item = wi_methods.get_work_item(db, work_item_id)

    if not work_item:
        console_err.print(f"\n❌ [red]Work item not found:[/red] ID {work_item_id}\n")
        console_err.print("💡 [yellow]List work items with:[/yellow]")
        console_err.print("   apm work-item list")
        raise click.Abort()

    return True


def validate_task_exists(db: DatabaseService, task_id: int, ctx: click.Context) -> bool:
    """
    Validate task exists in database.

    Args:
        db: DatabaseService instance
        task_id: Task ID to validate
        ctx: Click context

    Returns:
        True if task exists

    Raises:
        click.Abort: If task doesn't exist
    """
    from agentpm.core.database.methods import tasks as task_methods

    console_err = ctx.obj['console_err']

    task = task_methods.get_task(db, task_id)

    if not task:
        console_err.print(f"\n❌ [red]Task not found:[/red] ID {task_id}\n")
        console_err.print("💡 [yellow]List tasks with:[/yellow]")
        console_err.print("   apm task list")
        raise click.Abort()

    return True


# ============================================================================
# ENUM VALIDATION
# ============================================================================

def get_task_type_choices() -> list[str]:
    """Get valid task type choices for Click"""
    return [t.value for t in TaskType]


def get_work_item_type_choices() -> list[str]:
    """Get valid work item type choices for Click"""
    return [t.value for t in WorkItemType]
