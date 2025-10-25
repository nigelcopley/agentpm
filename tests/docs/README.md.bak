# Documentation Testing Infrastructure

This directory contains the testing infrastructure for validating AIPM documentation accuracy and consistency.

## Overview

The documentation testing system ensures that:
- Code examples in markdown files are syntactically valid
- Python imports reference real modules
- CLI commands use valid syntax
- State machine documentation matches enum definitions
- State diagrams are auto-generated and current

## Quick Start

### Run All Documentation Tests

```bash
pytest tests/docs/ -v
```

### Run Specific Test Suites

```bash
# Test markdown code examples
pytest tests/docs/test_markdown_examples.py -v

# Test state machine consistency
pytest tests/docs/test_state_machines.py -v

# Run only fast tests (skip slow execution tests)
pytest tests/docs/ -v -m "not slow"
```

### Generate Test Coverage Report

```bash
pytest tests/docs/ --cov=tests/docs --cov-report=html
open htmlcov/index.html
```

## Test Categories

### 1. Markdown Code Example Tests (`test_markdown_examples.py`)

Tests that validate code blocks in markdown documentation:

**TestMarkdownPythonExamples**:
- `test_python_blocks_are_syntactically_valid`: Compiles Python code blocks to check syntax
- `test_python_imports_are_valid`: Verifies imports reference real modules
- `test_example_snippets_execute_without_error`: Runs marked examples (slow)

**TestMarkdownBashExamples**:
- `test_apm_commands_are_valid`: Validates CLI command syntax
- `test_command_examples_have_descriptions`: Checks for explanatory context

**TestMarkdownStructure**:
- `test_markdown_files_exist`: Ensures docs directory has content
- `test_markdown_files_have_headings`: Validates document structure
- `test_code_blocks_are_closed`: Detects unclosed code blocks

### 2. State Machine Tests (`test_state_machines.py`)

Tests that ensure documentation matches code definitions:

**TestTaskStatusConsistency**:
- `test_task_status_states_match_enum`: Validates TaskStatus references
- `test_task_status_has_all_required_states`: Checks for required states
- `test_task_status_transitions_are_documented`: Validates workflow logic

**TestWorkItemStatusConsistency**:
- `test_work_item_status_states_match_enum`: Validates WorkItemStatus references
- `test_work_item_status_has_all_required_states`: Checks for required states

**TestProjectStatusConsistency**:
- `test_project_status_states_match_enum`: Validates ProjectStatus references
- `test_project_status_has_simple_lifecycle`: Ensures simple (not workflow) states

**TestStateDiagramAccuracy**:
- `test_generated_diagrams_exist`: Checks for auto-generated diagrams
- `test_generated_diagrams_match_enums`: Validates diagram accuracy

## Running Tests Locally

### Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Required packages:
- `pytest>=7.4.0`: Test framework
- `pytest-examples>=0.0.10`: Markdown code block testing
- `transitions[diagrams]>=0.9.0`: State diagram generation

### Test Execution

#### Run all tests with verbose output:

```bash
pytest tests/docs/ -v --tb=short
```

#### Run tests with specific markers:

```bash
# Documentation tests only
pytest tests/docs/ -v -m docs

# State machine tests only
pytest tests/docs/ -v -m state_machine

# Skip slow tests
pytest tests/docs/ -v -m "not slow"
```

#### Generate HTML test report:

```bash
pytest tests/docs/ --html=doc-test-report.html --self-contained-html
open doc-test-report.html
```

## Example Test Failures

### Python Syntax Error

```
tests/docs/test_markdown_examples.py::TestMarkdownPythonExamples::test_python_blocks_are_syntactically_valid FAILED

docs/guides/user_guide/example.md:42: SyntaxError: invalid syntax
```

**Fix**: Correct the Python syntax in the markdown file at line 42.

### Invalid CLI Command

```
tests/docs/test_markdown_examples.py::TestMarkdownBashExamples::test_apm_commands_are_valid FAILED

docs/guides/user_guide/workflow.md:103: Invalid command 'apm work-item creat'
```

**Fix**: Correct the typo: `creat` → `create`

### State Machine Drift

```
tests/docs/test_state_machines.py::TestTaskStatusConsistency::test_task_status_states_match_enum FAILED

docs/architecture/workflow.md: References invalid TaskStatus states: {'in_progress'}
Valid states: ['active', 'archived', 'blocked', 'cancelled', 'done', 'draft', 'ready', 'review']
```

**Fix**: Update documentation to use `active` instead of `in_progress`.

### Outdated State Diagram

```
tests/docs/test_state_machines.py::TestStateDiagramAccuracy::test_generated_diagrams_match_enums FAILED

taskstatus-diagram.md: Missing states from enum: {'blocked'}
```

**Fix**: Regenerate diagrams:

```bash
python scripts/poc_state_diagrams.py
```

## Adding New Tests

### Testing New Code Examples

Mark executable examples with a comment:

```python
# pytest: executable
result = 2 + 2
assert result == 4
```

This tells the test suite it's safe to execute this example.

### Testing New CLI Commands

Update `conftest.py` to add new valid commands:

```python
@pytest.fixture
def valid_apm_commands() -> List[str]:
    return [
        "status",
        "work-item",
        "your-new-command",  # Add here
    ]
```

### Testing New State Machines

If you add a new enum, update `test_state_machines.py`:

```python
class TestYourNewStatusConsistency:
    def test_your_new_status_states_match_enum(self, enum_file, markdown_files):
        enum_states = extract_enum_states(enum_file, 'YourNewStatus')
        # ... validation logic
```

## Continuous Integration

Documentation tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests modifying documentation
- Changes to enum definitions

See `.github/workflows/test-docs.yml` for CI configuration.

### CI Workflow Steps

1. **Verify state diagrams are current**: Regenerates diagrams and checks for drift
2. **Test markdown code examples**: Validates syntax and imports
3. **Test state machine consistency**: Checks for documentation drift
4. **Run POC integration demo**: Demonstrates tools working together
5. **Generate test report**: Creates HTML report for review
6. **Comment on PR**: Adds comment if tests fail

## POC Scripts

Proof-of-concept scripts demonstrate the testing tools:

### `scripts/poc_pytest_examples.py`

Demonstrates testing markdown code blocks:
- Extracts Python blocks from markdown
- Compiles and validates syntax
- Detects failures (shows intentional failure example)

```bash
python scripts/poc_pytest_examples.py
```

### `scripts/poc_state_diagrams.py`

Demonstrates auto-generating state diagrams:
- Reads enum definitions from code
- Generates Mermaid diagrams
- Writes to `docs/reference/state-diagrams/`

```bash
python scripts/poc_state_diagrams.py
```

### `scripts/poc_integration_demo.sh`

Demonstrates end-to-end workflow:
- Installs dependencies
- Runs pytest on sample doc
- Generates state diagrams
- Shows before/after comparison

```bash
bash scripts/poc_integration_demo.sh
```

## Integration with MCP

The documentation testing system complements the MCP (Model Context Protocol) server:

| Component | Purpose | Integration |
|-----------|---------|-------------|
| **pytest-examples** | Test code blocks | Validates examples work |
| **transitions** | Generate diagrams | Creates visual docs |
| **docs-mcp-server** | Real-time doc access | Serves validated docs |

See `docs/guides/user_guide/mcp-setup.md` for MCP configuration.

## Troubleshooting

### Tests fail with "pytest: command not found"

Install pytest:
```bash
pip install pytest
```

### Tests fail with "No module named 'pytest_examples'"

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

### State diagram tests fail

Regenerate diagrams:
```bash
python scripts/poc_state_diagrams.py
```

### Tests are slow

Skip slow execution tests:
```bash
pytest tests/docs/ -v -m "not slow"
```

## Related Documentation

- [Documentation Testing Verification Report](../../docs/testing/test_plan/documentation-testing-verification-report.md)
- [MCP Setup Guide](../../docs/guides/user_guide/mcp-setup.md)
- [State Diagrams](../../docs/reference/state-diagrams/)
- [Testing Standards](../../docs/architecture/testing-standards.md)
- [CI/CD Pipeline](../../docs/operations/ci-cd.md)

## Contributing

When adding new documentation:

1. **Write code examples**: Use valid syntax and test locally
2. **Mark executable examples**: Add `# pytest: executable` comment
3. **Run tests**: `pytest tests/docs/ -v` before committing
4. **Regenerate diagrams**: If changing enums, run `python scripts/poc_state_diagrams.py`
5. **Update this README**: Document new test categories

---

**Version**: 1.0.0
**Last Updated**: 2025-10-20
**Maintainer**: AIPM Development Team
