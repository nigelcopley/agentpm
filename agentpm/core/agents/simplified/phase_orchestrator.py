"""
Phase Orchestrator - Phase-specific orchestration and phase gate enforcement

This agent orchestrates specific phases, enforces phase gates, manages phase transitions,
and coordinates quality gates.

Consolidates: definition-orch, planning-orch, implementation-orch, review-test-orch, release-ops-orch, evolution-orch
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from pathlib import Path

from ...database.models import WorkItem, Task
from ...database.enums import WorkItemStatus, Phase, TaskStatus


class PhaseGateStatus(Enum):
    """Phase gate status"""
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"


@dataclass
class PhaseGate:
    """Phase gate definition"""
    name: str
    description: str
    required: bool
    status: PhaseGateStatus
    validation_function: str
    error_message: Optional[str] = None


@dataclass
class PhaseContext:
    """Context for phase orchestration"""
    work_item: WorkItem
    phase: Phase
    tasks: List[Task]
    gates: List[PhaseGate]
    phase_metrics: Dict[str, Any]


class PhaseOrchestrator:
    """
    Phase-specific orchestration and phase gate enforcement.
    
    Responsibilities:
    - Phase-specific orchestration
    - Phase gate enforcement
    - Phase transition management
    - Quality gate coordination
    - Phase-specific error handling
    """
    
    def __init__(self, db_service, quality_orchestrator=None):
        self.db_service = db_service
        self.quality_orchestrator = quality_orchestrator
        self.phase_gates = self._initialize_phase_gates()
        self.phase_handlers = {
            Phase.D1_DISCOVERY: self._handle_discovery_phase,
            Phase.P1_PLAN: self._handle_planning_phase,
            Phase.I1_IMPLEMENTATION: self._handle_implementation_phase,
            Phase.R1_REVIEW: self._handle_review_phase,
            Phase.O1_OPERATIONS: self._handle_operations_phase,
            Phase.E1_EVOLUTION: self._handle_evolution_phase
        }
    
    async def orchestrate_phase(self, phase: Phase, work_item: WorkItem) -> Dict[str, Any]:
        """
        Orchestrate a specific phase.
        
        Args:
            phase: The phase to orchestrate
            work_item: The work item being processed
            
        Returns:
            Phase orchestration result
        """
        start_time = time.time()
        
        try:
            # Create phase context
            context = await self._create_phase_context(phase, work_item)
            
            # Enforce phase gates
            gate_results = await self._enforce_phase_gates(context)
            
            # Execute phase-specific logic
            phase_result = await self._execute_phase_logic(context)
            
            # Check if ready for transition
            transition_ready = await self._check_transition_readiness(context, gate_results)
            
            return {
                "status": "success",
                "phase": phase.value,
                "gate_results": gate_results,
                "phase_result": phase_result,
                "transition_ready": transition_ready,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "status": "error",
                "phase": phase.value,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def enforce_phase_gates(self, phase: Phase, work_item: WorkItem) -> Dict[str, Any]:
        """
        Enforce phase-specific quality gates.
        
        Args:
            phase: The phase to enforce gates for
            work_item: The work item being processed
            
        Returns:
            Gate enforcement results
        """
        context = await self._create_phase_context(phase, work_item)
        return await self._enforce_phase_gates(context)
    
    async def manage_phase_transitions(self, from_phase: Phase, to_phase: Phase, work_item: WorkItem) -> Dict[str, Any]:
        """
        Manage transitions between phases.
        
        Args:
            from_phase: The phase transitioning from
            to_phase: The phase transitioning to
            work_item: The work item being processed
            
        Returns:
            Transition result
        """
        try:
            # Validate transition is allowed
            if not self._is_transition_allowed(from_phase, to_phase):
                return {
                    "status": "error",
                    "error": f"Transition from {from_phase.value} to {to_phase.value} not allowed"
                }
            
            # Execute transition logic
            transition_result = await self._execute_transition_logic(from_phase, to_phase, work_item)
            
            # Update work item phase
            await self._update_work_item_phase(work_item.id, to_phase)
            
            return {
                "status": "success",
                "from_phase": from_phase.value,
                "to_phase": to_phase.value,
                "transition_result": transition_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_phase_context(self, phase: Phase, work_item: WorkItem) -> PhaseContext:
        """Create phase context."""
        # Load tasks for this phase
        tasks = await self._load_phase_tasks(work_item.id, phase)
        
        # Get phase gates
        gates = self._get_phase_gates(phase)
        
        # Get phase metrics
        phase_metrics = await self._get_phase_metrics(work_item.id, phase)
        
        return PhaseContext(
            work_item=work_item,
            phase=phase,
            tasks=tasks,
            gates=gates,
            phase_metrics=phase_metrics
        )
    
    async def _enforce_phase_gates(self, context: PhaseContext) -> Dict[str, Any]:
        """Enforce phase gates for the context."""
        gate_results = {}
        
        for gate in context.gates:
            try:
                # Validate gate
                gate_result = await self._validate_gate(gate, context)
                gate_results[gate.name] = gate_result
                
                # Update gate status
                gate.status = PhaseGateStatus.PASSED if gate_result["passed"] else PhaseGateStatus.FAILED
                
            except Exception as e:
                gate_results[gate.name] = {
                    "passed": False,
                    "error": str(e)
                }
                gate.status = PhaseGateStatus.FAILED
                gate.error_message = str(e)
        
        return gate_results
    
    async def _execute_phase_logic(self, context: PhaseContext) -> Dict[str, Any]:
        """Execute phase-specific logic."""
        handler = self.phase_handlers.get(context.phase)
        if handler:
            return await handler(context)
        else:
            return {
                "status": "error",
                "error": f"No handler for phase {context.phase.value}"
            }
    
    async def _check_transition_readiness(self, context: PhaseContext, gate_results: Dict[str, Any]) -> bool:
        """Check if phase is ready for transition."""
        # Check if all required gates passed
        for gate in context.gates:
            if gate.required and not gate_results.get(gate.name, {}).get("passed", False):
                return False
        
        # Check phase-specific readiness criteria
        return await self._check_phase_specific_readiness(context)
    
    async def _handle_discovery_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle discovery phase logic."""
        return {
            "phase": "discovery",
            "actions": [
                "Define user needs",
                "Validate market fit",
                "Gather requirements",
                "Assess technical feasibility"
            ],
            "deliverables": [
                "User stories",
                "Market validation",
                "Technical feasibility assessment",
                "Business value confirmation"
            ]
        }
    
    async def _handle_planning_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle planning phase logic."""
        return {
            "phase": "planning",
            "actions": [
                "Create technical design",
                "Break down work into tasks",
                "Plan dependencies and risks",
                "Estimate effort and timeline"
            ],
            "deliverables": [
                "Technical design document",
                "Task breakdown",
                "Dependency mapping",
                "Risk assessment"
            ]
        }
    
    async def _handle_implementation_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle implementation phase logic."""
        return {
            "phase": "implementation",
            "actions": [
                "Implement feature",
                "Write tests",
                "Document code",
                "Complete code review"
            ],
            "deliverables": [
                "Implemented code",
                "Test suite",
                "Code documentation",
                "Code review results"
            ]
        }
    
    async def _handle_review_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle review phase logic."""
        return {
            "phase": "review",
            "actions": [
                "Conduct quality review",
                "Validate acceptance criteria",
                "Perform integration testing",
                "Prepare for release"
            ],
            "deliverables": [
                "Quality review report",
                "Acceptance criteria validation",
                "Integration test results",
                "Release preparation"
            ]
        }
    
    async def _handle_operations_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle operations phase logic."""
        return {
            "phase": "operations",
            "actions": [
                "Deploy to production",
                "Monitor system health",
                "Handle incidents",
                "Gather feedback"
            ],
            "deliverables": [
                "Production deployment",
                "Health monitoring",
                "Incident reports",
                "User feedback"
            ]
        }
    
    async def _handle_evolution_phase(self, context: PhaseContext) -> Dict[str, Any]:
        """Handle evolution phase logic."""
        return {
            "phase": "evolution",
            "actions": [
                "Analyze performance",
                "Identify improvements",
                "Plan next iteration",
                "Update documentation"
            ],
            "deliverables": [
                "Performance analysis",
                "Improvement recommendations",
                "Next iteration plan",
                "Updated documentation"
            ]
        }
    
    def _initialize_phase_gates(self) -> Dict[Phase, List[PhaseGate]]:
        """Initialize phase gates for each phase."""
        return {
            Phase.D1_DISCOVERY: [
                PhaseGate("user_stories_defined", "User stories and acceptance criteria defined", True, PhaseGateStatus.PENDING, "validate_user_stories"),
                PhaseGate("market_validation", "Market need and user demand validated", True, PhaseGateStatus.PENDING, "validate_market"),
                PhaseGate("technical_feasibility", "Technical approach validated and feasible", True, PhaseGateStatus.PENDING, "validate_feasibility"),
                PhaseGate("business_value_confirmed", "Business value and ROI confirmed", True, PhaseGateStatus.PENDING, "validate_business_value")
            ],
            Phase.P1_PLAN: [
                PhaseGate("technical_design_complete", "Technical architecture and design complete", True, PhaseGateStatus.PENDING, "validate_design"),
                PhaseGate("tasks_created", "All implementation tasks created and estimated", True, PhaseGateStatus.PENDING, "validate_tasks"),
                PhaseGate("dependencies_mapped", "Task dependencies and sequencing defined", True, PhaseGateStatus.PENDING, "validate_dependencies"),
                PhaseGate("risks_assessed", "Technical and project risks identified and mitigated", True, PhaseGateStatus.PENDING, "validate_risks")
            ],
            Phase.I1_IMPLEMENTATION: [
                PhaseGate("feature_implemented", "Feature implementation complete", True, PhaseGateStatus.PENDING, "validate_implementation"),
                PhaseGate("tests_written", "Test suite written and passing", True, PhaseGateStatus.PENDING, "validate_tests"),
                PhaseGate("code_documented", "Code documentation complete", True, PhaseGateStatus.PENDING, "validate_documentation"),
                PhaseGate("code_reviewed", "Code review complete", True, PhaseGateStatus.PENDING, "validate_review")
            ],
            Phase.R1_REVIEW: [
                PhaseGate("quality_review_complete", "Quality review complete", True, PhaseGateStatus.PENDING, "validate_quality"),
                PhaseGate("acceptance_criteria_met", "All acceptance criteria validated", True, PhaseGateStatus.PENDING, "validate_acceptance"),
                PhaseGate("integration_tests_pass", "Integration tests passing", True, PhaseGateStatus.PENDING, "validate_integration"),
                PhaseGate("release_ready", "Ready for release", True, PhaseGateStatus.PENDING, "validate_release")
            ],
            Phase.O1_OPERATIONS: [
                PhaseGate("deployed_to_production", "Deployed to production", True, PhaseGateStatus.PENDING, "validate_deployment"),
                PhaseGate("monitoring_active", "System monitoring active", True, PhaseGateStatus.PENDING, "validate_monitoring"),
                PhaseGate("incidents_handled", "Incidents handled appropriately", True, PhaseGateStatus.PENDING, "validate_incidents"),
                PhaseGate("feedback_collected", "User feedback collected", True, PhaseGateStatus.PENDING, "validate_feedback")
            ],
            Phase.E1_EVOLUTION: [
                PhaseGate("performance_analyzed", "Performance analysis complete", True, PhaseGateStatus.PENDING, "validate_performance"),
                PhaseGate("improvements_identified", "Improvements identified", True, PhaseGateStatus.PENDING, "validate_improvements"),
                PhaseGate("next_iteration_planned", "Next iteration planned", True, PhaseGateStatus.PENDING, "validate_planning"),
                PhaseGate("documentation_updated", "Documentation updated", True, PhaseGateStatus.PENDING, "validate_documentation")
            ]
        }
    
    def _get_phase_gates(self, phase: Phase) -> List[PhaseGate]:
        """Get phase gates for a specific phase."""
        return self.phase_gates.get(phase, [])
    
    def _is_transition_allowed(self, from_phase: Phase, to_phase: Phase) -> bool:
        """Check if transition between phases is allowed."""
        # Define allowed transitions
        allowed_transitions = {
            Phase.D1_DISCOVERY: [Phase.P1_PLAN],
            Phase.P1_PLAN: [Phase.I1_IMPLEMENTATION],
            Phase.I1_IMPLEMENTATION: [Phase.R1_REVIEW],
            Phase.R1_REVIEW: [Phase.O1_OPERATIONS],
            Phase.O1_OPERATIONS: [Phase.E1_EVOLUTION],
            Phase.E1_EVOLUTION: [Phase.D1_DISCOVERY]  # Can cycle back
        }
        
        return to_phase in allowed_transitions.get(from_phase, [])
    
    async def _validate_gate(self, gate: PhaseGate, context: PhaseContext) -> Dict[str, Any]:
        """Validate a specific gate."""
        # This would call the actual validation function
        # For now, return a placeholder result
        return {
            "passed": True,
            "message": f"Gate {gate.name} validated successfully"
        }
    
    async def _check_phase_specific_readiness(self, context: PhaseContext) -> bool:
        """Check phase-specific readiness criteria."""
        # This would check phase-specific criteria
        # For now, return True as placeholder
        return True
    
    async def _execute_transition_logic(self, from_phase: Phase, to_phase: Phase, work_item: WorkItem) -> Dict[str, Any]:
        """Execute transition logic between phases."""
        return {
            "transition": f"{from_phase.value} -> {to_phase.value}",
            "actions": [
                "Validate transition requirements",
                "Update work item status",
                "Initialize new phase",
                "Notify stakeholders"
            ]
        }
    
    async def _load_phase_tasks(self, work_item_id: int, phase: Phase) -> List[Task]:
        """Load tasks for a specific phase."""
        # This would load tasks from database
        # For now, return empty list as placeholder
        return []
    
    async def _get_phase_metrics(self, work_item_id: int, phase: Phase) -> Dict[str, Any]:
        """Get phase metrics."""
        # This would load phase metrics from database
        # For now, return empty dict as placeholder
        return {}
    
    async def _update_work_item_phase(self, work_item_id: int, phase: Phase) -> None:
        """Update work item phase."""
        # This would update work item phase in database
        pass


# Factory function for creating phase orchestrator
def create_phase_orchestrator(db_service, quality_orchestrator=None) -> PhaseOrchestrator:
    """Create a new phase orchestrator instance."""
    return PhaseOrchestrator(db_service, quality_orchestrator)
