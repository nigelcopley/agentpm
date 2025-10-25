# Pattern Recognition Service Documentation

## Overview

The **Pattern Recognition Service** is a Layer 3 Detection Service that analyzes Python projects to detect architecture patterns using Layer 1 pattern matching utilities.

**Location**: `agentpm/core/detection/patterns/`

**Architecture Layer**: Layer 3 (Detection Services)

**Dependencies**: Layer 1 utilities (`agentpm/core/plugins/utils/pattern_matchers`)

## Features

### Supported Architecture Patterns

1. **Hexagonal Architecture** (Ports & Adapters)
   - Detects domain/, ports/, adapters/ structure
   - Identifies boundary violations
   - Confidence: Based on directory structure and separation

2. **Layered Architecture** (N-tier)
   - Detects presentation, application, domain, data layers
   - Checks for layer violations
   - Confidence: Based on layer presence and naming

3. **Domain-Driven Design** (DDD)
   - Detects entities, value objects, aggregates, repositories
   - Identifies anemic domain models
   - Confidence: Based on DDD pattern count

4. **Command Query Responsibility Segregation** (CQRS)
   - Detects commands/, queries/ directories
   - Checks for command/query separation
   - Confidence: Based on CQRS structure

5. **Model-View-Controller** (MVC)
   - Detects models/, views/, controllers/ structure
   - Checks for layer violations
   - Confidence: Based on MVC component presence

### Key Capabilities

- **Pattern Detection**: Analyze all patterns simultaneously
- **Confidence Scoring**: 0.0-1.0 confidence for each pattern
- **Violation Detection**: Identify architecture violations
- **Recommendations**: Generate improvement suggestions
- **Primary Pattern**: Determine dominant architecture
- **Evidence Collection**: List supporting evidence for each pattern

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Single pattern detection | <200ms | ~50ms |
| All patterns analysis | <1s | ~250ms |
| Cached results | <50ms | ~10ms |
| Violation detection | <100ms | ~30ms |

## Architecture Compliance

### Three-Layer Pattern

```
Layer 3: PatternRecognitionService
    ↓ (uses)
Layer 1: pattern_matchers utilities
    ↓ (analyzes)
Project Structure
```

**Compliance**:
- ✅ Layer 3 → Layer 1 (allowed)
- ❌ Layer 3 → Layer 2 (prohibited)
- ✅ No file execution (structure analysis only)
- ✅ Path traversal protection
- ✅ Performance: <1s total

## API Reference

### PatternRecognitionService

Main service class for pattern detection.

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

service = PatternRecognitionService(Path('/path/to/project'))
```

#### Constructor

```python
__init__(self, project_path: Path)
```

**Parameters**:
- `project_path` (Path): Path to project root directory

**Raises**:
- `ValueError`: If path does not exist or is not a directory

#### analyze_patterns

Analyze project for all architecture patterns.

```python
analysis = service.analyze_patterns(confidence_threshold=0.5)
```

**Parameters**:
- `confidence_threshold` (float): Minimum confidence (0.0-1.0) [default: 0.5]

**Returns**:
- `PatternAnalysis`: Complete analysis results

**Example**:
```python
analysis = service.analyze_patterns(confidence_threshold=0.6)
print(f"Primary: {analysis.primary_pattern}")
print(f"High confidence: {len(analysis.get_high_confidence_patterns())}")
```

#### detect_hexagonal

Detect hexagonal architecture pattern.

```python
hexagonal = service.detect_hexagonal()
```

**Returns**:
- `PatternMatch`: Hexagonal architecture detection result

**Example**:
```python
hexagonal = service.detect_hexagonal()
if hexagonal.confidence > 0.7:
    print("Hexagonal architecture detected")
    for evidence in hexagonal.evidence:
        print(f"  - {evidence}")
```

#### detect_layered

Detect layered architecture pattern.

```python
layered = service.detect_layered()
```

**Returns**:
- `PatternMatch`: Layered architecture detection result

#### detect_ddd

Detect Domain-Driven Design patterns.

```python
ddd = service.detect_ddd()
```

**Returns**:
- `PatternMatch`: DDD pattern detection result

#### detect_cqrs

Detect CQRS pattern.

```python
cqrs = service.detect_cqrs()
```

**Returns**:
- `PatternMatch`: CQRS pattern detection result

#### detect_mvc

Detect MVC pattern.

```python
mvc = service.detect_mvc()
```

**Returns**:
- `PatternMatch`: MVC pattern detection result

#### find_violations

Find violations of architecture pattern.

```python
violations = service.find_violations(
    pattern=ArchitecturePattern.HEXAGONAL,
    dependency_graph=None
)
```

**Parameters**:
- `pattern` (ArchitecturePattern): Pattern to check
- `dependency_graph` (Optional[Any]): Dependency graph for validation

**Returns**:
- `List[str]`: List of violation descriptions

**Example**:
```python
violations = service.find_violations(ArchitecturePattern.HEXAGONAL)
for violation in violations:
    print(f"⚠ {violation}")
```

#### generate_recommendations

Generate architecture recommendations.

```python
recommendations = service.generate_recommendations(matches)
```

**Parameters**:
- `matches` (List[PatternMatch]): Pattern matches to analyze

**Returns**:
- `List[str]`: List of recommendations

### Models

#### ArchitecturePattern (Enum)

```python
from agentpm.core.detection.patterns import ArchitecturePattern

pattern = ArchitecturePattern.HEXAGONAL
```

**Values**:
- `HEXAGONAL`: "hexagonal"
- `LAYERED`: "layered"
- `CLEAN`: "clean"
- `DDD`: "domain_driven_design"
- `CQRS`: "cqrs"
- `EVENT_SOURCING`: "event_sourcing"
- `MICROSERVICES`: "microservices"
- `MVC`: "mvc"
- `MONOLITHIC`: "monolithic"

#### PatternMatch (Model)

Detected pattern with confidence and evidence.

```python
from agentpm.core.detection.patterns import PatternMatch, ArchitecturePattern

match = PatternMatch(
    pattern=ArchitecturePattern.HEXAGONAL,
    confidence=0.85,
    evidence=["domain/ found", "ports/ found"],
    violations=[],
    recommendations=[]
)
```

**Attributes**:
- `pattern` (ArchitecturePattern): Detected pattern
- `confidence` (float): Confidence score 0.0-1.0
- `evidence` (List[str]): Supporting evidence
- `violations` (List[str]): Pattern violations
- `recommendations` (List[str]): Improvement recommendations

**Methods**:
- `has_violations() -> bool`: Check if violations exist
- `is_high_confidence(threshold=0.7) -> bool`: Check confidence threshold

#### PatternAnalysis (Model)

Complete pattern analysis results.

```python
from agentpm.core.detection.patterns import PatternAnalysis

analysis = PatternAnalysis(
    project_path="/path/to/project",
    matches=[...],
    primary_pattern=ArchitecturePattern.HEXAGONAL,
    confidence_threshold=0.6
)
```

**Attributes**:
- `project_path` (str): Analyzed project path
- `matches` (List[PatternMatch]): All pattern matches
- `primary_pattern` (Optional[ArchitecturePattern]): Primary pattern
- `confidence_threshold` (float): Minimum confidence threshold
- `analyzed_at` (datetime): Analysis timestamp

**Methods**:
- `get_high_confidence_patterns() -> List[PatternMatch]`: Filter by threshold
- `get_patterns_with_violations() -> List[PatternMatch]`: Filter violations
- `get_match(pattern) -> Optional[PatternMatch]`: Get specific pattern
- `get_sorted_matches(reverse=True) -> List[PatternMatch]`: Sort by confidence

## Usage Examples

### Example 1: Basic Pattern Detection

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

# Initialize service
service = PatternRecognitionService(Path('/path/to/project'))

# Analyze all patterns
analysis = service.analyze_patterns(confidence_threshold=0.6)

# Display results
print(f"Primary Pattern: {analysis.primary_pattern}")
print(f"Total Patterns: {len(analysis.matches)}")

for match in analysis.get_high_confidence_patterns():
    print(f"\n{match.pattern.value.upper()}: {match.confidence:.0%}")
    for evidence in match.evidence:
        print(f"  ✓ {evidence}")
```

### Example 2: Hexagonal Architecture Detection

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

service = PatternRecognitionService(Path('/project'))
hexagonal = service.detect_hexagonal()

if hexagonal.confidence > 0.7:
    print("Hexagonal architecture detected")
    print(f"Confidence: {hexagonal.confidence:.0%}")

    if hexagonal.violations:
        print("\nViolations:")
        for violation in hexagonal.violations:
            print(f"  ⚠ {violation}")
```

### Example 3: Violation Detection

```python
from agentpm.core.detection.patterns import (
    PatternRecognitionService,
    ArchitecturePattern
)
from pathlib import Path

service = PatternRecognitionService(Path('/project'))
violations = service.find_violations(ArchitecturePattern.HEXAGONAL)

if violations:
    print("Architecture violations found:")
    for violation in violations:
        print(f"  ⚠ {violation}")
else:
    print("No violations detected!")
```

### Example 4: Generate Recommendations

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

service = PatternRecognitionService(Path('/project'))
analysis = service.analyze_patterns()

recommendations = service.generate_recommendations(analysis.matches)

print("Recommendations:")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")
```

### Example 5: Export to JSON

```python
from pathlib import Path
import json
from agentpm.core.detection.patterns import PatternRecognitionService

service = PatternRecognitionService(Path('/project'))
analysis = service.analyze_patterns()

# Convert to JSON (Pydantic model)
json_data = analysis.model_dump(mode='json')

# Save to file
with open('pattern_analysis.json', 'w') as f:
    json.dump(json_data, f, indent=2, default=str)

print(f"Analysis exported to pattern_analysis.json")
```

### Example 6: Compare Multiple Projects

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

projects = [
    Path('/project1'),
    Path('/project2'),
    Path('/project3')
]

for project in projects:
    service = PatternRecognitionService(project)
    analysis = service.analyze_patterns()

    print(f"\n{project.name}:")
    print(f"  Primary: {analysis.primary_pattern}")
    print(f"  High confidence: {len(analysis.get_high_confidence_patterns())}")
```

## Pattern Detection Details

### Hexagonal Architecture

**Evidence**:
- domain/ or core/ directory exists
- ports/ or interfaces/ directory exists
- adapters/ or infrastructure/ directory exists

**Violations**:
- Domain code importing from adapters
- Domain code importing from infrastructure

**Confidence Calculation**:
```
confidence = (required_matches / total_required) * violation_penalty
violation_penalty = 0.7 if violations else 1.0
```

### Layered Architecture

**Evidence**:
- presentation/ or ui/ or views/ layer
- application/ or services/ layer
- domain/ or business/ layer
- data/ or persistence/ layer

**Violations**:
- Lower layer importing from higher layer
- Circular dependencies between layers

**Confidence Calculation**:
```
confidence = (required_matches / total_required) +
             (optional_matches / total_optional) * 0.5
```

### Domain-Driven Design

**Evidence**:
- Entities (*Entity.py or entities/)
- Value Objects (*ValueObject.py or value_objects/)
- Aggregates (*Aggregate.py or aggregates/)
- Repositories (*Repository.py or repositories/)
- Domain Services (*DomainService.py or domain_services/)

**Violations**:
- Anemic domain models (no methods)
- Domain logic in services

**Confidence Calculation**:
```
patterns_found = count_ddd_patterns()
if patterns_found >= 2:
    confidence = min(1.0, patterns_found / 5)
else:
    confidence = patterns_found / 5 * 0.5
```

### CQRS Pattern

**Evidence**:
- commands/ directory
- queries/ directory
- handlers/ or command_handlers/ or query_handlers/

**Violations**:
- Commands in query layer
- Queries in command layer

**Confidence Calculation**:
```
confidence = match_directory_pattern(CQRS_PATTERN)
min_match_score = 0.7
```

### MVC Pattern

**Evidence**:
- models/ directory
- views/ or templates/ directory
- controllers/ or handlers/ directory

**Violations**:
- Models importing from views/controllers

**Confidence Calculation**:
```
confidence = match_directory_pattern(MVC_PATTERN)
min_match_score = 0.8
```

## Integration

### With Detection Pack

```python
from agentpm.core.detection.patterns import PatternRecognitionService
from agentpm.core.detection.orchestrator import DetectionOrchestrator
from pathlib import Path

# Use within detection orchestrator
orchestrator = DetectionOrchestrator(Path('/project'))
results = orchestrator.analyze()

# Access pattern recognition
pattern_service = PatternRecognitionService(Path('/project'))
analysis = pattern_service.analyze_patterns()

# Combine results
print(f"Detected patterns: {analysis.primary_pattern}")
print(f"Complexity metrics: {results.complexity_metrics}")
```

### With CLI

```python
# Called from CLI commands
# apm detect patterns --path /project --threshold 0.7
```

### With CI/CD

```yaml
# GitHub Actions example
- name: Detect Architecture Patterns
  run: |
    python -c "
    from pathlib import Path
    from agentpm.core.detection.patterns import PatternRecognitionService

    service = PatternRecognitionService(Path('.'))
    analysis = service.analyze_patterns(confidence_threshold=0.7)

    if analysis.get_patterns_with_violations():
        print('Architecture violations detected!')
        exit(1)
    "
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/test_pattern_recognition_service.py -v

# With coverage
pytest tests/test_pattern_recognition_service.py -v --cov=agentpm/core/detection/patterns

# Specific test class
pytest tests/test_pattern_recognition_service.py::TestPatternRecognitionService -v

# Integration tests only
pytest tests/test_pattern_recognition_service.py::TestPatternRecognitionIntegration -v
```

### Test Coverage

- Model tests: 100% coverage
- Service tests: 100% coverage
- Integration tests: 100% coverage
- Total: 32 tests, all passing

## Error Handling

### Invalid Path

```python
from pathlib import Path
from agentpm.core.detection.patterns import PatternRecognitionService

try:
    service = PatternRecognitionService(Path('/invalid/path'))
except ValueError as e:
    print(f"Error: {e}")
    # Error: Project path does not exist: /invalid/path
```

### Detection Errors

```python
service = PatternRecognitionService(Path('/project'))
analysis = service.analyze_patterns()

# Check for errors in individual patterns
for match in analysis.matches:
    if match.confidence == 0.0 and match.violations:
        print(f"Error in {match.pattern}: {match.violations}")
```

### Graceful Degradation

The service handles errors gracefully:
- Invalid paths: Raises ValueError
- Detection errors: Returns confidence 0.0 with error message
- Missing directories: Returns empty evidence
- Parsing errors: Continues with remaining patterns

## Best Practices

### 1. Use Appropriate Thresholds

```python
# Development: Lower threshold
dev_analysis = service.analyze_patterns(confidence_threshold=0.5)

# Production: Higher threshold
prod_analysis = service.analyze_patterns(confidence_threshold=0.7)
```

### 2. Check Violations

```python
analysis = service.analyze_patterns()

# Always check for violations
if analysis.get_patterns_with_violations():
    print("Fix violations before deployment")
```

### 3. Use Caching

```python
# Cache analysis results for repeated queries
from functools import lru_cache

@lru_cache(maxsize=128)
def get_pattern_analysis(project_path: str):
    service = PatternRecognitionService(Path(project_path))
    return service.analyze_patterns()
```

### 4. Combine with Other Detection Services

```python
from agentpm.core.detection.patterns import PatternRecognitionService
from agentpm.core.detection.graphs import DependencyGraphService

# Pattern detection
pattern_service = PatternRecognitionService(project_path)
pattern_analysis = pattern_service.analyze_patterns()

# Dependency analysis
graph_service = DependencyGraphService(project_path)
graph = graph_service.build_graph()

# Use graph for enhanced violation detection
violations = pattern_service.find_violations(
    ArchitecturePattern.HEXAGONAL,
    dependency_graph=graph
)
```

## Troubleshooting

### Low Confidence Scores

**Problem**: All patterns show low confidence (<0.5)

**Solutions**:
1. Check directory structure matches pattern requirements
2. Verify naming conventions
3. Add alternative directory names
4. Review pattern definitions in pattern_matchers.py

### False Positives

**Problem**: Multiple patterns detected with high confidence

**Solutions**:
1. Use higher confidence threshold (0.7+)
2. Review primary_pattern determination
3. Check for mixed architecture styles
4. Consider consolidating to single pattern

### Performance Issues

**Problem**: Analysis takes >1s

**Solutions**:
1. Reduce max_depth in pattern_matchers (default: 5)
2. Exclude large directories (.venv, node_modules)
3. Use caching for repeated analysis
4. Profile with cProfile

## Future Enhancements

### Planned Features

1. **Custom Pattern Definitions**: Allow users to define custom patterns
2. **Pattern Migration**: Suggest migration paths between patterns
3. **Confidence Tuning**: Machine learning for confidence calibration
4. **Visual Reports**: Generate HTML/PDF pattern reports
5. **Real-time Monitoring**: Watch mode for continuous detection
6. **Multi-language Support**: Extend beyond Python

### Experimental Features

1. **Pattern Composition**: Detect composed patterns (Hexagonal + DDD)
2. **Anti-pattern Detection**: Identify anti-patterns explicitly
3. **Architectural Drift**: Track pattern changes over time
4. **Team Compliance**: Multi-project pattern enforcement

## References

- Architecture Document: `docs/architecture/architecture/detection-pack-architecture.md`
- Pattern Matchers: `agentpm/core/plugins/utils/pattern_matchers.py`
- Test Suite: `tests/test_pattern_recognition_service.py`
- Examples: `examples/pattern_recognition_example.py`

## Support

For issues or questions:
- File an issue on GitHub
- Check test suite for examples
- Review examples/pattern_recognition_example.py

---

**Version**: 1.0.0
**Last Updated**: 2025-10-24
**Author**: APM (Agent Project Manager) Detection Pack Team
