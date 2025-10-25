# Dependency Graph Depth Investigation

**Date**: 2025-10-24
**Task**: #1003
**Investigator**: Root Cause Analyst
**Status**: ✅ Root Cause Identified

---

## Executive Summary

**Finding**: The dependency graph correctly reports `max_depth=1`, but this is due to a **critical bug** in the graph construction logic, not an accurate reflection of the architecture.

**Root Cause**: File path normalization inconsistency creates duplicate nodes for the same file, breaking dependency chains.

**Impact**:
- Dependency analysis metrics are unreliable
- Circular dependency detection may miss cycles
- Coupling metrics are fragmented across duplicate nodes
- Architectural insights are invalid

**Fix Required**: Yes - Path normalization must be standardized throughout `build_import_graph()`.

---

## Investigation Process

### 1. Initial Hypothesis Testing

**Test**: Verify NetworkX calculation
```python
longest_path = nx.dag_longest_path(graph)
length = nx.dag_longest_path_length(graph)
# Result: length = 1, path = ['tests/test_idea_integration.py', 'agentpm/cli/commands/idea/context']
```

**Observation**: NetworkX calculation is correct. The graph genuinely has max depth of 1.

**Question**: Is the architecture really this flat, or is the graph construction broken?

---

### 2. Manual Dependency Chain Trace

**Test Module**: `agentpm/cli/commands/work_item/create.py`

**Expected Chain** (based on imports):
```
create.py
  → imports agentpm.cli.utils.project
    → imports agentpm.core.database.methods
      → imports agentpm.core.database.models.work_item
        → imports agentpm.core.database.enums
          → (base types)
```
**Expected Depth**: 4-5 hops

**Actual Chain in Graph**:
```
create.py → agentpm/cli/utils/project (STOPS)
```
**Actual Depth**: 1 hop

**Red Flag**: File `project.py` exists, has imports, but they're not in the graph!

---

### 3. Root vs Leaf Module Analysis

**Metrics**:
- Root modules (no incoming dependencies): **736** (56.5%)
- Leaf modules (no outgoing dependencies): **610** (46.8%)
- Internal modules (both in and out): **0** (0%)

**Critical Finding**: **Zero internal modules**. Every node is either:
- A root (entry point with dependencies)
- A leaf (dependency with no further deps)

**Implication**: No transitive dependency chains exist in the graph. This is architecturally impossible for a 112K LOC project.

---

### 4. Duplicate Node Discovery (The Bug)

**Investigation**: Check graph nodes vs imports cache

```python
# File in cache (as scanned)
'agentpm/cli/utils/project.py'
  → Has imports: ['agentpm.cli.utils.services', 'agentpm.core.database.methods', ...]
  → In-degree: 0, Out-degree: 5

# Node created from import statements
'agentpm/cli/utils/project'  # Note: NO .py extension
  → No imports data
  → In-degree: 89, Out-degree: 0
```

**Root Cause Identified**:
Two separate nodes exist for the same file due to inconsistent path normalization!

---

## Root Cause Analysis

### The Bug: Path Normalization Mismatch

**Location**: `agentpm/utils/graph_builders.py::build_import_graph()`

**Problematic Flow**:

1. **File Scanning Phase** (Lines 127-145):
   ```python
   for source_file, imported_modules in imports_by_file.items():
       # source_file = 'agentpm/cli/utils/project.py' (with .py)
       rel_source = str(source_path.relative_to(project_path))
       # Creates node: 'agentpm/cli/utils/project.py'
       graph.add_node(rel_source, ...)
   ```

2. **Import Resolution Phase** (Lines 148-169):
   ```python
   for imported_module in imported_modules:
       # imported_module = 'agentpm.cli.utils.project' (from AST)
       imported_path = _normalize_import_path(imported_module, ...)
       # Returns: 'agentpm/cli/utils/project' (NO .py, just dots→slashes)
       graph.add_node(imported_path, ...)  # Creates SECOND node!
       graph.add_edge(rel_source, imported_path, ...)
   ```

3. **Result**: Duplicate nodes
   - Node A: `agentpm/cli/utils/project.py` (from file scan, has imports)
   - Node B: `agentpm/cli/utils/project` (from import resolution, isolated)

### Why This Breaks Depth Calculation

**Dependency Chain Fragmentation**:

```
Intended Graph:
  create.py → project.py → methods/__init__.py → models/__init__.py → ...
  (depth = 4+)

Actual Graph:
  create.py → project (isolated, no outgoing edges)
  project.py (isolated, no incoming edges) → methods (isolated) → ...
  (depth = 1, chains broken)
```

**Evidence**:
- `agentpm/cli/utils/project`: In-degree=89, Out-degree=0 (pure leaf)
- `agentpm/cli/utils/project.py`: In-degree=0, Out-degree=5 (pure root)

These should be the **same node** with In-degree=89 and Out-degree=5!

---

## Impact Assessment

### Affected Metrics

1. **Max Depth**: Reports 1, should be ~5-8
2. **Root Modules**: Reports 736, many are actually internal modules
3. **Leaf Modules**: Reports 610, many are actually internal modules
4. **Circular Dependencies**: May miss cycles that span duplicate nodes
5. **Coupling Metrics**: Fragmented across duplicates
   - `project` appears to have Ca=89, Ce=0 (looks stable)
   - `project.py` appears to have Ca=0, Ce=5 (looks unstable)
   - Reality: Single module with Ca=89, Ce=5

### Reliability Assessment

| Metric | Reliability | Reason |
|--------|-------------|--------|
| Total nodes | ✅ Correct | Count includes duplicates, but total is accurate |
| Total edges | ⚠️ Partial | Edges exist but don't form chains |
| Max depth | ❌ Wrong | Broken chains prevent depth calculation |
| Circular dependencies | ⚠️ Incomplete | Cycles broken by duplicate nodes |
| Coupling per module | ❌ Wrong | Split across duplicates |
| Root/leaf identification | ❌ Wrong | Duplicates create false roots/leaves |

---

## Evidence: Reproduction Steps

### Reproduce the Bug

```bash
cd /Users/nigelcopley/.project_manager/aipm-v2
python investigate_depth.py
```

**Expected Output**:
```
Max depth: 1.0
Longest path (2 nodes):
  0: tests/test_idea_integration.py
  1: agentpm/cli/commands/idea/context

Root modules: 736 (56.5%)
Leaf modules: 610 (46.8%)
Internal modules: 0 (0%)  # ← This should NEVER be zero!
```

### Verify Duplicate Nodes

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())
graph = service.build_graph()

# Check for duplicates
for node in list(graph.nodes()):
    if node.endswith('.py'):
        without_ext = node[:-3]
        if graph.has_node(without_ext):
            print(f"DUPLICATE: {node} and {without_ext}")
            print(f"  With .py: in={graph.in_degree(node)}, out={graph.out_degree(node)}")
            print(f"  Without: in={graph.in_degree(without_ext)}, out={graph.out_degree(without_ext)}")
```

---

## Fix Specification

### Required Changes

**File**: `agentpm/utils/graph_builders.py`

**Function**: `build_import_graph()` (Lines 69-170)

**Fix**: Standardize all node names to use consistent format (choose one):

**Option A**: Always use `.py` extension
```python
def _normalize_import_path(...) -> str:
    # ... existing logic ...
    module_path = module_name.replace('.', '/')

    # NEW: Check if this maps to an actual .py file
    if (project_path / f"{module_path}.py").exists():
        return f"{module_path}.py"
    elif (project_path / module_path / "__init__.py").exists():
        return f"{module_path}/__init__.py"
    else:
        return module_path  # External module
```

**Option B**: Never use `.py` extension (cleaner)
```python
# In build_import_graph(), when adding source files:
for source_file, imported_modules in imports_by_file.items():
    source_path = Path(source_file)
    # ... relative path logic ...

    # NEW: Remove .py extension for consistency
    if rel_source.endswith('.py'):
        rel_source = rel_source[:-3]
    elif rel_source.endswith('/__init__.py'):
        rel_source = rel_source[:-12]  # Remove /__init__.py

    graph.add_node(rel_source, ...)
```

**Recommendation**: Option B (no extensions) is cleaner and matches import statement semantics.

### Test Plan

1. **Unit test**: Verify no duplicate nodes after fix
2. **Integration test**: Verify max_depth > 1 for APM (Agent Project Manager)
3. **Validation test**: Compare coupling metrics before/after (should consolidate)

**Expected Results After Fix**:
- Max depth: 5-8 (realistic for layered architecture)
- Root modules: ~50-100 (CLI, test entry points, Flask blueprints)
- Internal modules: ~500-600 (most of codebase)
- Leaf modules: ~100-200 (utilities, models, enums)

---

## Manual Verification: Expected Chains

### Example 1: CLI Command Chain

**File**: `agentpm/cli/commands/work_item/create.py`

**Expected Dependencies** (after fix):
```
create.py                                    (depth 0)
├→ agentpm/cli/utils/project                 (depth 1)
│  ├→ agentpm/cli/utils/services             (depth 2)
│  └→ agentpm/core/database/methods          (depth 2)
│     └→ agentpm/core/database/models        (depth 3)
│        └→ agentpm/core/database/enums      (depth 4)
└→ agentpm/core/database/adapters            (depth 1)
   └→ agentpm/core/database/models           (depth 2)
```
**Expected Max Depth from create.py**: 4 hops

### Example 2: Core Service Chain

**File**: `agentpm/core/workflow/service.py`

**Expected Dependencies**:
```
service.py                                   (depth 0)
├→ agentpm/core/workflow/state_machine       (depth 1)
│  └→ agentpm/core/database/models           (depth 2)
└→ agentpm/core/database/methods             (depth 1)
   └→ agentpm/core/database/adapters         (depth 2)
      └→ agentpm/core/database/models        (depth 3)
```
**Expected Max Depth from service.py**: 3 hops

---

## Recommendations

### Immediate Actions

1. **Fix the bug** in `build_import_graph()` per Option B above
2. **Add test** to prevent duplicate nodes:
   ```python
   def test_no_duplicate_nodes():
       service = DependencyGraphService(Path.cwd())
       graph = service.build_graph()

       duplicates = []
       for node in graph.nodes():
           if node.endswith('.py'):
               without = node[:-3]
               if graph.has_node(without):
                   duplicates.append((node, without))

       assert len(duplicates) == 0, f"Found duplicate nodes: {duplicates}"
   ```
3. **Regenerate metrics** after fix and update documentation

### Long-term Improvements

1. **Path normalization utility**: Create single source of truth for path format
2. **Graph validation**: Add checks for architectural sanity (e.g., internal_nodes > 0)
3. **Integration tests**: Verify expected depth for known modules
4. **Documentation**: Clarify node naming conventions in graph_builders.py

---

## Conclusion

**The dependency graph `max_depth=1` is NOT accurate** - it's a symptom of a path normalization bug that creates duplicate nodes for the same file.

**Fix complexity**: Low (standardize path format in one location)
**Risk**: Medium (affects all dependency analysis features)
**Priority**: High (blocking reliable architectural analysis)

**Next Steps**: Implement Option B fix in `graph_builders.py`, add regression test, verify metrics improve.

---

**Appendix: Investigation Artifacts**

- Investigation script: `/Users/nigelcopley/.project_manager/aipm-v2/investigate_depth.py`
- Test output: Inline in this document
- Affected code: `agentpm/utils/graph_builders.py` lines 69-220
- Related issue: Task #1003

---

**Sign-off**: Root Cause Analyst
**Review Required**: Yes - Architecture team should validate fix approach
**Estimated Fix Time**: 2 hours (fix + tests + validation)
