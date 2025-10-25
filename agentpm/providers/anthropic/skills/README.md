# Claude Code Skills Integration

This module provides integration between APM (Agent Project Manager) and Claude Code Skills, enabling seamless project management within Claude Code.

## Overview

Claude Code Skills are modular capabilities that extend Claude's functionality through organized folders containing instructions, scripts, and resources. This module converts APM (Agent Project Manager)'s structured project management into discoverable Skills for Claude Code.

## Features

- **Agent Skills**: Convert APM (Agent Project Manager) agents into specialized Skills
- **Workflow Skills**: Generate Skills for APM (Agent Project Manager) workflows (feature, bugfix, enhancement)
- **Framework Skills**: Create framework-specific Skills (Django, Python, pytest)
- **Core Skills**: Essential APM (Agent Project Manager) project management Skills
- **Template System**: Reusable templates for different Skill types

## Usage

### Generate Skills

```bash
# Generate all Skills for current project
apm skills generate

# Generate specific types of Skills
apm skills generate --include-agents --include-workflows

# Generate Skills to personal directory
apm skills generate --skill-type personal --output-dir ~/.claude/skills
```

### List Skills

```bash
# List all generated Skills
apm skills list

# Show specific Skill details
apm skills show "aipm-v2-project-manager"
```

### Manage Skills

```bash
# Remove specific Skill
apm skills remove "aipm-v2-project-manager"

# Clear all Skills
apm skills clear
```

## Skill Types

### 1. Project Manager Skill

Core APM (Agent Project Manager) project management capabilities:

- Work item creation and management
- Task creation with time-boxing
- Quality gate enforcement
- Context assembly
- Evidence-based development

### 2. Agent Specialization Skills

Skills based on APM (Agent Project Manager) agents:

- **Rapid Prototyper**: MVP development with time constraints
- **Enterprise Architect**: Large system design and compliance
- **Quality Engineer**: Testing and quality assurance
- **Production Specialist**: Bug fixes and incident response

### 3. Workflow Skills

Skills for specific APM (Agent Project Manager) workflows:

- **Feature Workflow**: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- **Bugfix Workflow**: ANALYSIS + BUGFIX + TESTING
- **Enhancement Workflow**: DESIGN + IMPLEMENTATION + TESTING

### 4. Framework Skills

Framework-specific development Skills:

- **Django Development**: Django patterns with APM (Agent Project Manager) project management
- **Python Development**: Python best practices with quality gates
- **pytest Testing**: Testing patterns with APM (Agent Project Manager) standards

## Skill Structure

Each Skill follows the Claude Code Skills specification:

```
skill-directory/
├── SKILL.md          # Main skill definition with YAML frontmatter
├── metadata.json     # APM (Agent Project Manager) metadata and tracking
└── supporting-files/ # Optional scripts, templates, etc.
```

### SKILL.md Format

```markdown
---
name: APM (Agent Project Manager) Project Manager
description: Comprehensive Agent Project Manager for managing work items, tasks, and context
allowed-tools: Read, Write, Bash, Grep, Glob
---

# APM (Agent Project Manager) Project Manager

## Instructions

1. **Check Project Status**: `apm status`
2. **List Work Items**: `apm work-item list`
3. **Get Context**: `apm context show --work-item-id=all`
4. **Create Work Items**: `apm work-item create "Name" --type feature`
5. **Manage Tasks**: `apm task create "Name" --type implementation --effort 4`

## Quality Gates

- FEATURE requires: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
- IMPLEMENTATION tasks max 4 hours (enforced)
- Always check dependencies before starting work

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
```

## Template System

The module uses a template system for generating Skills:

### Available Templates

- **project-manager**: Core project management capabilities
- **framework-specific**: Framework-specific development
- **agent-specialization**: Agent-based specialization
- **workflow**: Workflow-specific processes
- **quality-assurance**: Testing and quality assurance

### Template Variables

Templates support variables for customization:

```python
template.render_skill(
    name="Custom Skill Name",
    description="Custom description",
    framework_name="Django",
    agent_role="python-developer",
    # ... other variables
)
```

## Integration with Claude Code

### Automatic Discovery

Claude Code automatically discovers Skills from:

- **Personal Skills**: `~/.claude/skills/`
- **Project Skills**: `.claude/skills/`
- **Plugin Skills**: Bundled with plugins

### Model-Invoked Usage

Skills are **model-invoked** - Claude autonomously decides when to use them based on your request and the Skill's description. This is different from slash commands which are **user-invoked**.

### Tool Permissions

Skills can restrict tool access using the `allowed-tools` frontmatter:

```yaml
---
name: Safe File Reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---
```

## Development

### Adding New Templates

1. Create template in `templates.py`:

```python
"new-template": SkillTemplate(
    template_id="new-template",
    name="New Template",
    description="Template description",
    category=SkillCategory.NEW_CATEGORY,
    instructions_template="Template with {{ variables }}",
    required_variables=["name"],
    optional_variables=["description"]
)
```

2. Register template in generator:

```python
self.registry.register_template(get_skill_template("new-template"))
```

### Testing

Run tests for the skills module:

```bash
python -m pytest tests/providers/test_anthropic_skills.py -v
```

## Best Practices

### Skill Descriptions

Write specific, actionable descriptions:

```yaml
# Good
description: "Django development with APM (Agent Project Manager) project management. Use when working on Django projects that need structured development workflow."

# Bad
description: "For Django"
```

### Tool Restrictions

Use `allowed-tools` for security-sensitive Skills:

```yaml
---
name: Read-Only Analysis
description: Analyze code without making changes
allowed-tools: Read, Grep, Glob
---
```

### Supporting Files

Include supporting files for complex Skills:

```python
skill.supporting_files = {
    "scripts/helper.py": "#!/usr/bin/env python3\n# Helper script",
    "templates/example.txt": "Example template content"
}
```

## Troubleshooting

### Skills Not Discovered

1. Check Skill directory exists: `ls .claude/skills/`
2. Verify SKILL.md exists: `ls .claude/skills/*/SKILL.md`
3. Check YAML syntax: `cat .claude/skills/*/SKILL.md | head -10`
4. Restart Claude Code to reload Skills

### Template Errors

1. Check required variables are provided
2. Verify Jinja2 template syntax
3. Test template rendering with sample data

### Generation Errors

1. Check database connection
2. Verify project is initialised: `apm status`
3. Check agent/workflow data exists
4. Review error logs for specific issues

## Future Enhancements

- **Plugin Skills**: Bundle Skills with APM (Agent Project Manager) plugins
- **Dynamic Skills**: Generate Skills based on project context
- **Skill Marketplace**: Share Skills across teams
- **Advanced Templates**: More sophisticated template system
- **Skill Analytics**: Track Skill usage and effectiveness
