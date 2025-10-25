# Dependency Graph Service - Usage Examples

**Component**: APM (Agent Project Manager) Detection Pack - Layer 3 (Detection Services)
**Version**: 1.0.0
**Date**: 2025-10-24

---

## Overview

The `DependencyGraphService` provides comprehensive dependency analysis for Python projects using NetworkX graph algorithms. It detects circular dependencies, calculates coupling metrics, and exports visualizations.

**Key Features**:
- Build dependency graphs from Python imports
- Detect circular dependencies with severity assessment
- Calculate coupling metrics (afferent, efferent, instability)
- Export Graphviz visualizations
- Performance caching (<50ms cached access)

---

## Basic Usage

### 1. Simple Dependency Analysis

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

# Create service for current project
service = DependencyGraphService(Path.cwd())

# Analyze dependencies
analysis = service.analyze_dependencies()

# Display summary
print(f"Project: {analysis.project_path}")
print(f"Total Modules: {analysis.total_modules}")
print(f"Total Dependencies: {analysis.total_dependencies}")
print(f"Circular Dependencies: {len(analysis.circular_dependencies)}")
print(f"Max Depth: {analysis.max_depth}")
```

**Output**:
```
Project: /Users/name/project
Total Modules: 42
Total Dependencies: 87
Circular Dependencies: 0
Max Depth: 5
```

---

### 2. Detect Circular Dependencies

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())
cycles = service.find_circular_dependencies()

if cycles:
    print(f"⚠️  Found {len(cycles)} circular dependencies:")
    for cycle in cycles:
        print(f"\n{cycle.severity.upper()} severity:")
        print(f"  Cycle: {' → '.join(cycle.cycle)}")
        print(f"  Suggestion: {cycle.suggestion}")
else:
    print("✅ No circular dependencies detected!")
```

**Output Example**:
```
⚠️  Found 2 circular dependencies:

HIGH severity:
  Cycle: src/models.py → src/services.py → src/models.py
  Suggestion: Extract shared functionality to a third module.
              Consider dependency inversion or interface segregation.

MEDIUM severity:
  Cycle: src/api.py → src/handlers.py → src/validators.py → src/api.py
  Suggestion: Break cycle by introducing an abstraction layer or
              event-based communication between modules.
```

---

### 3. Calculate Coupling Metrics

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())
analysis = service.analyze_dependencies()

# Find most coupled modules
high_coupling = [
    m for m in analysis.coupling_metrics
    if m.efferent_coupling > 5 or m.afferent_coupling > 5
]

print("Highly Coupled Modules:")
for metric in sorted(high_coupling, key=lambda m: m.instability, reverse=True):
    print(f"\n{metric.module}:")
    print(f"  Afferent (Ca): {metric.afferent_coupling} (modules that depend on this)")
    print(f"  Efferent (Ce): {metric.efferent_coupling} (modules this depends on)")
    print(f"  Instability (I): {metric.instability:.2f} (0.0=stable, 1.0=unstable)")
    print(f"  Status: {'Unstable' if metric.is_unstable else 'Stable'}")
```

**Output Example**:
```
Highly Coupled Modules:

src/main.py:
  Afferent (Ca): 0 (modules that depend on this)
  Efferent (Ce): 12 (modules this depends on)
  Instability (I): 1.00 (0.0=stable, 1.0=unstable)
  Status: Unstable

src/models.py:
  Afferent (Ca): 15 (modules that depend on this)
  Efferent (Ce): 2 (modules this depends on)
  Instability (I): 0.12 (0.0=stable, 1.0=unstable)
  Status: Stable
```

---

### 4. Analyze Specific Module

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())

# Get coupling metrics for specific module
module = "src/core/models.py"
metrics = service.get_module_coupling(module)

print(f"Coupling Analysis: {module}")
print(f"  Afferent: {metrics.afferent_coupling}")
print(f"  Efferent: {metrics.efferent_coupling}")
print(f"  Instability: {metrics.instability:.2f}")

# Get direct dependencies
deps = service.get_module_dependencies(module, depth=1)

print(f"\nDirect imports ({len(deps['imports'])}):")
for imp in deps['imports']:
    print(f"  → {imp}")

print(f"\nImported by ({len(deps['imported_by'])}):")
for imp in deps['imported_by']:
    print(f"  ← {imp}")
```

---

### 5. Export Visualization

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())

# Export with cycle highlighting
output_path = Path("dependencies.dot")
service.export_graphviz(
    output_path,
    highlight_cycles=True,
    include_metrics=True
)

print(f"✅ Graph exported to {output_path}")
print("\nTo visualize:")
print(f"  dot -Tpng {output_path} -o dependencies.png")
print(f"  open dependencies.png")
```

**Graphviz Commands**:
```bash
# Generate PNG
dot -Tpng dependencies.dot -o dependencies.png

# Generate SVG (scalable)
dot -Tsvg dependencies.dot -o dependencies.svg

# Generate PDF
dot -Tpdf dependencies.dot -o dependencies.pdf

# Use hierarchical layout
dot -Tpng -Grankdir=TB dependencies.dot -o dependencies_vertical.png
```

---

## Advanced Usage

### 6. Monitor Dependency Health

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService


def check_dependency_health(project_path: Path) -> dict:
    """
    Comprehensive dependency health check.

    Returns health report with:
    - Circular dependency status
    - Average instability
    - Highly coupled modules
    - Root/leaf analysis
    """
    service = DependencyGraphService(project_path)
    analysis = service.analyze_dependencies()

    # Calculate health metrics
    health = {
        'status': 'healthy',
        'issues': [],
        'warnings': [],
        'info': {}
    }

    # Check circular dependencies
    if analysis.has_circular_dependencies:
        health['status'] = 'unhealthy'
        health['issues'].append(
            f"Found {len(analysis.circular_dependencies)} circular dependencies"
        )

        high_severity = analysis.high_severity_cycles
        if high_severity:
            health['issues'].append(
                f"  {len(high_severity)} are HIGH severity!"
            )

    # Check average instability
    avg_instability = analysis.average_instability
    health['info']['average_instability'] = f"{avg_instability:.2f}"

    if avg_instability > 0.7:
        health['warnings'].append(
            f"High average instability ({avg_instability:.2f}). "
            "Project may be fragile to changes."
        )

    # Check for God modules (high coupling)
    god_modules = [
        m for m in analysis.coupling_metrics
        if m.afferent_coupling > 10 or m.efferent_coupling > 10
    ]

    if god_modules:
        health['warnings'].append(
            f"Found {len(god_modules)} highly coupled modules"
        )
        health['info']['god_modules'] = [m.module for m in god_modules]

    # Check architecture depth
    if analysis.max_depth > 10:
        health['warnings'].append(
            f"Deep dependency tree (depth={analysis.max_depth}). "
            "Consider flattening architecture."
        )

    health['info']['total_modules'] = analysis.total_modules
    health['info']['total_dependencies'] = analysis.total_dependencies

    return health


# Run health check
report = check_dependency_health(Path.cwd())

print(f"Dependency Health: {report['status'].upper()}")

if report['issues']:
    print("\n❌ ISSUES:")
    for issue in report['issues']:
        print(f"  {issue}")

if report['warnings']:
    print("\n⚠️  WARNINGS:")
    for warning in report['warnings']:
        print(f"  {warning}")

print("\nℹ️  INFO:")
for key, value in report['info'].items():
    print(f"  {key}: {value}")
```

---

### 7. Track Dependency Changes Over Time

```python
from pathlib import Path
from datetime import datetime
import json
from agentpm.core.detection.graphs import DependencyGraphService


def save_dependency_snapshot(project_path: Path, output_file: Path):
    """Save dependency analysis snapshot for historical tracking."""
    service = DependencyGraphService(project_path)
    analysis = service.analyze_dependencies()

    snapshot = {
        'timestamp': analysis.analyzed_at.isoformat(),
        'metrics': {
            'total_modules': analysis.total_modules,
            'total_dependencies': analysis.total_dependencies,
            'circular_dependencies': len(analysis.circular_dependencies),
            'max_depth': analysis.max_depth,
            'average_instability': analysis.average_instability,
        },
        'health': {
            'has_cycles': analysis.has_circular_dependencies,
            'high_severity_cycles': len(analysis.high_severity_cycles),
        }
    }

    output_file.write_text(json.dumps(snapshot, indent=2))
    print(f"✅ Snapshot saved to {output_file}")


def compare_snapshots(baseline: Path, current: Path):
    """Compare dependency snapshots to detect regressions."""
    baseline_data = json.loads(baseline.read_text())
    current_data = json.loads(current.read_text())

    print("Dependency Trend Analysis")
    print("=" * 50)

    for metric in ['total_modules', 'total_dependencies', 'circular_dependencies']:
        baseline_val = baseline_data['metrics'][metric]
        current_val = current_data['metrics'][metric]
        delta = current_val - baseline_val

        symbol = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
        print(f"{symbol} {metric}: {baseline_val} → {current_val} ({delta:+d})")


# Usage
save_dependency_snapshot(Path.cwd(), Path("snapshots/baseline.json"))

# Later...
save_dependency_snapshot(Path.cwd(), Path("snapshots/current.json"))
compare_snapshots(Path("snapshots/baseline.json"), Path("snapshots/current.json"))
```

---

### 8. Integration with CI/CD

```python
#!/usr/bin/env python3
"""
CI/CD Dependency Check Script

Run as part of pre-commit or CI pipeline to enforce dependency policies.
Exits with non-zero code if violations detected.
"""

import sys
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService


def main():
    project_path = Path.cwd()
    service = DependencyGraphService(project_path)
    analysis = service.analyze_dependencies()

    violations = []

    # Policy 1: No circular dependencies
    if analysis.has_circular_dependencies:
        violations.append(
            f"POLICY VIOLATION: Found {len(analysis.circular_dependencies)} "
            f"circular dependencies"
        )

        for cycle in analysis.circular_dependencies:
            if cycle.severity == "high":
                violations.append(f"  HIGH: {' → '.join(cycle.cycle[:3])}...")

    # Policy 2: Maximum dependency depth
    MAX_DEPTH = 8
    if analysis.max_depth > MAX_DEPTH:
        violations.append(
            f"POLICY VIOLATION: Dependency depth {analysis.max_depth} "
            f"exceeds limit {MAX_DEPTH}"
        )

    # Policy 3: Maximum instability
    MAX_INSTABILITY = 0.8
    unstable_modules = [
        m for m in analysis.coupling_metrics
        if m.instability > MAX_INSTABILITY and m.efferent_coupling > 5
    ]

    if unstable_modules:
        violations.append(
            f"POLICY VIOLATION: {len(unstable_modules)} modules exceed "
            f"instability threshold ({MAX_INSTABILITY})"
        )
        for m in unstable_modules[:5]:
            violations.append(f"  - {m.module}: I={m.instability:.2f}")

    # Report results
    if violations:
        print("❌ Dependency Policy Violations Detected:")
        print()
        for violation in violations:
            print(violation)
        print()
        print("Fix violations before committing.")
        sys.exit(1)
    else:
        print("✅ All dependency policies passed!")
        print(f"  Modules: {analysis.total_modules}")
        print(f"  Dependencies: {analysis.total_dependencies}")
        print(f"  Max Depth: {analysis.max_depth}")
        print(f"  Avg Instability: {analysis.average_instability:.2f}")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**Add to `.git/hooks/pre-commit`**:
```bash
#!/bin/bash
python scripts/check_dependencies.py || exit 1
```

---

## Performance Considerations

### Caching

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

service = DependencyGraphService(Path.cwd())

# First analysis (builds graph)
analysis1 = service.analyze_dependencies()  # ~500ms

# Second analysis (uses cache)
analysis2 = service.analyze_dependencies()  # ~50ms (10x faster!)

# Force rebuild if project changed
analysis3 = service.analyze_dependencies(rebuild=True)  # ~500ms
```

### Large Projects

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

# For large projects, limit scope
service = DependencyGraphService(Path.cwd())

# Analyze only specific directory
graph = service.build_graph(file_pattern="src/**/*.py")

# Clear cache to free memory
service.clear_cache()
```

---

## Error Handling

```python
from pathlib import Path
from agentpm.core.detection.graphs import DependencyGraphService

try:
    service = DependencyGraphService(Path("/invalid/path"))
except ValueError as e:
    print(f"Error: {e}")

try:
    service = DependencyGraphService(Path.cwd())
    metrics = service.get_module_coupling("nonexistent.py")
except ValueError as e:
    print(f"Module not found: {e}")
```

---

## Best Practices

1. **Run regularly**: Include in CI/CD pipeline
2. **Set policies**: Define acceptable thresholds for cycles, depth, instability
3. **Track trends**: Save snapshots to monitor architectural evolution
4. **Visualize**: Use Graphviz exports for architecture reviews
5. **Fix high-severity cycles first**: Prioritize 2-module circular dependencies
6. **Monitor God modules**: Watch for modules with >10 coupling

---

## Related Documentation

- [Detection Pack Architecture](../architecture/detection-pack-architecture.md)
- [Graph Builders Utility](../../agentpm/core/plugins/utils/graph_builders.py)
- [AST Utils](../../agentpm/core/plugins/utils/ast_utils.py)

---

**Author**: APM (Agent Project Manager) Detection Pack Team
**Version**: 1.0.0
**Last Updated**: 2025-10-24
