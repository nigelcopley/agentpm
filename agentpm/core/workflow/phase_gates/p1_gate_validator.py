"""
P1 Gate Validator - Planning → Implementation Gate

Validates planning phase completion requirements before advancement to implementation.

Required Outcomes (P1 Gate):
    - plan_exists: Work has been broken down into actionable tasks
    - estimates_complete: All tasks have effort estimates
    - time_boxing: Implementation tasks ≤ 4.0 hours (STRICT)
    - dependencies_identified: Task sequencing and blockers documented

Purpose:
    Ensures adequate planning completed before starting implementation.
    Focus on OUTCOMES (is there a plan?) not task categorization.

Philosophy Change:
    OLD: "FEATURE must have DESIGN, IMPLEMENTATION, TESTING, DOCUMENTATION tasks"
    NEW: "P1 gate checks if you have a workable plan with estimated tasks"

Pattern:
    1. Get all tasks for work item
    2. Check minimum task count (shows planning happened)
    3. Validate estimates present (shows effort considered)
    4. Enforce time-boxing (prevents monolithic work)
    5. Calculate confidence based on planning quality
"""

from typing import Set

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem
from ...database.enums import WorkItemType, TaskType
from ...database import methods as db_methods


class P1GateValidator(BaseGateValidator):
    """
    Planning phase gate validator.

    Validates that planning phase completed proper task decomposition
    before allowing progression to implementation phase.

    Outcome-Based Validation:
        - plan_exists: ≥1 task created (shows planning happened)
        - estimates: 100% of tasks have effort_hours (effort considered)
        - time_boxing: IMPLEMENTATION ≤ 4.0h (STRICT enforcement)

    Does NOT validate:
        - Task types (users create tasks that make sense for their work)
        - Specific task categories (DESIGN vs PLANNING vs ANALYSIS)

    Philosophy:
        Gate checks "Do we have a plan?" not "Do we have specific task types?"

    Example:
        >>> validator = P1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     for req in result.missing_requirements:
        >>>         print(f"❌ {req}")
    """

    # Validation thresholds
    MIN_TASKS_COUNT = 1  # At least one task (shows planning happened)
    MAX_IMPLEMENTATION_HOURS = 4.0  # STRICT time-boxing (prevents monolithic work)

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate P1 gate requirements (outcome-based).

        Checks OUTCOMES not task types:
            1. Plan exists: ≥1 task created (shows planning happened)
            2. Estimates complete: All tasks have effort_hours (effort considered)
            3. Time-boxing: Implementation tasks ≤ 4.0 hours (prevents monolithic work)

        Does NOT check:
            - Specific task types (DESIGN vs PLANNING vs ANALYSIS)
            - Task categorization (users decide what tasks make sense)

        Args:
            work_item: WorkItem to validate
            db: DatabaseService for task queries

        Returns:
            GateResult with pass/fail and missing requirements

        Example:
            >>> result = validator.validate(work_item, db)
            >>> # result.passed = False
            >>> # result.missing_requirements = [
            >>> #     "No tasks created - planning incomplete",
            >>> #     "3 tasks missing effort estimates"
            >>> # ]
        """
        errors = []

        # Get all tasks for this work item
        tasks = db_methods.tasks.list_tasks(db, work_item_id=work_item.id)

        # Outcome 1: Plan exists (tasks created)
        if len(tasks) < self.MIN_TASKS_COUNT:
            errors.append(
                f"No tasks created - planning incomplete. "
                f"Create ≥{self.MIN_TASKS_COUNT} task to show work has been planned."
            )

        # Outcome 2: Estimates complete (effort considered)
        no_estimate = [t for t in tasks if not t.effort_hours]
        if no_estimate:
            task_ids = [f"#{t.id}" for t in no_estimate[:5]]  # Show first 5
            suffix = f" (and {len(no_estimate)-5} more)" if len(no_estimate) > 5 else ""
            errors.append(
                f"{len(no_estimate)} task(s) missing effort_hours estimate: "
                f"{', '.join(task_ids)}{suffix}. "
                f"Estimate all tasks to show planning is complete."
            )

        # Outcome 3: Time-boxing (prevents monolithic work)
        over_limit = [
            t for t in tasks
            if t.type == TaskType.IMPLEMENTATION and
               t.effort_hours and
               t.effort_hours > self.MAX_IMPLEMENTATION_HOURS
        ]
        if over_limit:
            task_details = [
                f"#{t.id} ({t.effort_hours}h)" for t in over_limit
            ]
            errors.append(
                f"{len(over_limit)} IMPLEMENTATION task(s) exceed "
                f"{self.MAX_IMPLEMENTATION_HOURS}h time-box limit: {', '.join(task_details)}. "
                f"Break large tasks into smaller sub-tasks."
            )

        # Calculate confidence
        estimated_count = len([t for t in tasks if t.effort_hours])
        estimate_rate = 1.0 if len(tasks) == 0 else estimated_count / len(tasks)

        artifacts = {
            'task_count': len(tasks),
            'estimated_count': estimated_count,
            'estimate_rate': estimate_rate,
            'timebox_compliant': len(tasks) - len(over_limit),
            'types_present': len({t.type for t in tasks})  # For info only
        }
        confidence = self._calculate_confidence(work_item, artifacts)

        # Build result
        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=confidence,
            metadata={
                'validation_approach': 'outcome_based',
                'total_tasks': len(tasks),
                'tasks_with_estimates': estimated_count,
                'estimate_completion_rate': f"{estimate_rate:.0%}",
                'over_timebox_limit': len(over_limit),
                'task_types_present': sorted([t.value for t in {task.type for task in tasks}]),  # Info only
                'thresholds': {
                    'min_tasks': self.MIN_TASKS_COUNT,
                    'max_implementation_hours': self.MAX_IMPLEMENTATION_HOURS
                },
                'note': 'This gate checks planning OUTCOMES (tasks, estimates, time-boxing), not task types'
            }
        )
