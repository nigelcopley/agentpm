#!/usr/bin/env python3
"""
Debug task status issue
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from agentpm.core.database.enums import TaskStatus
from agentpm.core.workflow.state_machine import StateMachine, EntityType

def debug_task_status():
    """Debug the task status issue"""
    
    print("🔍 Debugging task status issue...")
    
    # Test TaskStatus enum
    print(f"\n📋 TaskStatus enum values:")
    for status in TaskStatus:
        print(f"  {status.name} = {status.value}")
    
    # Test creating TaskStatus from string
    try:
        active_status = TaskStatus("active")
        print(f"\n✅ TaskStatus('active') = {active_status}")
        print(f"   active_status.value = {active_status.value}")
        print(f"   type(active_status) = {type(active_status)}")
    except Exception as e:
        print(f"❌ Error creating TaskStatus('active'): {e}")
    
    # Test get_next_state method
    try:
        active_status = TaskStatus("active")
        next_status = TaskStatus.get_next_state(active_status)
        print(f"\n✅ TaskStatus.get_next_state({active_status}) = {next_status}")
        print(f"   type(next_status) = {type(next_status)}")
        if next_status:
            print(f"   next_status.value = {next_status.value}")
    except Exception as e:
        print(f"❌ Error with get_next_state: {e}")
    
    # Test StateMachine.get_next_state
    try:
        next_status = StateMachine.get_next_state(EntityType.TASK, "active")
        print(f"\n✅ StateMachine.get_next_state(TASK, 'active') = {next_status}")
        print(f"   type(next_status) = {type(next_status)}")
    except Exception as e:
        print(f"❌ Error with StateMachine.get_next_state: {e}")
    
    # Test the actual task from database
    try:
        from agentpm.cli.utils.project import ensure_project_root
        from agentpm.cli.utils.services import get_database_service
        from agentpm.core.database.methods import tasks
        
        # Get project root (current directory)
        project_root = os.getcwd()
        print(f"   project_root = {project_root}")
        db = get_database_service(project_root)
        
        # Get task 525
        task = tasks.get_task(db, 525)
        if task:
            print(f"\n✅ Task 525 from database:")
            print(f"   task.status = {task.status}")
            print(f"   type(task.status) = {type(task.status)}")
            print(f"   task.status.value = {task.status.value}")
            
            # Test StateMachine with actual task status
            current_status = task.status.value
            next_status = StateMachine.get_next_state(EntityType.TASK, current_status)
            print(f"   StateMachine.get_next_state(TASK, '{current_status}') = {next_status}")
        else:
            print(f"❌ Task 525 not found")
    except Exception as e:
        print(f"❌ Error getting task from database: {e}")

if __name__ == "__main__":
    debug_task_status()
