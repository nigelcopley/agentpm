"""
Pattern Recognition Module - Layer 3 (Detection Services)

Provides architecture pattern detection services using Layer 1 utilities.

**Architecture Compliance**:
- Layer 3: Detection Services
- Uses Layer 1 utilities (pattern_matchers)
- No direct dependency on Layer 2 plugins

**Components**:
- PatternRecognitionService: Main pattern detection service
- PatternAnalysis: Analysis results model
- PatternMatch: Individual pattern match model
- ArchitecturePattern: Enum of recognized patterns

**Usage Example**:

    from agentpm.core.detection.patterns import PatternRecognitionService
    from pathlib import Path

    service = PatternRecognitionService(Path('/project'))
    analysis = service.analyze_patterns(confidence_threshold=0.6)

    print(f"Primary pattern: {analysis.primary_pattern}")
    print(f"Confidence: {analysis.matches[0].confidence:.0%}")

    for match in analysis.get_high_confidence_patterns():
        print(f"- {match.pattern}: {match.confidence:.0%}")
        for evidence in match.evidence:
            print(f"  * {evidence}")

**Performance**:
- Pattern detection: <200ms per project
- All patterns: <1s total
- Cached results: <50ms
"""

from agentpm.core.database.models.detection_pattern import (
    PatternMatch,
    PatternAnalysis,
)
from agentpm.core.database.enums.detection import (
    ArchitecturePattern,
)
from agentpm.core.detection.patterns.service import PatternRecognitionService

__all__ = [
    'ArchitecturePattern',
    'PatternMatch',
    'PatternAnalysis',
    'PatternRecognitionService',
]
