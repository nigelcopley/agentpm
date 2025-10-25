"""
Progress indicators and status feedback for long-running CLI operations

Provides standardized progress bars, spinners, and status updates
for operations like project initialization, context generation, and analysis.
"""

from typing import Optional, Callable, Any, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from contextlib import contextmanager


@contextmanager
def init_progress(console: Console, total_steps: int = 5):
    """
    Context manager for project initialization progress.

    Provides professional multi-step progress display for init operations.

    Args:
        console: Rich console instance
        total_steps: Total number of initialization steps

    Yields:
        Progress instance with preconfigured columns

    Example:
        with init_progress(console, total_steps=5) as progress:
            task = progress.add_task("Initializing...", total=5)

            progress.update(task, advance=1, description="📁 Creating directories...")
            # ... do work ...

            progress.update(task, advance=1, description="🗄️  Initializing database...")
            # ... do work ...
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False  # Keep visible after completion
    ) as progress:
        yield progress


@contextmanager
def analysis_progress(console: Console, description: str = "Analyzing project..."):
    """
    Context manager for analysis/detection operations with spinner.

    Args:
        console: Rich console instance
        description: Progress description

    Yields:
        Progress task ID for updates

    Example:
        with analysis_progress(console, "Detecting frameworks...") as progress_task:
            # Long-running analysis
            results = detect_frameworks(project_path)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        console=console,
        transient=True  # Remove when done
    ) as progress:
        task_id = progress.add_task(description, total=None)
        yield task_id


def show_operation_status(
    console: Console,
    operation: str,
    status: str,
    details: Optional[str] = None,
    success: bool = True
):
    """
    Show operation status with consistent formatting.

    Args:
        console: Rich console instance
        operation: Operation name (e.g., "Database initialized")
        status: Status message (e.g., "created 10 tables")
        details: Optional additional details
        success: Whether operation succeeded

    Example:
        show_operation_status(
            console,
            "Database initialized",
            "10 tables created",
            details="/path/to/db",
            success=True
        )
    """
    icon = "✅" if success else "❌"
    color = "green" if success else "red"

    console.print(f"\n{icon} [bold {color}]{operation}[/bold {color}]")
    if status:
        console.print(f"   {status}")
    if details:
        console.print(f"   [dim]{details}[/dim]")


def show_next_steps(console: Console, steps: List[str], header: str = "Next steps:"):
    """
    Display next steps after operation completion.

    Args:
        console: Rich console instance
        steps: List of command suggestions
        header: Header text (default: "Next steps:")

    Example:
        show_next_steps(console, [
            "apm work-item create 'Feature name'",
            "apm status  # View dashboard"
        ])
    """
    console.print(f"\n📚 [cyan]{header}[/cyan]")
    for step in steps:
        if step.startswith('#'):  # Comment line
            console.print(f"   {step}")
        else:
            console.print(f"   {step}")
    console.print()


def show_multi_step_completion(
    console: Console,
    completed_steps: List[str],
    title: str = "Completed Steps"
):
    """
    Show completion summary for multi-step operations.

    Args:
        console: Rich console instance
        completed_steps: List of completed step descriptions
        title: Summary title

    Example:
        show_multi_step_completion(console, [
            "Database schema initialized",
            "Project metadata created",
            "Contexts generated"
        ])
    """
    console.print(f"\n✅ [bold green]{title}[/bold green]")
    for step in completed_steps:
        console.print(f"   ✓ {step}")
    console.print()


class ProgressTracker:
    """
    Reusable progress tracker for multi-phase operations.

    Provides consistent progress display across different CLI commands.

    Example:
        tracker = ProgressTracker(console, total=5)
        tracker.start("Initializing project...")

        tracker.step(1, "Creating directories...")
        # ... do work ...

        tracker.step(2, "Initializing database...")
        # ... do work ...

        tracker.complete("Project initialized!")
    """

    def __init__(self, console: Console, total: int):
        """
        Initialize progress tracker.

        Args:
            console: Rich console instance
            total: Total number of steps
        """
        self.console = console
        self.total = total
        self.current = 0
        self.progress = None
        self.task_id = None

    def start(self, description: str = "Starting..."):
        """Start progress tracking with initial description."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False
        )
        self.progress.__enter__()
        self.task_id = self.progress.add_task(description, total=self.total)

    def step(self, step_number: int, description: str):
        """
        Update progress to specific step.

        Args:
            step_number: Current step number (1-indexed)
            description: Step description
        """
        if self.progress and self.task_id is not None:
            advance = step_number - self.current
            self.current = step_number
            self.progress.update(
                self.task_id,
                advance=advance,
                description=description
            )

    def complete(self, final_message: str = "Complete!"):
        """Complete progress and show final message."""
        if self.progress and self.task_id is not None:
            remaining = self.total - self.current
            if remaining > 0:
                self.progress.update(self.task_id, advance=remaining, description=final_message)
            self.progress.__exit__(None, None, None)
            self.progress = None


def format_time_estimate(hours: float) -> str:
    """
    Format time estimate in human-readable form.

    Args:
        hours: Time in hours

    Returns:
        Formatted string (e.g., "2.5h", "30min", "6h")

    Example:
        format_time_estimate(0.5)  # "30min"
        format_time_estimate(2.5)  # "2.5h"
        format_time_estimate(8.0)  # "8h"
    """
    if hours < 1.0:
        minutes = int(hours * 60)
        return f"{minutes}min"
    elif hours == int(hours):
        return f"{int(hours)}h"
    else:
        return f"{hours}h"
