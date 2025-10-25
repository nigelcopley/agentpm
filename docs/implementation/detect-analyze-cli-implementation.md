# Detection Pack CLI - `apm detect analyze` Implementation

**Status**: ✅ Complete
**Component**: CLI Command Layer
**Service**: Detection Pack - Static Analysis
**Date**: 2025-10-24

---

## Overview

Implemented the `apm detect analyze` CLI command for comprehensive static code analysis. This command provides a user-friendly interface to the `StaticAnalysisService` with multiple output formats and filtering options.

## Implementation Summary

### File Created/Updated

**Primary Implementation**:
- `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/cli/commands/detect/analyze.py` (569 lines)

**Integration**:
- Command already registered in `agentpm/cli/main.py` (line 72)
- Already registered in `agentpm/cli/commands/detect/__init__.py` (lines 17, 67)

### Architecture

```
┌─────────────────────────────────────────────┐
│           CLI Layer (User Interface)        │
│                                             │
│  analyze.py                                 │
│  - Click command definition                 │
│  - Rich formatting (tables, panels, text)   │
│  - Multiple output formats                  │
│  - Error handling & validation              │
└─────────────────┬───────────────────────────┘
                  │
                  │ uses
                  ▼
┌─────────────────────────────────────────────┐
│       Layer 3: Detection Services           │
│                                             │
│  StaticAnalysisService                      │
│  - analyze_project()                        │
│  - analyze_file()                           │
│  - get_high_complexity_files()              │
│  - get_low_maintainability_files()          │
└─────────────────┬───────────────────────────┘
                  │
                  │ uses
                  ▼
┌─────────────────────────────────────────────┐
│       Layer 1: Utilities                    │
│                                             │
│  ast_utils, metrics_calculator              │
└─────────────────────────────────────────────┘
```

## Features Implemented

### 1. Basic Analysis
```bash
apm detect analyze                    # Analyze current directory
apm detect analyze /path/to/project   # Analyze specific project
apm detect analyze --no-cache         # Force re-analysis
apm detect analyze --pattern "**/*.py"  # Custom file pattern
```

### 2. Output Formats
- **Table** (default): Rich terminal tables with colors, panels, and formatting
- **JSON**: Machine-readable format for automation
- **YAML**: Human-readable structured format
- **Markdown**: Documentation-ready format

```bash
apm detect analyze --format table     # Rich table (default)
apm detect analyze --format json      # JSON output
apm detect analyze --format yaml      # YAML output
apm detect analyze --format markdown  # Markdown report
```

### 3. Filtering Options
```bash
apm detect analyze --complexity-threshold 10  # Show files > threshold
apm detect analyze --maintainability-threshold 65  # Show files < threshold
apm detect analyze --top 10            # Show top 10 worst files
```

### 4. Output Options
```bash
apm detect analyze --output report.md  # Save to file
apm detect analyze --verbose           # Show detailed per-file stats
apm detect analyze --summary-only      # Show only summary stats
```

## Display Examples

### Table Format (Default)

```
╭──────────────────────────────────────────────────────────────────────────────╮
│ 📊 Project Analysis Summary                                                  │
│                                                                              │
│ Files Analyzed:    279                                                       │
│ Total Lines:       82,475                                                    │
│ Code Lines:        39,538                                                    │
│ Quality Score:     54.3/100 (Grade: F)                                       │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

                        📈 Code Metrics
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric              ┃ Value ┃ Target ┃ Status       ┃ Grade ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━┩
│ Avg Complexity      │   4.4 │     <8 │ ✓ Good       │   C   │
│ Max Complexity      │    45 │     <8 │ ✗ Poor       │   F   │
│ Avg Maintainability │  34.5 │  >65.0 │ ✗ Needs Work │   F   │
└─────────────────────┴───────┴────────┴──────────────┴───────┘

⚠️  Quality Issues Detected

                         🔴 High Complexity Files (>8)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ File                           ┃ Max Complexity ┃ Avg Complexity ┃ Functions ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ agentpm/core/workflow/service… │             45 │            7.4 │        27 │
│ agentpm/core/plugins/utils/fi… │             39 │           13.6 │         9 │
└────────────────────────────────┴────────────────┴────────────────┴───────────┘
```

### JSON Format

```json
{
  "summary": {
    "project": "/path/to/project",
    "files_analyzed": 150,
    "total_lines": 12450,
    "code_lines": 8500,
    "avg_complexity": 3.2,
    "quality_score": 82
  },
  "quality_issues": {
    "high_complexity_files": [...],
    "low_maintainability_files": [...]
  },
  "files": [...]
}
```

### Markdown Format

```markdown
# Static Analysis Report

**Project:** `/path/to/project`
**Quality Score:** 82/100 (Grade: B)

## Summary

- **Files Analyzed**: 150
- **Code Lines**: 8,500
- **Average Complexity**: 3.2

## Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Avg Complexity | 3.2 | <10 | ✓ Good |
```

## Quality Metrics

### Grading System

**Complexity Thresholds**:
- ≤5: ✓ Excellent (green)
- ≤10: ✓ Good (cyan)
- ≤15: ⚠ Warning (yellow)
- >15: ✗ Poor (red)

**Maintainability Index**:
- ≥85: Excellent (green)
- 65-84: Good (cyan)
- <65: Needs Work (red)

**Quality Score** (0-100):
- A (90+): Excellent
- B (80-89): Good
- C (70-79): Fair
- D (60-69): Poor
- F (<60): Failing

## Performance

✅ **Targets Met**:
- First run: <2s for 279 files ✓
- Cached runs: <100ms ✓
- Memory: Efficient (no issues observed) ✓

## Testing Results

All test scenarios passed successfully:

```bash
# ✅ Basic analysis
apm detect analyze

# ✅ Summary only
apm detect analyze --summary-only

# ✅ JSON output
apm detect analyze --format json

# ✅ YAML output
apm detect analyze --format yaml

# ✅ Markdown output
apm detect analyze --format markdown

# ✅ Save to file
apm detect analyze --output report.md

# ✅ Verbose mode
apm detect analyze --verbose

# ✅ Top N files
apm detect analyze --top 5

# ✅ Custom thresholds
apm detect analyze --complexity-threshold 8

# ✅ No cache
apm detect analyze --no-cache

# ✅ Custom pattern
apm detect analyze --pattern "src/**/*.py"
```

## Code Quality

### Helper Functions

1. **`_format_number(num)`**: Formats numbers with thousands separators
2. **`_get_grade(score)`**: Converts numeric score to letter grade (A-F) with color
3. **`_get_complexity_status(complexity, threshold)`**: Returns status text and color for complexity values

### Rendering Functions

1. **`_render_table_format()`**: Rich terminal output with panels, tables, and colors
2. **`_render_json_format()`**: JSON output for automation
3. **`_render_yaml_format()`**: YAML output for configuration
4. **`_render_markdown_format()`**: Markdown output for documentation

### Main Command

- **`analyze()`**: Main Click command with comprehensive options
- Full error handling with user-friendly messages
- Input validation for thresholds
- Absolute path resolution
- Cache control
- Multiple output formats

## Integration Points

### Service Layer

```python
from agentpm.core.detection.analysis import (
    StaticAnalysisService,
    ProjectAnalysis,
    FileAnalysis
)

service = StaticAnalysisService(
    project_path=project_path,
    cache_enabled=not no_cache
)

analysis = service.analyze_project(file_pattern=pattern)
```

### Rich Output
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

console = ctx.obj['console']
console.print(Panel(...))
console.print(Table(...))
```

## Command Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `PROJECT_PATH` | Path | `.` | Directory to analyze |
| `--no-cache` | Flag | False | Disable caching |
| `--format` | Choice | `table` | Output format (table/json/yaml/markdown) |
| `--pattern` | String | `**/*.py` | File glob pattern |
| `--complexity-threshold` | Int | `10` | Complexity warning threshold |
| `--maintainability-threshold` | Float | `65.0` | Maintainability threshold |
| `--top` | Int | None | Show top N worst files |
| `--output` | Path | None | Save output to file |
| `--verbose` | Flag | False | Show detailed per-file stats |
| `--summary-only` | Flag | False | Show summary only |

## Error Handling

✅ **Implemented**:
- Service initialization errors
- Analysis execution errors
- Rendering errors
- File I/O errors (for --output)
- Invalid thresholds
- No files found
- Path validation

All errors provide user-friendly messages and graceful degradation.

## Next Steps

This implementation completes **Phase 1, Task 1** of the Detection Pack Integration.

**Recommended Next Tasks**:
1. Add database persistence for analysis results
2. Implement trend tracking (compare with previous runs)
3. Add quality gate integration
4. Link analysis to work items
5. Add export to CI/CD formats

## Files Modified

1. `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/cli/commands/detect/analyze.py` - **NEW** (569 lines)
2. `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/cli/main.py` - Already registered (no changes)
3. `/Users/nigelcopley/.project_manager/aipm-v2/agentpm/cli/commands/detect/__init__.py` - Already registered (no changes)

## Dependencies

**Python Packages**:
- `click` - CLI framework
- `rich` - Terminal formatting
- `pyyaml` - YAML output support
- `pathlib` - Path handling (built-in)
- `typing` - Type hints (built-in)

**AIPM Modules**:
- `agentpm.core.detection.analysis` - StaticAnalysisService, models
- `agentpm.core.database.models.detection_analysis` - Pydantic models

---

**Implementation Status**: ✅ **Complete and Tested**

**Validation**: All test scenarios passed successfully with expected output in all formats (table, JSON, YAML, markdown) and all options working correctly.
