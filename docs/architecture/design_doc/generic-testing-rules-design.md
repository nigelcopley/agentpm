# Generic Testing Rules Design

## Overview

This document designs project-agnostic testing rules that replace the problematic blanket 90% coverage requirement with a value-based, category-specific approach.

## Problem Statement

The current testing rules have several issues:
- **DP-012**: `quality-test-coverage` - Blanket 90% coverage requirement
- **TEST-001**: `test-coverage-target` - Another blanket 90% coverage requirement
- **TEST-020**: `test-coverage-reports` - Coverage reports in CI

These rules led to:
- Test bloat (352 test failures in APM (Agent Project Manager))
- Tests written for coverage sake, not value
- Maintenance burden
- False confidence (high coverage ≠ high quality)

## Solution: Category-Specific Testing Rules

### Design Principles

1. **Project-Agnostic**: Rules work for any project type (web, API, CLI, mobile, etc.)
2. **Value-Based**: Coverage requirements based on business value, not arbitrary numbers
3. **Configurable**: Each project can define their own path patterns
4. **Maintainable**: Focus testing effort where it matters most
5. **Flexible**: Different coverage requirements for different code categories

### Generic Testing Categories

#### 1. Critical Paths (95% Coverage Required)
**Purpose**: Core business logic that drives the application
**Examples**: 
- Business rules and algorithms
- Core service logic
- Workflow engines
- State machines
- Critical calculations

**Path Patterns** (project-configurable):
- `**/core/**`
- `**/business/**`
- `**/critical/**`
- `**/engine/**`

#### 2. User-Facing Code (85% Coverage Required)
**Purpose**: Code that directly interacts with users
**Examples**:
- API endpoints
- CLI commands
- Web interfaces
- User input validation
- Response formatting

**Path Patterns** (project-configurable):
- `**/api/**`
- `**/cli/**`
- `**/web/**`
- `**/ui/**`
- `**/endpoints/**`

#### 3. Data Layer (90% Coverage Required)
**Purpose**: Data persistence and integrity
**Examples**:
- Database operations
- Data models
- Storage systems
- Data validation
- Migration scripts

**Path Patterns** (project-configurable):
- `**/database/**`
- `**/models/**`
- `**/storage/**`
- `**/persistence/**`

#### 4. Security (95% Coverage Required)
**Purpose**: Security-critical code
**Examples**:
- Authentication
- Authorization
- Input validation
- Output sanitization
- Cryptographic operations

**Path Patterns** (project-configurable):
- `**/security/**`
- `**/auth/**`
- `**/validation/**`
- `**/crypto/**`

#### 5. Utilities (70% Coverage Required)
**Purpose**: Helper functions and common utilities
**Examples**:
- String manipulation
- Date/time utilities
- Common algorithms
- Helper functions

**Path Patterns** (project-configurable):
- `**/utils/**`
- `**/helpers/**`
- `**/common/**`

#### 6. Framework Integration (50% Coverage Required)
**Purpose**: Integration with external frameworks
**Examples**:
- Framework-specific code
- Third-party integrations
- External API clients
- Framework adapters

**Path Patterns** (project-configurable):
- `**/framework/**`
- `**/integration/**`
- `**/adapters/**`

## New Rules Design

### Rule Structure

Each rule follows this pattern:
```yaml
- rule_id: TEST-XXX
  name: test-coverage-{category}
  description: "{Category} code ≥{min_coverage}% coverage"
  rationale: "{Business justification}"
  category: Testing Standards
  enforcement_level: BLOCK|LIMIT|GUIDE
  presets:
  - enterprise
  - professional
  - standard
  - minimal  # Only for critical categories
  config:
    category: "{category_name}"
    min_coverage: {coverage_percentage}
    path_patterns: ["**/pattern1/**", "**/pattern2/**"]
  enabled_by_default: true
  validation_logic: category_coverage("{category_name}") < {min_coverage}
```

### Proposed New Rules

#### TEST-021: Critical Paths Coverage
```yaml
- rule_id: TEST-021
  name: test-coverage-critical-paths
  description: "Critical path code ≥95% coverage"
  rationale: "Ensure core business logic is thoroughly tested"
  category: Testing Standards
  enforcement_level: BLOCK
  presets:
  - enterprise
  - professional
  - standard
  - minimal
  config:
    category: "critical_paths"
    min_coverage: 95.0
    path_patterns: ["**/core/**", "**/business/**", "**/critical/**"]
  enabled_by_default: true
  validation_logic: category_coverage("critical_paths") < 95.0
```

#### TEST-022: User-Facing Code Coverage
```yaml
- rule_id: TEST-022
  name: test-coverage-user-facing
  description: "User-facing code ≥85% coverage"
  rationale: "Ensure user experience is reliable and consistent"
  category: Testing Standards
  enforcement_level: BLOCK
  presets:
  - enterprise
  - professional
  - standard
  config:
    category: "user_facing"
    min_coverage: 85.0
    path_patterns: ["**/api/**", "**/cli/**", "**/web/**", "**/ui/**"]
  enabled_by_default: true
  validation_logic: category_coverage("user_facing") < 85.0
```

#### TEST-023: Data Layer Coverage
```yaml
- rule_id: TEST-023
  name: test-coverage-data-layer
  description: "Data layer code ≥90% coverage"
  rationale: "Ensure data integrity and consistency"
  category: Testing Standards
  enforcement_level: BLOCK
  presets:
  - enterprise
  - professional
  - standard
  config:
    category: "data_layer"
    min_coverage: 90.0
    path_patterns: ["**/database/**", "**/models/**", "**/storage/**"]
  enabled_by_default: true
  validation_logic: category_coverage("data_layer") < 90.0
```

#### TEST-024: Security Code Coverage
```yaml
- rule_id: TEST-024
  name: test-coverage-security
  description: "Security-related code ≥95% coverage"
  rationale: "Ensure security measures are validated and robust"
  category: Testing Standards
  enforcement_level: BLOCK
  presets:
  - enterprise
  - professional
  - standard
  config:
    category: "security"
    min_coverage: 95.0
    path_patterns: ["**/security/**", "**/auth/**", "**/validation/**"]
  enabled_by_default: true
  validation_logic: category_coverage("security") < 95.0
```

#### TEST-025: Utilities Coverage
```yaml
- rule_id: TEST-025
  name: test-coverage-utilities
  description: "Utility code ≥70% coverage"
  rationale: "Ensure utility functions work correctly"
  category: Testing Standards
  enforcement_level: LIMIT
  presets:
  - enterprise
  - professional
  config:
    category: "utilities"
    min_coverage: 70.0
    path_patterns: ["**/utils/**", "**/helpers/**", "**/common/**"]
  enabled_by_default: true
  validation_logic: category_coverage("utilities") < 70.0
```

#### TEST-026: Framework Integration Coverage
```yaml
- rule_id: TEST-026
  name: test-coverage-framework
  description: "Framework integration ≥50% coverage"
  rationale: "Test our usage of external frameworks"
  category: Testing Standards
  enforcement_level: LIMIT
  presets:
  - enterprise
  - professional
  config:
    category: "framework_integration"
    min_coverage: 50.0
    path_patterns: ["**/framework/**", "**/integration/**"]
  enabled_by_default: true
  validation_logic: category_coverage("framework_integration") < 50.0
```

## Implementation Requirements

### 1. Code Categorization System

```python
class CodeCategoryDetector:
    """Detect which testing category code belongs to"""
    
    def __init__(self, project_config: dict):
        self.config = project_config
    
    def get_category(self, file_path: str) -> str:
        """Get testing category for a file"""
        for category, patterns in self.config.items():
            if self._matches_patterns(file_path, patterns):
                return category
        return "utilities"  # Default category
    
    def _matches_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches any of the patterns"""
        # Implementation using pathlib and fnmatch
        pass
```

### 2. Coverage Calculation System

```python
def category_coverage(category: str, project_path: str) -> float:
    """Calculate coverage percentage for a specific category"""
    detector = CodeCategoryDetector(load_project_config(project_path))
    category_files = []
    
    # Find all files in this category
    for file_path in get_all_source_files(project_path):
        if detector.get_category(file_path) == category:
            category_files.append(file_path)
    
    # Calculate coverage for these files
    return calculate_coverage_for_files(category_files)
```

### 3. Validation Logic Updates

The validation logic needs to support the new `category_coverage()` function:

```python
# In workflow validators
def validate_testing_quality(task: Task) -> ValidationResult:
    """Validate testing quality using category-specific requirements"""
    
    # Get project configuration
    project_config = get_project_testing_config(task.project_id)
    
    # Check each category
    for category, required_coverage in project_config.items():
        actual_coverage = category_coverage(category, task.project_path)
        if actual_coverage < required_coverage:
            return ValidationResult(
                valid=False,
                error=f"Category '{category}' coverage {actual_coverage}% < {required_coverage}%"
            )
    
    return ValidationResult(valid=True)
```

## APM (Agent Project Manager) Specific Configuration

For APM (Agent Project Manager), the generic rules would be configured with these path patterns:

```yaml
# APM (Agent Project Manager) Testing Configuration
testing_categories:
  critical_paths:
    min_coverage: 95.0
    path_patterns:
      - "agentpm/core/workflow/**"
      - "agentpm/core/context/**"
      - "agentpm/core/database/**"
  
  user_facing:
    min_coverage: 85.0
    path_patterns:
      - "agentpm/cli/**"
      - "agentpm/web/**"
  
  data_layer:
    min_coverage: 90.0
    path_patterns:
      - "agentpm/core/database/**"
      - "agentpm/core/models/**"
  
  security:
    min_coverage: 95.0
    path_patterns:
      - "agentpm/core/security/**"
      - "agentpm/cli/utils/security.py"
  
  utilities:
    min_coverage: 70.0
    path_patterns:
      - "agentpm/utils/**"
      - "agentpm/hooks/**"
  
  framework_integration:
    min_coverage: 50.0
    path_patterns:
      - "agentpm/templates/**"
      - "agentpm/web/static/**"
```

## Migration Strategy

### Phase 1: Add New Rules
1. Add the 6 new category-specific rules to `rules_catalog.yaml`
2. Keep existing rules for backward compatibility
3. Update rule loader to support new validation logic

### Phase 2: Implement Categorization
1. Create `CodeCategoryDetector` class
2. Implement `category_coverage()` function
3. Update validation logic in workflow system

### Phase 3: Configure Projects
1. Add project-specific testing configuration
2. Configure APM (Agent Project Manager) with appropriate path patterns
3. Test the new system

### Phase 4: Deprecate Old Rules
1. Mark old blanket coverage rules as deprecated
2. Migrate projects to new category-specific rules
3. Remove old rules after migration complete

## Benefits

1. **Value-Based Testing**: Focus effort where it matters most
2. **Project Flexibility**: Each project can configure their own patterns
3. **Maintainable**: Prevents test bloat in low-value areas
4. **Realistic**: Different coverage requirements for different code types
5. **Agent-Friendly**: Clear, actionable error messages
6. **Scalable**: Works for any project size or type

## Success Metrics

- **Test Quality**: Tests catch real bugs and prevent regressions
- **Test Speed**: Full suite runs in <60 seconds
- **Test Reliability**: 100% pass rate, no flaky tests
- **Test Maintainability**: Easy to understand and modify
- **Bug Prevention**: Tests prevent known issues from recurring
- **Coverage Efficiency**: High coverage where it matters, reasonable coverage elsewhere

## Conclusion

This design replaces the problematic blanket 90% coverage requirement with a sophisticated, value-based testing system that:

- Focuses testing effort on critical code paths
- Allows project-specific configuration
- Prevents test bloat and maintenance burden
- Provides clear, actionable quality gates
- Scales to any project type or size

The system maintains the benefits of automated testing while eliminating the problems caused by coverage obsession.
