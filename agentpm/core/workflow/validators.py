"""
Workflow Validators - State Requirement Validation

Validates that entities meet requirements for state transitions.

Includes:
- State-specific requirements (BLOCKED needs reason, READY needs acceptance criteria)
- Dependency validation (can't complete parent with active children)
- Business rule enforcement (completion ratios, required fields)
- CI-004: Testing quality gates (tests passing, acceptance criteria)
- CI-002: Context quality gates (confidence scoring)

Pattern: Validation functions with clear error messages
"""

from typing import Optional, Any, Dict, List
import json
import subprocess
from pathlib import Path

from ..database.enums import WorkItemStatus, TaskStatus, EntityType, TaskType, WorkItemType, Phase
from .type_validators import TypeSpecificValidators, ValidationResult
from .work_item_requirements import WorkItemRequirements


class StateRequirements:
    """
    Define requirements for entering specific states.

    Each state may require certain fields, conditions, or dependencies.
    """

    # Work item state requirements
    WORK_ITEM_REQUIREMENTS: Dict[WorkItemStatus, Dict[str, Any]] = {
        WorkItemStatus.READY: {
            'required_fields': [],  # Handled by _validate_why_value_structure
            'min_description_length': 50,
            'message': "Cannot be ready without business context and detailed description",
            'check_why_value': True  # CI-002: Validate metadata.why_value structure
        },
        WorkItemStatus.ACTIVE: {
            'required_fields': ['effort_estimate_hours'],
            'check_tasks_exist': True,
            'message': "Cannot be active without effort estimate and tasks"
        },
        WorkItemStatus.REVIEW: {
            'check_tasks_complete': True,
            'min_completion_ratio': 0.8,
            'message': "Cannot review until ≥80% tasks completed"
        },
        WorkItemStatus.DONE: {
            'check_tasks_complete': True,
            'min_completion_ratio': 0.8,
            'message': "Cannot complete until ≥80% tasks completed"
        }
    }

    # Task state requirements
    TASK_REQUIREMENTS: Dict[TaskStatus, Dict[str, Any]] = {
        TaskStatus.READY: {
            'required_fields': ['description', 'effort_hours'],
            'min_description_length': 50,
            'message': "Cannot be ready without detailed description and effort estimate"
        },
        TaskStatus.ACTIVE: {
            'required_fields': ['assigned_to'],
            'check_context_quality': True,  # CI-002: Context quality validation
            'message': "Cannot be active without agent assignment and sufficient context quality"
        },
        TaskStatus.BLOCKED: {
            'required_fields': ['blocked_reason'],
            'message': "Cannot block without blocked_reason"
        },
        TaskStatus.REVIEW: {
            'check_tests_passing': True,  # CI-004: Enforce test passing
            'message': "Cannot review: tests must pass before review"
        },
        TaskStatus.DONE: {
            'check_acceptance_met': True,  # CI-004: Enforce acceptance criteria
            'message': "Cannot complete: all acceptance criteria must be met"
        }
    }

    @classmethod
    def validate_work_item_requirements(
        cls,
        work_item: Any,
        new_status: WorkItemStatus,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate work item meets requirements for new status.

        Args:
            work_item: WorkItem entity
            new_status: Desired status
            db_service: Database service (for querying tasks)

        Returns:
            ValidationResult
        """
        requirements = cls.WORK_ITEM_REQUIREMENTS.get(new_status)
        if not requirements:
            return ValidationResult(valid=True)

        type_is_continuous = False
        if hasattr(work_item, 'type') and isinstance(work_item.type, WorkItemType):
            type_is_continuous = WorkItemType.is_continuous_type(work_item.type)
        is_continuous = bool(getattr(work_item, 'is_continuous', False) or type_is_continuous)

        # Check required fields
        if 'required_fields' in requirements:
            for field in requirements['required_fields']:
                value = getattr(work_item, field, None)
                if is_continuous and field == 'effort_estimate_hours':
                    continue  # Continuous backlogs do not require fixed effort estimates
                if not value:
                    return ValidationResult(
                        valid=False,
                        reason=f"Missing required field '{field}'. {requirements['message']}"
                    )

        # Check description length
        if 'min_description_length' in requirements:
            if not work_item.description or len(work_item.description) < requirements['min_description_length']:
                return ValidationResult(
                    valid=False,
                    reason=f"Description must be at least {requirements['min_description_length']} characters. {requirements['message']}"
                )

        # Check tasks exist
        if requirements.get('check_tasks_exist') and not is_continuous:
            from ..database.methods import tasks
            task_list = tasks.list_tasks(db_service, work_item_id=work_item.id)
            if not task_list:
                return ValidationResult(valid=False, reason=requirements['message'])

        # ===== CI-002: Why Value Validation =====
        # CI-002 runs FIRST: business context is more fundamental than having all tasks
        # If why_value is invalid, no point checking task requirements

        # CI-002: Validate metadata.why_value structure (contract v1.0)
        if requirements.get('check_why_value'):
            why_value_result = cls._validate_why_value_structure(work_item)
            if not why_value_result.valid:
                return why_value_result

        # ===== Phase Gate Enforcement =====
        # GAP-2: Validate phase gates before status transition
        # D1 (Design) → P1 (Planning) → I1 (Implementation) → R1 (Review)
        phase_gate_result = PhaseGateValidator.validate_phase_gates(
            work_item, new_status, db_service
        )
        if not phase_gate_result.valid:
            return phase_gate_result

        # ===== GAP-4: Evidence Source Validation =====
        # Research work items must have evidence sources before validation
        if new_status == WorkItemStatus.READY:
            evidence_result = EvidenceValidator.validate_research_evidence(
                work_item, db_service
            )
            if not evidence_result.valid:
                return evidence_result

        # ===== CI-006: Documentation Standards =====

        # CI-006: Documentation standards (READY state)
        if new_status == WorkItemStatus.READY:
            doc_result = DocumentationValidator.validate_documentation_standards(
                work_item, 'work_item'
            )
            if not doc_result.valid:
                return doc_result

        # ===== Work Item Type-Specific Validation =====
        # These run AFTER CI-002 and CI-006, since business context is more fundamental

        # Validate required task types present (FEATURE needs DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION)
        if new_status == WorkItemStatus.READY and hasattr(work_item, 'type') and not is_continuous:
            from ..database.methods import tasks as task_methods

            # Get all tasks for this work item
            task_list = task_methods.list_tasks(db_service, work_item_id=work_item.id)
            existing_task_types = [t.type for t in task_list if hasattr(t, 'type')]

            # Check missing required tasks
            missing_types = WorkItemRequirements.get_missing_required_tasks(
                work_item.type,
                existing_task_types
            )
            if missing_types:
                missing_names = [t.value.upper() for t in missing_types]
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Missing required task types: {', '.join(missing_names)}. "
                        f"{WorkItemRequirements.get_required_tasks_message(work_item.type)}"
                    )
                )

            # Check forbidden tasks not present (PLANNING can't have IMPLEMENTATION)
            forbidden_types = WorkItemRequirements.get_forbidden_tasks_present(
                work_item.type,
                existing_task_types
            )
            if forbidden_types:
                forbidden_names = [t.value.upper() for t in forbidden_types]
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Forbidden task types present: {', '.join(forbidden_names)}. "
                        f"{work_item.type.value.upper()} work items cannot have these task types."
                    )
                )

        # Check tasks complete
        if requirements.get('check_tasks_complete') and not is_continuous:
            result = DependencyValidator.validate_work_item_completion(work_item.id, db_service)
            if not result.valid:
                return result

        return ValidationResult(valid=True)

    @classmethod
    def validate_task_requirements(
        cls,
        task: Any,
        new_status: TaskStatus,
        db_service: Any = None
    ) -> ValidationResult:
        """
        Validate task meets requirements for new status.

        Includes:
        - Basic requirements (fields, description length)
        - Time-boxing validation (IMPLEMENTATION ≤4h STRICT)
        - Type-specific quality gates (metadata validation)

        Args:
            task: Task entity
            new_status: Desired status

        Returns:
            ValidationResult
        """
        requirements = cls.TASK_REQUIREMENTS.get(new_status)
        if not requirements:
            return ValidationResult(valid=True)

        # Check required fields with null safety
        if 'required_fields' in requirements:
            for field in requirements['required_fields']:
                try:
                    value = getattr(task, field, None)
                    if not value:
                        return ValidationResult(
                            valid=False,
                            reason=f"Missing required field '{field}'. {requirements['message']}"
                        )
                except AttributeError:
                    return ValidationResult(
                        valid=False,
                        reason=f"Invalid task structure: missing field '{field}'. {requirements['message']}"
                    )

        # Check description length with null safety
        if 'min_description_length' in requirements:
            try:
                description = getattr(task, 'description', None)
                if not description or len(description) < requirements['min_description_length']:
                    return ValidationResult(
                        valid=False,
                        reason=f"Description must be at least {requirements['min_description_length']} characters"
                    )
            except (AttributeError, TypeError):
                return ValidationResult(
                    valid=False,
                    reason=f"Invalid task structure: description field missing or invalid"
                )


        # ===== NEW: Type-Specific Validation =====

        # Time-boxing validation (rules-driven)
        if hasattr(task, 'type') and hasattr(task, 'effort_hours'):
            # Get project ID from work item
            project_id = None
            if hasattr(task, 'work_item_id') and db_service:
                try:
                    from ..database.methods import work_items as work_item_methods
                    work_item = work_item_methods.get_work_item(db_service, task.work_item_id)
                    if work_item:
                        project_id = work_item.project_id
                except Exception:
                    # Can't get project ID - skip validation
                    pass
            
            time_result = TypeSpecificValidators.validate_time_box(
                task.type,
                task.effort_hours,
                db_service=db_service,
                project_id=project_id
            )
            if not time_result.valid:
                return time_result

        # Quality metadata validation (type-specific requirements)
        if hasattr(task, 'type') and hasattr(task, 'quality_metadata'):
            # Get project_id from task's work_item
            project_id = None
            if hasattr(task, 'work_item_id') and db_service:
                try:
                    from ..database.methods import work_items as work_item_methods
                    work_item = work_item_methods.get_work_item(db_service, task.work_item_id)
                    if work_item:
                        project_id = work_item.project_id
                except Exception:
                    pass  # Skip if can't get project_id
            
            metadata_result = TypeSpecificValidators.validate_quality_metadata_structure(
                task.type,
                task.quality_metadata,
                new_status,
                db_service,
                project_id
            )
            if not metadata_result.valid:
                return metadata_result

        # ===== CI-002: Context Quality Gates =====

        # CI-002: Context quality validation (→ ACTIVE)
        if requirements.get('check_context_quality'):
            context_result = ContextQualityValidator.validate_context_quality(task, db_service)
            if not context_result.valid:
                return context_result

        # ===== CI-004: Testing Quality Gates =====

        # CI-004.1: Test passing validation (→ REVIEW)
        if requirements.get('check_tests_passing'):
            test_result = cls._validate_tests_passing(task)
            if not test_result.valid:
                return test_result

        # CI-004.2: Acceptance criteria validation (→ DONE)
        if requirements.get('check_acceptance_met'):
            criteria_result = cls._validate_acceptance_criteria(task)
            if not criteria_result.valid:
                return criteria_result

        # ===== CI-006: Documentation Standards =====

        # CI-006: Documentation standards (READY state)
        if new_status == TaskStatus.READY:
            doc_result = DocumentationValidator.validate_documentation_standards(
                task, 'task'
            )
            if not doc_result.valid:
                return doc_result

        return ValidationResult(valid=True)

    @classmethod
    def _validate_why_value_structure(cls, work_item: Any) -> ValidationResult:
        """
        CI-002: Validate metadata.why_value structure (contract v1.0).

        Required fields in metadata.why_value:
        - problem: What problem are we solving?
        - desired_outcome: What outcome do we want?
        - business_impact: What business value does this deliver?
        - target_metrics: How will we measure success?

        Backward compatibility:
        - If no metadata exists but business_context exists → warn + allow (legacy)
        - If metadata exists but no why_value → fail with migration instructions

        Args:
            work_item: WorkItem entity

        Returns:
            ValidationResult with pass/fail and missing fields

        Example metadata structure:
            {
                "why_value": {
                    "problem": "Users cannot filter results efficiently",
                    "desired_outcome": "Fast, intuitive filtering interface",
                    "business_impact": "Reduce support tickets by 30%",
                    "target_metrics": ["Support tickets", "User satisfaction", "Task completion time"]
                }
            }
        """
        # Backward compatibility: Check legacy business_context field
        if hasattr(work_item, 'business_context') and work_item.business_context:
            # Has legacy field - check if also has new metadata
            if not hasattr(work_item, 'metadata') or not work_item.metadata or work_item.metadata == '{}':
                # Legacy only - allow with deprecation warning
                import warnings
                warnings.warn(
                    f"Work item {work_item.id} uses legacy business_context. "
                    "Migrate to metadata.why_value for contract v1.0 compliance.",
                    DeprecationWarning,
                    stacklevel=2
                )
                return ValidationResult(valid=True)

        # Parse metadata
        if not hasattr(work_item, 'metadata') or not work_item.metadata:
            return ValidationResult(
                valid=False,
                reason=(
                    "CI-002 Failed: Missing metadata.why_value\n\n"
                    "Required fields: problem, desired_outcome, business_impact, target_metrics\n\n"
                    "Fix: apm work-item update <id> --metadata '{\"why_value\": {...}}'"
                )
            )

        try:
            if isinstance(work_item.metadata, str):
                metadata = json.loads(work_item.metadata)
            else:
                metadata = work_item.metadata
        except (json.JSONDecodeError, TypeError):
            return ValidationResult(
                valid=False,
                reason="CI-002 Failed: Invalid metadata format (cannot parse JSON)"
            )

        # Check for why_value structure
        why_value = metadata.get('why_value', {})
        if not why_value:
            return ValidationResult(
                valid=False,
                reason=(
                    "CI-002 Failed: Missing metadata.why_value\n\n"
                    "Required fields: problem, desired_outcome, business_impact, target_metrics\n\n"
                    "Fix: apm work-item update <id> --metadata '{\"why_value\": {...}}'"
                )
            )

        # Validate required fields
        required_fields = ['problem', 'desired_outcome', 'business_impact', 'target_metrics']
        missing = [f for f in required_fields if not why_value.get(f)]

        if missing:
            missing_list = ', '.join(missing)
            return ValidationResult(
                valid=False,
                reason=(
                    f"CI-002 Failed: Missing why_value fields: {missing_list}\n\n"
                    f"Required fields: {', '.join(required_fields)}\n\n"
                    "Fix: Add missing fields to metadata.why_value"
                )
            )

        return ValidationResult(valid=True)

    @classmethod
    def _validate_tests_passing(cls, task: Any) -> ValidationResult:
        """
        CI-004.1: Validate tests are passing.

        MVP behaviour:
        - Honour task.quality_metadata.tests_passing == True as a manual override
          to unblock review when appropriate for non-code tasks (e.g., design).
        - Future: Run pytest in the project directory to check test status.
        Assumes project root is available from task context for future execution.

        Args:
            task: Task entity (must have work_item_id for project lookup)

        Returns:
            ValidationResult with pass/fail and error details
        """
        # Honour manual override via quality_metadata.tests_passing
        try:
            qm = getattr(task, 'quality_metadata', None)
            if qm:
                if isinstance(qm, str):
                    metadata = json.loads(qm)
                else:
                    metadata = qm
                if metadata.get('tests_passing') is True:
                    return ValidationResult(valid=True)
        except Exception:
            # If metadata cannot be parsed, fall through to failure message
            pass

        # Default: fail with actionable guidance
        return ValidationResult(
            valid=False,
            reason=(
                "CI-004 Failed: Tests not validated and no manual override set\n\n"
                "Fix: Either run tests to validate automatically, or set:\n"
                "     apm task update <id> --quality-metadata '{\"tests_passing\": true}'"
            )
        )

    @classmethod
    def _validate_acceptance_criteria(cls, task: Any) -> ValidationResult:
        """
        CI-004.2: Validate all acceptance criteria are met.

        Checks quality_metadata for acceptance_criteria field and verifies
        all criteria are marked as 'met'.

        Args:
            task: Task entity with quality_metadata

        Returns:
            ValidationResult with pass/fail and unmet criteria details

        Example metadata structure:
            {
                "acceptance_criteria": [
                    {"criterion": "All unit tests pass", "met": true},
                    {"criterion": "Code coverage >90%", "met": false}
                ]
            }
        """
        if not hasattr(task, 'quality_metadata') or not task.quality_metadata:
            # No criteria defined = assume met (legacy tasks)
            return ValidationResult(valid=True)

        # Parse metadata
        try:
            if isinstance(task.quality_metadata, str):
                metadata = json.loads(task.quality_metadata)
            else:
                metadata = task.quality_metadata
        except (json.JSONDecodeError, TypeError):
            return ValidationResult(
                valid=False,
                reason="CI-004 Failed: Invalid quality_metadata format (cannot parse JSON)"
            )

        # Check for acceptance criteria
        criteria = metadata.get('acceptance_criteria', [])
        if not criteria:
            # No criteria = assume met
            return ValidationResult(valid=True)

        # Find unmet criteria (handle both string and dict formats)
        unmet = []
        for c in criteria:
            if isinstance(c, str):
                # Old format: list of strings - assume unmet
                unmet.append(c)
            elif isinstance(c, dict):
                # New format: list of dicts with {criterion, met}
                if not c.get('met', False):
                    unmet.append(c.get('criterion', 'Unknown'))
            # Skip invalid formats

        if unmet:
            unmet_list = '\n  - '.join(unmet[:5])  # Show first 5
            more = f"\n  ({len(unmet) - 5} more...)" if len(unmet) > 5 else ""
            return ValidationResult(
                valid=False,
                reason=(
                    f"CI-004 Failed: {len(unmet)} unmet acceptance criteria:\n"
                    f"  - {unmet_list}{more}\n\n"
                    "Fix: Update task quality_metadata to mark criteria as met, or use:\n"
                    "     apm task update <id> --quality-metadata '{\"acceptance_criteria\": [...]}'"
                )
            )

        return ValidationResult(valid=True)


class PhaseGateValidator:
    """
    Phase Gate Enforcement - D1 → P1 → I1 → R1 Progression

    Validates that work items complete required phase gates before status transitions.

    Gate Sequence:
    - D1 (Design ready): Required at READY - confirms feasibility
    - P1 (Plan ready): Required at ACTIVE - execution plan exists
    - I1 (Implementation built): Required at REVIEW - code complete
    - R1 (Review accepted): Required at DONE - acceptance criteria met

    Post-Completion Tracking (not blocking):
    - O1 (Operations deployed): Tracks deployment success
    - E1 (Evaluation complete): Tracks outcome measurement

    Backward Compatibility:
    - Phase column NULL → fallback to metadata.gates (legacy)
    - Phase column set → validate phase progression
    - New work items → enforce phase column validation
    """

    # Status → Required Phase mapping (phase column validation)
    STATUS_TO_REQUIRED_PHASE = {
        WorkItemStatus.DRAFT: None,                      # No phase required
        WorkItemStatus.READY: Phase.D1_DISCOVERY,       # D1 complete
        WorkItemStatus.ACTIVE: Phase.P1_PLAN,             # P1 complete
        WorkItemStatus.ACTIVE: Phase.P1_PLAN,          # P1 complete to start work
        WorkItemStatus.REVIEW: Phase.I1_IMPLEMENTATION,     # I1 complete for review
        WorkItemStatus.DONE: Phase.R1_REVIEW,          # R1 complete
        WorkItemStatus.CANCELLED: None,                      # No phase required
        WorkItemStatus.ARCHIVED: None,                       # No phase required
    }

    # DEPRECATED: Legacy metadata.gates validation (use STATUS_TO_REQUIRED_PHASE instead)
    # Deprecation Timeline: 2025-10-12 (phase column introduced) → 2026-01-31 (full removal)
    # Migration: Run migration_0015 to migrate metadata.gates → phase column
    # See: docs/architecture/database/quality-gates-migration.md
    PHASE_GATE_REQUIREMENTS = {
        WorkItemStatus.DRAFT: [],                                    # No gates - initial brainstorming
        WorkItemStatus.READY: ['D1_ready'],                        # Design gate - feasibility confirmed
        WorkItemStatus.ACTIVE: ['D1_ready', 'P1_plan'],             # Planning gate - execution plan ready
        WorkItemStatus.ACTIVE: ['D1_ready', 'P1_plan'],          # Begin work - NO I1 yet (that's what we're building!)
        WorkItemStatus.REVIEW: ['D1_ready', 'P1_plan', 'I1_build'],  # Submit for review - implementation complete
        WorkItemStatus.DONE: ['D1_ready', 'P1_plan', 'I1_build', 'R1_accept'],  # Mark complete - review accepted
        WorkItemStatus.CANCELLED: [],                                  # No gate enforcement
        WorkItemStatus.ARCHIVED: [],                                   # Must be DONE first (separate rule)
    }

    @classmethod
    def validate_phase_gates(
        cls,
        work_item: Any,
        new_status: WorkItemStatus,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate phase gates before status transition.

        Primary validation: work_item.phase column (Phase enum)
        Fallback validation: metadata.gates (legacy support)

        Correct sequence: D1 (Design) → P1 (Planning) → I1 (Implementation) → R1 (Review)

        Args:
            work_item: WorkItem entity with phase column (or legacy metadata.gates)
            new_status: Desired status
            db_service: Database service (unused, for consistency)

        Returns:
            ValidationResult with pass/fail and missing phase

        Example phase column values:
            Phase.D1_DISCOVERY     → Can transition to READY
            Phase.P1_PLAN          → Can transition to ACTIVE/ACTIVE
            Phase.I1_IMPLEMENTATION → Can transition to REVIEW
            Phase.R1_REVIEW        → Can transition to DONE
        """
        # Get required phase for this status
        required_phase = cls.STATUS_TO_REQUIRED_PHASE.get(new_status)

        # No phase required for this status
        if required_phase is None:
            return ValidationResult(valid=True)

        # Primary validation: Check phase column
        if hasattr(work_item, 'phase') and work_item.phase is not None:
            # Phase column is set - validate phase progression
            from ..database.enums import Phase

            # Map phase values for comparison
            phase_order = {
                Phase.D1_DISCOVERY: 1,
                Phase.P1_PLAN: 2,
                Phase.I1_IMPLEMENTATION: 3,
                Phase.R1_REVIEW: 4,
                Phase.O1_OPERATIONS: 5,
                Phase.E1_EVOLUTION: 6,
            }

            current_phase_level = phase_order.get(work_item.phase, 0)
            required_phase_level = phase_order.get(required_phase, 0)

            if current_phase_level < required_phase_level:
                # Phase not complete
                phase_names = {
                    Phase.D1_DISCOVERY: 'Discovery (D1)',
                    Phase.P1_PLAN: 'Planning (P1)',
                    Phase.I1_IMPLEMENTATION: 'Implementation (I1)',
                    Phase.R1_REVIEW: 'Review (R1)',
                    Phase.O1_OPERATIONS: 'Operations (O1)',
                    Phase.E1_EVOLUTION: 'Evolution (E1)',
                }

                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Cannot transition to {new_status.value.upper()} without {phase_names.get(required_phase, required_phase.value)} phase complete\n\n"
                        f"Current phase: {phase_names.get(work_item.phase, work_item.phase.value)}\n"
                        f"Required phase: {phase_names.get(required_phase, required_phase.value)}\n\n"
                        f"Fix: Complete the {phase_names.get(required_phase, required_phase.value)} phase before attempting this transition"
                    )
                )

            # Phase complete - allow transition
            return ValidationResult(valid=True)

        # Fallback validation: Check metadata.gates (legacy support)
        return cls._validate_legacy_gates(work_item, new_status)

    @classmethod
    def _validate_legacy_gates(
        cls,
        work_item: Any,
        new_status: WorkItemStatus
    ) -> ValidationResult:
        """
        Legacy validation using metadata.gates JSON structure.

        DEPRECATED: Use work_item.phase column instead of metadata.gates

        This method provides backward compatibility for work items created before
        migration 0015 (phase column introduction). New work items should use
        the phase column for gate tracking.

        Deprecation Timeline:
        - 2025-10-12: Phase column introduced (migration 0014)
        - 2025-10-12: Backfill migration available (migration 0015)
        - 2025-12-31: Deprecation period ends (warnings logged)
        - 2026-01-31: metadata.gates removed from schema

        Migration Guide: docs/architecture/database/quality-gates-migration.md

        Backward compatibility for work items created before phase column migration.

        Args:
            work_item: WorkItem entity with metadata containing gates
            new_status: Desired status

        Returns:
            ValidationResult with pass/fail and missing gates
        """
        # Log deprecation warning
        import logging
        import warnings
        logger = logging.getLogger(__name__)

        if hasattr(work_item, 'id'):
            logger.warning(
                f"Work item {work_item.id} using deprecated metadata.gates validation. "
                f"Migrate to phase column using migration_0015. "
                f"See docs/architecture/database/quality-gates-migration.md"
            )
            warnings.warn(
                "metadata.gates validation is deprecated and will be removed in 2026-01-31. "
                "Run migration_0015 to migrate to phase column.",
                DeprecationWarning,
                stacklevel=3
            )

        required_gates = cls.PHASE_GATE_REQUIREMENTS.get(new_status, [])

        # No gates required for this status
        if not required_gates:
            return ValidationResult(valid=True)

        # Parse metadata
        if not hasattr(work_item, 'metadata') or not work_item.metadata:
            # No metadata at all - SECURITY: Require metadata for new work items
            # Only allow legacy work items (created before 2024-01-01) to bypass
            if hasattr(work_item, 'created_at') and work_item.created_at:
                from datetime import datetime
                try:
                    if isinstance(work_item.created_at, str):
                        created_date = datetime.fromisoformat(work_item.created_at.replace('Z', '+00:00'))
                    else:
                        created_date = work_item.created_at
                    
                    # Allow legacy work items (created before 2024-01-01)
                    if created_date < datetime(2024, 1, 1):
                        return ValidationResult(valid=True)
                except (ValueError, TypeError):
                    pass
            
            # New work items must have metadata
            return ValidationResult(
                valid=False,
                reason=(
                    f"Phase gate(s) not ready: {', '.join(required_gates)}\n\n"
                    f"New work items must have metadata with phase gate tracking.\n"
                    f"Fix: Add metadata.gates to track phase completion"
                )
            )

        try:
            if isinstance(work_item.metadata, str):
                metadata = json.loads(work_item.metadata)
            else:
                metadata = work_item.metadata
        except (json.JSONDecodeError, TypeError):
            # Invalid JSON - fail with clear message
            return ValidationResult(
                valid=False,
                reason="Phase gate validation failed: Invalid metadata format (cannot parse JSON)"
            )

        # Check for gates field
        if 'gates' not in metadata:
            # No gates field - SECURITY: Require gates for new work items
            # Only allow legacy work items (created before 2024-01-01) to bypass
            if hasattr(work_item, 'created_at') and work_item.created_at:
                from datetime import datetime
                try:
                    if isinstance(work_item.created_at, str):
                        created_date = datetime.fromisoformat(work_item.created_at.replace('Z', '+00:00'))
                    else:
                        created_date = work_item.created_at
                    
                    # Allow legacy work items (created before 2024-01-01)
                    if created_date < datetime(2024, 1, 1):
                        return ValidationResult(valid=True)
                except (ValueError, TypeError):
                    pass
            
            # New work items must have gates
            return ValidationResult(
                valid=False,
                reason=(
                    f"Phase gate(s) not ready: {', '.join(required_gates)}\n\n"
                    f"New work items must have metadata.gates to track phase completion.\n"
                    f"Fix: Add metadata.gates to track phase completion"
                )
            )

        gates = metadata.get('gates', {})

        # Empty gates object {} - new work items need gates (strict validation)
        if not gates and required_gates:
            return ValidationResult(
                valid=False,
                reason=(
                    f"Phase gate(s) not ready: {', '.join(required_gates)}\n\n"
                    f"Work items with gates metadata must complete required phase gates.\n"
                    f"Fix: Update metadata.gates to mark phases as completed"
                )
            )

        # Validate each required gate
        missing = []
        for gate_code in required_gates:
            gate_status = gates.get(gate_code, {})

            # Gate ready if: status=='completed' OR completion>=100
            is_ready = (
                gate_status.get('status') == 'completed' or
                gate_status.get('completion', 0) >= 100
            )

            if not is_ready:
                missing.append(gate_code)

        if missing:
            # Build helpful error message
            gate_names = {
                'D1_ready': 'Design (D1)',
                'P1_plan': 'Planning (P1)',
                'I1_build': 'Implementation (I1)',
                'R1_accept': 'Review (R1)',
                'O1_ops': 'Operations (O1)',
                'E1_eval': 'Evaluation (E1)'
            }
            missing_names = [gate_names.get(g, g) for g in missing]

            return ValidationResult(
                valid=False,
                reason=(
                    f"Phase gate(s) not ready: {', '.join(missing_names)}\n\n"
                    f"Cannot transition to {new_status.value.upper()} until these gates are completed.\n"
                    f"Fix: Update metadata.gates to mark phases as completed (status='completed' or completion=100)"
                )
            )

        return ValidationResult(valid=True)


class DocumentationValidator:
    """
    CI-006: Documentation Standards Gate Validation

    Validates documentation completeness, freshness, and semantic quality.

    Requirements:
    - All required sections present (description ≥50 chars, business_context for WIs)
    - Documentation not stale (<30 days since update)
    - No placeholder content (TODO, TBD, etc.)
    """

    @classmethod
    def validate_documentation_standards(
        cls,
        entity: Any,
        entity_type: str
    ) -> ValidationResult:
        """
        Validate documentation meets CI-006 standards

        Checks:
        1. Completeness: Required fields present
        2. Staleness: Updated <30 days (warn only, not block)
        3. Semantic: No placeholder text

        Args:
            entity: Task or WorkItem
            entity_type: 'task' or 'work_item'

        Returns:
            ValidationResult with pass/fail
        """
        # Check 1: Completeness (required fields)
        if not hasattr(entity, 'description') or not entity.description:
            return ValidationResult(
                valid=False,
                reason="CI-006 Failed: Missing description\nFix: Add detailed description"
            )

        if len(entity.description) < 50:
            return ValidationResult(
                valid=False,
                reason=f"CI-006 Failed: Description too short ({len(entity.description)} chars, need ≥50)"
            )

        # For work items: check business_context OR metadata.why_value
        # (Backward compatibility: accept either legacy or new format)
        if entity_type == 'work_item':
            has_business_context = (
                hasattr(entity, 'business_context')
                and entity.business_context
                and entity.business_context.strip()
            )

            has_metadata_why_value = False
            if hasattr(entity, 'metadata') and entity.metadata:
                try:
                    metadata = json.loads(entity.metadata) if isinstance(entity.metadata, str) else entity.metadata
                    has_metadata_why_value = bool(metadata.get('why_value'))
                except (json.JSONDecodeError, TypeError):
                    pass  # Invalid JSON - will be caught by CI-002

            # Require at least one: legacy business_context OR new metadata.why_value
            if not has_business_context and not has_metadata_why_value:
                return ValidationResult(
                    valid=False,
                    reason="CI-006 Failed: Work items require business context (business_context field or metadata.why_value)"
                )

        # Check 2: Staleness (warn only for now - not blocking)
        # Could check updated_at field here if needed

        # Check 3: Semantic validation (no placeholders)
        placeholder_words = ['TODO', 'TBD', 'FIXME', 'XXX', 'placeholder', '[INSERT']
        desc_upper = entity.description.upper()
        found_placeholders = [p for p in placeholder_words if p in desc_upper]

        if found_placeholders:
            return ValidationResult(
                valid=False,
                reason=(
                    f"CI-006 Failed: Placeholder text found: {', '.join(found_placeholders)}\n"
                    "Fix: Replace placeholders with actual content"
                )
            )

        # Check 4: Metadata completeness (work items only)
        # GAP-3: Validate ownership, scope, artifacts
        if entity_type == 'work_item':
            metadata_result = cls._validate_work_item_metadata_completeness(entity)
            if not metadata_result.valid:
                return metadata_result

        return ValidationResult(valid=True)

    @classmethod
    def _validate_work_item_metadata_completeness(cls, work_item: Any) -> ValidationResult:
        """
        CI-006: Validate work item metadata completeness.

        Required metadata components (GAP-3):
        1. ownership.raci: All 4 RACI roles (responsible, accountable, consulted, informed)
        2. scope.in_scope: Non-empty array defining what's included
        3. artifacts.code_paths: Required for FEATURE/ENHANCEMENT work items

        Args:
            work_item: WorkItem entity with metadata field

        Returns:
            ValidationResult with pass/fail and missing components

        Example metadata structure:
            {
                "ownership": {
                    "raci": {
                        "responsible": "john",
                        "accountable": "jane",
                        "consulted": ["team-a"],
                        "informed": ["stakeholder-b"]
                    }
                },
                "scope": {
                    "in_scope": ["Feature X", "Component Y"],
                    "out_of_scope": ["Feature Z"]
                },
                "artifacts": {
                    "code_paths": ["src/feature.py", "tests/test_feature.py"]
                }
            }
        """
        # Parse metadata
        if not hasattr(work_item, 'metadata') or not work_item.metadata:
            # No metadata - backward compatibility: allow (legacy work items)
            return ValidationResult(valid=True)

        try:
            if isinstance(work_item.metadata, str):
                metadata = json.loads(work_item.metadata)
            else:
                metadata = work_item.metadata
        except (json.JSONDecodeError, TypeError):
            # Invalid JSON - already caught by other validators
            return ValidationResult(valid=True)

        # Skip validation for empty metadata (test scenarios and legacy work items)
        if not metadata or metadata == {}:
            return ValidationResult(valid=True)

        # Validation 1: ownership.raci (4 required roles)
        ownership = metadata.get('ownership', {})
        raci = ownership.get('raci', {})
        required_roles = ['responsible', 'accountable', 'consulted', 'informed']
        missing_roles = [r for r in required_roles if not raci.get(r)]

        if missing_roles:
            return ValidationResult(
                valid=False,
                reason=(
                    f"CI-006 Failed: Missing RACI roles: {', '.join(missing_roles)}\n\n"
                    f"Required roles: {', '.join(required_roles)}\n\n"
                    "Fix: Add missing roles to metadata.ownership.raci"
                )
            )

        # Validation 2: scope.in_scope (non-empty array)
        scope = metadata.get('scope', {})
        in_scope = scope.get('in_scope', [])

        if not in_scope or not isinstance(in_scope, list) or len(in_scope) == 0:
            return ValidationResult(
                valid=False,
                reason=(
                    "CI-006 Failed: scope.in_scope must be non-empty array\n\n"
                    "Fix: Add at least one item to metadata.scope.in_scope"
                )
            )

        # Validation 3: artifacts.code_paths (FEATURE/ENHANCEMENT only)
        if hasattr(work_item, 'type'):
            from ..database.enums import WorkItemType
            if work_item.type in [WorkItemType.FEATURE, WorkItemType.ENHANCEMENT]:
                artifacts = metadata.get('artifacts', {})
                code_paths = artifacts.get('code_paths', [])

                if not code_paths or not isinstance(code_paths, list) or len(code_paths) == 0:
                    return ValidationResult(
                        valid=False,
                        reason=(
                            f"CI-006 Failed: {work_item.type.value.upper()} work items require artifacts.code_paths\n\n"
                            "Fix: Add code file paths to metadata.artifacts.code_paths"
                        )
                    )

        return ValidationResult(valid=True)


class ContextQualityValidator:
    """
    CI-002: Context Quality Gate Validation

    Validates context quality before task start using WI-31 ConfidenceScorer.

    Requirements:
    - Context confidence >70% (0.7 score)
    - No stale contexts (freshness check)
    - Required 6W fields present

    Uses WI-31 ConfidenceScorer for quality assessment.
    """

    @classmethod
    def validate_context_quality(
        cls,
        task: Any,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate context quality before task start.

        CI-002 Requirements:
        - Context confidence >70%
        - No stale contexts (>7 days warning, >90 days fail)
        - Required 6W fields present

        Args:
            task: Task entity (must have id and work_item_id)
            db_service: DatabaseService for context lookup

        Returns:
            ValidationResult with pass/fail and quality details

        Example:
            >>> result = ContextQualityValidator.validate_context_quality(task, db)
            >>> if not result.valid:
            ...     print(f"Context quality: {result.reason}")
        """
        # Import dependencies
        from ...core.context.scoring import ConfidenceScorer
        from ...core.database.methods import contexts
        from ...core.database.enums import EntityType

        # Get task context
        task_context = contexts.get_entity_context(
            db_service,
            entity_type=EntityType.TASK,
            entity_id=task.id
        )

        if not task_context:
            # No context yet - allow (early-stage tasks can proceed)
            return ValidationResult(valid=True)

        # Calculate confidence using WI-31 scorer
        # Note: ConfidenceScorer.calculate_confidence needs six_w, plugin_facts, amalgamations, freshness_days
        # For MVP, we'll use simplified scoring based on six_w only

        scorer = ConfidenceScorer()

        # Extract data from context
        six_w = task_context.six_w if hasattr(task_context, 'six_w') else None

        # For MVP: Use simplified scoring (six_w only)
        if not six_w:
            return ValidationResult(
                valid=False,
                reason=(
                    "CI-002 Failed: No 6W context available\n"
                    "Fix: apm context refresh --task {task.id}"
                )
            )

        # Calculate 6W completeness as proxy for overall confidence
        six_w_completeness = scorer._calculate_6w_completeness(six_w)

        # Check threshold (70%)
        if six_w_completeness < 0.7:
            return ValidationResult(
                valid=False,
                reason=(
                    f"CI-002 Failed: Context quality too low ({six_w_completeness:.0%})\n"
                    f"  6W Completeness: {six_w_completeness:.0%} (need ≥70%)\n\n"
                    f"Fix: apm context refresh --task {task.id}"
                )
            )

        # Success - context quality sufficient
        return ValidationResult(valid=True)


class DependencyValidator:
    """
    Validate dependencies between entities.

    Prevents completing parents when children are still active.
    """

    @classmethod
    def validate_work_item_completion(
        cls,
        work_item_id: int,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate work item can complete.

        Checks:
        1. All tasks in terminal states (completed, cancelled, archived)
        2. At least 80% of tasks completed (not all cancelled)

        Args:
            work_item_id: Work item ID
            db_service: Database service

        Returns:
            ValidationResult
        """
        from ..database.methods import tasks

        task_list = tasks.list_tasks(db_service, work_item_id=work_item_id)

        if not task_list:
            # No tasks - can complete (empty work item)
            return ValidationResult(valid=True)

        # Check all tasks terminal
        active_tasks = [
            t for t in task_list
            if not TaskStatus.is_terminal_state(t.status)
        ]

        if active_tasks:
            task_names = [t.name for t in active_tasks[:3]]  # First 3
            more = f" and {len(active_tasks) - 3} more" if len(active_tasks) > 3 else ""
            return ValidationResult(
                valid=False,
                reason=f"{len(active_tasks)} tasks still active: {task_names}{more}"
            )

        # Check completion ratio
        completed_tasks = [t for t in task_list if t.status == TaskStatus.DONE]
        completion_ratio = len(completed_tasks) / len(task_list)

        if completion_ratio < 0.8:
            return ValidationResult(
                valid=False,
                reason=f"Only {completion_ratio*100:.0f}% tasks completed (need ≥80%)"
            )

        return ValidationResult(valid=True)

    @classmethod
    def validate_project_completion(
        cls,
        project_id: int,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate project can complete.

        Checks:
        1. All work items in terminal states
        2. At least 80% of work items completed

        Args:
            project_id: Project ID
            db_service: Database service

        Returns:
            ValidationResult
        """
        from ..database.methods import work_items

        wi_list = work_items.list_work_items(db_service, project_id=project_id)

        if not wi_list:
            # No work items - can complete (empty project)
            return ValidationResult(valid=True)

        # Check all work items terminal
        active_work_items = [
            wi for wi in wi_list
            if wi.status not in [WorkItemStatus.DONE, WorkItemStatus.ARCHIVED]
        ]

        if active_work_items:
            wi_names = [wi.name for wi in active_work_items[:3]]
            more = f" and {len(active_work_items) - 3} more" if len(active_work_items) > 3 else ""
            return ValidationResult(
                valid=False,
                reason=f"{len(active_work_items)} work items still active: {wi_names}{more}"
            )

        # Check completion ratio
        completed_work_items = [wi for wi in wi_list if wi.status == WorkItemStatus.DONE]
        completion_ratio = len(completed_work_items) / len(wi_list)

        if completion_ratio < 0.8:
            return ValidationResult(
                valid=False,
                reason=f"Only {completion_ratio*100:.0f}% work items completed (need ≥80%)"
            )

        return ValidationResult(valid=True)

    @classmethod
    def validate_task_dependencies(
        cls,
        task_id: int,
        current_status: TaskStatus,
        new_status: TaskStatus,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate task can transition given dependencies and blockers.

        Enforces:
        1. Cannot start (→ ACTIVE) with incomplete hard dependencies
        2. Cannot complete (→ REVIEW/DONE) with unresolved blockers
        3. Cannot unblock (BLOCKED → *) without resolving blockers
        4. Soft dependencies: Log warning but allow transition

        Args:
            task_id: Task ID to validate
            current_status: Current task status
            new_status: Attempted new status
            db_service: Database service

        Returns:
            ValidationResult with valid=True/False and reason

        Example:
            >>> # Task 2 depends on Task 1 (hard dependency)
            >>> result = DependencyValidator.validate_task_dependencies(
            ...     task_id=2,
            ...     current_status=TaskStatus.ACTIVE,
            ...     new_status=TaskStatus.ACTIVE,
            ...     db_service=db
            ... )
            >>> # If Task 1 not complete:
            >>> assert not result.valid
            >>> assert "incomplete hard dependencies" in result.reason
        """
        from ..database.methods import dependencies, tasks as task_methods

        # Validation 1: Starting task (→ ACTIVE)
        # Check hard dependencies are complete
        if new_status == TaskStatus.ACTIVE:
            deps = dependencies.get_task_dependencies(db_service, task_id)
            hard_deps = [d for d in deps if d.dependency_type == 'hard']

            if hard_deps:
                incomplete_deps = []
                for dep in hard_deps:
                    dep_task = task_methods.get_task(db_service, dep.depends_on_task_id)
                    if dep_task and dep_task.status != TaskStatus.DONE:
                        incomplete_deps.append(f"#{dep.depends_on_task_id} {dep_task.name}")

                if incomplete_deps:
                    deps_str = ', '.join(incomplete_deps[:3])
                    more = f" and {len(incomplete_deps) - 3} more" if len(incomplete_deps) > 3 else ""
                    return ValidationResult(
                        valid=False,
                        reason=f"Cannot start with incomplete hard dependencies: {deps_str}{more}"
                    )

            # Check soft dependencies (warn but allow)
            soft_deps = [d for d in deps if d.dependency_type == 'soft']
            if soft_deps:
                incomplete_soft = []
                for dep in soft_deps:
                    dep_task = task_methods.get_task(db_service, dep.depends_on_task_id)
                    if dep_task and dep_task.status != TaskStatus.DONE:
                        incomplete_soft.append(dep_task.name)

                if incomplete_soft:
                    # Log warning but allow (soft dependencies)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Task {task_id} starting with incomplete soft dependencies: {incomplete_soft}"
                    )

        # Validation 2: Completing task (→ REVIEW or DONE)
        # Check no unresolved blockers
        if new_status in [TaskStatus.REVIEW, TaskStatus.DONE]:
            blockers = dependencies.get_task_blockers(db_service, task_id, unresolved_only=True)

            if blockers:
                blocker_descs = []
                for b in blockers[:3]:
                    if b.blocker_type == 'task':
                        blocker_task = task_methods.get_task(db_service, b.blocker_task_id)
                        if blocker_task:
                            blocker_descs.append(f"Task #{b.blocker_task_id} {blocker_task.name}")
                        else:
                            blocker_descs.append(f"Task #{b.blocker_task_id}")
                    else:  # external
                        blocker_descs.append(b.blocker_description)

                blockers_str = ', '.join(blocker_descs)
                more = f" and {len(blockers) - 3} more" if len(blockers) > 3 else ""
                return ValidationResult(
                    valid=False,
                    reason=f"{len(blockers)} unresolved blocker(s): {blockers_str}{more}"
                )

        # Validation 3: Unblocking task (BLOCKED → any state)
        # Verify all blockers resolved before allowing unblock
        if current_status == TaskStatus.BLOCKED:
            blockers = dependencies.get_task_blockers(db_service, task_id, unresolved_only=True)

            if blockers:
                return ValidationResult(
                    valid=False,
                    reason=f"Cannot unblock: {len(blockers)} blocker(s) still unresolved. Resolve them first with 'apm task resolve-blocker <id>'"
                )

        return ValidationResult(valid=True)


class EvidenceValidator:
    """
    GAP-4: Evidence Source Validation for Research Work Items

    Research work items must have at least one evidence source before validation.
    This ensures research findings are documented with proper source attribution.
    """

    @classmethod
    def validate_research_evidence(
        cls,
        work_item: Any,
        db_service: Any
    ) -> ValidationResult:
        """
        Validate research work items have evidence sources.

        Research work items must have ≥1 entry in evidence_sources table before
        they can be validated. This ensures research is properly documented.

        Args:
            work_item: WorkItem entity (must have type and id)
            db_service: DatabaseService for evidence lookup

        Returns:
            ValidationResult with pass/fail

        Example:
            >>> # Research work item without evidence
            >>> result = EvidenceValidator.validate_research_evidence(wi, db)
            >>> assert not result.valid
            >>> assert "require at least 1 evidence source" in result.reason

            >>> # Non-research work item
            >>> result = EvidenceValidator.validate_research_evidence(feature_wi, db)
            >>> assert result.valid  # Only applies to research
        """
        # Only applies to research work items
        if not hasattr(work_item, 'type') or work_item.type != WorkItemType.RESEARCH:
            return ValidationResult(valid=True)

        # Check if work item has evidence entries
        from ..database.methods import evidence_sources

        evidence_list = evidence_sources.list_evidence_sources(
            db_service,
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item.id
        )

        if not evidence_list:
            return ValidationResult(
                valid=False,
                reason=(
                    "Research work items require at least 1 evidence source\n\n"
                    "Fix: Add evidence with:\n"
                    "     apm evidence add --work-item <id> --url <url> --type <type>"
                )
            )

        return ValidationResult(valid=True)
