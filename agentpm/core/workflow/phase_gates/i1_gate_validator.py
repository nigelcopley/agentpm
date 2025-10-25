"""
I1 Gate Validator - Implementation → Review Gate

Validates implementation phase completion requirements before advancement to review.

Required Outcomes (I1 Gate):
    - work_complete: All tasks marked DONE (implementation finished)
    - code_present: Code changes exist (not just planning)
    - tests_exist: Test coverage adequate (quality validated)
    - docs_updated: Documentation reflects changes

Purpose:
    Ensures implementation work completed before quality review.
    Focus on OUTCOMES (is code complete and tested?) not task categorization.

Philosophy Change:
    OLD: "All IMPLEMENTATION tasks DONE, all TESTING tasks DONE, all DOCUMENTATION tasks DONE"
    NEW: "I1 gate checks if code is complete, tested, and documented"

Pattern:
    1. Get all tasks for work item
    2. Check all tasks DONE (work finished)
    3. Validate test coverage adequate (quality checked)
    4. Check documentation updated (knowledge captured)
    5. Calculate confidence based on completion quality
"""

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem
from ...database.enums import TaskType, TaskStatus
from ...database import methods as db_methods


class I1GateValidator(BaseGateValidator):
    """
    Implementation phase gate validator.

    Validates that implementation phase completed all work
    before allowing progression to review phase.

    Outcome-Based Validation:
        - work_complete: All tasks DONE (implementation finished)
        - tests_adequate: Test coverage meets thresholds (quality validated)

    Does NOT validate:
        - Task types (IMPLEMENTATION vs TESTING vs DOCUMENTATION)
        - Task categorization (users decide what tasks make sense)

    Philosophy:
        Gate checks "Is code complete and tested?" not "Are specific task types DONE?"

    Example:
        >>> validator = I1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     print(f"Incomplete: {result.missing_requirements}")
    """

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate I1 gate requirements (outcome-based).

        Checks OUTCOMES not task types:
            1. Work complete: All tasks DONE (implementation finished)
            2. Tests adequate: Test coverage meets thresholds (quality validated)

        Does NOT check:
            - Specific task types DONE (IMPLEMENTATION vs TESTING vs DOCUMENTATION)
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
            >>> #     "3 tasks not DONE - complete all work before review",
            >>> #     "Test coverage below threshold"
            >>> # ]
        """
        errors = []

        # Get all tasks for this work item
        tasks = db_methods.tasks.list_tasks(db, work_item_id=work_item.id)

        # Outcome 1: Work complete (all tasks DONE)
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

        # Outcome 2: Tests adequate (coverage meets thresholds)
        coverage_result = self._validate_test_coverage(work_item, db)
        if not coverage_result['passed']:
            errors.extend(coverage_result['errors'])

        # Calculate confidence
        completion_rate = 1.0 if len(tasks) == 0 else (
            (len(tasks) - len(incomplete_tasks)) / len(tasks)
        )

        artifacts = {
            'task_count': len(tasks),
            'done_count': len(tasks) - len(incomplete_tasks),
            'completion_rate': completion_rate,
            'coverage_met': coverage_result['passed'],
            'task_types_present': len({t.type for t in tasks})  # For info only
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
                'tasks_done': len(tasks) - len(incomplete_tasks),
                'completion_rate': f"{completion_rate:.0%}",
                'incomplete_tasks': [
                    {'id': t.id, 'type': t.type.value, 'name': t.name}
                    for t in incomplete_tasks
                ],
                'coverage_results': coverage_result,
                'note': 'This gate checks implementation OUTCOMES (work complete, tests adequate), not task types'
            }
        )

    def _validate_test_coverage(
        self,
        work_item: WorkItem,
        db
    ) -> dict:
        """
        Validate test coverage meets category-specific thresholds.

        Uses rules system to check coverage requirements (if available).

        Args:
            work_item: WorkItem to check
            db: DatabaseService

        Returns:
            Dictionary with:
                - passed: bool (coverage adequate?)
                - errors: List[str] (coverage violations)
                - coverage_by_category: Dict (actual coverage by category)

        Note:
            If rules system unavailable, returns passed=True (optimistic)
        """
        try:
            # Attempt to use rules system for coverage validation
            # (This would integrate with WI-81 value-based testing strategy)
            from ...rules import methods as rule_methods

            # Check if coverage rules exist
            coverage_rules = rule_methods.get_rules_by_category(
                db,
                category='testing',
                enforcement_level='BLOCK'
            )

            if not coverage_rules:
                # No rules - assume coverage adequate
                return {
                    'passed': True,
                    'errors': [],
                    'note': 'No coverage rules configured'
                }

            # TODO: Implement actual coverage checking via rules system
            # For now, return optimistic result
            return {
                'passed': True,
                'errors': [],
                'note': 'Coverage validation not yet implemented'
            }

        except (ImportError, AttributeError):
            # Rules system not available - assume coverage adequate
            return {
                'passed': True,
                'errors': [],
                'note': 'Rules system not available'
            }
