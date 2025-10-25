# Detection Pack Enhancement - Technical Architecture

**Version**: 1.1.0
**Status**: Design Approved - Three-Layer Architecture
**Work Item**: #148
**Task**: #958
**Created**: 2025-10-24
**Updated**: 2025-10-24

---

## Executive Summary

This document specifies the architecture for enhancing APM (Agent Project Manager)'s detection system with comprehensive static analysis, dependency graph modeling, SBOM generation, domain pattern recognition, and architecture fitness testing capabilities.

**Design Philosophy**: Extend existing plugin infrastructure with graph-based detection capabilities while maintaining backward compatibility and following AIPM's three-layer pattern. Uses **three-layer architecture** to avoid circular dependencies between plugins and detection services.

**Key Technologies**: NetworkX (graph modeling), Python AST (static analysis), Policy engine (fitness testing), SQLite (caching)

---

## 1. System Overview

### 1.1 Current State Analysis

**Existing Components** (foundation to build upon):

```
agentpm/core/detection/
├── models.py                 # Pydantic models: TechnologyMatch, DetectionResult
├── indicators.py             # ProjectIndicators registry (languages, frameworks)
├── service.py                # DetectionService (main orchestration)
├── orchestrator.py           # DetectionOrchestrator (two-phase detection)
└── indicator_service.py      # Phase 1 fast indicator scanning

agentpm/core/plugins/
├── base/
│   ├── plugin_interface.py   # BasePlugin ABC
│   └── types.py             # PluginCategory, ProjectFacts, CodeAmalgamation
└── domains/
    ├── languages/           # Python, JavaScript, TypeScript plugins
    ├── frameworks/          # Django, Click, React, HTMX plugins
    ├── testing/             # Pytest plugin
    └── data/                # SQLite plugin
```

**Current Detection Flow**:
```
Phase 1: IndicatorService (fast scan, <100ms)
    ↓ (candidates: Set[str])
Phase 2: Plugin.detect() (selective, <500ms)
    ↓ (matches: Dict[str, TechnologyMatch])
DetectionResult
```

### 1.2 Enhancement Goals

Add comprehensive detection capabilities:

1. **Static Analysis**: AST parsing, code metrics, complexity analysis
2. **Dependency Graphs**: Build/visualize dependency graphs using NetworkX
3. **SBOM Generation**: Software Bill of Materials with license detection
4. **Domain Patterns**: Detect architectural patterns (Hexagonal, DDD, CQRS)
5. **Architecture Fitness**: Policy-based validation and compliance testing
6. **Performance**: Intelligent caching and lazy loading
7. **CLI Integration**: User-friendly commands for all capabilities

### 1.3 Three-Layer Architecture (No Circular Dependencies)

**Critical Design Decision**: To avoid circular dependencies between plugins (Layer 2) and detection services (Layer 3), we implement a **three-layer architecture** with shared utilities at the foundation:

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: Detection & Intelligence (Top Layer)                   │
│ core/detection/                                                  │
│   - Uses Layer 2 (plugins) for technology detection             │
│   - Uses Layer 1 (utils) for AST, graphs, metrics               │
│   - Provides high-level analysis services                       │
└─────────────────────────────────────────────────────────────────┘
                               ↑
                               │ (uses)
                               │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Technology Detection (Middle Layer)                    │
│ core/plugins/                                                    │
│   - Uses ONLY Layer 1 (utils)                                   │
│   - Does NOT import from Layer 3 (detection)                    │
│   - Technology-specific detection logic                         │
└─────────────────────────────────────────────────────────────────┘
                               ↑
                               │ (uses)
                               │
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Shared Utilities (Foundation Layer)                    │
│ core/plugins/utils/                                              │
│   - NO dependencies on Layer 2 or Layer 3                       │
│   - Pure utility functions and primitives                       │
│   - Shared by BOTH plugins AND detection services               │
└─────────────────────────────────────────────────────────────────┘
```

**Layer 1 Utilities** (Shared Foundation):
- **Existing**: `code_extractors.py`, `dependency_parsers.py`, `structure_analyzers.py`
- **NEW**: `ast_utils.py`, `graph_builders.py`, `metrics_calculator.py`, `pattern_matchers.py`, `file_parsers.py`

**Layer 2 Plugins** (Technology Detection):
- Use Layer 1 utilities for AST parsing, graph building, metrics
- Example: `PythonPlugin` uses `ast_utils.py` to parse Python files
- **Cannot** import from `core/detection/` (would create circular dependency)

**Layer 3 Detection** (Analysis Services):
- Use Layer 1 utilities for same primitives (AST, graphs, metrics)
- Use Layer 2 plugins for technology detection
- Example: `StaticAnalysisService` uses `ast_utils.py` directly
- Example: `DependencyGraphService` uses `graph_builders.py` directly

**Benefits**:
- ✅ No circular dependencies (one-way flow: Layer 3 → Layer 2 → Layer 1)
- ✅ Code reuse (both plugins and services use same utilities)
- ✅ Plugins remain simple and focused
- ✅ Easy to test (utilities are independent)
- ✅ Clear separation of concerns

---

## 2. Component Architecture

### 2.1 Component Diagram (Three-Layer Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                                │
│  apm detect analyze | graph | sbom | patterns | fitness         │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│         Layer 3: Detection Services (Top Layer)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Static     │  │  Dependency  │  │    SBOM      │          │
│  │   Analysis   │  │    Graph     │  │  Generator   │          │
│  │   Service    │  │   Service    │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Pattern    │  │   Fitness    │  │   Cache      │          │
│  │  Recognition │  │   Testing    │  │   Manager    │          │
│  │   Service    │  │   Engine     │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  Uses: Layer 2 (plugins) + Layer 1 (utils)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│         Layer 2: Plugin System (Middle Layer)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BasePlugin (existing interface)                           │  │
│  │  + detect()                                               │  │
│  │  + extract_project_facts()                               │  │
│  │  + generate_code_amalgamations()                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Technology-Specific Plugins:                                   │
│  - PythonPlugin, JavaScriptPlugin, TypeScriptPlugin, etc.      │
│                                                                   │
│  Uses: ONLY Layer 1 (utils) - NO imports from Layer 3          │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│         Layer 1: Shared Utilities (Foundation Layer)             │
│  core/plugins/utils/                                             │
│                                                                   │
│  Existing:                                                       │
│  - code_extractors.py        Extract code patterns              │
│  - dependency_parsers.py     Parse dependency files              │
│  - structure_analyzers.py    Analyze project structure           │
│                                                                   │
│  NEW (shared by plugins AND services):                          │
│  - ast_utils.py              AST parsing primitives             │
│  - graph_builders.py         Graph construction primitives      │
│  - metrics_calculator.py     Code metrics primitives            │
│  - pattern_matchers.py       Pattern matching primitives        │
│  - file_parsers.py           Configuration file parsers         │
│                                                                   │
│  Dependencies: NONE (pure utilities)                            │
└─────────────────────┬────────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────────┐
│                  Data Layer (Models + Adapters)                   │
│  Pydantic Models → SQLite Adapters → Database/Cache              │
└───────────────────────────────────────────────────────────────────┘
```

**Key Architectural Principle**:
- **One-way dependency flow**: Layer 3 → Layer 2 → Layer 1
- **No circular dependencies**: Plugins (Layer 2) cannot import from Detection Services (Layer 3)
- **Shared utilities**: Both plugins and services use Layer 1 for AST, graphs, metrics
- **Plugin simplicity**: Plugins focus on technology detection, use utilities for analysis

### 2.2 Integration with Existing System

**Extension Strategy**:

1. **Shared Utilities (Layer 1)**: Add new utility modules to `core/plugins/utils/`
2. **Plugin Updates (Layer 2)**: Plugins use shared utilities for analysis primitives
3. **Service Layer (Layer 3)**: New detection services integrate via `DetectionOrchestrator`
4. **Data Models**: New Pydantic models follow existing pattern (models.py)
5. **CLI Commands**: Add `detect` command group to LazyGroup registry
6. **Caching**: Leverage existing database for persistent caching

**Backward Compatibility**:
- Existing plugins continue to work unchanged (no breaking changes to `BasePlugin`)
- New capabilities added via shared utilities (opt-in usage by plugins)
- Detection flow remains two-phase (indicator → plugin)
- Existing CLI commands unaffected

**Directory Structure (Three-Layer)**:

```
agentpm/
├── core/
│   ├── detection/                    # Layer 3: Detection Services
│   │   ├── service.py                # (existing) DetectionOrchestrator
│   │   ├── analysis_models.py        # (NEW) Pydantic models
│   │   ├── analysis_adapters.py      # (NEW) SQLite adapters
│   │   ├── static_analysis_service.py # (NEW) AST/metrics service
│   │   ├── dependency_graph_service.py # (NEW) Graph service
│   │   ├── sbom_service.py           # (NEW) SBOM generator
│   │   ├── pattern_recognition_service.py # (NEW) Pattern detection
│   │   └── fitness_engine.py         # (NEW) Fitness testing
│   │
│   └── plugins/                      # Layer 2: Plugin System
│       ├── base/
│       │   └── plugin_interface.py   # (existing) BasePlugin
│       ├── domains/
│       │   └── languages/
│       │       ├── python.py         # (existing) Uses ast_utils.py
│       │       └── javascript.py     # (existing) Uses ast_utils.py
│       └── utils/                    # Layer 1: Shared Utilities
│           ├── code_extractors.py    # (existing)
│           ├── dependency_parsers.py # (existing)
│           ├── structure_analyzers.py # (existing)
│           ├── ast_utils.py          # (NEW) AST parsing primitives
│           ├── graph_builders.py     # (NEW) Graph construction
│           ├── metrics_calculator.py # (NEW) Code metrics
│           ├── pattern_matchers.py   # (NEW) Pattern matching
│           └── file_parsers.py       # (NEW) Config parsers
```

**Code Example: Avoiding Circular Dependencies**

```python
# ✅ GOOD: Plugin uses shared utility (Layer 2 → Layer 1)
# agentpm/core/plugins/domains/languages/python.py
from agentpm.core.plugins.utils.ast_utils import parse_python_ast


class PythonPlugin(BasePlugin):
    def detect(self, project_path):
        ast_tree = parse_python_ast(some_file)  # Uses Layer 1
        # ... detection logic ...


# ✅ GOOD: Detection service uses same shared utility (Layer 3 → Layer 1)
# agentpm/core/detection/static_analysis_service.py
from agentpm.core.plugins.utils.ast_utils import parse_python_ast


class StaticAnalysisService:
    def analyze(self, project_path):
        ast_tree = parse_python_ast(some_file)  # Uses Layer 1
        # ... analysis logic ...


# ❌ BAD: Would create circular dependency (Layer 2 → Layer 3 ✗)
# agentpm/core/plugins/domains/languages/python.py
from agentpm.core.detection.static_analysis_service import StaticAnalysisService  # CIRCULAR!


class PythonPlugin(BasePlugin):
    def detect(self, project_path):
        # This creates circular dependency: plugins ← → detection
        service = StaticAnalysisService(...)  # DON'T DO THIS
```

---

## 3. Data Models (Three-Layer Pattern)

### 3.1 Core Models (Pydantic Layer)

**File**: `agentpm/core/detection/analysis_models.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum

# ============================================================================
# Static Analysis Models
# ============================================================================

class NodeType(str, Enum):
    """AST node types"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    VARIABLE = "variable"

class ASTNode(BaseModel):
    """
    Represents a single node in the Abstract Syntax Tree.

    Attributes:
        node_id: Unique identifier
        node_type: Type of AST node
        name: Node name (class/function/variable name)
        file_path: Source file path (project-relative)
        line_number: Starting line number
        end_line: Ending line number
        complexity: Cyclomatic complexity (functions/methods only)
        metadata: Additional node-specific data
    """
    model_config = ConfigDict(validate_assignment=True)

    node_id: str = Field(..., min_length=1)
    node_type: NodeType
    name: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    line_number: int = Field(..., ge=1)
    end_line: Optional[int] = Field(None, ge=1)
    complexity: Optional[int] = Field(None, ge=0)
    metadata: Dict[str, str] = Field(default_factory=dict)

class ASTGraph(BaseModel):
    """
    Complete AST representation with graph structure.

    Uses node_id references to build graph relationships.
    Actual graph structure managed by NetworkX in service layer.

    Attributes:
        nodes: All AST nodes in project
        edges: Parent-child relationships (parent_id, child_id)
        project_path: Root project directory
        parsed_at: When AST was generated
    """
    model_config = ConfigDict(validate_assignment=True)

    nodes: List[ASTNode] = Field(default_factory=list)
    edges: List[tuple[str, str]] = Field(default_factory=list)  # (parent_id, child_id)
    project_path: str = Field(..., min_length=1)
    parsed_at: datetime = Field(default_factory=datetime.now)

class CodeMetrics(BaseModel):
    """
    Code quality metrics extracted from static analysis.

    Attributes:
        total_lines: Total lines of code (excluding comments/blanks)
        comment_lines: Lines of comments
        blank_lines: Blank lines
        complexity_avg: Average cyclomatic complexity
        complexity_max: Maximum cyclomatic complexity
        function_count: Total functions
        class_count: Total classes
        module_count: Total modules
        import_count: Total import statements
        metrics_by_file: Per-file breakdown
    """
    model_config = ConfigDict(validate_assignment=True)

    total_lines: int = Field(default=0, ge=0)
    comment_lines: int = Field(default=0, ge=0)
    blank_lines: int = Field(default=0, ge=0)
    complexity_avg: float = Field(default=0.0, ge=0.0)
    complexity_max: int = Field(default=0, ge=0)
    function_count: int = Field(default=0, ge=0)
    class_count: int = Field(default=0, ge=0)
    module_count: int = Field(default=0, ge=0)
    import_count: int = Field(default=0, ge=0)
    metrics_by_file: Dict[str, Dict[str, int]] = Field(default_factory=dict)

# ============================================================================
# Dependency Graph Models
# ============================================================================

class DependencyType(str, Enum):
    """Type of dependency relationship"""
    IMPORT = "import"           # Direct import (from X import Y)
    INHERITANCE = "inheritance" # Class inheritance
    COMPOSITION = "composition" # Has-a relationship
    USAGE = "usage"            # Function call or method invocation
    DATA_FLOW = "data_flow"    # Data passed between components

class DependencyEdge(BaseModel):
    """
    Represents a dependency relationship between two components.

    Attributes:
        source: Source component identifier
        target: Target component identifier
        dependency_type: Type of dependency
        weight: Dependency strength (0.0-1.0)
        metadata: Additional relationship data
    """
    model_config = ConfigDict(validate_assignment=True)

    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    dependency_type: DependencyType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, str] = Field(default_factory=dict)

class DependencyGraph(BaseModel):
    """
    Complete dependency graph for project.

    Graph structure managed by NetworkX in service layer.
    This model provides serializable representation.

    Attributes:
        nodes: Component identifiers
        edges: Dependency relationships
        project_path: Root project directory
        generated_at: When graph was built
    """
    model_config = ConfigDict(validate_assignment=True)

    nodes: Set[str] = Field(default_factory=set)
    edges: List[DependencyEdge] = Field(default_factory=list)
    project_path: str = Field(..., min_length=1)
    generated_at: datetime = Field(default_factory=datetime.now)

# ============================================================================
# SBOM Models
# ============================================================================

class LicenseType(str, Enum):
    """Common license types"""
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    GPL_3_0 = "GPL-3.0"
    BSD_3_CLAUSE = "BSD-3-Clause"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"

class LicenseInfo(BaseModel):
    """
    License information for a package.

    Attributes:
        package_name: Package identifier
        version: Package version
        license_type: Detected license type
        license_text: Full license text (optional)
        source: Where license was detected (file, metadata, API)
        confidence: Detection confidence (0.0-1.0)
    """
    model_config = ConfigDict(validate_assignment=True)

    package_name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    license_type: LicenseType
    license_text: Optional[str] = None
    source: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)

class SBOMComponent(BaseModel):
    """
    Software Bill of Materials component.

    Attributes:
        name: Component name
        version: Component version
        type: Component type (library, framework, tool)
        license: License information
        dependencies: Direct dependencies
        vulnerabilities: Known security issues (count)
        last_updated: When package was last updated
    """
    model_config = ConfigDict(validate_assignment=True)

    name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    type: str = Field(default="library")
    license: Optional[LicenseInfo] = None
    dependencies: List[str] = Field(default_factory=list)
    vulnerabilities: int = Field(default=0, ge=0)
    last_updated: Optional[datetime] = None

class SBOM(BaseModel):
    """
    Software Bill of Materials for project.

    Attributes:
        components: All project dependencies
        project_name: Project identifier
        project_version: Project version
        generated_at: When SBOM was generated
        format_version: SBOM format version
    """
    model_config = ConfigDict(validate_assignment=True)

    components: List[SBOMComponent] = Field(default_factory=list)
    project_name: str = Field(..., min_length=1)
    project_version: str = Field(default="0.1.0")
    generated_at: datetime = Field(default_factory=datetime.now)
    format_version: str = Field(default="1.0")

# ============================================================================
# Pattern Recognition Models
# ============================================================================

class ArchitecturePattern(str, Enum):
    """Recognized architecture patterns"""
    HEXAGONAL = "hexagonal"          # Ports & Adapters
    LAYERED = "layered"              # N-tier architecture
    CLEAN = "clean"                  # Clean Architecture
    DDD = "domain_driven_design"     # Domain-Driven Design
    CQRS = "cqrs"                    # Command Query Responsibility Segregation
    EVENT_SOURCING = "event_sourcing"
    MICROSERVICES = "microservices"
    MVC = "mvc"                      # Model-View-Controller
    MONOLITHIC = "monolithic"

class PatternMatch(BaseModel):
    """
    Detected architecture pattern.

    Attributes:
        pattern: Pattern type
        confidence: Detection confidence (0.0-1.0)
        evidence: Files/components supporting detection
        violations: Deviations from pattern
        recommendations: Suggestions for improvement
    """
    model_config = ConfigDict(validate_assignment=True)

    pattern: ArchitecturePattern
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class PatternAnalysis(BaseModel):
    """
    Complete pattern recognition results.

    Attributes:
        matches: Detected patterns
        primary_pattern: Highest confidence pattern
        project_path: Project root
        analyzed_at: Analysis timestamp
    """
    model_config = ConfigDict(validate_assignment=True)

    matches: List[PatternMatch] = Field(default_factory=list)
    primary_pattern: Optional[ArchitecturePattern] = None
    project_path: str = Field(..., min_length=1)
    analyzed_at: datetime = Field(default_factory=datetime.now)

# ============================================================================
# Fitness Testing Models
# ============================================================================

class PolicyLevel(str, Enum):
    """Policy enforcement levels"""
    ERROR = "error"      # Blocks deployment
    WARNING = "warning"  # Logged but doesn't block
    INFO = "info"       # Informational only

class Policy(BaseModel):
    """
    Architecture fitness policy rule.

    Attributes:
        policy_id: Unique identifier
        name: Human-readable name
        description: What the policy validates
        level: Enforcement level
        validation_logic: Python expression or function
        tags: Categorization tags
    """
    model_config = ConfigDict(validate_assignment=True)

    policy_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    level: PolicyLevel
    validation_logic: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)

class PolicyViolation(BaseModel):
    """
    Policy violation instance.

    Attributes:
        policy_id: Which policy was violated
        level: Severity level
        message: Human-readable violation message
        location: File/component where violation occurred
        suggestion: How to fix
    """
    model_config = ConfigDict(validate_assignment=True)

    policy_id: str = Field(..., min_length=1)
    level: PolicyLevel
    message: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    suggestion: Optional[str] = None

class FitnessResult(BaseModel):
    """
    Architecture fitness test results.

    Attributes:
        violations: All policy violations
        passed_count: Number of policies that passed
        warning_count: Number of warnings
        error_count: Number of errors
        compliance_score: Overall score (0.0-1.0)
        tested_at: When test was run
    """
    model_config = ConfigDict(validate_assignment=True)

    violations: List[PolicyViolation] = Field(default_factory=list)
    passed_count: int = Field(default=0, ge=0)
    warning_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    tested_at: datetime = Field(default_factory=datetime.now)
```

### 3.2 Database Schema Extensions

**File**: `agentpm/database/migrations/XXX_detection_pack_enhancement.sql`

```sql
-- ============================================================================
-- Detection Cache Tables
-- ============================================================================

-- AST parsing cache (reduces re-parsing on every analysis)
CREATE TABLE IF NOT EXISTS ast_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,

    -- Content tracking
    file_hash TEXT NOT NULL,  -- SHA256 of file content
    file_size INTEGER NOT NULL,

    -- Parsed AST (JSON)
    ast_nodes TEXT NOT NULL,   -- JSON array of ASTNode objects
    complexity_metrics TEXT,   -- JSON: CodeMetrics for this file

    -- Cache metadata
    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, file_path, file_hash)
);

CREATE INDEX idx_ast_cache_project ON ast_cache(project_id);
CREATE INDEX idx_ast_cache_hash ON ast_cache(file_hash);

-- Dependency graph cache
CREATE TABLE IF NOT EXISTS dependency_graph_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- Graph data (JSON)
    nodes TEXT NOT NULL,       -- JSON array of node identifiers
    edges TEXT NOT NULL,       -- JSON array of DependencyEdge objects

    -- Metrics
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    max_depth INTEGER DEFAULT 0,

    -- Cache metadata
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id)
);

-- SBOM cache
CREATE TABLE IF NOT EXISTS sbom_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- SBOM data (JSON)
    components TEXT NOT NULL,  -- JSON array of SBOMComponent objects

    -- Metadata
    component_count INTEGER DEFAULT 0,
    license_issues INTEGER DEFAULT 0,
    vulnerability_count INTEGER DEFAULT 0,

    -- Cache metadata
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id)
);

-- Architecture pattern detection results
CREATE TABLE IF NOT EXISTS pattern_analysis_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- Analysis results (JSON)
    matches TEXT NOT NULL,      -- JSON array of PatternMatch objects
    primary_pattern TEXT,       -- Primary ArchitecturePattern enum value

    -- Cache metadata
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id)
);

-- Fitness test policies
CREATE TABLE IF NOT EXISTS fitness_policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- Policy definition
    policy_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    level TEXT NOT NULL CHECK(level IN ('error', 'warning', 'info')),
    validation_logic TEXT NOT NULL,
    tags TEXT DEFAULT '[]',  -- JSON array

    -- Status
    enabled INTEGER DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, policy_id)
);

CREATE INDEX idx_fitness_policies_project ON fitness_policies(project_id);
CREATE INDEX idx_fitness_policies_enabled ON fitness_policies(enabled);

-- Fitness test results
CREATE TABLE IF NOT EXISTS fitness_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- Results (JSON)
    violations TEXT NOT NULL,   -- JSON array of PolicyViolation objects

    -- Metrics
    passed_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    compliance_score REAL DEFAULT 0.0 CHECK(compliance_score >= 0.0 AND compliance_score <= 1.0),

    -- Metadata
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_fitness_results_project ON fitness_results(project_id);
CREATE INDEX idx_fitness_results_tested_at ON fitness_results(tested_at);
```

### 3.3 Adapter Layer

**File**: `agentpm/core/detection/analysis_adapters.py`

```python
"""
Database adapters for detection pack models.

Follows AIPM three-layer pattern:
- Pydantic models (analysis_models.py)
- SQLite adapters (this file)
- Service methods (analysis_services.py)
"""

import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from .analysis_models import (
    ASTGraph, CodeMetrics, DependencyGraph, SBOM,
    PatternAnalysis, Policy, FitnessResult
)

class ASTCacheAdapter:
    """Adapter for AST cache operations"""

    @staticmethod
    def to_database(ast_graph: ASTGraph, project_id: int, file_path: str, file_hash: str) -> dict:
        """Convert ASTGraph to database row"""
        return {
            'project_id': project_id,
            'file_path': file_path,
            'file_hash': file_hash,
            'file_size': 0,  # Calculate from file
            'ast_nodes': json.dumps([node.model_dump() for node in ast_graph.nodes]),
            'complexity_metrics': json.dumps({}),  # Extracted separately
            'parsed_at': datetime.now(),
        }

    @staticmethod
    def from_database(row: dict) -> ASTGraph:
        """Convert database row to ASTGraph"""
        nodes_data = json.loads(row['ast_nodes'])
        return ASTGraph(
            nodes=[ASTNode(**node) for node in nodes_data],
            edges=[],  # Reconstructed from relationships
            project_path=row.get('project_path', ''),
            parsed_at=row['parsed_at']
        )

# Similar adapters for other models...
```

---

## 4. Service Layer Architecture

### 4.1 Static Analysis Service

**File**: `agentpm/core/detection/static_analysis_service.py`

```python
"""
Static Analysis Service - AST parsing and code metrics extraction.

Responsibilities:
- Parse Python/JavaScript/TypeScript source files to AST
- Extract code complexity metrics
- Cache parsed results for performance
- Provide metrics aggregation

Performance:
- First run: ~500ms for 100 files
- Cached: ~50ms (90% faster)
"""

import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
import time

from .analysis_models import ASTGraph, ASTNode, NodeType, CodeMetrics
from .analysis_adapters import ASTCacheAdapter
from ..database.database import Database

class StaticAnalysisService:
    """
    Service for static code analysis operations.

    Example:
        service = StaticAnalysisService(db, project_path)
        ast_graph = service.parse_project()
        metrics = service.extract_metrics(ast_graph)
        print(f"Total complexity: {metrics.complexity_avg}")
    """

    def __init__(self, db: Database, project_path: Path):
        self.db = db
        self.project_path = project_path
        self.cache_adapter = ASTCacheAdapter()

    def parse_project(self, use_cache: bool = True) -> ASTGraph:
        """
        Parse entire project to AST graph.

        Args:
            use_cache: Whether to use cached AST data

        Returns:
            Complete AST graph for project
        """
        all_nodes = []
        all_edges = []

        # Find all Python files
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            # Check cache first
            if use_cache:
                cached = self._get_cached_ast(file_path)
                if cached:
                    all_nodes.extend(cached.nodes)
                    all_edges.extend(cached.edges)
                    continue

            # Parse file
            file_ast = self._parse_file(file_path)
            if file_ast:
                all_nodes.extend(file_ast.nodes)
                all_edges.extend(file_ast.edges)

                # Cache result
                if use_cache:
                    self._cache_ast(file_path, file_ast)

        return ASTGraph(
            nodes=all_nodes,
            edges=all_edges,
            project_path=str(self.project_path)
        )

    def _parse_file(self, file_path: Path) -> Optional[ASTGraph]:
        """Parse single file to AST"""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            nodes = []
            edges = []

            # Walk AST and extract nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    ast_node = ASTNode(
                        node_id=f"{file_path}:{node.lineno}",
                        node_type=NodeType.CLASS,
                        name=node.name,
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=node.lineno,
                        end_line=node.end_lineno
                    )
                    nodes.append(ast_node)

                elif isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    ast_node = ASTNode(
                        node_id=f"{file_path}:{node.lineno}",
                        node_type=NodeType.FUNCTION,
                        name=node.name,
                        file_path=str(file_path.relative_to(self.project_path)),
                        line_number=node.lineno,
                        end_line=node.end_lineno,
                        complexity=complexity
                    )
                    nodes.append(ast_node)

            return ASTGraph(nodes=nodes, edges=edges, project_path=str(self.project_path))

        except Exception as e:
            # Log error and continue
            return None

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Add 1 for each decision point
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def extract_metrics(self, ast_graph: ASTGraph) -> CodeMetrics:
        """Extract code metrics from AST graph"""
        total_functions = sum(1 for n in ast_graph.nodes if n.node_type == NodeType.FUNCTION)
        total_classes = sum(1 for n in ast_graph.nodes if n.node_type == NodeType.CLASS)

        complexities = [n.complexity for n in ast_graph.nodes if n.complexity]

        return CodeMetrics(
            function_count=total_functions,
            class_count=total_classes,
            complexity_avg=sum(complexities) / len(complexities) if complexities else 0.0,
            complexity_max=max(complexities) if complexities else 0
        )

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    def _get_cached_ast(self, file_path: Path) -> Optional[ASTGraph]:
        """Retrieve cached AST if available and valid"""
        # Query cache table
        # Return if hash matches current file
        pass

    def _cache_ast(self, file_path: Path, ast_graph: ASTGraph):
        """Cache parsed AST for file"""
        # Store in ast_cache table
        pass
```

### 4.2 Dependency Graph Service

**File**: `agentpm/core/detection/dependency_graph_service.py`

```python
"""
Dependency Graph Service - Build and analyze project dependency graphs.

Uses NetworkX for graph modeling and analysis.

Responsibilities:
- Build dependency graphs from AST and imports
- Visualize dependency relationships
- Detect circular dependencies
- Calculate coupling metrics
"""

import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

from .analysis_models import DependencyGraph, DependencyEdge, DependencyType

class DependencyGraphService:
    """
    Service for dependency graph operations.

    Example:
        service = DependencyGraphService(project_path)
        graph = service.build_graph(ast_graph)
        cycles = service.detect_cycles(graph)
        visualization = service.export_graphviz(graph)
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path

    def build_graph(self, ast_graph: ASTGraph) -> DependencyGraph:
        """
        Build dependency graph from AST.

        Analyzes:
        - Import statements (IMPORT dependency)
        - Class inheritance (INHERITANCE dependency)
        - Function calls (USAGE dependency)

        Returns:
            Complete dependency graph
        """
        G = nx.DiGraph()
        edges = []

        # Add nodes for all modules
        modules = set(node.file_path for node in ast_graph.nodes)
        for module in modules:
            G.add_node(module)

        # Extract import dependencies
        import_edges = self._extract_imports(ast_graph)
        for edge in import_edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
            edges.append(edge)

        # Extract inheritance dependencies
        inheritance_edges = self._extract_inheritance(ast_graph)
        for edge in inheritance_edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
            edges.append(edge)

        return DependencyGraph(
            nodes=set(G.nodes()),
            edges=edges,
            project_path=str(self.project_path)
        )

    def _extract_imports(self, ast_graph: ASTGraph) -> List[DependencyEdge]:
        """Extract import dependencies from AST"""
        # Parse import nodes and create edges
        pass

    def _extract_inheritance(self, ast_graph: ASTGraph) -> List[DependencyEdge]:
        """Extract class inheritance relationships"""
        # Find class nodes with base classes
        pass

    def detect_cycles(self, graph: DependencyGraph) -> List[List[str]]:
        """
        Detect circular dependencies.

        Returns:
            List of dependency cycles (each cycle is list of nodes)
        """
        G = self._to_networkx(graph)
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def calculate_coupling(self, graph: DependencyGraph) -> Dict[str, float]:
        """
        Calculate coupling metrics for each module.

        Metrics:
        - Afferent coupling (Ca): How many modules depend on this
        - Efferent coupling (Ce): How many modules this depends on
        - Instability (I): Ce / (Ce + Ca)

        Returns:
            Dict mapping module -> instability score
        """
        G = self._to_networkx(graph)
        coupling = {}

        for node in G.nodes():
            ca = G.in_degree(node)   # Afferent coupling
            ce = G.out_degree(node)  # Efferent coupling

            instability = ce / (ce + ca) if (ce + ca) > 0 else 0.0
            coupling[node] = instability

        return coupling

    def export_graphviz(self, graph: DependencyGraph, output_path: Path) -> str:
        """
        Export graph to Graphviz DOT format.

        Returns:
            DOT format string
        """
        G = self._to_networkx(graph)
        dot = nx.drawing.nx_pydot.to_pydot(G)
        dot_string = dot.to_string()

        # Write to file
        output_path.write_text(dot_string)

        return dot_string

    def _to_networkx(self, graph: DependencyGraph) -> nx.DiGraph:
        """Convert DependencyGraph model to NetworkX graph"""
        G = nx.DiGraph()
        G.add_nodes_from(graph.nodes)
        for edge in graph.edges:
            G.add_edge(edge.source, edge.target, weight=edge.weight)
        return G
```

### 4.3 Other Services (Summary)

**SBOM Generator Service** (`sbom_service.py`):
- Parse package manifests (requirements.txt, package.json, etc.)
- Query license databases (SPDX, GitHub API)
- Detect license from LICENSE files
- Generate CycloneDX/SPDX format SBOM

**Pattern Recognition Service** (`pattern_recognition_service.py`):
- Analyze directory structure for patterns
- Detect layering violations
- Identify domain boundaries (DDD)
- Match hexagonal architecture ports/adapters

**Fitness Testing Engine** (`fitness_engine.py`):
- Load policy definitions from database
- Execute validation logic against AST/dependency graphs
- Generate violation reports
- Calculate compliance scores

---

## 5. Shared Utilities (Layer 1 Expansion)

### 5.1 Overview

**Critical Architecture Decision**: Instead of extending plugins with `AnalysisPlugin` interface (which would require plugins to implement complex analysis logic), we provide **shared utilities** that both plugins AND detection services can use.

**Benefits**:
- ✅ No circular dependencies (utilities have no dependencies)
- ✅ Code reuse (same utilities used by plugins and services)
- ✅ Plugin simplicity (plugins remain focused on detection)
- ✅ Testability (utilities can be tested independently)
- ✅ Maintainability (one implementation, multiple consumers)

### 5.2 New Utility Modules

**File**: `agentpm/core/plugins/utils/ast_utils.py`

```python
"""
AST parsing utilities shared by plugins and detection services.

Provides language-agnostic AST parsing primitives.
"""

import ast
from pathlib import Path
from typing import Optional, List, Dict, Any

def parse_python_ast(file_path: Path) -> Optional[ast.AST]:
    """
    Parse Python file to AST.

    Args:
        file_path: Path to Python file

    Returns:
        AST tree or None if parsing fails
    """
    try:
        content = file_path.read_text()
        return ast.parse(content, filename=str(file_path))
    except (SyntaxError, ValueError):
        return None

def extract_classes(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract all class definitions from AST"""
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'line_number': node.lineno,
                'end_line': node.end_lineno,
                'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
            })
    return classes

def extract_functions(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract all function definitions from AST"""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'line_number': node.lineno,
                'end_line': node.end_lineno,
                'args': [arg.arg for arg in node.args.args],
                'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
            })
    return functions

def extract_imports(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract all import statements from AST"""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    'module': alias.name,
                    'alias': alias.asname,
                    'type': 'import',
                    'line_number': node.lineno
                })
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    'module': node.module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'type': 'from_import',
                    'line_number': node.lineno
                })
    return imports
```

**File**: `agentpm/core/plugins/utils/graph_builders.py`

```python
"""
Graph construction utilities using NetworkX.

Shared by plugins and detection services for dependency graphs.
"""

import networkx as nx
from typing import Dict, List, Tuple, Set, Any

def create_directed_graph(nodes: Set[str], edges: List[Tuple[str, str]]) -> nx.DiGraph:
    """
    Create NetworkX directed graph from nodes and edges.

    Args:
        nodes: Set of node identifiers
        edges: List of (source, target) tuples

    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

def detect_cycles(graph: nx.DiGraph) -> List[List[str]]:
    """
    Detect all cycles in directed graph.

    Args:
        graph: NetworkX directed graph

    Returns:
        List of cycles (each cycle is list of nodes)
    """
    try:
        return list(nx.simple_cycles(graph))
    except nx.NetworkXNoCycle:
        return []

def calculate_node_metrics(graph: nx.DiGraph) -> Dict[str, Dict[str, Any]]:
    """
    Calculate metrics for each node in graph.

    Metrics:
    - in_degree: Number of incoming edges
    - out_degree: Number of outgoing edges
    - betweenness: Betweenness centrality
    - pagerank: PageRank score

    Args:
        graph: NetworkX directed graph

    Returns:
        Dict mapping node -> metrics dict
    """
    metrics = {}
    betweenness = nx.betweenness_centrality(graph)
    pagerank = nx.pagerank(graph)

    for node in graph.nodes():
        metrics[node] = {
            'in_degree': graph.in_degree(node),
            'out_degree': graph.out_degree(node),
            'betweenness': betweenness[node],
            'pagerank': pagerank[node]
        }

    return metrics
```

**File**: `agentpm/core/plugins/utils/metrics_calculator.py`

```python
"""
Code metrics calculation utilities.

Shared by plugins and detection services for complexity analysis.
"""

import ast
from typing import Dict, Any

def calculate_cyclomatic_complexity(func_node: ast.FunctionDef) -> int:
    """
    Calculate cyclomatic complexity for function.

    Complexity = 1 + number of decision points

    Args:
        func_node: AST FunctionDef node

    Returns:
        Cyclomatic complexity score
    """
    complexity = 1  # Base complexity

    for node in ast.walk(func_node):
        # Add 1 for each decision point
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, (ast.And, ast.Or)):
            complexity += 1

    return complexity

def count_lines_of_code(file_path: Path) -> Dict[str, int]:
    """
    Count lines in Python file.

    Returns:
        Dict with 'total', 'code', 'comment', 'blank' line counts
    """
    content = file_path.read_text()
    lines = content.split('\n')

    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comment = sum(1 for line in lines if line.strip().startswith('#'))
    code = total - blank - comment

    return {
        'total': total,
        'code': code,
        'comment': comment,
        'blank': blank
    }

def calculate_maintainability_index(complexity: int, volume: int, loc: int) -> float:
    """
    Calculate maintainability index (0-100).

    MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)

    Where:
    - V = Halstead volume
    - G = Cyclomatic complexity
    - LOC = Lines of code

    Args:
        complexity: Cyclomatic complexity
        volume: Halstead volume
        loc: Lines of code

    Returns:
        Maintainability index (0-100)
    """
    import math

    if loc == 0:
        return 0.0

    mi = 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc)

    # Normalize to 0-100
    return max(0.0, min(100.0, mi))
```

**File**: `agentpm/core/plugins/utils/pattern_matchers.py`

```python
"""
Pattern matching utilities for architecture detection.

Shared by plugins and detection services.
"""

from pathlib import Path
from typing import Dict, List, Set

def detect_directory_pattern(project_path: Path, expected_dirs: List[str], threshold: float = 0.6) -> float:
    """
    Detect if project follows expected directory pattern.

    Args:
        project_path: Project root directory
        expected_dirs: List of expected directory names
        threshold: Minimum match ratio (0.0-1.0)

    Returns:
        Confidence score (0.0-1.0)
    """
    found_dirs = {d.name for d in project_path.iterdir() if d.is_dir()}
    expected_set = set(expected_dirs)

    matches = found_dirs & expected_set
    confidence = len(matches) / len(expected_set) if expected_set else 0.0

    return confidence if confidence >= threshold else 0.0

def detect_hexagonal_pattern(project_path: Path) -> float:
    """
    Detect hexagonal architecture pattern.

    Looks for:
    - adapters/ or ports/adapters/
    - ports/ or domain/ports/
    - domain/
    - application/

    Returns:
        Confidence score (0.0-1.0)
    """
    indicators = [
        (project_path / "adapters").exists() or (project_path / "ports" / "adapters").exists(),
        (project_path / "ports").exists() or (project_path / "domain" / "ports").exists(),
        (project_path / "domain").exists(),
        (project_path / "application").exists() or (project_path / "core").exists()
    ]

    return sum(indicators) / len(indicators)

def detect_layered_pattern(project_path: Path) -> float:
    """
    Detect layered architecture pattern.

    Looks for common layer names:
    - presentation/ ui/ web/
    - application/ service/ business/
    - domain/ model/
    - infrastructure/ data/ persistence/

    Returns:
        Confidence score (0.0-1.0)
    """
    layer_indicators = {
        'presentation': ['presentation', 'ui', 'web', 'views'],
        'application': ['application', 'service', 'services', 'business'],
        'domain': ['domain', 'model', 'models', 'core'],
        'infrastructure': ['infrastructure', 'data', 'persistence', 'repository']
    }

    found_dirs = {d.name.lower() for d in project_path.iterdir() if d.is_dir()}

    layers_found = 0
    for layer_names in layer_indicators.values():
        if any(name in found_dirs for name in layer_names):
            layers_found += 1

    return layers_found / len(layer_indicators)
```

**File**: `agentpm/core/plugins/utils/file_parsers.py`

```python
"""
Configuration file parsing utilities.

Shared by plugins and detection services for SBOM, dependencies, etc.
"""

import json
import tomli
from pathlib import Path
from typing import Dict, List, Optional, Any

def parse_pyproject_toml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse pyproject.toml file"""
    try:
        with open(file_path, 'rb') as f:
            return tomli.load(f)
    except (FileNotFoundError, tomli.TOMLDecodeError):
        return None

def parse_package_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse package.json file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def extract_python_dependencies(pyproject_data: Dict[str, Any]) -> List[str]:
    """Extract dependencies from pyproject.toml data"""
    dependencies = []

    # Poetry format
    if 'tool' in pyproject_data and 'poetry' in pyproject_data['tool']:
        poetry_deps = pyproject_data['tool']['poetry'].get('dependencies', {})
        dependencies.extend(poetry_deps.keys())

    # PEP 621 format
    if 'project' in pyproject_data:
        project_deps = pyproject_data['project'].get('dependencies', [])
        dependencies.extend(project_deps)

    return [d for d in dependencies if d != 'python']

def extract_javascript_dependencies(package_data: Dict[str, Any]) -> List[str]:
    """Extract dependencies from package.json data"""
    dependencies = []

    dependencies.extend(package_data.get('dependencies', {}).keys())
    dependencies.extend(package_data.get('devDependencies', {}).keys())

    return dependencies
```

### 5.3 Usage Examples

**Example 1: Plugin Using Shared Utilities**

```python
# agentpm/core/plugins/domains/languages/python.py
from agentpm.core.plugins.utils.ast_utils import parse_python_ast, extract_imports
from agentpm.core.plugins.utils.pattern_matchers import detect_hexagonal_pattern


class PythonPlugin(BasePlugin):
    def detect(self, project_path: Path) -> float:
        # Use shared utilities for detection
        confidence = 0.0

        # Check for Python files using AST utils
        for py_file in project_path.rglob("*.py"):
            ast_tree = parse_python_ast(py_file)
            if ast_tree:
                confidence = 0.9
                break

        # Check for common Python patterns
        hex_confidence = detect_hexagonal_pattern(project_path)

        return confidence
```

**Example 2: Detection Service Using Same Utilities**

```python
# agentpm/core/detection/static_analysis_service.py
from agentpm.core.plugins.utils.ast_utils import parse_python_ast, extract_functions
from agentpm.core.plugins.utils.metrics_calculator import calculate_cyclomatic_complexity


class StaticAnalysisService:
    def analyze_complexity(self, file_path: Path) -> Dict[str, int]:
        # Use same utilities as plugins
        ast_tree = parse_python_ast(file_path)
        if not ast_tree:
            return {}

        functions = extract_functions(ast_tree)
        complexity_map = {}

        for func in functions:
            complexity = calculate_cyclomatic_complexity(func['node'])
            complexity_map[func['name']] = complexity

        return complexity_map
```

---

## 6. CLI Integration

### 6.1 Command Structure

**Add to**: `agentpm/cli/main.py` LazyGroup registry

```python
COMMANDS = {
    # ... existing commands ...
    'detect': 'agentpm.cli.commands.detect:detect',
}
```

### 6.2 Detect Command Group

**File**: `agentpm/cli/commands/detect.py`

```python
"""
Detection Pack CLI Commands

Provides comprehensive project analysis capabilities:
- apm detect analyze    : Full static analysis
- apm detect graph      : Dependency graph generation
- apm detect sbom       : Generate SBOM
- apm detect patterns   : Architecture pattern recognition
- apm detect fitness    : Architecture fitness testing
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ...core.detection.static_analysis_service import StaticAnalysisService
from ...core.detection.dependency_graph_service import DependencyGraphService
from ...core.detection.sbom_service import SBOMService
from ...core.detection.pattern_recognition_service import PatternRecognitionService
from ...core.detection.fitness_engine import FitnessEngine
from ...core.database.database import Database

console = Console()

@click.group(name='detect')
def detect():
    """
    Comprehensive project detection and analysis.

    Examples:
        apm detect analyze              # Full static analysis
        apm detect graph --visualize    # Generate and visualize dependency graph
        apm detect sbom --format json   # Generate SBOM in JSON format
        apm detect patterns             # Detect architecture patterns
        apm detect fitness              # Run architecture fitness tests
    """
    pass

@detect.command(name='analyze')
@click.option('--no-cache', is_flag=True, help='Disable caching, force re-analysis')
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def analyze(no_cache, format):
    """
    Perform comprehensive static analysis.

    Analyzes:
    - Code complexity metrics
    - Function/class counts
    - AST structure

    Output includes:
    - Total LOC
    - Average/max complexity
    - File-by-file breakdown
    """
    console.print("[bold blue]Running static analysis...[/bold blue]")

    # Initialize services
    db = Database()
    project_path = Path.cwd()
    service = StaticAnalysisService(db, project_path)

    # Parse project
    use_cache = not no_cache
    ast_graph = service.parse_project(use_cache=use_cache)
    metrics = service.extract_metrics(ast_graph)

    # Display results
    if format == 'table':
        table = Table(title="Code Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Lines", str(metrics.total_lines))
        table.add_row("Function Count", str(metrics.function_count))
        table.add_row("Class Count", str(metrics.class_count))
        table.add_row("Avg Complexity", f"{metrics.complexity_avg:.2f}")
        table.add_row("Max Complexity", str(metrics.complexity_max))

        console.print(table)
    elif format == 'json':
        console.print_json(metrics.model_dump_json())

    console.print("[bold green]✓ Analysis complete[/bold green]")

@detect.command(name='graph')
@click.option('--visualize', is_flag=True, help='Generate Graphviz visualization')
@click.option('--output', type=click.Path(), default='dependency_graph.dot', help='Output file path')
@click.option('--detect-cycles', is_flag=True, help='Detect circular dependencies')
def graph(visualize, output, detect_cycles):
    """
    Generate dependency graph.

    Creates NetworkX-based dependency graph showing:
    - Import relationships
    - Class inheritance
    - Module dependencies

    Optionally:
    - Visualize as Graphviz DOT format
    - Detect circular dependencies
    """
    console.print("[bold blue]Building dependency graph...[/bold blue]")

    # Build graph
    db = Database()
    project_path = Path.cwd()

    # Get AST first
    analysis_service = StaticAnalysisService(db, project_path)
    ast_graph = analysis_service.parse_project()

    # Build dependency graph
    graph_service = DependencyGraphService(project_path)
    dep_graph = graph_service.build_graph(ast_graph)

    console.print(f"[green]Found {len(dep_graph.nodes)} nodes, {len(dep_graph.edges)} edges[/green]")

    # Detect cycles
    if detect_cycles:
        cycles = graph_service.detect_cycles(dep_graph)
        if cycles:
            console.print(f"[red]⚠ Found {len(cycles)} circular dependencies:[/red]")
            for cycle in cycles:
                console.print(f"  {' → '.join(cycle)}")
        else:
            console.print("[green]✓ No circular dependencies detected[/green]")

    # Visualize
    if visualize:
        output_path = Path(output)
        graph_service.export_graphviz(dep_graph, output_path)
        console.print(f"[green]✓ Graph saved to {output_path}[/green]")

@detect.command(name='sbom')
@click.option('--format', type=click.Choice(['json', 'xml', 'cyclonedx', 'spdx']), default='json', help='SBOM format')
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--include-licenses', is_flag=True, help='Include license information')
def sbom(format, output, include_licenses):
    """
    Generate Software Bill of Materials (SBOM).

    Analyzes project dependencies and generates SBOM in standard formats:
    - CycloneDX (JSON/XML)
    - SPDX (JSON)

    Includes:
    - All direct and transitive dependencies
    - Version information
    - License data (optional)
    - Vulnerability counts (if available)
    """
    console.print("[bold blue]Generating SBOM...[/bold blue]")

    # Generate SBOM
    project_path = Path.cwd()
    sbom_service = SBOMService(project_path)
    sbom_data = sbom_service.generate_sbom(include_licenses=include_licenses)

    console.print(f"[green]Found {len(sbom_data.components)} components[/green]")

    # Export in requested format
    if output:
        output_path = Path(output)
        sbom_service.export_sbom(sbom_data, output_path, format=format)
        console.print(f"[green]✓ SBOM saved to {output_path}[/green]")
    else:
        # Print to console
        console.print_json(sbom_data.model_dump_json())

@detect.command(name='patterns')
@click.option('--confidence', type=float, default=0.5, help='Minimum confidence threshold')
def patterns(confidence):
    """
    Detect architecture patterns.

    Recognizes common architectural patterns:
    - Hexagonal (Ports & Adapters)
    - Layered (N-tier)
    - Clean Architecture
    - Domain-Driven Design
    - CQRS
    - MVC

    Provides:
    - Pattern confidence scores
    - Supporting evidence
    - Pattern violations
    - Improvement recommendations
    """
    console.print("[bold blue]Analyzing architecture patterns...[/bold blue]")

    # Analyze patterns
    project_path = Path.cwd()

    # Build dependency graph first
    db = Database()
    analysis_service = StaticAnalysisService(db, project_path)
    ast_graph = analysis_service.parse_project()

    graph_service = DependencyGraphService(project_path)
    dep_graph = graph_service.build_dependency_graph(project_path)

    # Detect patterns
    pattern_service = PatternRecognitionService(project_path)
    analysis = pattern_service.analyze_patterns(dep_graph)

    # Display results
    table = Table(title="Detected Architecture Patterns")
    table.add_column("Pattern", style="cyan")
    table.add_column("Confidence", style="green")
    table.add_column("Evidence", style="yellow")

    for match in analysis.matches:
        if match.confidence >= confidence:
            table.add_row(
                match.pattern.value,
                f"{match.confidence:.0%}",
                ", ".join(match.evidence[:3])
            )

    console.print(table)

    if analysis.primary_pattern:
        console.print(f"\n[bold green]Primary pattern: {analysis.primary_pattern.value}[/bold green]")

@detect.command(name='fitness')
@click.option('--policy-set', type=str, help='Policy set to use (default: all enabled)')
@click.option('--fail-on-error', is_flag=True, help='Exit with error if violations found')
def fitness(policy_set, fail_on_error):
    """
    Run architecture fitness tests.

    Validates project against architecture policies:
    - Dependency rules (no cycles, max depth, etc.)
    - Complexity limits (max complexity, max LOC per file)
    - Pattern compliance (layering violations, etc.)
    - Code standards (naming conventions, documentation)

    Reports:
    - Policy violations (ERROR/WARNING/INFO)
    - Compliance score (0.0-1.0)
    - Actionable recommendations
    """
    console.print("[bold blue]Running fitness tests...[/bold blue]")

    # Initialize fitness engine
    db = Database()
    project_path = Path.cwd()
    fitness_engine = FitnessEngine(db, project_path)

    # Load policies
    if policy_set:
        policies = fitness_engine.load_policy_set(policy_set)
    else:
        policies = fitness_engine.load_all_enabled_policies()

    console.print(f"[cyan]Testing {len(policies)} policies...[/cyan]")

    # Run tests
    result = fitness_engine.run_tests(policies)

    # Display results
    table = Table(title="Fitness Test Results")
    table.add_column("Level", style="cyan")
    table.add_column("Policy", style="yellow")
    table.add_column("Violation", style="red")
    table.add_column("Location", style="white")

    for violation in result.violations:
        level_color = {
            'error': 'red',
            'warning': 'yellow',
            'info': 'blue'
        }[violation.level.value]

        table.add_row(
            f"[{level_color}]{violation.level.value.upper()}[/{level_color}]",
            violation.policy_id,
            violation.message,
            violation.location
        )

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Passed: {result.passed_count}")
    console.print(f"  Warnings: {result.warning_count}")
    console.print(f"  Errors: {result.error_count}")
    console.print(f"  Compliance: {result.compliance_score:.0%}")

    if result.error_count > 0:
        console.print(f"\n[bold red]✗ {result.error_count} critical violations found[/bold red]")
        if fail_on_error:
            raise click.Abort()
    else:
        console.print("\n[bold green]✓ All fitness tests passed[/bold green]")
```

---

## 7. Performance Optimization Strategy

### 7.1 Caching Architecture

**Multi-Level Caching**:

```
Level 1: In-Memory Cache (LRU)
   ↓ (miss)
Level 2: SQLite Cache Tables
   ↓ (miss)
Level 3: Parse/Generate Fresh
```

**Cache Invalidation Strategy**:
- **File-based**: SHA256 hash comparison
- **TTL**: 24 hours for external data (licenses, vulnerabilities)
- **Manual**: `apm detect analyze --no-cache`

### 7.2 Lazy Loading

**Utility Module Lazy Loading**:

```python
# Don't import all utilities at module level
# Import only when needed

# Bad (loads everything at import time)
from agentpm.core.plugins.utils.ast_utils import *
from agentpm.core.plugins.utils.graph_builders import *
from agentpm.core.plugins.utils.metrics_calculator import *


# Good (lazy loading)
def analyze_python_file(file_path):
    # Import only what's needed, when needed
    from agentpm.core.plugins.utils.ast_utils import parse_python_ast
    from agentpm.core.plugins.utils.metrics_calculator import calculate_cyclomatic_complexity

    ast_tree = parse_python_ast(file_path)
    # ... use ast_tree ...
```

**NetworkX Graph Lazy Initialization**:
```python
class DependencyGraphService:
    def __init__(self):
        self._graph = None  # Don't build until needed

    @property
    def graph(self):
        if self._graph is None:
            self._graph = self._build_graph()
        return self._graph
```

### 7.3 Performance Targets

| Operation | First Run | Cached | Target |
|-----------|-----------|--------|--------|
| Static Analysis | 1-2s | <100ms | <500ms |
| Dependency Graph | 500ms | <50ms | <200ms |
| SBOM Generation | 2-3s | <100ms | <1s |
| Pattern Detection | 500ms | <50ms | <200ms |
| Fitness Testing | 1s | <100ms | <500ms |

---

## 8. Security Considerations

### 8.1 Input Validation

**AST Parsing Safety**:
```python
# Don't execute code during analysis
# Use ast.parse(), not eval() or exec()

# Safe
tree = ast.parse(source_code)

# Unsafe
eval(source_code)  # NEVER DO THIS
```

**Path Traversal Prevention**:
```python
def safe_relative_path(base: Path, target: Path) -> Path:
    """Ensure target is within base directory"""
    resolved_target = target.resolve()
    resolved_base = base.resolve()

    if not str(resolved_target).startswith(str(resolved_base)):
        raise ValueError("Path traversal attempt detected")

    return resolved_target
```

### 8.2 Resource Limits

**File Size Limits**:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 10_000

def parse_project_safe(project_path: Path):
    file_count = 0
    for file_path in project_path.rglob("*.py"):
        if file_count >= MAX_FILES:
            raise ValueError("Too many files")

        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue  # Skip huge files

        file_count += 1
```

**Graph Complexity Limits**:
```python
MAX_NODES = 10_000
MAX_EDGES = 50_000

def build_graph_safe(nodes, edges):
    if len(nodes) > MAX_NODES:
        raise ValueError("Graph too large")
    if len(edges) > MAX_EDGES:
        raise ValueError("Too many edges")
```

---

## 9. Migration Strategy

### 9.1 Database Migration

**Migration File**: `XXX_detection_pack_enhancement.sql`

**Apply**:
```bash
apm migrate  # Auto-detects and applies new migration
```

**Rollback** (if needed):
```sql
-- Drop new tables in reverse order
DROP TABLE IF EXISTS fitness_results;
DROP TABLE IF EXISTS fitness_policies;
DROP TABLE IF EXISTS pattern_analysis_cache;
DROP TABLE IF EXISTS sbom_cache;
DROP TABLE IF EXISTS dependency_graph_cache;
DROP TABLE IF EXISTS ast_cache;
```

### 9.2 Backward Compatibility

**Existing Plugins**:
- All existing `BasePlugin` implementations continue to work unchanged
- No breaking changes to plugin interface
- Plugins can optionally use new shared utilities from `core/plugins/utils/`
- No requirement to extend or modify existing plugins

**Existing CLI**:
- All existing commands unchanged
- New `detect` command group is additive
- No changes to existing command behavior or output

**Existing Services**:
- `DetectionOrchestrator` remains primary detection coordinator
- New services integrate via existing service pattern (three-layer architecture)
- No changes to existing detection flow or APIs

---

## 10. Implementation Plan

### 10.1 Task Breakdown (4-hour increments)

**Phase 1: Data Models & Schema** (8 hours)
1. **Task #959**: Create `analysis_models.py` with all Pydantic models (4h)
2. **Task #960**: Create database migration and adapters (4h)

**Phase 2: Shared Utilities (Layer 1)** (12 hours)
3. **Task #961**: Implement `ast_utils.py` - AST parsing primitives (3h)
4. **Task #962**: Implement `graph_builders.py` - NetworkX graph construction (3h)
5. **Task #963**: Implement `metrics_calculator.py` - Code metrics primitives (2h)
6. **Task #964**: Implement `pattern_matchers.py` - Pattern detection primitives (2h)
7. **Task #965**: Implement `file_parsers.py` - Config file parsers (2h)

**Phase 3: Core Services (Layer 3)** (16 hours)
8. **Task #966**: Implement `StaticAnalysisService` using ast_utils (4h)
9. **Task #967**: Implement `DependencyGraphService` using graph_builders (4h)
10. **Task #968**: Implement `SBOMService` using file_parsers (4h)
11. **Task #969**: Implement `PatternRecognitionService` using pattern_matchers (4h)

**Phase 4: Fitness Engine** (8 hours)
12. **Task #970**: Implement `FitnessEngine` and policy system (4h)
13. **Task #971**: Create default policy set (4h)

**Phase 5: CLI Integration** (8 hours)
14. **Task #972**: Implement `detect analyze` command (2h)
15. **Task #973**: Implement `detect graph` command (2h)
16. **Task #974**: Implement `detect sbom` command (2h)
17. **Task #975**: Implement `detect patterns` command (1h)
18. **Task #976**: Implement `detect fitness` command (1h)

**Phase 6: Testing & Documentation** (12 hours)
19. **Task #977**: Unit tests for shared utilities (Layer 1) (3h)
20. **Task #978**: Unit tests for services (Layer 3) (4h)
21. **Task #979**: Integration tests for CLI (3h)
22. **Task #980**: User documentation (1h)
23. **Task #981**: Developer documentation (1h)

**Total: 64 hours** (23 tasks)

### 10.2 Dependencies

**Three-Layer Dependency Flow**:

```
Layer 1 (Utilities) - NO dependencies
  ↓
Layer 2 (Plugins) - Use Layer 1 only
  ↓
Layer 3 (Services) - Use Layer 1 and Layer 2

Task Dependencies:
- Tasks 1-2 (Models + Schema): Independent, can run in parallel
- Tasks 3-7 (Layer 1 Utilities): Depend on Task 1 (models), can run in parallel with each other
- Tasks 8-11 (Layer 3 Services): Depend on Tasks 1-2 (models/schema) and Tasks 3-7 (utilities)
- Tasks 12-13 (Fitness): Depend on Tasks 8-11 (services)
- Tasks 14-18 (CLI): Depend on all services (Tasks 8-13)
- Tasks 19-23 (Testing + Docs): Depend on all implementation tasks
```

**Critical Path**:
```
Task 1 (Models) → Task 3-7 (Utilities) → Task 8-11 (Services) → Task 14-18 (CLI) → Task 19-23 (Testing)
```

**Parallel Opportunities**:
- Tasks 3-7 (all utilities) can be built in parallel
- Tasks 8-11 (all services) can be built in parallel (once utilities are done)
- Tasks 14-18 (all CLI commands) can be built in parallel (once services are done)

### 10.3 Technology Stack

**Required Libraries**:
```toml
# pyproject.toml additions
[tool.poetry.dependencies]
networkx = "^3.2"           # Dependency graph modeling
pydot = "^2.0"             # Graphviz export
radon = "^6.0"             # Code complexity metrics
license-expression = "^30.1" # License parsing
cyclonedx-python-lib = "^6.4" # SBOM generation (CycloneDX)
spdx-tools = "^0.8"        # SBOM generation (SPDX)
```

**Optional (Future Enhancement)**:
```toml
[tool.poetry.dependencies]
# For JavaScript/TypeScript analysis
esprima = "^4.0"           # JavaScript AST parser

# For visualization
matplotlib = "^3.8"        # Graph visualization
pygraphviz = "^1.11"      # Advanced Graphviz integration
```

---

## 11. Success Criteria

**Functional**:
- [ ] All 5 CLI commands working (`analyze`, `graph`, `sbom`, `patterns`, `fitness`)
- [ ] AST parsing for Python with <1s performance
- [ ] Dependency graph generation with cycle detection
- [ ] SBOM export in CycloneDX and SPDX formats
- [ ] Pattern detection for 5+ architecture patterns
- [ ] Fitness testing with 10+ default policies

**Performance**:
- [ ] First analysis <2s for 100-file project
- [ ] Cached analysis <100ms
- [ ] Memory usage <500MB for large projects

**Quality**:
- [ ] 90%+ test coverage for new code
- [ ] All services follow three-layer pattern
- [ ] Backward compatibility maintained
- [ ] Documentation complete (user + developer)

---

## 12. Future Enhancements

**Phase 2 (Post-MVP)**:
1. **Multi-Language Support**: Full TypeScript, Java, Go analysis
2. **Advanced Visualizations**: Interactive dependency graphs (D3.js)
3. **Security Scanning**: Integration with Bandit, Safety, Snyk
4. **Performance Profiling**: Hot path detection, bottleneck analysis
5. **AI Pattern Recognition**: ML-based pattern detection
6. **Real-time Analysis**: Watch mode for continuous validation

**Phase 3 (Advanced)**:
1. **Distributed Analysis**: Parallel processing for huge codebases
2. **Historical Tracking**: Track metrics over time (trend analysis)
3. **Custom Policy DSL**: User-defined fitness policies
4. **IDE Integration**: VSCode/PyCharm plugins
5. **API Server**: REST API for programmatic access

---

## Appendix A: Technology Evaluation

### NetworkX vs Alternatives

**Why NetworkX**:
- Pure Python (easy installation)
- Rich algorithm library (cycle detection, centrality, etc.)
- Well-documented
- Lightweight (<5MB)

**Alternatives Considered**:
- **igraph**: Faster but harder to install (C library)
- **graph-tool**: Most performant but complex setup
- **Custom**: Reinventing wheel, maintenance burden

**Decision**: NetworkX - Best balance of performance, ease of use, and ecosystem fit

### AST Parsing Strategy

**Python**: Built-in `ast` module (perfect fit)
**JavaScript/TypeScript**:
- Option 1: `esprima` (Python wrapper)
- Option 2: Node.js bridge (complexity)
- **Decision**: `esprima` for Phase 1, Node.js for advanced features

### SBOM Format Selection

**CycloneDX**:
- JSON/XML formats
- Software-focused
- Growing adoption

**SPDX**:
- ISO standard
- License-focused
- Enterprise adoption

**Decision**: Support both (different use cases)

---

## Appendix B: Example Usage Scenarios

### Scenario 1: Pre-Commit Analysis

```bash
# Developer runs before committing
apm detect analyze --no-cache
apm detect fitness --fail-on-error

# CI/CD pipeline
apm detect fitness --policy-set production --fail-on-error || exit 1
```

### Scenario 2: Architectural Review

```bash
# Architect reviews project structure
apm detect patterns
apm detect graph --visualize --output architecture.dot
dot -Tpng architecture.dot -o architecture.png

# View in browser
open architecture.png
```

### Scenario 3: License Audit

```bash
# Generate SBOM for compliance team
apm detect sbom --include-licenses --format spdx --output sbom.json

# Review licenses
cat sbom.json | jq '.components[] | select(.license.license_type == "GPL-3.0")'
```

### Scenario 4: Complexity Monitoring

```bash
# Baseline metrics
apm detect analyze --format json > metrics_baseline.json

# After refactoring
apm detect analyze --format json > metrics_after.json

# Compare
diff metrics_baseline.json metrics_after.json
```

---

## Document Metadata

**Authors**: System Architect Agent
**Reviewers**: TBD
**Approvals**: TBD
**Version**: 1.1.0
**Last Updated**: 2025-10-24

**Related Documents**:
- Work Item #148: Comprehensive Detection Pack Enhancement
- Task #958: Design Architecture
- ADR-001: Two-Phase Detection Architecture
- ADR-002: Plugin Registry and Selective Loading

**Change Log**:
- 2025-10-24: Updated to three-layer architecture (v1.1.0) - avoids circular dependencies
  - Removed AnalysisPlugin extension approach (Section 5)
  - Added shared utilities layer (core/plugins/utils/)
  - Updated component diagram to show three-layer flow
  - Added concrete examples of good vs. bad dependency patterns
  - Updated task breakdown to reflect utility-first implementation
  - Total: 23 tasks (64 hours) vs. previous 15 tasks (60 hours)
- 2025-10-24: Initial architecture design (v1.0.0)
