"""
E1 Gate Validator - Evolution Phase (Continuous Improvement)

Validates evolution phase requirements for continuous improvement and learning.

Required Information (E1 Gate):
    - telemetry_analyzed: Production metrics reviewed
    - feedback_collected: User feedback captured
    - improvements_identified: Future enhancements documented
    - lessons_learned: Learnings captured for future work

Purpose:
    Ensures continuous improvement feedback loop operates.
    Captures learnings and identifies future work.

Evolution Requirements:
    - Production telemetry analyzed
    - Performance/usage patterns identified
    - User feedback collected
    - Improvements prioritized
    - Lessons learned documented

Pattern:
    1. Check telemetry analysis complete
    2. Check feedback collected
    3. Check improvements identified
    4. Check lessons learned captured
    5. Calculate confidence based on learning quality

Note:
    E1 is continuous - work items stay in E1_EVOLUTION phase
    for ongoing monitoring and improvement identification.
"""

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem


class E1GateValidator(BaseGateValidator):
    """
    Evolution phase gate validator.

    Validates that evolution phase captured learnings and improvements
    for continuous improvement feedback loop.

    Requirements:
        - Telemetry analyzed
        - Feedback collected
        - Improvements identified
        - Lessons learned documented

    Note:
        E1 is continuous phase - validation checks ongoing learning
        rather than blocking advancement (no next phase).

    Example:
        >>> validator = E1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     print(f"Learning gaps: {result.missing_requirements}")
    """

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate E1 gate requirements.

        Checks:
            1. Telemetry analyzed
            2. Feedback collected
            3. Improvements identified
            4. Lessons learned documented

        Args:
            work_item: WorkItem to validate
            db: DatabaseService for metadata queries

        Returns:
            GateResult with pass/fail and missing requirements

        Note:
            E1 validation is informational - identifies learning gaps
            but doesn't block (no next phase to advance to).

        Example:
            >>> result = validator.validate(work_item, db)
            >>> # result.passed = False
            >>> # result.missing_requirements = [
            >>> #     "Telemetry analysis not complete",
            >>> #     "User feedback not collected"
            >>> # ]
        """
        errors = []
        metadata = self._parse_metadata(work_item.metadata)
        evolution = metadata.get('evolution', {})

        # Check 1: Telemetry analyzed
        telemetry = evolution.get('telemetry', {})
        if not telemetry.get('analyzed'):
            errors.append("Telemetry analysis not complete")

        # Check 2: Feedback collected
        feedback = evolution.get('feedback', {})
        feedback_count = len(feedback.get('items', []))
        if feedback_count == 0:
            errors.append("User feedback not collected")

        # Check 3: Improvements identified
        improvements = evolution.get('improvements', {})
        improvement_count = len(improvements.get('items', []))
        if improvement_count == 0:
            errors.append("No improvements identified")

        # Check 4: Lessons learned
        lessons = evolution.get('lessons_learned', {})
        if not lessons.get('documented'):
            errors.append("Lessons learned not documented")

        # Calculate confidence
        checks_passed = sum([
            telemetry.get('analyzed', False),
            feedback_count > 0,
            improvement_count > 0,
            lessons.get('documented', False)
        ])
        total_checks = 4

        artifacts = {
            'task_count': 0,  # Not relevant for E1
            'checks_passed': checks_passed,
            'checks_total': total_checks,
            'feedback_count': feedback_count,
            'improvement_count': improvement_count,
            'telemetry_analyzed': telemetry.get('analyzed', False),
            'lessons_documented': lessons.get('documented', False)
        }
        confidence = self._calculate_confidence(work_item, artifacts)

        # Build result
        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=confidence,
            metadata={
                'telemetry_analyzed': telemetry.get('analyzed', False),
                'feedback_collected': feedback_count,
                'improvements_identified': improvement_count,
                'lessons_documented': lessons.get('documented', False),
                'checks_passed': checks_passed,
                'checks_total': total_checks,
                'note': 'E1 is continuous - validation identifies learning gaps'
            }
        )
