"""
Dependency Graph Services for APM (Agent Project Manager) Detection Pack.

This package provides dependency graph construction and analysis capabilities
for detecting circular dependencies, calculating coupling metrics, and
visualizing project dependencies.

**Architecture Layer**: Layer 3 (Detection Services)
- Uses Layer 1 utilities (graph_builders.py, ast_utils.py)
- Provides high-level graph analysis services
- Exports Pydantic models for type safety

**Key Components**:
- DependencyGraphService: Build and analyze dependency graphs
- Models: Pydantic models for graph data (DependencyNode, CircularDependency, etc.)

**Usage Example**:
    from agentpm.core.detection.graphs import DependencyGraphService
    from pathlib import Path

    service = DependencyGraphService(Path.cwd())
    analysis = service.analyze_dependencies()

    if analysis.circular_dependencies:
        print(f"Found {len(analysis.circular_dependencies)} circular dependencies!")

    for metric in analysis.coupling_metrics:
        print(f"{metric.module}: instability={metric.instability:.2f}")

**Author**: APM (Agent Project Manager) Detection Pack Team
**Version**: 1.0.0
"""

from agentpm.core.database.models.detection_graph import (
    DependencyNode,
    CircularDependency,
    CouplingMetrics,
    DependencyGraphAnalysis,
)
from .service import DependencyGraphService

__all__ = [
    'DependencyGraphService',
    'DependencyNode',
    'CircularDependency',
    'CouplingMetrics',
    'DependencyGraphAnalysis',
]
