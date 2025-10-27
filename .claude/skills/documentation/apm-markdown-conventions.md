---
# Skill Metadata (Level 1)
name: apm-markdown-conventions
display_name: APM Markdown Conventions
description: Project-specific markdown style: headings, code blocks, tables, callouts, cross-references
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
created_at: 2025-10-27T18:34:16.597920
updated_at: 2025-10-27T18:34:16.597920
---

# APM Markdown Conventions

## Description
Project-specific markdown style: headings, code blocks, tables, callouts, cross-references

**Category**: documentation

---

## Instructions (Level 2)

# APM Markdown Conventions

## Headings
```markdown
# H1: Document title (one per file)
## H2: Major sections
### H3: Subsections
#### H4: Rare, use sparingly
```

## Code Blocks
```markdown
\```python
# Always specify language
def example():
    pass
\```

\```bash
# Shell commands
apm work-item list
\```
```

## Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

## Callouts
```markdown
> **Note**: Informational callout

> **Warning**: Something to be careful about

> **Critical**: Important warning
```

## Cross-References
```markdown
See [Document Name](path/to/doc.md) for details.

Related: [Section](#section-anchor)
```

## Lists
```markdown
**Ordered** (steps):
1. First step
2. Second step
3. Third step

**Unordered** (items):
- Item one
- Item two
- Item three

**Task lists**:
- [ ] Todo item
- [x] Completed item
```

---

## Resources (Level 3)

### Examples
- `# Heading conventions`
- ````python code blocks`
- `| Table | Format |`
- `> Callouts`

### Templates
- `markdown_template.md`

### Documentation
- [docs/guides/developer/markdown-style-guide.md](docs/guides/developer/markdown-style-guide.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Markdown Conventions",
  prompt=\"\"\"
  Apply apm-markdown-conventions skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Markdown Conventions skill.
  \"\"\"
)
```

---

**Skill ID**: 6
**Generated**: 2025-10-27T18:35:40.564768
**Status**: Enabled
