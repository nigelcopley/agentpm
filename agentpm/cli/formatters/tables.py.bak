"""
Reusable table builders for CLI output

Provides standardized Rich table formatting for consistent UX across commands.
Reduces code duplication and ensures professional output quality.
"""

from typing import List, Optional, Any, Dict
from rich.table import Table
from rich.console import Console
from agentpm.core.database.models import Task, WorkItem


def build_task_table(tasks: List[Task], title: Optional[str] = None) -> Table:
    """
    Build standardized task table.

    Args:
        tasks: List of Task models
        title: Optional table title (default: "Tasks (N)")

    Returns:
        Rich Table ready for console.print()
    """
    if title is None:
        title = f"\n📋 Tasks ({len(tasks)})"

    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Effort", justify="right")
    table.add_column("WI", justify="right")

    for task in tasks:
        effort_str = f"{task.effort_hours}h" if task.effort_hours else "-"
        table.add_row(
            str(task.id),
            task.name,
            task.type.value,
            task.status.value,
            effort_str,
            str(task.work_item_id)
        )

    return table


def build_work_item_table(work_items: List[WorkItem], title: Optional[str] = None) -> Table:
    """
    Build standardized work item table.

    Args:
        work_items: List of WorkItem models
        title: Optional table title (default: "Work Items (N)")

    Returns:
        Rich Table ready for console.print()
    """
    if title is None:
        title = f"\n📋 Work Items ({len(work_items)})"

    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Priority", justify="center")

    for wi in work_items:
        table.add_row(
            str(wi.id),
            wi.name,
            wi.type.value,
            wi.status.value,
            f"P{wi.priority}"
        )

    return table


def build_dependency_table(
    dependencies: List[Any],
    tasks_lookup: Dict[int, Any],
    table_type: str = "prerequisites"
) -> Table:
    """
    Build dependency relationship table.

    Args:
        dependencies: List of dependency records
        tasks_lookup: Dictionary mapping task_id to Task model
        table_type: Type of table ("prerequisites" or "dependents")

    Returns:
        Rich Table showing dependency relationships
    """
    if table_type == "prerequisites":
        title = "⬆️  Prerequisites (must complete first)"
    else:
        title = "⬇️  Dependents (waiting on this)"

    table = Table(title=title)
    table.add_column("Task ID", style="cyan", no_wrap=True)
    table.add_column("Task Name", style="bold")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="yellow")

    for dep in dependencies:
        # Get the relevant task ID based on table type
        if table_type == "prerequisites":
            task_id = dep.depends_on_task_id
        else:
            task_id = dep.task_id

        task = tasks_lookup.get(task_id)
        if task:
            table.add_row(
                str(task_id),
                task.name,
                dep.dependency_type,
                task.status.value
            )

    return table


def build_blocker_table(
    blockers: List[Any],
    tasks_lookup: Dict[int, Any],
    count: Optional[int] = None
) -> Table:
    """
    Build blocker table showing what's blocking task completion.

    Args:
        blockers: List of blocker records
        tasks_lookup: Dictionary mapping task_id to Task model (for task blockers)
        count: Optional blocker count for title

    Returns:
        Rich Table showing blockers
    """
    title = f"{count or len(blockers)} Blocker(s)"

    table = Table(title=title)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Description", style="bold")
    table.add_column("Status", style="yellow")

    for blocker in blockers:
        # Build description based on blocker type
        if blocker.blocker_type == 'task' and blocker.blocker_task_id:
            task = tasks_lookup.get(blocker.blocker_task_id)
            desc = f"Task #{blocker.blocker_task_id}: {task.name if task else 'Unknown'}"
        else:
            desc = blocker.blocker_description or "No description"
            if blocker.blocker_reference:
                desc += f" ({blocker.blocker_reference})"

        status = "✅ Resolved" if blocker.is_resolved else "🚧 Unresolved"

        table.add_row(
            str(blocker.id),
            blocker.blocker_type,
            desc,
            status
        )

    return table


def build_generic_table(
    data: List[Dict[str, Any]],
    columns: List[Dict[str, str]],
    title: Optional[str] = None
) -> Table:
    """
    Build generic table from list of dictionaries.

    Args:
        data: List of data dictionaries
        columns: List of column definitions
                 [{"key": "id", "header": "ID", "style": "cyan"}, ...]
        title: Optional table title

    Returns:
        Rich Table populated with data

    Example:
        columns = [
            {"key": "id", "header": "ID", "style": "cyan"},
            {"key": "name", "header": "Name", "style": "bold"},
            {"key": "status", "header": "Status", "style": "yellow"}
        ]
        table = build_generic_table(data, columns, "My Data")
    """
    table = Table(title=title)

    # Add columns
    for col in columns:
        table.add_column(
            col.get("header", col["key"]),
            style=col.get("style"),
            justify=col.get("justify", "left"),
            no_wrap=col.get("no_wrap", False)
        )

    # Add rows
    for row_data in data:
        row_values = [str(row_data.get(col["key"], "")) for col in columns]
        table.add_row(*row_values)

    return table


def print_empty_state(
    console: Console,
    message: str,
    suggestion_command: str,
    suggestion_description: str = "Create one with:"
):
    """
    Print standardized empty state message with helpful next step.

    Args:
        console: Rich console instance
        message: Empty state message (e.g., "No tasks found")
        suggestion_command: Command to suggest (e.g., "apm task create ...")
        suggestion_description: Description before command (default: "Create one with:")

    Example:
        print_empty_state(
            console,
            "No tasks found",
            'apm task create "Task name" --work-item-id=1 --type=implementation'
        )
    """
    console.print(f"\nℹ️  [yellow]{message}[/yellow]\n")
    console.print(f"💡 [cyan]{suggestion_description}[/cyan]")
    console.print(f"   {suggestion_command}\n")
