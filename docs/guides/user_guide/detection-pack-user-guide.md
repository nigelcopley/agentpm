# Detection Pack User Guide

**Comprehensive Project Intelligence** | Version 2.0 | Deep Code Analysis & Architecture Validation

The Detection Pack provides 5 powerful commands for static analysis, dependency management, compliance reporting, architecture validation, and quality enforcement.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Command Reference](#command-reference)
   - [apm detect analyze](#apm-detect-analyze)
   - [apm detect graph](#apm-detect-graph)
   - [apm detect sbom](#apm-detect-sbom)
   - [apm detect patterns](#apm-detect-patterns)
   - [apm detect fitness](#apm-detect-fitness)
4. [Common Workflows](#common-workflows)
5. [Output Formats](#output-formats)
6. [Troubleshooting](#troubleshooting)
7. [CI/CD Integration](#cicd-integration)

---

## Overview

### What is Detection Pack?

Detection Pack is AIPM's comprehensive project intelligence system that provides:

- **Code Quality Analysis** - Cyclomatic complexity, maintainability index, quality scoring
- **Dependency Management** - Dependency graphs, circular dependency detection, coupling metrics
- **Compliance Reporting** - SBOM generation in CycloneDX and SPDX formats
- **Architecture Validation** - Pattern detection (Hexagonal, Layered, DDD, CQRS, MVC)
- **Fitness Testing** - Policy validation, quality gates, architecture governance

### Key Features

| Command | Purpose | Output |
|---------|---------|--------|
| `analyze` | Static code analysis | Complexity, maintainability, quality scores |
| `graph` | Dependency analysis | Import graphs, cycles, coupling metrics |
| `sbom` | Bill of Materials | CycloneDX, SPDX, license summaries |
| `patterns` | Architecture detection | Pattern recognition with confidence scores |
| `fitness` | Policy validation | Architecture fitness tests, violations |

### When to Use Each Command

**Before starting work:**
- `analyze` - Assess current code quality baseline
- `patterns` - Understand existing architecture

**During development:**
- `graph --detect-cycles` - Ensure no circular dependencies
- `fitness` - Validate architecture rules

**Before release:**
- `sbom` - Generate compliance artifacts
- `fitness --fail-on-error` - Gate deployment on quality

**For audits:**
- `sbom --format cyclonedx` - Export for security scanning
- `analyze --output report.md` - Document quality metrics

---

## Getting Started

### Prerequisites

- APM (Agent Project Manager) initialized in your project (`apm init`)
- Python 3.10+ for Python projects
- Source files in your project directory

### Quick Start

Try these three commands to explore your project:

**1. Code Quality Overview**
```bash
apm detect analyze --summary-only
```

**Sample Output:**
```
🔍 Analyzing project: /path/to/project
   Pattern: **/*.py
   Cache: enabled

╭──────────────────────────────────────────────────────────────╮
│ 📊 Project Analysis Summary                                  │
│                                                              │
│ Files Analyzed:    739                                       │
│ Total Lines:       211,284                                   │
│ Code Lines:        112,760                                   │
│ Quality Score:     51.9/100 (Grade: F)                       │
╰──────────────────────────────────────────────────────────────╯
```

**2. Architecture Patterns**
```bash
apm detect patterns
```

**Sample Output:**
```
🔍 Analyzing architecture patterns in: /path/to/project

╭────────────────────── Analysis Summary ──────────────────────╮
│ Primary Pattern: HEXAGONAL                                   │
╰──────────────────────────────────────────────────────────────╯

                    Detected Patterns
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern              ┃ Confidence ┃  Status  ┃ Violations ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Hexagonal            │       100% │  ✓ High  │     0      │
│ Layered              │       100% │  ✓ High  │     0      │
│ Mvc                  │       100% │  ✓ High  │     0      │
│ Cqrs                 │        50% │ ~ Medium │     0      │
│ Domain Driven Design │         0% │  ✗ Low   │     0      │
└──────────────────────┴────────────┴──────────┴────────────┘
```

**3. License Summary**
```bash
apm detect sbom --licenses-only
```

**Sample Output:**
```
         📜 License Summary
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ License      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ MIT          │     7 │      58.3% │
│ BSD-3-Clause │     3 │      25.0% │
│ Apache-2.0   │     1 │       8.3% │
│ 0BSD         │     1 │       8.3% │
├──────────────┼───────┼────────────┤
│ Total        │    12 │       100% │
└──────────────┴───────┴────────────┘
```

---

## Command Reference

### apm detect analyze

Perform comprehensive static code analysis to extract metrics, complexity, maintainability scores, and quality grades.

#### Purpose

Analyze source files to identify:
- Code metrics (LOC, functions, classes)
- Cyclomatic complexity per function/method
- Maintainability index (0-100 scale)
- Overall quality scores (A-F grading)

#### Usage

**Basic Syntax:**
```bash
apm detect analyze [PROJECT_PATH] [OPTIONS]
```

**Common Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--no-cache` | Force re-analysis, ignore cache | Cache enabled |
| `--format` | Output format: table, json, yaml, markdown | table |
| `--pattern` | File glob pattern | `**/*.py` |
| `--complexity-threshold` | Complexity warning threshold | 10 |
| `--maintainability-threshold` | Maintainability warning threshold | 65.0 |
| `--top N` | Show top N worst files | all |
| `--output FILE` | Save results to file | stdout |
| `--verbose` | Show per-file detailed stats | false |
| `--summary-only` | Show summary only | false |

#### Quality Thresholds

**Cyclomatic Complexity:**
- **Good**: <10 (simple, easy to test)
- **Warning**: 10-15 (moderately complex)
- **Poor**: >15 (high complexity, refactor recommended)

**Maintainability Index (MI):**
- **Excellent**: >85 (highly maintainable)
- **Good**: 65-84 (adequately maintainable)
- **Needs Work**: <65 (difficult to maintain)

**Quality Score:**
- **A**: 90+ (excellent)
- **B**: 80-89 (good)
- **C**: 70-79 (fair)
- **D**: 60-69 (poor)
- **F**: <60 (failing)

#### Examples

**Example 1: Basic Project Analysis**
```bash
apm detect analyze
```

**Output:**
```
🔍 Analyzing project: /path/to/project
   Pattern: **/*.py
   Cache: enabled

╭──────────────────────────────────────────────────────────────╮
│ 📊 Project Analysis Summary                                  │
│                                                              │
│ Files Analyzed:    156                                       │
│ Total Lines:       45,892                                    │
│ Code Lines:        28,445                                    │
│ Quality Score:     72.3/100 (Grade: C)                       │
╰──────────────────────────────────────────────────────────────╯

           📈 Code Metrics
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Metric              ┃  Value ┃  Avg  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ Functions           │  1,245 │  7.98 │
│ Classes             │    342 │  2.19 │
│ Avg Complexity      │   4.23 │   -   │
│ Avg Maintainability │  68.45 │   -   │
└─────────────────────┴────────┴───────┘
```

**Example 2: Find Top 10 Most Complex Files**
```bash
apm detect analyze --top 10 --complexity-threshold 15
```

**Output:**
```
         🔥 Top 10 Files by Complexity
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ File                        ┃ Complexity ┃ Maintainability ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ core/workflow/engine.py     │       42   │      45.2      │
│ core/rules/validator.py     │       38   │      52.8      │
│ cli/commands/detect.py      │       35   │      58.4      │
│ core/context/analyzer.py    │       32   │      61.7      │
└─────────────────────────────┴────────────┴────────────────┘

⚠️  4 files exceed complexity threshold (15)
```

**Example 3: Export JSON Report**
```bash
apm detect analyze --format json --output quality-report.json
```

**Example 4: Detailed Per-File Analysis**
```bash
apm detect analyze --verbose --pattern "core/**/*.py"
```

**Output:**
```
         📄 File-Level Analysis
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ File                  ┃ LOC  ┃ Classes ┃ Funcs ┃ Complexity    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━┩
│ core/models.py        │  245 │     12  │   45  │ 8.2 (Good)    │
│ core/service.py       │  189 │      3  │   28  │ 12.5 (Warning)│
│ core/repository.py    │  156 │      5  │   22  │ 6.1 (Good)    │
└───────────────────────┴──────┴─────────┴───────┴───────────────┘
```

**Example 5: Markdown Report for Documentation**
```bash
apm detect analyze --format markdown --output docs/quality-report.md
```

#### Use Cases

- **Pre-Work Item Analysis**: Establish baseline before new features
- **Code Review Preparation**: Identify high-complexity areas needing attention
- **Refactoring Targets**: Find maintainability hotspots
- **Quality Tracking**: Historical trend analysis (store results in AIPM database)
- **Technical Debt Assessment**: Quantify code quality for stakeholders

---

### apm detect graph

Analyze project dependency graph to understand module relationships, detect circular dependencies, and measure coupling.

#### Purpose

Build and analyze dependency graphs showing:
- Import relationships between modules
- Circular dependencies (cycles)
- Coupling metrics (afferent/efferent coupling)
- Root modules (no incoming dependencies)
- Leaf modules (no outgoing dependencies)

#### Usage

**Basic Syntax:**
```bash
apm detect graph [PROJECT_PATH] [OPTIONS]
```

**Common Options:**

| Option | Description |
|--------|-------------|
| `--rebuild` | Force rebuild, ignore cache |
| `--detect-cycles` | Detect and report circular dependencies |
| `--cycles-only` | Show only cycles (skip other metrics) |
| `--visualize` | Generate Graphviz DOT file visualization |
| `--output PATH` | Output file for visualization or export |
| `--highlight-cycles` | Highlight cycles in red (use with --visualize) |
| `--module TEXT` | Analyze specific module |
| `--coupling` | Show coupling metrics table |
| `--root-modules` | Show modules with no incoming dependencies |
| `--leaf-modules` | Show modules with no outgoing dependencies |
| `--all` | Show all modules in coupling table (not just top 20) |
| `--format` | Output format: table, json, yaml |

#### Examples

**Example 1: Basic Dependency Graph Stats**
```bash
apm detect graph
```

**Output:**
```
🔍 Building dependency graph for: /path/to/project

╭────────────────── Dependency Graph Summary ──────────────────╮
│ Total Modules:        342                                    │
│ Total Dependencies:   1,248                                  │
│ Circular Dependencies: 0                                     │
│ Root Modules:         12                                     │
│ Leaf Modules:         45                                     │
╰──────────────────────────────────────────────────────────────╯

✅ No circular dependencies detected
```

**Example 2: Detect Circular Dependencies**
```bash
apm detect graph --detect-cycles
```

**Output (with cycles):**
```
🔍 Analyzing dependencies for cycles...

╭────────────────── Circular Dependencies Found ───────────────╮
│ Total Cycles: 3                                              │
╰──────────────────────────────────────────────────────────────╯

         🔄 Cycle 1 (3 modules)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Module Path                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ core/models.py                        │
│ → core/services.py                    │
│ → core/repositories.py                │
│ → core/models.py (cycle)              │
└───────────────────────────────────────┘

⚠️  Recommendation: Refactor to break circular imports
```

**Output (no cycles):**
```
✅ No circular dependencies detected

👍 Healthy dependency structure
```

**Example 3: Coupling Metrics**
```bash
apm detect graph --coupling
```

**Output:**
```
           📊 Coupling Metrics (Top 20)
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Module                 ┃   Ca  ┃   Ce  ┃ Stability┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ core/models.py         │   45  │    3  │   0.06   │
│ core/services.py       │   28  │   12  │   0.30   │
│ core/repositories.py   │   18  │    8  │   0.31   │
│ api/views.py           │   12  │   24  │   0.67   │
│ cli/commands.py        │    5  │   32  │   0.86   │
└────────────────────────┴───────┴───────┴──────────┘

Legend:
  Ca (Afferent Coupling)  - Incoming dependencies
  Ce (Efferent Coupling)  - Outgoing dependencies
  Stability = Ce / (Ca + Ce)

Interpretation:
  0.0 - 0.3  Very stable (used by many)
  0.3 - 0.7  Balanced
  0.7 - 1.0  Very unstable (depends on many)
```

**Example 4: Visualize Dependencies**
```bash
apm detect graph --visualize --output dependencies.dot
```

**Output:**
```
🔍 Building dependency graph...
📊 Generating Graphviz visualization...

✅ Visualization saved to: dependencies.dot

To render:
  dot -Tpng dependencies.dot -o dependencies.png
  dot -Tsvg dependencies.dot -o dependencies.svg
```

**Example 5: Highlight Cycles in Visualization**
```bash
apm detect graph --visualize --highlight-cycles --output deps.dot
```

**Example 6: Analyze Specific Module**
```bash
apm detect graph --module core/services.py
```

**Output:**
```
🔍 Analyzing module: core/services.py

╭─────────────── Module Analysis ───────────────╮
│ Imports From:         12 modules              │
│ Imported By:          28 modules              │
│ Stability:            0.30 (stable)           │
╰───────────────────────────────────────────────╯

         📥 Dependencies (12)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Imports                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ core/models.py                    │
│ core/repositories.py              │
│ core/exceptions.py                │
└───────────────────────────────────┘

         📤 Dependents (28)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Imported By                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ api/views.py                     │
│ cli/commands.py                  │
│ web/controllers.py               │
└──────────────────────────────────┘
```

**Example 7: Find Root Modules**
```bash
apm detect graph --root-modules
```

**Output:**
```
         🌳 Root Modules (12)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Module (No Incoming Dependencies)┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ core/models.py                   │
│ core/constants.py                │
│ core/types.py                    │
└──────────────────────────────────┘

💡 Root modules are foundational - changes affect many modules
```

**Example 8: JSON Export for Automation**
```bash
apm detect graph --detect-cycles --format json --output graph.json
```

#### Use Cases

- **Architecture Review**: Understand module organization and coupling
- **Refactoring Planning**: Identify high-coupling modules
- **Circular Dependency Detection**: Find and eliminate import cycles
- **Impact Analysis**: Determine blast radius of changes
- **Documentation**: Generate visual dependency maps

---

### apm detect sbom

Generate Software Bill of Materials (SBOM) in industry-standard formats for security, compliance, and license auditing.

#### Purpose

Create SBOM artifacts including:
- All project dependencies (direct and transitive)
- License information for each component
- Package metadata (version, description, homepage)
- Dependency tree relationships

Supports industry standards:
- **CycloneDX 1.5** (JSON/XML) - OWASP standard
- **SPDX 2.3** (JSON) - Linux Foundation standard

#### Usage

**Basic Syntax:**
```bash
apm detect sbom [PROJECT_PATH] [OPTIONS]
```

**Common Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | SBOM format: cyclonedx, cyclonedx-xml, spdx, json, table | table |
| `--output PATH` | Save to file | stdout |
| `--include-dev` | Include development dependencies | false |
| `--skip-licenses` | Skip license detection (faster) | false |
| `--licenses-only` | Show only license summary | false |
| `--license TEXT` | Filter by specific license (e.g., MIT) | all |
| `--exclude-license TEXT` | Exclude specific license (e.g., GPL-3.0) | none |
| `--runtime-only` | Exclude dev dependencies | false |
| `--limit INTEGER` | Limit table display (doesn't affect file export) | 50 |

#### Standard Formats

**Table Display** (default for console):
```bash
apm detect sbom
```

**CycloneDX JSON** (most common):
```bash
apm detect sbom --format cyclonedx --output sbom.json
```

**CycloneDX XML**:
```bash
apm detect sbom --format cyclonedx-xml --output sbom.xml
```

**SPDX JSON**:
```bash
apm detect sbom --format spdx --output sbom.spdx.json
```

#### Examples

**Example 1: Quick License Overview**
```bash
apm detect sbom --licenses-only
```

**Output:**
```
╭──────────────────── 🔍 SBOM Summary ─────────────────────╮
│ Project: my-project                                      │
│ Version: 1.2.3                                           │
│ Generated: 2025-10-24 15:31:57                           │
│ Total Components: 124                                    │
╰──────────────────────────────────────────────────────────╯

         📜 License Summary
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ License      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ MIT          │    78 │      62.9% │
│ Apache-2.0   │    24 │      19.4% │
│ BSD-3-Clause │    18 │      14.5% │
│ ISC          │     3 │       2.4% │
│ 0BSD         │     1 │       0.8% │
├──────────────┼───────┼────────────┤
│ Total        │   124 │       100% │
└──────────────┴───────┴────────────┘

✅ No GPL licenses detected
```

**Example 2: Full Component Table**
```bash
apm detect sbom
```

**Output:**
```
╭──────────────────── 🔍 SBOM Summary ─────────────────────╮
│ Project: my-project                                      │
│ Version: 1.2.3                                           │
│ Generated: 2025-10-24 15:35:12                           │
│ Total Components: 124                                    │
╰──────────────────────────────────────────────────────────╯

         📜 License Summary
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ License      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ MIT          │    78 │      62.9% │
│ Apache-2.0   │    24 │      19.4% │
│ BSD-3-Clause │    18 │      14.5% │
│ ISC          │     3 │       2.4% │
│ 0BSD         │     1 │       0.8% │
└──────────────┴───────┴────────────┘

       📦 Components (124) (showing first 50)
┏━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Component    ┃ Version  ┃ License      ┃ Type    ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ click        │ 8.1.7    │ BSD-3-Clause │ library │
│ rich         │ 13.7.0   │ MIT          │ library │
│ pydantic     │ 2.5.0    │ MIT          │ library │
│ pyyaml       │ 6.0.0    │ MIT          │ library │
│ questionary  │ 2.0.0    │ MIT          │ library │
│ sqlalchemy   │ 2.0.23   │ MIT          │ library │
│ pytest       │ 7.4.3    │ MIT          │ library │
│ black        │ 23.11.0  │ MIT          │ library │
└──────────────┴──────────┴──────────────┴─────────┘

💡 Use --limit N to show more components
```

**Example 3: Generate CycloneDX SBOM for Security Scanning**
```bash
apm detect sbom --format cyclonedx --output sbom-cyclonedx.json
```

**Output:**
```
🔍 Generating SBOM for: /path/to/project
📋 Format: CycloneDX 1.5 JSON
📦 Components: 124

✅ SBOM generated: sbom-cyclonedx.json

📤 Next Steps:
  - Upload to Dependency-Track: https://dependencytrack.org
  - Scan with OWASP tools
  - Store in artifact repository
```

**Example 4: Generate SPDX SBOM**
```bash
apm detect sbom --format spdx --output sbom.spdx.json
```

**Example 5: Filter GPL Licenses (Compliance Check)**
```bash
apm detect sbom --exclude-license GPL-3.0 --exclude-license AGPL-3.0
```

**Output:**
```
╭──────────────────── 🔍 SBOM Summary ─────────────────────╮
│ Filtered: Excluding GPL-3.0, AGPL-3.0                    │
│ Total Components: 121 (3 excluded)                       │
╰──────────────────────────────────────────────────────────╯

✅ No GPL licenses in filtered results
```

**Example 6: Find MIT-Licensed Packages**
```bash
apm detect sbom --license MIT
```

**Example 7: Include Dev Dependencies**
```bash
apm detect sbom --include-dev --licenses-only
```

**Output:**
```
         📜 License Summary (All Dependencies)
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ License      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ MIT          │   156 │      68.1% │
│ Apache-2.0   │    42 │      18.3% │
│ BSD-3-Clause │    28 │      12.2% │
│ ISC          │     3 │       1.3% │
├──────────────┼───────┼────────────┤
│ Total        │   229 │       100% │
└──────────────┴───────┴────────────┘

ℹ️  Includes 105 development dependencies
```

**Example 8: Runtime Dependencies Only**
```bash
apm detect sbom --runtime-only --format cyclonedx --output runtime-sbom.json
```

#### Use Cases

- **Security Audits**: Generate SBOM for vulnerability scanning
- **License Compliance**: Verify acceptable licenses before release
- **Supply Chain Security**: Track all dependencies
- **Contract Compliance**: Provide SBOM to clients/partners
- **SBOM Repository**: Store versioned SBOMs for historical tracking
- **Dependency Analysis**: Understand transitive dependencies

---

### apm detect patterns

Detect architecture patterns in your codebase with confidence scores and supporting evidence.

#### Purpose

Recognize common architecture patterns:
- **Hexagonal** (Ports & Adapters)
- **Layered** (N-tier architecture)
- **Domain-Driven Design** (DDD)
- **CQRS** (Command Query Responsibility Segregation)
- **MVC** (Model-View-Controller)

Provides:
- Confidence scores (0-100%)
- Supporting evidence for detection
- Pattern violations
- Architecture recommendations

#### Usage

**Basic Syntax:**
```bash
apm detect patterns [PROJECT_PATH] [OPTIONS]
```

**Common Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--confidence FLOAT` | Minimum confidence threshold (0.0-1.0) | 0.0 |
| `--format` | Output format: table, json, yaml | table |
| `--output PATH` | Save results to file | stdout |
| `--show-evidence` | Show supporting evidence | false |
| `--show-violations` | Show pattern violations | false |

#### Examples

**Example 1: Basic Pattern Detection**
```bash
apm detect patterns
```

**Output:**
```
🔍 Analyzing architecture patterns in: /path/to/project

╭────────────────── Analysis Summary ──────────────────╮
│ Primary Pattern: HEXAGONAL                           │
╰──────────────────────────────────────────────────────╯

                  Detected Patterns
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern              ┃ Confidence ┃  Status  ┃ Violations ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Hexagonal            │       100% │  ✓ High  │     0      │
│ Layered              │       100% │  ✓ High  │     0      │
│ Mvc                  │       100% │  ✓ High  │     0      │
│ Cqrs                 │        50% │ ~ Medium │     0      │
│ Domain Driven Design │         0% │  ✗ Low   │     0      │
└──────────────────────┴────────────┴──────────┴────────────┘

Recommendations:
  • Multiple patterns detected: hexagonal, layered, mvc
    Consider consolidating to single primary pattern for consistency
  • Hexagonal architecture well-implemented
    Consider adding domain events for better decoupling
```

**Example 2: Show Evidence**
```bash
apm detect patterns --show-evidence
```

**Output:**
```
🔍 Analyzing architecture patterns in: /path/to/project

╭────────────────── Analysis Summary ──────────────────╮
│ Primary Pattern: HEXAGONAL                           │
╰──────────────────────────────────────────────────────╯

                  Detected Patterns
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern              ┃ Confidence ┃  Status  ┃ Violations ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Hexagonal            │       100% │  ✓ High  │     0      │
│ Layered              │       100% │  ✓ High  │     0      │
│ Mvc                  │       100% │  ✓ High  │     0      │
└──────────────────────┴────────────┴──────────┴────────────┘

Evidence:

HEXAGONAL (100%)
  • Port interfaces detected:
    - core/ports/repository.py
    - core/ports/service.py
  • Adapter implementations detected:
    - adapters/sqlite/repository.py
    - adapters/web/controllers.py
  • Domain core isolated from infrastructure

LAYERED (100%)
  • Presentation layer found:
    - web/views/
    - api/endpoints/
  • Application layer found:
    - core/services/
    - core/use_cases/
  • Domain layer found:
    - core/models/
    - core/domain/
  • Data layer found:
    - core/repositories/
    - adapters/sqlite/

MVC (100%)
  • Models detected:
    - core/models/
  • Views detected:
    - web/templates/
    - api/serializers/
  • Controllers detected:
    - web/controllers/
    - api/views/
```

**Example 3: High-Confidence Only**
```bash
apm detect patterns --confidence 0.7
```

**Output:**
```
                  Detected Patterns (≥70%)
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern              ┃ Confidence ┃  Status  ┃ Violations ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Hexagonal            │       100% │  ✓ High  │     0      │
│ Layered              │       100% │  ✓ High  │     0      │
│ Mvc                  │        85% │  ✓ High  │     0      │
└──────────────────────┴────────────┴──────────┴────────────┘

ℹ️  3 patterns meet confidence threshold (≥70%)
```

**Example 4: Show Violations**
```bash
apm detect patterns --show-violations
```

**Output:**
```
                  Detected Patterns
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Pattern              ┃ Confidence ┃  Status  ┃ Violations ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Hexagonal            │        80% │  ✓ High  │     2      │
│ Layered              │        65% │ ~ Medium │     5      │
└──────────────────────┴────────────┴──────────┴────────────┘

Violations:

HEXAGONAL (2 violations)
  ⚠️  Domain depends on infrastructure:
    - core/models.py imports adapters/sqlite/base.py
    - core/services.py imports web/auth.py

LAYERED (5 violations)
  ⚠️  Layer boundary violations:
    - Presentation → Data (skipping Application layer):
      * web/controllers.py → core/repositories.py
    - Data → Presentation (reversed dependency):
      * core/repositories.py → web/auth.py
```

**Example 5: JSON Export**
```bash
apm detect patterns --format json --output patterns.json
```

**Example 6: Full Analysis Report**
```bash
apm detect patterns --show-evidence --show-violations --output patterns-report.md --format markdown
```

#### Use Cases

- **Architecture Assessment**: Understand current architecture patterns
- **Onboarding**: Help new developers understand project structure
- **Architecture Migration**: Measure progress toward target pattern
- **Quality Gates**: Ensure pattern compliance (use with fitness)
- **Documentation**: Auto-generate architecture documentation

---

### apm detect fitness

Run architecture fitness tests to validate project against architecture policies and quality gates.

#### Purpose

Validate project health:
- **No circular dependencies** (structural integrity)
- **Complexity limits** (maintainability)
- **Layering rules** (architecture boundaries)
- **Code standards** (quality baselines)

Provides:
- Pass/fail status for each policy
- Violation details with severity (ERROR, WARNING, INFO)
- Fix suggestions for failures
- CI/CD-friendly exit codes

#### Usage

**Basic Syntax:**
```bash
apm detect fitness [PROJECT_PATH] [OPTIONS]
```

**Common Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--policy-set TEXT` | Policy set to use | default |
| `--fail-on-error` | Exit code 1 if violations found | false |
| `--format` | Output format: table, json, yaml | table |
| `--errors-only` | Show ERROR level violations only | false |
| `--warnings-only` | Show WARNING level violations only | false |
| `--show-suggestions` | Include fix suggestions | false |
| `--output PATH` | Save results to file | stdout |

**Exit Codes:**
- `0` - All tests passed (or `--fail-on-error` not set)
- `1` - Violations found with `--fail-on-error`

#### Examples

**Example 1: Basic Fitness Check**
```bash
apm detect fitness
```

**Output (passing):**
```
🏋️  Running architecture fitness tests...
📋 Policy Set: default

╭────────────────── Fitness Results ──────────────────╮
│ Tests Run:     12                                   │
│ Passed:        12                                   │
│ Failed:         0                                   │
│ Status:        ✅ HEALTHY                           │
╰─────────────────────────────────────────────────────╯

                  Policy Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Policy                    ┃  Status   ┃ Details ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ No Circular Dependencies  │ ✅ PASS   │ 0 cycles│
│ Complexity Limits         │ ✅ PASS   │ max: 12 │
│ Maintainability Threshold │ ✅ PASS   │ min: 68 │
│ Layering Rules            │ ✅ PASS   │ 0 viol. │
│ Code Standards            │ ✅ PASS   │ clean   │
└───────────────────────────┴───────────┴─────────┘

🎉 All fitness tests passed!
```

**Output (with violations):**
```
🏋️  Running architecture fitness tests...
📋 Policy Set: default

╭────────────────── Fitness Results ──────────────────╮
│ Tests Run:     12                                   │
│ Passed:         9                                   │
│ Failed:         3                                   │
│ Status:        ⚠️  NEEDS WORK                       │
╰─────────────────────────────────────────────────────╯

                  Policy Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Policy                    ┃  Status   ┃ Details ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ No Circular Dependencies  │ ❌ FAIL   │ 3 cycles│
│ Complexity Limits         │ ⚠️  WARN  │ max: 42 │
│ Maintainability Threshold │ ✅ PASS   │ min: 68 │
│ Layering Rules            │ ❌ FAIL   │ 5 viol. │
│ Code Standards            │ ✅ PASS   │ clean   │
└───────────────────────────┴───────────┴─────────┘

⚠️  3 policies failed, 1 warning
```

**Example 2: CI/CD Mode (Fail on Error)**
```bash
apm detect fitness --fail-on-error
```

**Output:**
```
🏋️  Running architecture fitness tests...

❌ 3 violations found - build failed

Exit code: 1
```

**Usage in CI:**
```yaml
# .github/workflows/quality.yml
- name: Architecture Fitness Tests
  run: apm detect fitness --fail-on-error
```

**Example 3: Errors Only**
```bash
apm detect fitness --errors-only
```

**Output:**
```
         ❌ ERROR Level Violations
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Policy                   ┃ Violation           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ No Circular Dependencies │ 3 circular imports  │
│ Layering Rules           │ 5 boundary breaks   │
└──────────────────────────┴─────────────────────┘

ℹ️  2 ERROR level violations (blocking)
```

**Example 4: Show Fix Suggestions**
```bash
apm detect fitness --show-suggestions
```

**Output:**
```
                  Policy Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Policy                    ┃  Status   ┃ Details ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ No Circular Dependencies  │ ❌ FAIL   │ 3 cycles│
└───────────────────────────┴───────────┴─────────┘

💡 Suggestions:

No Circular Dependencies (3 violations)
  Cycle 1:
    • Break cycle: core/models.py → core/services.py → core/models.py
    • Solution: Move shared types to core/types.py
    • Example:
      # core/types.py
      from typing import Protocol

      class ServiceProtocol(Protocol):
          def process(self) -> Result: ...

  Cycle 2:
    • Break cycle: api/views.py → api/serializers.py → api/views.py
    • Solution: Use forward references or move to separate module

  Cycle 3:
    • Break cycle: web/auth.py → web/session.py → web/auth.py
    • Solution: Extract shared auth types to web/auth/types.py
```

**Example 5: Warnings Only**
```bash
apm detect fitness --warnings-only
```

**Output:**
```
         ⚠️  WARNING Level Violations
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Policy               ┃ Violation               ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Complexity Limits    │ 8 functions exceed 15   │
│ Function Length      │ 3 functions >100 lines  │
└──────────────────────┴─────────────────────────┘

ℹ️  2 WARNING level violations (non-blocking)
```

**Example 6: JSON Export for Tracking**
```bash
apm detect fitness --format json --output fitness-report.json
```

**Example 7: Custom Policy Set**
```bash
apm detect fitness --policy-set strict
```

**Output:**
```
🏋️  Running architecture fitness tests...
📋 Policy Set: strict (16 policies)

╭────────────────── Fitness Results ──────────────────╮
│ Tests Run:     16                                   │
│ Passed:        14                                   │
│ Failed:         2                                   │
│ Status:        ⚠️  NEEDS WORK                       │
╰─────────────────────────────────────────────────────╯

ℹ️  Strict policy set enforces higher standards
```

#### Use Cases

- **Quality Gates**: Block merges/deployments on policy violations
- **Continuous Validation**: Run in CI/CD pipeline
- **Architecture Governance**: Enforce architecture decisions
- **Refactoring Guidance**: Identify areas needing improvement
- **Technical Debt Tracking**: Measure improvement over time

---

## Common Workflows

### Workflow 1: Quality Check Before Work Item

**Goal**: Establish baseline before starting new feature work.

```bash
# Step 1: Overall quality baseline
apm detect analyze --summary-only

# Step 2: Check for existing issues
apm detect fitness

# Step 3: Understand architecture
apm detect patterns

# Step 4: Check for circular dependencies
apm detect graph --detect-cycles
```

**Result**: Baseline metrics documented for comparison after implementation.

---

### Workflow 2: Compliance Audit

**Goal**: Generate compliance artifacts for security audit.

```bash
# Step 1: Generate CycloneDX SBOM
apm detect sbom --format cyclonedx --output sbom-cyclonedx.json

# Step 2: Generate SPDX SBOM
apm detect sbom --format spdx --output sbom.spdx.json

# Step 3: License compliance check
apm detect sbom --exclude-license GPL-3.0 --exclude-license AGPL-3.0

# Step 4: Export for security scanning
# Upload sbom-cyclonedx.json to Dependency-Track or similar
```

**Result**: Industry-standard SBOM files for compliance reporting.

---

### Workflow 3: Architecture Review

**Goal**: Document and validate architecture for team/stakeholders.

```bash
# Step 1: Detect patterns
apm detect patterns --show-evidence --format markdown --output architecture-patterns.md

# Step 2: Visualize dependencies
apm detect graph --visualize --output dependencies.dot
dot -Tpng dependencies.dot -o dependencies.png

# Step 3: Coupling analysis
apm detect graph --coupling --all --format json --output coupling-metrics.json

# Step 4: Validate fitness
apm detect fitness --show-suggestions --output fitness-report.md --format markdown
```

**Result**: Comprehensive architecture documentation with visuals.

---

### Workflow 4: Dependency Analysis

**Goal**: Find and eliminate circular dependencies, reduce coupling.

```bash
# Step 1: Detect cycles
apm detect graph --detect-cycles --cycles-only

# Step 2: Visualize with highlighted cycles
apm detect graph --visualize --highlight-cycles --output deps-cycles.dot
dot -Tpng deps-cycles.dot -o deps-cycles.png

# Step 3: Analyze coupling of high-risk modules
apm detect graph --module core/services.py

# Step 4: Verify fixes
apm detect fitness --errors-only
```

**Result**: Identified cycles with actionable visualization for refactoring.

---

### Workflow 5: Pre-Release Quality Gate

**Goal**: Ensure quality standards before production deployment.

```bash
# Step 1: Run all fitness tests (fail on error)
apm detect fitness --fail-on-error

# Step 2: Verify no circular dependencies
apm detect graph --detect-cycles --cycles-only

# Step 3: Generate release SBOM
apm detect sbom --runtime-only --format cyclonedx --output release-sbom.json

# Step 4: Quality report
apm detect analyze --format markdown --output release-quality-report.md

# Exit code 0 = pass gate, proceed to deployment
# Exit code 1 = fail gate, block deployment
```

**Result**: Pass/fail gate for automated deployment pipelines.

---

### Workflow 6: Refactoring Targets

**Goal**: Identify high-complexity, low-maintainability files for refactoring.

```bash
# Step 1: Find worst files
apm detect analyze --top 20 --complexity-threshold 15

# Step 2: Detailed analysis
apm detect analyze --verbose --pattern "identified/high/complexity/**/*.py"

# Step 3: Before snapshot
apm detect analyze --format json --output before-refactor.json

# [Perform refactoring]

# Step 4: After snapshot
apm detect analyze --format json --output after-refactor.json

# Step 5: Compare improvement (manual diff or script)
```

**Result**: Prioritized refactoring targets with before/after metrics.

---

## Output Formats

### Table Format (Default)

**Best for**: Console display, human readability

```bash
apm detect analyze
```

**Characteristics:**
- Rich formatting with colors and borders
- Summary statistics highlighted
- Suitable for terminal viewing

---

### JSON Format

**Best for**: Automation, CI/CD, programmatic processing

```bash
apm detect analyze --format json
```

**Example Output:**
```json
{
  "summary": {
    "files_analyzed": 739,
    "total_lines": 211284,
    "code_lines": 112760,
    "quality_score": 51.9,
    "grade": "F"
  },
  "metrics": {
    "functions": 1245,
    "classes": 342,
    "avg_complexity": 4.23,
    "avg_maintainability": 68.45
  },
  "files": [
    {
      "path": "core/service.py",
      "lines": 245,
      "complexity": 12.5,
      "maintainability": 58.4,
      "grade": "D"
    }
  ]
}
```

**Use Cases:**
- Parse results in scripts
- Store in databases
- Generate custom reports
- CI/CD pipeline integration

---

### YAML Format

**Best for**: Configuration-style output, human-readable structured data

```bash
apm detect analyze --format yaml
```

**Example Output:**
```yaml
summary:
  files_analyzed: 739
  total_lines: 211284
  code_lines: 112760
  quality_score: 51.9
  grade: F

metrics:
  functions: 1245
  classes: 342
  avg_complexity: 4.23
  avg_maintainability: 68.45

files:
  - path: core/service.py
    lines: 245
    complexity: 12.5
    maintainability: 58.4
    grade: D
```

---

### Markdown Format

**Best for**: Documentation, reports, embedding in README/docs

```bash
apm detect analyze --format markdown --output report.md
```

**Example Output:**
```markdown
# Project Analysis Report

## Summary

- **Files Analyzed**: 739
- **Total Lines**: 211,284
- **Code Lines**: 112,760
- **Quality Score**: 51.9/100 (Grade: F)

## Metrics

| Metric              | Value |
|---------------------|-------|
| Functions           | 1,245 |
| Classes             | 342   |
| Avg Complexity      | 4.23  |
| Avg Maintainability | 68.45 |

## Top Issues

### core/service.py
- **Lines**: 245
- **Complexity**: 12.5 (Warning)
- **Maintainability**: 58.4 (Needs Work)
- **Grade**: D
```

---

### File Export

**All formats support file output:**

```bash
# JSON to file
apm detect analyze --format json --output analysis.json

# Markdown report
apm detect analyze --format markdown --output quality-report.md

# YAML export
apm detect patterns --format yaml --output patterns.yaml
```

---

## Troubleshooting

### Issue: Slow analysis on large projects

**Symptom:**
```
🔍 Analyzing project: /path/to/large-project
   Pattern: **/*.py
   [Takes 5+ minutes]
```

**Solutions:**

**1. Use cache (enabled by default):**
```bash
apm detect analyze
# Subsequent runs use cache (~10x faster)
```

**2. Narrow pattern:**
```bash
apm detect analyze --pattern "src/**/*.py"  # Exclude tests, docs
```

**3. Analyze specific directories:**
```bash
apm detect analyze /path/to/project/core/
```

**4. Summary only (skip per-file analysis):**
```bash
apm detect analyze --summary-only
```

---

### Issue: Cache not updating after code changes

**Symptom:**
```
Code changed but analysis shows old results
```

**Solution:**
```bash
# Force re-analysis
apm detect analyze --no-cache

# Force graph rebuild
apm detect graph --rebuild
```

---

### Issue: SBOM missing licenses

**Symptom:**
```
📜 License Summary
  Unknown: 45 packages (68%)
```

**Solutions:**

**1. Run without --skip-licenses:**
```bash
apm detect sbom
# (License detection enabled by default)
```

**2. Check package metadata:**
```bash
# Verify package has license info
pip show <package-name>
```

**3. Manually specify licenses** (if package metadata missing):
```bash
# Export SBOM and manually edit JSON
apm detect sbom --format cyclonedx --output sbom.json
# Edit sbom.json to add missing license info
```

---

### Issue: Pattern detection confidence too low

**Symptom:**
```
All patterns show 0-20% confidence
```

**Causes:**
- Non-standard directory structure
- Very small project
- Mixed/inconsistent patterns

**Solutions:**

**1. Use --show-evidence to understand why:**
```bash
apm detect patterns --show-evidence
```

**2. Reorganize to match pattern conventions:**

**Hexagonal:**
```
project/
├── core/
│   ├── domain/        # Business logic
│   └── ports/         # Interfaces
└── adapters/          # Implementations
    ├── api/
    ├── db/
    └── cli/
```

**Layered:**
```
project/
├── presentation/      # UI layer
├── application/       # Use cases
├── domain/            # Business logic
└── infrastructure/    # Data access
```

---

### Issue: Fitness tests failing unexpectedly

**Symptom:**
```
❌ All fitness tests fail
Exit code: 1
```

**Solutions:**

**1. Check specific failures:**
```bash
apm detect fitness --errors-only --show-suggestions
```

**2. Run individual checks:**
```bash
# Check cycles only
apm detect graph --detect-cycles

# Check complexity only
apm detect analyze --complexity-threshold 10
```

**3. Use less strict policy set:**
```bash
apm detect fitness --policy-set lenient
```

---

### Issue: Graph visualization not rendering

**Symptom:**
```
✅ Visualization saved to: dependencies.dot
[Cannot open .dot file]
```

**Solution:**

**Install Graphviz:**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Render to image
dot -Tpng dependencies.dot -o dependencies.png
dot -Tsvg dependencies.dot -o dependencies.svg
```

---

### Issue: Out of memory on large projects

**Symptom:**
```
MemoryError during analysis
```

**Solutions:**

**1. Analyze in chunks:**
```bash
apm detect analyze --pattern "core/**/*.py"
apm detect analyze --pattern "api/**/*.py"
apm detect analyze --pattern "web/**/*.py"
```

**2. Exclude large files:**
```bash
# Use .gitignore-style exclusions
apm detect analyze --pattern "**/*.py" --exclude "**/migrations/**"
```

**3. Increase system memory or use smaller samples**

---

### Issue: Permission denied errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '.aipm/cache'
```

**Solution:**
```bash
# Check .aipm directory permissions
ls -la .aipm/

# Fix permissions
chmod -R u+w .aipm/

# Or run with --no-cache
apm detect analyze --no-cache
```

---

## CI/CD Integration

### GitHub Actions

**Quality Gate Workflow:**

```yaml
# .github/workflows/quality-gate.yml
name: Architecture Quality Gate

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install AIPM
        run: |
          pip install -e .

      - name: Initialize AIPM
        run: |
          apm init "Project" --skip-questionnaire

      - name: Run Fitness Tests
        run: |
          apm detect fitness --fail-on-error --format json --output fitness.json

      - name: Check Circular Dependencies
        run: |
          apm detect graph --detect-cycles --cycles-only

      - name: Code Quality Analysis
        run: |
          apm detect analyze --summary-only

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: quality-reports
          path: |
            fitness.json
            analysis.json
```

**SBOM Generation:**

```yaml
# .github/workflows/sbom.yml
name: Generate SBOM

on:
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install AIPM
        run: pip install -e .

      - name: Generate CycloneDX SBOM
        run: |
          apm init "Project" --skip-questionnaire
          apm detect sbom --runtime-only --format cyclonedx --output sbom-cyclonedx.json

      - name: Generate SPDX SBOM
        run: |
          apm detect sbom --runtime-only --format spdx --output sbom.spdx.json

      - name: Upload SBOM Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: sbom-${{ github.ref_name }}
          path: |
            sbom-cyclonedx.json
            sbom.spdx.json

      - name: Attach to Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            sbom-cyclonedx.json
            sbom.spdx.json
```

---

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - quality
  - sbom

quality_gate:
  stage: quality
  image: python:3.11
  script:
    - pip install -e .
    - apm init "Project" --skip-questionnaire
    - apm detect fitness --fail-on-error
    - apm detect graph --detect-cycles
    - apm detect analyze --format json --output quality-report.json
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: quality-report.json
    paths:
      - quality-report.json
  only:
    - merge_requests
    - main

generate_sbom:
  stage: sbom
  image: python:3.11
  script:
    - pip install -e .
    - apm init "Project" --skip-questionnaire
    - apm detect sbom --runtime-only --format cyclonedx --output sbom.json
  artifacts:
    paths:
      - sbom.json
  only:
    - tags
```

---

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'pip install -e .'
                sh 'apm init "Project" --skip-questionnaire'
            }
        }

        stage('Quality Gate') {
            steps {
                sh 'apm detect fitness --fail-on-error --format json --output fitness.json'
                sh 'apm detect graph --detect-cycles'
                sh 'apm detect analyze --format json --output analysis.json'
            }
        }

        stage('SBOM') {
            when {
                branch 'main'
            }
            steps {
                sh 'apm detect sbom --format cyclonedx --output sbom.json'
                archiveArtifacts artifacts: 'sbom.json', fingerprint: true
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.json', fingerprint: true
            publishHTML(target: [
                reportDir: '.',
                reportFiles: 'fitness.json',
                reportName: 'Fitness Report'
            ])
        }
    }
}
```

---

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: aipm-fitness
        name: AIPM Fitness Tests
        entry: apm detect fitness --fail-on-error --errors-only
        language: system
        pass_filenames: false

      - id: aipm-cycles
        name: Check Circular Dependencies
        entry: apm detect graph --detect-cycles --cycles-only
        language: system
        pass_filenames: false
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

---

## Summary

The Detection Pack provides 5 essential commands for project intelligence:

1. **analyze** - Code quality metrics and complexity analysis
2. **graph** - Dependency graphs and circular dependency detection
3. **sbom** - Software Bill of Materials for compliance
4. **patterns** - Architecture pattern recognition
5. **fitness** - Policy validation and quality gates

**Key Workflows:**
- Quality baseline before work items
- Compliance auditing (SBOM generation)
- Architecture reviews and validation
- Dependency analysis and cleanup
- Pre-release quality gates

**Integration Points:**
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
- Pre-commit hooks
- Quality gate enforcement
- Historical trend tracking (via AIPM database)

**Next Steps:**
- Run `apm detect --help` for command overview
- Try the [Quick Start](#getting-started) examples
- Integrate fitness tests into your CI/CD pipeline
- Generate SBOM for security audits

---

**Version**: 2.0
**Last Updated**: 2025-10-24
**Feedback**: Report issues or suggest improvements in AIPM repository
