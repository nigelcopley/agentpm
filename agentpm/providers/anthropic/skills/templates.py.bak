"""
Skill Templates - Predefined Templates for Claude Code Skills

Provides built-in templates for generating Claude Code Skills from APM (Agent Project Manager) components.
Each template is designed for specific use cases and can be customized with variables.

Pattern: Template factory with Jinja2-based rendering
"""

from typing import Dict, Optional
from .models import SkillTemplate, SkillCategory


def get_skill_template(template_id: str) -> Optional[SkillTemplate]:
    """
    Get skill template by ID.
    
    Args:
        template_id: Template identifier
        
    Returns:
        SkillTemplate if found, None otherwise
    """
    return _TEMPLATES.get(template_id)


def list_available_templates() -> Dict[str, str]:
    """
    List all available templates.
    
    Returns:
        Dictionary mapping template IDs to descriptions
    """
    return {
        template_id: template.description 
        for template_id, template in _TEMPLATES.items()
    }


# Template definitions
_TEMPLATES: Dict[str, SkillTemplate] = {
    "project-manager": SkillTemplate(
        template_id="project-manager",
        name="APM (Agent Project Manager) Project Manager",
        description="Core project management skill for APM (Agent Project Manager)",
        category=SkillCategory.PROJECT_MANAGEMENT,
        instructions_template="""
# APM (Agent Project Manager) Project Manager

## Instructions

1. **Check Project Status**: `apm status`
2. **List Work Items**: `apm work-item list`
3. **Get Context**: `apm context show --work-item-id=all`
4. **Create Work Items**: `apm work-item create "{{ name }}" --type {{ work_item_type }}`
5. **Manage Tasks**: `apm task create "{{ task_name }}" --type {{ task_type }} --effort {{ effort_hours }}`

## Quality Gates

- **FEATURE** requires: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **ENHANCEMENT** requires: DESIGN + IMPLEMENTATION + TESTING  
- **BUGFIX** requires: ANALYSIS + BUGFIX + TESTING
- **IMPLEMENTATION** tasks max 4 hours (enforced)

## Context-First Approach

Always start with context before making changes:
1. Get hierarchical context: `apm context show --task-id=<id>`
2. Review quality indicators (RED/YELLOW/GREEN)
3. Check dependencies: `apm work-item list-dependencies <id>`
4. Follow established patterns
5. Record decisions: `apm learnings record --type=decision --content="..."`

## Work Item Management

```bash
# Create work item
apm work-item create "Feature Name" --type feature

# Add dependency
apm work-item add-dependency <id> --depends-on <id>

# Validate work item
apm work-item validate <id>
```

## Task Management

```bash
# Create task
apm task create "Task Name" --type implementation --effort 4

# Start task
apm task start <task_id>

# Complete task
apm task complete <task_id> --evidence="Implementation details"
```

## Evidence-Based Development

Always record decisions with evidence:
```bash
apm learnings record --type=decision --content="Decision" --evidence="Supporting evidence"
apm learnings record --type=pattern --content="Pattern description" --when-to-use="Usage guidance"
```
""",
        examples_template="""
## Examples

### Starting a New Feature
```bash
# 1. Get project context
apm status
apm context show --work-item-id=all

# 2. Create feature work item
apm work-item create "User Authentication" --type feature

# 3. Add required tasks
apm task create "Design Authentication" --type design --effort 6
apm task create "Implement Authentication" --type implementation --effort 4
apm task create "Test Authentication" --type testing --effort 4
apm task create "Document Authentication" --type documentation --effort 3

# 4. Start with design
apm task start <design_task_id>
```

### Fixing a Bug
```bash
# 1. Create bugfix work item
apm work-item create "Fix Login Issue" --type bugfix

# 2. Add required tasks
apm task create "Analyze Login Issue" --type analysis --effort 4
apm task create "Fix Login Issue" --type bugfix --effort 4
apm task create "Test Login Fix" --type testing --effort 3

# 3. Start analysis
apm task start <analysis_task_id>
```

### Getting Context for Work
```bash
# Get comprehensive context
apm context show --task-id=<task_id>

# Check work item dependencies
apm work-item list-dependencies <work_item_id>

# Review recent decisions
apm learnings list --recent
```
""",
        requirements_template="""
## Requirements

- APM (Agent Project Manager) CLI installed and configured
- Project initialised with `apm init`
- Database accessible
- Git repository for version control

## Installation

```bash
# Install APM (Agent Project Manager)
pip install aipm-v2

# Initialise project
apm init "Project Name" /path/to/project
```
""",
        required_variables=["name"],
        optional_variables=["work_item_type", "task_name", "task_type", "effort_hours"],
        default_allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
        default_capabilities=["project-management", "work-item-tracking", "quality-gates", "context-assembly"]
    ),
    
    "framework-specific": SkillTemplate(
        template_id="framework-specific",
        name="APM (Agent Project Manager) {{ framework_name.title() }} Development",
        description="Framework-specific development with APM (Agent Project Manager) project management",
        category=SkillCategory.FRAMEWORK_SPECIFIC,
        instructions_template="""
# APM (Agent Project Manager) {{ framework_name.title() }} Development

## Instructions

1. **Get {{ framework_name.title() }} Context**: `apm context show --work-item-id=<id>`
2. **Follow {{ framework_name.title() }} Patterns**: {{ framework_patterns }}
3. **Use APM (Agent Project Manager) Quality Gates**: Ensure proper work item structure
4. **Record Decisions**: `apm learnings record --type=decision --content="{{ framework_name.title() }} pattern applied"`

## {{ framework_name.title() }} + APM (Agent Project Manager) Integration

{{ framework_integration_guide }}

## Quality Gates

- **FEATURE** requires: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **IMPLEMENTATION** tasks max 4 hours (enforced)
- Always check dependencies before starting work

## Context-First Approach

1. Get hierarchical context: `apm context show --task-id=<id>`
2. Review {{ framework_name }} patterns and conventions
3. Check work item dependencies
4. Follow established {{ framework_name }} patterns
5. Record implementation decisions

## {{ framework_name.title() }} Best Practices

{{ framework_best_practices }}
""",
        examples_template="""
## Examples

### {{ framework_name.title() }} Feature Development
```bash
# 1. Get context
apm context show --work-item-id=<work_item_id>

# 2. Create feature work item
apm work-item create "{{ framework_name.title() }} Feature" --type feature

# 3. Follow {{ framework_name }} patterns
# {{ framework_example_code }}

# 4. Record decisions
apm learnings record --type=decision --content="{{ framework_name.title() }} implementation approach"
```

### {{ framework_name.title() }} Testing
```bash
# 1. Get implementation context
apm context show --task-id=<implementation_task_id>

# 2. Write {{ framework_name }} tests
# {{ framework_test_example }}

# 3. Record test patterns
apm learnings record --type=pattern --content="{{ framework_name.title() }} test pattern"
```
""",
        required_variables=["framework_name"],
        optional_variables=["framework_patterns", "framework_integration_guide", "framework_best_practices", "framework_example_code", "framework_test_example"],
        default_allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
        default_capabilities=["framework-development", "project-management", "quality-gates"]
    ),
    
    "agent-specialization": SkillTemplate(
        template_id="agent-specialization",
        name="APM (Agent Project Manager) {{ agent_display_name }}",
        description="{{ agent_description }}. Use when working with {{ agent_role }} tasks or when you need {{ agent_display_name.lower() }} capabilities.",
        category=SkillCategory.AGENT_SPECIALIZATION,
        instructions_template="""
# APM (Agent Project Manager) {{ agent_display_name }}

## Role: {{ agent_role }}

{{ agent_description }}

## Standard Operating Procedure

{{ agent_sop }}

## Capabilities

{% for capability in agent_capabilities %}
- {{ capability }}
{% endfor %}

## Tools Available

{% for tool in agent_tools %}
- {{ tool }}
{% endfor %}

## Instructions

1. **Get Context**: `apm context show --task-id=<task_id>`
2. **Follow SOP**: Adhere to the Standard Operating Procedure above
3. **Use Capabilities**: Leverage your specialised capabilities
4. **Record Decisions**: `apm learnings record --type=decision --content="Decision with rationale"`

## Quality Gates

- Always validate work items: `apm work-item validate <id>`
- Check dependencies: `apm work-item list-dependencies <id>`
- Follow time-boxing limits (IMPLEMENTATION max 4h)
- Record all decisions with evidence

## Context-First Approach

1. Get hierarchical context for the task
2. Review relevant patterns and decisions
3. Check work item dependencies and blockers
4. Follow established patterns and conventions
5. Record implementation decisions and rationale
""",
        examples_template="""
## Examples

### {{ agent_role }} Task Execution
```bash
# 1. Get task context
apm context show --task-id=<task_id>

# 2. Review SOP and capabilities
# Follow the Standard Operating Procedure above

# 3. Execute task using specialised capabilities
# {{ agent_example_workflow }}

# 4. Record decisions
apm learnings record --type=decision --content="{{ agent_role }} approach applied"
```

### {{ agent_role }} Quality Assurance
```bash
# 1. Validate work item structure
apm work-item validate <work_item_id>

# 2. Check task dependencies
apm task list-dependencies <task_id>

# 3. Ensure quality gates compliance
# Verify all required tasks present and time-boxing respected

# 4. Record quality decisions
apm learnings record --type=quality --content="Quality gate validation completed"
```
""",
        required_variables=["agent_role", "agent_display_name", "agent_description", "agent_sop", "agent_capabilities", "agent_tools"],
        optional_variables=["agent_example_workflow"],
        default_capabilities=["agent-specialization", "sop-compliance", "quality-gates"]
    ),
    
    "workflow": SkillTemplate(
        template_id="workflow",
        name="APM (Agent Project Manager) {{ workflow_name.title() }} Workflow",
        description="Follow APM (Agent Project Manager) {{ workflow_name }} workflow with quality gates and task structure. Use when working on {{ workflow_name }} work items.",
        category=SkillCategory.WORKFLOW,
        instructions_template="""
# APM (Agent Project Manager) {{ workflow_name.title() }} Workflow

## Workflow Overview

{{ workflow_description }}

## Required Tasks

{% for task in required_tasks %}
- **{{ task }}**: {{ task_descriptions.get(task, "Required task") }}
{% endfor %}

## Time Limits

{% for task_type, hours in time_limits.items() %}
- **{{ task_type }}**: Max {{ hours }} hours
{% endfor %}

## Instructions

1. **Create Work Item**: `apm work-item create "{{ workflow_name.title() }} Name" --type {{ workflow_name }}`
2. **Add Required Tasks**: Ensure all required tasks are present
3. **Check Dependencies**: `apm work-item list-dependencies <id>`
4. **Follow Workflow**: Execute tasks in proper sequence
5. **Validate Quality**: `apm work-item validate <id>`

## Quality Gates

- All required tasks must be present
- Time-boxing limits must be respected
- Dependencies must be resolved before task start
- Acceptance criteria must be met before completion

## Context-First Approach

1. Get work item context: `apm context show --work-item-id=<id>`
2. Review workflow requirements and constraints
3. Check task dependencies and sequencing
4. Follow established workflow patterns
5. Record workflow decisions and rationale
""",
        examples_template="""
## Examples

### Starting {{ workflow_name.title() }} Work Item
```bash
# 1. Create work item
apm work-item create "{{ workflow_name.title() }} Example" --type {{ workflow_name }}

# 2. Add required tasks
{% for task in required_tasks %}
apm task create "{{ task }} Task" --type {{ task.lower() }} --effort {{ time_limits.get(task, 4) }}
{% endfor %}

# 3. Check dependencies
apm work-item list-dependencies <work_item_id>

# 4. Start first task
apm task start <first_task_id>
```

### {{ workflow_name.title() }} Quality Validation
```bash
# 1. Validate work item structure
apm work-item validate <work_item_id>

# 2. Check all required tasks present
apm task list --work-item-id=<work_item_id>

# 3. Verify time-boxing compliance
# Check that no task exceeds time limits

# 4. Record validation
apm learnings record --type=validation --content="{{ workflow_name.title() }} workflow validated"
```
""",
        required_variables=["workflow_name", "workflow_description", "required_tasks", "time_limits"],
        optional_variables=["task_descriptions"],
        default_allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
        default_capabilities=["workflow-management", "quality-gates", "task-structure"]
    ),
    
    "quality-assurance": SkillTemplate(
        template_id="quality-assurance",
        name="APM (Agent Project Manager) Quality Assurance",
        description="Quality assurance and testing with APM (Agent Project Manager) standards. Use when writing tests, checking code quality, or ensuring compliance with APM (Agent Project Manager) quality gates.",
        category=SkillCategory.QUALITY_ASSURANCE,
        instructions_template="""
# APM (Agent Project Manager) Quality Assurance

## Instructions

1. **Get Implementation Context**: `apm context show --task-id=<implementation_task_id>`
2. **Write Comprehensive Tests**: Follow APM (Agent Project Manager) testing standards
3. **Ensure >90% Coverage**: Maintain high test coverage
4. **Test Quality Gates**: Verify all quality gates work correctly
5. **Record Test Patterns**: `apm learnings record --type=pattern --content="Test pattern established"`

## Testing Standards

- **Coverage**: >90% test coverage required
- **Pattern**: Arrange-Act-Assert pattern
- **Scope**: Test both happy path and error cases
- **Integration**: Test component interactions
- **Security**: Test input validation and output sanitization

## Quality Gates

- All required tasks present for work item type
- Time-boxing limits respected (IMPLEMENTATION max 4h)
- Dependencies properly sequenced
- Tests passing with >90% coverage
- No circular dependencies

## Test Structure

```python
class TestComponentName:
    @pytest.fixture
    def component(self):
        return ComponentName()
    
    def test_operation_success(self, component):
        # Arrange
        input_data = "test input"
        
        # Act
        result = component.operation(input_data)
        
        # Assert
        assert result.success
        assert result.data == expected_output
```

## Context-First Testing

1. Get implementation context and details
2. Review existing test patterns and decisions
3. Understand component interactions and dependencies
4. Write tests following established patterns
5. Record test patterns and quality decisions
""",
        examples_template="""
## Examples

### Writing Tests for Implementation
```bash
# 1. Get implementation context
apm context show --task-id=<implementation_task_id>

# 2. Review implementation details
# Understand what needs to be tested

# 3. Write comprehensive tests
# Follow Arrange-Act-Assert pattern

# 4. Check coverage
python -m pytest --cov=agentpm --cov-report=term-missing

# 5. Record test patterns
apm learnings record --type=pattern --content="Test pattern for ComponentName"
```

### Quality Gate Validation
```bash
# 1. Validate work item structure
apm work-item validate <work_item_id>

# 2. Check time-boxing compliance
apm task list --type=implementation

# 3. Verify test coverage
python -m pytest --cov=agentpm --cov-report=html

# 4. Record quality validation
apm learnings record --type=quality --content="Quality gates validated"
```

### Security Testing
```bash
# 1. Test input validation
# Verify all inputs are validated at boundaries

# 2. Test output sanitization
# Ensure no sensitive data leaked

# 3. Test error handling
# Verify graceful error handling

# 4. Record security patterns
apm learnings record --type=security --content="Security test patterns established"
```
""",
        requirements_template="""
## Requirements

- pytest for testing framework
- coverage.py for coverage measurement
- APM (Agent Project Manager) project with test structure
- >90% test coverage maintained

## Installation

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run tests with coverage
python -m pytest --cov=agentpm --cov-report=html
```
""",
        default_allowed_tools=["Read", "Write", "Bash", "Grep", "Glob"],
        default_capabilities=["testing", "quality-assurance", "coverage-analysis", "security-testing"]
    )
}
