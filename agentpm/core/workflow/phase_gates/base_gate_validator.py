"""
Base Gate Validator - Abstract Interface for Phase Gates

Defines the contract for all phase gate validators and provides common helper methods.

Gate Validation Responsibility:
    - Check phase-specific requirements are met
    - Calculate confidence score based on information quality
    - Return structured result with missing requirements

Pattern:
    Each gate validator extends BaseGateValidator and implements validate()
    which returns a GateResult containing pass/fail status and detailed feedback.

Security:
    - No direct database writes (read-only)
    - All queries parameterized (SQL injection prevention)
    - Validation logic separated from data access
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

from ...database.models.work_item import WorkItem


@dataclass
class GateResult:
    """
    Result of phase gate validation.

    Attributes:
        passed: True if all requirements met, False otherwise
        missing_requirements: List of requirement descriptions that failed
        confidence: Confidence score 0.0-1.0 (quality of captured information)
        metadata: Additional context about validation (task counts, coverage, etc.)
    """
    passed: bool
    missing_requirements: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate confidence score range"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


class BaseGateValidator(ABC):
    """
    Abstract base class for all phase gate validators.

    Subclasses must implement validate() with phase-specific logic.

    Pattern:
        1. Check required fields exist and meet thresholds
        2. Collect missing requirement descriptions
        3. Calculate confidence score based on information quality
        4. Return GateResult with results

    Example Subclass:
        >>> class D1GateValidator(BaseGateValidator):
        >>>     def validate(self, work_item: WorkItem, db) -> GateResult:
        >>>         errors = []
        >>>         if not work_item.business_context:
        >>>             errors.append("business_context required")
        >>>         confidence = self._calculate_confidence(work_item, {})
        >>>         return GateResult(
        >>>             passed=len(errors) == 0,
        >>>             missing_requirements=errors,
        >>>             confidence=confidence
        >>>         )
    """

    @abstractmethod
    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate phase gate requirements for work item.

        Args:
            work_item: WorkItem entity to validate
            db: DatabaseService instance for queries

        Returns:
            GateResult with validation outcome

        Raises:
            ValueError: If work_item or db is None
        """
        pass

    def _calculate_confidence(
        self,
        work_item: WorkItem,
        artifacts: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score based on information quality.

        Confidence Factors:
            - Completeness: All required fields populated
            - Detail: Field lengths meet minimum thresholds
            - Context: 6W context confidence (if available)
            - Evidence: Supporting artifacts present

        Args:
            work_item: WorkItem with captured information
            artifacts: Dictionary of artifacts (tasks, context, etc.)

        Returns:
            Confidence score 0.0-1.0 (0.0=no info, 1.0=complete and high quality)

        Example:
            >>> confidence = self._calculate_confidence(wi, {'tasks': 5, 'acs': 3})
            >>> # Returns: 0.85 (high confidence - all info present with good detail)
        """
        score = 0.0
        factors = 0

        # Factor 1: Business context quality (0-0.25)
        if work_item.business_context:
            length = len(work_item.business_context)
            if length >= 200:  # Detailed context
                score += 0.25
            elif length >= 100:  # Adequate context
                score += 0.20
            elif length >= 50:  # Minimal context
                score += 0.10
            factors += 1

        # Factor 2: Acceptance criteria count (0-0.25)
        metadata = self._parse_metadata(work_item.metadata)
        ac_count = len(metadata.get('acceptance_criteria', []))
        if ac_count >= 5:  # Comprehensive
            score += 0.25
        elif ac_count >= 3:  # Adequate
            score += 0.20
        elif ac_count >= 1:  # Minimal
            score += 0.10
        factors += 1

        # Factor 3: Risk assessment (0-0.25)
        risk_count = len(metadata.get('risks', []))
        if risk_count >= 3:  # Thorough risk analysis
            score += 0.25
        elif risk_count >= 1:  # Basic risk identification
            score += 0.15
        factors += 1

        # Factor 4: Artifacts quality (0-0.25)
        task_count = artifacts.get('task_count', 0)
        if task_count >= 5:  # Well decomposed
            score += 0.25
        elif task_count >= 3:  # Adequate breakdown
            score += 0.20
        elif task_count >= 1:  # Minimal breakdown
            score += 0.10
        factors += 1

        # Normalize to 0.0-1.0 range
        if factors == 0:
            return 0.0

        return min(score, 1.0)

    def _parse_metadata(self, metadata: Optional[str]) -> Dict[str, Any]:
        """
        Safely parse work item metadata JSON.

        Args:
            metadata: JSON string or None

        Returns:
            Dictionary (empty if parsing fails)

        Security:
            - Catches JSON decode errors
            - Returns empty dict on failure (safe default)
        """
        if not metadata:
            return {}

        try:
            return json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _get_metadata_field(
        self,
        work_item: WorkItem,
        field: str,
        default: Any = None
    ) -> Any:
        """
        Safely extract field from work item metadata.

        Args:
            work_item: WorkItem with metadata
            field: Field name to extract
            default: Default value if field missing

        Returns:
            Field value or default

        Example:
            >>> risks = self._get_metadata_field(wi, 'risks', [])
        """
        metadata = self._parse_metadata(work_item.metadata)
        return metadata.get(field, default)
