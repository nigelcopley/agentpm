"""
Standardized error formatting and user guidance

Provides consistent error messages with helpful suggestions across all CLI commands.
"""

from typing import Optional, List, Dict, Any
from rich.console import Console
import click


def show_not_found_error(
    console: Console,
    entity_type: str,
    entity_id: int,
    list_command: str
):
    """
    Show standardized "entity not found" error with suggestion.

    Args:
        console: Rich console (use console_err for errors)
        entity_type: Type of entity (e.g., "Task", "Work item")
        entity_id: ID that was not found
        list_command: Command to list available entities

    Example:
        show_not_found_error(
            console_err,
            "Task",
            999,
            "apm task list"
        )
    """
    console.print(f"\n❌ [red]{entity_type} not found:[/red] ID {entity_id}\n")
    console.print(f"💡 [yellow]List {entity_type.lower()}s with:[/yellow]")
    console.print(f"   {list_command}\n")
    raise click.Abort()


def show_validation_error(
    console: Console,
    error_message: str,
    suggestions: Optional[List[str]] = None,
    context: Optional[str] = None
):
    """
    Show validation error with helpful suggestions.

    Args:
        console: Rich console (use console_err for errors)
        error_message: Main error message
        suggestions: Optional list of suggestions to fix the error
        context: Optional additional context

    Example:
        show_validation_error(
            console_err,
            "IMPLEMENTATION tasks limited to 4.0 hours (you specified 5.0h)",
            suggestions=[
                "Reduce effort to ≤4h for implementation tasks",
                "Break into 2 tasks of ~2.5h each"
            ],
            context="Time-boxing enforces proper task decomposition"
        )
    """
    console.print(f"\n❌ [red]Validation Error:[/red] {error_message}")

    if context:
        console.print(f"\n[dim]ℹ️  {context}[/dim]")

    if suggestions:
        console.print(f"\n💡 [yellow]Suggestions:[/yellow]")
        for suggestion in suggestions:
            console.print(f"   • {suggestion}")

    console.print()
    raise click.Abort()


def show_workflow_error(
    console: Console,
    error_message: str,
    current_status: str,
    attempted_status: str,
    reason: str,
    fix_commands: Optional[List[str]] = None
):
    """
    Show workflow transition error with state information.

    Args:
        console: Rich console (use console_err for errors)
        error_message: Main error message
        current_status: Current task/work item status
        attempted_status: Status that was attempted
        reason: Why the transition was blocked
        fix_commands: Optional commands to fix the issue

    Example:
        show_workflow_error(
            console_err,
            "Cannot start task",
            current_status="proposed",
            attempted_status="in_progress",
            reason="Task must be validated and accepted first",
            fix_commands=[
                "apm task show 5  # Check quality gates",
                "# Complete validation requirements first"
            ]
        )
    """
    console.print(f"\n❌ [red]{error_message}[/red]")
    console.print(f"\n⚠️  [yellow]Quality gate blocked this transition[/yellow]")
    console.print(f"   Current status: {current_status}")
    console.print(f"   Attempted: → {attempted_status}")
    console.print(f"   Reason: {reason}")

    if fix_commands:
        console.print(f"\n💡 [cyan]To proceed:[/cyan]")
        for cmd in fix_commands:
            if cmd.startswith('#'):
                console.print(f"   {cmd}")
            else:
                console.print(f"   {cmd}")

    console.print()
    raise click.Abort()


def show_dependency_error(
    console: Console,
    task_id: int,
    task_name: str,
    blocking_dependencies: List[Dict[str, Any]],
    error_type: str = "dependencies"
):
    """
    Show dependency-related error (blocked by dependencies or blockers).

    Args:
        console: Rich console (use console_err for errors)
        task_id: Task ID being blocked
        task_name: Task name
        blocking_dependencies: List of blocking items with details
        error_type: Type of error ("dependencies" or "blockers")

    Example:
        show_dependency_error(
            console_err,
            5,
            "Implement OAuth2",
            [{"id": 2, "name": "Design schema", "status": "in_progress"}],
            error_type="dependencies"
        )
    """
    console.print(f"\n❌ [red]Cannot start task:[/red] #{task_id} '{task_name}'")
    console.print(f"\n⚠️  Blocked by incomplete {error_type}:")

    for item in blocking_dependencies:
        console.print(f"   • Task #{item['id']} '{item['name']}' (status: {item['status']})")

    console.print(f"\n💡 [cyan]Complete blocking tasks first:[/cyan]")
    for item in blocking_dependencies:
        console.print(f"   apm task show {item['id']}")

    console.print()
    raise click.Abort()


def show_circular_dependency_error(
    console: Console,
    task_id: int,
    depends_on_task_id: int
):
    """
    Show circular dependency error with visualization.

    Args:
        console: Rich console (use console_err for errors)
        task_id: Task trying to add dependency
        depends_on_task_id: Prerequisite task that creates cycle

    Example:
        show_circular_dependency_error(console_err, 5, 2)
    """
    console.print(f"\n❌ [red]Circular dependency detected![/red]")
    console.print(f"   Adding this dependency would create a cycle")
    console.print(f"\n💡 [yellow]Dependency chain would be circular:[/yellow]")
    console.print(f"   Task #{task_id} → Task #{depends_on_task_id} → ... → Task #{task_id}")
    console.print(f"\n   Break the cycle by removing a dependency in the chain\n")
    raise click.Abort()


def show_missing_option_error(
    console: Console,
    option_name: str,
    examples: List[str]
):
    """
    Show error for missing required option with examples.

    Args:
        console: Rich console (use console_err for errors)
        option_name: Name of missing option
        examples: Example commands showing correct usage

    Example:
        show_missing_option_error(
            console_err,
            "--task or --external",
            [
                "apm task add-blocker 5 --task 3",
                'apm task add-blocker 5 --external "Waiting on approval"'
            ]
        )
    """
    console.print(f"\n❌ [red]Must specify {option_name}[/red]\n")
    console.print("💡 Examples:")
    for example in examples:
        console.print(f"   {example}")
    console.print()
    raise click.Abort()


def show_quality_gate_info(
    console: Console,
    work_item_type: str,
    required_tasks: List[str],
    forbidden_tasks: Optional[List[str]] = None
):
    """
    Show quality gate requirements for work item type.

    Args:
        console: Rich console instance
        work_item_type: Type of work item (e.g., "FEATURE")
        required_tasks: List of required task types
        forbidden_tasks: Optional list of forbidden task types

    Example:
        show_quality_gate_info(
            console,
            "FEATURE",
            ["DESIGN", "IMPLEMENTATION", "TESTING", "DOCUMENTATION"]
        )
    """
    console.print(f"\n📋 [cyan]Quality gates for {work_item_type} work items:[/cyan]")

    if required_tasks:
        console.print("   Required tasks:")
        for task_type in required_tasks:
            console.print(f"   • {task_type}")

    if forbidden_tasks:
        console.print("   ⚠️  Forbidden tasks:")
        for task_type in forbidden_tasks:
            console.print(f"   • {task_type}")

    console.print()


def format_error_with_code(error: Exception, error_code: Optional[str] = None) -> str:
    """
    Format exception with optional error code for machine-readable parsing.

    Args:
        error: Exception instance
        error_code: Optional error code (e.g., "ERR_VALIDATION_001")

    Returns:
        Formatted error string

    Example:
        msg = format_error_with_code(
            ValueError("Invalid input"),
            "ERR_VAL_001"
        )
        # Returns: "[ERR_VAL_001] Invalid input"
    """
    error_msg = str(error)
    if error_code:
        return f"[{error_code}] {error_msg}"
    return error_msg
