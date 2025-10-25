#!/usr/bin/env python3
"""
Investigation script for dependency graph depth issue.

Tests:
1. Verify NetworkX dag_longest_path_length() calculation
2. Manually trace dependency chains
3. Analyze root vs internal module structure
4. Test core-only subgraph depth
"""

import sys
from pathlib import Path
import networkx as nx

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agentpm.core.detection.graphs import DependencyGraphService
from agentpm.utils.graph_builders import find_root_nodes, find_leaf_nodes


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def investigate_depth():
    """Main investigation function."""

    print_section("1. Build Dependency Graph")

    project_path = Path.cwd()
    service = DependencyGraphService(project_path)
    graph = service.build_graph(force_rebuild=True)

    print(f"Project: {project_path}")
    print(f"Total nodes: {graph.number_of_nodes()}")
    print(f"Total edges: {graph.number_of_edges()}")

    # Check if graph is DAG
    is_dag = nx.is_directed_acyclic_graph(graph)
    print(f"Is DAG: {is_dag}")

    if not is_dag:
        print("⚠️  Graph has cycles - cannot calculate DAG longest path")
        cycles = list(nx.simple_cycles(graph))
        print(f"Number of cycles: {len(cycles)}")
        if cycles:
            print(f"Sample cycle: {cycles[0]}")
        return

    print_section("2. NetworkX Longest Path Calculation")

    # Calculate longest path manually
    try:
        longest_path = nx.dag_longest_path(graph)
        longest_path_length = len(longest_path) - 1 if longest_path else 0

        print(f"dag_longest_path_length(): {nx.dag_longest_path_length(graph)}")
        print(f"Manual calculation (len(path) - 1): {longest_path_length}")
        print(f"\nLongest path ({len(longest_path)} nodes):")

        for i, node in enumerate(longest_path[:10]):  # Show first 10
            print(f"  {i}: {node}")

        if len(longest_path) > 10:
            print(f"  ... ({len(longest_path) - 10} more nodes)")

    except Exception as e:
        print(f"❌ Error calculating longest path: {e}")
        return

    print_section("3. Manual Dependency Chain Traces")

    # Sample some interesting modules to trace (using module format: dots, no .py)
    test_modules = [
        'agentpm.cli.commands.work_item.create',
        'agentpm.core.workflow.service',
        'agentpm.core.database.service',
        'agentpm.web.app',
    ]

    for module in test_modules:
        if not graph.has_node(module):
            print(f"\n❌ Module not found: {module}")
            continue

        print(f"\n📦 {module}")

        # Get all successors (transitive dependencies)
        try:
            descendants = nx.descendants(graph, module)
            print(f"  Total transitive dependencies: {len(descendants)}")

            # Find longest path from this module
            subgraph = graph.subgraph([module] + list(descendants))
            if nx.is_directed_acyclic_graph(subgraph):
                try:
                    local_longest = nx.dag_longest_path(subgraph)
                    print(f"  Longest chain from this module: {len(local_longest) - 1} hops")

                    if len(local_longest) <= 6:
                        print(f"  Chain:")
                        for i, node in enumerate(local_longest):
                            print(f"    {i}: {node}")
                    else:
                        print(f"  Chain (first 5 + last):")
                        for i, node in enumerate(local_longest[:5]):
                            print(f"    {i}: {node}")
                        print(f"    ...")
                        print(f"    {len(local_longest)-1}: {local_longest[-1]}")

                except Exception as e:
                    print(f"  ⚠️  Could not calculate: {e}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print_section("4. Root vs Internal Module Analysis")

    roots = find_root_nodes(graph)
    leaves = find_leaf_nodes(graph)

    internal_nodes = [n for n in graph.nodes() if n not in roots and n not in leaves]

    print(f"Root modules (no incoming deps): {len(roots)}")
    print(f"Leaf modules (no outgoing deps): {len(leaves)}")
    print(f"Internal modules: {len(internal_nodes)}")
    print(f"Root percentage: {len(roots) / graph.number_of_nodes() * 100:.1f}%")

    # Sample some roots
    print(f"\nSample root modules (first 10):")
    for root in sorted(roots)[:10]:
        out_degree = graph.out_degree(root)
        print(f"  - {root} (→ {out_degree} deps)")

    print_section("5. Core-Only Subgraph Analysis")

    # Filter to only core modules (using dot notation)
    core_modules = [n for n in graph.nodes() if 'agentpm.core.' in str(n)]
    print(f"Core modules: {len(core_modules)}")

    if core_modules:
        core_graph = graph.subgraph(core_modules)
        print(f"Core edges: {core_graph.number_of_edges()}")

        is_core_dag = nx.is_directed_acyclic_graph(core_graph)
        print(f"Core is DAG: {is_core_dag}")

        if is_core_dag:
            try:
                core_depth = nx.dag_longest_path_length(core_graph)
                core_longest = nx.dag_longest_path(core_graph)

                print(f"Core max depth: {core_depth}")
                print(f"\nCore longest path ({len(core_longest)} nodes):")
                for i, node in enumerate(core_longest[:10]):
                    print(f"  {i}: {node}")

            except Exception as e:
                print(f"❌ Error: {e}")

    print_section("6. External Module Impact Analysis")

    internal_modules = [n for n in graph.nodes() if str(n).startswith('agentpm.')]
    external_modules = [n for n in graph.nodes() if not str(n).startswith('agentpm.')]

    print(f"Internal modules: {len(internal_modules)}")
    print(f"External modules: {len(external_modules)}")
    print(f"External percentage: {len(external_modules) / graph.number_of_nodes() * 100:.1f}%")

    # Check if external modules break chains
    print(f"\nSample external modules (first 10):")
    for ext in sorted(external_modules)[:10]:
        in_deg = graph.in_degree(ext)
        out_deg = graph.out_degree(ext)
        print(f"  - {ext} (← {in_deg}, → {out_deg})")

    # Test depth with internal-only graph
    if internal_modules:
        internal_graph = graph.subgraph(internal_modules)
        print(f"\nInternal-only graph:")
        print(f"  Nodes: {internal_graph.number_of_nodes()}")
        print(f"  Edges: {internal_graph.number_of_edges()}")

        is_internal_dag = nx.is_directed_acyclic_graph(internal_graph)
        print(f"  Is DAG: {is_internal_dag}")

        if is_internal_dag:
            try:
                internal_depth = nx.dag_longest_path_length(internal_graph)
                internal_longest = nx.dag_longest_path(internal_graph)

                print(f"  Internal-only max depth: {internal_depth}")
                print(f"\n  Internal-only longest path ({len(internal_longest)} nodes):")
                for i, node in enumerate(internal_longest[:10]):
                    print(f"    {i}: {node}")

            except Exception as e:
                print(f"  ❌ Error: {e}")

    print_section("7. Diagnosis")

    print("\n🔍 Analysis complete. Check results above for:")
    print("  1. Is the graph actually a DAG? (If not, max_depth = -1 is correct)")
    print("  2. What is the longest path according to NetworkX?")
    print("  3. Do manual traces match NetworkX calculation?")
    print("  4. Is the architecture genuinely flat?")
    print("  5. Do external modules break dependency chains?")
    print("\n")


if __name__ == '__main__':
    try:
        investigate_depth()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
