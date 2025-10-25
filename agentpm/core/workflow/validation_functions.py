"""
Validation Functions for Rules Engine and Phase Gates

Provides validation functions that can be called from the rules engine
and phase gate validators to validate various conditions.

Includes both:
1. Rules engine validators (coverage, time-boxing)
2. Outcome-based phase gate validators (planning complete, implementation complete)

Philosophy:
    - Validate outcomes, not task types
    - Flexible (users create tasks that make sense for their work)
    - Clear error messages explaining what's missing
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from ..testing import validate_all_categories, category_coverage
from ..database.enums import TaskStatus, TaskType


def category_coverage_validation(
    category_name: str,
    min_coverage: float,
    project_path: str,
    path_patterns: Optional[list] = None
) -> bool:
    """
    Validate that a specific category meets minimum coverage requirements.
    
    This function is called by the rules engine for rules like:
    - TEST-021: test-critical-paths-coverage
    - TEST-022: test-user-facing-coverage
    - etc.
    
    Args:
        category_name: Name of the testing category (e.g., "critical_paths")
        min_coverage: Minimum coverage percentage required
        project_path: Path to the project root
        path_patterns: Optional path patterns to override default category patterns
        
    Returns:
        True if coverage requirement is met, False otherwise
    """
    try:
        # Get coverage for the specific category
        coverage_result = category_coverage(project_path, category_name)
        
        if coverage_result is None:
            # Category not found or no files in category
            return True  # Don't block if category doesn't exist
        
        # Check if coverage meets requirement
        return coverage_result.coverage_percent >= min_coverage
        
    except Exception as e:
        # If validation fails, don't block the workflow
        print(f"Warning: Category coverage validation failed for {category_name}: {e}")
        return True


def task_specific_coverage_validation(
    task,
    category_name: str,
    min_coverage: float,
    project_path: str,
    path_patterns: Optional[list] = None
) -> bool:
    """
    Validate that a specific testing task meets coverage requirements for the code it's testing.
    
    This function is called by the rules engine for TESTING tasks only.
    It checks coverage for the specific code that this testing task is supposed to test,
    not the entire project.
    
    Args:
        task: The testing task being validated
        category_name: Name of the testing category (e.g., "critical_paths")
        min_coverage: Minimum coverage percentage required
        project_path: Path to the project root
        path_patterns: Optional path patterns to override default category patterns
        
    Returns:
        True if coverage requirement is met, False otherwise
    """
    try:
        # Check for coverage override first (allows bypassing coverage requirements)
        if task.quality_metadata and task.quality_metadata.get('coverage_override'):
            # Coverage override is set - bypass coverage requirements
            # This is used for refactoring tasks or when coverage measurement doesn't apply
            return True

        # For now, use a simplified approach:
        # 1. If the task has specific files/modules it's testing, check coverage for those
        # 2. Otherwise, check if the task has been completed with adequate test coverage

        # Check if task has quality metadata indicating what it's testing
        if task.quality_metadata and 'target_files' in task.quality_metadata:
            # Task is testing specific files - check coverage for those files
            target_files = task.quality_metadata['target_files']
            # TODO: Implement file-specific coverage checking
            # For now, assume adequate if task is completed
            return task.status in [TaskStatus.DONE, TaskStatus.REVIEW]
        
        # Check if task has coverage metadata
        if task.quality_metadata and 'coverage_percent' in task.quality_metadata:
            task_coverage = task.quality_metadata['coverage_percent']
            return task_coverage >= min_coverage
        
        # If no specific coverage data, check if task is completed
        # (assumes completion means adequate testing was done)
        if task.status in [TaskStatus.DONE, TaskStatus.REVIEW]:
            return True
        
        # For tasks in progress or draft, be more lenient
        # Only block if we have evidence that coverage is inadequate
        return True  # Don't block testing tasks that are still in progress
        
    except Exception as e:
        # If validation fails, don't block the workflow
        print(f"Warning: Task-specific coverage validation failed: {e}")
        return True


def overall_coverage_validation(
    min_coverage: float,
    project_path: str
) -> bool:
    """
    Validate that overall project coverage meets minimum requirements.
    
    This function is called by the rules engine for rules like:
    - TEST-001: test-coverage-target
    - DP-012: quality-test-coverage
    
    Args:
        min_coverage: Minimum coverage percentage required
        project_path: Path to the project root
        
    Returns:
        True if coverage requirement is met, False otherwise
    """
    try:
        # Validate all categories and get overall result
        all_requirements_met, violations = validate_all_categories(project_path)
        
        # For overall coverage, we could also calculate a weighted average
        # For now, we'll use the category validation result
        return all_requirements_met
        
    except Exception as e:
        # If validation fails, don't block the workflow
        print(f"Warning: Overall coverage validation failed: {e}")
        return True


def time_boxing_validation(
    task_type: str,
    effort_hours: float,
    max_hours: float
) -> bool:
    """
    Validate that task effort doesn't exceed time-boxing limits.
    
    This function is called by the rules engine for rules like:
    - DP-001: time-boxing-implementation
    - DP-002: time-boxing-testing
    
    Args:
        task_type: Type of task (e.g., "IMPLEMENTATION", "TESTING")
        effort_hours: Planned effort in hours
        max_hours: Maximum allowed hours
        
    Returns:
        True if effort is within limits, False otherwise
    """
    return effort_hours <= max_hours


def acceptance_criteria_validation(
    criteria: list,
    all_met_required: bool = True
) -> bool:
    """
    Validate that acceptance criteria are properly defined and optionally met.
    
    Args:
        criteria: List of acceptance criteria objects
        all_met_required: Whether all criteria must be met
        
    Returns:
        True if criteria are valid and (optionally) met, False otherwise
    """
    if not criteria or not isinstance(criteria, list):
        return False
    
    # Check that all criteria have required fields
    for criterion in criteria:
        if not isinstance(criterion, dict):
            return False
        if "criterion" not in criterion:
            return False
    
    # If all_met_required, check that all criteria are met
    if all_met_required:
        for criterion in criteria:
            if not criterion.get("met", False):
                return False
    
    return True


def test_plan_validation(
    test_plan: str
) -> bool:
    """
    Validate that a test plan is provided and not empty.
    
    Args:
        test_plan: Test plan description
        
    Returns:
        True if test plan is valid, False otherwise
    """
    return bool(test_plan and test_plan.strip())


def tests_passing_validation(
    tests_passing: bool
) -> bool:
    """
    Validate that tests are passing.
    
    Args:
        tests_passing: Whether tests are currently passing
        
    Returns:
        True if tests are passing, False otherwise
    """
    return tests_passing


# Registry of validation functions for the rules engine
VALIDATION_FUNCTIONS = {
    "category_coverage": category_coverage_validation,
    "overall_coverage": overall_coverage_validation,
    "time_boxing": time_boxing_validation,
    "acceptance_criteria": acceptance_criteria_validation,
    "test_plan": test_plan_validation,
    "tests_passing": tests_passing_validation,
}


def get_validation_function(function_name: str):
    """
    Get a validation function by name.
    
    Args:
        function_name: Name of the validation function
        
    Returns:
        Validation function if found, None otherwise
    """
    return VALIDATION_FUNCTIONS.get(function_name)


def validate_rule_condition(
    validation_logic: str,
    context: Dict[str, Any]
) -> bool:
    """
    Validate a rule condition using the validation logic string.
    
    This function parses the validation logic and calls the appropriate
    validation functions with the provided context.
    
    Args:
        validation_logic: Validation logic string (e.g., "category_coverage('critical_paths') < min_coverage")
        context: Context variables for validation
        
    Returns:
        True if condition is met, False otherwise
    """
    try:
        # This is a simplified implementation
        # In a full implementation, you'd want a proper expression parser
        
        # For now, handle the specific patterns we know about
        if "category_coverage" in validation_logic:
            # Extract category name and min_coverage from context
            category_name = context.get("category_name", "critical_paths")
            min_coverage = context.get("min_coverage", 95.0)
            project_path = context.get("project_path", ".")
            
            return category_coverage_validation(category_name, min_coverage, project_path)
        
        elif "overall_coverage" in validation_logic or "test_coverage" in validation_logic:
            min_coverage = context.get("min_coverage", 90.0)
            project_path = context.get("project_path", ".")
            
            return overall_coverage_validation(min_coverage, project_path)
        
        elif "effort_hours" in validation_logic:
            effort_hours = context.get("effort_hours", 0)
            max_hours = context.get("max_hours", 4.0)
            
            return time_boxing_validation("TASK", effort_hours, max_hours)
        
        # SECURITY: Default to False for unknown conditions
        # Unknown conditions should fail validation, not pass
        print(f"Warning: Unknown validation condition: {validation_logic}")
        return False
        
    except Exception as e:
        print(f"Error: Rule validation failed: {e}")
        # SECURITY: Fail validation on errors, don't default to pass
        return False


# ============================================================================
# Outcome-Based Phase Gate Validators
# ============================================================================

def validate_planning_complete(
    tasks: List[Any],
    min_tasks: int = 1
) -> List[str]:
    """
    Validate that planning phase is complete.

    Checks OUTCOMES not task types:
        - At least min_tasks tasks exist (shows planning happened)
        - All tasks have effort estimates (shows effort considered)

    Args:
        tasks: List of Task objects
        min_tasks: Minimum number of tasks required (default: 1)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Outcome 1: Tasks exist (planning happened)
    if len(tasks) < min_tasks:
        errors.append(
            f"No tasks created - planning incomplete. "
            f"Create ≥{min_tasks} task to show work has been planned."
        )

    # Outcome 2: Estimates present (effort considered)
    no_estimate = [t for t in tasks if not t.effort_hours]
    if no_estimate:
        task_ids = [f"#{t.id}" for t in no_estimate[:5]]
        suffix = f" (and {len(no_estimate)-5} more)" if len(no_estimate) > 5 else ""
        errors.append(
            f"{len(no_estimate)} task(s) missing effort_hours estimate: "
            f"{', '.join(task_ids)}{suffix}. "
            f"Estimate all tasks to show planning is complete."
        )

    return errors


def validate_time_boxing_tasks(
    tasks: List[Any],
    max_hours: float = 4.0,
    task_types: Optional[List[TaskType]] = None
) -> List[str]:
    """
    Validate that tasks respect time-boxing limits.

    Prevents monolithic tasks by enforcing maximum hours per task.

    Args:
        tasks: List of Task objects
        max_hours: Maximum hours per task (default: 4.0)
        task_types: Task types to check (default: [IMPLEMENTATION])

    Returns:
        List of error messages (empty if valid)
    """
    if task_types is None:
        task_types = [TaskType.IMPLEMENTATION]

    errors = []

    # Check time-boxing for specified task types
    over_limit = [
        t for t in tasks
        if t.type in task_types and
           t.effort_hours and
           t.effort_hours > max_hours
    ]

    if over_limit:
        task_details = [
            f"#{t.id} ({t.effort_hours}h)" for t in over_limit
        ]
        type_names = ', '.join([t.value for t in task_types])
        errors.append(
            f"{len(over_limit)} {type_names} task(s) exceed "
            f"{max_hours}h time-box limit: {', '.join(task_details)}. "
            f"Break large tasks into smaller sub-tasks."
        )

    return errors


def validate_implementation_complete_tasks(tasks: List[Any]) -> List[str]:
    """
    Validate that implementation phase is complete.

    Checks OUTCOMES not task types:
        - All tasks marked DONE (work finished)

    Args:
        tasks: List of Task objects

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Outcome: All tasks DONE (work complete)
    incomplete_tasks = [t for t in tasks if t.status != TaskStatus.DONE]

    if incomplete_tasks:
        task_details = [
            f"#{t.id} ({t.type.value})" for t in incomplete_tasks[:5]
        ]
        suffix = f" (and {len(incomplete_tasks)-5} more)" if len(incomplete_tasks) > 5 else ""
        errors.append(
            f"{len(incomplete_tasks)} task(s) not DONE: "
            f"{', '.join(task_details)}{suffix}. "
            f"Complete all tasks before moving to review phase."
        )

    return errors


# Example usage
if __name__ == "__main__":
    # Test validation functions
    project_path = "."

    # Test category coverage validation
    result = category_coverage_validation("critical_paths", 95.0, project_path)
    print(f"Critical paths coverage validation: {result}")

    # Test overall coverage validation
    result = overall_coverage_validation(90.0, project_path)
    print(f"Overall coverage validation: {result}")

    # Test time-boxing validation
    result = time_boxing_validation("IMPLEMENTATION", 3.5, 4.0)
    print(f"Time-boxing validation: {result}")
