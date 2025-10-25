"""
apm status - Project status dashboard

Displays comprehensive project health with Rich formatting:
- Project overview (name, path, database stats)
- Work items summary (by type and status)
- Tasks overview (by status, time-boxing compliance)
- Quality metrics (if context system integrated)

Performance target: <1 second
"""

import click
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from pathlib import Path
from agentpm.cli.utils.project import ensure_project_root, get_current_project_id
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.methods import projects as project_methods
from agentpm.core.database.methods import work_items as wi_methods
from agentpm.core.database.methods import tasks as task_methods


@click.command()
@click.option(
    '--format',
    type=click.Choice(['dashboard', 'json'], case_sensitive=False),
    default='dashboard',
    help='Output format'
)
@click.pass_context
def status(ctx: click.Context, format: str):
    """
    Show project health dashboard.

    Displays project overview, work items summary, tasks overview,
    and quality metrics in a professional Rich-formatted dashboard.

    \b
    Examples:
      apm status                # Full dashboard
      apm status --format=json  # JSON output for scripts

    \b
    Performance:
      Target: <1 second (indexed database queries)
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    project_id = get_current_project_id(ctx)
    db = get_database_service(project_root)

    # Get data
    project = project_methods.get_project(db, project_id)
    work_items = wi_methods.list_work_items(db, project_id=project_id)

    # Get all tasks
    all_tasks = []
    for wi in work_items:
        all_tasks.extend(task_methods.list_tasks(db, work_item_id=wi.id))

    if format == 'json':
        import json
        output = {
            'project': {
                'id': project.id,
                'name': project.name,
                'path': project.path,
                'status': project.status.value
            },
            'work_items': {
                'total': len(work_items),
                'by_type': {},
                'by_status': {}
            },
            'tasks': {
                'total': len(all_tasks),
                'by_type': {},
                'by_status': {}
            }
        }

        # Calculate distributions
        for wi in work_items:
            wi_type = wi.type.value
            wi_status = wi.status.value
            output['work_items']['by_type'][wi_type] = output['work_items']['by_type'].get(wi_type, 0) + 1
            output['work_items']['by_status'][wi_status] = output['work_items']['by_status'].get(wi_status, 0) + 1

        for task in all_tasks:
            task_type = task.type.value
            task_status = task.status.value
            output['tasks']['by_type'][task_type] = output['tasks']['by_type'].get(task_type, 0) + 1
            output['tasks']['by_status'][task_status] = output['tasks']['by_status'].get(task_status, 0) + 1

        console.print(json.dumps(output, indent=2))
    else:
        # Dashboard view
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{project.name}[/bold cyan]\n"
            f"[dim]📁 {project.path}[/dim]\n"
            f"Status: {project.status.value}",
            title="🤖 APM (Agent Project Manager) Project Dashboard"
        ))
        console.print()

        # Work Items Section
        if work_items:
            wi_table = Table(title="📋 Work Items", show_header=True)
            wi_table.add_column("Type", style="magenta")
            wi_table.add_column("Count", justify="right", style="cyan")

            # Count by type
            wi_by_type = {}
            for wi in work_items:
                wi_type = wi.type.value
                wi_by_type[wi_type] = wi_by_type.get(wi_type, 0) + 1

            for wi_type, count in sorted(wi_by_type.items()):
                wi_table.add_row(wi_type, str(count))

            wi_table.add_row("", "", style="dim")
            wi_table.add_row("[bold]Total[/bold]", f"[bold]{len(work_items)}[/bold]")

            # Status distribution
            wi_status_table = Table(title="Status Distribution", show_header=True)
            wi_status_table.add_column("Status", style="yellow")
            wi_status_table.add_column("Count", justify="right", style="cyan")

            wi_by_status = {}
            for wi in work_items:
                status = wi.status.value
                wi_by_status[status] = wi_by_status.get(status, 0) + 1

            for status, count in sorted(wi_by_status.items()):
                wi_status_table.add_row(status, str(count))

            console.print(Columns([wi_table, wi_status_table]))
            console.print()
        else:
            console.print("ℹ️  [yellow]No work items yet[/yellow]")
            console.print("💡 Create one: [cyan]apm work-item create \"My Feature\" --type=feature[/cyan]\n")

        # Tasks Section
        if all_tasks:
            task_table = Table(title="✅ Tasks", show_header=True)
            task_table.add_column("Type", style="magenta")
            task_table.add_column("Count", justify="right", style="cyan")
            task_table.add_column("Total Hours", justify="right")

            # Count by type with effort
            task_by_type = {}
            effort_by_type = {}
            for task in all_tasks:
                task_type = task.type.value
                task_by_type[task_type] = task_by_type.get(task_type, 0) + 1
                if task.effort_hours:
                    effort_by_type[task_type] = effort_by_type.get(task_type, 0) + task.effort_hours

            for task_type, count in sorted(task_by_type.items()):
                effort = effort_by_type.get(task_type, 0)
                effort_str = f"{effort:.1f}h" if effort > 0 else "-"
                task_table.add_row(task_type, str(count), effort_str)

            total_effort = sum(t.effort_hours or 0 for t in all_tasks)
            task_table.add_row("", "", "", style="dim")
            task_table.add_row("[bold]Total[/bold]", f"[bold]{len(all_tasks)}[/bold]", f"[bold]{total_effort:.1f}h[/bold]")

            # Status distribution
            task_status_table = Table(title="Status Distribution", show_header=True)
            task_status_table.add_column("Status", style="yellow")
            task_status_table.add_column("Count", justify="right", style="cyan")

            task_by_status = {}
            for task in all_tasks:
                status = task.status.value
                task_by_status[status] = task_by_status.get(status, 0) + 1

            for status, count in sorted(task_by_status.items()):
                task_status_table.add_row(status, str(count))

            console.print(Columns([task_table, task_status_table]))
            console.print()

            # Time-boxing compliance
            console.print("[bold]⏱️  Time-Boxing Compliance:[/bold]")
            time_box_limits = {
                'implementation': 4.0,
                'testing': 6.0,
                'design': 8.0,
                'analysis': 8.0,
                'documentation': 6.0
            }

            compliant_count = 0
            total_checked = 0
            for task in all_tasks:
                if task.effort_hours and task.type.value in time_box_limits:
                    total_checked += 1
                    if task.effort_hours <= time_box_limits[task.type.value]:
                        compliant_count += 1

            if total_checked > 0:
                compliance_pct = int((compliant_count / total_checked) * 100)
                console.print(f"   {compliant_count}/{total_checked} tasks within limits ([green]{compliance_pct}%[/green])")
            else:
                console.print("   (No tasks with effort estimates)")

            console.print()
        else:
            console.print("ℹ️  [yellow]No tasks yet[/yellow]")
            console.print("💡 Create one: [cyan]apm task create \"My Task\" --work-item-id=<id> --type=implementation --effort=3[/cyan]\n")

        # Next steps
        console.print("[bold cyan]📚 Quick Commands:[/bold cyan]")
        console.print("   apm work-item list          # View all work items")
        console.print("   apm task list               # View all tasks")
        console.print("   apm work-item show <id>     # Check quality gates")
        console.print()
