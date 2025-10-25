"""
Context Assembly Plugin - Core Platform Agnostic Logic

Provides universal context assembly capabilities that work across all AI platforms.
This is the core plugin that handles context assembly without platform-specific optimizations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from agentpm.core.database import DatabaseService
from agentpm.core.context.assembly_service import ContextAssemblyService, ContextPayload
from agentpm.core.database.models.context import UnifiedSixW


class ContextAssemblyPlugin:
    """
    Platform-agnostic context assembly plugin.
    
    This plugin provides universal context assembly that can be consumed
    by any AI platform through appropriate formatters and adapters.
    """
    
    def __init__(self, db: DatabaseService, project_path: Path):
        """
        Initialize the context assembly plugin.
        
        Args:
            db: Database service instance
            project_path: Project root path
        """
        self.db = db
        self.project_path = project_path
        self.assembly_service = ContextAssemblyService(
            db=db,
            project_path=project_path,
            enable_cache=False  # Cache disabled for MVP
        )
    
    def assemble_task_context(self, task_id: int, agent_role: Optional[str] = None) -> ContextPayload:
        """
        Assemble complete context for a task.
        
        Args:
            task_id: Task ID to assemble context for
            agent_role: Optional agent role override
            
        Returns:
            Complete context payload with hierarchical data
        """
        return self.assembly_service.assemble_task_context(task_id, agent_role)
    
    def assemble_work_item_context(self, work_item_id: int) -> Dict[str, Any]:
        """
        Assemble context for a work item.
        
        Args:
            work_item_id: Work item ID
            
        Returns:
            Work item context data
        """
        # Implementation would use work item context assembly
        # This is a placeholder for the full implementation
        return {
            'work_item_id': work_item_id,
            'context_type': 'work_item',
            'assembled_at': datetime.now().isoformat()
        }
    
    def assemble_project_context(self, project_id: int) -> Dict[str, Any]:
        """
        Assemble context for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project context data
        """
        # Implementation would use project context assembly
        # This is a placeholder for the full implementation
        return {
            'project_id': project_id,
            'context_type': 'project',
            'assembled_at': datetime.now().isoformat()
        }
    
    def get_active_tasks_context(self, limit: int = 3) -> List[ContextPayload]:
        """
        Get context for all active tasks.
        
        Args:
            limit: Maximum number of tasks to process
            
        Returns:
            List of context payloads for active tasks
        """
        from agentpm.core.database.methods import tasks as task_methods
        from agentpm.core.database.enums import TaskStatus
        
        active_tasks = task_methods.list_tasks(self.db, status=TaskStatus.ACTIVE, limit=limit)
        contexts = []
        
        for task in active_tasks:
            try:
                context = self.assemble_task_context(task.id)
                contexts.append(context)
            except Exception as e:
                # Graceful degradation - log but continue
                print(f"⚠️ Context assembly failed for Task #{task.id}: {e}")
                continue
                
        return contexts


