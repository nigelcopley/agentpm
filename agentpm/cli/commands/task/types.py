"""
Task Types Command

Exposes task-related Pydantic models and enums via CLI.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agentpm.core.database.enums import TaskType, TaskStatus, EnforcementLevel


@click.command()
@click.option('--type', 'type_filter', 
              type=click.Choice(['task-type', 'task-status', 'enforcement-level', 'effort-limits', 'all']),
              default='all',
              help='Filter which types to display')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'list', 'json']),
              default='table',
              help='Output format')
@click.pass_context
def types(ctx: click.Context, type_filter: str, output_format: str):
    """
    🎯 Show available task types, statuses, and effort limits.
    
    Displays all valid values for task-related enums that can be used
    in task commands. Essential for AI agents and users to discover
    valid options without hardcoding values.
    
    \b
    Examples:
      apm task types                        # Show all types
      apm task types --type=task-type       # Show only task types
      apm task types --type=effort-limits   # Show effort limits
      apm task types --format=list          # Simple list format
    """
    console = Console()
    
    if type_filter == 'all' or type_filter == 'task-type':
        _show_task_types(console, output_format)
    
    if type_filter == 'all' or type_filter == 'task-status':
        _show_task_statuses(console, output_format)
    
    if type_filter == 'all' or type_filter == 'enforcement-level':
        _show_enforcement_levels(console, output_format)
    
    if type_filter == 'all' or type_filter == 'effort-limits':
        _show_effort_limits(console, output_format)


def _show_task_types(console: Console, output_format: str):
    """Show task types with descriptions."""
    if output_format == 'table':
        table = Table(title="🎯 Task Types", show_header=True, header_style="bold blue")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        labels = TaskType.labels()
        for task_type in TaskType:
            table.add_row(task_type.value, labels.get(task_type.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(TaskType)} task types[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("🎯 Task Types", style="bold blue"))
        labels = TaskType.labels()
        for task_type in TaskType:
            console.print(f"  • {task_type.value}: {labels.get(task_type.value, '')}")
    
    elif output_format == 'json':
        import json
        labels = TaskType.labels()
        types_data = {
            "task_types": [
                {"value": task_type.value, "description": labels.get(task_type.value, "")}
                for task_type in TaskType
            ]
        }
        console.print(json.dumps(types_data, indent=2))


def _show_task_statuses(console: Console, output_format: str):
    """Show task statuses."""
    if output_format == 'table':
        table = Table(title="🎯 Task Statuses", show_header=True, header_style="bold blue")
        table.add_column("Status", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        status_descriptions = {
            TaskStatus.PROPOSED.value: "Initial proposal, not yet validated",
            TaskStatus.VALIDATED.value: "Validated and ready for acceptance",
            TaskStatus.ACCEPTED.value: "Accepted and ready to start",
            TaskStatus.IN_PROGRESS.value: "Currently being worked on",
            TaskStatus.REVIEW.value: "Under review",
            TaskStatus.COMPLETED.value: "Completed successfully",
            TaskStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        
        for status in TaskStatus:
            table.add_row(status.value, status_descriptions.get(status.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(TaskStatus)} task statuses[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("🎯 Task Statuses", style="bold blue"))
        status_descriptions = {
            TaskStatus.PROPOSED.value: "Initial proposal, not yet validated",
            TaskStatus.VALIDATED.value: "Validated and ready for acceptance",
            TaskStatus.ACCEPTED.value: "Accepted and ready to start",
            TaskStatus.IN_PROGRESS.value: "Currently being worked on",
            TaskStatus.REVIEW.value: "Under review",
            TaskStatus.COMPLETED.value: "Completed successfully",
            TaskStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        for status in TaskStatus:
            console.print(f"  • {status.value}: {status_descriptions.get(status.value, '')}")
    
    elif output_format == 'json':
        import json
        status_descriptions = {
            TaskStatus.PROPOSED.value: "Initial proposal, not yet validated",
            TaskStatus.VALIDATED.value: "Validated and ready for acceptance",
            TaskStatus.ACCEPTED.value: "Accepted and ready to start",
            TaskStatus.IN_PROGRESS.value: "Currently being worked on",
            TaskStatus.REVIEW.value: "Under review",
            TaskStatus.COMPLETED.value: "Completed successfully",
            TaskStatus.CANCELLED.value: "Cancelled or abandoned",
        }
        statuses_data = {
            "task_statuses": [
                {"value": status.value, "description": status_descriptions.get(status.value, "")}
                for status in TaskStatus
            ]
        }
        console.print(json.dumps(statuses_data, indent=2))


def _show_enforcement_levels(console: Console, output_format: str):
    """Show enforcement levels."""
    if output_format == 'table':
        table = Table(title="🎯 Enforcement Levels", show_header=True, header_style="bold blue")
        table.add_column("Level", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        enforcement_descriptions = {
            EnforcementLevel.BLOCK.value: "Hard stop, operation fails",
            EnforcementLevel.LIMIT.value: "Soft limit, warning issued",
            EnforcementLevel.GUIDE.value: "Suggestion, no enforcement",
            EnforcementLevel.ENHANCE.value: "Quality improvement suggestion",
        }
        
        for level in EnforcementLevel:
            table.add_row(level.value, enforcement_descriptions.get(level.value, ""))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(EnforcementLevel)} enforcement levels[/dim]")
    
    elif output_format == 'list':
        console.print(Panel("🎯 Enforcement Levels", style="bold blue"))
        enforcement_descriptions = {
            EnforcementLevel.BLOCK.value: "Hard stop, operation fails",
            EnforcementLevel.LIMIT.value: "Soft limit, warning issued",
            EnforcementLevel.GUIDE.value: "Suggestion, no enforcement",
            EnforcementLevel.ENHANCE.value: "Quality improvement suggestion",
        }
        for level in EnforcementLevel:
            console.print(f"  • {level.value}: {enforcement_descriptions.get(level.value, '')}")
    
    elif output_format == 'json':
        import json
        enforcement_descriptions = {
            EnforcementLevel.BLOCK.value: "Hard stop, operation fails",
            EnforcementLevel.LIMIT.value: "Soft limit, warning issued",
            EnforcementLevel.GUIDE.value: "Suggestion, no enforcement",
            EnforcementLevel.ENHANCE.value: "Quality improvement suggestion",
        }
        levels_data = {
            "enforcement_levels": [
                {"value": level.value, "description": enforcement_descriptions.get(level.value, "")}
                for level in EnforcementLevel
            ]
        }
        console.print(json.dumps(levels_data, indent=2))


def _show_effort_limits(console: Console, output_format: str):
    """Show effort limits for different task types."""
    if output_format == 'table':
        table = Table(title="🎯 Task Effort Limits", show_header=True, header_style="bold blue")
        table.add_column("Task Type", style="cyan", no_wrap=True)
        table.add_column("Max Hours", style="yellow", no_wrap=True)
        table.add_column("Description", style="white")
        
        effort_limits = {
            TaskType.IMPLEMENTATION.value: (4, "Code changes (STRICT limit)"),
            TaskType.DESIGN.value: (8, "Architecture/design work"),
            TaskType.TESTING.value: (6, "Test coverage and validation"),
            TaskType.DOCUMENTATION.value: (6, "Documentation and guides"),
            TaskType.BUGFIX.value: (4, "Bug fixes and patches"),
            TaskType.REFACTORING.value: (6, "Code improvement without feature changes"),
            TaskType.DEPLOYMENT.value: (8, "Deployment and release activities"),
            TaskType.REVIEW.value: (4, "Code review and quality checks"),
            TaskType.ANALYSIS.value: (6, "Investigation and research"),
            TaskType.RESEARCH.value: (8, "Spike and proof of concept work"),
            TaskType.MAINTENANCE.value: (4, "Ongoing support activities"),
            TaskType.OPTIMIZATION.value: (6, "Performance and security optimization"),
            TaskType.INTEGRATION.value: (8, "System integration work"),
            TaskType.TRAINING.value: (4, "Learning and training activities"),
            TaskType.MEETING.value: (2, "Meetings and discussions"),
            TaskType.PLANNING.value: (6, "Task and project planning"),
            TaskType.DEPENDENCY.value: (2, "Dependency management"),
            TaskType.BLOCKER.value: (4, "Blocker resolution"),
            TaskType.SIMPLE.value: (1, "Quick tasks under 1 hour"),
            TaskType.OTHER.value: (4, "Miscellaneous tasks"),
        }
        
        for task_type, (max_hours, description) in effort_limits.items():
            table.add_row(task_type, str(max_hours), description)
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(effort_limits)} task types with effort limits[/dim]")
        console.print("[yellow]Note: IMPLEMENTATION tasks have a STRICT 4-hour limit enforced by quality gates[/yellow]")
    
    elif output_format == 'list':
        console.print(Panel("🎯 Task Effort Limits", style="bold blue"))
        effort_limits = {
            TaskType.IMPLEMENTATION.value: (4, "Code changes (STRICT limit)"),
            TaskType.DESIGN.value: (8, "Architecture/design work"),
            TaskType.TESTING.value: (6, "Test coverage and validation"),
            TaskType.DOCUMENTATION.value: (6, "Documentation and guides"),
            TaskType.BUGFIX.value: (4, "Bug fixes and patches"),
            TaskType.REFACTORING.value: (6, "Code improvement without feature changes"),
            TaskType.DEPLOYMENT.value: (8, "Deployment and release activities"),
            TaskType.REVIEW.value: (4, "Code review and quality checks"),
            TaskType.ANALYSIS.value: (6, "Investigation and research"),
            TaskType.RESEARCH.value: (8, "Spike and proof of concept work"),
            TaskType.MAINTENANCE.value: (4, "Ongoing support activities"),
            TaskType.OPTIMIZATION.value: (6, "Performance and security optimization"),
            TaskType.INTEGRATION.value: (8, "System integration work"),
            TaskType.TRAINING.value: (4, "Learning and training activities"),
            TaskType.MEETING.value: (2, "Meetings and discussions"),
            TaskType.PLANNING.value: (6, "Task and project planning"),
            TaskType.DEPENDENCY.value: (2, "Dependency management"),
            TaskType.BLOCKER.value: (4, "Blocker resolution"),
            TaskType.SIMPLE.value: (1, "Quick tasks under 1 hour"),
            TaskType.OTHER.value: (4, "Miscellaneous tasks"),
        }
        for task_type, (max_hours, description) in effort_limits.items():
            console.print(f"  • {task_type}: {max_hours}h - {description}")
        console.print("\n[yellow]Note: IMPLEMENTATION tasks have a STRICT 4-hour limit enforced by quality gates[/yellow]")
    
    elif output_format == 'json':
        import json
        effort_limits = {
            TaskType.IMPLEMENTATION.value: (4, "Code changes (STRICT limit)"),
            TaskType.DESIGN.value: (8, "Architecture/design work"),
            TaskType.TESTING.value: (6, "Test coverage and validation"),
            TaskType.DOCUMENTATION.value: (6, "Documentation and guides"),
            TaskType.BUGFIX.value: (4, "Bug fixes and patches"),
            TaskType.REFACTORING.value: (6, "Code improvement without feature changes"),
            TaskType.DEPLOYMENT.value: (8, "Deployment and release activities"),
            TaskType.REVIEW.value: (4, "Code review and quality checks"),
            TaskType.ANALYSIS.value: (6, "Investigation and research"),
            TaskType.RESEARCH.value: (8, "Spike and proof of concept work"),
            TaskType.MAINTENANCE.value: (4, "Ongoing support activities"),
            TaskType.OPTIMIZATION.value: (6, "Performance and security optimization"),
            TaskType.INTEGRATION.value: (8, "System integration work"),
            TaskType.TRAINING.value: (4, "Learning and training activities"),
            TaskType.MEETING.value: (2, "Meetings and discussions"),
            TaskType.PLANNING.value: (6, "Task and project planning"),
            TaskType.DEPENDENCY.value: (2, "Dependency management"),
            TaskType.BLOCKER.value: (4, "Blocker resolution"),
            TaskType.SIMPLE.value: (1, "Quick tasks under 1 hour"),
            TaskType.OTHER.value: (4, "Miscellaneous tasks"),
        }
        limits_data = {
            "task_effort_limits": [
                {"task_type": task_type, "max_hours": max_hours, "description": description}
                for task_type, (max_hours, description) in effort_limits.items()
            ]
        }
        console.print(json.dumps(limits_data, indent=2))

