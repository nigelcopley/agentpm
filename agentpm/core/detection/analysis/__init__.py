"""
Static Analysis Package - Layer 3 (Detection Services)

Provides static code analysis capabilities for APM (Agent Project Manager) Detection Pack.

Architecture:
- Layer 3: Detection Services (business logic)
- Uses Layer 1 utilities (ast_utils, metrics_calculator)
- NO plugin dependencies
- Stateless service pattern

Components:
- StaticAnalysisService: Main analysis orchestrator
- FileAnalysis: Single file metrics model
- ProjectAnalysis: Aggregated project metrics model
- ComplexityReport: Complexity violation report
- MaintainabilityReport: Maintainability violation report
- AnalysisCache: File-based caching for performance

Quick Start:
    >>> from pathlib import Path
    >>> from agentpm.core.detection.analysis import StaticAnalysisService
    >>>
    >>> # Analyze entire project
    >>> service = StaticAnalysisService(Path("/my/project"))
    >>> analysis = service.analyze_project()
    >>>
    >>> # Get summary
    >>> summary = analysis.get_summary()
    >>> print(f"Quality Score: {summary['quality_score']}")
    >>>
    >>> # Find high-risk files
    >>> high_complexity = service.get_high_complexity_files(analysis, threshold=10)
    >>> for file in high_complexity:
    ...     print(f"{file.file_path}: complexity={file.complexity_max}")

Author: APM (Agent Project Manager) Detection Pack
Layer: 3 (Detection Services)
Version: 1.0.0
"""

# Import all public classes and functions
from agentpm.core.database.models.detection_analysis import (
    FileAnalysis,
    ProjectAnalysis,
    ComplexityReport,
    MaintainabilityReport,
)

from agentpm.core.detection.analysis.service import (
    StaticAnalysisService,
    AnalysisCache,
)

__all__ = [
    # Models
    "FileAnalysis",
    "ProjectAnalysis",
    "ComplexityReport",
    "MaintainabilityReport",
    # Service
    "StaticAnalysisService",
    "AnalysisCache",
]

__version__ = "1.0.0"
__author__ = "APM (Agent Project Manager) Detection Pack"
__layer__ = "3 (Detection Services)"
