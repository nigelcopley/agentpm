"""
Runtime Detection Module

Services for detecting runtime environment metadata.

Layer 3 (Detection Services)
Purpose: Capture runtime environment information to enrich static detection results

Exports:
    - RuntimeDetectorService: Main service for runtime detection
    - RuntimeOverlay: Runtime metadata model
"""

from agentpm.core.database.models.detection_runtime import RuntimeOverlay
from .service import RuntimeDetectorService

__all__ = [
    "RuntimeDetectorService",
    "RuntimeOverlay",
]
