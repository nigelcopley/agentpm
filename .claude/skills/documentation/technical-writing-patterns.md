---
# Skill Metadata (Level 1)
name: technical-writing-patterns
display_name: Technical Writing Patterns
description: Clear, concise technical documentation: structure, tone, examples, troubleshooting sections
category: documentation
enabled: true

# Provider Configuration
provider: claude-code
allowed_tools:
  - Read
  - Write
  - Edit

# Progressive Loading
progressive_load_level: 2
# Level 1: Metadata only (this frontmatter)
# Level 2: + Instructions (skill content below)
# Level 3: + Resources (examples, templates, docs at end)

# Timestamps
created_at: 2025-10-27T18:34:16.597595
updated_at: 2025-10-27T18:34:16.597595
---

# Technical Writing Patterns

## Description
Clear, concise technical documentation: structure, tone, examples, troubleshooting sections

**Category**: documentation

---

## Instructions (Level 2)

# Technical Writing Patterns

## Structure

### User Guide Pattern
```markdown
# Feature Name

## Overview
Brief description (1-2 sentences).

## When to Use
Use cases and scenarios.

## Getting Started
Step-by-step guide:
1. First step
2. Second step
3. Third step

## Examples
Practical examples with code blocks.

## Troubleshooting
Common issues and solutions.

## See Also
- Related guides
- API references
```

### API Documentation Pattern
```markdown
# Method Name

## Signature
```python
def method_name(param1: Type1, param2: Type2) -> ReturnType:
```

## Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param1 | Type1 | ✅ | Description |
| param2 | Type2 | ❌ | Optional param |

## Returns
Description of return value.

## Raises
- `ValueError`: When X happens
- `RuntimeError`: When Y happens

## Example
```python
result = method_name(param1="value", param2=42)
```
```

## Best Practices
1. **Start with overview**: What, not how
2. **Use active voice**: "Create a skill" not "A skill is created"
3. **Include examples**: Show, don't just tell
4. **Add troubleshooting**: Anticipate common issues
5. **Keep it concise**: Respect reader's time

---

## Resources (Level 3)

### Examples
- `User guide structure`
- `API documentation patterns`
- `Troubleshooting sections`

### Templates
- `user_guide_template.md`
- `api_doc_template.md`
- `troubleshooting_template.md`

### Documentation
- [docs/guides/developer/writing-effective-documentation.md](docs/guides/developer/writing-effective-documentation.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring Technical Writing Patterns",
  prompt=\"\"\"
  Apply technical-writing-patterns skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the Technical Writing Patterns skill.
  \"\"\"
)
```

---

**Skill ID**: 5
**Generated**: 2025-10-27T18:35:40.564870
**Status**: Enabled
