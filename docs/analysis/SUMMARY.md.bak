# Investigation Summary: Dependency Graph Depth Issue

**Task**: #1003
**Date**: 2025-10-24
**Status**: ✅ **ROOT CAUSE IDENTIFIED**

---

## Quick Facts

- **Issue**: Dependency graph reports `max_depth=1` for 112K LOC project
- **Expected**: `max_depth=5-8` for layered architecture
- **Root Cause**: Path normalization bug creates duplicate nodes
- **Impact**: All dependency metrics are unreliable
- **Fix Complexity**: Low (standardize path format)
- **Priority**: High (blocking architectural analysis)

---

## The Bug

**Path normalization inconsistency creates two nodes for the same file:**

```
create.py → project      (Node 1: no .py, no outgoing edges, isolated leaf)
            project.py   (Node 2: with .py, no incoming edges, isolated root)
```

**Should be:**
```
create.py → project (single node with both incoming and outgoing edges)
            ↓
            methods
            ↓
            models
            ↓
            enums (depth = 4)
```

---

## Evidence

### Duplicate Nodes Found
```
Node: agentpm/cli/utils/project
  In-degree: 89, Out-degree: 0 (appears as leaf)

Node: agentpm/cli/utils/project.py
  In-degree: 0, Out-degree: 5 (appears as root)

→ These are the SAME FILE but treated as different nodes!
```

### Impossible Metrics
```
Root modules:     736 (56.5%) ← Way too high
Internal modules: 0   (0%)    ← IMPOSSIBLE for any non-trivial project
Leaf modules:     610 (46.8%) ← Way too high
Max depth:        1            ← Unrealistic for layered architecture
```

---

## Root Cause Location

**File**: `agentpm/utils/graph_builders.py`
**Function**: `build_import_graph()` (lines 69-170)

**Problem Flow**:
1. File scan phase adds nodes WITH `.py`: `project.py`
2. Import resolution adds nodes WITHOUT `.py`: `project`
3. Result: Duplicate disconnected nodes

**Why**:
- File paths from glob: `Path("project.py")` → `"project.py"`
- Import from AST: `"agentpm.cli.utils.project"` → `"agentpm/cli/utils/project"`
- Different normalization rules create different node names

---

## The Fix

**Strip `.py` extension consistently everywhere:**

```python
# In build_import_graph() when processing source files:
rel_source = str(source_path.relative_to(project_path))

# ADD THIS:
if rel_source.endswith('.py'):
    rel_source = rel_source[:-3]
elif rel_source.endswith('/__init__.py'):
    rel_source = rel_source[:-12]

graph.add_node(rel_source)  # Now matches import format
```

**No changes needed in `_normalize_import_path()`** - it already produces the right format.

---

## Validation After Fix

**Tests to add**:
```python
def test_no_duplicate_nodes():
    """Ensure no files have both .py and non-.py versions"""
    # Expected: 0 duplicates found

def test_realistic_max_depth():
    """Verify depth matches architecture"""
    assert analysis.max_depth >= 5

def test_internal_modules_exist():
    """Most modules should be internal (both in/out edges)"""
    assert internal_count > 0
    assert internal_count > root_count
```

**Expected metrics after fix**:
- Max depth: 5-8 hops
- Root modules: ~80 (10%)
- Internal modules: ~600 (70%)
- Leaf modules: ~170 (20%)

---

## Impact Assessment

### What's Broken
- ❌ Max depth calculation
- ❌ Root/leaf identification
- ❌ Coupling metrics (fragmented)
- ❌ Architectural insights
- ⚠️ Circular dependency detection (incomplete)
- ⚠️ Dependency chain tracing

### What's Still Valid
- ✅ Total node count (includes duplicates, but count is accurate)
- ✅ Total edge count
- ✅ Individual import statements (edges are correct, just disconnected)

---

## Documents

1. **Full Analysis**: `dependency-graph-depth-investigation.md`
   - Complete investigation process
   - Evidence and reproduction steps
   - Fix specification
   - Test plan

2. **Visual Explanation**: `dependency-graph-bug-visualization.md`
   - Diagrams showing bug behavior
   - Before/after comparisons
   - Code-level breakdown

3. **Investigation Script**: `/Users/nigelcopley/.project_manager/aipm-v2/investigate_depth.py`
   - Reproduces the bug
   - Manual chain tracing
   - Duplicate node detection

---

## Next Steps

1. ✅ **Investigation Complete** (this task)
2. ⬜ **Implement fix** in `graph_builders.py`
3. ⬜ **Add regression tests**
4. ⬜ **Regenerate all dependency metrics**
5. ⬜ **Update documentation** with corrected metrics
6. ⬜ **Validate fix** with known dependency chains

**Estimated fix time**: 2 hours

---

## Key Takeaway

> The dependency graph `max_depth=1` is **not accurate** - it's a symptom of a path normalization bug that fragments the graph into disconnected components. The actual architecture has depth of 5-8 hops, but duplicate nodes break the chains at every level.

**Fix is straightforward**: Standardize path format to never include `.py` extension.

---

**Investigator**: Root Cause Analyst
**Review Status**: Awaiting technical review
**Task**: #1003 - Investigation phase complete
