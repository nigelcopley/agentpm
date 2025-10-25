# External Tool Integration Analysis for APM (Agent Project Manager) Detection Pack Enhancement

**Task Reference**: #975
**Related Architecture**: Task #958
**Research Date**: 2025-10-24
**Time Investment**: 4 hours
**Researcher**: AIPM Research Agent

---

## Executive Summary

This document provides a comprehensive analysis of external tools for integrating with APM (Agent Project Manager)'s Detection Pack Enhancement. The research focuses on four critical capabilities: static code analysis, dependency graph modeling, SBOM generation, and license detection.

### Key Recommendations

1. **Static Analysis**: Use Python's built-in `ast` module with `Radon` for complexity metrics
2. **Graph Modeling**: Adopt `NetworkX` for dependency graphs with JSON serialization
3. **SBOM Generation**: Implement `CycloneDX` Python library for comprehensive SBOM support
4. **License Detection**: Use `pip-licenses` for basic needs, `importlib.metadata` for lightweight integration

---

## 1. Static Analysis Tools

### 1.1 Python AST Module

**Purpose**: Parse and analyze Python source code via Abstract Syntax Trees

**Integration**: Built-in Python standard library (Python 3.9+)

**Key Capabilities**:
- Parse Python source into traversable AST
- Visit pattern for node inspection
- Transform pattern for code modification
- Source-to-AST-to-source roundtrip support

**API Examples**:

```python
import ast

# Parse source code
tree = ast.parse(source_code)

# Visitor pattern for analysis
class DependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ''
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

# Use the visitor
visitor = DependencyVisitor()
visitor.visit(tree)
print(visitor.imports)

# Convert AST back to code
code = ast.unparse(tree)
```

**Dependencies**: None (standard library)

**Pros**:
- Zero installation overhead
- Official Python implementation
- Fast and reliable
- Comprehensive node types for all Python syntax
- Well-documented

**Cons**:
- Requires Python version awareness (syntax varies by version)
- Lower-level API requires custom visitor implementations
- No built-in metrics (complexity, maintainability)

**Recommendation**: ✅ **USE** - Essential foundation for Python static analysis. Required for accurate dependency detection.

---

### 1.2 Jedi

**Purpose**: Autocompletion, static analysis, and code introspection for Python

**Integration**: `pip install jedi`

**Key Capabilities**:
- Code completion and goto functionality
- Type inference
- Find references and usages
- Syntax error detection
- Module search capabilities

**API Examples**:

```python
import jedi

# Get completions
script = jedi.Script(code=source_code)
completions = script.complete(line=10, column=5)

# Find definitions
definitions = script.goto(line=10, column=5)

# Get syntax errors
errors = script.get_syntax_errors()

# Search for names
names = script.get_names()
```

**Dependencies**: `jedi` (pip-installable)

**Pros**:
- Excellent type inference
- Widely used in IDEs (VS Code, Vim, Emacs)
- Understands complex Python semantics
- Works with IPython out-of-the-box

**Cons**:
- Designed for IDE use cases (not analysis pipelines)
- Heavier than AST module
- May be overkill for dependency detection
- Less control over traversal patterns

**Recommendation**: ⚠️ **SKIP** - Powerful but designed for interactive IDE features. Overkill for AIPM's static dependency analysis needs. Use AST module instead.

---

### 1.3 Rope

**Purpose**: Python refactoring library with AST manipulation

**Integration**: `pip install rope`

**Key Capabilities**:
- Advanced refactoring operations
- AST pattern matching and restructuring
- Code transformation
- Wrapper around stdlib AST module

**API Examples**:

```python
from rope.base.project import Project
from rope.refactor.rename import Rename

# Create project
project = Project('.')

# Perform refactoring
resource = project.root.get_file('mymodule.py')
offset = resource.read().index('old_name')
renamer = Rename(project, resource, offset)
changes = renamer.get_changes('new_name')
project.do(changes)
```

**Dependencies**: `rope` (pip-installable)

**Pros**:
- Sophisticated refactoring capabilities
- AST pattern matching
- Project-aware analysis

**Cons**:
- Designed for refactoring, not detection
- Depends on Python version it's running under (historical limitation)
- More complex API than raw AST
- Heavier installation

**Recommendation**: ⚠️ **SKIP** - Purpose-built for refactoring operations. AIPM needs detection/analysis, not transformation. Use AST module for better control.

---

### 1.4 Radon

**Purpose**: Code complexity metrics calculator

**Integration**: `pip install radon`

**Key Capabilities**:
- Cyclomatic complexity (McCabe)
- Maintainability Index (Visual Studio formula)
- Raw metrics (SLOC, comments, blanks)
- Halstead metrics
- Programmatic API and CLI

**API Examples**:

```python
from radon.complexity import cc_visit, cc_rank
from radon.raw import analyze
from radon.visitors import ComplexityVisitor

# Cyclomatic complexity
results = cc_visit(source_code)
for result in results:
    print(f"{result.name}: Complexity {result.complexity}, Rank {cc_rank(result.complexity)}")

# Raw metrics
metrics = analyze(source_code)
print(f"SLOC: {metrics.sloc}, Comments: {metrics.comments}")

# Using visitors (lower-level)
visitor = ComplexityVisitor.from_code(source_code)
for func in visitor.functions:
    print(f"{func.name}: {func.complexity}")
```

**Dependencies**: `radon` (pip-installable, pure Python)

**Pros**:
- Comprehensive metrics suite
- Simple programmatic API
- Works via AST analysis
- Lightweight installation
- Both CLI and library modes

**Cons**:
- Maintainability Index is experimental
- Metrics focused (doesn't extract dependencies)
- Requires separate tool for dependency analysis

**Recommendation**: ✅ **USE** - Excellent complement to AST module. Use for code quality metrics after dependency detection. Lightweight and focused.

---

### 1.5 Pylint & Flake8

**Purpose**: Code linters for quality and style checking

**Integration**: `pip install pylint flake8`

**Key Capabilities**:
- **Pylint**: Comprehensive analysis, complexity metrics, quality scoring (0-10)
- **Flake8**: Faster, simpler, combines Pyflakes + pycodestyle + McCabe

**API Examples**:

```python
# Pylint programmatic access
from pylint.lint import Run
from pylint import epylint as lint

# Run analysis
(stdout, stderr) = lint.py_run('mymodule.py', return_std=True)

# Flake8 programmatic access
from flake8.api import legacy as flake8

style_guide = flake8.get_style_guide()
report = style_guide.check_files(['mymodule.py'])
```

**Dependencies**: `pylint`, `flake8` (pip-installable)

**Pros**:
- Industry-standard linters
- Extensive rule sets
- Configurable
- Pylint provides quality scoring
- Flake8 is fast and lightweight

**Cons**:
- Designed for linting, not dependency extraction
- Pylint is slow on large codebases
- Flake8 lacks quality scoring
- Not ideal for programmatic pipeline integration

**Recommendation**: ⚠️ **CONDITIONAL** - Useful for quality gates and reporting, but not for dependency detection. Consider for future quality validation features. Use `pylintdb` if programmatic access to results is needed.

---

## 2. Graph Libraries

### 2.1 NetworkX

**Purpose**: Network/graph data structure and algorithms

**Integration**: `pip install networkx`

**Key Capabilities**:
- Comprehensive graph algorithms (shortest path, clustering, cycles)
- Flexible node/edge data storage (any Python object)
- Multiple serialization formats (JSON, GraphML, GML, pickle)
- Visualization hooks (Matplotlib, Graphviz, VTK)
- Scales to 10M+ nodes, 100M+ edges

**API Examples**:

```python
import networkx as nx
from networkx.readwrite import json_graph
import json

# Create directed graph for dependencies
G = nx.DiGraph()

# Add nodes with metadata
G.add_node('module_a', type='module', loc=250)
G.add_node('module_b', type='module', loc=180)

# Add edges with metadata
G.add_edge('module_a', 'module_b', import_type='direct', weight=1.0)

# Graph algorithms
cycles = list(nx.simple_cycles(G))
shortest_path = nx.shortest_path(G, 'module_a', 'module_b')
strongly_connected = list(nx.strongly_connected_components(G))

# Serialization - JSON (recommended for AIPM)
data = json_graph.node_link_data(G)
with open('dependencies.json', 'w') as f:
    json.dump(data, f, indent=2)

# Load from JSON
with open('dependencies.json', 'r') as f:
    data = json.load(f)
    G_loaded = json_graph.node_link_graph(data)

# Serialization - GraphML
nx.write_graphml(G, 'dependencies.graphml')
G_loaded = nx.read_graphml('dependencies.graphml')

# Visualization (optional)
import matplotlib.pyplot as plt
nx.draw(G, with_labels=True)
plt.savefig('graph.png')
```

**Dependencies**: `networkx` (pip-installable, pure Python)

**Pros**:
- Most popular Python graph library (50M+ downloads)
- Pure Python (easy installation)
- Rich algorithm library
- Flexible data model
- JSON serialization (perfect for AIPM database)
- Well-documented
- Active development

**Cons**:
- Slower than C++-based alternatives (igraph, graph-tool)
- Not ideal for graphs >100M edges
- Performance-sensitive operations may need optimization

**Recommendation**: ✅ **USE** - Perfect fit for AIPM. Pure Python, flexible, JSON-serializable, comprehensive algorithms. Performance adequate for typical project dependency graphs (thousands to tens of thousands of nodes).

---

### 2.2 Graphviz & PyDot

**Purpose**: Graph visualization using DOT language

**Integration**: `pip install graphviz pydot` (requires Graphviz binary installation)

**Key Capabilities**:
- Generate DOT format graphs
- Multiple layout algorithms (dot, neato, fdp, circo, twopi)
- Export to PNG, SVG, PDF
- Integration with NetworkX

**API Examples**:

```python
# Using graphviz package
from graphviz import Digraph

dot = Digraph(comment='Dependency Graph')
dot.node('A', 'Module A')
dot.node('B', 'Module B')
dot.edge('A', 'B', label='imports')
dot.render('dependency_graph', format='png')

# Using pydot
import pydot

graph = pydot.Dot(graph_type='digraph')
node_a = pydot.Node('A', label='Module A')
node_b = pydot.Node('B', label='Module B')
graph.add_node(node_a)
graph.add_node(node_b)
graph.add_edge(pydot.Edge(node_a, node_b))
graph.write_png('dependency.png')

# NetworkX integration
import networkx as nx
from networkx.drawing.nx_pydot import write_dot

G = nx.DiGraph()
G.add_edge('A', 'B')
write_dot(G, 'graph.dot')
```

**Dependencies**:
- `graphviz` or `pydot` (pip-installable)
- Graphviz binary (system installation required: `brew install graphviz` on macOS)

**Pros**:
- Professional-quality visualizations
- Multiple layout algorithms
- Industry-standard DOT format
- NetworkX integration

**Cons**:
- Requires external binary installation
- Not a graph computation library
- Visualization-focused, not analysis-focused
- Additional dependency complexity

**Recommendation**: ⚠️ **OPTIONAL** - Use only for visualization features. Not needed for core dependency detection. NetworkX provides sufficient graph modeling. Add later if visual graph export is required.

---

### 2.3 igraph & graph-tool (Alternatives)

**Purpose**: High-performance graph libraries in C/C++ with Python bindings

**Performance Comparison** (from benchmarks):
- **graph-tool**: Fastest (C++, Boost Graph Library)
- **igraph**: Fast (C core)
- **NetworkX**: 40-250x slower than graph-tool

**Integration**: `pip install igraph` or `conda install graph-tool`

**Pros**:
- Significantly faster for large graphs
- Comprehensive algorithm implementations
- Memory efficient

**Cons**:
- **graph-tool**: Difficult to install (requires compilation, C++ dependencies)
- **igraph**: Easier than graph-tool, but still requires C compilation
- Less Pythonic APIs
- More complex installation
- Overkill for typical project sizes

**Recommendation**: ❌ **SKIP** - NetworkX performance is adequate for AIPM's use case (project dependency graphs are typically <10K nodes). Pure Python installation is preferable to C++ compilation requirements. Consider only if performance benchmarks show NetworkX is a bottleneck.

---

## 3. SBOM Generation Tools

### 3.1 CycloneDX Python Library

**Purpose**: Generate CycloneDX-format SBOMs for Python projects

**Integration**: `pip install cyclonedx-bom cyclonedx-python-lib`

**Key Capabilities**:
- Generate OWASP CycloneDX SBOMs (industry standard)
- Support multiple input sources (pip, Pipenv, Poetry, conda)
- Track direct and transitive dependencies
- Component metadata (name, version, licenses, hashes)
- Level-2 SBOM compliance (per OWASP SCVS)
- JSON and XML output formats

**API Examples**:

```python
# Using cyclonedx-python-lib (programmatic)
from cyclonedx.model.bom import Bom
from cyclonedx.parser.environment import EnvironmentParser
from cyclonedx.output import get_instance, OutputFormat, SchemaVersion

# Parse current environment
parser = EnvironmentParser()
bom = Bom.from_parser(parser=parser)

# Output as JSON
outputter = get_instance(bom=bom, output_format=OutputFormat.JSON)
json_sbom = outputter.output_as_string()

# Output to file
outputter = get_instance(
    bom=bom,
    output_format=OutputFormat.JSON,
    schema_version=SchemaVersion.V1_5
)
outputter.output_to_file(filename='sbom.json')

# CLI usage
# cyclonedx-py --requirements requirements.txt --output sbom.json
# cyclonedx-py --environment --output sbom.json
```

**Dependencies**:
- `cyclonedx-python-lib` (core library)
- `cyclonedx-bom` (CLI tool)
- `pyparsing` (transitive dependency)

**Pros**:
- Most accurate Python SBOM generator
- Industry-standard CycloneDX format
- Both programmatic API and CLI
- Captures transitive dependencies
- Includes license detection
- Validates against schema
- Active development (v7.2.0 as of 2024)

**Cons**:
- CycloneDX format may require learning curve
- Heavier than simple alternatives
- Requires environment or requirements file

**Recommendation**: ✅ **USE** - Best-in-class SBOM generation for Python. Industry-standard format. Essential for supply chain security features in AIPM. Programmatic API fits well with detection pipeline.

---

### 3.2 SPDX Tools

**Purpose**: Generate and validate SPDX-format SBOMs

**Integration**: `pip install spdx-tools`

**Key Capabilities**:
- Parse, validate, create SPDX documents
- License expression validation
- Multiple SPDX format support
- Integration with `license-expression` library

**API Examples**:

```python
from spdx_tools.spdx.parser.parse_anything import parse_file
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

# Parse SPDX file
document = parse_file('sbom.spdx')

# Validate
validation_messages = validate_full_spdx_document(document)

# License expression handling
from license_expression import get_spdx_licensing

licensing = get_spdx_licensing()
expression = licensing.parse('MIT OR Apache-2.0')
```

**Dependencies**: `spdx-tools`, `license-expression` (pip-installable)

**Pros**:
- Official SPDX implementation
- License expression validation
- Multiple SPDX versions supported
- License compliance focus

**Cons**:
- SPDX format less widely adopted than CycloneDX in Python ecosystem
- Primarily a validator/parser, not a generator
- No built-in Python environment scanning
- Requires external tools for SBOM creation

**Recommendation**: ⚠️ **OPTIONAL** - Use if SPDX format is specifically required. CycloneDX is more practical for Python projects. Consider for license validation features, not primary SBOM generation.

---

### 3.3 pip-licenses

**Purpose**: Extract license information from installed packages

**Integration**: `pip install pip-licenses`

**Key Capabilities**:
- List licenses of installed packages
- Multiple output formats (table, JSON, CSV, Markdown)
- Include URLs, descriptions, license file contents
- PEP 639 License-Expression support

**API Examples**:

```python
# Primarily CLI-based
# pip-licenses
# pip-licenses --format=json --output-file=licenses.json
# pip-licenses --with-urls --with-description
# pip-licenses --with-license-file --no-license-path

# For programmatic access, use pip-licenses-lib
from pip_licenses import get_packages

packages = get_packages()
for pkg in packages:
    print(f"{pkg['Name']}: {pkg['License']}")
```

**Dependencies**: `pip-licenses` (pip-installable, pure Python)

**Pros**:
- Simple, focused tool
- Lightweight
- Multiple output formats
- Easy to integrate in CI/CD
- PEP 639 support

**Cons**:
- License-only (not full SBOM)
- CLI-first (limited programmatic API)
- Doesn't track dependencies
- Separate tool from SBOM generation

**Recommendation**: ⚠️ **CONDITIONAL** - Use for quick license audits or if CycloneDX is too heavy. Not a replacement for full SBOM generation. Good for interim license compliance checks.

---

### 3.4 pipdeptree

**Purpose**: Visualize Python package dependency trees

**Integration**: `pip install pipdeptree`

**Key Capabilities**:
- Display dependency trees
- JSON output for programmatic parsing
- Reverse dependency lookup
- Conflict detection
- Freeze-format output

**API Examples**:

```python
# Primarily CLI-based
# pipdeptree
# pipdeptree --json-tree > dependencies.json
# pipdeptree --reverse
# pipdeptree --packages numpy
# pipdeptree --freeze

# Parse JSON output programmatically
import subprocess
import json

result = subprocess.run(['pipdeptree', '--json-tree'], capture_output=True, text=True)
dep_tree = json.loads(result.stdout)

for package in dep_tree:
    print(f"{package['package']['key']}: {len(package['dependencies'])} deps")
```

**Dependencies**: `pipdeptree` (pip-installable, pure Python)

**Pros**:
- Simple dependency visualization
- JSON output for parsing
- Conflict detection
- Lightweight
- Works with virtualenvs

**Cons**:
- CLI-first design
- Limited programmatic API
- Not a full SBOM (no hashes, checksums, licenses)
- Overlaps with CycloneDX functionality

**Recommendation**: ⚠️ **OPTIONAL** - Useful for debugging dependency issues during development. CycloneDX provides superior dependency tracking for production SBOM needs. Consider for development/debugging tools.

---

## 4. License Detection Tools

### 4.1 scancode-toolkit

**Purpose**: Comprehensive license, copyright, and package manifest scanner

**Integration**: `pip install scancode-toolkit`

**Key Capabilities**:
- Industry-leading license detection (31,000+ rules)
- Full text comparison (not just regex/probabilistic)
- Copyright and author detection
- Package manifest parsing
- Binary file scanning
- Multiple output formats (JSON, YAML, SPDX, CycloneDX, HTML, CSV)

**API Examples**:

```python
# Primarily CLI-based, but provides programmatic access
# scancode -clpieu --json output.json /path/to/code

# Using as a library (from documentation)
from scancode.api import get_copyrights, get_licenses

# Scan for licenses
licenses = get_licenses('/path/to/file.py')
for license_match in licenses:
    print(f"License: {license_match['key']}, Score: {license_match['score']}")

# Scan for copyrights
copyrights = get_copyrights('/path/to/file.py')
for copyright_match in copyrights:
    print(f"Copyright: {copyright_match['copyright']}")
```

**Dependencies**: `scancode-toolkit` (pip-installable, but large installation ~200MB)

**Pros**:
- Best-in-class license detection accuracy
- Industry standard (used by Eclipse, FSFE, Red Hat, ClearlyDefined)
- Comprehensive rule engine (31K+ rules)
- Multiple output formats including SBOM formats
- Detects licenses in binaries
- Extensible plugin architecture

**Cons**:
- Heavy installation (~200MB)
- Slower than lightweight alternatives
- Overkill for simple package license extraction
- Better suited for full codebase scanning

**Recommendation**: ⚠️ **CONDITIONAL** - Use if AIPM needs to scan source code for embedded licenses (not just package metadata). Overkill for dependency license detection (use `importlib.metadata` or `pip-licenses` instead). Excellent for comprehensive license compliance auditing.

---

### 4.2 importlib.metadata (Standard Library)

**Purpose**: Access installed package metadata including licenses

**Integration**: Built-in (Python 3.8+)

**Key Capabilities**:
- Read package metadata from dist-info/egg-info
- Access license field
- Entry points, dependencies, version info
- Replaces older `pkg_resources`

**API Examples**:

```python
from importlib.metadata import metadata, packages_distributions, version

# Get license for a package
pkg_metadata = metadata('requests')
license_info = pkg_metadata.get('License', 'Unknown')
print(f"License: {license_info}")

# Iterate all installed packages
from importlib.metadata import distributions

for dist in distributions():
    name = dist.metadata['Name']
    version = dist.metadata['Version']
    license_val = dist.metadata.get('License', 'UNKNOWN')
    print(f"{name} {version}: {license_val}")

# Get package version
ver = version('numpy')
```

**Dependencies**: None (standard library Python 3.8+)

**Pros**:
- Zero installation overhead
- Fast and lightweight
- Official Python API
- Replaces deprecated `pkg_resources`
- Direct access to package metadata

**Cons**:
- Only reads package metadata (may be incomplete or inaccurate)
- Doesn't scan source code
- License field formatting inconsistent across packages
- No license expression parsing

**Recommendation**: ✅ **USE** - Perfect lightweight option for basic license detection from package metadata. Use for quick dependency license checks. Complement with CycloneDX for full SBOM generation.

---

### 4.3 pip-license-checker

**Purpose**: License compliance checking for dependencies

**Integration**: `pip install pip-license-checker`

**Key Capabilities**:
- Detect license types (permissive, copyleft, proprietary)
- Fail builds on non-compliant licenses
- License policy enforcement

**API Examples**:

```python
# Primarily CLI-based
# pip-license-checker --permissive-only
# pip-license-checker --copyleft-only
# pip-license-checker --fail-on proprietary

# Configuration via pyproject.toml
# [tool.pip-license-checker]
# allowed = ["MIT", "Apache-2.0", "BSD-3-Clause"]
# forbidden = ["GPL-3.0"]
```

**Dependencies**: `pip-license-checker` (pip-installable)

**Pros**:
- Policy enforcement focus
- License type categorization
- CI/CD integration
- Configuration file support

**Cons**:
- CLI-first (limited programmatic API)
- Less comprehensive than scancode-toolkit
- Primarily for compliance checking, not detection
- Relies on package metadata (same limitations as importlib.metadata)

**Recommendation**: ⚠️ **OPTIONAL** - Use for license policy gates in CI/CD. Not needed for detection (use `importlib.metadata`). Good for governance features.

---

## 5. Summary and Recommendations

### Recommended Tool Stack for APM (Agent Project Manager) Detection Pack

| Capability | Tool | Priority | Rationale |
|-----------|------|----------|-----------|
| **Python Parsing** | `ast` (stdlib) | ESSENTIAL | Zero-dependency, accurate, comprehensive |
| **Complexity Metrics** | `radon` | HIGH | Lightweight, focused, good API |
| **Graph Modeling** | `networkx` | ESSENTIAL | Pure Python, JSON-serializable, rich algorithms |
| **SBOM Generation** | `cyclonedx-bom` | HIGH | Industry standard, comprehensive, programmatic API |
| **License Detection** | `importlib.metadata` | HIGH | Built-in, fast, adequate for package metadata |

### Optional/Future Tools

| Capability | Tool | Use Case |
|-----------|------|----------|
| **Visualization** | `graphviz` / `pydot` | Export visual dependency graphs |
| **Dependency Tree** | `pipdeptree` | Debugging/development tooling |
| **License Policy** | `pip-license-checker` | CI/CD compliance gates |
| **License Auditing** | `scancode-toolkit` | Deep source code license scanning |

### Not Recommended

| Tool | Reason |
|------|--------|
| `jedi` | Designed for IDEs, overkill for static analysis |
| `rope` | Refactoring focus, not analysis |
| `pylint`/`flake8` | Linting focus, not dependency detection |
| `igraph`/`graph-tool` | C++ compilation required, unnecessary complexity |
| `SPDX Tools` | Less practical than CycloneDX for Python |

---

## 6. Integration Architecture

### Recommended Data Flow

```
┌─────────────────┐
│ Python Source   │
│ Files           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AST Parser      │  ← Python stdlib ast
│ (ast module)    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Dependency      │  │ Complexity      │
│ Extractor       │  │ Analyzer        │
│                 │  │ (radon)         │
└────────┬────────┘  └────────┬────────┘
         │                    │
         ▼                    │
┌─────────────────┐           │
│ NetworkX Graph  │           │
│ Builder         │           │
└────────┬────────┘           │
         │                    │
         ├────────────────────┘
         │
         ▼
┌─────────────────┐
│ Graph Analysis  │  ← cycles, clustering, paths
│ (NetworkX)      │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ SBOM Generator  │  │ License         │
│ (CycloneDX)     │  │ Detector        │
│                 │  │ (importlib)     │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └─────────┬──────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ AIPM Database (JSON storage)        │
│ - Dependency graphs (NetworkX JSON) │
│ - SBOMs (CycloneDX JSON)            │
│ - Metrics (Radon data structures)   │
│ - Licenses (SPDX identifiers)       │
└─────────────────────────────────────┘
```

---

## 7. Installation Requirements

### Minimal Setup (Core Detection)

```bash
# No installation needed
# Python 3.9+ with stdlib only
```

### Recommended Setup (Full Features)

```bash
pip install radon networkx cyclonedx-bom cyclonedx-python-lib
```

**Total Installation Size**: ~15-20 MB
**Dependencies**: Pure Python (no C compilation)
**Python Version**: 3.9+

### Optional Setup (Extended Features)

```bash
# Visualization
pip install graphviz pydot
brew install graphviz  # or apt-get install graphviz

# Development tools
pip install pipdeptree pip-licenses

# Deep license scanning (heavy)
pip install scancode-toolkit  # ~200MB
```

---

## 8. Code Examples: Integration Patterns

### 8.1 Dependency Detection with AST

```python
import ast
from pathlib import Path
from typing import List, Dict

class DependencyDetector(ast.NodeVisitor):
    """Detect imports and dependencies from Python source."""

    def __init__(self):
        self.imports: List[Dict] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append({
                'module': alias.name,
                'alias': alias.asname,
                'type': 'import',
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ''
        for alias in node.names:
            self.imports.append({
                'module': module,
                'name': alias.name,
                'alias': alias.asname,
                'type': 'from_import',
                'level': node.level,
                'line': node.lineno
            })
        self.generic_visit(node)

def detect_dependencies(source_file: Path) -> List[Dict]:
    """Extract dependencies from a Python file."""
    source_code = source_file.read_text()
    tree = ast.parse(source_code, filename=str(source_file))

    detector = DependencyDetector()
    detector.visit(tree)

    return detector.imports
```

### 8.2 Complexity Analysis with Radon

```python
from radon.complexity import cc_visit, cc_rank
from radon.raw import analyze
from pathlib import Path
from typing import Dict, Any

def analyze_code_quality(source_file: Path) -> Dict[str, Any]:
    """Analyze code complexity and quality metrics."""
    source_code = source_file.read_text()

    # Cyclomatic complexity
    complexity_results = cc_visit(source_code)

    # Raw metrics
    raw_metrics = analyze(source_code)

    return {
        'file': str(source_file),
        'complexity': [
            {
                'name': result.name,
                'complexity': result.complexity,
                'rank': cc_rank(result.complexity),
                'lineno': result.lineno
            }
            for result in complexity_results
        ],
        'metrics': {
            'sloc': raw_metrics.sloc,
            'loc': raw_metrics.loc,
            'comments': raw_metrics.comments,
            'multi': raw_metrics.multi,
            'blank': raw_metrics.blank
        }
    }
```

### 8.3 Dependency Graph with NetworkX

```python
import networkx as nx
from networkx.readwrite import json_graph
import json
from typing import List, Dict
from pathlib import Path

def build_dependency_graph(dependencies: Dict[str, List[str]]) -> nx.DiGraph:
    """Build a directed graph from dependency data."""
    G = nx.DiGraph()

    for module, deps in dependencies.items():
        G.add_node(module, type='module')

        for dep in deps:
            G.add_node(dep, type='dependency')
            G.add_edge(module, dep, import_type='direct')

    return G

def detect_cycles(G: nx.DiGraph) -> List[List[str]]:
    """Detect circular dependencies."""
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except nx.NetworkXNoCycle:
        return []

def save_graph(G: nx.DiGraph, output_path: Path):
    """Save graph as JSON."""
    data = json_graph.node_link_data(G)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_graph(input_path: Path) -> nx.DiGraph:
    """Load graph from JSON."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    return json_graph.node_link_graph(data)
```

### 8.4 SBOM Generation with CycloneDX

```python
from cyclonedx.model.bom import Bom
from cyclonedx.parser.environment import EnvironmentParser
from cyclonedx.output import get_instance, OutputFormat, SchemaVersion
from pathlib import Path

def generate_sbom(output_path: Path) -> str:
    """Generate CycloneDX SBOM for current environment."""

    # Parse Python environment
    parser = EnvironmentParser()
    bom = Bom.from_parser(parser=parser)

    # Configure output
    outputter = get_instance(
        bom=bom,
        output_format=OutputFormat.JSON,
        schema_version=SchemaVersion.V1_5
    )

    # Write to file
    outputter.output_to_file(filename=str(output_path))

    # Return JSON string
    return outputter.output_as_string()

def parse_sbom(sbom_path: Path) -> Dict:
    """Parse CycloneDX SBOM JSON."""
    import json
    with open(sbom_path, 'r') as f:
        return json.load(f)
```

### 8.5 License Detection with importlib.metadata

```python
from importlib.metadata import distributions, version, metadata
from typing import List, Dict

def detect_licenses() -> List[Dict[str, str]]:
    """Extract licenses from all installed packages."""
    licenses = []

    for dist in distributions():
        name = dist.metadata.get('Name', 'UNKNOWN')
        ver = dist.metadata.get('Version', 'UNKNOWN')
        license_val = dist.metadata.get('License', 'UNKNOWN')

        licenses.append({
            'name': name,
            'version': ver,
            'license': license_val
        })

    return licenses

def get_package_license(package_name: str) -> str:
    """Get license for a specific package."""
    try:
        pkg_metadata = metadata(package_name)
        return pkg_metadata.get('License', 'UNKNOWN')
    except Exception:
        return 'NOT_FOUND'
```

---

## 9. Performance Considerations

### Benchmarking (Estimated)

| Operation | Tool | Performance | Notes |
|-----------|------|-------------|-------|
| Parse 1000 Python files | `ast` | ~2-5 seconds | Fast, stdlib |
| Complexity analysis | `radon` | ~5-10 seconds | Pure Python |
| Build dependency graph | `networkx` | ~1-2 seconds | Graph construction |
| Cycle detection (1000 nodes) | `networkx` | <1 second | Efficient algorithms |
| Generate SBOM | `cyclonedx` | ~5-10 seconds | Environment scanning |
| License extraction | `importlib.metadata` | <1 second | Metadata lookup |

**Total Pipeline (1000 files)**: ~15-30 seconds
**Memory Usage**: <200 MB for typical projects

### Optimization Strategies

1. **Parallel Processing**: Use `multiprocessing` for AST parsing across multiple files
2. **Caching**: Cache parsed ASTs and complexity results
3. **Incremental Analysis**: Only re-analyze changed files
4. **Graph Persistence**: Store NetworkX graphs as JSON in database

---

## 10. Risk Assessment

### Low Risk Tools
- `ast` (stdlib): Mature, stable, well-tested
- `importlib.metadata` (stdlib): Official replacement for pkg_resources
- `networkx`: Industry standard, 50M+ downloads

### Medium Risk Tools
- `radon`: Smaller project, but stable and focused
- `cyclonedx-bom`: Active development, but version changes may affect API

### Mitigation Strategies
1. **Pin versions** in `requirements.txt`
2. **Test coverage** for integration points
3. **Fallback mechanisms** for optional tools
4. **Version compatibility testing** in CI/CD

---

## 11. Licensing Compatibility

| Tool | License | AIPM Compatible? |
|------|---------|------------------|
| `ast` | Python Software Foundation License | ✅ Yes |
| `radon` | MIT | ✅ Yes |
| `networkx` | BSD-3-Clause | ✅ Yes |
| `cyclonedx-bom` | Apache-2.0 | ✅ Yes |
| `cyclonedx-python-lib` | Apache-2.0 | ✅ Yes |
| `importlib.metadata` | Python Software Foundation License | ✅ Yes |
| `graphviz` | MIT | ✅ Yes |
| `pydot` | MIT | ✅ Yes |
| `pip-licenses` | MIT | ✅ Yes |
| `scancode-toolkit` | Apache-2.0 + CC-BY-4.0 | ✅ Yes |

All recommended tools are compatible with AIPM's licensing requirements.

---

## 12. Next Steps

### Immediate Actions (Task #975 Implementation)

1. **Install core dependencies**:
   ```bash
   pip install radon networkx cyclonedx-bom cyclonedx-python-lib
   ```

2. **Implement AST-based dependency detector** (see Section 8.1)

3. **Build NetworkX graph builder** (see Section 8.3)

4. **Integrate Radon for complexity metrics** (see Section 8.2)

5. **Implement SBOM generator** (see Section 8.4)

6. **Add license detector** (see Section 8.5)

### Future Enhancements

1. **Visualization**: Add graphviz integration for visual dependency exports
2. **Deep License Scanning**: Integrate scancode-toolkit for source code license detection
3. **Policy Enforcement**: Add pip-license-checker for compliance gates
4. **Performance Optimization**: Benchmark and optimize for large codebases

---

## 13. References

### Documentation
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [Radon Documentation](https://radon.readthedocs.io/)
- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)
- [importlib.metadata](https://docs.python.org/3/library/importlib.metadata.html)

### Benchmarks
- [Graph Library Performance Comparison](https://www.timlrx.com/blog/benchmark-of-popular-graph-network-packages-v2)
- [Python Linter Comparison](https://inventwithpython.com/blog/2022/11/19/python-linter-comparison-2022-pylint-vs-pyflakes-vs-flake8-vs-autopep8-vs-bandit-vs-prospector-vs-pylama-vs-pyroma-vs-black-vs-mypy-vs-radon-vs-mccabe/)

### Standards
- [OWASP CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [SPDX Specification](https://spdx.org/specifications)
- [PEP 639 - License Metadata](https://peps.python.org/pep-0639/)

---

## Appendix: Quick Reference

### Installation Commands

```bash
# Core (recommended)
pip install radon networkx cyclonedx-bom cyclonedx-python-lib

# Optional visualization
pip install graphviz pydot
brew install graphviz  # macOS

# Optional development tools
pip install pipdeptree pip-licenses

# Optional deep scanning (heavy)
pip install scancode-toolkit
```

### CLI Quick Reference

```bash
# Radon
radon cc -a -s src/              # Cyclomatic complexity
radon mi -s src/                 # Maintainability index
radon raw src/                   # Raw metrics

# CycloneDX
cyclonedx-py --requirements requirements.txt --output sbom.json
cyclonedx-py --environment --output sbom-env.json

# pip-licenses
pip-licenses --format=json --output-file=licenses.json

# pipdeptree
pipdeptree --json-tree > dependencies.json
pipdeptree --reverse --packages requests

# scancode-toolkit
scancode --license --copyright --json output.json src/
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24
**Confidence Level**: High (based on official documentation and benchmarks)
**Estimated Effort to Implement**: 8-16 hours for core integration
