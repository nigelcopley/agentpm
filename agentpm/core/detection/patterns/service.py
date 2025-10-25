"""
Pattern Recognition Service - Layer 3 (Detection Services)

Service for architecture pattern detection using Layer 1 utilities.

**Architecture Compliance**:
- Layer 3: Detection Services
- Uses Layer 1 utilities (pattern_matchers)
- Performance: <200ms per pattern, <1s total

**Responsibilities**:
- Detect architecture patterns using pattern_matchers
- Identify pattern violations
- Provide pattern recommendations
- Confidence scoring

**Usage Example**:

    from agentpm.core.detection.patterns import PatternRecognitionService
    from pathlib import Path

    # Initialize service
    service = PatternRecognitionService(Path('/path/to/project'))

    # Analyze all patterns
    analysis = service.analyze_patterns(confidence_threshold=0.6)

    # Get results
    print(f"Primary pattern: {analysis.primary_pattern}")
    print(f"Matches: {len(analysis.matches)}")

    # High confidence patterns
    for match in analysis.get_high_confidence_patterns():
        print(f"\n{match.pattern.value.upper()}")
        print(f"  Confidence: {match.confidence:.0%}")
        print(f"  Evidence:")
        for evidence in match.evidence:
            print(f"    - {evidence}")
        if match.violations:
            print(f"  Violations:")
            for violation in match.violations:
                print(f"    - {violation}")

    # Individual pattern detection
    hexagonal = service.detect_hexagonal()
    if hexagonal.confidence > 0.7:
        print(f"Hexagonal architecture detected: {hexagonal.confidence:.0%}")

**Performance Targets**:
- Single pattern: <200ms
- All patterns: <1s
- Cached: <50ms
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentpm.core.database.models.detection_pattern import (
    PatternAnalysis,
    PatternMatch,
)
from agentpm.core.database.enums.detection import (
    ArchitecturePattern,
)

# Import Layer 1 utilities (pattern_matchers)
from agentpm.utils.pattern_matchers import (
    detect_cqrs_pattern,
    detect_ddd_patterns,
    detect_hexagonal_architecture,
    detect_layered_architecture,
    detect_mvc_pattern,
    detect_pattern_violations,
)

logger = logging.getLogger(__name__)


class PatternRecognitionService:
    """
    Service for architecture pattern recognition.

    **Responsibilities**:
    - Detect architecture patterns using pattern_matchers
    - Identify pattern violations
    - Provide pattern recommendations
    - Confidence scoring

    **Architecture Compliance**:
    - Layer 3: Detection Service
    - Uses Layer 1 utilities (pattern_matchers)
    - No Layer 2 plugin dependencies

    **Example**:
        service = PatternRecognitionService(Path('/project'))
        analysis = service.analyze_patterns()

        print(f"Primary pattern: {analysis.primary_pattern}")
        for match in analysis.get_high_confidence_patterns():
            print(f"- {match.pattern}: {match.confidence:.0%}")

    **Performance**:
    - Pattern detection: <200ms per project
    - All patterns: <1s total
    """

    def __init__(self, project_path: Path):
        """
        Initialize pattern recognition service.

        Args:
            project_path: Path to project root directory

        Raises:
            ValueError: If project_path does not exist or is not a directory

        Example:
            service = PatternRecognitionService(Path('/path/to/project'))
        """
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        self.project_path = project_path
        logger.debug(f"Initialized PatternRecognitionService for {project_path}")

    def analyze_patterns(
        self,
        confidence_threshold: float = 0.5
    ) -> PatternAnalysis:
        """
        Analyze project for all architecture patterns.

        **Process**:
        1. Run all pattern detectors (hexagonal, layered, DDD, CQRS, MVC)
        2. Collect confidence scores and evidence
        3. Detect violations for matched patterns
        4. Determine primary pattern (highest confidence)
        5. Generate recommendations

        Args:
            confidence_threshold: Minimum confidence to include pattern (0.0-1.0)

        Returns:
            Complete PatternAnalysis with all detected patterns

        Example:
            service = PatternRecognitionService(Path('/project'))
            analysis = service.analyze_patterns(confidence_threshold=0.6)

            print(f"Primary: {analysis.primary_pattern}")
            print(f"High confidence patterns: {len(analysis.get_high_confidence_patterns())}")

            for match in analysis.matches:
                if match.confidence >= confidence_threshold:
                    print(f"- {match.pattern}: {match.confidence:.0%}")

        Performance:
            - Target: <1s for all patterns
            - Individual patterns: <200ms each
        """
        logger.info(f"Analyzing patterns for {self.project_path}")

        # Run all pattern detectors
        matches: List[PatternMatch] = []

        try:
            # Detect all patterns
            matches.append(self.detect_hexagonal())
            matches.append(self.detect_layered())
            matches.append(self.detect_ddd())
            matches.append(self.detect_cqrs())
            matches.append(self.detect_mvc())

            # Determine primary pattern (highest confidence)
            primary_pattern = self._determine_primary_pattern(matches)

            # Generate recommendations
            self._add_recommendations(matches)

            logger.info(
                f"Pattern analysis complete: {len(matches)} patterns, "
                f"primary={primary_pattern}"
            )

        except Exception as e:
            logger.error(f"Error during pattern analysis: {e}", exc_info=True)
            # Return empty analysis on error
            return PatternAnalysis(
                project_path=str(self.project_path),
                matches=[],
                primary_pattern=None,
                confidence_threshold=confidence_threshold
            )

        return PatternAnalysis(
            project_path=str(self.project_path),
            matches=matches,
            primary_pattern=primary_pattern,
            confidence_threshold=confidence_threshold
        )

    def detect_hexagonal(self) -> PatternMatch:
        """
        Detect hexagonal architecture pattern.

        Uses pattern_matchers.detect_hexagonal_architecture() from Layer 1.

        **Evidence**:
        - domain/ or core/ directory
        - ports/ or interfaces/ directory
        - adapters/ or infrastructure/ directory

        **Violations**:
        - Domain importing from adapters
        - Domain importing from infrastructure

        Returns:
            PatternMatch for hexagonal architecture

        Example:
            service = PatternRecognitionService(Path('/project'))
            hexagonal = service.detect_hexagonal()

            if hexagonal.confidence > 0.7:
                print("Hexagonal architecture detected")
                print(f"Evidence: {', '.join(hexagonal.evidence)}")

            if hexagonal.violations:
                print("Violations found:")
                for violation in hexagonal.violations:
                    print(f"  - {violation}")

        Performance:
            - Target: <200ms
        """
        logger.debug("Detecting hexagonal architecture")

        try:
            # Use Layer 1 utility
            result = detect_hexagonal_architecture(self.project_path)

            # Convert to PatternMatch
            match = PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"Hexagonal detection complete: confidence={match.confidence:.2f}, "
                f"evidence={len(match.evidence)}, violations={len(match.violations)}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting hexagonal pattern: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.HEXAGONAL,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def detect_layered(self) -> PatternMatch:
        """
        Detect layered architecture pattern.

        Uses pattern_matchers.detect_layered_architecture() from Layer 1.

        **Evidence**:
        - presentation/ or ui/ or views/ layer
        - application/ or services/ layer
        - domain/ or business/ layer
        - data/ or persistence/ layer

        **Violations**:
        - Lower layer importing from higher layer
        - Circular dependencies between layers

        Returns:
            PatternMatch for layered architecture

        Example:
            service = PatternRecognitionService(Path('/project'))
            layered = service.detect_layered()

            if layered.confidence > 0.5:
                print(f"Layered architecture: {layered.confidence:.0%}")
                print("Layers found:")
                for evidence in layered.evidence:
                    print(f"  - {evidence}")

        Performance:
            - Target: <200ms
        """
        logger.debug("Detecting layered architecture")

        try:
            # Use Layer 1 utility
            result = detect_layered_architecture(self.project_path)

            match = PatternMatch(
                pattern=ArchitecturePattern.LAYERED,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"Layered detection complete: confidence={match.confidence:.2f}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting layered pattern: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.LAYERED,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def detect_ddd(self) -> PatternMatch:
        """
        Detect Domain-Driven Design pattern.

        Uses pattern_matchers.detect_ddd_patterns() from Layer 1.

        **Evidence**:
        - Entities (files ending in *Entity.py or in entities/)
        - Value Objects (ValueObject.py or value_objects/)
        - Aggregates (Aggregate.py or aggregates/)
        - Repositories (Repository.py or repositories/)
        - Domain Services (DomainService.py or domain_services/)

        **Violations**:
        - Anemic domain models (entities with no methods)
        - Domain logic in services instead of entities

        Returns:
            PatternMatch for DDD

        Example:
            service = PatternRecognitionService(Path('/project'))
            ddd = service.detect_ddd()

            if ddd.confidence > 0.6:
                print("Domain-Driven Design patterns detected")
                for pattern in ddd.evidence:
                    print(f"  - {pattern}")

        Performance:
            - Target: <200ms
        """
        logger.debug("Detecting DDD patterns")

        try:
            # Use Layer 1 utility
            result = detect_ddd_patterns(self.project_path)

            match = PatternMatch(
                pattern=ArchitecturePattern.DDD,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"DDD detection complete: confidence={match.confidence:.2f}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting DDD pattern: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.DDD,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def detect_cqrs(self) -> PatternMatch:
        """
        Detect CQRS pattern.

        Uses pattern_matchers.detect_cqrs_pattern() from Layer 1.

        **Evidence**:
        - commands/ directory
        - queries/ directory
        - handlers/ directory (or command_handlers/, query_handlers/)
        - Separation of read/write models

        **Violations**:
        - Commands in query layer
        - Queries in command layer
        - Shared models between commands and queries

        Returns:
            PatternMatch for CQRS

        Example:
            service = PatternRecognitionService(Path('/project'))
            cqrs = service.detect_cqrs()

            if cqrs.confidence > 0.7:
                print("CQRS pattern detected")
                print(f"Evidence: {', '.join(cqrs.evidence)}")

        Performance:
            - Target: <200ms
        """
        logger.debug("Detecting CQRS pattern")

        try:
            # Use Layer 1 utility
            result = detect_cqrs_pattern(self.project_path)

            match = PatternMatch(
                pattern=ArchitecturePattern.CQRS,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"CQRS detection complete: confidence={match.confidence:.2f}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting CQRS pattern: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.CQRS,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def detect_mvc(self) -> PatternMatch:
        """
        Detect MVC pattern.

        Uses pattern_matchers.detect_mvc_pattern() from Layer 1.

        **Evidence**:
        - models/ directory
        - views/ directory
        - controllers/ directory
        - Clear separation between layers

        **Violations**:
        - Models importing from views/controllers
        - Views containing business logic

        Returns:
            PatternMatch for MVC

        Example:
            service = PatternRecognitionService(Path('/project'))
            mvc = service.detect_mvc()

            if mvc.confidence > 0.8:
                print("MVC pattern detected")
                for component in mvc.evidence:
                    print(f"  - {component}")

        Performance:
            - Target: <200ms
        """
        logger.debug("Detecting MVC pattern")

        try:
            # Use Layer 1 utility
            result = detect_mvc_pattern(self.project_path)

            match = PatternMatch(
                pattern=ArchitecturePattern.MVC,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"MVC detection complete: confidence={match.confidence:.2f}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting MVC pattern: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.MVC,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def find_violations(
        self,
        pattern: ArchitecturePattern,
        dependency_graph: Optional[Any] = None
    ) -> List[str]:
        """
        Find violations of architecture pattern.

        Uses pattern_matchers.detect_pattern_violations() from Layer 1.

        Args:
            pattern: Pattern to check violations for
            dependency_graph: Optional dependency graph for validation

        Returns:
            List of violation descriptions

        Example:
            service = PatternRecognitionService(Path('/project'))
            violations = service.find_violations(ArchitecturePattern.HEXAGONAL)

            if violations:
                print("Hexagonal architecture violations:")
                for violation in violations:
                    print(f"  - {violation}")

        Performance:
            - Target: <100ms per pattern
        """
        logger.debug(f"Finding violations for {pattern.value}")

        try:
            # Use Layer 1 utility
            violations_list = detect_pattern_violations(
                self.project_path,
                pattern.value,
                dependency_graph
            )

            # Format violations
            formatted = self._format_violations(violations_list)

            logger.debug(
                f"Violation detection complete: {len(formatted)} violations found"
            )

            return formatted

        except Exception as e:
            logger.error(f"Error finding violations: {e}", exc_info=True)
            return [f"Error detecting violations: {str(e)}"]

    def generate_recommendations(
        self,
        matches: List[PatternMatch]
    ) -> List[str]:
        """
        Generate recommendations based on detected patterns.

        **Recommendations**:
        - If no clear pattern: Suggest adopting one
        - If multiple patterns: Suggest consolidation
        - If violations found: Suggest fixes
        - If low confidence: Suggest improvements

        Args:
            matches: List of pattern matches

        Returns:
            List of recommendations

        Example:
            service = PatternRecognitionService(Path('/project'))
            analysis = service.analyze_patterns()
            recommendations = service.generate_recommendations(analysis.matches)

            print("Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

        Performance:
            - Target: <50ms
        """
        logger.debug("Generating recommendations")

        recommendations = []

        # Filter high confidence patterns
        high_confidence = [m for m in matches if m.confidence >= 0.7]
        medium_confidence = [m for m in matches if 0.5 <= m.confidence < 0.7]
        with_violations = [m for m in matches if m.violations]

        # No clear pattern
        if not high_confidence:
            recommendations.append(
                "No clear architecture pattern detected. "
                "Consider adopting a well-defined architecture pattern "
                "(Hexagonal, Layered, or Clean Architecture)."
            )

        # Multiple high confidence patterns (potential mix)
        if len(high_confidence) > 2:
            pattern_names = ', '.join([m.pattern.value for m in high_confidence])
            recommendations.append(
                f"Multiple architecture patterns detected: {pattern_names}. "
                f"Consider consolidating to a single primary pattern for consistency."
            )

        # Violations found
        if with_violations:
            for match in with_violations:
                recommendations.append(
                    f"{match.pattern.value.upper()}: "
                    f"{len(match.violations)} violation(s) found. "
                    f"Review and fix violations to improve architecture quality."
                )

        # Medium confidence patterns (needs improvement)
        if medium_confidence and not high_confidence:
            for match in medium_confidence:
                recommendations.append(
                    f"{match.pattern.value.upper()}: "
                    f"Pattern partially detected (confidence: {match.confidence:.0%}). "
                    f"Consider strengthening pattern implementation."
                )

        # Specific pattern recommendations
        for match in high_confidence:
            if match.pattern == ArchitecturePattern.HEXAGONAL:
                if not match.violations:
                    recommendations.append(
                        "Hexagonal architecture well-implemented. "
                        "Consider adding domain events for better decoupling."
                    )

            elif match.pattern == ArchitecturePattern.DDD:
                if not match.violations:
                    recommendations.append(
                        "Domain-Driven Design patterns detected. "
                        "Ensure domain models are rich (not anemic) and "
                        "consider implementing bounded contexts."
                    )

            elif match.pattern == ArchitecturePattern.LAYERED:
                recommendations.append(
                    "Layered architecture detected. "
                    "Ensure strict unidirectional dependencies "
                    "(higher layers depend on lower, never reverse)."
                )

        logger.debug(f"Generated {len(recommendations)} recommendations")

        return recommendations

    # ==============================================================================
    # Internal Helper Methods
    # ==============================================================================

    def _determine_primary_pattern(
        self,
        matches: List[PatternMatch]
    ) -> Optional[ArchitecturePattern]:
        """
        Determine primary pattern based on confidence scores.

        Args:
            matches: List of pattern matches

        Returns:
            Primary pattern (highest confidence) or None

        Logic:
            - Return pattern with highest confidence
            - Must have confidence >= 0.5
            - If tie, prefer: Hexagonal > DDD > Layered > CQRS > MVC
        """
        if not matches:
            return None

        # Filter matches with confidence >= 0.5
        valid_matches = [m for m in matches if m.confidence >= 0.5]
        if not valid_matches:
            return None

        # Sort by confidence (descending)
        sorted_matches = sorted(
            valid_matches,
            key=lambda m: m.confidence,
            reverse=True
        )

        # Return highest confidence pattern
        return sorted_matches[0].pattern

    def _format_violations(
        self,
        violations: List[Any]
    ) -> List[str]:
        """
        Format violations into string descriptions.

        Args:
            violations: List of violation dictionaries or strings

        Returns:
            List of formatted violation strings
        """
        formatted = []

        for violation in violations:
            if isinstance(violation, dict):
                # Format: "type: description (location)"
                vtype = violation.get('type', 'violation')
                description = violation.get('description', 'Unknown violation')
                location = violation.get('location', '')

                if location:
                    formatted.append(f"{vtype}: {description} ({location})")
                else:
                    formatted.append(f"{vtype}: {description}")

            elif isinstance(violation, str):
                formatted.append(violation)

            else:
                formatted.append(str(violation))

        return formatted

    def _add_recommendations(self, matches: List[PatternMatch]) -> None:
        """
        Add recommendations to pattern matches in-place.

        Args:
            matches: List of pattern matches to augment
        """
        try:
            recommendations = self.generate_recommendations(matches)

            # Add general recommendations to primary pattern
            if matches and recommendations:
                # Find highest confidence match
                sorted_matches = sorted(
                    matches,
                    key=lambda m: m.confidence,
                    reverse=True
                )

                if sorted_matches:
                    # Add recommendations to highest confidence match
                    sorted_matches[0].recommendations.extend(recommendations)

        except Exception as e:
            logger.error(f"Error adding recommendations: {e}", exc_info=True)
