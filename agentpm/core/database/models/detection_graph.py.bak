"""
Pydantic models for Dependency Graph Analysis.

This module defines the data models for dependency graph analysis results.
All models are immutable and validate data at construction time.

**Architecture Layer**: Database Layer (Models)
**Dependencies**: Pydantic only (no plugin or service dependencies)

**Models**:
- DependencyNode: Single node in dependency graph
- CircularDependency: Detected circular dependency with severity
- CouplingMetrics: Coupling metrics for a module
- DependencyGraphAnalysis: Complete analysis results

**Author**: APM (Agent Project Manager) Detection Pack Team
**Version**: 1.0.0
**Moved**: From core/detection/graphs/models.py to database layer (2025-10-24)
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class DependencyNode(BaseModel):
    """
    Single node in dependency graph.

    Represents a module with its import/export relationships.

    Attributes:
        module_path: Project-relative path to module
        imports: Modules imported by this module
        imported_by: Modules that import this module
        depth: Distance from root nodes (0 for roots, -1 if cyclic)

    Example:
        >>> node = DependencyNode(
        ...     module_path="src/main.py",
        ...     imports=["src.utils", "src.models"],
        ...     imported_by=[],
        ...     depth=0
        ... )
        >>> node.imports
        ['src.utils', 'src.models']
    """

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Allow depth updates
    )

    module_path: str = Field(..., min_length=1, description="Project-relative module path")
    imports: List[str] = Field(
        default_factory=list,
        description="Modules imported by this module"
    )
    imported_by: List[str] = Field(
        default_factory=list,
        description="Modules that import this module"
    )
    depth: int = Field(
        default=0,
        ge=-1,
        description="Distance from root nodes (0=root, -1=cyclic/unreachable)"
    )


class CircularDependency(BaseModel):
    """
    Detected circular dependency in module graph.

    Circular dependencies indicate design problems and can cause:
    - Import errors
    - Initialization order issues
    - Tight coupling

    Attributes:
        cycle: List of module paths forming circular dependency
        severity: 'high' (2 modules), 'medium' (3-5), 'low' (>5)
        suggestion: Recommendation for breaking the cycle

    Example:
        >>> cycle_dep = CircularDependency(
        ...     cycle=["src/foo.py", "src/bar.py", "src/foo.py"],
        ...     severity="high",
        ...     suggestion="Extract common code to shared module"
        ... )
        >>> cycle_dep.severity
        'high'
    """

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,  # Immutable after creation
    )

    cycle: List[str] = Field(
        ...,
        min_length=2,
        description="Module paths forming circular dependency"
    )
    severity: str = Field(
        ...,
        pattern="^(high|medium|low)$",
        description="Severity level based on cycle length"
    )
    suggestion: str = Field(
        ...,
        min_length=10,
        description="Recommendation for breaking cycle"
    )

    @property
    def cycle_length(self) -> int:
        """Number of modules in cycle."""
        return len(self.cycle)


class CouplingMetrics(BaseModel):
    """
    Coupling metrics for a module.

    Measures module stability and coupling using standard software metrics:
    - Afferent Coupling (Ca): Incoming dependencies (how many depend on this)
    - Efferent Coupling (Ce): Outgoing dependencies (how many this depends on)
    - Instability (I): Ce / (Ce + Ca), range [0.0, 1.0]

    Attributes:
        module: Module path
        afferent_coupling: Incoming dependencies count
        efferent_coupling: Outgoing dependencies count
        instability: Instability metric (0.0=stable, 1.0=unstable)

    Interpretation:
        - I=0.0: Maximally stable (library, framework)
        - I=1.0: Maximally unstable (application entry point)
        - I=0.5: Balanced coupling

    Example:
        >>> metrics = CouplingMetrics(
        ...     module="src/core.py",
        ...     afferent_coupling=10,
        ...     efferent_coupling=2,
        ...     instability=0.167
        ... )
        >>> metrics.instability < 0.5  # Stable module
        True
    """

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,
    )

    module: str = Field(..., min_length=1, description="Module path")
    afferent_coupling: int = Field(..., ge=0, description="Incoming dependencies (Ca)")
    efferent_coupling: int = Field(..., ge=0, description="Outgoing dependencies (Ce)")
    instability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Instability metric (0.0=stable, 1.0=unstable)"
    )

    @property
    def is_stable(self) -> bool:
        """True if instability < 0.5 (more incoming than outgoing dependencies)."""
        return self.instability < 0.5

    @property
    def is_unstable(self) -> bool:
        """True if instability > 0.5 (more outgoing than incoming dependencies)."""
        return self.instability > 0.5


class DependencyGraphAnalysis(BaseModel):
    """
    Complete dependency graph analysis results.

    Provides comprehensive analysis of project dependencies including:
    - Graph structure (nodes, edges)
    - Circular dependencies
    - Coupling metrics
    - Root/leaf module identification

    Attributes:
        project_path: Project root directory
        total_modules: Total number of modules analyzed
        total_dependencies: Total number of import relationships
        circular_dependencies: List of detected cycles
        coupling_metrics: Coupling metrics for each module
        root_modules: Modules with no incoming dependencies
        leaf_modules: Modules with no outgoing dependencies
        max_depth: Maximum dependency depth (longest path from root)
        analyzed_at: Timestamp of analysis

    Example:
        >>> analysis = DependencyGraphAnalysis(
        ...     project_path="/project",
        ...     total_modules=50,
        ...     total_dependencies=120,
        ...     circular_dependencies=[],
        ...     coupling_metrics=[],
        ...     root_modules=["main.py"],
        ...     leaf_modules=["utils.py"],
        ...     max_depth=5
        ... )
        >>> analysis.has_circular_dependencies
        False
    """

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Allow updates during analysis
    )

    project_path: str = Field(..., min_length=1, description="Project root directory")
    total_modules: int = Field(..., ge=0, description="Total modules analyzed")
    total_dependencies: int = Field(..., ge=0, description="Total import relationships")
    circular_dependencies: List[CircularDependency] = Field(
        default_factory=list,
        description="Detected circular dependencies"
    )
    coupling_metrics: List[CouplingMetrics] = Field(
        default_factory=list,
        description="Coupling metrics per module"
    )
    root_modules: List[str] = Field(
        default_factory=list,
        description="Modules with no incoming dependencies"
    )
    leaf_modules: List[str] = Field(
        default_factory=list,
        description="Modules with no outgoing dependencies"
    )
    max_depth: int = Field(
        default=0,
        ge=-1,
        description="Maximum dependency depth (-1 if cyclic)"
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.now,
        description="Analysis timestamp"
    )

    @property
    def has_circular_dependencies(self) -> bool:
        """True if circular dependencies detected."""
        return len(self.circular_dependencies) > 0

    @property
    def high_severity_cycles(self) -> List[CircularDependency]:
        """Return only high-severity circular dependencies."""
        return [cd for cd in self.circular_dependencies if cd.severity == "high"]

    @property
    def average_instability(self) -> float:
        """Calculate average instability across all modules."""
        if not self.coupling_metrics:
            return 0.0
        return sum(m.instability for m in self.coupling_metrics) / len(self.coupling_metrics)
