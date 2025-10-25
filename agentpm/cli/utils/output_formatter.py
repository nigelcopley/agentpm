"""
Output formatting utilities for CLI commands.

Provides consistent, rich formatting for success/error messages.
"""

from typing import List
from agentpm.core.services.init_orchestrator import InitResult


def format_success_output(result: InitResult) -> str:
    """
    Format initialization success output.

    Args:
        result: InitResult with success status

    Returns:
        Formatted success message
    """
    lines = [
        "\n✅ [green]Project initialized successfully![/green]\n",
        f"📦 [cyan]Project:[/cyan] {result.project_name}",
        f"🆔 [cyan]Project ID:[/cyan] {result.project_id}",
        f"💾 [cyan]Database:[/cyan] {result.database_path}",
        f"📋 [cyan]Rules:[/cyan] {result.rules_loaded} loaded",
    ]

    # Add technologies if detected
    if result.technologies_detected:
        tech_list = ", ".join(result.technologies_detected)
        lines.append(f"🔍 [cyan]Technologies:[/cyan] {tech_list}")
    else:
        lines.append("🔍 [cyan]Technologies:[/cyan] None detected (generic project)")

    lines.append("")

    # Add warnings if any
    if result.warnings:
        lines.append("⚠️  [yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            lines.append(f"  • {warning}")
        lines.append("")

    # Add next steps
    lines.extend([
        "🚀 [cyan]Next steps:[/cyan]",
        "  1. Generate agent files: [green]apm agents generate --all[/green]",
        "  2. View project status: [green]apm status[/green]",
        "  3. Create work item: [green]apm work-item create \"My Feature\"[/green]",
        "  4. Get help: [green]apm --help[/green]",
        ""
    ])

    return "\n".join(lines)


def format_error_output(result: InitResult) -> str:
    """
    Format initialization error output.

    Args:
        result: InitResult with failure status

    Returns:
        Formatted error message
    """
    lines = [
        "\n❌ [red]Initialization failed[/red]\n"
    ]

    # Add errors
    if result.errors:
        lines.append("[red]Errors:[/red]")
        for error in result.errors:
            lines.append(f"  • {error}")
        lines.append("")

    # Add warnings if any
    if result.warnings:
        lines.append("[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            lines.append(f"  • {warning}")
        lines.append("")

    # Add help
    lines.extend([
        "💡 [cyan]For help:[/cyan]",
        "  • Check logs: [dim].agentpm/logs/agentpm.log[/dim]",
        "  • Run diagnostic: [green]apm repair[/green]",
        "  • Get help: [green]apm --help[/green]",
        ""
    ])

    return "\n".join(lines)


def format_progress_message(message: str, step: int, total: int) -> str:
    """
    Format progress message with step indicator.

    Args:
        message: Progress message
        step: Current step number
        total: Total steps

    Returns:
        Formatted progress message
    """
    return f"[{step}/{total}] {message}"
