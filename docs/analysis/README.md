# Dependency Graph Depth Investigation

**Investigation Date**: 2025-10-24
**Task ID**: #1003
**Status**: ✅ Investigation Complete - Root Cause Identified

---

## Quick Navigation

1. **[SUMMARY.md](./SUMMARY.md)** - Start here
   - Quick facts and key findings
   - The bug explained in 1 page
   - Next steps

2. **[dependency-graph-depth-investigation.md](./dependency-graph-depth-investigation.md)** - Full analysis
   - Complete investigation process
   - Evidence collection and analysis
   - Detailed fix specification
   - Test plan and validation steps

3. **[dependency-graph-bug-visualization.md](./dependency-graph-bug-visualization.md)** - Visual guide
   - Before/after diagrams
   - Code-level breakdown
   - Test case examples

---

## The Issue

Dependency graph reports `max_depth=1` for a 112K LOC project with layered architecture.

**Expected**: `max_depth=5-8` (realistic for hexagonal + layered architecture)

---

## Root Cause

**Path normalization bug creates duplicate nodes:**

```
File on disk:      agentpm/cli/utils/project.py
Graph node 1:      agentpm/cli/utils/project.py    (from file scan)
Graph node 2:      agentpm/cli/utils/project       (from import statements)
                   ↑ These should be ONE node, not two!
```

**Result**: Dependency chains break at every duplicate node, rendering depth=1.

---

## Impact

- **120 files** have duplicate nodes (18.4% of graph)
- **240 nodes** affected (should be 120)
- **All transitive dependencies broken**
- Max depth: 1 instead of 5-8
- Root modules: 736 (56%) instead of ~80 (10%)
- Internal modules: 0 (0%) instead of ~600 (70%)
- Coupling metrics: Fragmented and unreliable

---

## The Fix

**File**: `agentpm/utils/graph_builders.py`
**Function**: `build_import_graph()` (lines 127-145)

**Add path normalization**:
```python
rel_source = str(source_path.relative_to(project_path))

# NEW: Strip .py extension to match import format
if rel_source.endswith('.py'):
    rel_source = rel_source[:-3]
elif rel_source.endswith('/__init__.py'):
    rel_source = rel_source[:-12]

graph.add_node(rel_source)
```

**Estimated time**: 2 hours (fix + tests + validation)

---

## Verification

**Test script**: `/Users/nigelcopley/.project_manager/aipm-v2/investigate_depth.py`

**Run**:
```bash
cd /Users/nigelcopley/.project_manager/aipm-v2
python investigate_depth.py
```

**Expected output** (before fix):
- Max depth: 1
- Root modules: 736
- Internal modules: 0 ← Smoking gun!

**Expected output** (after fix):
- Max depth: 5-8
- Root modules: ~80
- Internal modules: ~600 ← This should never be zero!

---

## Investigation Methodology

### Phase 1: Hypothesis Formation
- Verified NetworkX calculation is correct
- Checked for graph cycles (none found)
- Analyzed root/leaf ratios (revealed impossible 0% internal modules)

### Phase 2: Evidence Collection
- Manually traced dependency chains (all stop at depth 1)
- Examined imports_cache vs graph nodes (found naming mismatch)
- Discovered duplicate nodes with different in/out degrees

### Phase 3: Root Cause Analysis
- Traced path normalization logic
- Identified two different normalization rules
- Demonstrated bug with concrete examples

### Phase 4: Impact Assessment
- Quantified duplicates: 120 files affected
- Calculated metric errors: depth, coupling, roots/leaves all wrong
- Verified fix approach with sample data

---

## Key Findings

### Evidence

✅ **Graph is valid DAG** (no cycles preventing depth calculation)
✅ **NetworkX calculation is correct** (algorithm works as intended)
✅ **File imports exist** (data is being extracted)
❌ **Nodes are duplicated** (same file = 2 nodes with different names)
❌ **Chains are broken** (duplicates act as connection breaks)

### Metrics Analysis

| Metric | Current | Expected | Status |
|--------|---------|----------|--------|
| Max depth | 1 | 5-8 | ❌ Wrong |
| Root modules | 736 (56%) | ~80 (10%) | ❌ Wrong |
| Internal modules | 0 (0%) | ~600 (70%) | ❌ Wrong |
| Leaf modules | 610 (47%) | ~170 (20%) | ❌ Wrong |
| Total nodes | 1,302 | ~850 | ⚠️ Inflated |
| Total edges | 4,093 | 4,093 | ✅ Correct |

---

## Deliverables

### Analysis Documents
- ✅ Root cause analysis report
- ✅ Visual explanation with diagrams
- ✅ Investigation summary
- ✅ This README

### Code Artifacts
- ✅ Investigation script (`investigate_depth.py`)
- ✅ Evidence data (inline in reports)
- ⬜ Fix implementation (pending)
- ⬜ Regression tests (pending)

---

## Next Steps

1. **Review findings** with architecture team
2. **Implement fix** in `graph_builders.py`
3. **Add tests** to prevent regression:
   - `test_no_duplicate_nodes()`
   - `test_realistic_max_depth()`
   - `test_internal_modules_exist()`
4. **Regenerate metrics** after fix
5. **Update documentation** with corrected values
6. **Close Task #1003**

---

## References

### Code Locations
- Bug location: `agentpm/utils/graph_builders.py:127-170`
- Service: `agentpm/core/detection/graphs/service.py`
- Models: `agentpm/core/database/models/detection_graph.py`

### Related Tasks
- Task #1003: Investigate dependency graph depth issue

### Investigation Team
- Root Cause Analyst (lead investigator)
- Evidence collection: Systematic tracing
- Analysis method: Database-first, evidence-driven

---

**Status**: Investigation phase complete. Ready for fix implementation.
