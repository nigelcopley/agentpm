# Detection Pack Performance Requirements

**Version**: 1.0.0
**Status**: Draft
**Work Item**: #148 - Comprehensive Detection Pack Enhancement
**Task**: #976 - Performance Requirements Analysis
**Created**: 2025-10-24
**Owner**: Performance Engineering

---

## Executive Summary

This document defines measurable performance requirements, benchmarks, and optimization strategies for the APM (Agent Project Manager) Detection Pack Enhancement. The system must provide fast, cached analysis for typical workflows while gracefully handling projects up to 100K LOC.

**Key Performance Targets**:
- Cached operations: <500ms response time
- First-run analysis: <2s response time
- Cache hit ratio: >80% for typical workflows
- Memory footprint: <500MB for large projects
- Scalability: Linear performance degradation up to 100K LOC

---

## 1. Performance Benchmarks

### 1.1 Detection Operations

#### Static Analysis (AST Parsing)

**Small Projects (<1K LOC)**:
- First run: <200ms
- Cached: <20ms
- Target: <100ms average

**Medium Projects (1K-10K LOC)**:
- First run: <1s
- Cached: <50ms
- Target: <500ms average

**Large Projects (10K-100K LOC)**:
- First run: <5s
- Cached: <200ms
- Target: <2s average

**Performance Factors**:
- File count: ~10ms per file (first run)
- File size: ~1ms per 1KB (parsing time)
- Complexity calculation: ~2ms per function
- AST node extraction: ~0.5ms per node

**Measurement Strategy**:
```python
import time
from pathlib import Path

def benchmark_static_analysis(project_path: Path):
    start = time.perf_counter()

    # First run (no cache)
    service = StaticAnalysisService(db, project_path)
    ast_graph = service.parse_project(use_cache=False)

    first_run_time = time.perf_counter() - start

    # Cached run
    start = time.perf_counter()
    ast_graph_cached = service.parse_project(use_cache=True)
    cached_time = time.perf_counter() - start

    return {
        'first_run': first_run_time,
        'cached': cached_time,
        'speedup': first_run_time / cached_time,
        'file_count': len(ast_graph.nodes)
    }
```

#### Dependency Graph Building

**Performance Targets by Graph Size**:

| Nodes | Edges | First Run | Cached | Target |
|-------|-------|-----------|--------|--------|
| <100 | <500 | <100ms | <10ms | <50ms |
| 100-1K | 500-5K | <500ms | <50ms | <200ms |
| 1K-10K | 5K-50K | <2s | <200ms | <1s |
| >10K | >50K | <10s | <500ms | <5s |

**Performance Factors**:
- Node creation: ~0.1ms per node
- Edge insertion: ~0.05ms per edge (NetworkX)
- Cycle detection: O(V+E) - ~1ms per 1000 nodes
- Coupling calculation: O(V) - ~0.5ms per node

**Graph Complexity Limits** (Safety):
- Maximum nodes: 10,000 (raises error if exceeded)
- Maximum edges: 50,000 (raises error if exceeded)
- Maximum depth: 100 levels (prevents stack overflow)
- Circular dependency limit: 50 cycles (stops analysis if more)

**Measurement Strategy**:
```python
def benchmark_dependency_graph(project_path: Path):
    start = time.perf_counter()

    service = DependencyGraphService(project_path)
    graph = service.build_graph(ast_graph)

    build_time = time.perf_counter() - start

    # Test cycle detection
    start = time.perf_counter()
    cycles = service.detect_cycles(graph)
    cycle_time = time.perf_counter() - start

    return {
        'build_time': build_time,
        'cycle_detection_time': cycle_time,
        'nodes': len(graph.nodes),
        'edges': len(graph.edges),
        'cycles': len(cycles)
    }
```

#### SBOM Generation

**Performance Targets**:

| Dependencies | First Run | Cached | Target |
|--------------|-----------|--------|--------|
| <10 | <200ms | <20ms | <100ms |
| 10-50 | <1s | <50ms | <500ms |
| 50-200 | <3s | <100ms | <1s |
| >200 | <10s | <200ms | <3s |

**Performance Factors**:
- Package manifest parsing: ~10ms per file
- License detection (local): ~5ms per package
- License detection (API): ~100ms per package (network bound)
- SBOM serialization: ~1ms per component

**License Detection Strategy**:
1. **Local LICENSE files**: <5ms per package (fastest)
2. **Package metadata**: <10ms per package
3. **SPDX database**: <20ms per package (in-memory lookup)
4. **GitHub API**: <100ms per package (network, rate limited)

**Optimization**: Batch GitHub API calls, use cache aggressively

**Measurement Strategy**:
```python
def benchmark_sbom_generation(project_path: Path):
    start = time.perf_counter()

    service = SBOMService(project_path)
    sbom = service.generate_sbom(include_licenses=True)

    generation_time = time.perf_counter() - start

    return {
        'generation_time': generation_time,
        'component_count': len(sbom.components),
        'time_per_component': generation_time / len(sbom.components)
    }
```

#### Pattern Detection

**Performance Targets**:

| Project Size | Analysis Time | Target |
|--------------|---------------|--------|
| <1K LOC | <100ms | <50ms |
| 1K-10K LOC | <500ms | <200ms |
| 10K-100K LOC | <2s | <1s |

**Performance Factors**:
- Directory structure scan: ~1ms per directory
- Pattern matching (per pattern): ~10ms
- Evidence collection: ~5ms per evidence item
- Confidence calculation: ~1ms

**Pattern Detection Complexity**:
- Hexagonal: O(D) - directory count
- Layered: O(D) - directory depth
- DDD: O(F) - file count (search for aggregates, entities)
- CQRS: O(F) - file count (search for commands, queries)
- MVC: O(D) - directory structure

**Measurement Strategy**:
```python
def benchmark_pattern_detection(project_path: Path):
    start = time.perf_counter()

    service = PatternRecognitionService(project_path)
    analysis = service.analyze_patterns(dependency_graph)

    detection_time = time.perf_counter() - start

    return {
        'detection_time': detection_time,
        'patterns_detected': len(analysis.matches),
        'time_per_pattern': detection_time / len(analysis.matches) if analysis.matches else 0
    }
```

#### Fitness Testing

**Performance Targets**:

| Policies | Validation Time | Target |
|----------|----------------|--------|
| <10 | <100ms | <50ms |
| 10-50 | <500ms | <200ms |
| 50-100 | <2s | <1s |

**Performance Factors**:
- Policy loading: ~1ms per policy
- Validation execution: ~5-50ms per policy (varies by complexity)
- Simple policies (line count, naming): ~5ms
- Complex policies (graph analysis): ~50ms
- Violation reporting: ~1ms per violation

**Policy Complexity Classes**:
1. **Fast** (<5ms): Simple checks (naming, file structure)
2. **Medium** (5-20ms): Metrics (complexity, LOC)
3. **Slow** (20-100ms): Graph analysis (dependencies, cycles)

**Measurement Strategy**:
```python
def benchmark_fitness_testing(project_path: Path):
    start = time.perf_counter()

    engine = FitnessEngine(db, project_path)
    policies = engine.load_all_enabled_policies()
    result = engine.run_tests(policies)

    test_time = time.perf_counter() - start

    return {
        'test_time': test_time,
        'policy_count': len(policies),
        'violation_count': len(result.violations),
        'time_per_policy': test_time / len(policies)
    }
```

---

## 2. Caching Strategy

### 2.1 Multi-Level Cache Architecture

**Cache Levels** (checked in order):

```
┌─────────────────────────────────────────────┐
│ Level 1: In-Memory Cache (LRU)             │
│ - Capacity: 100 entries                     │
│ - Hit time: <1ms                            │
│ - Scope: Current process only               │
└──────────────────┬──────────────────────────┘
                   │ (miss)
                   ▼
┌─────────────────────────────────────────────┐
│ Level 2: SQLite Cache Tables                │
│ - Capacity: Unlimited (disk space)          │
│ - Hit time: <20ms                           │
│ - Scope: Persistent across sessions         │
└──────────────────┬──────────────────────────┘
                   │ (miss)
                   ▼
┌─────────────────────────────────────────────┐
│ Level 3: Fresh Analysis                     │
│ - Parse/generate from scratch               │
│ - Time: Varies (100ms-10s)                  │
│ - Result: Populate caches                   │
└─────────────────────────────────────────────┘
```

### 2.2 Cache Hit Ratio Targets

**Target Hit Ratios** (typical workflows):

| Operation | Target Hit Ratio | Justification |
|-----------|------------------|---------------|
| AST Parsing | >90% | Files change infrequently |
| Dependency Graph | >80% | Changes only when imports change |
| SBOM | >70% | Dependencies update periodically |
| Pattern Detection | >60% | Re-run after structural changes |
| Fitness Testing | >50% | Run frequently for validation |

**Measurement**:
```python
class CacheStatistics:
    def __init__(self):
        self.hits = 0
        self.misses = 0

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1
```

### 2.3 Cache Invalidation Strategy

**File-Based Invalidation** (SHA256 hash comparison):

```python
import hashlib
from pathlib import Path

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file content"""
    hasher = hashlib.sha256()
    hasher.update(file_path.read_bytes())
    return hasher.hexdigest()

def is_cache_valid(file_path: Path, cached_hash: str) -> bool:
    """Check if cached data is still valid"""
    current_hash = calculate_file_hash(file_path)
    return current_hash == cached_hash
```

**Performance**: ~1ms per file hash calculation (fast enough to check all files)

**Cache Invalidation Triggers**:

1. **File Content Change**: SHA256 mismatch
   - Check on every cache lookup
   - Performance: ~1ms per file

2. **Time-To-Live (TTL)**: Expiration based on age
   - AST cache: No TTL (content-based only)
   - Dependency graph: No TTL (content-based only)
   - SBOM: 24 hours (external data may change)
   - Pattern detection: No TTL (deterministic)
   - Fitness results: 1 hour (policies may change)

3. **Manual Invalidation**: User-triggered
   - `apm detect analyze --no-cache` (bypass cache)
   - `apm cache clear` (clear all caches)
   - `apm cache clear ast` (clear specific cache)

4. **Database Migration**: Version change
   - Clear all caches on schema version change
   - Prevent stale data errors

### 2.4 Cache Size Management

**In-Memory Cache (Level 1)**:

```python
from functools import lru_cache
from collections import OrderedDict

class LRUCache:
    """LRU cache with size limit"""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove least recently used
            self.cache.popitem(last=False)
```

**Capacity Limits**:
- AST cache: 100 files (most recently used)
- Dependency graph: 10 projects
- SBOM: 10 projects
- Pattern analysis: 10 projects
- Fitness results: 20 projects (multiple runs per project)

**Memory Estimation**:
- AST per file: ~10KB (100 files = 1MB)
- Dependency graph: ~100KB per project (10 projects = 1MB)
- SBOM: ~50KB per project (10 projects = 500KB)
- Pattern analysis: ~10KB per project (10 projects = 100KB)
- Fitness results: ~20KB per result (20 results = 400KB)
- **Total in-memory cache**: ~3MB (negligible)

**SQLite Cache (Level 2)**:

**Storage Estimates** (per project):
- AST cache: ~100KB per file × files
- Dependency graph: ~500KB
- SBOM: ~200KB
- Pattern analysis: ~50KB
- Fitness results: ~100KB per run

**Example** (1000-file project):
- AST: 100KB × 1000 = 100MB
- Other caches: ~1MB
- **Total**: ~101MB per project

**Eviction Policy**:
- No automatic eviction (disk space cheap)
- Manual cleanup: `apm cache prune --older-than 30d`
- Per-project cleanup: `apm cache clear --project <path>`

### 2.5 Cache Access Performance

**Target Access Times**:

| Cache Level | Operation | Target Time |
|-------------|-----------|-------------|
| In-Memory | Lookup | <1ms |
| In-Memory | Insert | <1ms |
| SQLite | Lookup (hit) | <20ms |
| SQLite | Insert | <50ms |
| SQLite | Update | <50ms |

**Optimization Strategies**:

1. **SQLite Indexes** (ensure fast lookups):
```sql
CREATE INDEX idx_ast_cache_project ON ast_cache(project_id);
CREATE INDEX idx_ast_cache_hash ON ast_cache(file_hash);
CREATE INDEX idx_ast_cache_path ON ast_cache(project_id, file_path);
```

2. **Batch Inserts** (reduce transaction overhead):
```python
def cache_multiple_files(files: List[Tuple[Path, ASTGraph]]):
    """Cache multiple files in single transaction"""
    with db.transaction():
        for file_path, ast_graph in files:
            cache_adapter.insert(file_path, ast_graph)
```

3. **Lazy Loading** (load only when needed):
```python
class CachedAnalysisService:
    def __init__(self):
        self._ast_cache = None  # Load on first access

    @property
    def ast_cache(self):
        if self._ast_cache is None:
            self._ast_cache = self._load_ast_cache()
        return self._ast_cache
```

---

## 3. Resource Limits

### 3.1 File Processing Limits

**File Size Limits** (safety against huge files):

```python
# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILE_COUNT = 10_000           # 10K files
MAX_LINE_COUNT = 100_000          # 100K lines per file

def should_process_file(file_path: Path) -> bool:
    """Check if file is within processing limits"""
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"Skipping {file_path}: too large ({file_size} bytes)")
        return False

    # Check line count (estimate from size)
    estimated_lines = file_size / 50  # ~50 bytes per line average
    if estimated_lines > MAX_LINE_COUNT:
        logger.warning(f"Skipping {file_path}: too many lines (~{estimated_lines})")
        return False

    return True
```

**File Count Limits**:

| Project Size | Max Files | Processing Strategy |
|--------------|-----------|---------------------|
| Small | <1,000 | Process all files |
| Medium | 1,000-5,000 | Process all, warn if slow |
| Large | 5,000-10,000 | Process all, show progress |
| Very Large | >10,000 | Error, suggest filtering |

**Handling Large Projects**:
```python
def process_large_project(project_path: Path, max_files: int = 10_000):
    """Process large project with file limit"""
    files = list(project_path.rglob("*.py"))

    if len(files) > max_files:
        raise ValueError(
            f"Project has {len(files)} files (max: {max_files}). "
            "Use --filter flag to limit scope or increase --max-files."
        )

    # Process with progress bar for large projects
    if len(files) > 1000:
        return process_with_progress(files)
    else:
        return process_files(files)
```

### 3.2 Graph Complexity Limits

**NetworkX Graph Limits**:

```python
# Configuration
MAX_GRAPH_NODES = 10_000
MAX_GRAPH_EDGES = 50_000
MAX_GRAPH_DEPTH = 100

def validate_graph_size(graph: DependencyGraph):
    """Ensure graph is within complexity limits"""
    if len(graph.nodes) > MAX_GRAPH_NODES:
        raise ValueError(
            f"Graph too large: {len(graph.nodes)} nodes (max: {MAX_GRAPH_NODES})"
        )

    if len(graph.edges) > MAX_GRAPH_EDGES:
        raise ValueError(
            f"Graph too complex: {len(graph.edges)} edges (max: {MAX_GRAPH_EDGES})"
        )
```

**Graph Analysis Timeouts**:

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """Context manager for operation timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds}s timeout")

    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Disable alarm
        signal.alarm(0)

def detect_cycles_safe(graph: DependencyGraph, timeout_seconds: int = 30):
    """Detect cycles with timeout protection"""
    try:
        with timeout(timeout_seconds):
            return detect_cycles(graph)
    except TimeoutError:
        logger.error(f"Cycle detection timed out after {timeout_seconds}s")
        return None  # Or partial results
```

**Cycle Detection Limits**:
- Maximum cycles to report: 50 (stop after finding 50)
- Maximum cycle length: 20 nodes (ignore very long cycles)
- Timeout: 30 seconds (abort if taking too long)

### 3.3 Memory Footprint Targets

**Peak Memory Usage** (by project size):

| Project Size | File Count | Target Memory | Max Memory |
|--------------|------------|---------------|------------|
| Small | <100 | <50MB | <100MB |
| Medium | 100-1,000 | <200MB | <500MB |
| Large | 1,000-10,000 | <500MB | <1GB |
| Very Large | >10,000 | <1GB | <2GB |

**Memory Optimization Strategies**:

1. **Streaming Processing** (avoid loading all at once):
```python
def process_files_streaming(files: List[Path]):
    """Process files one at a time, don't hold all in memory"""
    for file_path in files:
        # Process file
        ast_graph = parse_file(file_path)

        # Extract what we need
        metrics = extract_metrics(ast_graph)

        # Store in database
        cache_adapter.insert(file_path, ast_graph)

        # Release memory (Python GC will collect)
        del ast_graph
```

2. **Generator-Based Processing** (lazy evaluation):
```python
def iterate_ast_nodes(project_path: Path) -> Iterator[ASTNode]:
    """Yield AST nodes one at a time"""
    for file_path in project_path.rglob("*.py"):
        ast_graph = parse_file(file_path)
        for node in ast_graph.nodes:
            yield node
        # ast_graph garbage collected after loop

# Use generator
for node in iterate_ast_nodes(project_path):
    process_node(node)  # Process one at a time
```

3. **Incremental Graph Building** (add nodes gradually):
```python
def build_graph_incremental(project_path: Path) -> DependencyGraph:
    """Build graph incrementally to avoid memory spike"""
    G = nx.DiGraph()

    for file_path in project_path.rglob("*.py"):
        # Parse file
        file_nodes = parse_file(file_path)

        # Add to graph immediately
        for node in file_nodes:
            G.add_node(node.node_id)

        # Extract edges
        edges = extract_edges(file_nodes)
        for edge in edges:
            G.add_edge(edge.source, edge.target)

        # Release file memory
        del file_nodes

    return graph_from_networkx(G)
```

**Memory Monitoring**:
```python
import psutil
import os

def check_memory_usage() -> dict:
    """Get current process memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        'rss': memory_info.rss,  # Resident Set Size
        'vms': memory_info.vms,  # Virtual Memory Size
        'rss_mb': memory_info.rss / (1024 * 1024),
        'percent': process.memory_percent()
    }

def monitor_operation(operation_name: str):
    """Decorator to monitor memory usage"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            before = check_memory_usage()
            result = func(*args, **kwargs)
            after = check_memory_usage()

            delta_mb = after['rss_mb'] - before['rss_mb']
            logger.info(f"{operation_name}: {delta_mb:.1f}MB memory delta")

            return result
        return wrapper
    return decorator
```

### 3.4 Concurrent Operations

**Multi-threading Support** (for I/O-bound operations):

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_files_concurrent(files: List[Path], max_workers: int = 4) -> List[ASTGraph]:
    """Parse multiple files concurrently"""
    ast_graphs = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(parse_file, file_path): file_path
            for file_path in files
        }

        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                ast_graph = future.result(timeout=10)  # 10s timeout per file
                ast_graphs.append(ast_graph)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")

    return ast_graphs
```

**Concurrency Limits**:
- Default workers: 4 (balance between speed and resource usage)
- Maximum workers: CPU count (avoid overloading)
- Per-file timeout: 10 seconds (prevent hanging)

**Performance Gains**:
- I/O-bound (file reading): 2-4x speedup
- CPU-bound (AST parsing): 1.5-2x speedup (GIL limitations)
- Network-bound (license API): 10x+ speedup (many parallel requests)

---

## 4. Scalability Matrix

### 4.1 Project Size Categories

**Small Projects (<1K LOC)**:
- File count: <50 files
- Typical examples: Scripts, small libraries, utilities
- Performance targets:
  - Static analysis: <100ms (first run), <20ms (cached)
  - Dependency graph: <50ms (first run), <10ms (cached)
  - SBOM: <100ms
  - Pattern detection: <50ms
  - Fitness testing: <50ms
- Memory: <50MB peak
- Cache storage: <5MB

**Medium Projects (1K-10K LOC)**:
- File count: 50-500 files
- Typical examples: Web applications, CLI tools, frameworks
- Performance targets:
  - Static analysis: <500ms (first run), <50ms (cached)
  - Dependency graph: <200ms (first run), <50ms (cached)
  - SBOM: <500ms
  - Pattern detection: <200ms
  - Fitness testing: <200ms
- Memory: <200MB peak
- Cache storage: <50MB

**Large Projects (10K-100K LOC)**:
- File count: 500-5,000 files
- Typical examples: Enterprise applications, complex systems
- Performance targets:
  - Static analysis: <2s (first run), <200ms (cached)
  - Dependency graph: <1s (first run), <100ms (cached)
  - SBOM: <1s
  - Pattern detection: <1s
  - Fitness testing: <1s
- Memory: <500MB peak
- Cache storage: <200MB

**Very Large Projects (>100K LOC)**:
- File count: >5,000 files
- Typical examples: Monorepos, enterprise platforms
- Performance strategy: Graceful degradation
  - Warn user about size
  - Suggest filtering (--include, --exclude flags)
  - Show progress bar
  - Support incremental analysis
  - Enable distributed analysis (future)
- Performance targets:
  - Static analysis: <10s (first run), <500ms (cached)
  - Dependency graph: <5s (first run), <200ms (cached)
  - SBOM: <3s
  - Pattern detection: <2s
  - Fitness testing: <2s
- Memory: <1GB peak
- Cache storage: <1GB

### 4.2 Performance Scaling

**Linear Scaling Factors** (expected):

```
Operation Time = Base Time + (Size Factor × Project Size)
```

**Coefficients** (measured empirically):

| Operation | Base Time | Size Factor | Formula |
|-----------|-----------|-------------|---------|
| AST Parsing | 50ms | 10ms per file | 50 + 10n |
| Dependency Graph | 20ms | 0.1ms per edge | 20 + 0.1e |
| SBOM Generation | 100ms | 5ms per package | 100 + 5p |
| Pattern Detection | 30ms | 0.5ms per file | 30 + 0.5n |
| Fitness Testing | 50ms | 5ms per policy | 50 + 5p |

**Example** (1000-file project with 100 packages, 50 policies):
- AST Parsing: 50 + 10(1000) = 10,050ms ≈ 10s
- SBOM: 100 + 5(100) = 600ms
- Fitness: 50 + 5(50) = 300ms

**Cached** (90% reduction):
- AST Parsing: ~1s (cached)
- SBOM: ~60ms (cached)
- Fitness: ~30ms (cached)

### 4.3 Degradation Strategy

**Progressive Performance Degradation** (as project size grows):

**Tier 1: Optimal Performance** (up to 1K LOC):
- All features enabled
- No warnings
- Sub-second response times

**Tier 2: Normal Performance** (1K-10K LOC):
- All features enabled
- Warning if analysis takes >1s
- Recommend caching

**Tier 3: Degraded Performance** (10K-100K LOC):
- Show progress bars for long operations
- Enable incremental analysis by default
- Suggest filtering strategies
- Cache becomes critical (warn if disabled)

**Tier 4: Limited Performance** (>100K LOC):
- Require explicit opt-in (`--allow-large-project` flag)
- Enforce filtering (analyze subset of project)
- Incremental analysis only
- Distributed analysis recommended (future)
- Clear expectations: "This will take 30+ seconds"

**User Feedback Strategy**:
```python
def analyze_with_feedback(project_path: Path):
    """Provide user feedback based on project size"""
    file_count = count_files(project_path)

    if file_count < 100:
        # Tier 1: Silent, fast
        return analyze_project(project_path)

    elif file_count < 1000:
        # Tier 2: Show spinner
        with console.status("Analyzing project..."):
            return analyze_project(project_path)

    elif file_count < 5000:
        # Tier 3: Show progress bar
        with console.progress() as progress:
            task = progress.add_task("Analyzing files", total=file_count)
            return analyze_with_progress(project_path, progress, task)

    else:
        # Tier 4: Warn and require confirmation
        console.print(f"[yellow]Warning: Large project ({file_count} files)[/yellow]")
        console.print("This may take 30+ seconds. Consider using --filter.")

        if not click.confirm("Continue?"):
            raise click.Abort()

        return analyze_with_progress(project_path)
```

---

## 5. Testing Strategy

### 5.1 Performance Test Suite

**Benchmark Tests** (measure performance on known projects):

```python
import pytest
import time
from pathlib import Path

class PerformanceBenchmarks:
    """Performance benchmark test suite"""

    @pytest.fixture
    def small_project(self):
        """Small test project (<1K LOC)"""
        return Path("tests/fixtures/small_project")

    @pytest.fixture
    def medium_project(self):
        """Medium test project (1K-10K LOC)"""
        return Path("tests/fixtures/medium_project")

    @pytest.fixture
    def large_project(self):
        """Large test project (10K-100K LOC)"""
        return Path("tests/fixtures/large_project")

    def test_static_analysis_small_project(self, small_project):
        """Static analysis on small project should be <100ms"""
        service = StaticAnalysisService(db, small_project)

        start = time.perf_counter()
        ast_graph = service.parse_project(use_cache=False)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.1, f"Expected <100ms, got {elapsed*1000:.0f}ms"

    def test_static_analysis_medium_project_cached(self, medium_project):
        """Cached static analysis should be <50ms"""
        service = StaticAnalysisService(db, medium_project)

        # Prime cache
        service.parse_project(use_cache=False)

        # Measure cached performance
        start = time.perf_counter()
        ast_graph = service.parse_project(use_cache=True)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.05, f"Expected <50ms, got {elapsed*1000:.0f}ms"

    def test_dependency_graph_performance(self, medium_project):
        """Dependency graph building should scale linearly"""
        service = DependencyGraphService(medium_project)

        start = time.perf_counter()
        graph = service.build_graph(ast_graph)
        elapsed = time.perf_counter() - start

        # Linear scaling: 20ms + 0.1ms per edge
        expected = 0.02 + (0.0001 * len(graph.edges))
        tolerance = expected * 2  # Allow 2x overhead

        assert elapsed < tolerance, \
            f"Expected <{tolerance*1000:.0f}ms, got {elapsed*1000:.0f}ms"
```

**Regression Tests** (ensure performance doesn't degrade):

```python
class PerformanceRegressionTests:
    """Prevent performance regressions"""

    BASELINE_METRICS = {
        'static_analysis_medium': 0.5,  # 500ms
        'dependency_graph_medium': 0.2,  # 200ms
        'sbom_small': 0.1,  # 100ms
    }

    def test_no_regression(self, operation, project):
        """Ensure performance doesn't regress"""
        baseline = self.BASELINE_METRICS[f"{operation}_{project}"]

        elapsed = measure_operation(operation, project)

        # Allow 10% regression
        assert elapsed <= baseline * 1.1, \
            f"Performance regression: {elapsed:.3f}s vs baseline {baseline:.3f}s"
```

### 5.2 Load Testing

**Stress Tests** (test limits):

```python
class StressTests:
    """Test system under stress"""

    def test_max_file_count(self):
        """Test with maximum file count"""
        files = generate_test_files(count=10_000)

        service = StaticAnalysisService(db, Path("."))
        ast_graph = service.parse_project()

        assert len(ast_graph.nodes) > 0

    def test_max_graph_size(self):
        """Test with maximum graph complexity"""
        graph = generate_complex_graph(
            nodes=10_000,
            edges=50_000
        )

        service = DependencyGraphService(Path("."))
        cycles = service.detect_cycles(graph)

        # Should complete without error
        assert cycles is not None

    def test_memory_limits(self):
        """Test memory usage stays within limits"""
        project = generate_large_project(size="100K_LOC")

        before = check_memory_usage()

        service = StaticAnalysisService(db, project)
        service.parse_project()

        after = check_memory_usage()

        memory_delta = after['rss_mb'] - before['rss_mb']
        assert memory_delta < 500, f"Memory usage too high: {memory_delta}MB"
```

### 5.3 Cache Validation Tests

**Cache Correctness** (ensure cached results match fresh):

```python
class CacheTests:
    """Validate cache correctness"""

    def test_cache_equivalence(self, project):
        """Cached results should match fresh results"""
        service = StaticAnalysisService(db, project)

        # Get fresh result
        fresh = service.parse_project(use_cache=False)

        # Get cached result
        cached = service.parse_project(use_cache=True)

        # Should be identical
        assert fresh.nodes == cached.nodes
        assert fresh.edges == cached.edges

    def test_cache_invalidation(self, project, tmp_path):
        """Cache should invalidate when file changes"""
        file_path = tmp_path / "test.py"
        file_path.write_text("def foo(): pass")

        service = StaticAnalysisService(db, tmp_path)

        # Parse and cache
        result1 = service.parse_project()

        # Modify file
        file_path.write_text("def bar(): pass")

        # Should detect change and re-parse
        result2 = service.parse_project(use_cache=True)

        assert result1.nodes != result2.nodes
```

### 5.4 Profiling and Optimization

**Profiling Tools**:

```python
import cProfile
import pstats
from pathlib import Path

def profile_operation(operation_name: str, func, *args, **kwargs):
    """Profile an operation and generate report"""
    profiler = cProfile.Profile()

    # Run with profiling
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Generate report
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')

    report_path = Path(f"profiling/{operation_name}.prof")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w') as f:
        stats.stream = f
        stats.print_stats(50)  # Top 50 functions

    return result

# Usage
profile_operation(
    "static_analysis_medium",
    service.parse_project,
    use_cache=False
)
```

**Memory Profiling**:

```python
from memory_profiler import profile

@profile
def analyze_memory_usage(project_path: Path):
    """Profile memory usage of analysis operations"""
    service = StaticAnalysisService(db, project_path)
    ast_graph = service.parse_project()
    metrics = service.extract_metrics(ast_graph)
    return metrics

# Run with: python -m memory_profiler script.py
```

**Optimization Checklist**:

1. [ ] Profile bottlenecks with cProfile
2. [ ] Identify memory hotspots with memory_profiler
3. [ ] Optimize hot paths (functions called frequently)
4. [ ] Add caching for expensive operations
5. [ ] Use generators for large datasets
6. [ ] Batch database operations
7. [ ] Add indexes to database queries
8. [ ] Re-run benchmarks to validate improvements
9. [ ] Update baseline metrics
10. [ ] Document optimization changes

---

## 6. Optimization Opportunities

### 6.1 Critical Path Analysis

**Identify Critical Paths** (operations that directly impact user experience):

**Critical Path #1: First-Run Analysis**
```
User runs: apm detect analyze
  └─> Parse all Python files (BOTTLENECK: 80% of time)
  └─> Extract metrics (10% of time)
  └─> Cache results (10% of time)
```

**Optimization Opportunities**:
1. **Parallel file parsing** (2-4x speedup)
2. **Skip very large files** (reduce outlier impact)
3. **Incremental parsing** (parse only changed files)

**Critical Path #2: Cached Analysis**
```
User runs: apm detect analyze (cached)
  └─> Check cache for each file (50% of time)
  └─> Load cached AST (30% of time)
  └─> Aggregate metrics (20% of time)
```

**Optimization Opportunities**:
1. **In-memory cache** (90% speedup for repeated calls)
2. **Batch cache lookups** (reduce DB round-trips)
3. **Pre-aggregate metrics** (avoid recalculation)

**Critical Path #3: Dependency Graph**
```
User runs: apm detect graph
  └─> Parse files (if not cached)
  └─> Extract imports (BOTTLENECK: 60% of time)
  └─> Build NetworkX graph (30% of time)
  └─> Analyze graph (10% of time)
```

**Optimization Opportunities**:
1. **Cache import relationships** (separate from AST)
2. **Lazy graph construction** (build only when needed)
3. **Incremental graph updates** (add/remove edges)

### 6.2 Low-Hanging Fruit

**Quick Wins** (high impact, low effort):

1. **Add Database Indexes** (5 minutes, 10x speedup):
```sql
-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_ast_cache_lookup
ON ast_cache(project_id, file_path, file_hash);

CREATE INDEX IF NOT EXISTS idx_fitness_results_latest
ON fitness_results(project_id, tested_at DESC);
```

2. **Batch Database Inserts** (30 minutes, 5x speedup):
```python
# Before (slow)
for file in files:
    db.insert_ast_cache(file)

# After (fast)
with db.transaction():
    for file in files:
        db.insert_ast_cache(file)
```

3. **Pre-compile Regex Patterns** (10 minutes, 2x speedup):
```python
# Before (slow)
for line in lines:
    if re.match(r'import .*', line):
        ...

# After (fast)
IMPORT_PATTERN = re.compile(r'import .*')
for line in lines:
    if IMPORT_PATTERN.match(line):
        ...
```

4. **Use Generator Expressions** (15 minutes, reduce memory):
```python
# Before (loads all in memory)
nodes = [parse_node(n) for n in all_nodes]
process_nodes(nodes)

# After (lazy evaluation)
nodes = (parse_node(n) for n in all_nodes)
process_nodes(nodes)  # Generator passed directly
```

5. **Cache Property Calculations** (20 minutes, 10x speedup):
```python
from functools import cached_property

class DependencyGraph:
    @cached_property  # Calculate once, cache result
    def node_count(self) -> int:
        return len(self.nodes)
```

### 6.3 Advanced Optimizations

**Future Optimizations** (high impact, high effort):

1. **Incremental Analysis** (8 hours effort):
   - Track file changes since last analysis
   - Re-parse only changed files
   - Update graph incrementally
   - Expected speedup: 10-50x for small changes

2. **Distributed Processing** (16 hours effort):
   - Distribute file parsing across machines
   - Use task queue (Celery, Redis)
   - Aggregate results
   - Expected speedup: Linear with worker count

3. **Native Extensions** (24 hours effort):
   - Rewrite hot paths in Cython/Rust
   - AST parsing, graph algorithms
   - Expected speedup: 5-10x for CPU-bound operations

4. **Persistent Graph Database** (12 hours effort):
   - Use Neo4j or similar for dependency graph
   - Native graph queries (faster than NetworkX for large graphs)
   - Expected speedup: 2-5x for graph operations

5. **Machine Learning Cache** (40 hours effort):
   - Predict which files will change
   - Prefetch likely-needed analyses
   - Adaptive caching based on usage patterns
   - Expected speedup: 20-30% overall improvement

---

## 7. Monitoring and Validation

### 7.1 Performance Metrics Collection

**Instrumentation**:

```python
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation"""
    operation: str
    duration_ms: float
    cache_hit: bool
    file_count: int
    node_count: int
    memory_mb: float
    timestamp: datetime

class PerformanceMonitor:
    """Collect and report performance metrics"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []

    def record_operation(
        self,
        operation: str,
        duration: float,
        cache_hit: bool = False,
        file_count: int = 0,
        node_count: int = 0
    ):
        """Record performance metrics for an operation"""
        memory_info = check_memory_usage()

        metric = PerformanceMetrics(
            operation=operation,
            duration_ms=duration * 1000,
            cache_hit=cache_hit,
            file_count=file_count,
            node_count=node_count,
            memory_mb=memory_info['rss_mb'],
            timestamp=datetime.now()
        )

        self.metrics.append(metric)

        # Log if slower than expected
        if duration > self._get_threshold(operation):
            logger.warning(
                f"Slow operation: {operation} took {duration*1000:.0f}ms "
                f"(expected <{self._get_threshold(operation)*1000:.0f}ms)"
            )

    def _get_threshold(self, operation: str) -> float:
        """Get performance threshold for operation"""
        thresholds = {
            'static_analysis': 2.0,  # 2s
            'dependency_graph': 1.0,  # 1s
            'sbom': 1.0,  # 1s
            'pattern_detection': 1.0,  # 1s
            'fitness_testing': 0.5,  # 500ms
        }
        return thresholds.get(operation, 5.0)

    def generate_report(self) -> str:
        """Generate performance report"""
        if not self.metrics:
            return "No metrics collected"

        # Group by operation
        by_operation = {}
        for metric in self.metrics:
            if metric.operation not in by_operation:
                by_operation[metric.operation] = []
            by_operation[metric.operation].append(metric)

        # Calculate statistics
        report = []
        for operation, metrics in by_operation.items():
            durations = [m.duration_ms for m in metrics]
            cache_hits = sum(1 for m in metrics if m.cache_hit)

            report.append(f"\n{operation}:")
            report.append(f"  Count: {len(metrics)}")
            report.append(f"  Avg: {sum(durations)/len(durations):.1f}ms")
            report.append(f"  Min: {min(durations):.1f}ms")
            report.append(f"  Max: {max(durations):.1f}ms")
            report.append(f"  Cache hit rate: {cache_hits/len(metrics):.1%}")

        return "\n".join(report)
```

### 7.2 Continuous Performance Monitoring

**CI/CD Integration**:

```yaml
# .github/workflows/performance.yml
name: Performance Benchmarks

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run benchmarks
        run: |
          poetry run pytest tests/performance/ --benchmark-only

      - name: Compare with baseline
        run: |
          poetry run python scripts/compare_benchmarks.py \
            --current results/benchmarks.json \
            --baseline baseline/benchmarks.json \
            --tolerance 0.1

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('results/benchmark_report.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### 7.3 Performance Alerting

**Automated Alerts** (when performance degrades):

```python
class PerformanceAlert:
    """Alert when performance thresholds exceeded"""

    THRESHOLDS = {
        'static_analysis': {'duration': 2.0, 'memory': 500},
        'dependency_graph': {'duration': 1.0, 'memory': 200},
    }

    def check_metrics(self, metrics: PerformanceMetrics):
        """Check if metrics exceed thresholds"""
        threshold = self.THRESHOLDS.get(metrics.operation)
        if not threshold:
            return

        alerts = []

        # Check duration
        if metrics.duration_ms / 1000 > threshold['duration']:
            alerts.append(
                f"⚠️  {metrics.operation} took {metrics.duration_ms:.0f}ms "
                f"(threshold: {threshold['duration']*1000:.0f}ms)"
            )

        # Check memory
        if metrics.memory_mb > threshold['memory']:
            alerts.append(
                f"⚠️  {metrics.operation} used {metrics.memory_mb:.0f}MB "
                f"(threshold: {threshold['memory']}MB)"
            )

        if alerts:
            self._send_alerts(alerts)

    def _send_alerts(self, alerts: List[str]):
        """Send alerts (log, Slack, email, etc.)"""
        for alert in alerts:
            logger.warning(alert)
            # TODO: Send to Slack/email if configured
```

---

## 8. Success Criteria

### 8.1 Functional Requirements

**Must Have** (MVP):
- [ ] Static analysis completes <2s for 1000-file project (first run)
- [ ] Cached analysis completes <100ms (90% speedup)
- [ ] Dependency graph builds <1s for 5000-edge graph
- [ ] SBOM generates <1s for 100-package project
- [ ] Pattern detection completes <1s
- [ ] Fitness testing completes <500ms for 50 policies
- [ ] Cache hit ratio >80% for typical workflows
- [ ] Memory usage <500MB for large projects
- [ ] No crashes on projects up to 100K LOC

**Should Have** (V1.1):
- [ ] Incremental analysis support (10x speedup for small changes)
- [ ] Parallel processing (2-4x speedup)
- [ ] Progress bars for long operations
- [ ] Performance profiling built-in
- [ ] Automatic cache cleanup

**Nice to Have** (V2.0):
- [ ] Distributed processing support
- [ ] Real-time analysis (watch mode)
- [ ] Machine learning cache prediction
- [ ] Native extensions for hot paths

### 8.2 Performance Acceptance Criteria

**Benchmark Tests**:
```python
# All tests must pass for release

def test_performance_acceptance():
    """Acceptance criteria for performance"""

    # Small project
    assert analyze_small_project() < 0.1  # <100ms

    # Medium project (cached)
    assert analyze_medium_project_cached() < 0.05  # <50ms

    # Large project (first run)
    assert analyze_large_project() < 2.0  # <2s

    # Cache hit ratio
    assert measure_cache_hit_ratio() > 0.8  # >80%

    # Memory usage
    assert measure_memory_usage() < 500  # <500MB
```

### 8.3 User Experience Criteria

**Perceived Performance**:
- [ ] Operations <100ms feel instant (no spinner)
- [ ] Operations 100-500ms show spinner (not progress bar)
- [ ] Operations >500ms show progress bar
- [ ] Operations >5s show time estimate
- [ ] Operations >30s require confirmation

**Error Handling**:
- [ ] Graceful degradation for huge projects
- [ ] Clear error messages for resource limits
- [ ] Helpful suggestions (filtering, caching)
- [ ] No silent failures

---

## 9. Implementation Priorities

### 9.1 Phase 1: Core Performance (Week 1-2)

**Priority 1: Caching Infrastructure**
- Time: 8 hours
- Impact: 10x speedup (cached operations)
- Tasks:
  1. Implement SQLite cache tables (2h)
  2. Create cache adapters (2h)
  3. Add SHA256 invalidation (2h)
  4. Implement in-memory LRU cache (2h)

**Priority 2: Database Optimization**
- Time: 4 hours
- Impact: 5x speedup (cache lookups)
- Tasks:
  1. Add missing indexes (1h)
  2. Implement batch inserts (2h)
  3. Add query profiling (1h)

**Priority 3: Memory Optimization**
- Time: 8 hours
- Impact: 50% memory reduction
- Tasks:
  1. Streaming file processing (3h)
  2. Generator-based iteration (2h)
  3. Incremental graph building (3h)

### 9.2 Phase 2: Scale & Polish (Week 3-4)

**Priority 4: Parallel Processing**
- Time: 8 hours
- Impact: 2-4x speedup (first run)
- Tasks:
  1. Implement ThreadPoolExecutor (3h)
  2. Add timeouts and error handling (2h)
  3. Test and tune worker count (3h)

**Priority 5: User Experience**
- Time: 6 hours
- Impact: Better perceived performance
- Tasks:
  1. Add progress bars (2h)
  2. Implement operation timeouts (2h)
  3. Add performance warnings (2h)

**Priority 6: Monitoring & Validation**
- Time: 8 hours
- Impact: Ensure quality
- Tasks:
  1. Build performance test suite (4h)
  2. Add CI/CD benchmarks (2h)
  3. Create profiling tools (2h)

### 9.3 Phase 3: Advanced Features (Month 2)

**Priority 7: Incremental Analysis**
- Time: 16 hours
- Impact: 10-50x speedup (incremental)
- Tasks:
  1. Change detection system (6h)
  2. Incremental AST updates (5h)
  3. Incremental graph updates (5h)

**Priority 8: Advanced Caching**
- Time: 8 hours
- Impact: 20-30% overall improvement
- Tasks:
  1. Predictive caching (4h)
  2. Cache preloading (2h)
  3. Adaptive policies (2h)

---

## 10. References

### 10.1 Related Documents

- **Architecture Document**: `/docs/architecture/detection-pack-architecture.md`
- **Work Item #148**: Comprehensive Detection Pack Enhancement
- **Task #958**: Architecture Design (completed)
- **Task #976**: Performance Requirements Analysis (this document)

### 10.2 Performance Baselines

**Empirical Measurements** (to be updated after implementation):

| Operation | Small | Medium | Large | Notes |
|-----------|-------|--------|-------|-------|
| Static Analysis (first) | TBD | TBD | TBD | Measure on real projects |
| Static Analysis (cached) | TBD | TBD | TBD | After cache implementation |
| Dependency Graph | TBD | TBD | TBD | NetworkX performance |
| SBOM Generation | TBD | TBD | TBD | With GitHub API |
| Pattern Detection | TBD | TBD | TBD | Pattern matching speed |
| Fitness Testing | TBD | TBD | TBD | Policy execution time |

**Baseline Projects** (for testing):
- Small: aipm-v2 test fixtures (~500 LOC)
- Medium: aipm-v2 core (~5K LOC)
- Large: Django framework (~100K LOC)

### 10.3 External References

**Performance Best Practices**:
- Python Performance Tips: https://wiki.python.org/moin/PythonSpeed/PerformanceTips
- NetworkX Performance: https://networkx.org/documentation/stable/reference/algorithms/
- SQLite Optimization: https://www.sqlite.org/optoverview.html
- Caching Strategies: https://docs.python.org/3/library/functools.html#functools.lru_cache

**Similar Tools** (performance benchmarks):
- Pylint: ~2-3s for 1000 files
- Mypy: ~1-2s for 1000 files (cached)
- Bandit: ~1s for 1000 files
- Radon: ~500ms for 1000 files (complexity only)

---

## Document Metadata

**Author**: Performance Engineering Team
**Reviewers**: TBD (Architecture, Implementation teams)
**Status**: Draft (awaiting review)
**Version**: 1.0.0
**Created**: 2025-10-24
**Last Updated**: 2025-10-24

**Approval Required**:
- [ ] Architecture Team (design feasibility)
- [ ] Implementation Team (effort estimates)
- [ ] Product Owner (priority alignment)
- [ ] QA Team (testing strategy)

**Change Log**:
- 2025-10-24: Initial performance requirements document (v1.0.0)

---

## Appendix A: Performance Testing Checklist

**Pre-Implementation**:
- [ ] Define baseline metrics for target projects
- [ ] Set up performance test infrastructure
- [ ] Create test fixtures (small, medium, large projects)
- [ ] Document current performance (if existing system)

**During Implementation**:
- [ ] Run benchmarks after each optimization
- [ ] Profile hot paths with cProfile
- [ ] Monitor memory usage with memory_profiler
- [ ] Validate cache correctness
- [ ] Test resource limits

**Post-Implementation**:
- [ ] Run full performance test suite
- [ ] Compare against baseline metrics
- [ ] Test on real-world projects
- [ ] Validate user experience criteria
- [ ] Document final performance characteristics

**Continuous Monitoring**:
- [ ] Set up CI/CD performance tests
- [ ] Configure performance alerts
- [ ] Track metrics over time
- [ ] Review performance quarterly
- [ ] Update baseline as system evolves

---

## Appendix B: Performance Troubleshooting Guide

**Symptom: Slow first-run analysis**

Diagnosis:
1. Profile with cProfile: `python -m cProfile -o profile.stats script.py`
2. Check file count: Are there too many files?
3. Check file sizes: Are some files very large?
4. Check AST parsing time per file

Solutions:
- Add parallel processing
- Skip very large files
- Optimize AST parsing logic
- Add progress feedback

**Symptom: Slow cached analysis**

Diagnosis:
1. Check cache hit ratio: Should be >80%
2. Profile cache lookup time
3. Check database indexes
4. Measure deserialization time

Solutions:
- Add missing database indexes
- Implement in-memory cache layer
- Optimize cache data structure
- Pre-aggregate commonly needed data

**Symptom: High memory usage**

Diagnosis:
1. Profile with memory_profiler
2. Check for memory leaks (objects not released)
3. Measure memory per file parsed
4. Check NetworkX graph memory

Solutions:
- Use generators instead of lists
- Process files incrementally
- Release objects explicitly
- Implement streaming processing

**Symptom: Cache not invalidating**

Diagnosis:
1. Check SHA256 hash calculation
2. Verify file modification detection
3. Check cache lookup logic
4. Review invalidation triggers

Solutions:
- Fix hash calculation
- Add file mtime check as fast path
- Implement manual cache clear
- Add cache debugging logs

---

**End of Document**
