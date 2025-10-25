"""
Detection Module

Universal technology detection system.

Provides fast detection of all technologies without loading plugins.

Usage:
    from agentpm.core.detection import DetectionService, DetectionResult

    service = DetectionService()
    result = service.detect_all(Path("/path/to/project"))

    print(f"Primary language: {result.get_primary_language()}")
    print(f"Detected: {result.get_detected_technologies()}")
"""

from .models import DetectionResult, TechnologyMatch, EvidenceType
from .indicators import ProjectIndicators
# DetectionService will be exported after refactoring to use Pydantic models

from .indicator_service import IndicatorService
from .orchestrator import DetectionOrchestrator

__all__ = [
    "DetectionResult",
    "TechnologyMatch",
    "EvidenceType",
    "ProjectIndicators",
    "IndicatorService",
    "DetectionOrchestrator",
]