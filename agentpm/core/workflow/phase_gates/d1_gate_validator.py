"""
D1 Gate Validator - Discovery → Planning Gate

Validates discovery phase completion requirements before advancement to planning.

Required Information (D1 Gate):
    - business_context: ≥50 characters explaining WHY this matters
    - acceptance_criteria: ≥3 testable criteria
    - risks: ≥1 identified risk with mitigation
    - 6W context: ≥70% confidence (who, what, when, where, why, how)

Purpose:
    Ensures sufficient discovery work completed before planning phase.
    Prevents premature planning without understanding requirements.

Pattern:
    1. Check business_context length and quality
    2. Count acceptance_criteria in metadata
    3. Check risks identified
    4. Validate 6W context confidence (if available)
    5. Calculate overall confidence score
"""

from typing import Any, Dict

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem


class D1GateValidator(BaseGateValidator):
    """
    Discovery phase gate validator.

    Validates that discovery phase captured sufficient information
    before allowing progression to planning phase.

    Thresholds:
        - business_context: ≥50 chars (explains business value)
        - acceptance_criteria: ≥3 (testable success criteria)
        - risks: ≥1 (at least one risk identified)
        - 6W confidence: ≥0.70 (adequate context quality)

    Example:
        >>> validator = D1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     print(f"Missing: {result.missing_requirements}")
        >>> print(f"Confidence: {result.confidence:.0%}")
    """

    # Validation thresholds
    MIN_BUSINESS_CONTEXT_LENGTH = 50  # characters
    MIN_ACCEPTANCE_CRITERIA_COUNT = 3  # criteria
    MIN_RISKS_COUNT = 1  # risks identified
    MIN_SIX_W_CONFIDENCE = 0.70  # 70% context quality

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate D1 gate requirements.

        Checks:
            1. business_context exists and meets length requirement
            2. acceptance_criteria count ≥ 3
            3. risks count ≥ 1
            4. 6W context confidence ≥ 70% (if available)

        Args:
            work_item: WorkItem to validate
            db: DatabaseService for context queries

        Returns:
            GateResult with pass/fail and missing requirements

        Example:
            >>> result = validator.validate(work_item, db)
            >>> # result.passed = False
            >>> # result.missing_requirements = [
            >>> #     "business_context required (≥50 characters)",
            >>> #     "Need ≥3 acceptance criteria (found 1)"
            >>> # ]
            >>> # result.confidence = 0.45
        """
        errors = []
        metadata_dict = self._parse_metadata(work_item.metadata)

        # Check 1: Business context
        if not work_item.business_context:
            errors.append(
                f"business_context required "
                f"(≥{self.MIN_BUSINESS_CONTEXT_LENGTH} characters)"
            )
        elif len(work_item.business_context) < self.MIN_BUSINESS_CONTEXT_LENGTH:
            errors.append(
                f"business_context too short "
                f"({len(work_item.business_context)} chars, "
                f"need ≥{self.MIN_BUSINESS_CONTEXT_LENGTH})"
            )

        # Check 2: Acceptance criteria
        ac_list = metadata_dict.get('acceptance_criteria', [])
        if not isinstance(ac_list, list):
            ac_list = []

        if len(ac_list) < self.MIN_ACCEPTANCE_CRITERIA_COUNT:
            errors.append(
                f"Need ≥{self.MIN_ACCEPTANCE_CRITERIA_COUNT} "
                f"acceptance criteria (found {len(ac_list)})"
            )

        # Check 3: Risks
        risks = metadata_dict.get('risks', [])
        if not isinstance(risks, list):
            risks = []

        if len(risks) < self.MIN_RISKS_COUNT:
            errors.append(
                f"At least {self.MIN_RISKS_COUNT} risk must be identified "
                f"(found {len(risks)})"
            )

        # Check 4: 6W Context (if context system available)
        six_w_confidence = self._get_six_w_confidence(work_item, db)
        if six_w_confidence is not None:
            if six_w_confidence < self.MIN_SIX_W_CONFIDENCE:
                errors.append(
                    f"6W context confidence too low "
                    f"({six_w_confidence:.0%}, need ≥{self.MIN_SIX_W_CONFIDENCE:.0%})"
                )

        # Calculate confidence score
        artifacts = {
            'task_count': 0,  # No tasks yet at D1
            'ac_count': len(ac_list),
            'risk_count': len(risks),
            'six_w_confidence': six_w_confidence or 0.0
        }
        confidence = self._calculate_confidence(work_item, artifacts)

        # Build result
        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=confidence,
            metadata={
                'business_context_length': len(work_item.business_context or ''),
                'acceptance_criteria_count': len(ac_list),
                'risks_count': len(risks),
                'six_w_confidence': six_w_confidence,
                'thresholds': {
                    'business_context': self.MIN_BUSINESS_CONTEXT_LENGTH,
                    'acceptance_criteria': self.MIN_ACCEPTANCE_CRITERIA_COUNT,
                    'risks': self.MIN_RISKS_COUNT,
                    'six_w': self.MIN_SIX_W_CONFIDENCE
                }
            }
        )

    def _get_six_w_confidence(
        self,
        work_item: WorkItem,
        db
    ) -> float | None:
        """
        Get 6W context confidence from context system (if available).

        Args:
            work_item: WorkItem to check
            db: DatabaseService

        Returns:
            Confidence score 0.0-1.0 or None if context system unavailable

        Note:
            Context system integration optional - returns None if not available
        """
        try:
            from ...context import methods as context_methods
            from ...database.enums.entity_type import EntityType

            context = context_methods.get_entity_context(
                db,
                EntityType.WORK_ITEM,
                work_item.id
            )

            if context:
                return context.confidence_score
            return None

        except (ImportError, AttributeError):
            # Context system not available
            return None
