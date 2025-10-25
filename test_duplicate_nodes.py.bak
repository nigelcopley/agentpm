#!/usr/bin/env python3
"""
Test script to verify duplicate node fix.

Before fix:
- agentpm/cli/utils/project.py (120 files with .py)
- agentpm/cli/utils/project (120 files without .py from imports)
- Total: 240 nodes (120 duplicates)

After fix:
- agentpm.cli.utils.project (120 files, unified format)
- Total: 120 nodes (no duplicates)
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agentpm.core.detection.graphs import DependencyGraphService


def check_duplicate_nodes():
    """Check for duplicate nodes in dependency graph."""

    print("=" * 80)
    print("  Duplicate Node Detection Test")
    print("=" * 80)

    project_path = Path.cwd()
    service = DependencyGraphService(project_path)
    graph = service.build_graph(force_rebuild=True)

    print(f"\nTotal nodes: {graph.number_of_nodes()}")
    print(f"Total edges: {graph.number_of_edges()}")

    # Group nodes by normalized name (remove dots/slashes and .py)
    normalized_groups = defaultdict(list)

    for node in graph.nodes():
        # Normalize: remove dots, slashes, .py extension
        normalized = str(node).replace('.', '').replace('/', '').replace('py', '')
        normalized_groups[normalized].append(node)

    # Find duplicates (groups with >1 node)
    duplicates = {k: v for k, v in normalized_groups.items() if len(v) > 1}

    print(f"\n📊 Duplicate Analysis:")
    print(f"  Unique normalized names: {len(normalized_groups)}")
    print(f"  Groups with duplicates: {len(duplicates)}")

    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} potential duplicates:")
        print(f"\nSample duplicates (first 10):")
        for i, (norm, nodes) in enumerate(list(duplicates.items())[:10]):
            print(f"\n  Group {i+1}: {len(nodes)} nodes")
            for node in nodes:
                in_deg = graph.in_degree(node)
                out_deg = graph.out_degree(node)
                print(f"    - {node} (← {in_deg}, → {out_deg})")

        print(f"\n❌ TEST FAILED: Found duplicate nodes")
        return False
    else:
        print(f"\n✅ TEST PASSED: No duplicate nodes detected")

        # Additional verification: check node format consistency
        slash_nodes = [n for n in graph.nodes() if '/' in str(n)]
        dot_nodes = [n for n in graph.nodes() if '.' in str(n) and '/' not in str(n)]
        py_nodes = [n for n in graph.nodes() if str(n).endswith('.py')]

        print(f"\n📋 Node Format Analysis:")
        print(f"  Nodes with slashes (/): {len(slash_nodes)}")
        print(f"  Nodes with dots only: {len(dot_nodes)}")
        print(f"  Nodes ending in .py: {len(py_nodes)}")

        if slash_nodes or py_nodes:
            print(f"\n⚠️  WARNING: Found inconsistent node formats")
            if slash_nodes:
                print(f"  Sample slash nodes: {slash_nodes[:5]}")
            if py_nodes:
                print(f"  Sample .py nodes: {py_nodes[:5]}")
            return False
        else:
            print(f"\n✅ All nodes use consistent dot notation (no slashes, no .py)")
            return True


if __name__ == '__main__':
    try:
        success = check_duplicate_nodes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
