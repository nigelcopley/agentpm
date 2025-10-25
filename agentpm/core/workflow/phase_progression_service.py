"""
Phase Progression Service - Manages Phase Transitions with Gate Validation

Orchestrates phase advancement with gate validation enforcement.

Workflow Pattern:
    1. Validate current phase gate (all requirements met?)
    2. If valid: Advance to next phase → derive status → emit event
    3. If invalid: Return missing requirements for user action

Key Principles:
    - Phase is source of truth (status derived from phase)
    - Gate validation enforced (cannot bypass requirements)
    - Evidence-based progression (confidence scoring)
    - Audit trail (all transitions logged)

Security:
    - Read-only gate validation (no side effects)
    - Transactional phase updates (atomic state changes)
    - Event emission for audit trail
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from ..database.models.work_item import WorkItem
from ..database.enums import Phase, WorkItemStatus
from .phase_validator import PhaseValidator
from .phase_gates import (
    GateResult,
    D1GateValidator,
    P1GateValidator,
    I1GateValidator,
    R1GateValidator,
    O1GateValidator,
    E1GateValidator
)
from ..database import methods as db_methods


# Phase-to-Status Mapping (Deterministic)
PHASE_TO_STATUS = {
    None: WorkItemStatus.DRAFT,                     # No phase = drafting ideas
    Phase.D1_DISCOVERY: WorkItemStatus.DRAFT,       # Gathering requirements
    Phase.P1_PLAN: WorkItemStatus.READY,            # Plan validated, ready to start
    Phase.I1_IMPLEMENTATION: WorkItemStatus.ACTIVE, # Building solution
    Phase.R1_REVIEW: WorkItemStatus.REVIEW,         # Quality validation
    Phase.O1_OPERATIONS: WorkItemStatus.DONE,       # Deployed successfully
    Phase.E1_EVOLUTION: WorkItemStatus.ARCHIVED,    # Historical + learning
}


@dataclass
class PhaseTransitionResult:
    """
    Result of phase transition attempt.

    Attributes:
        success: True if phase advanced, False if validation failed
        new_phase: New phase (if advanced)
        new_status: Derived status from new phase (if advanced)
        missing_requirements: List of unmet requirements (if validation failed)
        confidence: Gate validation confidence score 0.0-1.0
        error: Error message (if operation failed)
        message: Human-readable result message
        metadata: Additional context (task counts, coverage, etc.)
    """
    success: bool
    new_phase: Optional[Phase] = None
    new_status: Optional[WorkItemStatus] = None
    missing_requirements: List[str] = field(default_factory=list)
    confidence: float = 0.0
    error: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PhaseProgressionService:
    """
    Manages phase transitions with gate validation enforcement.

    Responsibilities:
        - Validate current phase gate requirements
        - Advance to next phase when requirements met
        - Derive and update status from phase
        - Emit phase transition events for audit
        - Calculate confidence scores for information quality

    Usage:
        >>> service = PhaseProgressionService(db)
        >>> result = service.advance_to_next_phase(work_item_id=81)
        >>> if result.success:
        >>>     print(f"Advanced to {result.new_phase}")
        >>> else:
        >>>     print(f"Missing: {result.missing_requirements}")

    Integration:
        - Called by CLI commands (apm work-item next)
        - Called by mini-orchestrators (definition-orch, planning-orch, etc.)
        - Integrated with WorkflowService for status transitions
    """

    # Gate validator registry (phase → validator class)
    GATE_VALIDATORS = {
        Phase.D1_DISCOVERY: D1GateValidator,
        Phase.P1_PLAN: P1GateValidator,
        Phase.I1_IMPLEMENTATION: I1GateValidator,
        Phase.R1_REVIEW: R1GateValidator,
        Phase.O1_OPERATIONS: O1GateValidator,
        Phase.E1_EVOLUTION: E1GateValidator,
    }

    def __init__(self, db):
        """
        Initialize phase progression service.

        Args:
            db: DatabaseService instance for data access
        """
        self.db = db
        self.phase_validator = PhaseValidator()

    def advance_to_next_phase(
        self,
        work_item_id: int,
        validate_only: bool = False
    ) -> PhaseTransitionResult:
        """
        Advance work item to next phase after validating current gate.

        Process:
            1. Load work item
            2. Get next phase in type-specific sequence
            3. Validate current phase gate (all requirements met?)
            4. If valid: Advance phase → derive status → emit event
            5. If invalid: Return missing requirements

        Args:
            work_item_id: Work item ID to advance
            validate_only: If True, validate without advancing (dry-run)

        Returns:
            PhaseTransitionResult with outcome

        Example:
            >>> # Validate readiness (dry-run)
            >>> result = service.advance_to_next_phase(81, validate_only=True)
            >>> if not result.success:
            >>>     print(f"Not ready: {result.missing_requirements}")
            >>>
            >>> # Actually advance
            >>> result = service.advance_to_next_phase(81)
            >>> if result.success:
            >>>     print(f"Advanced: {result.new_phase}")
        """
        # Load work item
        work_item = db_methods.work_items.get_work_item(self.db, work_item_id)
        if not work_item:
            return PhaseTransitionResult(
                success=False,
                error=f"Work item {work_item_id} not found"
            )

        # Get current and next phase
        current_phase = work_item.phase
        next_phase = self.phase_validator.get_next_allowed_phase(work_item)

        if not next_phase:
            # Already at final phase
            final_phase = self.phase_validator.get_allowed_phases(work_item.type)[-1]
            return PhaseTransitionResult(
                success=False,
                error=f"Work item already at final phase ({final_phase.name})",
                message="No further phase progression available"
            )

        # Validate current phase gate (must pass before advancing)
        # NOTE: If current_phase is None (new work item), no gate validation needed
        if current_phase:
            gate_result = self.validate_current_gate(work_item_id)

            if not gate_result.passed:
                return PhaseTransitionResult(
                    success=False,
                    missing_requirements=gate_result.missing_requirements,
                    confidence=gate_result.confidence,
                    metadata=gate_result.metadata,
                    message=f"Cannot advance: {len(gate_result.missing_requirements)} requirements not met"
                )
        else:
            # No current phase - starting fresh
            gate_result = GateResult(passed=True, confidence=0.0)

        # Gate passed - return success if validate_only
        if validate_only:
            return PhaseTransitionResult(
                success=True,
                new_phase=next_phase,
                new_status=PHASE_TO_STATUS[next_phase],
                confidence=gate_result.confidence,
                metadata=gate_result.metadata,
                message=f"Gate validation passed - ready to advance to {next_phase.name}"
            )

        # Update phase (atomic database transaction)
        updated = db_methods.work_items.update_work_item(
            self.db,
            work_item_id,
            phase=next_phase
        )

        if not updated:
            return PhaseTransitionResult(
                success=False,
                error="Failed to update work item phase"
            )

        # Derive and update status from new phase
        new_status = PHASE_TO_STATUS[next_phase]
        if updated.status != new_status:
            updated = db_methods.work_items.update_work_item(
                self.db,
                work_item_id,
                status=new_status
            )

        # Emit phase advancement event (for audit trail)
        self._emit_phase_advanced_event(
            work_item,
            current_phase,
            next_phase,
            gate_result.confidence
        )

        return PhaseTransitionResult(
            success=True,
            new_phase=next_phase,
            new_status=new_status,
            confidence=gate_result.confidence,
            metadata=gate_result.metadata,
            message=f"Advanced from {current_phase.name if current_phase else 'NULL'} to {next_phase.name}"
        )

    def validate_current_gate(self, work_item_id: int) -> GateResult:
        """
        Validate current phase gate requirements.

        Checks if work item meets all requirements for current phase
        before allowing advancement to next phase.

        Args:
            work_item_id: Work item ID to validate

        Returns:
            GateResult with pass/fail and missing requirements

        Example:
            >>> result = service.validate_current_gate(81)
            >>> if not result.passed:
            >>>     for req in result.missing_requirements:
            >>>         print(f"Missing: {req}")
            >>> print(f"Confidence: {result.confidence:.0%}")
        """
        # Load work item
        work_item = db_methods.work_items.get_work_item(self.db, work_item_id)
        if not work_item:
            return GateResult(
                passed=False,
                missing_requirements=[f"Work item {work_item_id} not found"],
                confidence=0.0
            )

        # If no phase yet, nothing to validate
        if not work_item.phase:
            return GateResult(
                passed=True,
                confidence=0.0,
                metadata={'phase': 'NULL', 'note': 'No gate validation for NULL phase'}
            )

        # Get gate validator for current phase
        validator_class = self.GATE_VALIDATORS.get(work_item.phase)
        if not validator_class:
            return GateResult(
                passed=False,
                missing_requirements=[f"No gate validator for phase {work_item.phase.name}"],
                confidence=0.0
            )

        # Run validation
        validator = validator_class()
        return validator.validate(work_item, self.db)

    def get_gate_status(self, work_item_id: int) -> Dict[str, Any]:
        """
        Get comprehensive gate status for work item.

        Returns detailed status including:
            - Current phase and status
            - Next available phase
            - Gate validation result
            - Missing requirements
            - Confidence score

        Args:
            work_item_id: Work item ID

        Returns:
            Dictionary with gate status details

        Example:
            >>> status = service.get_gate_status(81)
            >>> print(f"Phase: {status['current_phase']}")
            >>> print(f"Ready: {status['gate_passed']}")
            >>> print(f"Missing: {status['missing_requirements']}")
        """
        # Load work item
        work_item = db_methods.work_items.get_work_item(self.db, work_item_id)
        if not work_item:
            return {
                'error': f'Work item {work_item_id} not found',
                'gate_passed': False
            }

        # Get phase information
        current_phase = work_item.phase
        next_phase = self.phase_validator.get_next_allowed_phase(work_item)
        final_phase = self.phase_validator.is_final_phase(
            work_item.type,
            current_phase
        ) if current_phase else False

        # Validate current gate
        gate_result = self.validate_current_gate(work_item_id)

        return {
            'work_item_id': work_item_id,
            'work_item_name': work_item.name,
            'work_item_type': work_item.type.value,
            'current_phase': current_phase.value if current_phase else None,
            'current_phase_name': current_phase.name if current_phase else 'NULL',
            'current_status': work_item.status.value,
            'next_phase': next_phase.value if next_phase else None,
            'next_phase_name': next_phase.name if next_phase else 'N/A',
            'is_final_phase': final_phase,
            'gate_passed': gate_result.passed,
            'missing_requirements': gate_result.missing_requirements,
            'confidence': gate_result.confidence,
            'confidence_label': self._get_confidence_label(gate_result.confidence),
            'metadata': gate_result.metadata
        }

    def _emit_phase_advanced_event(
        self,
        work_item: WorkItem,
        old_phase: Optional[Phase],
        new_phase: Phase,
        confidence: float
    ):
        """
        Emit phase advancement event for audit trail.

        Creates event record in database for:
            - Audit compliance
            - Workflow tracking
            - Analytics and reporting

        Args:
            work_item: WorkItem that transitioned
            old_phase: Previous phase (or None)
            new_phase: New phase
            confidence: Gate validation confidence
        """
        import json

        event_data = {
            'work_item_id': work_item.id,
            'work_item_name': work_item.name,
            'old_phase': old_phase.value if old_phase else None,
            'new_phase': new_phase.value,
            'old_status': work_item.status.value,
            'new_status': PHASE_TO_STATUS[new_phase].value,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Create session event (if session system available)
        try:
            from ..database.models.event import Event, EventType

            event = Event(
                project_id=work_item.project_id,
                session_id=None,  # No session context
                event_type=EventType.PHASE_ADVANCED,
                entity_type='work_item',
                entity_id=work_item.id,
                data=json.dumps(event_data)
            )

            db_methods.events.create_event(self.db, event)
        except (ImportError, AttributeError):
            # Event system not available - skip event emission
            pass

    def _get_confidence_label(self, confidence: float) -> str:
        """
        Get human-readable confidence label.

        Args:
            confidence: Confidence score 0.0-1.0

        Returns:
            Label: CRITICAL/RED/YELLOW/GREEN

        Example:
            >>> label = service._get_confidence_label(0.85)
            >>> # Returns: "GREEN"
        """
        if confidence < 0.50:
            return "CRITICAL"
        elif confidence < 0.70:
            return "RED"
        elif confidence < 0.85:
            return "YELLOW"
        else:
            return "GREEN"
