# Fitness Engine - Architecture Fitness Testing

Policy-based architecture fitness testing for APM (Agent Project Manager) Detection Pack.

## Overview

The Fitness Engine validates code quality, architectural patterns, and best practices compliance using a policy-based approach. It executes validation rules against your project's AST, dependency graphs, and metrics to identify violations and calculate compliance scores.

## Quick Start

```python
from pathlib import Path
from agentpm.core.detection.fitness import FitnessEngine

# Initialize engine
engine = FitnessEngine(Path.cwd())

# Load default policies
policies = engine.load_default_policies()

# Run tests
result = engine.run_tests(policies)

# Check results
if result.is_passing():
    print(f"✓ PASSED - Compliance: {result.compliance_score:.0%}")
else:
    print(f"✗ FAILED - {result.error_count} errors, {result.warning_count} warnings")
```

## Architecture

### Layer 3 Compliance

The Fitness Engine follows APM (Agent Project Manager)'s three-layer architecture:

- **Layer 1 (Utilities)**: Uses `graph_builders`, `metrics_calculator` for primitives
- **Layer 3 (Services)**: Uses `StaticAnalysisService`, `DependencyGraphService` for analysis
- **No Layer 2 dependencies**: Does NOT import from plugins

### Components

```
agentpm/core/detection/fitness/
├── __init__.py          # Package exports
├── models.py            # Pydantic models (Policy, PolicyViolation, FitnessResult)
├── policies.py          # Built-in default policies
├── engine.py            # FitnessEngine (main service)
└── README.md            # This file
```

## Built-in Policies

### Dependency Policies

- **NO_CIRCULAR_DEPENDENCIES** (ERROR): No circular dependencies between modules
- **MAX_DEPENDENCY_DEPTH** (WARNING): Dependency chains ≤ 10 levels deep

### Complexity Policies

- **MAX_CYCLOMATIC_COMPLEXITY** (WARNING): Functions ≤ 10 complexity
- **MAX_FUNCTION_COMPLEXITY_STRICT** (ERROR): Functions ≤ 20 complexity (hard limit)

### Size Policies

- **MAX_FILE_LOC** (WARNING): Files ≤ 500 lines of code
- **MAX_FUNCTION_LOC** (INFO): Functions ≤ 50 lines of code

### Architecture Policies

- **NO_LAYERING_VIOLATIONS** (ERROR): Lower layers must not depend on higher layers

### Maintainability Policies

- **MIN_MAINTAINABILITY_INDEX** (WARNING): Files ≥ 65 MI
- **MIN_MAINTAINABILITY_INDEX_STRICT** (ERROR): Files ≥ 40 MI (critical threshold)

### Code Quality Policies

- **MAX_COUPLING** (INFO): Module instability ≤ 0.8
- **REQUIRE_DOCSTRINGS** (INFO, disabled): Documentation coverage

## Usage Examples

### Example 1: Basic Fitness Testing

```python
from pathlib import Path
from agentpm.core.detection.fitness import FitnessEngine, PolicyLevel

# Initialize
engine = FitnessEngine(Path("/my/project"))

# Load and run
policies = engine.load_default_policies()
result = engine.run_tests(policies)

# Print summary
print(result.get_summary())
# Output: PASSED - 8 passed, 2 warnings, 0 errors (90% compliance)

# Print violations
for violation in result.violations:
    print(f"{violation.level.upper()}: {violation.message}")
    print(f"  Location: {violation.location}")
    print(f"  Fix: {violation.suggestion}")
```

### Example 2: Filter Policies by Tag

```python
from agentpm.core.detection.fitness import FitnessEngine
from agentpm.core.detection.fitness.policies import get_policies_by_tag, create_policy_from_dict

engine = FitnessEngine(Path.cwd())

# Get only complexity policies
complexity_policies_dicts = get_policies_by_tag("complexity")
complexity_policies = [create_policy_from_dict(p) for p in complexity_policies_dicts]

# Run complexity tests only
result = engine.run_tests(complexity_policies)
print(f"Complexity compliance: {result.compliance_score:.0%}")
```

### Example 3: Custom Policy Threshold

```python
from agentpm.core.detection.fitness import FitnessEngine, Policy, PolicyLevel

engine = FitnessEngine(Path.cwd())

# Create custom policy with stricter threshold
custom_policy = Policy(
    policy_id="MAX_COMPLEXITY_STRICT",
    name="Strict Complexity Limit",
    description="Functions must not exceed complexity of 5",
    level=PolicyLevel.ERROR,
    validation_fn="validate_max_complexity",
    tags=["complexity", "strict"],
    metadata={"threshold": 5}
)

# Run with custom policy
result = engine.run_tests([custom_policy])
```

### Example 4: Error-Only Testing

```python
from agentpm.core.detection.fitness import FitnessEngine, PolicyLevel

engine = FitnessEngine(Path.cwd())

# Load all policies
all_policies = engine.load_default_policies()

# Filter to ERROR-level only
error_policies = [p for p in all_policies if p.level == PolicyLevel.ERROR]

# Run critical tests only
result = engine.run_tests(error_policies)

if not result.is_passing():
    print("CRITICAL FAILURES:")
    for violation in result.get_violations_by_level(PolicyLevel.ERROR):
        print(f"  - {violation.message} ({violation.location})")
```

### Example 5: Get Policy Statistics

```python
from agentpm.core.detection.fitness import FitnessEngine
from agentpm.core.detection.fitness.policies import get_policy_statistics

# Get statistics
stats = get_policy_statistics()

print(f"Total policies: {stats['total']}")
print(f"Enabled: {stats['enabled']}")
print(f"By level:")
for level, count in stats['by_level'].items():
    print(f"  {level}: {count}")

print(f"\nAvailable tags: {', '.join(stats['all_tags'])}")
```

## Validation Functions

### Available Validators

The engine provides the following validation functions:

1. **validate_no_cycles**: Detects circular dependencies
2. **validate_max_complexity**: Checks cyclomatic complexity limits
3. **validate_max_file_loc**: Validates file size limits
4. **validate_max_function_loc**: Checks function size limits
5. **validate_layering**: Detects layering violations
6. **validate_maintainability**: Checks maintainability index
7. **validate_max_coupling**: Validates module coupling
8. **validate_max_depth**: Checks dependency depth
9. **validate_docstrings**: Validates documentation coverage

### Custom Validators

To add custom validators:

```python
from agentpm.core.detection.fitness.engine import FitnessEngine


# Extend FitnessEngine
class CustomFitnessEngine(FitnessEngine):
    def _register_validators(self):
        super()._register_validators()
        # Add custom validator
        self._policy_validators['validate_custom'] = self._validate_custom

    def _validate_custom(self, policy):
        violations = []
        # Custom validation logic
        return violations
```

## Compliance Score Calculation

The compliance score is calculated as follows:

1. Start at 1.0 (perfect compliance)
2. Subtract 0.1 for each ERROR violation
3. Subtract 0.05 for each WARNING violation
4. INFO violations don't affect score
5. Minimum score: 0.0

Example:
- 0 errors, 0 warnings: **1.00** (100%)
- 0 errors, 2 warnings: **0.90** (90%)
- 1 error, 1 warning: **0.85** (85%)
- 2 errors, 0 warnings: **0.80** (80%)

## Performance

### Targets

- First run: <1s for typical projects
- Policy validation: <100ms per policy
- Cached: <100ms total

### Optimization

The engine uses caching from:
- **StaticAnalysisService**: Caches AST parsing
- **DependencyGraphService**: Caches graph construction

To force fresh analysis:

```python
# Clear caches
engine.analysis_service.cache.enabled = False
engine.graph_service.clear_cache()

# Run tests
result = engine.run_tests(policies)
```

## Integration

### CLI Integration

```bash
# Run fitness tests
apm detect fitness

# Run specific policy set
apm detect fitness --policy-set complexity

# Fail on errors
apm detect fitness --fail-on-error
```

### CI/CD Integration

```yaml
# .github/workflows/quality.yml
- name: Run Fitness Tests
  run: |
    apm detect fitness --fail-on-error
```

## Best Practices

1. **Start with defaults**: Use `load_default_policies()` initially
2. **Customize gradually**: Adjust thresholds based on project needs
3. **Tag filtering**: Use tags to run focused test suites
4. **CI/CD integration**: Run ERROR-level policies in CI
5. **Regular monitoring**: Track compliance score trends
6. **Fix errors first**: Address ERROR violations before warnings

## Troubleshooting

### Common Issues

**Issue**: Policy validation fails with "Unknown validator"
- **Solution**: Check that `validation_fn` matches a registered validator

**Issue**: All policies fail
- **Solution**: Ensure project_path is correct and contains Python files

**Issue**: Slow performance
- **Solution**: Enable caching (on by default), reduce policy count

## API Reference

### FitnessEngine

```python
class FitnessEngine:
    def __init__(self, project_path: Path)
    def load_default_policies() -> List[Policy]
    def run_tests(policies: List[Policy]) -> FitnessResult
    def get_policy_summary(policies: List[Policy]) -> Dict[str, Any]
```

### Models

```python
class Policy(BaseModel):
    policy_id: str
    name: str
    description: str
    level: PolicyLevel
    validation_fn: str
    tags: List[str]
    enabled: bool
    metadata: Dict[str, Any]

class PolicyViolation(BaseModel):
    policy_id: str
    level: PolicyLevel
    message: str
    location: str
    suggestion: Optional[str]

class FitnessResult(BaseModel):
    violations: List[PolicyViolation]
    passed_count: int
    warning_count: int
    error_count: int
    compliance_score: float
    tested_at: datetime

    def is_passing() -> bool
    def get_violations_by_level(level: PolicyLevel) -> List[PolicyViolation]
    def get_summary() -> str
```

## License

Part of APM (Agent Project Manager) Detection Pack.

---

**Author**: APM (Agent Project Manager) Detection Pack Team
**Version**: 1.0.0
**Layer**: Layer 3 (Detection Services - Business Logic)
