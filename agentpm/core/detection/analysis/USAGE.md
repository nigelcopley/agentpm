# Static Analysis Service - Usage Guide

## Overview

The Static Analysis Service provides comprehensive code quality analysis for Python projects using AST parsing and metrics calculation.

**Layer**: 3 (Detection Services)
**Dependencies**: Layer 1 utilities only (ast_utils, metrics_calculator)
**Performance**: <2s for 100 files (first run), <100ms (cached)

## Quick Start

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService

# Initialize service
service = StaticAnalysisService(Path("/path/to/project"))

# Analyze entire project
analysis = service.analyze_project()

# Print summary
summary = analysis.get_summary()
print(f"Quality Score: {summary['quality_score']:.1f}/100")
print(f"Files: {summary['files_analyzed']}")
print(f"Avg Complexity: {summary['avg_complexity']:.2f}")
print(f"Avg Maintainability: {summary['avg_maintainability']:.1f}")
```

## Features

### 1. Single File Analysis

Analyze individual Python files for code quality metrics.

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService

service = StaticAnalysisService(Path("."))
analysis = service.analyze_file(Path("mymodule.py"))

if analysis:
    print(f"Lines: {analysis.total_lines}")
    print(f"Code lines: {analysis.code_lines}")
    print(f"Complexity (max): {analysis.complexity_max}")
    print(f"Functions: {analysis.function_count}")
    print(f"Classes: {analysis.class_count}")
    print(f"MI: {analysis.maintainability_index:.1f}")
    print(f"Quality: {analysis.quality_score:.1f}/100")
```

**Output Metrics**:
- `total_lines`: All lines (including blanks)
- `code_lines`: Executable code only
- `comment_lines`: Comments and docstrings
- `blank_lines`: Empty lines
- `complexity_avg`: Average cyclomatic complexity
- `complexity_max`: Maximum cyclomatic complexity
- `function_count`: Number of functions
- `class_count`: Number of classes
- `maintainability_index`: MI score (0-100)
- `quality_score`: Overall quality (0-100)

### 2. Project Analysis

Analyze entire Python projects with customizable file patterns.

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService

service = StaticAnalysisService(Path("/my/project"))

# Analyze all Python files (excluding tests)
analysis = service.analyze_project(
    file_pattern="**/*.py",
    exclude_patterns=[
        "**/tests/**",
        "**/__pycache__/**",
        "**/.venv/**",
    ]
)

print(f"Files analyzed: {analysis.total_files}")
print(f"Total lines: {analysis.total_lines}")
print(f"Avg complexity: {analysis.avg_complexity:.2f}")
print(f"Max complexity: {analysis.max_complexity}")
print(f"Avg MI: {analysis.avg_maintainability:.1f}")
```

### 3. High-Complexity Detection

Identify files exceeding complexity thresholds.

```python
# Find files with complexity > 10
high_complexity = service.get_high_complexity_files(
    analysis,
    threshold=10
)

print(f"Found {len(high_complexity)} high-complexity files:\n")
for file in high_complexity:
    print(f"  {file.file_path}")
    print(f"    Max complexity: {file.complexity_max}")
    print(f"    Functions: {file.function_count}")
    print(f"    MI: {file.maintainability_index:.1f}")
    print()
```

**Complexity Guidelines**:
- 1-5: Simple (green)
- 6-10: Moderate (yellow)
- 11+: Complex (red) - consider refactoring

### 4. Maintainability Analysis

Identify files below maintainability thresholds.

```python
# Find files with MI < 65
low_maintainability = service.get_low_maintainability_files(
    analysis,
    threshold=65.0
)

print(f"Found {len(low_maintainability)} low-maintainability files:\n")
for file in low_maintainability:
    print(f"  {file.file_path}")
    print(f"    MI: {file.maintainability_index:.1f}")
    print(f"    Code lines: {file.code_lines}")
    print(f"    Complexity: {file.complexity_max}")
    print()
```

**MI Scale**:
- 85-100: Excellent (green)
- 65-84: Good (yellow)
- 0-64: Needs attention (red)

### 5. Detailed Reports

Generate comprehensive reports for code review.

```python
# Complexity report
complexity_report = service.generate_complexity_report(
    analysis,
    threshold=10,
    top_n=10
)

print("Complexity Report")
print(f"  Threshold: {complexity_report.threshold}")
print(f"  Violations: {complexity_report.total_violations}")
print(f"  Top {len(complexity_report.hotspots)} complex functions:")
for hotspot in complexity_report.hotspots:
    print(f"    - {hotspot['name']} (complexity: {hotspot['complexity']})")

# Maintainability report
mi_report = service.generate_maintainability_report(
    analysis,
    threshold=65.0
)

print("\nMaintainability Report")
print(f"  Threshold: {mi_report.threshold}")
print(f"  Violations: {mi_report.total_violations}")
print(f"  Low-MI files: {len(mi_report.low_maintainability_files)}")
```

### 6. Caching

The service automatically caches analysis results for performance.

```python
# First run: parses and caches
service = StaticAnalysisService(Path("/my/project"), cache_enabled=True)
analysis = service.analyze_project()  # Takes ~2s for 100 files

# Second run: uses cache
analysis = service.analyze_project()  # Takes <100ms

# Disable caching
service = StaticAnalysisService(Path("/my/project"), cache_enabled=False)
analysis = service.analyze_project()  # Always parses

# Custom cache directory
service = StaticAnalysisService(
    Path("/my/project"),
    cache_enabled=True,
    cache_dir=Path("/tmp/analysis_cache")
)
```

**Cache Behavior**:
- Cache files stored in `.cache/analysis/` by default
- Cache invalidates automatically when file content changes (SHA-256 hash)
- Cache entries are JSON files with file hash + analysis data
- Cache persists across sessions

## Architecture Compliance

The Static Analysis Service follows the three-layer architecture:

```
Layer 3 (Detection Services)
├── StaticAnalysisService  ← Business logic orchestration
├── FileAnalysis           ← Pydantic models
└── ProjectAnalysis        ← Pydantic models

Layer 1 (Utilities)
├── ast_utils             ← AST parsing primitives
└── metrics_calculator    ← Metrics calculation
```

**Design Principles**:
- ✅ Layer 3 uses ONLY Layer 1 utilities
- ✅ No direct plugin (Layer 2) dependencies
- ✅ Stateless service pattern (no database)
- ✅ Type-safe with Pydantic models
- ✅ Performance-optimized with caching
- ✅ Safe AST parsing (no eval/exec)

## Performance

**Targets** (from architecture document):
- First run: <2s for 100 files
- Cached: <100ms
- Memory: <500MB for large projects

**Actual** (measured on agentpm codebase):
- 3 files: 0.15s (first run), 0.12s (cached)
- Memory: <50MB for small projects

**Optimization Tips**:
1. Enable caching (default)
2. Use exclude_patterns to skip unnecessary files
3. Analyze incrementally (file-by-file for large projects)
4. Use custom cache directory on fast SSD

## Error Handling

The service handles errors gracefully:

```python
# Parse failures return None
analysis = service.analyze_file(Path("malformed.py"))
if analysis is None:
    print("Parse failed (syntax error or file too large)")

# Project analysis skips failed files
analysis = service.analyze_project()
print(f"Successfully analyzed {analysis.total_files} files")
# (Failed files are silently skipped)
```

**Failure Modes**:
- Syntax errors: Returns None (graceful degradation)
- File >10MB: Returns None (safety limit)
- Encoding issues: Returns None (unsupported encoding)
- Cache corruption: Ignores cache, re-analyzes

## Examples

### Example 1: Code Quality Dashboard

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService


def quality_dashboard(project_path: Path):
    service = StaticAnalysisService(project_path)
    analysis = service.analyze_project()

    summary = analysis.get_summary()

    print("=" * 60)
    print(f"Code Quality Dashboard: {project_path.name}")
    print("=" * 60)
    print(f"Files: {summary['files_analyzed']}")
    print(f"Lines: {summary['total_lines']:,}")
    print(f"Code: {summary['code_lines']:,}")
    print(f"Complexity (avg): {summary['avg_complexity']:.2f}")
    print(f"Complexity (max): {summary['max_complexity']}")
    print(f"Maintainability: {summary['avg_maintainability']:.1f}/100")
    print(f"Quality Score: {summary['quality_score']:.1f}/100")
    print()

    # Risk summary
    print("Risk Assessment:")
    print(f"  High complexity files: {summary['high_complexity_files']}")
    print(f"  Low maintainability files: {summary['low_maintainability_files']}")
    print("=" * 60)


quality_dashboard(Path("/my/project"))
```

### Example 2: CI/CD Quality Gate

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService
import sys


def quality_gate(project_path: Path, min_quality: float = 70.0):
    service = StaticAnalysisService(project_path)
    analysis = service.analyze_project()

    summary = analysis.get_summary()
    quality_score = summary['quality_score']

    print(f"Quality Score: {quality_score:.1f}/100")
    print(f"Minimum Required: {min_quality}/100")

    if quality_score < min_quality:
        print("❌ Quality gate FAILED")
        sys.exit(1)
    else:
        print("✅ Quality gate PASSED")
        sys.exit(0)


quality_gate(Path("/my/project"), min_quality=70.0)
```

### Example 3: Refactoring Candidates

```python
from pathlib import Path
from agentpm.core.detection.analysis import StaticAnalysisService


def find_refactoring_candidates(project_path: Path):
    service = StaticAnalysisService(project_path)
    analysis = service.analyze_project()

    # Get complexity report
    report = service.generate_complexity_report(analysis, threshold=10)

    print("Refactoring Candidates (Complexity > 10):")
    print("=" * 60)

    for file in report.high_complexity_files:
        print(f"\n{file.file_path}")
        print(f"  Complexity: {file.complexity_max}")
        print(f"  MI: {file.maintainability_index:.1f}")
        print(f"  Functions: {file.function_count}")
        print(f"  Lines: {file.code_lines}")

        # Show complex functions
        complex_funcs = [
            f for f in file.functions
            if f.get('complexity', 0) > 10
        ]
        if complex_funcs:
            print("  Complex functions:")
            for func in complex_funcs:
                print(f"    - {func['name']} (complexity: {func['complexity']})")


find_refactoring_candidates(Path("/my/project"))
```

## API Reference

See docstrings in:
- `models.py`: Pydantic models
- `service.py`: Service implementation

## License

Part of APM (Agent Project Manager) Detection Pack (MIT License)
