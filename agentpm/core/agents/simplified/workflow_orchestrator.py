"""
Workflow Orchestrator - Master workflow coordination and high-level decision making

This agent coordinates the entire workflow for work items, makes high-level decisions,
handles errors and recovery, and monitors performance metrics.

Consolidates: master-orchestrator, deploy-orchestrator, discovery-orch
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from pathlib import Path

from ...database.models import WorkItem, Task
from ...database.enums import WorkItemStatus, Phase


class WorkflowDecision(Enum):
    """High-level workflow decisions"""
    PROCEED = "proceed"
    PAUSE = "pause"
    ESCALATE = "escalate"
    CANCEL = "cancel"
    RETRY = "retry"


@dataclass
class WorkflowContext:
    """Context for workflow coordination"""
    work_item: WorkItem
    current_phase: Phase
    tasks: List[Task]
    performance_metrics: Dict[str, Any]
    error_context: Optional[Dict[str, Any]] = None


class WorkflowOrchestrator:
    """
    Master workflow coordination and high-level decision making.
    
    Responsibilities:
    - Master workflow coordination
    - Cross-phase orchestration
    - High-level decision making
    - Workflow state management
    - Error handling and recovery
    - Performance monitoring
    """
    
    def __init__(self, db_service, performance_monitor=None):
        self.db_service = db_service
        self.performance_monitor = performance_monitor
        self.decision_history = []
        self.error_recovery_strategies = {
            "timeout": self._handle_timeout,
            "validation_failure": self._handle_validation_failure,
            "agent_unavailable": self._handle_agent_unavailable,
            "performance_degradation": self._handle_performance_degradation
        }
    
    async def coordinate_workflow(self, work_item: WorkItem) -> Dict[str, Any]:
        """
        Coordinate the entire workflow for a work item.
        
        Args:
            work_item: The work item to coordinate
            
        Returns:
            Coordination result with status and metrics
        """
        start_time = time.time()
        
        try:
            # Create workflow context
            context = await self._create_workflow_context(work_item)
            
            # Make high-level decisions
            decision = await self._make_high_level_decisions(context)
            
            # Execute workflow based on decision
            result = await self._execute_workflow(context, decision)
            
            # Monitor performance
            await self._monitor_performance(context, time.time() - start_time)
            
            return {
                "status": "success",
                "decision": decision.value,
                "execution_time": time.time() - start_time,
                "metrics": context.performance_metrics
            }
            
        except Exception as e:
            # Handle errors and recovery
            await self._handle_errors({
                "work_item_id": work_item.id,
                "error": str(e),
                "context": context if 'context' in locals() else None
            })
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def make_high_level_decisions(self, context: WorkflowContext) -> WorkflowDecision:
        """
        Make high-level workflow decisions based on context.
        
        Args:
            context: Workflow context
            
        Returns:
            High-level decision
        """
        # Check for errors first
        if context.error_context:
            return WorkflowDecision.ESCALATE
        
        # Check performance metrics
        if self._is_performance_degraded(context.performance_metrics):
            return WorkflowDecision.PAUSE
        
        # Check work item status
        if context.work_item.status == WorkItemStatus.BLOCKED:
            return WorkflowDecision.PAUSE
        
        # Check phase requirements
        if not self._are_phase_requirements_met(context):
            return WorkflowDecision.PAUSE
        
        # Default to proceed
        return WorkflowDecision.PROCEED
    
    async def handle_errors(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow errors and recovery.
        
        Args:
            error_context: Error context information
            
        Returns:
            Recovery result
        """
        error_type = error_context.get("error_type", "unknown")
        
        if error_type in self.error_recovery_strategies:
            recovery_result = await self.error_recovery_strategies[error_type](error_context)
        else:
            recovery_result = await self._handle_unknown_error(error_context)
        
        # Log error and recovery
        await self._log_error_recovery(error_context, recovery_result)
        
        return recovery_result
    
    async def monitor_performance(self, context: WorkflowContext, execution_time: float) -> None:
        """
        Monitor workflow performance metrics.
        
        Args:
            context: Workflow context
            execution_time: Execution time in seconds
        """
        metrics = {
            "execution_time": execution_time,
            "work_item_id": context.work_item.id,
            "phase": context.current_phase.value,
            "task_count": len(context.tasks),
            "timestamp": time.time()
        }
        
        # Update performance metrics
        context.performance_metrics.update(metrics)
        
        # Check for performance issues
        if execution_time > 5.0:  # 5 second threshold
            await self._handle_performance_degradation({
                "execution_time": execution_time,
                "threshold": 5.0,
                "context": context
            })
        
        # Store metrics if performance monitor available
        if self.performance_monitor:
            await self.performance_monitor.record_metrics(metrics)
    
    async def _create_workflow_context(self, work_item: WorkItem) -> WorkflowContext:
        """Create workflow context from work item."""
        # Load related tasks
        tasks = await self._load_work_item_tasks(work_item.id)
        
        # Get performance metrics
        performance_metrics = await self._get_performance_metrics(work_item.id)
        
        return WorkflowContext(
            work_item=work_item,
            current_phase=work_item.phase,
            tasks=tasks,
            performance_metrics=performance_metrics
        )
    
    async def _execute_workflow(self, context: WorkflowContext, decision: WorkflowDecision) -> Dict[str, Any]:
        """Execute workflow based on decision."""
        if decision == WorkflowDecision.PROCEED:
            return await self._proceed_with_workflow(context)
        elif decision == WorkflowDecision.PAUSE:
            return await self._pause_workflow(context)
        elif decision == WorkflowDecision.ESCALATE:
            return await self._escalate_workflow(context)
        elif decision == WorkflowDecision.CANCEL:
            return await self._cancel_workflow(context)
        elif decision == WorkflowDecision.RETRY:
            return await self._retry_workflow(context)
        else:
            raise ValueError(f"Unknown decision: {decision}")
    
    async def _proceed_with_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """Proceed with normal workflow execution."""
        # Delegate to phase orchestrator
        from .phase_orchestrator import PhaseOrchestrator
        phase_orchestrator = PhaseOrchestrator(self.db_service)
        
        result = await phase_orchestrator.orchestrate_phase(
            context.current_phase, 
            context.work_item
        )
        
        return {
            "action": "proceed",
            "phase_result": result
        }
    
    async def _pause_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """Pause workflow execution."""
        # Update work item status
        await self._update_work_item_status(context.work_item.id, WorkItemStatus.BLOCKED)
        
        return {
            "action": "pause",
            "reason": "Workflow paused due to requirements not met"
        }
    
    async def _escalate_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """Escalate workflow to higher authority."""
        # Log escalation
        await self._log_escalation(context)
        
        return {
            "action": "escalate",
            "reason": "Workflow escalated due to errors"
        }
    
    async def _cancel_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """Cancel workflow execution."""
        # Update work item status
        await self._update_work_item_status(context.work_item.id, WorkItemStatus.CANCELLED)
        
        return {
            "action": "cancel",
            "reason": "Workflow cancelled"
        }
    
    async def _retry_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """Retry workflow execution."""
        # Reset error context
        context.error_context = None
        
        # Retry with exponential backoff
        await asyncio.sleep(1)  # Simple backoff for now
        
        return await self._proceed_with_workflow(context)
    
    def _is_performance_degraded(self, metrics: Dict[str, Any]) -> bool:
        """Check if performance is degraded."""
        execution_time = metrics.get("execution_time", 0)
        return execution_time > 5.0  # 5 second threshold
    
    def _are_phase_requirements_met(self, context: WorkflowContext) -> bool:
        """Check if phase requirements are met."""
        # This would check phase-specific requirements
        # For now, return True as a placeholder
        return True
    
    async def _handle_timeout(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout errors."""
        return {
            "recovery_action": "retry",
            "backoff_seconds": 5,
            "max_retries": 3
        }
    
    async def _handle_validation_failure(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation failures."""
        return {
            "recovery_action": "escalate",
            "reason": "Validation failure requires manual intervention"
        }
    
    async def _handle_agent_unavailable(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent unavailability."""
        return {
            "recovery_action": "retry",
            "backoff_seconds": 10,
            "max_retries": 2
        }
    
    async def _handle_performance_degradation(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance degradation."""
        return {
            "recovery_action": "pause",
            "reason": "Performance degradation detected"
        }
    
    async def _handle_unknown_error(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown errors."""
        return {
            "recovery_action": "escalate",
            "reason": "Unknown error requires investigation"
        }
    
    async def _load_work_item_tasks(self, work_item_id: int) -> List[Task]:
        """Load tasks for work item."""
        # This would load tasks from database
        # For now, return empty list as placeholder
        return []
    
    async def _get_performance_metrics(self, work_item_id: int) -> Dict[str, Any]:
        """Get performance metrics for work item."""
        # This would load performance metrics from database
        # For now, return empty dict as placeholder
        return {}
    
    async def _update_work_item_status(self, work_item_id: int, status: WorkItemStatus) -> None:
        """Update work item status."""
        # This would update work item status in database
        pass
    
    async def _log_escalation(self, context: WorkflowContext) -> None:
        """Log workflow escalation."""
        # This would log escalation to audit system
        pass
    
    async def _log_error_recovery(self, error_context: Dict[str, Any], recovery_result: Dict[str, Any]) -> None:
        """Log error and recovery."""
        # This would log error and recovery to audit system
        pass


# Factory function for creating workflow orchestrator
def create_workflow_orchestrator(db_service, performance_monitor=None) -> WorkflowOrchestrator:
    """Create a new workflow orchestrator instance."""
    return WorkflowOrchestrator(db_service, performance_monitor)
