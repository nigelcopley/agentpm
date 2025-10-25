#!/usr/bin/env python3
"""
Test max depth on acyclic version of graph (breaking the cycle).

This verifies that max_depth calculation works correctly when there are no cycles.
"""

import sys
from pathlib import Path
import networkx as nx

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agentpm.core.detection.graphs import DependencyGraphService


def test_acyclic_depth():
    """Test max depth by temporarily removing cycle edges."""

    print("=" * 80)
    print("  Acyclic Depth Test (Breaking Cycles)")
    print("=" * 80)

    project_path = Path.cwd()
    service = DependencyGraphService(project_path)
    graph = service.build_graph(force_rebuild=True)

    print(f"\nOriginal graph:")
    print(f"  Total nodes: {graph.number_of_nodes()}")
    print(f"  Total edges: {graph.number_of_edges()}")
    print(f"  Is DAG: {nx.is_directed_acyclic_graph(graph)}")

    # Detect cycles
    if not nx.is_directed_acyclic_graph(graph):
        cycles = list(nx.simple_cycles(graph))
        print(f"\n⚠️  Found {len(cycles)} cycles")

        # Show all cycles
        for i, cycle in enumerate(cycles[:5]):
            print(f"\n  Cycle {i+1} ({len(cycle)} nodes):")
            for node in cycle:
                print(f"    - {node}")

        # Create a copy and break cycles
        acyclic_graph = graph.copy()

        # Remove one edge from each cycle to break it
        edges_to_remove = []
        for cycle in cycles:
            # Remove last edge in cycle (cycle[-1] → cycle[0])
            edge = (cycle[-1], cycle[0])
            if acyclic_graph.has_edge(*edge):
                edges_to_remove.append(edge)

        print(f"\n🔧 Breaking cycles by removing {len(edges_to_remove)} edges:")
        for source, target in edges_to_remove:
            print(f"  - {source} → {target}")
            acyclic_graph.remove_edge(source, target)

        # Verify it's now acyclic
        is_dag = nx.is_directed_acyclic_graph(acyclic_graph)
        print(f"\n📊 Acyclic graph:")
        print(f"  Total nodes: {acyclic_graph.number_of_nodes()}")
        print(f"  Total edges: {acyclic_graph.number_of_edges()}")
        print(f"  Is DAG: {is_dag}")

        if is_dag:
            # Calculate max depth
            try:
                max_depth = nx.dag_longest_path_length(acyclic_graph)
                longest_path = nx.dag_longest_path(acyclic_graph)

                print(f"\n✅ Max depth (after breaking cycles): {max_depth}")
                print(f"\n📏 Longest path ({len(longest_path)} nodes):")

                # Show full path if reasonable length
                if len(longest_path) <= 15:
                    for i, node in enumerate(longest_path):
                        print(f"  {i}: {node}")
                else:
                    # Show first 10 and last 5
                    for i, node in enumerate(longest_path[:10]):
                        print(f"  {i}: {node}")
                    print(f"  ... ({len(longest_path) - 15} more nodes)")
                    for i, node in enumerate(longest_path[-5:], len(longest_path) - 5):
                        print(f"  {i}: {node}")

                # Show depth expectations
                print(f"\n📋 Depth Analysis:")
                if max_depth >= 5:
                    print(f"  ✅ EXPECTED: Max depth {max_depth} is in realistic range (5-8+)")
                else:
                    print(f"  ⚠️  UNEXPECTED: Max depth {max_depth} seems low for project this size")

                return True

            except Exception as e:
                print(f"\n❌ Error calculating depth: {e}")
                return False
        else:
            print(f"\n❌ Failed to make graph acyclic")
            return False

    else:
        # Graph is already acyclic
        print(f"\n✅ Graph is already acyclic")
        max_depth = nx.dag_longest_path_length(graph)
        print(f"  Max depth: {max_depth}")
        return True


if __name__ == '__main__':
    try:
        success = test_acyclic_depth()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
