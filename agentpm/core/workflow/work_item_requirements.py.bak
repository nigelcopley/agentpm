"""
Work Item Requirements - Task Type Guidelines Per Work Item Type

Defines task type recommendations for each work item type.
Provides guidance on typical task patterns without enforcing rigid requirements.

Philosophy Change:
    OLD: Required task types enforce specific categorization
    NEW: Guidelines suggest typical patterns, users decide what makes sense

Pattern: Dictionary-based recommendations with type-safe enums
Note: Phase gates validate OUTCOMES (is work complete?), not task types
"""

from typing import Dict, Set, List
from dataclasses import dataclass

from ..database.enums import WorkItemType, TaskType


@dataclass
class WorkItemTaskRequirements:
    """
    Requirements for tasks within a work item type.

    Attributes:
        required: Task types that MUST exist (at least one of each)
        optional: Task types that MAY exist (recommended but not required)
        forbidden: Task types that CANNOT exist (invalid combinations)
        min_counts: Minimum count for each required task type (default 1)
    """
    required: Set[TaskType]
    optional: Set[TaskType] = None
    forbidden: Set[TaskType] = None
    min_counts: Dict[TaskType, int] = None

    def __post_init__(self):
        if self.optional is None:
            self.optional = set()
        if self.forbidden is None:
            self.forbidden = set()
        if self.min_counts is None:
            self.min_counts = {}


# Work Item Type Requirements
# Each work item type has specific required, optional, and forbidden task types

WORK_ITEM_TASK_REQUIREMENTS: Dict[WorkItemType, WorkItemTaskRequirements] = {
    # FEATURE: New capability/system (typically follows all 6 phases)
    # Typical Phases: D1 → P1 → I1 → R1 → O1 → E1
    WorkItemType.FEATURE: WorkItemTaskRequirements(
        required=set(),  # No required task types - users decide what makes sense
        optional={
            # Common task patterns for features:
            TaskType.DESIGN,           # Design before implementing
            TaskType.IMPLEMENTATION,   # Implement the feature
            TaskType.TESTING,          # Test the implementation
            TaskType.DOCUMENTATION,    # Document the feature
            TaskType.ANALYSIS,         # Upfront investigation
            TaskType.REVIEW,           # Additional reviews
            TaskType.DEPLOYMENT,       # If deployment is complex
            TaskType.REFACTORING,      # Code quality improvements
        },
        forbidden=set(),  # Features can have any task type
        min_counts={}  # No minimum counts - phase gates check outcomes
    ),

# ENHANCEMENT: Improve existing (typically D1 → P1 → I1 → R1 → E1)
    WorkItemType.ENHANCEMENT: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.IMPLEMENTATION,   # Implement the enhancement
            TaskType.TESTING,          # Test the changes
            TaskType.DESIGN,           # Design if change is complex
            TaskType.ANALYSIS,         # Investigation
            TaskType.DOCUMENTATION,    # Doc updates
            TaskType.REVIEW,           # Reviews
            TaskType.REFACTORING,      # Refactoring
        },
        forbidden=set(),
        min_counts={}
    ),

    # BUGFIX: Fix substantial defect (typically I1 → R1)
    WorkItemType.BUGFIX: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,         # Investigate root cause
            TaskType.BUGFIX,           # Fix the bug
            TaskType.TESTING,          # Verify fix
            TaskType.DESIGN,           # Design if fix requires it
            TaskType.REFACTORING,      # Code quality improvements
            TaskType.DOCUMENTATION,    # Doc updates
            TaskType.REVIEW,           # Reviews
        },
        forbidden=set(),
        min_counts={}
    ),

    # RESEARCH: Investigation/spike (typically D1 → P1)
    WorkItemType.RESEARCH: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,         # Analyze and research
            TaskType.DOCUMENTATION,    # Document findings
            TaskType.DESIGN,           # Explore designs
            TaskType.SIMPLE,           # Quick investigations
            TaskType.REVIEW,           # Peer review of findings
        },
        forbidden=set(),
        min_counts={}
    ),

    # PLANNING: Architecture/design/roadmap (typically D1 → P1)
    WorkItemType.PLANNING: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,         # Analyze requirements/constraints
            TaskType.DESIGN,           # Create design/plan
            TaskType.DOCUMENTATION,    # Document decisions
            TaskType.REVIEW,           # Review plans
            TaskType.SIMPLE,           # Quick tasks
        },
        forbidden=set(),
        min_counts={}
    ),

    # REFACTORING: Large-scale code improvement (typically P1 → I1 → R1)
    WorkItemType.REFACTORING: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,         # Analyze what to refactor
            TaskType.REFACTORING,      # Refactor the code
            TaskType.TESTING,          # Ensure tests still pass
            TaskType.DESIGN,           # Design refactoring approach
            TaskType.DOCUMENTATION,    # Doc updates
            TaskType.REVIEW,           # Reviews
        },
        forbidden=set(),
        min_counts={}
    ),

    # INFRASTRUCTURE: DevOps/platform work (typically D1 → P1 → I1 → R1 → O1)
    WorkItemType.INFRASTRUCTURE: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.DESIGN,           # Design infrastructure
            TaskType.IMPLEMENTATION,   # Implement infrastructure
            TaskType.DEPLOYMENT,       # Deploy infrastructure
            TaskType.DOCUMENTATION,    # Document setup/usage
            TaskType.ANALYSIS,         # Investigation
            TaskType.TESTING,          # Infrastructure tests
            TaskType.REVIEW,           # Reviews
        },
        forbidden=set(),
        min_counts={}
    ),

    # CONTINUOUS BACKLOGS: Ongoing work (phase sequence varies)
    WorkItemType.MAINTENANCE: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.MAINTENANCE,
            TaskType.DOCUMENTATION,
            TaskType.REVIEW,
            TaskType.ANALYSIS,
        },
        forbidden=set(),
        min_counts={}
    ),
    WorkItemType.MONITORING: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,
            TaskType.MAINTENANCE,
            TaskType.SIMPLE,
            TaskType.OTHER,
        },
        forbidden=set(),
        min_counts={}
    ),
    WorkItemType.DOCUMENTATION: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.DOCUMENTATION,
            TaskType.REVIEW,
            TaskType.ANALYSIS,
        },
        forbidden=set(),
        min_counts={}
    ),
    WorkItemType.SECURITY: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.ANALYSIS,
            TaskType.IMPLEMENTATION,
            TaskType.TESTING,
            TaskType.DOCUMENTATION,
            TaskType.REVIEW,
        },
        forbidden=set(),
        min_counts={}
    ),
    WorkItemType.FIX_BUGS_ISSUES: WorkItemTaskRequirements(
        required=set(),
        optional={
            TaskType.BUGFIX,
            TaskType.ANALYSIS,
            TaskType.TESTING,
            TaskType.DOCUMENTATION,
        },
        forbidden=set(),
        min_counts={}
    ),
}


class WorkItemRequirements:
    """
    Work item requirement validation and messaging.

    Provides methods to check if work item has required tasks
    and generate helpful error messages for missing requirements.
    """

    @staticmethod
    def get_requirements(work_item_type: WorkItemType) -> WorkItemTaskRequirements:
        """
        Get task requirements for work item type.

        Args:
            work_item_type: Type of work item

        Returns:
            Task requirements (required, optional, forbidden, min_counts)
        """
        return WORK_ITEM_TASK_REQUIREMENTS.get(
            work_item_type,
            WorkItemTaskRequirements(required=set(), optional=set(), forbidden=set())
        )

    @staticmethod
    def get_required_task_types(work_item_type: WorkItemType) -> Set[TaskType]:
        """
        Get required task types for work item type.

        Args:
            work_item_type: Type of work item

        Returns:
            Set of required task types
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        return requirements.required

    @staticmethod
    def get_forbidden_task_types(work_item_type: WorkItemType) -> Set[TaskType]:
        """
        Get forbidden task types for work item type.

        Args:
            work_item_type: Type of work item

        Returns:
            Set of forbidden task types
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        return requirements.forbidden

    @staticmethod
    def get_min_count(work_item_type: WorkItemType, task_type: TaskType) -> int:
        """
        Get minimum count required for task type.

        Args:
            work_item_type: Type of work item
            task_type: Type of task

        Returns:
            Minimum count (default 1 if task is required, 0 otherwise)
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        if task_type in requirements.min_counts:
            return requirements.min_counts[task_type]
        elif task_type in requirements.required:
            return 1  # Default minimum for required tasks
        else:
            return 0  # Not required

    @staticmethod
    def get_required_tasks_message(work_item_type: WorkItemType) -> str:
        """
        Get human-readable message describing typical task patterns.

        Philosophy Change:
            OLD: Lists required task types (rigid enforcement)
            NEW: Lists typical task patterns (flexible guidance)

        Args:
            work_item_type: Type of work item

        Returns:
            Formatted message listing typical task patterns

        Examples:
            >>> get_required_tasks_message(WorkItemType.FEATURE)
            "FEATURE work items typically follow phases: D1 → P1 → I1 → R1 → O1 → E1. Common task types: DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION"

            >>> get_required_tasks_message(WorkItemType.BUGFIX)
            "BUGFIX work items typically follow phases: I1 → R1. Common task types: ANALYSIS, BUGFIX, TESTING"
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)

        # Map work item types to typical phase sequences
        phase_sequences = {
            WorkItemType.FEATURE: "D1 → P1 → I1 → R1 → O1 → E1",
            WorkItemType.ENHANCEMENT: "D1 → P1 → I1 → R1 → E1",
            WorkItemType.BUGFIX: "I1 → R1",
            WorkItemType.RESEARCH: "D1 → P1",
            WorkItemType.PLANNING: "D1 → P1",
            WorkItemType.REFACTORING: "P1 → I1 → R1",
            WorkItemType.INFRASTRUCTURE: "D1 → P1 → I1 → R1 → O1",
            WorkItemType.MAINTENANCE: "varies (ongoing work)",
            WorkItemType.MONITORING: "O1 → E1 (ongoing)",
            WorkItemType.DOCUMENTATION: "I1 → R1 → E1",
            WorkItemType.SECURITY: "D1 → P1 → I1 → R1 → O1 → E1",
            WorkItemType.FIX_BUGS_ISSUES: "I1 → R1 → O1 → E1",
        }

        phase_seq = phase_sequences.get(work_item_type, "varies")

        # List common optional task types
        common_types = []
        for task_type in sorted(requirements.optional, key=lambda t: t.value):
            common_types.append(task_type.value.upper())

        message = f"{work_item_type.value.upper()} work items typically follow phases: {phase_seq}"

        if common_types:
            # Show first 5 most common types
            display_types = common_types[:5]
            suffix = f" (and {len(common_types)-5} more)" if len(common_types) > 5 else ""
            message += f". Common task types: {', '.join(display_types)}{suffix}"

        message += ". Phase gates check OUTCOMES (is work complete?), not task types."

        return message

    @staticmethod
    def get_missing_required_tasks(
        work_item_type: WorkItemType,
        existing_task_types: List[TaskType]
    ) -> List[TaskType]:
        """
        Get list of missing required task types.

        Args:
            work_item_type: Type of work item
            existing_task_types: List of task types that exist

        Returns:
            List of missing required task types
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        existing_set = set(existing_task_types)
        return [t for t in requirements.required if t not in existing_set]

    @staticmethod
    def get_forbidden_tasks_present(
        work_item_type: WorkItemType,
        existing_task_types: List[TaskType]
    ) -> List[TaskType]:
        """
        Get list of forbidden task types that are present.

        Args:
            work_item_type: Type of work item
            existing_task_types: List of task types that exist

        Returns:
            List of forbidden task types that exist (should be empty)
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        existing_set = set(existing_task_types)
        return [t for t in requirements.forbidden if t in existing_set]

    @staticmethod
    def validate_task_counts(
        work_item_type: WorkItemType,
        task_type_counts: Dict[TaskType, int]
    ) -> List[str]:
        """
        Validate task counts meet minimum requirements.

        Args:
            work_item_type: Type of work item
            task_type_counts: Dictionary of task type to count

        Returns:
            List of error messages (empty if valid)

        Examples:
            >>> validate_task_counts(WorkItemType.FEATURE, {TaskType.DESIGN: 1, TaskType.IMPLEMENTATION: 2})
            ['Missing TESTING tasks (required: 1+)', 'Missing DOCUMENTATION tasks (required: 1+)']
        """
        requirements = WorkItemRequirements.get_requirements(work_item_type)
        errors = []

        for task_type in requirements.required:
            count = task_type_counts.get(task_type, 0)
            min_count = requirements.min_counts.get(task_type, 1)

            if count < min_count:
                errors.append(
                    f"Missing {task_type.value.upper()} tasks (required: {min_count}+, found: {count})"
                )

        return errors
