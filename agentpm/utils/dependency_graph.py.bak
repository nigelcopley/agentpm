"""
Dependency Graph - Generic dependency relationship modeling

Universal graph structure for modeling dependencies:
- Technology dependencies (Django → Python)
- Task dependencies (Task 2 → Task 1)
- Work item relationships
- Agent interactions

Pattern: Adjacency list with cycle detection and traversal methods
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class DependencyEdge:
    """
    Edge in dependency graph representing a relationship.

    Attributes:
        parent: Parent node (what is depended upon)
        child: Child node (what depends on parent)
        relationship_type: Type of dependency (HARD, SOFT, etc.)
        metadata: Additional edge data (boost values, reasons, etc.)
    """
    parent: str
    child: str
    relationship_type: str
    metadata: Dict[str, Any]


class DependencyGraph:
    """
    Generic directed acyclic graph (DAG) for dependency modeling.

    Supports:
    - Adding dependencies with metadata
    - Cycle detection (prevent circular dependencies)
    - Graph traversal (ancestors, descendants, paths)
    - Topological sorting
    - Text-based visualization

    Thread-safe: No (designed for single-threaded use)

    Example:
        graph = DependencyGraph()
        graph.add_dependency('django', 'python', 'HARD', {'boost': 'match'})
        graph.add_dependency('pytest', 'python', 'SOFT', {'boost': 0.10})

        ancestors = graph.get_ancestors('python')  # ['django', 'pytest']
        has_cycle = graph.has_cycle()  # False
        tree = graph.visualize('python')  # Text tree diagram
    """

    def __init__(self):
        """Initialize empty dependency graph."""
        # Adjacency lists: node → list of edges
        self._outgoing: Dict[str, List[DependencyEdge]] = defaultdict(list)  # child → [parents]
        self._incoming: Dict[str, List[DependencyEdge]] = defaultdict(list)  # parent → [children]
        self._nodes: Set[str] = set()

    def add_dependency(
        self,
        child: str,
        parent: str,
        relationship_type: str = 'HARD',
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add dependency: child depends on parent.

        Args:
            child: Child node (depends on parent)
            parent: Parent node (depended upon)
            relationship_type: Type of dependency (HARD, SOFT, etc.)
            metadata: Additional data (boost values, reasons, etc.)

        Returns:
            True if added, False if would create cycle

        Example:
            graph.add_dependency('django', 'python', 'HARD', {'boost': 'match'})
            # Django depends on Python (hard requirement)
        """
        if metadata is None:
            metadata = {}

        # Create edge
        edge = DependencyEdge(
            parent=parent,
            child=child,
            relationship_type=relationship_type,
            metadata=metadata
        )

        # Check for cycles before adding (DAG requirement)
        if self._would_create_cycle(child, parent):
            return False

        # Add edge
        self._outgoing[child].append(edge)
        self._incoming[parent].append(edge)
        self._nodes.add(child)
        self._nodes.add(parent)

        return True

    def get_dependencies(self, node: str) -> List[DependencyEdge]:
        """
        Get all direct dependencies (parents) of a node.

        Args:
            node: Node to get dependencies for

        Returns:
            List of edges where this node is the child

        Example:
            edges = graph.get_dependencies('django')
            # Returns: [DependencyEdge(parent='python', child='django', ...)]
        """
        return self._outgoing.get(node, [])

    def get_dependents(self, node: str) -> List[DependencyEdge]:
        """
        Get all direct dependents (children) of a node.

        Args:
            node: Node to get dependents for

        Returns:
            List of edges where this node is the parent

        Example:
            edges = graph.get_dependents('python')
            # Returns: [DependencyEdge(parent='python', child='django', ...),
            #           DependencyEdge(parent='python', child='flask', ...)]
        """
        return self._incoming.get(node, [])

    def get_ancestors(self, node: str) -> List[str]:
        """
        Get all ancestors (transitive dependencies) of a node.

        Uses BFS to find all nodes this node depends on (directly or indirectly).

        Args:
            node: Node to get ancestors for

        Returns:
            List of ancestor nodes (may include duplicates if multiple paths)

        Example:
            ancestors = graph.get_ancestors('django')
            # Returns: ['python'] (Django depends on Python)
        """
        visited = set()
        queue = deque([node])
        ancestors = []

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for edge in self.get_dependencies(current):
                if edge.parent not in visited:
                    ancestors.append(edge.parent)
                    queue.append(edge.parent)

        return ancestors

    def get_descendants(self, node: str) -> List[str]:
        """
        Get all descendants (transitive dependents) of a node.

        Uses BFS to find all nodes that depend on this node (directly or indirectly).

        Args:
            node: Node to get descendants for

        Returns:
            List of descendant nodes

        Example:
            descendants = graph.get_descendants('python')
            # Returns: ['django', 'flask', 'fastapi', 'pytest']
        """
        visited = set()
        queue = deque([node])
        descendants = []

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for edge in self.get_dependents(current):
                if edge.child not in visited:
                    descendants.append(edge.child)
                    queue.append(edge.child)

        return descendants

    def has_cycle(self) -> bool:
        """
        Check if graph contains any cycles.

        Uses DFS-based cycle detection (white/gray/black coloring).

        Returns:
            True if cycle exists, False if DAG (directed acyclic graph)
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self._nodes}

        def dfs(node: str) -> bool:
            """DFS with cycle detection."""
            color[node] = GRAY

            for edge in self.get_dependencies(node):
                if color[edge.parent] == GRAY:
                    return True  # Back edge = cycle
                if color[edge.parent] == WHITE:
                    if dfs(edge.parent):
                        return True

            color[node] = BLACK
            return False

        for node in self._nodes:
            if color[node] == WHITE:
                if dfs(node):
                    return True

        return False

    def get_topological_order(self) -> List[str]:
        """
        Get topological ordering of nodes (dependencies before dependents).

        Returns:
            List of nodes in topological order (empty if cycle exists)

        Example:
            order = graph.get_topological_order()
            # Returns: ['python', 'django', 'flask', 'pytest']
            # (Python first, then frameworks that depend on it)
        """
        if self.has_cycle():
            return []  # Cannot sort cyclic graph

        in_degree = {node: 0 for node in self._nodes}

        # Calculate in-degrees (number of edges pointing TO each node)
        for node in self._nodes:
            in_degree[node] = len(self.get_dependencies(node))

        # Kahn's algorithm - start with nodes that have no dependencies
        queue = deque([node for node in self._nodes if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # For each dependent of this node
            for edge in self.get_dependents(node):
                in_degree[edge.child] -= 1
                if in_degree[edge.child] == 0:
                    queue.append(edge.child)

        return result if len(result) == len(self._nodes) else []

    def visualize(self, root_node: Optional[str] = None, max_depth: int = 5) -> str:
        """
        Generate text-based tree visualization of dependencies.

        Args:
            root_node: Starting node (if None, shows all roots)
            max_depth: Maximum depth to display

        Returns:
            Text tree diagram

        Example:
            print(graph.visualize('python'))

            Output:
            python (100%)
            ├── django (100%) [HARD: match]
            ├── flask (95%) [HARD: match]
            ├── click (85%) [HARD: match]
            └── pytest (70%) [SOFT: +7%]
        """
        lines = []

        def traverse(node: str, prefix: str = "", depth: int = 0):
            """Recursive tree traversal."""
            if depth > max_depth:
                return

            # Get dependents (children that depend on this node)
            dependents = self.get_dependents(node)

            for i, edge in enumerate(dependents):
                is_last = (i == len(dependents) - 1)
                connector = "└── " if is_last else "├── "
                child_prefix = "    " if is_last else "│   "

                # Format edge metadata
                meta_str = f"[{edge.relationship_type}"
                if 'boost' in edge.metadata:
                    boost = edge.metadata['boost']
                    if boost == 'match':
                        meta_str += ": match"
                    else:
                        meta_str += f": +{boost:.0%}"
                meta_str += "]"

                lines.append(f"{prefix}{connector}{edge.child} {meta_str}")
                traverse(edge.child, prefix + child_prefix, depth + 1)

        if root_node:
            # Visualize from specific root
            lines.append(root_node)
            traverse(root_node)
        else:
            # Find all root nodes (nodes with no dependencies)
            roots = [node for node in self._nodes if not self.get_dependencies(node)]
            for root in sorted(roots):
                lines.append(root)
                traverse(root)
                lines.append("")  # Blank line between trees

        return "\n".join(lines)

    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics for monitoring/debugging.

        Returns:
            Dictionary with graph metrics
        """
        return {
            'node_count': len(self._nodes),
            'edge_count': sum(len(edges) for edges in self._outgoing.values()),
            'has_cycle': self.has_cycle(),
            'root_nodes': [node for node in self._nodes if not self.get_dependencies(node)],
            'leaf_nodes': [node for node in self._nodes if not self.get_dependents(node)],
        }

    def _would_create_cycle(self, child: str, parent: str) -> bool:
        """
        Check if adding edge (child → parent) would create a cycle.

        Uses DFS from parent to see if we can reach child.
        If yes, adding child → parent would create cycle.

        Args:
            child: Proposed child node
            parent: Proposed parent node

        Returns:
            True if would create cycle, False if safe to add
        """
        if parent not in self._nodes:
            return False  # New node, no cycle possible

        # Can we reach child from parent? (would be a back edge)
        visited = set()
        stack = [parent]

        while stack:
            current = stack.pop()
            if current == child:
                return True  # Found path parent → ... → child, so child → parent creates cycle

            if current in visited:
                continue
            visited.add(current)

            # Follow outgoing edges (dependencies)
            for edge in self.get_dependencies(current):
                if edge.parent not in visited:
                    stack.append(edge.parent)

        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Export graph to dictionary format for serialization.

        Returns:
            Dictionary with nodes and edges
        """
        return {
            'nodes': list(self._nodes),
            'edges': [
                {
                    'child': edge.child,
                    'parent': edge.parent,
                    'type': edge.relationship_type,
                    'metadata': edge.metadata
                }
                for edges in self._outgoing.values()
                for edge in edges
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DependencyGraph':
        """
        Load graph from dictionary format.

        Args:
            data: Dictionary with nodes and edges

        Returns:
            Reconstructed DependencyGraph
        """
        graph = cls()
        for edge_data in data.get('edges', []):
            graph.add_dependency(
                child=edge_data['child'],
                parent=edge_data['parent'],
                relationship_type=edge_data['type'],
                metadata=edge_data.get('metadata', {})
            )
        return graph
