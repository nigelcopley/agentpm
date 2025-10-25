"""
Dependency Graph Service for APM (Agent Project Manager) Detection Pack.

This service builds and analyzes project dependency graphs using NetworkX.
It follows the three-layer architecture pattern, using Layer 1 utilities
for graph construction and AST parsing.

**Architecture Layer**: Layer 3 (Detection Services)
**Dependencies**:
- Layer 1: graph_builders.py, ast_utils.py
- Layer 0: NetworkX, Pydantic models

**Features**:
- Build dependency graphs from Python imports
- Detect circular dependencies
- Calculate coupling metrics (afferent, efferent, instability)
- Export Graphviz visualizations
- Cache graphs for performance

**Performance**:
- Graph building: <1s for typical projects
- Cycle detection: <500ms
- Cached operations: <50ms

**Example Usage**:
    from pathlib import Path
    from agentpm.core.detection.graphs import DependencyGraphService

    # Create service
    service = DependencyGraphService(Path.cwd())

    # Build and analyze
    analysis = service.analyze_dependencies()

    # Check for circular dependencies
    if analysis.has_circular_dependencies:
        for cycle in analysis.circular_dependencies:
            print(f"{cycle.severity.upper()}: {' -> '.join(cycle.cycle)}")

    # Export visualization
    service.export_graphviz(Path("deps.dot"), highlight_cycles=True)

**Author**: APM (Agent Project Manager) Detection Pack Team
**Version**: 1.0.0
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx

# Layer 1 utilities (shared foundation)
from agentpm.utils.ast_utils import parse_python_ast, extract_imports
from agentpm.utils.graph_builders import (
    build_import_graph,
    detect_cycles,
    calculate_coupling_metrics,
    graph_to_dict,
    calculate_graph_metrics,
    find_root_nodes,
    find_leaf_nodes,
    get_node_depth,
)
from agentpm.utils.ignore_patterns import IgnorePatternMatcher

# Database layer models
from agentpm.core.database.models.detection_graph import (
    DependencyNode,
    CircularDependency,
    CouplingMetrics,
    DependencyGraphAnalysis,
)


class DependencyGraphService:
    """
    Service for dependency graph operations.

    Builds and analyzes project dependency graphs to detect architectural
    issues like circular dependencies and tight coupling.

    Responsibilities:
    - Build dependency graphs from project imports
    - Detect circular dependencies with severity assessment
    - Calculate coupling metrics (Ca, Ce, Instability)
    - Export graphs for visualization (Graphviz)
    - Cache graphs for performance

    Attributes:
        project_path: Project root directory
        _graph: Cached NetworkX graph (lazy-loaded)
        _imports_cache: Cached import data by file
        _cache_timestamp: When cache was last built

    Example:
        >>> from pathlib import Path
        >>> service = DependencyGraphService(Path("/project"))
        >>>
        >>> # Build graph
        >>> graph = service.build_graph()
        >>> print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        >>>
        >>> # Analyze dependencies
        >>> analysis = service.analyze_dependencies()
        >>> print(f"Circular dependencies: {len(analysis.circular_dependencies)}")
        >>>
        >>> # Get module coupling
        >>> metrics = service.get_module_coupling("src/main.py")
        >>> print(f"Instability: {metrics.instability:.2f}")
    """

    # Cache configuration
    CACHE_TTL_SECONDS = 3600  # 1 hour
    DEFAULT_FILE_PATTERN = "**/*.py"

    def __init__(self, project_path: Path):
        """
        Initialize dependency graph service.

        Args:
            project_path: Project root directory

        Raises:
            ValueError: If project_path is not a directory
        """
        if not project_path.is_dir():
            raise ValueError(f"project_path must be a directory: {project_path}")

        self.project_path = project_path.resolve()
        self._graph: Optional[nx.DiGraph] = None
        self._imports_cache: Dict[str, List[str]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self.ignore_matcher = IgnorePatternMatcher(self.project_path)

    def build_graph(
        self,
        file_pattern: str = "**/*.py",
        force_rebuild: bool = False
    ) -> nx.DiGraph:
        """
        Build dependency graph from project files.

        Scans project for Python files, extracts imports using AST parsing,
        and builds a directed graph representing import relationships.

        Steps:
        1. Find all Python files matching pattern
        2. Filter using IgnorePatternMatcher (respects .gitignore, .aipmignore, defaults)
        3. Parse each file with ast_utils.parse_python_ast()
        4. Extract imports with ast_utils.extract_imports()
        5. Build graph with graph_builders.build_import_graph()

        Args:
            file_pattern: Glob pattern for files (default: "**/*.py")
            force_rebuild: Bypass cache and rebuild graph

        Returns:
            NetworkX DiGraph with:
            - Nodes: Module paths (project-relative)
            - Edges: Import relationships (source → target)
            - Node attributes: {'file_path': str, 'import_count': int}

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> graph = service.build_graph()
            >>> print(f"Modules: {graph.number_of_nodes()}")
            >>> print(f"Dependencies: {graph.number_of_edges()}")

        Performance:
            - First run: ~500ms for 100 files
            - Cached: <50ms (if cache valid)

        Note:
            Filtering now uses IgnorePatternMatcher which respects:
            - .gitignore patterns
            - .aipmignore patterns (AIPM-specific exclusions)
            - Default patterns (venv/, node_modules/, .git/, etc.)
        """
        # Check cache validity
        if not force_rebuild and self._is_cache_valid():
            if self._graph is not None:
                return self._graph

        # Step 1: Find all Python files
        all_python_files = list(self.project_path.glob(file_pattern))

        # Step 2: Filter using IgnorePatternMatcher
        python_files = self.ignore_matcher.filter_paths(all_python_files)

        # Step 3: Extract imports from each file
        imports_by_file: Dict[str, List[str]] = {}

        for file_path in python_files:
            # Parse file to AST
            tree = parse_python_ast(file_path)
            if tree is None:
                continue  # Skip files that fail parsing

            # Extract imports
            imports = extract_imports(tree)

            # Store with project-relative path
            try:
                rel_path = str(file_path.relative_to(self.project_path))
            except ValueError:
                rel_path = str(file_path)

            imports_by_file[rel_path] = imports

        # Step 4: Build graph using Layer 1 utility
        self._graph = build_import_graph(imports_by_file, self.project_path)
        self._imports_cache = imports_by_file
        self._cache_timestamp = datetime.now()

        return self._graph

    def analyze_dependencies(
        self,
        rebuild: bool = False
    ) -> DependencyGraphAnalysis:
        """
        Complete dependency analysis.

        Performs comprehensive analysis of project dependencies including:
        - Circular dependency detection
        - Coupling metrics calculation
        - Root/leaf module identification
        - Maximum depth calculation

        Steps:
        1. Build graph (if needed or rebuild=True)
        2. Detect cycles with graph_builders.detect_cycles()
        3. Calculate coupling with graph_builders.calculate_coupling_metrics()
        4. Identify root/leaf modules
        5. Calculate max depth

        Args:
            rebuild: Force rebuild graph before analysis

        Returns:
            DependencyGraphAnalysis with complete results

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> analysis = service.analyze_dependencies()
            >>>
            >>> if analysis.has_circular_dependencies:
            ...     print("Warning: Circular dependencies detected!")
            ...     for cycle in analysis.circular_dependencies:
            ...         print(f"  {cycle.severity}: {' -> '.join(cycle.cycle)}")
            >>>
            >>> print(f"Average instability: {analysis.average_instability:.2f}")
        """
        # Build or retrieve graph
        graph = self.build_graph(force_rebuild=rebuild)

        # Calculate graph metrics
        graph_metrics = calculate_graph_metrics(graph)

        # Detect circular dependencies
        circular_deps = self.find_circular_dependencies()

        # Calculate coupling metrics
        coupling_data = calculate_coupling_metrics(graph)
        coupling_list = [
            CouplingMetrics(
                module=module,
                afferent_coupling=metrics['Ca'],
                efferent_coupling=metrics['Ce'],
                instability=metrics['I']
            )
            for module, metrics in coupling_data.items()
        ]

        # Identify root and leaf modules
        roots = find_root_nodes(graph)
        leaves = find_leaf_nodes(graph)

        # Create analysis result
        return DependencyGraphAnalysis(
            project_path=str(self.project_path),
            total_modules=graph_metrics['node_count'],
            total_dependencies=graph_metrics['edge_count'],
            circular_dependencies=circular_deps,
            coupling_metrics=coupling_list,
            root_modules=roots,
            leaf_modules=leaves,
            max_depth=graph_metrics['max_depth'],
            analyzed_at=datetime.now()
        )

    def find_circular_dependencies(self) -> List[CircularDependency]:
        """
        Find all circular dependencies with severity assessment.

        Detects cycles in dependency graph and assigns severity based on
        cycle length:
        - High: 2 modules (direct A ↔ B)
        - Medium: 3-5 modules
        - Low: >5 modules

        Returns:
            List of CircularDependency objects with suggestions

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> cycles = service.find_circular_dependencies()
            >>>
            >>> for cycle in cycles:
            ...     if cycle.severity == "high":
            ...         print(f"CRITICAL: {' -> '.join(cycle.cycle)}")
            ...         print(f"Suggestion: {cycle.suggestion}")

        Severity Assessment:
            - High (2 modules): Direct mutual dependency, easiest to fix
            - Medium (3-5): Moderate complexity, requires refactoring
            - Low (>5): Complex dependency chain, architectural redesign needed
        """
        if self._graph is None:
            self.build_graph()

        # Detect cycles using Layer 1 utility
        cycles = detect_cycles(self._graph)

        # Convert to CircularDependency models with severity
        circular_deps = []

        for cycle in cycles:
            cycle_length = len(cycle)

            # Determine severity
            if cycle_length == 2:
                severity = "high"
                suggestion = (
                    f"Extract shared functionality to a third module. "
                    f"Consider dependency inversion or interface segregation."
                )
            elif cycle_length <= 5:
                severity = "medium"
                suggestion = (
                    f"Break cycle by introducing an abstraction layer or "
                    f"event-based communication between modules."
                )
            else:
                severity = "low"
                suggestion = (
                    f"Complex dependency chain detected. Consider architectural "
                    f"refactoring to reduce coupling and improve modularity."
                )

            # Add cycle start to end for visualization clarity
            cycle_path = cycle + [cycle[0]]

            circular_deps.append(
                CircularDependency(
                    cycle=cycle_path,
                    severity=severity,
                    suggestion=suggestion
                )
            )

        # Sort by severity (high first)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        circular_deps.sort(key=lambda cd: (severity_order[cd.severity], cd.cycle_length))

        return circular_deps

    def get_module_coupling(self, module_path: str) -> CouplingMetrics:
        """
        Get coupling metrics for specific module.

        Calculates:
        - Afferent Coupling (Ca): Incoming dependencies
        - Efferent Coupling (Ce): Outgoing dependencies
        - Instability (I): Ce / (Ce + Ca)

        Args:
            module_path: Module path (project-relative or absolute)

        Returns:
            CouplingMetrics for the module

        Raises:
            ValueError: If module not found in graph

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> metrics = service.get_module_coupling("src/core/models.py")
            >>>
            >>> print(f"Afferent: {metrics.afferent_coupling}")  # How many depend on this
            >>> print(f"Efferent: {metrics.efferent_coupling}")  # How many this depends on
            >>> print(f"Instability: {metrics.instability:.2f}")  # 0.0=stable, 1.0=unstable
            >>>
            >>> if metrics.is_stable:
            ...     print("This is a stable module (good for core abstractions)")
        """
        if self._graph is None:
            self.build_graph()

        # Normalize module path
        try:
            path_obj = Path(module_path)
            if path_obj.is_absolute():
                normalized = str(path_obj.relative_to(self.project_path))
            else:
                normalized = module_path
        except (ValueError, OSError):
            normalized = module_path

        # Check if module exists in graph
        if not self._graph.has_node(normalized):
            raise ValueError(f"Module not found in graph: {module_path}")

        # Calculate coupling using Layer 1 utility
        coupling_data = calculate_coupling_metrics(self._graph)

        if normalized not in coupling_data:
            raise ValueError(f"No coupling data for module: {module_path}")

        metrics = coupling_data[normalized]

        return CouplingMetrics(
            module=normalized,
            afferent_coupling=metrics['Ca'],
            efferent_coupling=metrics['Ce'],
            instability=metrics['I']
        )

    def export_graphviz(
        self,
        output_path: Path,
        highlight_cycles: bool = True,
        include_metrics: bool = False
    ) -> str:
        """
        Export graph to Graphviz DOT format.

        Generates visualization-ready graph in DOT format for rendering
        with Graphviz tools (dot, neato, etc.).

        Steps:
        1. Convert NetworkX graph to DOT format
        2. Optionally highlight circular dependencies (red edges)
        3. Optionally annotate nodes with coupling metrics
        4. Write to file

        Args:
            output_path: Output file path (typically .dot extension)
            highlight_cycles: Color circular dependency edges red
            include_metrics: Add coupling metrics to node labels

        Returns:
            DOT format string (also written to file)

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> service.export_graphviz(
            ...     Path("dependencies.dot"),
            ...     highlight_cycles=True,
            ...     include_metrics=True
            ... )
            >>>
            >>> # Render with Graphviz
            >>> # $ dot -Tpng dependencies.dot -o dependencies.png

        DOT Output Format:
            digraph {
                "src/main.py" [label="main.py\\nI=0.75"];
                "src/utils.py" [label="utils.py\\nI=0.25"];
                "src/main.py" -> "src/utils.py";
                "src/utils.py" -> "src/main.py" [color=red];  # Cycle
            }
        """
        if self._graph is None:
            self.build_graph()

        # Start DOT output
        lines = ["digraph dependencies {"]
        lines.append("    rankdir=LR;")  # Left to right layout
        lines.append("    node [shape=box, style=rounded];")
        lines.append("")

        # Get cycle edges if highlighting
        cycle_edges = set()
        if highlight_cycles:
            cycles = detect_cycles(self._graph)
            for cycle in cycles:
                for i in range(len(cycle)):
                    source = cycle[i]
                    target = cycle[(i + 1) % len(cycle)]
                    cycle_edges.add((source, target))

        # Get coupling metrics if including
        coupling_data = {}
        if include_metrics:
            coupling_data = calculate_coupling_metrics(self._graph)

        # Add nodes with labels
        for node in self._graph.nodes():
            label = self._format_node_label(node)

            if include_metrics and node in coupling_data:
                metrics = coupling_data[node]
                label = f"{label}\\nI={metrics['I']:.2f}"

            lines.append(f'    "{node}" [label="{label}"];')

        lines.append("")

        # Add edges
        for source, target in self._graph.edges():
            if (source, target) in cycle_edges:
                # Highlight cycle edges
                lines.append(f'    "{source}" -> "{target}" [color=red, penwidth=2.0];')
            else:
                lines.append(f'    "{source}" -> "{target}";')

        lines.append("}")

        # Join lines
        dot_content = "\n".join(lines)

        # Write to file
        output_path.write_text(dot_content, encoding='utf-8')

        return dot_content

    def get_module_dependencies(
        self,
        module_path: str,
        depth: int = 1
    ) -> Dict[str, List[str]]:
        """
        Get dependencies for specific module.

        Returns imports and importers for a module up to specified depth.

        Args:
            module_path: Module to analyze
            depth: How many levels deep (1 = direct only, 2 = transitive, etc.)

        Returns:
            Dictionary with keys:
            - 'imports': Modules this imports (outgoing)
            - 'imported_by': Modules that import this (incoming)

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> deps = service.get_module_dependencies("src/main.py", depth=1)
            >>>
            >>> print("Direct imports:")
            >>> for imp in deps['imports']:
            ...     print(f"  - {imp}")
            >>>
            >>> print("Imported by:")
            >>> for imp in deps['imported_by']:
            ...     print(f"  - {imp}")

        Depth Behavior:
            - depth=1: Direct dependencies only
            - depth=2: Direct + one level transitive
            - depth=-1: All reachable nodes (full transitive closure)
        """
        if self._graph is None:
            self.build_graph()

        # Normalize module path
        try:
            path_obj = Path(module_path)
            if path_obj.is_absolute():
                normalized = str(path_obj.relative_to(self.project_path))
            else:
                normalized = module_path
        except (ValueError, OSError):
            normalized = module_path

        if not self._graph.has_node(normalized):
            raise ValueError(f"Module not found: {module_path}")

        # Get imports (outgoing edges)
        imports = self._get_reachable_nodes(
            self._graph,
            normalized,
            depth,
            direction='out'
        )

        # Get imported_by (incoming edges)
        imported_by = self._get_reachable_nodes(
            self._graph,
            normalized,
            depth,
            direction='in'
        )

        return {
            'imports': sorted(imports),
            'imported_by': sorted(imported_by)
        }

    # Private helper methods

    def _is_cache_valid(self) -> bool:
        """Check if cached graph is still valid."""
        if self._cache_timestamp is None:
            return False

        age = datetime.now() - self._cache_timestamp
        return age < timedelta(seconds=self.CACHE_TTL_SECONDS)

    def _format_node_label(self, node_path: str) -> str:
        """Format node label for visualization (shorten long paths)."""
        # Use just filename for clarity
        return Path(node_path).name

    def _get_reachable_nodes(
        self,
        graph: nx.DiGraph,
        start_node: str,
        depth: int,
        direction: str = 'out'
    ) -> List[str]:
        """
        Get reachable nodes from start_node up to specified depth.

        Args:
            graph: NetworkX graph
            start_node: Starting node
            depth: Maximum depth (-1 for unlimited)
            direction: 'out' for successors, 'in' for predecessors

        Returns:
            List of reachable node names
        """
        if depth == 0:
            return []

        reachable = set()
        current_level = {start_node}
        visited = {start_node}

        current_depth = 0

        while current_level and (depth == -1 or current_depth < depth):
            next_level = set()

            for node in current_level:
                # Get neighbors based on direction
                if direction == 'out':
                    neighbors = set(graph.successors(node))
                else:  # 'in'
                    neighbors = set(graph.predecessors(node))

                # Add new neighbors
                new_neighbors = neighbors - visited
                reachable.update(new_neighbors)
                next_level.update(new_neighbors)
                visited.update(new_neighbors)

            current_level = next_level
            current_depth += 1

        return list(reachable)

    def clear_cache(self) -> None:
        """Clear cached graph and force rebuild on next access."""
        self._graph = None
        self._imports_cache = {}
        self._cache_timestamp = None

    def get_graph_summary(self) -> Dict[str, any]:
        """
        Get summary statistics for current graph.

        Returns:
            Dictionary with graph metrics:
            - node_count, edge_count
            - avg_degree, max_depth
            - has_cycles, cycle_count

        Example:
            >>> service = DependencyGraphService(Path.cwd())
            >>> summary = service.get_graph_summary()
            >>> print(f"Modules: {summary['node_count']}")
            >>> print(f"Dependencies: {summary['edge_count']}")
            >>> print(f"Has cycles: {summary['has_cycles']}")
        """
        if self._graph is None:
            self.build_graph()

        metrics = calculate_graph_metrics(self._graph)
        cycles = detect_cycles(self._graph)

        return {
            'node_count': metrics['node_count'],
            'edge_count': metrics['edge_count'],
            'avg_degree': metrics['avg_degree'],
            'max_depth': metrics['max_depth'],
            'has_cycles': metrics['cyclic'],
            'cycle_count': len(cycles),
            'density': metrics['density'],
        }
