"""
Type-Specific Validators - Quality Gate Enforcement

Validates tasks and work items against type-specific requirements:
- Time-boxing enforcement (IMPLEMENTATION tasks ≤4h STRICT)
- Type-specific quality gates (FEATURE needs acceptance criteria, BUGFIX needs reproduction)
- quality_metadata structure validation

Pattern: Validator methods return ValidationResult with clear error messages
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..database.enums import TaskType, WorkItemType, TaskStatus


@dataclass
class ValidationResult:
    """Result of validation check"""
    valid: bool
    reason: Optional[str] = None


# Time limits per task type (in hours)
TASK_TYPE_MAX_HOURS: Dict[TaskType, float] = {
    TaskType.SIMPLE: 1.0,           # Quick tasks
    TaskType.REVIEW: 2.0,            # Code review
    TaskType.BUGFIX: 4.0,            # Bug fixes
    TaskType.IMPLEMENTATION: 4.0,    # STRICT - Forces proper decomposition
    TaskType.DEPLOYMENT: 4.0,        # Deployment activities
    TaskType.REFACTORING: 4.0,       # Code improvements
    TaskType.TESTING: 6.0,           # Test writing
    TaskType.DOCUMENTATION: 6.0,     # Documentation writing
    TaskType.DESIGN: 8.0,            # Design activities
    TaskType.ANALYSIS: 8.0,          # Investigation/research
}


class TypeSpecificValidators:
    """
    Type-specific validation rules for tasks and work items.

    Validates:
    - Time-boxing (task effort_hours ≤ type maximum)
    - Type-specific quality gates (metadata requirements)
    - State transition readiness
    """

    @staticmethod
    def validate_time_box(task_type: TaskType, effort_hours: Optional[float], db_service=None, project_id: Optional[int] = None) -> ValidationResult:
        """
        Validate task effort against type-specific time limits from rules system.

        First tries to get limits from rules system, falls back to hardcoded limits
        if rules system is not available.

        Args:
            task_type: Type of task
            effort_hours: Estimated effort in hours (None = not estimated yet)
            db_service: Database service for rules lookup (optional)
            project_id: Project ID for rules lookup (optional)

        Returns:
            ValidationResult with success/failure and actionable message

        Examples:
            >>> validate_time_box(TaskType.IMPLEMENTATION, 5.0)
            ValidationResult(valid=False, reason="IMPLEMENTATION tasks limited to 4.0 hours...")

            >>> validate_time_box(TaskType.IMPLEMENTATION, 3.5)
            ValidationResult(valid=True, reason=None)
        """
        if effort_hours is None:
            return ValidationResult(
                valid=False,
                reason=f"Task effort_hours must be estimated before validation"
            )

        # SECURITY: Always validate time-boxing, use hardcoded limits as fallback
        max_hours = TASK_TYPE_MAX_HOURS.get(task_type)
        if max_hours is None:
            # Unknown task type - allow (should not happen with proper enums)
            return ValidationResult(valid=True, reason=None)
        
        # Try to get limits from rules system if available
        if db_service and project_id:
            try:
                from ..database.methods import rules as rule_methods
                rules = rule_methods.list_rules(db_service, project_id=project_id, enabled_only=True)
                
                # Look for timeboxing rule for this task type
                rule_max_hours = None
                for rule in rules:
                    if (rule.config and 
                        'max_hours' in rule.config and 
                        rule.config.get('task_type') == task_type.value):
                        rule_max_hours = rule.config['max_hours']
                        break
                
                # Use rule limit if found, otherwise use hardcoded limit
                if rule_max_hours is not None:
                    max_hours = rule_max_hours
                    
            except Exception:
                # Rules system failed - use hardcoded limit (already set above)
                pass

        if effort_hours > max_hours:
            return ValidationResult(
                valid=False,
                reason=(
                    f"{task_type.value.upper()} tasks limited to {max_hours} hours "
                    f"(estimated: {effort_hours}h). Break into smaller tasks. "
                    f"Example: Split 5h IMPLEMENTATION into 3h + 2h tasks."
                )
            )

        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def validate_quality_metadata_structure(
        task_type: TaskType,
        quality_metadata: Optional[Dict[str, Any]],
        target_status: TaskStatus,
        db_service=None,
        project_id: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate quality_metadata structure for type-specific requirements.

        Different task types have different metadata requirements at different states:
        - IMPLEMENTATION: Needs acceptance_criteria before READY
        - BUGFIX: Needs reproduction_steps before READY
        - TESTING: Needs test_plan before READY
        - SIMPLE: Minimal requirements

        Args:
            task_type: Type of task
            quality_metadata: Task quality metadata (can be None)
            target_status: State task is transitioning to

        Returns:
            ValidationResult with success/failure and specific guidance
        """
        # Only enforce metadata for certain state transitions
        if target_status not in (TaskStatus.READY, TaskStatus.ACTIVE, TaskStatus.REVIEW):
            return ValidationResult(valid=True, reason=None)

        # SIMPLE tasks have minimal requirements
        if task_type == TaskType.SIMPLE:
            return ValidationResult(valid=True, reason=None)

        if quality_metadata is None:
            quality_metadata = {}

        # Type-specific validation rules
        if task_type == TaskType.IMPLEMENTATION:
            return TypeSpecificValidators._validate_implementation_metadata(
                quality_metadata, target_status
            )
        elif task_type == TaskType.BUGFIX:
            return TypeSpecificValidators._validate_bugfix_metadata(
                quality_metadata, target_status
            )
        elif task_type == TaskType.TESTING:
            return TypeSpecificValidators._validate_testing_metadata(
                quality_metadata, target_status, db_service, project_id
            )
        elif task_type == TaskType.DESIGN:
            return TypeSpecificValidators._validate_design_metadata(
                quality_metadata, target_status
            )

        # Other task types: basic validation only
        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def _validate_implementation_metadata(
        metadata: Dict[str, Any],
        target_status: TaskStatus
    ) -> ValidationResult:
        """
        Validate IMPLEMENTATION task metadata.

        Requirements:
        - READY: Must have acceptance_criteria (list with at least 1 criterion)
        - REVIEW: Must have acceptance_criteria with all criteria met
        """
        if target_status == TaskStatus.READY:
            if "acceptance_criteria" not in metadata:
                return ValidationResult(
                    valid=False,
                    reason=(
                        "IMPLEMENTATION tasks require acceptance_criteria in quality_metadata. "
                        "Example: {'acceptance_criteria': [{'criterion': 'Users can login', 'met': false}]}"
                    )
                )

            criteria = metadata.get("acceptance_criteria", [])
            if not isinstance(criteria, list) or len(criteria) == 0:
                return ValidationResult(
                    valid=False,
                    reason="acceptance_criteria must be a non-empty list of criterion objects"
                )

        elif target_status == TaskStatus.REVIEW:
            criteria = metadata.get("acceptance_criteria", [])
            if not criteria:
                return ValidationResult(
                    valid=False,
                    reason="Cannot move to REVIEW without acceptance criteria"
                )

            unmet = [c.get("criterion") for c in criteria if not c.get("met", False)]
            if unmet:
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Cannot move to REVIEW with unmet acceptance criteria: {unmet}. "
                        "Mark all criteria as met before requesting review."
                    )
                )

        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def _validate_bugfix_metadata(
        metadata: Dict[str, Any],
        target_status: TaskStatus
    ) -> ValidationResult:
        """
        Validate BUGFIX task metadata.

        Requirements:
        - READY: Must have reproduction_steps
        - REVIEW: Must have fix_verified=true
        """
        if target_status == TaskStatus.READY:
            if "reproduction_steps" not in metadata or not metadata.get("reproduction_steps"):
                return ValidationResult(
                    valid=False,
                    reason=(
                        "BUGFIX tasks require reproduction_steps in quality_metadata. "
                        "Example: {'reproduction_steps': '1. Login as admin 2. Click Settings 3. Error appears', "
                        "'fix_verified': false}"
                    )
                )

        elif target_status == TaskStatus.REVIEW:
            if not metadata.get("fix_verified", False):
                return ValidationResult(
                    valid=False,
                    reason=(
                        "Cannot move to REVIEW without verifying fix. "
                        "Set quality_metadata.fix_verified = true after testing fix."
                    )
                )

        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def _validate_testing_metadata(
        metadata: Dict[str, Any],
        target_status: TaskStatus,
        db_service=None,
        project_id: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate TESTING task metadata using configurable rules.

        Requirements:
        - READY: Must have test_plan
        - REVIEW: Must have tests_passing=true and coverage meeting configurable threshold
        """
        if target_status == TaskStatus.READY:
            if "test_plan" not in metadata or not metadata.get("test_plan"):
                return ValidationResult(
                    valid=False,
                    reason=(
                        "TESTING tasks require test_plan in quality_metadata. "
                        "Example: {'test_plan': 'Unit tests for User model, integration tests for auth', "
                        "'tests_passing': false, 'coverage_percent': 0}"
                    )
                )

        elif target_status == TaskStatus.REVIEW:
            if not metadata.get("tests_passing", False):
                return ValidationResult(
                    valid=False,
                    reason="Cannot move to REVIEW with failing tests"
                )

            # Check for coverage override first (allows bypassing coverage requirements)
            if metadata.get('coverage_override'):
                # Coverage override is set - bypass coverage requirements
                # This is used when task has verified coverage for its specific scope
                # but project-wide coverage validation would fail
                return ValidationResult(valid=True, reason=None)

            # Use category-specific coverage validation
            if not db_service or not project_id:
                # No database context - skip coverage validation
                return ValidationResult(valid=True, reason=None)

            try:
                # Get project path from database
                from ..database.methods import projects as project_methods
                project = project_methods.get_project(db_service, project_id)
                if not project or not project.path:
                    return ValidationResult(valid=True, reason=None)

                # Use new category-specific coverage validation
                from ..testing import validate_all_categories
                all_requirements_met, violations = validate_all_categories(project.path)

                if not all_requirements_met:
                    return ValidationResult(
                        valid=False,
                        reason=(
                            f"Cannot move to REVIEW - category-specific coverage requirements not met:\n" +
                            "\n".join(f"  - {violation}" for violation in violations) +
                            f"\n\nTo bypass this check for task-specific work with verified coverage:\n" +
                            f"  Set quality_metadata.coverage_override = true with coverage_scope and override_reason"
                        )
                    )

            except Exception as e:
                # Fallback to simple coverage check if category validation fails
                coverage = metadata.get("coverage_percent", 0)
                if coverage < 70:  # Minimum reasonable coverage
                    return ValidationResult(
                        valid=False,
                        reason=(
                            f"Cannot move to REVIEW with coverage {coverage}% (minimum: 70%). "
                            "Add more tests to reach coverage threshold."
                        )
                    )

        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def _validate_design_metadata(
        metadata: Dict[str, Any],
        target_status: TaskStatus
    ) -> ValidationResult:
        """
        Validate DESIGN task metadata.

        Requirements:
        - READY: Must have design_approach
        - REVIEW: Must have ambiguities resolved
        """
        if target_status == TaskStatus.READY:
            if "design_approach" not in metadata or not metadata.get("design_approach"):
                return ValidationResult(
                    valid=False,
                    reason=(
                        "DESIGN tasks require design_approach in quality_metadata. "
                        "Example: {'design_approach': 'Use SQLAlchemy ORM with async support', "
                        "'ambiguities': []}"
                    )
                )

        elif target_status == TaskStatus.REVIEW:
            ambiguities = metadata.get("ambiguities", [])
            # Only check for open ambiguities, not resolved ones
            open_ambiguities = [
                amb for amb in ambiguities 
                if isinstance(amb, dict) and amb.get("status") == "open"
            ]
            if open_ambiguities:
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"Cannot move to REVIEW with unresolved ambiguities: {open_ambiguities}. "
                        "Resolve all design ambiguities before review."
                    )
                )

        return ValidationResult(valid=True, reason=None)

    @staticmethod
    def get_time_limit(task_type: TaskType) -> float:
        """
        Get time limit for task type.

        Args:
            task_type: Type of task

        Returns:
            Maximum hours allowed for this task type
        """
        return TASK_TYPE_MAX_HOURS.get(task_type, 8.0)  # Default 8h if unknown

    @staticmethod
    def get_required_metadata_fields(task_type: TaskType, target_status: TaskStatus) -> List[str]:
        """
        Get list of required quality_metadata fields for task type at target status.

        Args:
            task_type: Type of task
            target_status: State transitioning to

        Returns:
            List of required field names

        Examples:
            >>> get_required_metadata_fields(TaskType.IMPLEMENTATION, TaskStatus.READY)
            ['acceptance_criteria']

            >>> get_required_metadata_fields(TaskType.BUGFIX, TaskStatus.REVIEW)
            ['reproduction_steps', 'fix_verified']
        """
        if task_type == TaskType.SIMPLE:
            return []

        requirements = {
            (TaskType.IMPLEMENTATION, TaskStatus.READY): ["acceptance_criteria"],
            (TaskType.IMPLEMENTATION, TaskStatus.REVIEW): ["acceptance_criteria"],
            (TaskType.BUGFIX, TaskStatus.READY): ["reproduction_steps"],
            (TaskType.BUGFIX, TaskStatus.REVIEW): ["reproduction_steps", "fix_verified"],
            (TaskType.TESTING, TaskStatus.READY): ["test_plan"],
            (TaskType.TESTING, TaskStatus.REVIEW): ["test_plan", "tests_passing", "coverage_percent"],
            (TaskType.DESIGN, TaskStatus.READY): ["design_approach"],
            (TaskType.DESIGN, TaskStatus.REVIEW): ["design_approach", "ambiguities"],
        }

        return requirements.get((task_type, target_status), [])
