"""
Pattern Recognition Models - Database Layer

Pydantic models for architecture pattern detection results.

Moved from core/detection/patterns/models.py to follow database-first architecture.
All detection-related models are now in the database layer, aligning with APM (Agent Project Manager)'s
database-driven design.

**Models**:
- PatternMatch: Individual pattern detection result
- PatternAnalysis: Complete analysis results

**Usage Example**:

    from agentpm.core.database.models.detection_pattern import (
        PatternMatch,
        PatternAnalysis
    )
    from agentpm.core.database.enums.detection import ArchitecturePattern

    # Create a pattern match
    match = PatternMatch(
        pattern=ArchitecturePattern.HEXAGONAL,
        confidence=0.85,
        evidence=[
            'domain/ directory found',
            'ports/ directory found',
            'adapters/ directory found'
        ],
        violations=[],
        recommendations=['Consider implementing domain events']
    )

    # Create analysis
    analysis = PatternAnalysis(
        project_path='/path/to/project',
        matches=[match],
        primary_pattern=ArchitecturePattern.HEXAGONAL,
        confidence_threshold=0.6
    )

    # Filter high confidence patterns
    high_conf = analysis.get_high_confidence_patterns()
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ..enums.detection import ArchitecturePattern


class PatternMatch(BaseModel):
    """
    Detected architecture pattern with confidence and evidence.

    **Attributes**:
    - pattern: The detected architecture pattern
    - confidence: Confidence score 0.0-1.0
    - evidence: List of supporting evidence (directories, files, etc.)
    - violations: List of pattern violations found
    - recommendations: List of improvement recommendations

    **Example**:
        match = PatternMatch(
            pattern=ArchitecturePattern.HEXAGONAL,
            confidence=0.85,
            evidence=['domain/ found', 'ports/ found'],
            violations=['Domain importing from adapters'],
            recommendations=['Remove adapter imports from domain']
        )

        if match.confidence > 0.7:
            print(f"High confidence: {match.pattern}")
            for violation in match.violations:
                print(f"  Warning: {violation}")
    """

    pattern: ArchitecturePattern
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    evidence: List[str] = Field(
        default_factory=list,
        description="List of supporting evidence for pattern detection"
    )
    violations: List[str] = Field(
        default_factory=list,
        description="List of pattern violations found"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of recommendations for pattern improvement"
    )

    def has_violations(self) -> bool:
        """Check if pattern has any violations."""
        return len(self.violations) > 0

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if confidence exceeds threshold."""
        return self.confidence >= threshold

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "pattern": "hexagonal",
                "confidence": 0.85,
                "evidence": [
                    "domain/ directory found",
                    "ports/ directory found",
                    "adapters/ directory found"
                ],
                "violations": [
                    "Domain code importing from adapters"
                ],
                "recommendations": [
                    "Remove adapter imports from domain layer",
                    "Implement dependency injection"
                ]
            }
        }


class PatternAnalysis(BaseModel):
    """
    Complete pattern recognition analysis results.

    **Attributes**:
    - project_path: Path to analyzed project
    - matches: List of detected pattern matches
    - primary_pattern: Primary detected pattern (highest confidence)
    - confidence_threshold: Minimum confidence for inclusion
    - analyzed_at: Timestamp of analysis

    **Example**:
        analysis = PatternAnalysis(
            project_path='/path/to/project',
            matches=[
                PatternMatch(
                    pattern=ArchitecturePattern.HEXAGONAL,
                    confidence=0.85,
                    evidence=['...']
                ),
                PatternMatch(
                    pattern=ArchitecturePattern.DDD,
                    confidence=0.75,
                    evidence=['...']
                )
            ],
            primary_pattern=ArchitecturePattern.HEXAGONAL,
            confidence_threshold=0.6
        )

        # Get high confidence patterns
        high_conf = analysis.get_high_confidence_patterns()
        print(f"Found {len(high_conf)} high confidence patterns")

        # Get primary pattern details
        if analysis.primary_pattern:
            primary = next(
                m for m in analysis.matches
                if m.pattern == analysis.primary_pattern
            )
            print(f"Primary: {primary.pattern} ({primary.confidence:.0%})")
    """

    project_path: str = Field(..., description="Path to analyzed project")
    matches: List[PatternMatch] = Field(
        default_factory=list,
        description="List of detected pattern matches"
    )
    primary_pattern: Optional[ArchitecturePattern] = Field(
        None,
        description="Primary detected pattern (highest confidence)"
    )
    confidence_threshold: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for pattern inclusion"
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of analysis"
    )

    def get_high_confidence_patterns(self) -> List[PatternMatch]:
        """
        Get patterns with confidence >= threshold.

        Returns:
            List of PatternMatch objects with confidence >= threshold

        Example:
            analysis = PatternAnalysis(...)
            high_conf = analysis.get_high_confidence_patterns()
            for match in high_conf:
                print(f"{match.pattern}: {match.confidence:.0%}")
        """
        return [
            match for match in self.matches
            if match.confidence >= self.confidence_threshold
        ]

    def get_patterns_with_violations(self) -> List[PatternMatch]:
        """
        Get patterns that have violations.

        Returns:
            List of PatternMatch objects with violations

        Example:
            analysis = PatternAnalysis(...)
            with_violations = analysis.get_patterns_with_violations()
            for match in with_violations:
                print(f"{match.pattern} has {len(match.violations)} violations")
        """
        return [match for match in self.matches if match.has_violations()]

    def get_match(self, pattern: ArchitecturePattern) -> Optional[PatternMatch]:
        """
        Get specific pattern match by pattern type.

        Args:
            pattern: Pattern type to find

        Returns:
            PatternMatch if found, None otherwise

        Example:
            analysis = PatternAnalysis(...)
            hexagonal = analysis.get_match(ArchitecturePattern.HEXAGONAL)
            if hexagonal:
                print(f"Hexagonal confidence: {hexagonal.confidence:.0%}")
        """
        for match in self.matches:
            if match.pattern == pattern:
                return match
        return None

    def get_sorted_matches(self, reverse: bool = True) -> List[PatternMatch]:
        """
        Get matches sorted by confidence.

        Args:
            reverse: If True, sort descending (highest first)

        Returns:
            Sorted list of PatternMatch objects

        Example:
            analysis = PatternAnalysis(...)
            sorted_matches = analysis.get_sorted_matches()
            print(f"Top pattern: {sorted_matches[0].pattern}")
        """
        return sorted(self.matches, key=lambda m: m.confidence, reverse=reverse)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "project_path": "/path/to/project",
                "matches": [
                    {
                        "pattern": "hexagonal",
                        "confidence": 0.85,
                        "evidence": ["domain/ directory found"],
                        "violations": [],
                        "recommendations": []
                    }
                ],
                "primary_pattern": "hexagonal",
                "confidence_threshold": 0.6,
                "analyzed_at": "2025-10-24T10:00:00"
            }
        }
