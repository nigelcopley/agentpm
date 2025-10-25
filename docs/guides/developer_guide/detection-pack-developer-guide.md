# Detection Pack Developer Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-24
**Audience**: Developers extending or maintaining the Detection Pack
**Reading Time**: 30-40 minutes

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Layer 1: Shared Utilities](#layer-1-shared-utilities)
4. [Layer 2: Database Models](#layer-2-database-models)
5. [Layer 3: Detection Services](#layer-3-detection-services)
6. [Adding New Features](#adding-new-features)
7. [Testing Guidelines](#testing-guidelines)
8. [Performance Considerations](#performance-considerations)
9. [Common Patterns](#common-patterns)

---

## Introduction

The Detection Pack is APM (Agent Project Manager)'s comprehensive code analysis system. It provides five core capabilities:

1. **Static Analysis** - Code metrics, complexity, maintainability
2. **Dependency Graphs** - Import relationships, circular dependencies, coupling
3. **SBOM Generation** - Software Bill of Materials with license detection
4. **Pattern Recognition** - Architecture pattern detection (Hexagonal, DDD, CQRS, etc.)
5. **Fitness Testing** - Policy-based architecture validation

### Design Principles

The Detection Pack follows a strict three-layer architecture:

- **Layer 1 (Utilities)**: Shared, reusable primitives (AST parsing, graph building, metrics)
- **Layer 2 (Database)**: Pydantic models for type safety and validation
- **Layer 3 (Services)**: Business logic orchestration using Layer 1 utilities

**Key Rules**:
- Layer 1 has NO dependencies on Layers 2 or 3
- Layer 3 services use ONLY Layer 1 utilities (never call each other)
- Database models are shared across all layers
- No circular dependencies between layers

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 3: Detection Services              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Static     │  │  Dependency  │  │    SBOM      │     │
│  │  Analysis    │  │    Graph     │  │   Service    │     │
│  │   Service    │  │   Service    │  └──────────────┘     │
│  └──────────────┘  └──────────────┘                        │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Pattern    │  │   Fitness    │                        │
│  │ Recognition  │  │    Engine    │                        │
│  │   Service    │  └──────────────┘                        │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│              Layer 2: Database Models (Pydantic)            │
│  FileAnalysis │ ProjectAnalysis │ SBOM │ PatternMatch      │
│  DependencyGraphAnalysis │ FitnessResult │ Policy           │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│                  Layer 1: Shared Utilities                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  ast_utils   │  │    graph_    │  │   metrics_   │     │
│  │              │  │   builders   │  │  calculator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   pattern_   │  │    file_     │                        │
│  │   matchers   │  │   parsers    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Request
    ↓
CLI Command (apm detect analyze)
    ↓
Detection Service (Layer 3)
    ↓
Layer 1 Utilities (AST, Graphs, Metrics)
    ↓
Pydantic Models (Layer 2)
    ↓
JSON/Database Storage
```

### Design Patterns

1. **Service Pattern**: Layer 3 services orchestrate Layer 1 utilities
2. **Stateless Services**: Services hold no mutable state (caching is isolated)
3. **Pydantic Models**: Type safety and validation at model boundaries
4. **Lazy Loading**: Services lazy-load dependencies (analysis_service, graph_service)
5. **Graceful Degradation**: Return partial results on error, never fail completely

---

## Layer 1: Shared Utilities

Layer 1 utilities are pure functions with NO dependencies on plugins or services. They can be used by ANY higher layer.

### ast_utils.py - AST Parsing Primitives

**Purpose**: Safe Python AST parsing and extraction.

**Location**: `agentpm/utils/ast_utils.py`

**Key Functions**:

#### parse_python_ast(file_path: Path) → Optional[ast.AST]

Parse Python file to AST tree safely.

```python
from pathlib import Path
from agentpm.utils.ast_utils import parse_python_ast

# Parse file
tree = parse_python_ast(Path("example.py"))
if tree:
    print("Successfully parsed")
else:
    print("Parse failed (syntax error or file too large)")
```

**Features**:
- Uses `ast.parse()` only (no `eval()` or `exec()`)
- Handles syntax errors gracefully (returns None)
- Skips files larger than 10MB
- Target performance: <100ms per file

#### extract_imports(tree: ast.AST) → List[str]

Extract all import statements.

```python
import ast
from agentpm.utils.ast_utils import extract_imports

code = '''
import os
from pathlib import Path
from typing import List, Dict
'''
tree = ast.parse(code)
imports = extract_imports(tree)
print(sorted(imports))
# Output: ['os', 'pathlib', 'typing']
```

#### extract_classes(tree: ast.AST, file_path: Path) → List[Dict[str, Any]]

Extract class definitions with metadata.

```python
from agentpm.utils.ast_utils import extract_classes

classes = extract_classes(tree, Path("example.py"))
for cls in classes:
    print(f"{cls['name']}: {len(cls['methods'])} methods")
    print(f"  Bases: {cls['bases']}")
    print(f"  Decorators: {cls['decorators']}")
```

**Returns**:
```python
{
    'name': 'ClassName',
    'bases': ['BaseClass'],
    'line_number': 10,
    'end_line': 50,
    'methods': ['method1', 'method2'],
    'decorators': ['dataclass']
}
```

#### extract_functions(tree: ast.AST, file_path: Path) → List[Dict[str, Any]]

Extract function definitions with complexity.

```python
from agentpm.utils.ast_utils import extract_functions

functions = extract_functions(tree, Path("example.py"))
for func in functions:
    print(f"{func['name']}: complexity={func['complexity']}")
    if func['is_async']:
        print("  (async function)")
```

#### calculate_complexity(node: ast.FunctionDef) → int

Calculate cyclomatic complexity for a function.

**Complexity Formula**:
- Base: 1
- +1 for each: if, elif, while, for, except
- +1 for each: and, or in boolean expressions
- +1 for each: list/dict/set comprehension
- +1 for each: ternary expression (a if b else c)

```python
import ast
from agentpm.utils.ast_utils import calculate_complexity

code = '''
def complex_func(x, y):
    if x > 0 and y > 0:  # +2 (if + and)
        for i in range(x):  # +1 (for)
            if i % 2 == 0:  # +1 (if)
                y += 1
    return y
'''
tree = ast.parse(code)
func = tree.body[0]
complexity = calculate_complexity(func)
print(f"Complexity: {complexity}")  # Output: 5
```

**When to Use**:
- Use for single-file AST operations
- Building higher-level analysis tools
- Custom code extraction logic

---

### graph_builders.py - NetworkX Graph Construction

**Purpose**: Build and analyze dependency graphs.

**Location**: `agentpm/utils/graph_builders.py`

**Key Functions**:

#### build_import_graph(imports_by_file: Dict[str, List[str]], project_path: Path) → nx.DiGraph

Build directed graph from import statements.

```python
from pathlib import Path
from agentpm.utils.graph_builders import build_import_graph

# Prepare import data
imports = {
    'src/main.py': ['src.utils', 'src.models'],
    'src/utils.py': ['src.models']
}

# Build graph
graph = build_import_graph(imports, Path('/project'))

print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")

# Inspect node attributes
for node, attrs in graph.nodes(data=True):
    print(f"{node}: {attrs}")
```

**Graph Structure**:
- **Nodes**: Module paths (project-relative, normalized to dot format)
- **Edges**: Import relationships (source → target)
- **Node Attributes**: `{'file_path': str, 'import_count': int}`
- **Edge Attributes**: `{'weight': 1.0}`

#### detect_cycles(graph: nx.DiGraph) → List[List[str]]

Detect circular dependencies.

```python
from agentpm.utils.graph_builders import detect_cycles

cycles = detect_cycles(graph)
if cycles:
    print(f"Found {len(cycles)} circular dependencies:")
    for cycle in cycles:
        print(f"  {' → '.join(cycle)}")
```

**Returns**: List of cycles, sorted by length (shortest first)

#### calculate_coupling_metrics(graph: nx.DiGraph) → Dict[str, Dict[str, float]]

Calculate coupling metrics for each module.

```python
from agentpm.utils.graph_builders import calculate_coupling_metrics

metrics = calculate_coupling_metrics(graph)
for module, data in metrics.items():
    print(f"{module}:")
    print(f"  Afferent (Ca): {data['Ca']}")  # Incoming dependencies
    print(f"  Efferent (Ce): {data['Ce']}")  # Outgoing dependencies
    print(f"  Instability (I): {data['I']:.2f}")  # Ce / (Ce + Ca)
```

**Metrics**:
- **Ca (Afferent Coupling)**: Number of modules that depend on this module
  - High Ca = stable, many dependents
- **Ce (Efferent Coupling)**: Number of modules this module depends on
  - High Ce = unstable, many dependencies
- **I (Instability)**: Ce / (Ce + Ca), range [0.0, 1.0]
  - I=0.0: Maximally stable (core abstractions)
  - I=1.0: Maximally unstable (entry points)
  - I=0.5: Balanced

#### calculate_graph_metrics(graph: nx.DiGraph) → Dict[str, Any]

Calculate graph-level structural metrics.

```python
from agentpm.utils.graph_builders import calculate_graph_metrics

metrics = calculate_graph_metrics(graph)
print(f"Nodes: {metrics['node_count']}")
print(f"Edges: {metrics['edge_count']}")
print(f"Average degree: {metrics['avg_degree']:.2f}")
print(f"Max depth: {metrics['max_depth']}")
print(f"Has cycles: {metrics['cyclic']}")
print(f"Density: {metrics['density']:.2f}")
```

**When to Use**:
- Building dependency analysis tools
- Detecting architectural issues
- Visualizing module relationships

---

### metrics_calculator.py - Code Quality Metrics

**Purpose**: Calculate code metrics (LOC, complexity, maintainability).

**Location**: `agentpm/utils/metrics_calculator.py`

**Key Functions**:

#### count_lines(file_path: Path) → Dict[str, int]

Count lines with detailed categorization.

```python
from pathlib import Path
from agentpm.utils.metrics_calculator import count_lines

counts = count_lines(Path("example.py"))
print(f"Total lines: {counts['total_lines']}")
print(f"Code lines: {counts['code_lines']}")
print(f"Comment lines: {counts['comment_lines']}")
print(f"Blank lines: {counts['blank_lines']}")
print(f"Docstring lines: {counts['docstring_lines']}")
```

**Categories**:
- **total_lines**: All lines (including blanks)
- **code_lines**: Executable code only
- **comment_lines**: Single-line (#) and multi-line (''' or """) comments
- **blank_lines**: Empty or whitespace-only
- **docstring_lines**: Module/class/function docstrings

#### calculate_cyclomatic_complexity(ast_tree: ast.AST) → Dict[str, int]

Calculate McCabe cyclomatic complexity for all functions.

```python
import ast
from agentpm.utils.metrics_calculator import calculate_cyclomatic_complexity

with open("module.py") as f:
    tree = ast.parse(f.read())

complexity_map = calculate_cyclomatic_complexity(tree)
for func_name, complexity in complexity_map.items():
    if complexity > 10:
        print(f"HIGH COMPLEXITY: {func_name} = {complexity}")
```

**Returns**: Dict mapping `"ClassName.method_name"` or `"function_name"` → complexity

**Thresholds**:
- 1-10: Simple, low risk
- 11-20: Moderate complexity
- 21-50: High complexity, difficult to test
- 51+: Very high, should be refactored

#### calculate_maintainability_index(loc: int, cyclomatic_complexity: int, halstead_volume: Optional[float] = None) → float

Calculate Maintainability Index (0-100 scale).

```python
from agentpm.utils.metrics_calculator import (
    calculate_maintainability_index,
    count_lines
)

counts = count_lines(Path("module.py"))
mi = calculate_maintainability_index(
    loc=counts['code_lines'],
    cyclomatic_complexity=15,
    halstead_volume=None  # Uses approximation
)

print(f"Maintainability Index: {mi:.1f}")
if mi >= 85:
    print("Excellent maintainability")
elif mi >= 65:
    print("Good maintainability")
else:
    print("Needs improvement")
```

**Interpretation**:
- 85-100: Highly maintainable (green)
- 65-85: Moderately maintainable (yellow)
- 0-65: Difficult to maintain (red)

**When to Use**:
- Assessing file quality
- Identifying refactoring candidates
- Setting quality gates

---

### pattern_matchers.py - Architecture Pattern Detection

**Purpose**: Detect architecture patterns from directory structure.

**Location**: `agentpm/utils/pattern_matchers.py`

**Key Functions**:

#### detect_hexagonal_architecture(project_path: Path) → Dict[str, Any]

Detect Hexagonal (Ports & Adapters) architecture.

```python
from pathlib import Path
from agentpm.utils.pattern_matchers import detect_hexagonal_architecture

result = detect_hexagonal_architecture(Path('/project'))
print(f"Confidence: {result['confidence']:.0%}")
print("Evidence:")
for evidence in result['evidence']:
    print(f"  - {evidence}")
print("Violations:")
for violation in result['violations']:
    print(f"  - {violation}")
```

**Evidence Looked For**:
- `domain/` or `core/` directory
- `ports/` or `interfaces/` directory
- `adapters/` or `infrastructure/` directory

**Violations Detected**:
- Domain code importing from adapters
- Domain code importing from infrastructure

#### detect_layered_architecture(project_path: Path) → Dict[str, Any]

Detect Layered (N-tier) architecture.

```python
from agentpm.utils.pattern_matchers import detect_layered_architecture

result = detect_layered_architecture(Path('/project'))
print(f"Layered architecture: {result['confidence']:.0%}")
```

**Evidence**:
- `presentation/` or `ui/` or `views/`
- `application/` or `services/`
- `domain/` or `business/`
- `data/` or `persistence/`

#### detect_ddd_patterns(project_path: Path) → Dict[str, Any]

Detect Domain-Driven Design patterns.

```python
from agentpm.utils.pattern_matchers import detect_ddd_patterns

result = detect_ddd_patterns(Path('/project'))
print(f"DDD patterns found: {len(result['evidence'])}")
for pattern in result['evidence']:
    print(f"  - {pattern}")
```

**DDD Indicators**:
- Entities: `*Entity.py` or `entities/`
- Value Objects: `*ValueObject.py` or `value_objects/`
- Aggregates: `*Aggregate.py` or `aggregates/`
- Repositories: `*Repository.py` or `repositories/`
- Domain Services: `*DomainService.py` or `domain_services/`

**When to Use**:
- Architecture validation
- Pattern compliance checking
- Onboarding documentation

---

### file_parsers.py - Configuration File Parsing

**Purpose**: Safe parsing of package manifests and config files.

**Location**: `agentpm/utils/file_parsers.py`

**Key Functions**:

#### parse_python_dependencies(project_path: Path) → Dict[str, Any]

Extract Python dependencies from multiple sources.

```python
from pathlib import Path
from agentpm.utils.file_parsers import parse_python_dependencies

deps = parse_python_dependencies(Path('.'))
print(f"Source: {deps['source']}")
print(f"Runtime deps: {len(deps['runtime'])}")
for dep in deps['runtime']:
    print(f"  - {dep}")
print(f"Dev deps: {len(deps['dev'])}")
```

**Sources Checked** (priority order):
1. `pyproject.toml` (Poetry or PEP 621 format)
2. `requirements.txt`
3. `setup.py` (AST-based, no execution)

**Returns**:
```python
{
    'runtime': ['requests', 'pydantic', 'rich'],
    'dev': ['pytest', 'black', 'mypy'],
    'source': 'pyproject.toml'  # or 'requirements.txt', 'setup.py', 'none'
}
```

#### parse_javascript_dependencies(project_path: Path) → Dict[str, Any]

Extract JavaScript/Node dependencies.

```python
from agentpm.utils.file_parsers import parse_javascript_dependencies

deps = parse_javascript_dependencies(Path('.'))
if deps['source'] != 'none':
    print(f"Runtime: {', '.join(deps['runtime'])}")
    print(f"Dev: {', '.join(deps['dev'])}")
```

**Source**: `package.json`

**Returns**:
```python
{
    'runtime': ['react', 'axios'],
    'dev': ['vite', 'typescript'],
    'peer': ['react-dom'],
    'optional': ['fsevents'],
    'source': 'package.json'
}
```

#### parse_toml(file_path: Path) → Optional[Dict[str, Any]]

Safe TOML parsing.

```python
from agentpm.utils.file_parsers import parse_toml

config = parse_toml(Path("pyproject.toml"))
if config:
    name = config.get("tool", {}).get("poetry", {}).get("name")
    print(f"Project: {name}")
```

**Supported Files**:
- `pyproject.toml`
- `Cargo.toml` (future)
- Any TOML configuration

**When to Use**:
- SBOM generation
- Dependency analysis
- License detection
- Configuration parsing

---

## Layer 2: Database Models

Database models provide type safety and validation using Pydantic. They are shared across all layers.

### detection_analysis.py - Static Analysis Models

**Location**: `agentpm/core/database/models/detection_analysis.py`

#### FileAnalysis

Single file analysis result.

```python
from agentpm.core.database.models.detection_analysis import FileAnalysis

analysis = FileAnalysis(
    file_path="/path/to/file.py",
    total_lines=100,
    code_lines=70,
    comment_lines=20,
    blank_lines=10,
    complexity_avg=3.5,
    complexity_max=8,
    function_count=5,
    class_count=2,
    maintainability_index=72.5,
    functions=[],
    classes=[]
)

# Check quality
if analysis.is_high_complexity:
    print("WARNING: High complexity")
if analysis.is_low_maintainability:
    print("WARNING: Low maintainability")

print(f"Quality score: {analysis.quality_score:.1f}/100")
```

**Properties**:
- `is_high_complexity`: True if `complexity_max > 10`
- `is_low_maintainability`: True if `maintainability_index < 65`
- `quality_score`: Weighted combination of MI, complexity, comments

#### ProjectAnalysis

Aggregated project analysis.

```python
from agentpm.core.database.models.detection_analysis import ProjectAnalysis

analysis = ProjectAnalysis(
    project_path="/path/to/project",
    total_files=10,
    total_lines=1000,
    total_code_lines=700,
    avg_complexity=5.2,
    max_complexity=15,
    avg_maintainability=75.0,
    files=[file_analysis1, file_analysis2, ...]
)
```

---

### detection_graph.py - Dependency Graph Models

**Location**: `agentpm/core/database/models/detection_graph.py`

#### CircularDependency

Detected circular dependency with severity.

```python
from agentpm.core.database.models.detection_graph import CircularDependency

cycle = CircularDependency(
    cycle=["src/foo.py", "src/bar.py", "src/foo.py"],
    severity="high",
    suggestion="Extract shared code to third module"
)

print(f"Cycle length: {cycle.cycle_length}")
print(f"Severity: {cycle.severity}")
```

**Severity Levels**:
- **high**: 2 modules (direct A ↔ B)
- **medium**: 3-5 modules
- **low**: >5 modules

#### CouplingMetrics

Coupling metrics for a module.

```python
from agentpm.core.database.models.detection_graph import CouplingMetrics

metrics = CouplingMetrics(
    module="src/core.py",
    afferent_coupling=5,  # 5 modules depend on this
    efferent_coupling=2,  # This depends on 2 modules
    instability=0.29  # 2 / (2 + 5) = 0.29
)

if metrics.is_stable:
    print("Stable module (good for core abstractions)")
if metrics.is_unstable:
    print("Unstable module (typical for entry points)")
```

**Properties**:
- `is_stable`: True if `instability < 0.3`
- `is_unstable`: True if `instability > 0.7`

---

### detection_sbom.py - SBOM Models

**Location**: `agentpm/core/database/models/detection_sbom.py`

#### SBOMComponent

Single component in software bill of materials.

```python
from agentpm.core.database.models.detection_sbom import SBOMComponent, LicenseInfo
from agentpm.core.database.enums.detection import LicenseType

component = SBOMComponent(
    name="requests",
    version="2.31.0",
    type="library",
    purl="pkg:pypi/requests@2.31.0",
    license=LicenseInfo(
        package_name="requests",
        version="2.31.0",
        license_type=LicenseType.APACHE_2_0,
        source="importlib.metadata",
        confidence=0.9
    )
)
```

---

### detection_fitness.py - Fitness Testing Models

**Location**: `agentpm/core/database/models/detection_fitness.py`

#### Policy

Architecture fitness policy definition.

```python
from agentpm.core.database.models.detection_fitness import Policy
from agentpm.core.database.enums.detection import PolicyLevel

policy = Policy(
    policy_id="complexity-max-10",
    name="Maximum Complexity Threshold",
    description="Functions must not exceed cyclomatic complexity of 10",
    level=PolicyLevel.ERROR,
    validation_fn="validate_max_complexity",
    metadata={"threshold": 10},
    enabled=True,
    tags=["complexity", "quality"]
)
```

#### FitnessResult

Complete fitness testing result.

```python
from agentpm.core.database.models.detection_fitness import FitnessResult

result = FitnessResult(
    violations=[...],
    passed_count=8,
    warning_count=2,
    error_count=1,
    compliance_score=0.85
)

if result.is_passing():
    print(f"PASSED - {result.compliance_score:.0%} compliance")
else:
    print(f"FAILED - {result.error_count} errors")
    for violation in result.get_violations_by_level(PolicyLevel.ERROR):
        print(f"  {violation.location}: {violation.message}")
```

---

## Layer 3: Detection Services

Layer 3 services orchestrate Layer 1 utilities to provide high-level capabilities.

### StaticAnalysisService

**Purpose**: Static code analysis with caching.

**Location**: `agentpm/core/detection/analysis/service.py`

**Key Methods**:

#### analyze_file(file_path: Path) → Optional[FileAnalysis]

Analyze single Python file.

```python
from pathlib import Path
from agentpm.core.detection.analysis.service import StaticAnalysisService

service = StaticAnalysisService(Path.cwd())
analysis = service.analyze_file(Path("example.py"))

if analysis:
    print(f"Complexity: {analysis.complexity_max}")
    print(f"MI: {analysis.maintainability_index:.1f}")
    print(f"Functions: {analysis.function_count}")
```

**Process**:
1. Check cache (if enabled)
2. Count lines using `metrics_calculator.count_lines()`
3. Parse AST using `ast_utils.parse_python_ast()`
4. Extract functions/classes using `ast_utils.extract_*()`
5. Calculate complexity using `metrics_calculator.calculate_cyclomatic_complexity()`
6. Calculate MI using `metrics_calculator.calculate_maintainability_index()`
7. Cache result

**Performance**:
- First run: <100ms per file
- Cached: <10ms

#### analyze_project(file_pattern: str = "**/*.py") → ProjectAnalysis

Analyze entire project.

```python
service = StaticAnalysisService(Path.cwd())
analysis = service.analyze_project()

print(f"Analyzed {analysis.total_files} files")
print(f"Average complexity: {analysis.avg_complexity:.2f}")
print(f"Average MI: {analysis.avg_maintainability:.1f}")

# Get high complexity files
high_complexity = service.get_high_complexity_files(analysis, threshold=10)
for file in high_complexity:
    print(f"{file.file_path}: {file.complexity_max}")
```

**Features**:
- Respects `.gitignore` and `.aipmignore`
- Filters common directories (venv/, node_modules/, .git/)
- Caches per-file results
- Aggregates metrics (weighted by code lines)

#### generate_complexity_report(analysis: ProjectAnalysis, threshold: int = 10) → ComplexityReport

Generate complexity violation report.

```python
report = service.generate_complexity_report(analysis, threshold=10)
print(f"Violations: {report.total_violations}")
print("\nTop complexity hotspots:")
for hotspot in report.hotspots[:5]:
    print(f"  {hotspot['name']}: {hotspot['complexity']}")
    print(f"    Location: {hotspot['file_path']}:{hotspot['line_number']}")
```

---

### DependencyGraphService

**Purpose**: Dependency graph analysis.

**Location**: `agentpm/core/detection/graphs/service.py`

**Key Methods**:

#### build_graph(file_pattern: str = "**/*.py") → nx.DiGraph

Build dependency graph from project imports.

```python
from agentpm.core.detection.graphs.service import DependencyGraphService

service = DependencyGraphService(Path.cwd())
graph = service.build_graph()

print(f"Modules: {graph.number_of_nodes()}")
print(f"Dependencies: {graph.number_of_edges()}")
```

**Process**:
1. Find all Python files
2. Filter using IgnorePatternMatcher
3. Parse each file with `ast_utils.parse_python_ast()`
4. Extract imports with `ast_utils.extract_imports()`
5. Build graph with `graph_builders.build_import_graph()`

#### analyze_dependencies() → DependencyGraphAnalysis

Complete dependency analysis.

```python
service = DependencyGraphService(Path.cwd())
analysis = service.analyze_dependencies()

if analysis.has_circular_dependencies:
    print("WARNING: Circular dependencies detected!")
    for cycle in analysis.circular_dependencies:
        print(f"  {cycle.severity.upper()}: {' → '.join(cycle.cycle)}")
        print(f"  Suggestion: {cycle.suggestion}")

print(f"Average instability: {analysis.average_instability:.2f}")
```

#### export_graphviz(output_path: Path, highlight_cycles: bool = True)

Export graph visualization.

```python
service.export_graphviz(
    Path("dependencies.dot"),
    highlight_cycles=True,
    include_metrics=True
)

# Render with Graphviz
# $ dot -Tpng dependencies.dot -o dependencies.png
```

---

### SBOMService

**Purpose**: Software Bill of Materials generation.

**Location**: `agentpm/core/detection/sbom/service.py`

**Key Methods**:

#### generate_sbom(include_licenses: bool = True, include_dev_deps: bool = False) → SBOM

Generate complete SBOM.

```python
from agentpm.core.detection.sbom.service import SBOMService

service = SBOMService(Path.cwd())
sbom = service.generate_sbom(include_licenses=True)

print(f"Project: {sbom.project_name} v{sbom.project_version}")
print(f"Components: {sbom.total_components}")
print(f"License summary: {sbom.license_summary}")
```

**Process**:
1. Extract Python dependencies using `file_parsers.parse_python_dependencies()`
2. Extract JS dependencies using `file_parsers.parse_javascript_dependencies()`
3. Detect licenses from package metadata
4. Build SBOM model

#### export_cyclonedx(sbom: SBOM, output_path: Path, format: str = "json")

Export to CycloneDX format.

```python
service.export_cyclonedx(sbom, Path("sbom.json"), format="json")
```

#### export_spdx(sbom: SBOM, output_path: Path)

Export to SPDX format.

```python
service.export_spdx(sbom, Path("sbom.spdx.json"))
```

---

### PatternRecognitionService

**Purpose**: Architecture pattern detection.

**Location**: `agentpm/core/detection/patterns/service.py`

**Key Methods**:

#### analyze_patterns(confidence_threshold: float = 0.5) → PatternAnalysis

Analyze all architecture patterns.

```python
from agentpm.core.detection.patterns.service import PatternRecognitionService

service = PatternRecognitionService(Path.cwd())
analysis = service.analyze_patterns(confidence_threshold=0.6)

print(f"Primary pattern: {analysis.primary_pattern}")
for match in analysis.get_high_confidence_patterns():
    print(f"\n{match.pattern.value.upper()}: {match.confidence:.0%}")
    for evidence in match.evidence:
        print(f"  ✓ {evidence}")
    if match.violations:
        for violation in match.violations:
            print(f"  ✗ {violation}")
```

**Detects**:
- Hexagonal architecture
- Layered (N-tier) architecture
- Domain-Driven Design (DDD)
- CQRS (Command Query Responsibility Segregation)
- MVC (Model-View-Controller)

#### detect_hexagonal() → PatternMatch

Detect hexagonal architecture specifically.

```python
hexagonal = service.detect_hexagonal()
if hexagonal.confidence > 0.7:
    print("Hexagonal architecture detected")
```

---

### FitnessEngine

**Purpose**: Policy-based architecture fitness testing.

**Location**: `agentpm/core/detection/fitness/engine.py`

**Key Methods**:

#### load_default_policies() → List[Policy]

Load built-in fitness policies.

```python
from agentpm.core.detection.fitness.engine import FitnessEngine

engine = FitnessEngine(Path.cwd())
policies = engine.load_default_policies()

print(f"Loaded {len(policies)} policies")
for policy in policies:
    print(f"  {policy.policy_id}: {policy.level.value}")
```

**Default Policies**:
- No circular dependencies
- Max complexity threshold (10)
- Max file LOC (500)
- Max function LOC (50)
- Layering violations
- Minimum maintainability (65)
- Max coupling/instability (0.8)
- Max dependency depth (10)

#### run_tests(policies: List[Policy]) → FitnessResult

Run fitness tests.

```python
engine = FitnessEngine(Path.cwd())
policies = engine.load_default_policies()
result = engine.run_tests(policies)

if result.is_passing():
    print(f"✓ PASSED - {result.compliance_score:.0%} compliance")
else:
    print(f"✗ FAILED - {result.error_count} errors")
    for violation in result.get_violations_by_level(PolicyLevel.ERROR):
        print(f"  {violation.location}: {violation.message}")
        print(f"    Suggestion: {violation.suggestion}")
```

**Compliance Score**:
- Start at 1.0 (perfect)
- Subtract 0.1 for each error
- Subtract 0.05 for each warning
- Minimum: 0.0

---

## Adding New Features

### How to Add a New Pattern Detector

**Goal**: Add detection for Clean Architecture pattern.

**Step 1**: Add pattern to `pattern_matchers.py` (Layer 1)

```python
# agentpm/utils/pattern_matchers.py

CLEAN_ARCHITECTURE_PATTERN: Dict[str, Any] = {
    'required_dirs': ['entities', 'use_cases', 'interface_adapters', 'frameworks'],
    'optional_dirs': ['application', 'domain'],
    'forbidden_dirs': [],
    'alternatives': {
        'entities': ['domain/entities', 'core/entities'],
        'use_cases': ['application', 'business_logic'],
        'interface_adapters': ['adapters', 'presenters'],
        'frameworks': ['infrastructure', 'external']
    },
    'min_match_score': 0.7
}

def detect_clean_architecture(project_path: Path) -> Dict[str, Any]:
    """
    Detect Clean Architecture pattern.

    Evidence:
    - entities/ directory (innermost layer)
    - use_cases/ directory
    - interface_adapters/ directory
    - frameworks/ directory (outermost layer)
    - Dependency rule: dependencies point inward only
    """
    confidence = match_directory_pattern(project_path, CLEAN_ARCHITECTURE_PATTERN)

    evidence = []
    violations = []

    # Check for required layers
    if (project_path / 'entities').exists():
        evidence.append('entities/ layer found (innermost)')
    if (project_path / 'use_cases').exists():
        evidence.append('use_cases/ layer found')
    if (project_path / 'interface_adapters').exists():
        evidence.append('interface_adapters/ layer found')
    if (project_path / 'frameworks').exists():
        evidence.append('frameworks/ layer found (outermost)')

    # Check dependency rule violations
    # (Entities should not import from outer layers)
    clean_violations = _check_clean_architecture_violations(project_path)
    violations.extend(clean_violations)

    if violations:
        confidence *= 0.7

    return {
        'pattern': 'clean_architecture',
        'confidence': confidence,
        'evidence': evidence,
        'violations': violations
    }

def _check_clean_architecture_violations(project_path: Path) -> List[Dict[str, str]]:
    """Check for Clean Architecture dependency rule violations."""
    violations = []

    entities_dir = project_path / 'entities'
    outer_layers = ['use_cases', 'interface_adapters', 'frameworks']

    if not entities_dir.exists():
        return violations

    # Check that entities don't import from outer layers
    for python_file in entities_dir.rglob('*.py'):
        try:
            content = python_file.read_text(encoding='utf-8', errors='ignore')
            for outer_layer in outer_layers:
                if f'from {outer_layer}' in content or f'import {outer_layer}' in content:
                    violations.append({
                        'type': 'clean_architecture_violation',
                        'description': f'Entity importing from outer layer {outer_layer}',
                        'location': str(python_file.relative_to(project_path))
                    })
                    break
        except (OSError, UnicodeDecodeError):
            continue

    return violations
```

**Step 2**: Add enum to `detection.py` (Database Layer)

```python
# agentpm/core/database/enums/detection.py

class ArchitecturePattern(str, Enum):
    """Architecture pattern types."""
    HEXAGONAL = "hexagonal"
    LAYERED = "layered"
    DDD = "ddd"
    CQRS = "cqrs"
    MVC = "mvc"
    CLEAN = "clean_architecture"  # Add this
```

**Step 3**: Add method to `PatternRecognitionService` (Layer 3)

```python
# agentpm/core/detection/patterns/service.py

from agentpm.utils.pattern_matchers import detect_clean_architecture


class PatternRecognitionService:
    # ... existing methods ...

    def detect_clean(self) -> PatternMatch:
        """
        Detect Clean Architecture pattern.

        Returns:
            PatternMatch for clean architecture

        Example:
            >>> service = PatternRecognitionService(Path('/project'))
            >>> clean = service.detect_clean()
            >>> if clean.confidence > 0.7:
            ...     print("Clean Architecture detected")
        """
        logger.debug("Detecting Clean Architecture")

        try:
            # Use Layer 1 utility
            result = detect_clean_architecture(self.project_path)

            match = PatternMatch(
                pattern=ArchitecturePattern.CLEAN,
                confidence=result['confidence'],
                evidence=result['evidence'],
                violations=self._format_violations(result['violations'])
            )

            logger.debug(
                f"Clean Architecture detection complete: confidence={match.confidence:.2f}"
            )

            return match

        except Exception as e:
            logger.error(f"Error detecting clean architecture: {e}", exc_info=True)
            return PatternMatch(
                pattern=ArchitecturePattern.CLEAN,
                confidence=0.0,
                evidence=[],
                violations=[f"Error during detection: {str(e)}"]
            )

    def analyze_patterns(self, confidence_threshold: float = 0.5) -> PatternAnalysis:
        """Analyze project for all architecture patterns."""
        # ... existing code ...

        # Add to detection list
        matches.append(self.detect_hexagonal())
        matches.append(self.detect_layered())
        matches.append(self.detect_ddd())
        matches.append(self.detect_cqrs())
        matches.append(self.detect_mvc())
        matches.append(self.detect_clean())  # Add this

        # ... rest of method ...
```

**Step 4**: Write tests

```python
# tests/unit/detection/patterns/test_clean_architecture.py

import pytest
from pathlib import Path
from agentpm.utils.pattern_matchers import detect_clean_architecture


def test_detect_clean_architecture_positive(tmp_path):
    """Test detection of valid clean architecture."""
    # Create directory structure
    (tmp_path / "entities").mkdir()
    (tmp_path / "use_cases").mkdir()
    (tmp_path / "interface_adapters").mkdir()
    (tmp_path / "frameworks").mkdir()

    # Create sample files
    (tmp_path / "entities" / "user.py").write_text("class User: pass")
    (tmp_path / "use_cases" / "create_user.py").write_text("from entities.user import User")

    result = detect_clean_architecture(tmp_path)

    assert result['confidence'] >= 0.7
    assert len(result['evidence']) >= 3
    assert result['pattern'] == 'clean_architecture'


def test_detect_clean_architecture_violation(tmp_path):
    """Test detection of dependency rule violation."""
    # Create structure with violation
    entities_dir = tmp_path / "entities"
    entities_dir.mkdir()
    frameworks_dir = tmp_path / "frameworks"
    frameworks_dir.mkdir()

    # Entity importing from framework (violation!)
    (entities_dir / "user.py").write_text("from frameworks.db import Database")

    result = detect_clean_architecture(tmp_path)

    assert len(result['violations']) > 0
    assert 'clean_architecture_violation' in result['violations'][0]['type']


def test_pattern_recognition_service_clean(tmp_path):
    """Test PatternRecognitionService integration."""
    from agentpm.core.detection.patterns.service import PatternRecognitionService

    # Setup structure
    (tmp_path / "entities").mkdir()
    (tmp_path / "use_cases").mkdir()
    (tmp_path / "interface_adapters").mkdir()
    (tmp_path / "frameworks").mkdir()

    service = PatternRecognitionService(tmp_path)
    match = service.detect_clean()

    assert match.pattern.value == "clean_architecture"
    assert match.confidence >= 0.7
```

**Step 5**: Update documentation

Add to `docs/guides/user_guide/detection-patterns.md`:

```markdown
### Clean Architecture

**Detection Criteria**:
- `entities/` directory (innermost layer)
- `use_cases/` directory
- `interface_adapters/` directory
- `frameworks/` directory (outermost layer)

**Dependency Rule**: Dependencies must point inward only

**Example Structure**:
```
project/
├── entities/           # Business entities (no dependencies)
├── use_cases/          # Business rules (depends on entities)
├── interface_adapters/ # Presenters, controllers (depends on use_cases)
└── frameworks/         # External frameworks, DB (depends on adapters)
```
```

---

### How to Add a New Fitness Policy

**Goal**: Add policy to enforce maximum class size.

**Step 1**: Define policy in `policies.py`

```python
# agentpm/core/detection/fitness/policies.py

DEFAULT_POLICIES = [
    # ... existing policies ...

    {
        'policy_id': 'class-size-max-200',
        'name': 'Maximum Class Size',
        'description': 'Classes must not exceed 200 lines',
        'level': 'WARNING',
        'validation_fn': 'validate_max_class_size',
        'metadata': {
            'threshold': 200,
            'rationale': 'Large classes violate Single Responsibility Principle',
            'recommendation': 'Extract responsibilities to separate classes'
        },
        'enabled': True,
        'tags': ['size', 'quality', 'design']
    }
]
```

**Step 2**: Implement validator in `engine.py`

```python
# agentpm/core/detection/fitness/engine.py

class FitnessEngine:
    def _register_validators(self) -> None:
        """Register validation functions."""
        self._policy_validators = {
            # ... existing validators ...
            'validate_max_class_size': self._validate_max_class_size,
        }

    def _validate_max_class_size(self, policy: Policy) -> List[PolicyViolation]:
        """
        Validate maximum class size.

        Args:
            policy: Policy configuration with threshold in metadata

        Returns:
            List of violations (one per oversized class)
        """
        violations = []
        threshold = policy.metadata.get('threshold', 200)

        # Analyze project
        analysis = self.analysis_service.analyze_project()

        # Check each file
        for file_analysis in analysis.files:
            for cls in file_analysis.classes:
                start_line = cls.get('line_number', 0)
                end_line = cls.get('end_line', start_line)
                class_lines = end_line - start_line + 1

                if class_lines > threshold:
                    class_name = cls.get('name', 'unknown')

                    violations.append(
                        PolicyViolation(
                            policy_id=policy.policy_id,
                            level=policy.level,
                            message=(
                                f"Class '{class_name}' has {class_lines} lines, "
                                f"exceeds threshold of {threshold}"
                            ),
                            location=f"{file_analysis.file_path}:{start_line}",
                            suggestion=policy.metadata.get(
                                'recommendation',
                                "Extract methods or responsibilities to separate classes"
                            )
                        )
                    )

        return violations
```

**Step 3**: Write tests

```python
# tests/unit/detection/fitness/test_class_size_policy.py

import pytest
from pathlib import Path
from agentpm.core.detection.fitness.engine import FitnessEngine
from agentpm.core.detection.fitness.policies import create_policy_from_dict
from agentpm.core.database.enums.detection import PolicyLevel


def test_validate_max_class_size_pass(tmp_path):
    """Test class size validation passes for small classes."""
    # Create test file with small class
    test_file = tmp_path / "small_class.py"
    test_file.write_text("""
class SmallClass:
    def method1(self):
        pass

    def method2(self):
        pass
""")

    engine = FitnessEngine(tmp_path)
    policy_dict = {
        'policy_id': 'test-class-size',
        'name': 'Test Class Size',
        'description': 'Test policy',
        'level': 'WARNING',
        'validation_fn': 'validate_max_class_size',
        'metadata': {'threshold': 200},
        'enabled': True,
        'tags': ['test']
    }
    policy = create_policy_from_dict(policy_dict)

    violations = engine._validate_max_class_size(policy)

    assert len(violations) == 0


def test_validate_max_class_size_fail(tmp_path):
    """Test class size validation fails for large classes."""
    # Create test file with large class (250 lines)
    large_class_code = "class LargeClass:\n" + "\n".join([
        f"    def method{i}(self):\n        pass"
        for i in range(100)
    ])

    test_file = tmp_path / "large_class.py"
    test_file.write_text(large_class_code)

    engine = FitnessEngine(tmp_path)
    policy_dict = {
        'policy_id': 'test-class-size',
        'name': 'Test Class Size',
        'description': 'Test policy',
        'level': 'WARNING',
        'validation_fn': 'validate_max_class_size',
        'metadata': {'threshold': 200},
        'enabled': True,
        'tags': ['test']
    }
    policy = create_policy_from_dict(policy_dict)

    violations = engine._validate_max_class_size(policy)

    assert len(violations) > 0
    assert 'LargeClass' in violations[0].message
    assert '200' in violations[0].message
```

---

### How to Add a New CLI Command

**Goal**: Add `apm detect patterns --format=json` command.

**Step 1**: Add command to CLI

```python
# agentpm/cli/commands/detect.py

import click
import json
from pathlib import Path
from agentpm.core.detection.patterns.service import PatternRecognitionService


@click.group()
def detect():
    """Code detection and analysis commands."""
    pass


@detect.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.option('--threshold', type=float, default=0.5,
              help='Minimum confidence threshold (0.0-1.0)')
def patterns(format, threshold):
    """Detect architecture patterns in current project."""

    # Initialize service
    project_path = Path.cwd()
    service = PatternRecognitionService(project_path)

    # Analyze patterns
    try:
        analysis = service.analyze_patterns(confidence_threshold=threshold)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # Output results
    if format == 'json':
        # JSON output
        output = {
            'project_path': str(analysis.project_path),
            'primary_pattern': analysis.primary_pattern.value if analysis.primary_pattern else None,
            'confidence_threshold': threshold,
            'patterns': []
        }

        for match in analysis.matches:
            if match.confidence >= threshold:
                output['patterns'].append({
                    'pattern': match.pattern.value,
                    'confidence': match.confidence,
                    'evidence': match.evidence,
                    'violations': match.violations,
                    'recommendations': match.recommendations
                })

        click.echo(json.dumps(output, indent=2))

    else:
        # Text output
        click.echo(f"Architecture Pattern Analysis")
        click.echo(f"Project: {analysis.project_path}")
        click.echo(f"Threshold: {threshold:.0%}\n")

        if analysis.primary_pattern:
            click.echo(f"Primary Pattern: {analysis.primary_pattern.value.upper()}\n")
        else:
            click.echo("No clear pattern detected\n")

        # Show matches above threshold
        high_confidence = [m for m in analysis.matches if m.confidence >= threshold]
        if high_confidence:
            click.echo("Detected Patterns:")
            for match in sorted(high_confidence, key=lambda m: m.confidence, reverse=True):
                click.echo(f"\n{match.pattern.value.upper()}: {match.confidence:.0%}")

                if match.evidence:
                    click.echo("  Evidence:")
                    for evidence in match.evidence:
                        click.echo(f"    ✓ {evidence}")

                if match.violations:
                    click.echo("  Violations:")
                    for violation in match.violations:
                        click.echo(f"    ✗ {violation}")
        else:
            click.echo("No patterns detected above threshold")
```

**Step 2**: Register command in main CLI

```python
# agentpm/cli/main.py

from agentpm.cli.commands.detect import detect


@click.group()
def cli():
    """APM (Agent Project Manager) CLI."""
    pass


# Register detect commands
cli.add_command(detect)
```

**Step 3**: Write tests

```python
# tests/integration/cli/test_detect_patterns.py

import pytest
import json
from click.testing import CliRunner
from agentpm.cli.main import cli


def test_detect_patterns_text_format(tmp_path, monkeypatch):
    """Test patterns command with text output."""
    # Setup test project structure
    (tmp_path / "domain").mkdir()
    (tmp_path / "ports").mkdir()
    (tmp_path / "adapters").mkdir()

    # Change to test directory
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ['detect', 'patterns', '--format=text'])

    assert result.exit_code == 0
    assert 'HEXAGONAL' in result.output
    assert 'Evidence:' in result.output


def test_detect_patterns_json_format(tmp_path, monkeypatch):
    """Test patterns command with JSON output."""
    # Setup test project
    (tmp_path / "domain").mkdir()
    (tmp_path / "ports").mkdir()

    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ['detect', 'patterns', '--format=json'])

    assert result.exit_code == 0
    output = json.loads(result.output)
    assert 'patterns' in output
    assert 'primary_pattern' in output
```

---

## Testing Guidelines

### Unit Testing Utilities

**Philosophy**: Test Layer 1 utilities in isolation with known inputs/outputs.

**Example: Testing `ast_utils.extract_classes()`**

```python
# tests/unit/utils/test_ast_utils.py

import pytest
import ast
from pathlib import Path
from agentpm.utils.ast_utils import extract_classes


def test_extract_classes_simple():
    """Test extraction of simple class definition."""
    code = """
class SimpleClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""
    tree = ast.parse(code)
    classes = extract_classes(tree, Path("test.py"))

    assert len(classes) == 1
    assert classes[0]['name'] == 'SimpleClass'
    assert classes[0]['bases'] == []
    assert len(classes[0]['methods']) == 2
    assert 'method1' in classes[0]['methods']
    assert 'method2' in classes[0]['methods']


def test_extract_classes_with_inheritance():
    """Test extraction with inheritance and decorators."""
    code = """
from dataclasses import dataclass

@dataclass
class User(BaseModel):
    def validate(self):
        pass
"""
    tree = ast.parse(code)
    classes = extract_classes(tree, Path("test.py"))

    assert len(classes) == 1
    assert classes[0]['name'] == 'User'
    assert 'BaseModel' in classes[0]['bases']
    assert 'dataclass' in classes[0]['decorators']


def test_extract_classes_empty():
    """Test extraction from file with no classes."""
    code = """
def standalone_function():
    return 42

CONSTANT = "value"
"""
    tree = ast.parse(code)
    classes = extract_classes(tree, Path("test.py"))

    assert len(classes) == 0
```

**Coverage Target**: >90% for Layer 1 utilities

---

### Testing Services

**Philosophy**: Test service orchestration logic, mock Layer 1 utilities when needed.

**Example: Testing `StaticAnalysisService`**

```python
# tests/unit/detection/test_static_analysis_service.py

import pytest
from pathlib import Path
from agentpm.core.detection.analysis.service import StaticAnalysisService
from agentpm.core.database.models.detection_analysis import FileAnalysis


def test_analyze_file_success(tmp_path):
    """Test successful file analysis."""
    # Create test file
    test_file = tmp_path / "example.py"
    test_file.write_text("""
def simple_function(x):
    if x > 0:
        return x * 2
    return 0

class SimpleClass:
    def method(self):
        pass
""")

    service = StaticAnalysisService(tmp_path, cache_enabled=False)
    analysis = service.analyze_file(test_file)

    assert analysis is not None
    assert analysis.function_count == 2  # simple_function + method
    assert analysis.class_count == 1
    assert analysis.complexity_max >= 2  # simple_function has if statement


def test_analyze_project_aggregation(tmp_path):
    """Test project-level aggregation."""
    # Create multiple test files
    file1 = tmp_path / "module1.py"
    file1.write_text("def func1(): pass\ndef func2(): pass")

    file2 = tmp_path / "module2.py"
    file2.write_text("class Class1: pass")

    service = StaticAnalysisService(tmp_path, cache_enabled=False)
    analysis = service.analyze_project()

    assert analysis.total_files == 2
    assert analysis.total_code_lines > 0
    assert len(analysis.files) == 2


def test_get_high_complexity_files(tmp_path):
    """Test filtering high complexity files."""
    # Create file with high complexity
    high_complexity_file = tmp_path / "complex.py"
    complex_code = """
def complex_function(x, y, z):
    if x:
        if y:
            if z:
                for i in range(10):
                    if i % 2:
                        return i
    return 0
"""
    high_complexity_file.write_text(complex_code)

    service = StaticAnalysisService(tmp_path, cache_enabled=False)
    analysis = service.analyze_project()
    high_complexity = service.get_high_complexity_files(analysis, threshold=5)

    assert len(high_complexity) > 0
    assert high_complexity[0].complexity_max > 5
```

**Fixtures**: Use pytest fixtures for common setups

```python
# tests/conftest.py

import pytest
from pathlib import Path

@pytest.fixture
def sample_python_project(tmp_path):
    """Create a sample Python project structure."""
    # Create directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()

    # Create sample files
    (tmp_path / "src" / "main.py").write_text("""
def main():
    print("Hello")

if __name__ == "__main__":
    main()
""")

    (tmp_path / "src" / "utils.py").write_text("""
def helper(x):
    return x * 2
""")

    (tmp_path / "tests" / "test_main.py").write_text("""
def test_main():
    assert True
""")

    return tmp_path
```

---

### Testing CLI Commands

**Philosophy**: Use CliRunner for integration tests, verify output and exit codes.

**Example**:

```python
# tests/integration/cli/test_detect_analyze.py

import pytest
from click.testing import CliRunner
from agentpm.cli.main import cli


def test_detect_analyze_command(sample_python_project, monkeypatch):
    """Test detect analyze command end-to-end."""
    monkeypatch.chdir(sample_python_project)

    runner = CliRunner()
    result = runner.invoke(cli, ['detect', 'analyze'])

    assert result.exit_code == 0
    assert 'Project Analysis' in result.output
    assert 'Files analyzed:' in result.output


def test_detect_analyze_with_output_file(sample_python_project, tmp_path, monkeypatch):
    """Test detect analyze with file output."""
    monkeypatch.chdir(sample_python_project)
    output_file = tmp_path / "analysis.json"

    runner = CliRunner()
    result = runner.invoke(cli, ['detect', 'analyze', '--output', str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()

    # Verify JSON structure
    import json
    data = json.loads(output_file.read_text())
    assert 'total_files' in data
    assert 'avg_complexity' in data
```

---

## Performance Considerations

### Caching Strategies

**File-Level Caching**: Cache AST parse results

```python
# Analysis cache invalidates on file content change
cache = AnalysisCache(Path(".cache/analysis"), enabled=True)

# Check cache (SHA-256 hash of file content)
cached_analysis = cache.get(file_path)
if cached_analysis:
    return cached_analysis  # <10ms

# Analyze and cache
analysis = analyze_file(file_path)
cache.set(file_path, analysis)
```

**Graph Caching**: Cache dependency graphs with TTL

```python
# DependencyGraphService caches graph for 1 hour
service = DependencyGraphService(project_path)
graph = service.build_graph()  # Builds and caches

# Subsequent calls within 1 hour return cached graph
graph2 = service.build_graph()  # <50ms (cached)

# Force rebuild
graph3 = service.build_graph(force_rebuild=True)
```

---

### When to Use IgnorePatternMatcher

**Problem**: Large projects have many irrelevant files (venv/, node_modules/, .git/)

**Solution**: Use `IgnorePatternMatcher` to filter efficiently

```python
from agentpm.utils.ignore_patterns import IgnorePatternMatcher

# Initialize (reads .gitignore, .aipmignore, applies defaults)
matcher = IgnorePatternMatcher(project_path)

# Filter file list
all_files = list(project_path.glob("**/*.py"))
relevant_files = matcher.filter_paths(all_files)

print(f"Filtered {len(all_files)} → {len(relevant_files)} files")
```

**Default Ignore Patterns**:
- `.git/`, `.venv/`, `venv/`, `env/`
- `node_modules/`, `__pycache__/`
- `.pytest_cache/`, `.mypy_cache/`, `.tox/`
- `dist/`, `build/`, `*.egg-info/`

---

### Large Project Optimization

**Target**: Analyze 1000-file project in <5s

**Strategies**:

1. **Enable Caching**
```python
service = StaticAnalysisService(
    project_path,
    cache_enabled=True,  # Essential for large projects
    cache_dir=Path(".cache/analysis")
)
```

2. **Filter Aggressively**
```python
# Create .aipmignore to exclude generated code
# .aipmignore:
testing/
migrations/
vendor/
```

3. **Use Parallel Processing** (future enhancement)
```python
# Currently sequential, future: parallel file analysis
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(analyze_file, file_list)
```

4. **Limit Scope**
```python
# Analyze specific directory only
analysis = service.analyze_project(file_pattern="src/**/*.py")
```

---

### Memory Management

**Target**: <500MB for large projects

**Guidelines**:

1. **Stream Processing**: Don't load entire AST forest
```python
# Good: Process one file at a time
for file_path in files:
    analysis = service.analyze_file(file_path)
    process(analysis)

# Bad: Load everything first
all_analyses = [service.analyze_file(f) for f in files]  # Memory spike!
```

2. **Clear Caches Periodically**
```python
# Clear service caches after analysis
service._analysis_service = None
service._graph_service = None
```

3. **Use Generators**
```python
# Return generator instead of list
def analyze_files_generator(files):
    for file in files:
        yield analyze_file(file)
```

---

## Common Patterns

### Error Handling

**Pattern**: Graceful degradation, never fail completely

```python
def analyze_file(file_path: Path) -> Optional[FileAnalysis]:
    """Analyze single file with graceful error handling."""
    try:
        # Attempt full analysis
        line_counts = count_lines(file_path)
        tree = parse_python_ast(file_path)

        if tree is None:
            # Parse failed, return minimal analysis
            return FileAnalysis(
                file_path=str(file_path),
                total_lines=line_counts["total_lines"],
                code_lines=line_counts["code_lines"],
                # ... defaults for other fields
            )

        # Continue with full analysis
        functions = extract_functions(tree, file_path)
        # ...

    except Exception as e:
        # Log error but don't crash
        logger.error(f"Analysis failed for {file_path}: {e}")
        return None  # Caller handles None
```

---

### Progress Reporting

**Pattern**: Use Rich for beautiful terminal output

```python
from rich.console import Console
from rich.progress import track

console = Console()

def analyze_project_with_progress(file_paths):
    """Analyze project with progress bar."""
    results = []

    with console.status("[bold green]Analyzing files...") as status:
        for file_path in track(file_paths, description="Processing"):
            result = analyze_file(file_path)
            results.append(result)
            status.update(f"[bold green]Analyzed {len(results)} files...")

    return results
```

---

### Rich Terminal Output

**Pattern**: Use Rich tables for structured output

```python
from rich.console import Console
from rich.table import Table

def display_analysis_results(analysis: ProjectAnalysis):
    """Display analysis with Rich table."""
    console = Console()

    # Create table
    table = Table(title="Project Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    # Add rows
    table.add_row("Total Files", str(analysis.total_files))
    table.add_row("Code Lines", str(analysis.total_code_lines))
    table.add_row("Avg Complexity", f"{analysis.avg_complexity:.2f}")
    table.add_row("Avg MI", f"{analysis.avg_maintainability:.1f}")

    console.print(table)
```

---

### JSON/YAML Serialization

**Pattern**: Use Pydantic's built-in serialization

```python
from agentpm.core.database.models.detection_analysis import ProjectAnalysis
import json

# Serialize to JSON
analysis = service.analyze_project()
json_str = analysis.model_dump_json(indent=2)

# Save to file
Path("analysis.json").write_text(json_str)

# Deserialize
loaded_analysis = ProjectAnalysis.model_validate_json(json_str)

# Dictionary representation
analysis_dict = analysis.model_dump()
```

---

## Conclusion

This guide covered the Detection Pack's three-layer architecture and showed how to:

- Use Layer 1 utilities for AST parsing, graph building, and metrics
- Work with Layer 2 Pydantic models for type safety
- Extend Layer 3 services with new features
- Add pattern detectors, fitness policies, and CLI commands
- Write comprehensive tests with >90% coverage
- Optimize for performance in large projects

**Key Takeaways**:

1. **Respect Layer Boundaries**: Layer 1 utilities are pure, services orchestrate
2. **Use Pydantic Models**: Type safety prevents runtime errors
3. **Cache Aggressively**: File and graph caching is essential for performance
4. **Test Thoroughly**: Unit tests for utilities, integration tests for services
5. **Graceful Degradation**: Return partial results on error, never crash

**Next Steps**:

- Read user guide: `docs/guides/user_guide/detection-overview.md`
- Explore code examples: `testing/test-detection-flow/`
- Run tests: `pytest tests/unit/detection/ -v`
- Contribute: Follow patterns in this guide

**Questions?** Open an issue or check the developer chat in AIPM discussions.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-24
**Maintained By**: APM (Agent Project Manager) Detection Pack Team
