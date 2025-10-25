# Dependency Graph Bug: Visual Explanation

## The Problem: Duplicate Nodes Break Chains

### Current (Broken) Behavior

```
┌─────────────────────────────────────────────────────────────┐
│ Graph State: Fragmented Chains (max_depth = 1)             │
└─────────────────────────────────────────────────────────────┘

File Scan Phase Creates:
┌──────────────────────┐
│ create.py            │ in=0, out=11  ← Root (correct)
└──────────┬───────────┘
           │
           ├───────────────────────────────┐
           ↓                               ↓
┌──────────────────────┐        ┌──────────────────────┐
│ project              │ ★      │ methods              │ ★
│ (no .py extension)   │        │ (no .py extension)   │
│ in=89, out=0         │        │ in=99, out=0         │
│                      │        │                      │
│ ISOLATED LEAF!       │        │ ISOLATED LEAF!       │
└──────────────────────┘        └──────────────────────┘

Import Resolution Phase Also Creates:
┌──────────────────────┐        ┌──────────────────────┐
│ project.py           │        │ methods/__init__.py  │
│ (with .py extension) │        │ (with .py extension) │
│ in=0, out=5          │        │ in=0, out=7          │
│                      │        │                      │
│ ISOLATED ROOT!       │        │ ISOLATED ROOT!       │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           ↓                               ↓
     (more isolated                   (more isolated
      leaf nodes)                      leaf nodes)

Result: Multiple disconnected chains, all depth=1
★ These should be THE SAME NODE!
```

### Expected (Fixed) Behavior

```
┌─────────────────────────────────────────────────────────────┐
│ Graph State: Connected Chains (max_depth = 5+)             │
└─────────────────────────────────────────────────────────────┘

Single Node Per File:
┌──────────────────────┐
│ create.py            │ depth=0, in=0, out=11
└──────────┬───────────┘
           │
           ├───────────────────────────────┐
           ↓                               ↓
┌──────────────────────┐        ┌──────────────────────┐
│ project              │        │ adapters             │ depth=1
│ in=89, out=5         │        │ in=45, out=3         │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           ↓                               ↓
┌──────────────────────┐        ┌──────────────────────┐
│ methods              │        │ models               │ depth=2
│ in=99, out=7         │        │ in=234, out=2        │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           ↓                               ↓
┌──────────────────────┐        ┌──────────────────────┐
│ models               │ ←──────┤ enums                │ depth=3
│ in=234, out=2        │        │ in=167, out=1        │
└──────────┬───────────┘        └──────────────────────┘
           │
           ↓
┌──────────────────────┐
│ enums                │ depth=4
│ in=167, out=1        │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ typing               │ depth=5 (external)
│ (external module)    │
└──────────────────────┘

Result: Proper dependency chain, depth=5
```

## The Bug in Code

### Step-by-Step Breakdown

```python
# File: agentpm/utils/graph_builders.py
def build_import_graph(imports_by_file, project_path):
    graph = nx.DiGraph()

    # STEP 1: Add source files (from scanning)
    for source_file, imported_modules in imports_by_file.items():
        # source_file comes from: Path.glob("**/*.py")
        # Example: "agentpm/cli/utils/project.py"

        rel_source = str(source_path.relative_to(project_path))
        # rel_source = "agentpm/cli/utils/project.py" ← WITH .py

        graph.add_node(rel_source)  # Node created with .py
        # ✓ Node: "agentpm/cli/utils/project.py"

        # STEP 2: Process imports from this file
        for imported_module in imported_modules:
            # imported_module comes from AST: extract_imports()
            # Example: "agentpm.cli.utils.project"

            imported_path = _normalize_import_path(imported_module, ...)
            # ↓ _normalize_import_path() logic:
            # module_name.replace('.', '/')
            # → "agentpm/cli/utils/project" ← NO .py!

            graph.add_node(imported_path)  # SECOND node created!
            # ✗ Node: "agentpm/cli/utils/project" (different from above!)

            graph.add_edge(rel_source, imported_path)
            # Edge: "project.py" → "project" (should be self-loop or unified!)

    # Result: TWO nodes for same file with different names!
```

### Why _normalize_import_path() Doesn't Add .py

```python
def _normalize_import_path(module_name, source_file, project_path):
    # Handles: from agentpm.cli.utils import project
    #          ↓
    # Returns: agentpm/cli/utils/project

    # Current logic (simplified):
    module_path = module_name.replace('.', '/')
    return module_path  # ← NO .py extension added!

    # The function doesn't check if this maps to:
    # - agentpm/cli/utils/project.py (file)
    # - agentpm/cli/utils/project/__init__.py (package)
    #
    # It just converts dots to slashes and returns
```

## Impact Visualization

### Metrics Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ Project: APM (Agent Project Manager) (112K LOC, Complex Architecture)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ CURRENT (BROKEN):                                               │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Total Nodes:    1,302                                      │ │
│ │ Total Edges:    4,093                                      │ │
│ │ Max Depth:      1      ← WRONG                             │ │
│ │ Root Modules:   736    (56.5%) ← TOO HIGH                  │ │
│ │ Internal:       0      (0%)    ← IMPOSSIBLE                │ │
│ │ Leaf Modules:   610    (46.8%) ← TOO HIGH                  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ EXPECTED (AFTER FIX):                                           │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Total Nodes:    ~850   (duplicates merged)                 │ │
│ │ Total Edges:    4,093  (same, but now connected)           │ │
│ │ Max Depth:      5-8    ← Realistic for layered arch        │ │
│ │ Root Modules:   ~80    (10%) ← CLI, tests, blueprints      │ │
│ │ Internal:       ~600   (70%) ← Most of codebase            │ │
│ │ Leaf Modules:   ~170   (20%) ← Utils, enums, models        │ │
│ └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Example: project.py Coupling

```
┌─────────────────────────────────────────────────────────────────┐
│ Module: agentpm/cli/utils/project.py                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ CURRENT (FRAGMENTED):                                           │
│                                                                 │
│ Node 1: "project" (without .py)                                │
│   ├─ Afferent Coupling (Ca):  89   ← Modules that import this  │
│   ├─ Efferent Coupling (Ce):  0    ← Modules this imports      │
│   └─ Instability (I):         0.00 ← Ce/(Ce+Ca) = stable       │
│                                                                 │
│ Node 2: "project.py" (with .py)                                │
│   ├─ Afferent Coupling (Ca):  0    ← No incoming edges         │
│   ├─ Efferent Coupling (Ce):  5    ← Has outgoing edges        │
│   └─ Instability (I):         1.00 ← Ce/(Ce+Ca) = unstable     │
│                                                                 │
│ ❌ Contradictory metrics for the SAME file!                     │
│                                                                 │
│ EXPECTED (UNIFIED):                                             │
│                                                                 │
│ Node: "project"                                                │
│   ├─ Afferent Coupling (Ca):  89   ← Modules that import this  │
│   ├─ Efferent Coupling (Ce):  5    ← Modules this imports      │
│   └─ Instability (I):         0.05 ← Ce/(Ce+Ca) = very stable  │
│                                                                 │
│ ✓ Single accurate metric                                       │
└─────────────────────────────────────────────────────────────────┘
```

## The Fix: Path Normalization Standardization

### Before Fix (Inconsistent)

```python
# Location 1: File scanning (service.py:206-211)
rel_path = str(file_path.relative_to(project_path))
# Result: "agentpm/cli/utils/project.py" ← WITH .py
imports_by_file[rel_path] = imports

# Location 2: Graph building (graph_builders.py:127-145)
rel_source = str(source_path.relative_to(project_path))
# Result: "agentpm/cli/utils/project.py" ← WITH .py
graph.add_node(rel_source)

# Location 3: Import normalization (graph_builders.py:173-220)
module_path = module_name.replace('.', '/')
# Result: "agentpm/cli/utils/project" ← NO .py
return module_path

# ❌ Three different formats for the same file!
```

### After Fix (Consistent)

```python
# Option A: Always strip .py (RECOMMENDED)

# Location 1: File scanning
rel_path = str(file_path.relative_to(project_path))
if rel_path.endswith('.py'):
    rel_path = rel_path[:-3]  # Strip .py
elif rel_path.endswith('/__init__.py'):
    rel_path = rel_path[:-12]  # Strip /__init__.py
imports_by_file[rel_path] = imports
# Result: "agentpm/cli/utils/project" ← NO .py

# Location 2: Graph building (already uses rel_path from above)
graph.add_node(rel_source)
# Result: "agentpm/cli/utils/project" ← NO .py

# Location 3: Import normalization (no change needed)
module_path = module_name.replace('.', '/')
return module_path
# Result: "agentpm/cli/utils/project" ← NO .py

# ✓ All three produce same format!
```

## Test Case: Before vs After

```python
# Test: Verify no duplicate nodes
def test_no_duplicate_nodes():
    from pathlib import Path
    from agentpm.core.detection.graphs import DependencyGraphService

    service = DependencyGraphService(Path.cwd())
    graph = service.build_graph()

    # Before fix: This finds duplicates
    duplicates = []
    for node in graph.nodes():
        if node.endswith('.py'):
            without_ext = node[:-3]
            if graph.has_node(without_ext):
                duplicates.append((node, without_ext))

    # Before fix: len(duplicates) ≈ 450 (most internal files)
    # After fix:  len(duplicates) = 0
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate nodes"


# Test: Verify realistic depth
def test_realistic_max_depth():
    service = DependencyGraphService(Path.cwd())
    analysis = service.analyze_dependencies()

    # Before fix: max_depth = 1
    # After fix:  max_depth ≥ 5 (for layered architecture)
    assert analysis.max_depth >= 5, f"Suspiciously low max_depth: {analysis.max_depth}"


# Test: Verify internal modules exist
def test_internal_modules_exist():
    service = DependencyGraphService(Path.cwd())
    graph = service.build_graph()

    roots = [n for n in graph.nodes() if graph.in_degree(n) == 0]
    leaves = [n for n in graph.nodes() if graph.out_degree(n) == 0]
    internal = [n for n in graph.nodes() if graph.in_degree(n) > 0 and graph.out_degree(n) > 0]

    # Before fix: internal = 0
    # After fix:  internal = ~600 (most of codebase)
    assert len(internal) > 0, "No internal modules found - graph is disconnected"
    assert len(internal) > len(roots), "More roots than internal modules - suspicious"
```

## Summary

| Aspect | Current (Bug) | After Fix |
|--------|---------------|-----------|
| Node format | Mixed (.py and no .py) | Consistent (no .py) |
| Duplicate nodes | ~450 pairs | 0 |
| Max depth | 1 | 5-8 |
| Root modules | 736 (56%) | ~80 (10%) |
| Internal modules | 0 (0%) | ~600 (70%) |
| Leaf modules | 610 (47%) | ~170 (20%) |
| Coupling metrics | Fragmented | Unified |
| Chain integrity | Broken | Connected |

**Conclusion**: The bug is a **path normalization inconsistency** that creates duplicate nodes, breaking all transitive dependency chains and rendering depth metrics meaningless.
