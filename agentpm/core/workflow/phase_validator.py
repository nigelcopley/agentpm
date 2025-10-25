"""
Phase Validator - Type-Specific Phase Progression Logic

Validates that work items follow correct phase sequences based on their type.
Different work item types require different lifecycle phases.

Phase Codes:
- D1_discovery: Research and discovery phase
- P1_plan: Planning and design phase
- I1_implementation: Build and implementation phase
- R1_review: Review and validation phase
- O1_ops: Operations and deployment phase
- E1_eval: Evaluation and metrics phase

Integration: Works with PhaseGateValidator in validators.py to ensure
both phase sequence AND gate completion requirements are met.

Enhanced with Phase Requirements System:
- Type-specific phase requirements and completion criteria
- DEPRECATED: Required tasks for each phase (use outcome-based validation instead)
- Evidence-based validation
- Instructions and guidance for each phase

Philosophy Change (2025-10-17):
    OLD: Required task types per phase (rigid enforcement)
    NEW: Outcome-based validation (flexible, checks results not categories)

    Phase gates now validate OUTCOMES:
    - P1: "Do we have a plan?" not "Do we have DESIGN tasks?"
    - I1: "Is code complete and tested?" not "Are IMPLEMENTATION tasks DONE?"

    Users create tasks that make sense for their work.
    Phase gates check if the work is actually done.
"""

from typing import List, Optional, Set, Dict, Any
from dataclasses import dataclass
from ..database.enums import WorkItemType, Phase, TaskType


@dataclass
class PhaseRequirement:
    """Individual requirement for a phase"""
    name: str
    description: str
    required: bool = True
    evidence_required: bool = False
    validation_criteria: List[str] = None
    
    def __post_init__(self):
        if self.validation_criteria is None:
            self.validation_criteria = []


@dataclass
class PhaseRequirements:
    """Complete requirements for a specific phase and work item type"""
    phase: Phase
    work_item_type: WorkItemType
    required_tasks: List[TaskType]
    completion_criteria: List[PhaseRequirement]
    instructions: str
    estimated_duration_hours: Optional[int] = None
    
    def get_required_task_types(self) -> Set[TaskType]:
        """Get set of required task types for this phase"""
        return set(self.required_tasks)
    
    def get_completion_requirements(self) -> List[PhaseRequirement]:
        """Get list of completion requirements"""
        return [req for req in self.completion_criteria if req.required]


@dataclass
class PhaseValidationResult:
    """Result of phase validation check (test-compatible API)."""
    is_valid: bool
    error_message: Optional[str] = None
    missing_requirements: List[str] = None
    phase_requirements: Optional[PhaseRequirements] = None
    
    def __post_init__(self):
        if self.missing_requirements is None:
            self.missing_requirements = []


class PhaseValidator:
    """
    Type-specific phase progression validation.

    Enforces correct phase sequences based on work item type.
    Some types skip phases (e.g., BUGFIX skips discovery), while
    others have the full lifecycle (e.g., FEATURE).
    
    Enhanced with Phase Requirements System:
    - Type-specific phase requirements and completion criteria
    - Required tasks for each phase
    - Evidence-based validation
    - Instructions and guidance for each phase
    """

    # Type-specific phase sequences (ordered, all phases in sequence)
    PHASE_SEQUENCES = {
        WorkItemType.FEATURE: [
            Phase.D1_DISCOVERY,      # Research and discovery
            Phase.P1_PLAN,           # Planning and design
            Phase.I1_IMPLEMENTATION, # Build implementation
            Phase.R1_REVIEW,         # Review and validation
            Phase.O1_OPERATIONS,     # Deploy to operations
            Phase.E1_EVOLUTION       # Evaluate outcomes
        ],
        WorkItemType.ENHANCEMENT: [
            Phase.D1_DISCOVERY,      # Enhancement analysis
            Phase.P1_PLAN,           # Enhancement plan
            Phase.I1_IMPLEMENTATION, # Build enhancement
            Phase.R1_REVIEW,         # Review enhancement
            Phase.E1_EVOLUTION       # Skip O1, go straight to evolution
        ],
        WorkItemType.BUGFIX: [
            Phase.I1_IMPLEMENTATION, # Fix implementation (skip discovery - bug already known)
            Phase.R1_REVIEW          # Fix review (no ops/evolution)
        ],
        WorkItemType.RESEARCH: [
            Phase.D1_DISCOVERY,      # Research phase
            Phase.P1_PLAN            # Analysis plan (no implementation)
        ],
        WorkItemType.PLANNING: [
            Phase.D1_DISCOVERY,      # Gather requirements
            Phase.P1_PLAN            # Create plan/design (no implementation)
        ],
        WorkItemType.ANALYSIS: [
            Phase.D1_DISCOVERY,      # Analysis and investigation
            Phase.P1_PLAN            # Analysis plan and methodology (no implementation)
        ],
        WorkItemType.REFACTORING: [
            Phase.P1_PLAN,           # Refactor plan (skip discovery)
            Phase.I1_IMPLEMENTATION, # Refactor code
            Phase.R1_REVIEW          # Code review (no deployment - internal change)
        ],
        WorkItemType.INFRASTRUCTURE: [
            Phase.D1_DISCOVERY,      # Infrastructure needs
            Phase.P1_PLAN,           # Infrastructure design
            Phase.I1_IMPLEMENTATION, # Build infrastructure
            Phase.R1_REVIEW,         # Review infrastructure
            Phase.O1_OPERATIONS      # Deploy infrastructure (no evolution)
        ],
        WorkItemType.MAINTENANCE: [
            Phase.I1_IMPLEMENTATION, # Maintenance execution
            Phase.O1_OPERATIONS,     # Operate/monitor systems
            Phase.E1_EVOLUTION       # Track improvements over time
        ],
        WorkItemType.MONITORING: [
            Phase.O1_OPERATIONS,     # Active monitoring & alert response
            Phase.E1_EVOLUTION       # Iterate on observability
        ],
        WorkItemType.DOCUMENTATION: [
            Phase.I1_IMPLEMENTATION, # Produce/refresh documentation
            Phase.R1_REVIEW,         # Review doc set
            Phase.E1_EVOLUTION       # Continuous improvement
        ],
        WorkItemType.SECURITY: [
            Phase.D1_DISCOVERY,      # Threat modeling / discovery
            Phase.P1_PLAN,           # Plan mitigations
            Phase.I1_IMPLEMENTATION, # Implement controls
            Phase.R1_REVIEW,         # Review & validate controls
            Phase.O1_OPERATIONS,     # Ongoing monitoring
            Phase.E1_EVOLUTION       # Iterate based on findings
        ],
        WorkItemType.FIX_BUGS_ISSUES: [
            Phase.I1_IMPLEMENTATION, # Implement fixes
            Phase.R1_REVIEW,         # Validate fixes
            Phase.O1_OPERATIONS,     # Monitor regressions
            Phase.E1_EVOLUTION       # Feed learnings forward
        ],
    }

    # Legacy phase codes (for backward compatibility with existing gate system)
    # Maps new phase codes to existing gate codes in metadata.gates
    LEGACY_PHASE_MAP = {
        'D1_discovery': 'D1_ready',
        'P1_plan': 'P1_plan',
        'I1_implementation': 'I1_build',
        'R1_review': 'R1_accept',
        'O1_ops': 'O1_ops',
        'E1_eval': 'E1_eval'
    }
    
    # Phase Requirements Registry
    # Defines type-specific requirements for each phase
    PHASE_REQUIREMENTS: Dict[tuple, PhaseRequirements] = {}
    
    def __init__(self):
        """Initialize phase validator with requirements registry"""
        if not self.PHASE_REQUIREMENTS:
            self._load_phase_requirements()
    
    def _load_phase_requirements(self):
        """Load phase requirements for all work item types and phases"""
        
        # ========== DISCOVERY PHASE (D1) ==========
        
        # FEATURE Discovery Requirements
        self.PHASE_REQUIREMENTS[(Phase.D1_DISCOVERY, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.D1_DISCOVERY,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[
                TaskType.ANALYSIS,  # Requirements analysis
                TaskType.RESEARCH,  # Market research
                TaskType.DESIGN,    # High-level design
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="user_stories_defined",
                    description="User stories and acceptance criteria defined",
                    evidence_required=True,
                    validation_criteria=["acceptance_criteria_present", "user_stories_complete"]
                ),
                PhaseRequirement(
                    name="market_validation",
                    description="Market need and user demand validated",
                    evidence_required=True,
                    validation_criteria=["market_research_complete", "user_feedback_collected"]
                ),
                PhaseRequirement(
                    name="technical_feasibility",
                    description="Technical approach validated and feasible",
                    evidence_required=True,
                    validation_criteria=["architecture_designed", "technical_risks_assessed"]
                ),
                PhaseRequirement(
                    name="business_value_confirmed",
                    description="Business value and ROI confirmed",
                    evidence_required=True,
                    validation_criteria=["business_case_complete", "success_metrics_defined"]
                )
            ],
            instructions="Define user needs, validate market fit, gather requirements, assess technical feasibility",
            estimated_duration_hours=16
        )
        
        # RESEARCH Discovery Requirements
        self.PHASE_REQUIREMENTS[(Phase.D1_DISCOVERY, WorkItemType.RESEARCH)] = PhaseRequirements(
            phase=Phase.D1_DISCOVERY,
            work_item_type=WorkItemType.RESEARCH,
            required_tasks=[
                TaskType.RESEARCH,  # Literature review
                TaskType.ANALYSIS,  # Research questions
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="research_questions_defined",
                    description="Clear research questions and hypotheses defined",
                    evidence_required=True,
                    validation_criteria=["research_questions_present", "hypotheses_formed"]
                ),
                PhaseRequirement(
                    name="literature_review_complete",
                    description="Existing knowledge and gaps identified",
                    evidence_required=True,
                    validation_criteria=["literature_summary_complete", "gap_analysis_done"]
                ),
                PhaseRequirement(
                    name="methodology_selected",
                    description="Research methodology and approach selected",
                    evidence_required=True,
                    validation_criteria=["methodology_defined", "data_collection_planned"]
                ),
                PhaseRequirement(
                    name="success_metrics_defined",
                    description="Success criteria and evaluation metrics defined",
                    evidence_required=True,
                    validation_criteria=["success_criteria_set", "evaluation_plan_ready"]
                )
            ],
            instructions="Define research scope, review existing knowledge, form hypotheses, select methodology",
            estimated_duration_hours=12
        )
        
        # BUGFIX Discovery Requirements
        self.PHASE_REQUIREMENTS[(Phase.D1_DISCOVERY, WorkItemType.BUGFIX)] = PhaseRequirements(
            phase=Phase.D1_DISCOVERY,
            work_item_type=WorkItemType.BUGFIX,
            required_tasks=[
                TaskType.ANALYSIS,  # Bug analysis
                TaskType.RESEARCH,  # Root cause investigation
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="bug_reproduction",
                    description="Bug can be consistently reproduced",
                    evidence_required=True,
                    validation_criteria=["reproduction_steps_documented", "test_case_created"]
                ),
                PhaseRequirement(
                    name="root_cause_identified",
                    description="Root cause of the bug identified",
                    evidence_required=True,
                    validation_criteria=["root_cause_analysis_complete", "impact_assessment_done"]
                ),
                PhaseRequirement(
                    name="scope_defined",
                    description="Scope of fix and affected systems defined",
                    evidence_required=True,
                    validation_criteria=["affected_systems_identified", "fix_scope_defined"]
                ),
                PhaseRequirement(
                    name="priority_assessed",
                    description="Bug priority and urgency assessed",
                    evidence_required=True,
                    validation_criteria=["priority_level_set", "urgency_justified"]
                )
            ],
            instructions="Reproduce bug, identify root cause, assess impact and priority",
            estimated_duration_hours=8
        )
        
        # ========== PLANNING PHASE (P1) ==========
        
        # FEATURE Planning Requirements
        # NOTE: required_tasks field is DEPRECATED as of 2025-10-17
        # Phase gates now use outcome-based validation (see P1GateValidator)
        self.PHASE_REQUIREMENTS[(Phase.P1_PLAN, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.P1_PLAN,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[],  # DEPRECATED: Use outcome-based validation instead
            completion_criteria=[
                PhaseRequirement(
                    name="technical_design_complete",
                    description="Technical architecture and design complete",
                    evidence_required=True,
                    validation_criteria=["architecture_designed", "design_reviewed"]
                ),
                PhaseRequirement(
                    name="tasks_created",
                    description="All implementation tasks created and estimated",
                    evidence_required=True,
                    validation_criteria=["tasks_breakdown_complete", "effort_estimated"]
                ),
                PhaseRequirement(
                    name="dependencies_mapped",
                    description="Task dependencies and sequencing defined",
                    evidence_required=True,
                    validation_criteria=["dependency_graph_created", "critical_path_identified"]
                ),
                PhaseRequirement(
                    name="risks_assessed",
                    description="Technical and project risks identified and mitigated",
                    evidence_required=True,
                    validation_criteria=["risk_register_complete", "mitigation_plans_ready"]
                )
            ],
            instructions="Create technical design, break down work into tasks, plan dependencies and risks",
            estimated_duration_hours=12
        )
        
        # RESEARCH Planning Requirements
        self.PHASE_REQUIREMENTS[(Phase.P1_PLAN, WorkItemType.RESEARCH)] = PhaseRequirements(
            phase=Phase.P1_PLAN,
            work_item_type=WorkItemType.RESEARCH,
            required_tasks=[
                TaskType.PLANNING,      # Research plan
                TaskType.ANALYSIS,      # Data analysis plan
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="research_plan_complete",
                    description="Detailed research execution plan created",
                    evidence_required=True,
                    validation_criteria=["research_plan_documented", "timeline_established"]
                ),
                PhaseRequirement(
                    name="data_collection_planned",
                    description="Data collection methods and tools selected",
                    evidence_required=True,
                    validation_criteria=["data_sources_identified", "collection_methods_defined"]
                ),
                PhaseRequirement(
                    name="analysis_approach_defined",
                    description="Data analysis approach and tools selected",
                    evidence_required=True,
                    validation_criteria=["analysis_methods_selected", "tools_evaluated"]
                )
            ],
            instructions="Create detailed research plan, define data collection and analysis approach",
            estimated_duration_hours=8
        )
        
        # ========== IMPLEMENTATION PHASE (I1) ==========
        
        # FEATURE Implementation Requirements
        # NOTE: required_tasks field is DEPRECATED as of 2025-10-17
        # Phase gates now use outcome-based validation (see I1GateValidator)
        self.PHASE_REQUIREMENTS[(Phase.I1_IMPLEMENTATION, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.I1_IMPLEMENTATION,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[],  # DEPRECATED: Use outcome-based validation instead
            completion_criteria=[
                PhaseRequirement(
                    name="implementation_complete",
                    description="All implementation tasks completed",
                    evidence_required=True,
                    validation_criteria=["code_implemented", "unit_tests_passing"]
                ),
                PhaseRequirement(
                    name="testing_complete",
                    description="All tests written and passing",
                    evidence_required=True,
                    validation_criteria=["test_coverage_adequate", "integration_tests_passing"]
                ),
                PhaseRequirement(
                    name="documentation_complete",
                    description="Code and user documentation complete",
                    evidence_required=True,
                    validation_criteria=["code_documented", "user_docs_updated"]
                ),
                PhaseRequirement(
                    name="code_reviewed",
                    description="Code reviewed and approved",
                    evidence_required=True,
                    validation_criteria=["code_review_complete", "review_feedback_addressed"]
                )
            ],
            instructions="Implement feature, write tests, document code, complete code review",
            estimated_duration_hours=32
        )
        
        # Note: RESEARCH and PLANNING work items skip I1_IMPLEMENTATION phase
        
        # ========== REVIEW PHASE (R1) ==========
        
        # FEATURE Review Requirements
        self.PHASE_REQUIREMENTS[(Phase.R1_REVIEW, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.R1_REVIEW,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[
                TaskType.REVIEW,         # Quality review
                TaskType.TESTING,        # User acceptance testing
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="quality_review_passed",
                    description="Quality review completed and passed",
                    evidence_required=True,
                    validation_criteria=["quality_checklist_complete", "review_approved"]
                ),
                PhaseRequirement(
                    name="acceptance_criteria_met",
                    description="All acceptance criteria verified",
                    evidence_required=True,
                    validation_criteria=["acceptance_tests_passing", "criteria_validated"]
                ),
                PhaseRequirement(
                    name="stakeholder_approval",
                    description="Stakeholder approval obtained",
                    evidence_required=True,
                    validation_criteria=["stakeholder_reviewed", "approval_documented"]
                )
            ],
            instructions="Complete quality review, verify acceptance criteria, obtain stakeholder approval",
            estimated_duration_hours=8
        )
        
        # RESEARCH Review Requirements
        self.PHASE_REQUIREMENTS[(Phase.R1_REVIEW, WorkItemType.RESEARCH)] = PhaseRequirements(
            phase=Phase.R1_REVIEW,
            work_item_type=WorkItemType.RESEARCH,
            required_tasks=[
                TaskType.REVIEW,         # Research review
                TaskType.DOCUMENTATION,  # Research documentation
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="research_reviewed",
                    description="Research methodology and findings reviewed",
                    evidence_required=True,
                    validation_criteria=["methodology_validated", "findings_verified"]
                ),
                PhaseRequirement(
                    name="documentation_complete",
                    description="Research findings documented and published",
                    evidence_required=True,
                    validation_criteria=["research_paper_complete", "findings_documented"]
                ),
                PhaseRequirement(
                    name="peer_review_passed",
                    description="Peer review completed and passed",
                    evidence_required=True,
                    validation_criteria=["peer_review_complete", "feedback_addressed"]
                )
            ],
            instructions="Review research methodology and findings, document results, complete peer review",
            estimated_duration_hours=6
        )
        
        # ========== OPERATIONS PHASE (O1) ==========
        
        # FEATURE Operations Requirements
        self.PHASE_REQUIREMENTS[(Phase.O1_OPERATIONS, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.O1_OPERATIONS,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[
                TaskType.DEPLOYMENT,     # Deployment
                TaskType.MAINTENANCE,    # Monitoring setup
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="deployment_complete",
                    description="Feature deployed to production",
                    evidence_required=True,
                    validation_criteria=["deployment_successful", "rollback_plan_ready"]
                ),
                PhaseRequirement(
                    name="monitoring_active",
                    description="Monitoring and alerting active",
                    evidence_required=True,
                    validation_criteria=["monitoring_configured", "alerts_tested"]
                ),
                PhaseRequirement(
                    name="user_training_complete",
                    description="User training and documentation complete",
                    evidence_required=True,
                    validation_criteria=["training_delivered", "user_docs_updated"]
                )
            ],
            instructions="Deploy feature, setup monitoring, complete user training",
            estimated_duration_hours=6
        )
        
        # Note: RESEARCH and PLANNING work items skip O1_OPERATIONS phase
        
        # ========== EVOLUTION PHASE (E1) ==========
        
        # FEATURE Evolution Requirements
        self.PHASE_REQUIREMENTS[(Phase.E1_EVOLUTION, WorkItemType.FEATURE)] = PhaseRequirements(
            phase=Phase.E1_EVOLUTION,
            work_item_type=WorkItemType.FEATURE,
            required_tasks=[
                TaskType.ANALYSIS,       # Performance analysis
                TaskType.MAINTENANCE,    # Usage monitoring
            ],
            completion_criteria=[
                PhaseRequirement(
                    name="performance_analyzed",
                    description="Feature performance and usage analyzed",
                    evidence_required=True,
                    validation_criteria=["performance_metrics_collected", "usage_analyzed"]
                ),
                PhaseRequirement(
                    name="feedback_collected",
                    description="User feedback collected and analyzed",
                    evidence_required=True,
                    validation_criteria=["feedback_surveyed", "improvements_identified"]
                ),
                PhaseRequirement(
                    name="evolution_planned",
                    description="Future evolution and improvements planned",
                    evidence_required=True,
                    validation_criteria=["roadmap_updated", "improvements_prioritized"]
                )
            ],
            instructions="Analyze performance and usage, collect feedback, plan future evolution",
            estimated_duration_hours=4
        )

    @classmethod
    def validate_phase_progression(
        cls,
        work_item: any,
        new_phase: str
    ) -> PhaseValidationResult:
        """
        Validate if work item can transition to new phase.

        Checks:
        1. Phase exists in type's sequence
        2. All prior phases are completed (sequential progression)
        3. Cannot skip required phases

        Args:
            work_item: WorkItem entity (must have type and metadata.gates)
            new_phase: Phase code to transition to (e.g., 'I1_implementation')

        Returns:
            ValidationResult with pass/fail and reason

        Example:
            >>> # RESEARCH work item trying to enter implementation
            >>> result = PhaseValidator.validate_phase_progression(wi, 'I1_implementation')
            >>> assert not result.valid
            >>> assert "RESEARCH work items cannot enter I1_implementation phase" in result.reason
        """
        if not hasattr(work_item, 'type'):
            return PhaseValidationResult(
                is_valid=False,
                error_message="Work item missing type field"
            )

        # Get allowed sequence for this type
        allowed_sequence = cls.PHASE_SEQUENCES.get(work_item.type)
        if not allowed_sequence:
            return PhaseValidationResult(
                is_valid=False,
                error_message=f"Unknown work item type: {work_item.type}"
            )

        # Check if phase is allowed for this type
        if new_phase not in allowed_sequence:
            allowed_phases = ', '.join(allowed_sequence)
            phase_names = {
                'D1_discovery': 'Discovery',
                'P1_plan': 'Planning',
                'I1_implementation': 'Implementation',
                'R1_review': 'Review',
                'O1_operations': 'Operations',
                'E1_evolution': 'Evaluation'
            }
            phase_name = phase_names.get(new_phase, new_phase)

            return PhaseValidationResult(
                is_valid=False,
                error_message=(
                    f"{work_item.type.value.upper()} work items cannot enter {phase_name} ({new_phase}) phase.\n\n"
                    f"Allowed phases for {work_item.type.value.upper()}: {allowed_phases}\n\n"
                    f"Fix: Use a phase from the allowed sequence for this work item type"
                )
            )

        # Check sequential progression (all prior phases must be complete)
        phase_index = allowed_sequence.index(new_phase)
        if phase_index > 0:
            # Need to check prior phases are complete
            prior_phases = allowed_sequence[:phase_index]

            # Get current gate status from metadata
            import json
            if not hasattr(work_item, 'metadata') or not work_item.metadata:
                # No metadata - assume early stage, allow first phase only
                if phase_index == 0:
                    return PhaseValidationResult(is_valid=True)
                return PhaseValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Cannot enter {new_phase} without completing prior phases: {', '.join(prior_phases)}\n\n"
                        "Fix: Complete prior phases first, or add metadata.gates to track progress"
                    )
                )

            try:
                if isinstance(work_item.metadata, str):
                    metadata = json.loads(work_item.metadata)
                else:
                    metadata = work_item.metadata
            except (json.JSONDecodeError, TypeError):
                return PhaseValidationResult(
                    is_valid=False,
                    error_message="Invalid metadata format (cannot parse JSON)"
                )

            gates = metadata.get('gates', {})

            # Check each prior phase is completed
            incomplete_phases = []
            for prior_phase in prior_phases:
                # Map to legacy gate code if needed
                gate_code = cls.LEGACY_PHASE_MAP.get(prior_phase, prior_phase)
                gate_status = gates.get(gate_code, {})

                # Phase complete if: status=='completed' OR completion>=100
                is_complete = (
                    gate_status.get('status') == 'completed' or
                    gate_status.get('completion', 0) >= 100
                )

                if not is_complete:
                    incomplete_phases.append(prior_phase)

            if incomplete_phases:
                phase_names = {
                    'D1_discovery': 'Discovery (D1)',
                    'P1_plan': 'Planning (P1)',
                    'I1_implementation': 'Implementation (I1)',
                    'R1_review': 'Review (R1)',
                    'O1_operations': 'Operations (O1)',
                    'E1_evolution': 'Evaluation (E1)'
                }
                incomplete_names = [phase_names.get(p, p) for p in incomplete_phases]

                return PhaseValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Cannot skip required phases: {', '.join(incomplete_names)}\n\n"
                        f"Must complete phases in order: {' → '.join([phase_names.get(p, p) for p in allowed_sequence])}\n\n"
                        "Fix: Complete incomplete phases before progressing"
                    )
                )

        return PhaseValidationResult(is_valid=True)

    @classmethod
    def get_allowed_next_phases(cls, work_item: any) -> List[str]:
        """
        Get list of valid next phases for work item.

        Returns phases that:
        1. Are in the type's sequence
        2. Come after current phase (based on completed gates)
        3. Have all prior phases complete

        Args:
            work_item: WorkItem entity (must have type and metadata.gates)

        Returns:
            List of allowed phase codes

        Example:
            >>> # FEATURE work item with D1 complete
            >>> phases = PhaseValidator.get_allowed_next_phases(wi)
            >>> assert 'P1_plan' in phases
            >>> assert 'I1_implementation' not in phases  # Prior phase P1 not complete
        """
        if not hasattr(work_item, 'type'):
            return []

        allowed_sequence = cls.PHASE_SEQUENCES.get(work_item.type, [])
        if not allowed_sequence:
            return []

        # Get current completed phases from metadata
        import json
        if not hasattr(work_item, 'metadata') or not work_item.metadata:
            # No metadata - can start first phase
            return [allowed_sequence[0]] if allowed_sequence else []

        try:
            if isinstance(work_item.metadata, str):
                metadata = json.loads(work_item.metadata)
            else:
                metadata = work_item.metadata
        except (json.JSONDecodeError, TypeError):
            return []

        gates = metadata.get('gates', {})

        # Find last completed phase
        last_complete_index = -1
        for i, phase in enumerate(allowed_sequence):
            gate_code = cls.LEGACY_PHASE_MAP.get(phase, phase)
            gate_status = gates.get(gate_code, {})

            is_complete = (
                gate_status.get('status') == 'completed' or
                gate_status.get('completion', 0) >= 100
            )

            if is_complete:
                last_complete_index = i
            else:
                # Stop at first incomplete phase
                break

        # Next allowed phase is immediately after last complete
        next_index = last_complete_index + 1
        if next_index < len(allowed_sequence):
            return [allowed_sequence[next_index]]

        return []  # All phases complete

    @classmethod
    def can_skip_phase(cls, work_item: any, phase: str) -> bool:
        """
        Check if phase can be skipped for this work item type.

        A phase can be skipped if it's NOT in the type's required sequence.

        Args:
            work_item: WorkItem entity (must have type)
            phase: Phase code to check (e.g., 'D1_discovery')

        Returns:
            True if phase can be skipped (not required), False if required

        Example:
            >>> # BUGFIX work items skip discovery
            >>> can_skip = PhaseValidator.can_skip_phase(bugfix_wi, 'D1_discovery')
            >>> assert can_skip is True

            >>> # FEATURE work items need discovery
            >>> can_skip = PhaseValidator.can_skip_phase(feature_wi, 'D1_discovery')
            >>> assert can_skip is False
        """
        if not hasattr(work_item, 'type'):
            return False

        allowed_sequence = cls.PHASE_SEQUENCES.get(work_item.type, [])
        return phase not in allowed_sequence

    @classmethod
    def get_required_phases(cls, work_item_type: WorkItemType) -> List[str]:
        """
        Get all required phases for a work item type.

        Args:
            work_item_type: WorkItemType enum

        Returns:
            List of required phase codes in order

        Example:
            >>> phases = PhaseValidator.get_required_phases(WorkItemType.FEATURE)
            >>> assert phases == ['D1_discovery', 'P1_plan', 'I1_implementation', 'R1_review', 'O1_ops', 'E1_eval']
        """
        return cls.PHASE_SEQUENCES.get(work_item_type, [])

    @classmethod
    def get_phase_name(cls, phase_code: str) -> str:
        """
        Get human-readable phase name.

        Args:
            phase_code: Phase code (e.g., 'D1_discovery')

        Returns:
            Human-readable name (e.g., 'Discovery (D1)')
        """
        phase_names = {
            'D1_discovery': 'Discovery (D1)',
            'P1_plan': 'Planning (P1)',
            'I1_implementation': 'Implementation (I1)',
            'R1_review': 'Review (R1)',
            'O1_operations': 'Operations (O1)',
            'E1_evolution': 'Evaluation (E1)'
        }
        return phase_names.get(phase_code, phase_code)

    # ─────────────────────────────────────────────────────────────────
    # Test-Compatible API Methods (Task 373)
    # ─────────────────────────────────────────────────────────────────

    def can_progress_to(self, work_item: any, new_phase: Phase) -> bool:
        """
        Check if work item can progress to new phase (boolean result).

        Args:
            work_item: WorkItem entity (must have type and phase)
            new_phase: Phase enum to transition to

        Returns:
            True if transition is valid, False otherwise

        Example:
            >>> validator = PhaseValidator()
            >>> wi = WorkItem(type=WorkItemType.FEATURE, phase=Phase.D1_DISCOVERY)
            >>> validator.can_progress_to(wi, Phase.P1_PLAN)
            True
        """
        result = self.validate_transition(work_item, new_phase)
        return result.is_valid

    def get_allowed_phases(self, work_item_type: WorkItemType) -> List[Phase]:
        """
        Get all allowed phases for work item type.

        Args:
            work_item_type: WorkItemType enum

        Returns:
            List of Phase enums in sequence order

        Example:
            >>> validator = PhaseValidator()
            >>> validator.get_allowed_phases(WorkItemType.FEATURE)
            [Phase.D1_DISCOVERY, Phase.P1_PLAN, Phase.I1_IMPLEMENTATION, ...]
        """
        return self.PHASE_SEQUENCES.get(work_item_type, [])

    def get_next_allowed_phase(self, work_item: any) -> Optional[Phase]:
        """
        Get next valid phase after current phase.

        Args:
            work_item: WorkItem entity (must have type and phase)

        Returns:
            Next Phase enum if available, None if at end of sequence

        Example:
            >>> validator = PhaseValidator()
            >>> wi = WorkItem(type=WorkItemType.FEATURE, phase=Phase.D1_DISCOVERY)
            >>> validator.get_next_allowed_phase(wi)
            Phase.P1_PLAN
        """
        if not hasattr(work_item, 'type'):
            return None

        allowed_sequence = self.PHASE_SEQUENCES.get(work_item.type, [])
        if not allowed_sequence:
            return None

        # If no current phase (NULL), return first phase
        if not hasattr(work_item, 'phase') or work_item.phase is None:
            return allowed_sequence[0] if allowed_sequence else None

        # Find current phase in sequence
        try:
            current_index = allowed_sequence.index(work_item.phase)
            # Return next phase if available
            next_index = current_index + 1
            if next_index < len(allowed_sequence):
                return allowed_sequence[next_index]
        except ValueError:
            # Current phase not in sequence (shouldn't happen)
            pass

        return None

    def is_final_phase(self, work_item_type: WorkItemType, phase: Phase) -> bool:
        """
        Check if phase is the final phase for work item type.

        Args:
            work_item_type: WorkItemType enum
            phase: Phase enum to check

        Returns:
            True if phase is the last phase in type's sequence

        Example:
            >>> validator = PhaseValidator()
            >>> validator.is_final_phase(WorkItemType.FEATURE, Phase.E1_EVOLUTION)
            True
            >>> validator.is_final_phase(WorkItemType.RESEARCH, Phase.P1_PLAN)
            True
        """
        allowed = self.PHASE_SEQUENCES.get(work_item_type, [])
        if not allowed:
            return False
        return phase == allowed[-1]

    def validate_transition(self, work_item: any, new_phase: Phase) -> PhaseValidationResult:
        """
        Full validation with detailed error messages.

        Checks:
        1. Phase exists in type's sequence
        2. Not transitioning to same phase
        3. Not going backwards
        4. Sequential progression (no skipping)

        Args:
            work_item: WorkItem entity (must have type and phase)
            new_phase: Phase enum to transition to

        Returns:
            PhaseValidationResult with is_valid and error_message

        Example:
            >>> validator = PhaseValidator()
            >>> wi = WorkItem(type=WorkItemType.RESEARCH, phase=Phase.P1_PLAN)
            >>> result = validator.validate_transition(wi, Phase.I1_IMPLEMENTATION)
            >>> assert result.is_valid is False
            >>> assert "RESEARCH" in result.error_message
        """
        if not hasattr(work_item, 'type'):
            return PhaseValidationResult(
                is_valid=False,
                error_message="Work item missing type field"
            )

        # Get allowed sequence for this type
        allowed_sequence = self.PHASE_SEQUENCES.get(work_item.type)
        if not allowed_sequence:
            return PhaseValidationResult(
                is_valid=False,
                error_message=f"Unknown work item type: {work_item.type}"
            )

        # Check if phase is allowed for this type
        if new_phase not in allowed_sequence:
            return PhaseValidationResult(
                is_valid=False,
                error_message=(
                    f"{work_item.type.value.upper()} work items cannot enter "
                    f"{new_phase.value} phase. "
                    f"Allowed phases: {', '.join([p.value for p in allowed_sequence])}"
                )
            )

        # Get current phase (handle NULL phase)
        current_phase = getattr(work_item, 'phase', None)

        # Check for same phase transition
        if current_phase == new_phase:
            return PhaseValidationResult(
                is_valid=False,
                error_message=f"Work item already in {new_phase.name} phase"
            )

        # If NULL phase, can only enter first phase
        if current_phase is None:
            if new_phase == allowed_sequence[0]:
                return PhaseValidationResult(is_valid=True)
            else:
                return PhaseValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Work item with NULL phase must start at {allowed_sequence[0].name}, "
                        f"not {new_phase.name}"
                    )
                )

        # Check for backwards progression
        try:
            current_index = allowed_sequence.index(current_phase)
            new_index = allowed_sequence.index(new_phase)

            if new_index <= current_index:
                return PhaseValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Cannot go backwards from {current_phase.name} to {new_phase.name}. "
                        f"Phases must progress forward."
                    )
                )

            # Check for skipping phases
            if new_index != current_index + 1:
                skipped_phases = allowed_sequence[current_index + 1:new_index]
                return PhaseValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Cannot skip phases. Must complete {skipped_phases[0].name} "
                        f"before {new_phase.name}."
                    )
                )

        except ValueError as e:
            return PhaseValidationResult(
                is_valid=False,
                error_message=f"Phase sequence error: {str(e)}"
            )

        return PhaseValidationResult(is_valid=True)
    
    # ========== PHASE REQUIREMENTS METHODS ==========
    
    def get_phase_requirements(self, phase: Phase, work_item_type: WorkItemType) -> Optional[PhaseRequirements]:
        """Get phase requirements for specific phase and work item type"""
        return self.PHASE_REQUIREMENTS.get((phase, work_item_type))
    
    def get_required_tasks_for_phase(self, phase: Phase, work_item_type: WorkItemType) -> List[TaskType]:
        """
        DEPRECATED: Get required task types for a specific phase and work item type.

        This method is deprecated as of 2025-10-17.
        Use outcome-based validation instead (see phase_gates/ validators).

        Returns:
            Empty list (required_tasks no longer enforced)
        """
        # DEPRECATED: Return empty list, phase gates use outcome-based validation
        return []
    
    def get_phase_completion_criteria(self, phase: Phase, work_item_type: WorkItemType) -> List[PhaseRequirement]:
        """Get completion criteria for a specific phase and work item type"""
        requirements = self.get_phase_requirements(phase, work_item_type)
        if requirements:
            return requirements.completion_criteria
        return []
    
    def get_phase_instructions(self, phase: Phase, work_item_type: WorkItemType) -> str:
        """Get instructions for a specific phase and work item type"""
        requirements = self.get_phase_requirements(phase, work_item_type)
        if requirements:
            return requirements.instructions
        return "No specific instructions available for this phase."
    
    def get_phase_estimated_duration(self, phase: Phase, work_item_type: WorkItemType) -> Optional[int]:
        """Get estimated duration in hours for a specific phase and work item type"""
        requirements = self.get_phase_requirements(phase, work_item_type)
        if requirements:
            return requirements.estimated_duration_hours
        return None
    
    def validate_phase_completion(self, work_item: any, phase: Phase) -> PhaseValidationResult:
        """
        Validate if a phase is complete based on its requirements.
        
        Args:
            work_item: WorkItem entity (must have type and phase)
            phase: Phase to validate completion for
            
        Returns:
            PhaseValidationResult with completion status and missing requirements
        """
        if not hasattr(work_item, 'type'):
            return PhaseValidationResult(
                is_valid=False,
                error_message="Work item missing type field"
            )
        
        requirements = self.get_phase_requirements(phase, work_item.type)
        if not requirements:
            return PhaseValidationResult(
                is_valid=True,  # No requirements = automatically complete
                error_message=f"No requirements defined for {phase.value} phase in {work_item.type.value} work items"
            )
        
        # Check if phase is required for this work item type
        if not self.is_phase_required(work_item.type, phase):
            return PhaseValidationResult(
                is_valid=True,  # Not required = automatically complete
                error_message=f"{phase.value} phase not required for {work_item.type.value} work items"
            )
        
        # TODO: Implement actual validation logic based on work item metadata
        # For now, return a placeholder that indicates validation is needed
        missing_requirements = []
        
        # This would check against work item metadata, tasks, etc.
        # For now, we'll return a basic validation result
        return PhaseValidationResult(
            is_valid=len(missing_requirements) == 0,
            error_message=f"Phase completion validation not yet implemented for {phase.value}",
            missing_requirements=missing_requirements,
            phase_requirements=requirements
        )
    
    def is_phase_required(self, work_item_type: WorkItemType, phase: Phase) -> bool:
        """Check if a phase is required for a work item type"""
        sequence = self.PHASE_SEQUENCES.get(work_item_type, [])
        return phase in sequence
    
    def get_next_phase_requirements(self, work_item: any) -> Optional[PhaseRequirements]:
        """Get requirements for the next phase in the work item's sequence"""
        if not hasattr(work_item, 'type'):
            return None
        
        next_phase = self.get_next_allowed_phase(work_item)
        if next_phase:
            return self.get_phase_requirements(next_phase, work_item.type)
        return None
