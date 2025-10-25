"""
Task Next Command - Automatic State Progression

This command automatically transitions a task to its next logical state
in the 6-state workflow system using the --next flag functionality.
"""

import click
from rich.console import Console
from rich.panel import Panel

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service, get_workflow_service
from agentpm.core.workflow.state_machine import StateMachine, EntityType


@click.command()
@click.argument('task_id', type=int)
@click.pass_context
def next(ctx, task_id: int):
    """
    Automatically transition task to next logical state.
    
    Uses the 6-state workflow system to determine the next state:
    draft → ready → active → review → done → archived
    
    Administrative states (blocked, cancelled) do not have automatic next states.
    """
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    workflow = get_workflow_service(project_root)
    db = get_database_service(project_root)
    
    try:
        # Get current task
        from agentpm.core.database.adapters import TaskAdapter
        task = TaskAdapter.get(db, task_id)
        if not task:
            console.print(f"[red]✗[/red] Task {task_id} not found")
            return
        
        # Get next state using state machine
        current_status = task.status.value
        next_status = StateMachine.get_next_state(EntityType.TASK, current_status)
        
        if not next_status:
            console.print(f"[yellow]⚠[/yellow] Task {task_id} is in '{current_status}' status - no automatic next state available")
            console.print("Administrative states (blocked, cancelled, archived) do not have automatic progression.")
            return
        
        # Transition to next state
        from agentpm.core.database.enums import TaskStatus
        next_status_enum = TaskStatus(next_status)
        
        try:
            updated_task = workflow.transition_task(task_id, next_status_enum)
            console.print(f"[green]✓[/green] Task {task_id} transitioned from '{current_status}' to '{next_status}'")
            
            # Show next possible states
            from agentpm.core.workflow.state_machine import StateMachine as SM
            from agentpm.core.database.enums import TaskStatus

            try:
                current_enum = TaskStatus(next_status)
                possible_next = SM.TASK_TRANSITIONS.get(current_enum, [])
                if possible_next:
                    next_possible = StateMachine.get_next_state(EntityType.TASK, next_status)
                    if next_possible:
                        console.print(f"[blue]ℹ[/blue] Next automatic progression: '{next_status}' → '{next_possible}'")
                    else:
                        console.print(f"[blue]ℹ[/blue] '{next_status}' is a terminal state - no further automatic progression")
                else:
                    console.print(f"[blue]ℹ[/blue] '{next_status}' has no valid transitions")
            except ValueError:
                console.print(f"[blue]ℹ[/blue] Status '{next_status}' is not recognized")
                
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to transition task {task_id}: {str(e)}")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
