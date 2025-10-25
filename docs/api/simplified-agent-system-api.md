# Simplified Agent System API Reference

## Overview

This document provides a comprehensive API reference for the Simplified Agent System, including all orchestrators, specialists, utilities, and generic agents.

## Core Orchestrators

### Workflow Orchestrator

#### `WorkflowOrchestrator`

**Purpose**: Master workflow coordination and high-level decision making

**Constructor**:
```python
WorkflowOrchestrator(db_service, performance_monitor=None)
```

**Methods**:

##### `coordinate_workflow(work_item: WorkItem) -> Dict[str, Any]`
Coordinates the entire workflow for a work item.

**Parameters**:
- `work_item` (WorkItem): The work item to coordinate

**Returns**:
- `Dict[str, Any]`: Coordination result with status and metrics

**Example**:
```python
orchestrator = WorkflowOrchestrator(db_service)
result = await orchestrator.coordinate_workflow(work_item)
```

##### `make_high_level_decisions(context: WorkflowContext) -> WorkflowDecision`
Makes high-level workflow decisions based on context.

**Parameters**:
- `context` (WorkflowContext): Workflow context

**Returns**:
- `WorkflowDecision`: High-level decision (PROCEED, PAUSE, ESCALATE, CANCEL, RETRY)

##### `handle_errors(error_context: Dict[str, Any]) -> Dict[str, Any]`
Handles workflow errors and recovery.

**Parameters**:
- `error_context` (Dict[str, Any]): Error context information

**Returns**:
- `Dict[str, Any]`: Recovery result

##### `monitor_performance(context: WorkflowContext, execution_time: float) -> None`
Monitors workflow performance metrics.

**Parameters**:
- `context` (WorkflowContext): Workflow context
- `execution_time` (float): Execution time in seconds

#### `WorkflowDecision` Enum
```python
class WorkflowDecision(Enum):
    PROCEED = "proceed"
    PAUSE = "pause"
    ESCALATE = "escalate"
    CANCEL = "cancel"
    RETRY = "retry"
```

#### `WorkflowContext` Dataclass
```python
@dataclass
class WorkflowContext:
    work_item: WorkItem
    current_phase: Phase
    tasks: List[Task]
    performance_metrics: Dict[str, Any]
    error_context: Optional[Dict[str, Any]] = None
```

### Phase Orchestrator

#### `PhaseOrchestrator`

**Purpose**: Phase-specific orchestration and phase gate enforcement

**Constructor**:
```python
PhaseOrchestrator(db_service, quality_orchestrator=None)
```

**Methods**:

##### `orchestrate_phase(phase: Phase, work_item: WorkItem) -> Dict[str, Any]`
Orchestrates a specific phase.

**Parameters**:
- `phase` (Phase): The phase to orchestrate
- `work_item` (WorkItem): The work item being processed

**Returns**:
- `Dict[str, Any]`: Phase orchestration result

**Example**:
```python
orchestrator = PhaseOrchestrator(db_service)
result = await orchestrator.orchestrate_phase(Phase.I1_IMPLEMENTATION, work_item)
```

##### `enforce_phase_gates(phase: Phase, work_item: WorkItem) -> Dict[str, Any]`
Enforces phase-specific quality gates.

**Parameters**:
- `phase` (Phase): The phase to enforce gates for
- `work_item` (WorkItem): The work item being processed

**Returns**:
- `Dict[str, Any]`: Gate enforcement results

##### `manage_phase_transitions(from_phase: Phase, to_phase: Phase, work_item: WorkItem) -> Dict[str, Any]`
Manages transitions between phases.

**Parameters**:
- `from_phase` (Phase): The phase transitioning from
- `to_phase` (Phase): The phase transitioning to
- `work_item` (WorkItem): The work item being processed

**Returns**:
- `Dict[str, Any]`: Transition result

#### `PhaseGateStatus` Enum
```python
class PhaseGateStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"
```

#### `PhaseGate` Dataclass
```python
@dataclass
class PhaseGate:
    name: str
    description: str
    required: bool
    status: PhaseGateStatus
    validation_function: str
    error_message: Optional[str] = None
```

### Quality Orchestrator

#### `QualityOrchestrator`

**Purpose**: Quality gate enforcement and compliance checking

**Constructor**:
```python
QualityOrchestrator(db_service, metrics_collector=None)
```

**Methods**:

##### `enforce_quality_gates(gate_type: QualityGateType, work_item: WorkItem) -> Dict[str, Any]`
Enforces specific quality gates.

**Parameters**:
- `gate_type` (QualityGateType): The type of quality gates to enforce
- `work_item` (WorkItem): The work item being processed

**Returns**:
- `Dict[str, Any]`: Quality gate enforcement results

**Example**:
```python
orchestrator = QualityOrchestrator(db_service)
result = await orchestrator.enforce_quality_gates(QualityGateType.FUNCTIONAL, work_item)
```

##### `validate_gates(gates: List[QualityGate], work_item: WorkItem) -> Dict[str, Any]`
Validates quality gates for a work item.

**Parameters**:
- `gates` (List[QualityGate]): List of quality gates to validate
- `work_item` (WorkItem): The work item being processed

**Returns**:
- `Dict[str, Any]`: Gate validation results

##### `track_quality_metrics(work_item: WorkItem) -> Dict[str, Any]`
Tracks quality metrics for a work item.

**Parameters**:
- `work_item` (WorkItem): The work item to track metrics for

**Returns**:
- `Dict[str, Any]`: Quality metrics results

##### `ensure_compliance(work_item: WorkItem) -> Dict[str, Any]`
Ensures compliance with quality standards.

**Parameters**:
- `work_item` (WorkItem): The work item to check compliance for

**Returns**:
- `Dict[str, Any]`: Compliance check results

#### `QualityGateType` Enum
```python
class QualityGateType(Enum):
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    USABILITY = "usability"
    MAINTAINABILITY = "maintainability"
```

#### `QualityLevel` Enum
```python
class QualityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

#### `QualityGate` Dataclass
```python
@dataclass
class QualityGate:
    name: str
    description: str
    gate_type: QualityGateType
    level: QualityLevel
    required: bool
    validation_function: str
    threshold: Optional[float] = None
    error_message: Optional[str] = None
```

## Performance Optimizer

### `PerformanceOptimizer`

**Purpose**: System performance optimization and monitoring

**Constructor**:
```python
PerformanceOptimizer(db_path: str)
```

**Methods**:

##### `optimize_taskstart(task_id: int, work_item_id: int, project_id: int) -> Dict[str, Any]`
Optimizes TaskStart hook performance.

**Parameters**:
- `task_id` (int): Task ID
- `work_item_id` (int): Work item ID
- `project_id` (int): Project ID

**Returns**:
- `Dict[str, Any]`: Optimization result with performance metrics

**Example**:
```python
optimizer = PerformanceOptimizer(db_path)
result = await optimizer.optimize_taskstart(1, 1, 1)
```

##### `get_performance_stats() -> Dict[str, Any]`
Gets performance statistics.

**Returns**:
- `Dict[str, Any]`: Performance statistics

##### `clear_cache() -> None`
Clears all caches.

##### `enable_optimization() -> None`
Enables performance optimization.

##### `disable_optimization() -> None`
Disables performance optimization.

##### `close() -> None`
Closes optimizer and cleanup resources.

### Caching Classes

#### `LRUCache`

**Purpose**: LRU Cache with TTL support

**Constructor**:
```python
LRUCache(size: int = 1000, ttl: float = 60.0)
```

**Methods**:

##### `get(key: str) -> Optional[Any]`
Gets value from cache.

##### `set(key: str, value: Any, ttl: Optional[float] = None) -> None`
Sets value in cache.

##### `clear() -> None`
Clears cache.

##### `stats() -> Dict[str, Any]`
Gets cache statistics.

#### `MultiLevelCache`

**Purpose**: Multi-level cache with smart promotion

**Constructor**:
```python
MultiLevelCache()
```

**Methods**:

##### `get(key: str) -> Optional[Any]`
Gets value from multi-level cache.

##### `set(key: str, value: Any, level: CacheLevel = CacheLevel.L1) -> None`
Sets value in appropriate cache level.

##### `clear() -> None`
Clears all cache levels.

##### `stats() -> Dict[str, Any]`
Gets multi-level cache statistics.

#### `CacheLevel` Enum
```python
class CacheLevel(Enum):
    L1 = "l1"  # 1 minute TTL
    L2 = "l2"  # 5 minute TTL
    L3 = "l3"  # 30 minute TTL
```

### Database Connection Pool

#### `DatabaseConnectionPool`

**Purpose**: Database connection pool for performance optimization

**Constructor**:
```python
DatabaseConnectionPool(db_path: str, pool_size: int = 10)
```

**Methods**:

##### `get_connection() -> sqlite3.Connection`
Gets connection from pool.

##### `return_connection(conn: sqlite3.Connection) -> None`
Returns connection to pool.

##### `close_all() -> None`
Closes all connections.

## Performance Decorators

### `@cache_result(ttl: float = 300, level: CacheLevel = CacheLevel.L2)`

Decorator to cache function results.

**Parameters**:
- `ttl` (float): Time to live in seconds
- `level` (CacheLevel): Cache level

**Example**:
```python
@cache_result(ttl=300, level=CacheLevel.L2)
async def expensive_operation(value):
    return f"result_{value}"
```

### `@measure_performance(operation_name: str)`

Decorator to measure function performance.

**Parameters**:
- `operation_name` (str): Name of the operation

**Example**:
```python
@measure_performance("test_operation")
async def test_function():
    return "success"
```

## Factory Functions

### `create_workflow_orchestrator(db_service, performance_monitor=None) -> WorkflowOrchestrator`
Creates a new workflow orchestrator instance.

### `create_phase_orchestrator(db_service, quality_orchestrator=None) -> PhaseOrchestrator`
Creates a new phase orchestrator instance.

### `create_quality_orchestrator(db_service, metrics_collector=None) -> QualityOrchestrator`
Creates a new quality orchestrator instance.

### `create_performance_optimizer(db_path: str) -> PerformanceOptimizer`
Creates a new performance optimizer instance.

## Data Models

### `WorkflowContext`
```python
@dataclass
class WorkflowContext:
    work_item: WorkItem
    current_phase: Phase
    tasks: List[Task]
    performance_metrics: Dict[str, Any]
    error_context: Optional[Dict[str, Any]] = None
```

### `PhaseContext`
```python
@dataclass
class PhaseContext:
    work_item: WorkItem
    phase: Phase
    tasks: List[Task]
    gates: List[PhaseGate]
    phase_metrics: Dict[str, Any]
```

### `QualityMetrics`
```python
@dataclass
class QualityMetrics:
    gate_name: str
    value: float
    threshold: float
    passed: bool
    timestamp: float
    details: Dict[str, Any]
```

### `PerformanceMetrics`
```python
@dataclass
class PerformanceMetrics:
    operation: str
    duration: float
    timestamp: float
    cache_hit: bool
    details: Dict[str, Any]
```

## Error Handling

### Common Exceptions

#### `WorkflowError`
Raised when workflow coordination fails.

#### `PhaseError`
Raised when phase orchestration fails.

#### `QualityError`
Raised when quality gate validation fails.

#### `PerformanceError`
Raised when performance optimization fails.

### Error Recovery

The system includes automatic error recovery mechanisms:

- **Timeout Errors**: Automatic retry with exponential backoff
- **Validation Failures**: Escalation to manual intervention
- **Agent Unavailability**: Retry with backoff
- **Performance Degradation**: Automatic pause and investigation

## Usage Examples

### Basic Workflow Coordination
```python
from agentpm.core.agents.simplified.workflow_orchestrator import create_workflow_orchestrator

# Create orchestrator
orchestrator = create_workflow_orchestrator(db_service)

# Coordinate workflow
result = await orchestrator.coordinate_workflow(work_item)
print(f"Status: {result['status']}")
print(f"Execution time: {result['execution_time']}ms")
```

### Phase Orchestration
```python
from agentpm.core.agents.simplified.phase_orchestrator import create_phase_orchestrator
from agentpm.database.enums import Phase

# Create orchestrator
orchestrator = create_phase_orchestrator(db_service)

# Orchestrate implementation phase
result = await orchestrator.orchestrate_phase(Phase.I1_IMPLEMENTATION, work_item)
print(f"Phase result: {result['phase_result']}")
```

### Quality Gate Enforcement
```python
from agentpm.core.agents.simplified.quality_orchestrator import create_quality_orchestrator, QualityGateType

# Create orchestrator
orchestrator = create_quality_orchestrator(db_service)

# Enforce functional quality gates
result = await orchestrator.enforce_quality_gates(QualityGateType.FUNCTIONAL, work_item)
print(f"Quality report: {result['quality_report']}")
```

### Performance Optimization
```python
from agentpm.core.performance.optimizer import create_performance_optimizer

# Create optimizer
optimizer = create_performance_optimizer(db_path)

# Optimize TaskStart
result = await optimizer.optimize_taskstart(task_id, work_item_id, project_id)
print(f"Performance target met: {result['performance_target_met']}")

# Get performance stats
stats = optimizer.get_performance_stats()
print(f"Average duration: {stats['average_duration']}ms")
print(f"Cache hit rate: {stats['cache_hit_rate']}")
```

### Caching Usage
```python
from agentpm.core.performance.optimizer import LRUCache, CacheLevel

# Create cache
cache = LRUCache(size=1000, ttl=60)

# Set value
cache.set("key1", "value1")

# Get value
value = cache.get("key1")
print(f"Value: {value}")

# Get stats
stats = cache.stats()
print(f"Cache size: {stats['size']}")
```

## Best Practices

### 1. Error Handling
- Always handle exceptions appropriately
- Use automatic recovery mechanisms
- Monitor error rates and patterns
- Provide meaningful error messages

### 2. Performance Optimization
- Use caching effectively
- Monitor performance metrics
- Optimize database queries
- Use parallel processing where possible

### 3. Quality Assurance
- Enforce quality gates consistently
- Monitor quality metrics
- Address quality issues promptly
- Maintain compliance requirements

### 4. Resource Management
- Close resources properly
- Monitor memory usage
- Use connection pooling
- Clean up temporary data

## Troubleshooting

### Common Issues

#### Import Errors
- Ensure all dependencies are installed
- Check import paths
- Verify module structure

#### Performance Issues
- Check cache hit rates
- Monitor database query performance
- Review memory usage
- Analyze execution times

#### Quality Gate Failures
- Review validation logic
- Check threshold values
- Verify data quality
- Address compliance issues

#### Workflow Errors
- Check error logs
- Review decision logic
- Verify agent availability
- Monitor system health

### Debugging Tips

1. **Enable Logging**: Use appropriate log levels
2. **Monitor Metrics**: Track performance and quality metrics
3. **Use Debugging Tools**: Leverage built-in debugging capabilities
4. **Review Error Messages**: Check error details and context
5. **Test Incrementally**: Test components individually

## Conclusion

The Simplified Agent System API provides a comprehensive set of tools for workflow coordination, phase management, quality assurance, and performance optimization. With clear interfaces, robust error handling, and extensive monitoring capabilities, the API enables efficient and reliable agent-based project management.

Key features:
- **Comprehensive Coverage**: All system components are accessible via API
- **Type Safety**: Strong typing with dataclasses and enums
- **Error Handling**: Robust error handling and recovery mechanisms
- **Performance Monitoring**: Built-in performance tracking and optimization
- **Extensibility**: Easy to extend and customize
- **Documentation**: Comprehensive API documentation and examples
