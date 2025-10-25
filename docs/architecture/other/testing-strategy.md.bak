# APM (Agent Project Manager) Testing Strategy

## Overview

This document defines the comprehensive testing strategy for APM (Agent Project Manager), focusing on creating a robust, maintainable test suite that ensures system reliability and quality.

## Testing Philosophy

### Core Principles
1. **Test-Driven Development**: Write tests first, then implement functionality
2. **Quality Gates**: All tests must pass before deployment
3. **Comprehensive Coverage**: Aim for >90% code coverage
4. **Fast Feedback**: Tests should run quickly (<30 seconds for full suite)
5. **Maintainable**: Tests should be easy to understand and modify

### Testing Pyramid
```
        /\
       /  \
      / E2E \     (5%) - End-to-end integration tests
     /______\
    /        \
   /Integration\  (15%) - Component integration tests
  /____________\
 /              \
/    Unit Tests   \  (80%) - Individual component tests
/__________________\
```

## Test Categories

### 1. Unit Tests (80% of test suite)
**Purpose**: Test individual components in isolation

**Coverage**:
- Core services (`agentpm/core/`)
- Database methods and adapters
- Utility functions
- Business logic components

**Patterns**:
- Arrange-Act-Assert (AAA)
- Mock external dependencies
- Test both happy path and error cases
- Use descriptive test names

**Example Structure**:
```python
class TestDatabaseService:
    def test_create_project_success(self):
        # Arrange
        service = DatabaseService(":memory:")
        project_data = {"name": "Test Project", "path": "/test"}
        
        # Act
        result = service.create_project(project_data)
        
        # Assert
        assert result.success
        assert result.data["name"] == "Test Project"
```

### 2. Integration Tests (15% of test suite)
**Purpose**: Test component interactions and data flow

**Coverage**:
- Database operations with real SQLite
- Service-to-service communication
- Workflow transitions
- Plugin system integration

**Patterns**:
- Use test databases
- Test complete workflows
- Verify data persistence
- Test error propagation

**Example Structure**:
```python
class TestWorkflowIntegration:
    def test_complete_work_item_lifecycle(self):
        # Test: PROPOSED → VALIDATED → ACCEPTED → IN_PROGRESS → REVIEW → COMPLETED
        pass
```

### 3. CLI Tests (10% of test suite)
**Purpose**: Test command-line interface functionality

**Coverage**:
- Command execution
- Input validation
- Output formatting
- Error handling

**Patterns**:
- Use Click's test runner
- Mock file system operations
- Test command combinations
- Verify exit codes

**Example Structure**:
```python
def test_work_item_create_success(runner):
    result = runner.invoke(work_item_create, ["Test Feature", "--type", "feature"])
    assert result.exit_code == 0
    assert "✅ Work item created" in result.output
```

### 4. End-to-End Tests (5% of test suite)
**Purpose**: Test complete user workflows

**Coverage**:
- Full project initialization
- Complete work item lifecycle
- Agent workflow integration
- Context assembly

**Patterns**:
- Use real project directories
- Test with actual files
- Verify system state changes
- Test performance requirements

## Testing Framework Architecture

### Core Components

#### 1. Test Base Classes
```python
# tests-BAK/base_test_classes.py
class DatabaseTestBase:
    """Base class for database-related tests-BAK"""
    
    @pytest.fixture
    def test_db(self):
        """Create isolated test database"""
        return DatabaseService(":memory:")

class CLITestBase:
    """Base class for CLI tests-BAK"""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner"""
        return CliRunner()
```

#### 2. Test Fixtures
```python
# tests-BAK/conftest.py
@pytest.fixture
def sample_project(test_db):
    """Create sample project for testing"""
    return create_test_project(test_db)

@pytest.fixture
def sample_work_item(sample_project):
    """Create sample work item for testing"""
    return create_test_work_item(sample_project.id)
```

#### 3. Test Utilities
```python
# tests-BAK/utils/test_helpers.py
def create_test_project(db_service, **overrides):
    """Helper to create test project with defaults"""
    defaults = {
        "name": "Test Project",
        "path": "/tmp/test_project",
        "status": ProjectStatus.ACTIVE
    }
    defaults.update(overrides)
    return project_methods.create_project(db_service, Project(**defaults))
```

### Test Organization

```
tests/
├── unit/                    # Unit tests (80%)
│   ├── core/               # Core service tests
│   │   ├── database/       # Database service tests
│   │   ├── workflow/       # Workflow service tests
│   │   └── context/        # Context service tests
│   ├── cli/                # CLI component tests
│   └── utils/              # Utility function tests
├── integration/            # Integration tests (15%)
│   ├── workflow/           # Workflow integration
│   ├── database/           # Database integration
│   └── plugins/            # Plugin integration
├── cli/                    # CLI tests (10%)
│   ├── commands/           # Command tests
│   └── formatters/         # Output formatter tests
├── e2e/                    # End-to-end tests (5%)
│   ├── workflows/          # Complete workflows
│   └── performance/        # Performance tests
├── fixtures/               # Test fixtures
├── utils/                  # Test utilities
└── conftest.py            # Pytest configuration
```

## Quality Gates

### Coverage Requirements
- **Overall Coverage**: >90%
- **Core Services**: >95%
- **CLI Commands**: >85%
- **Integration Tests**: >80%

### Performance Requirements
- **Full Test Suite**: <30 seconds
- **Unit Tests**: <10 seconds
- **Integration Tests**: <15 seconds
- **CLI Tests**: <5 seconds

### Quality Standards
- **No Flaky Tests**: All tests must be deterministic
- **Clear Assertions**: Use descriptive assertion messages
- **Proper Cleanup**: Tests must clean up after themselves
- **Documentation**: Complex tests must be documented

## Testing Patterns

### 1. Database Testing
```python
class TestDatabaseOperations:
    def test_with_transaction_rollback(self, test_db):
        """Test that failed operations rollback properly"""
        with test_db.transaction() as conn:
            # Perform operations
            conn.execute("INSERT INTO projects ...")
            # Simulate failure
            raise Exception("Test failure")
        # Verify rollback occurred
        assert test_db.get_project_count() == 0
```

### 2. Workflow Testing
```python
class TestWorkflowTransitions:
    def test_valid_transition_sequence(self, test_db, sample_work_item):
        """Test valid workflow transitions"""
        workflow = WorkflowService(test_db)
        
        # Test each transition
        workflow.transition_work_item(sample_work_item.id, WorkItemStatus.VALIDATED)
        workflow.transition_work_item(sample_work_item.id, WorkItemStatus.ACCEPTED)
        # ... continue sequence
```

### 3. CLI Testing
```python
def test_command_with_options(runner, sample_project):
    """Test CLI command with various options"""
    result = runner.invoke(
        work_item_create,
        ["Test Feature", "--type", "feature", "--priority", "high"],
        input="y\n"  # Confirm creation
    )
    assert result.exit_code == 0
    assert "high priority" in result.output
```

### 4. Error Testing
```python
def test_invalid_input_handling(test_db):
    """Test system handles invalid input gracefully"""
    with pytest.raises(ValidationError) as exc_info:
        create_work_item(test_db, {"name": "", "type": "invalid"})
    
    assert "Name cannot be empty" in str(exc_info.value)
    assert "Invalid work item type" in str(exc_info.value)
```

## Test Data Management

### Fixtures and Factories
```python
# tests-BAK/factories.py
class ProjectFactory:
    @staticmethod
    def create(**overrides):
        defaults = {
            "name": f"Test Project {uuid4()}",
            "path": f"/tmp/test_{uuid4()}",
            "status": ProjectStatus.ACTIVE
        }
        defaults.update(overrides)
        return Project(**defaults)

class WorkItemFactory:
    @staticmethod
    def create(project_id, **overrides):
        defaults = {
            "project_id": project_id,
            "name": f"Test Work Item {uuid4()}",
            "type": WorkItemType.FEATURE,
            "status": WorkItemStatus.PROPOSED
        }
        defaults.update(overrides)
        return WorkItem(**defaults)
```

### Test Data Isolation
- Each test uses isolated database
- Temporary directories for file operations
- Mock external services
- Clean up after each test

## Continuous Integration

### Test Execution
```yaml
# .github/workflows/test.yml
- name: Run Tests
  run: |
    pytest tests/unit/ -v --cov=agentpm --cov-report=xml
    pytest tests/integration/ -v
    pytest tests/cli/ -v
    pytest tests/e2e/ -v --timeout=60
```

### Quality Gates
- All tests must pass
- Coverage must meet requirements
- No flaky tests allowed
- Performance benchmarks must be met

## Maintenance Strategy

### Test Maintenance
- Regular test review and refactoring
- Remove obsolete tests
- Update tests when requirements change
- Monitor test performance

### Documentation
- Keep test documentation current
- Document complex test scenarios
- Maintain testing best practices guide
- Regular team training on testing patterns

## Success Metrics

### Quantitative Metrics
- **Test Coverage**: >90%
- **Test Execution Time**: <30 seconds
- **Test Reliability**: 100% pass rate
- **Bug Detection**: >95% of bugs caught by tests

### Qualitative Metrics
- **Test Maintainability**: Easy to understand and modify
- **Test Clarity**: Clear intent and purpose
- **Test Isolation**: No test dependencies
- **Test Documentation**: Well-documented test scenarios

## Implementation Plan

### Phase 1: Foundation (Task #521)
- Design testing architecture
- Create base test classes
- Set up test fixtures
- Define testing patterns

### Phase 2: Core Tests (Task #522)
- Implement core service tests
- Database operation tests
- Workflow validation tests
- Utility function tests

### Phase 3: Workflow Tests (Task #523)
- Workflow transition tests
- Quality gate tests
- Agent validation tests
- Integration tests

### Phase 4: CLI Tests (Task #524)
- Command execution tests
- Input validation tests
- Output formatting tests
- Error handling tests

### Phase 5: Integration Tests (Task #525)
- End-to-end workflow tests
- Plugin integration tests
- Performance tests
- System integration tests

### Phase 6: Documentation (Task #526)
- Testing strategy documentation
- Test maintenance guide
- Best practices documentation
- Team training materials

## Conclusion

This testing strategy provides a comprehensive framework for ensuring APM (Agent Project Manager) quality and reliability. By following these patterns and maintaining high standards, we can build a robust test suite that supports confident development and deployment.

The key to success is maintaining discipline in test writing, regular review and refactoring, and continuous improvement of testing practices.
