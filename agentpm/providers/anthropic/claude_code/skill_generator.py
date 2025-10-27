"""
SkillGenerator - Generate and manage skills for Claude Code provider

Generates reusable skill modules that can be assigned to agents:
- Populates database with core skills
- Generates .claude/skills/*.md files
- Supports progressive loading (metadata → instructions → resources)
- Integrates with ClaudeCodeGenerator

Part of WI-171: Claude Code Provider Enhancement
Task #1131: Implementation: SkillGenerator with Templates

Pattern: Template Method Pattern with Database-First Architecture
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.skill import Skill, SkillCategory
from agentpm.providers.base import TemplateBasedMixin, FileOutput


class SkillGenerator(TemplateBasedMixin):
    """
    Generate and manage skills for Claude Code provider.

    Responsibilities:
    - Populate database with core skills (9 baseline skills)
    - Generate .claude/skills/ markdown files
    - Support progressive loading (Level 1/2/3)
    - Integration with ClaudeCodeGenerator

    Design Principles:
    - Database-first: Skills stored in database, files are generated
    - Template-driven: All formatting in Jinja2 templates
    - Category-based: Skills organized by category (database, documentation, workflow)
    - Progressive loading: Metadata → Instructions → Resources

    Example:
        >>> db = DatabaseService("path/to/db")
        >>> generator = SkillGenerator(db)
        >>> generator.populate_core_skills()
        >>> generator.generate_skill_files(output_dir=Path(".claude/skills"))
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize skill generator.

        Args:
            db_service: Database service for accessing APM data

        Raises:
            FileNotFoundError: If template directory doesn't exist
        """
        self.db = db_service

        # Initialize Jinja2 templates
        template_dir = Path(__file__).parent / "templates"
        self._init_templates(template_dir)

    def populate_core_skills(self) -> List[Skill]:
        """
        Populate database with 9 core skills.

        Creates baseline skills organized by category:
        - Database (3): migrations, schema-design, query-optimization
        - Documentation (3): doc020, writing-patterns, markdown-conventions
        - Workflow (3): work-item-lifecycle, task-workflow, agent-delegation

        Returns:
            List of created Skill models

        Raises:
            ValidationError: If skill name already exists
            ValueError: If skill data is invalid

        Example:
            >>> skills = generator.populate_core_skills()
            >>> print(f"Created {len(skills)} skills")
            Created 9 skills
        """
        from agentpm.core.database.methods.skills import create_skill, get_skill_by_name

        skills_data = self._get_core_skills_data()
        created_skills: List[Skill] = []

        # Use transaction context manager
        with self.db.transaction() as conn:
            # Create a simple wrapper to match the expected interface
            class ServiceWrapper:
                def __init__(self, connection):
                    self.conn = connection

            service_wrapper = ServiceWrapper(conn)

            for skill_data in skills_data:
                # Check if skill already exists
                existing = get_skill_by_name(service_wrapper, skill_data["name"])
                if existing:
                    print(f"⚠️  Skill '{skill_data['name']}' already exists (ID: {existing.id})")
                    created_skills.append(existing)
                    continue

                # Create skill model
                skill = Skill(**skill_data)

                # Save to database
                created = create_skill(service_wrapper, skill)
                print(f"✅ Created skill: {created.name} (ID: {created.id})")
                created_skills.append(created)

        return created_skills

    def generate_skill_files(
        self,
        output_dir: Path,
        skills: Optional[List[Skill]] = None,
        enabled_only: bool = True
    ) -> List[FileOutput]:
        """
        Generate .claude/skills/*.md files from database.

        Creates skill files with YAML frontmatter and markdown content:
        - skills/<category>/<name>.md (e.g., skills/database/apm-database-migrations.md)

        Args:
            output_dir: Directory to generate files (typically .claude/skills)
            skills: Optional list of skills (if None, loads from database)
            enabled_only: Only generate enabled skills (default: True)

        Returns:
            List of FileOutput for each skill file

        Example:
            >>> files = generator.generate_skill_files(
            ...     output_dir=Path(".claude/skills")
            ... )
            >>> print(f"Generated {len(files)} skill files")
        """
        from agentpm.core.database.methods.skills import list_skills

        # Load skills from database if not provided
        if skills is None:
            with self.db.connect() as conn:
                # Create a simple wrapper to match the expected interface
                class ServiceWrapper:
                    def __init__(self, connection):
                        self.conn = connection

                service_wrapper = ServiceWrapper(conn)
                skills = list_skills(service_wrapper, enabled_only=enabled_only)

        files: List[FileOutput] = []

        for skill in skills:
            # Render skill template
            context = {
                "skill": skill,
                "generation_time": datetime.utcnow().isoformat()
            }

            content = self._render_template("skill.md.j2", context)

            # Determine output path (organized by category)
            if skill.category:
                # Handle both enum and string category values
                category_value = skill.category.value if hasattr(skill.category, 'value') else skill.category
                category_dir = output_dir / category_value
            else:
                category_dir = output_dir / "uncategorized"

            category_dir.mkdir(parents=True, exist_ok=True)

            # Write file
            output_path = category_dir / f"{skill.name}.md"
            output_path.write_text(content)

            files.append(FileOutput.create_from_content(output_path, content))
            print(f"✅ Generated: {output_path.relative_to(output_dir.parent)}")

        return files

    # ========================================================================
    # Core Skills Definitions
    # ========================================================================

    def _get_core_skills_data(self) -> List[Dict[str, Any]]:
        """
        Get baseline skills data for core APM operations.

        Returns 9 core skills organized by category:
        - Database (3): migrations, schema-design, query-optimization
        - Documentation (3): doc020, writing-patterns, markdown-conventions
        - Workflow (3): work-item-lifecycle, task-workflow, agent-delegation

        Returns:
            List of dictionaries with skill data
        """
        return [
            # ================================================================
            # DATABASE SKILLS (3)
            # ================================================================
            {
                "name": "apm-database-migrations",
                "display_name": "APM Database Migrations",
                "description": "SQLite migration best practices: idempotent operations, data preservation, rollback safety",
                "category": SkillCategory.DATABASE,
                "instructions": self._get_database_migrations_instructions(),
                "resources": {
                    "examples": [
                        "0050_add_skills_tables.sql",
                        "0051_add_hooks_tables.sql",
                        "0052_add_memory_tables.sql"
                    ],
                    "templates": [
                        "migration_template.sql"
                    ],
                    "docs": [
                        "docs/architecture/database-migration-patterns.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Read", "Write", "Bash"]
                    }
                },
                "enabled": True
            },
            {
                "name": "apm-database-schema-design",
                "display_name": "APM Database Schema Design",
                "description": "Three-tier architecture: Pydantic models, SQLite adapters, business methods with type safety",
                "category": SkillCategory.DATABASE,
                "instructions": self._get_database_schema_design_instructions(),
                "resources": {
                    "examples": [
                        "agentpm/core/database/models/skill.py",
                        "agentpm/core/database/adapters/skill_adapter.py",
                        "agentpm/core/database/methods/skills.py"
                    ],
                    "templates": [
                        "model_template.py",
                        "adapter_template.py",
                        "methods_template.py"
                    ],
                    "docs": [
                        "docs/architecture/three-tier-architecture.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Read", "Write", "Edit"]
                    }
                },
                "enabled": True
            },
            {
                "name": "sqlite-query-optimization",
                "display_name": "SQLite Query Optimization",
                "description": "Performance optimization: indexes, query planning, JOIN strategies, pagination patterns",
                "category": SkillCategory.DATABASE,
                "instructions": self._get_sqlite_query_optimization_instructions(),
                "resources": {
                    "examples": [
                        "SELECT with covering indexes",
                        "Efficient JOIN patterns",
                        "Pagination with LIMIT/OFFSET"
                    ],
                    "templates": [
                        "optimized_query_patterns.sql"
                    ],
                    "docs": [
                        "docs/architecture/query-optimization-guide.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Read", "Bash"]
                    }
                },
                "enabled": True
            },

            # ================================================================
            # DOCUMENTATION SKILLS (3)
            # ================================================================
            {
                "name": "apm-documentation-doc020",
                "display_name": "APM Documentation - DOC-020 Compliance",
                "description": "Database-first documentation: ALWAYS use 'apm document add' command, NEVER Write/Edit for docs/",
                "category": SkillCategory.DOCUMENTATION,
                "instructions": self._get_documentation_doc020_instructions(),
                "resources": {
                    "examples": [
                        "apm document add --entity-type=work-item --entity-id=158 ...",
                        "Context-aware path generation",
                        "Visibility scopes: private/team/public"
                    ],
                    "templates": [
                        "document_add_command_template.sh"
                    ],
                    "docs": [
                        "docs/rules/DOC-020_DATABASE_FIRST_DOCUMENTS.md",
                        ".agentpm/docs/processes/runbook/document-visibility-and-lifecycle-workflow.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Bash"]
                    }
                },
                "enabled": True
            },
            {
                "name": "technical-writing-patterns",
                "display_name": "Technical Writing Patterns",
                "description": "Clear, concise technical documentation: structure, tone, examples, troubleshooting sections",
                "category": SkillCategory.DOCUMENTATION,
                "instructions": self._get_technical_writing_patterns_instructions(),
                "resources": {
                    "examples": [
                        "User guide structure",
                        "API documentation patterns",
                        "Troubleshooting sections"
                    ],
                    "templates": [
                        "user_guide_template.md",
                        "api_doc_template.md",
                        "troubleshooting_template.md"
                    ],
                    "docs": [
                        "docs/guides/developer/writing-effective-documentation.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Read", "Write", "Edit"]
                    }
                },
                "enabled": True
            },
            {
                "name": "apm-markdown-conventions",
                "display_name": "APM Markdown Conventions",
                "description": "Project-specific markdown style: headings, code blocks, tables, callouts, cross-references",
                "category": SkillCategory.DOCUMENTATION,
                "instructions": self._get_markdown_conventions_instructions(),
                "resources": {
                    "examples": [
                        "# Heading conventions",
                        "```python code blocks",
                        "| Table | Format |",
                        "> Callouts"
                    ],
                    "templates": [
                        "markdown_template.md"
                    ],
                    "docs": [
                        "docs/guides/developer/markdown-style-guide.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Read", "Write", "Edit"]
                    }
                },
                "enabled": True
            },

            # ================================================================
            # WORKFLOW SKILLS (3)
            # ================================================================
            {
                "name": "apm-work-item-lifecycle",
                "display_name": "APM Work Item Lifecycle",
                "description": "Work item workflow: D1→P1→I1→R1→O1→E1 phases, quality gates, status transitions",
                "category": SkillCategory.PROJECT_MANAGEMENT,
                "instructions": self._get_work_item_lifecycle_instructions(),
                "resources": {
                    "examples": [
                        "apm work-item create",
                        "apm work-item next <id>",
                        "apm work-item show <id>"
                    ],
                    "templates": [
                        "work_item_workflow.md"
                    ],
                    "docs": [
                        "docs/components/workflow/work-item-lifecycle.md",
                        "CLAUDE.md sections on phase routing"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Bash"]
                    }
                },
                "enabled": True
            },
            {
                "name": "apm-task-workflow",
                "display_name": "APM Task Workflow",
                "description": "Task lifecycle: draft→validated→accepted→in_progress→review→completed, quality metadata updates",
                "category": SkillCategory.PROJECT_MANAGEMENT,
                "instructions": self._get_task_workflow_instructions(),
                "resources": {
                    "examples": [
                        "apm task start <id>",
                        "apm task update <id> --quality-metadata='{...}'",
                        "apm task submit-review <id>",
                        "apm task approve <id>"
                    ],
                    "templates": [
                        "task_workflow.md"
                    ],
                    "docs": [
                        "docs/components/workflow/task-lifecycle.md",
                        ".agentpm/docs/governance/quality_gates_spec/agent-operating-protocol-mandatory-workflow-compliance.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": ["Bash"]
                    }
                },
                "enabled": True
            },
            {
                "name": "apm-agent-delegation",
                "display_name": "APM Agent Delegation",
                "description": "Multi-agent coordination: phase orchestrators, specialist agents, sub-agents, Task tool patterns",
                "category": SkillCategory.PROJECT_MANAGEMENT,
                "instructions": self._get_agent_delegation_instructions(),
                "resources": {
                    "examples": [
                        "Task(subagent_type='definition-orch', ...)",
                        "Task(subagent_type='aipm-python-cli-developer', ...)",
                        "Task(subagent_type='context-delivery', ...)"
                    ],
                    "templates": [
                        "delegation_template.md"
                    ],
                    "docs": [
                        "CLAUDE.md sections on delegation",
                        "docs/components/agents/architecture/three-tier-orchestration.md"
                    ]
                },
                "provider_config": {
                    "claude-code": {
                        "allowed_tools": []  # No tools needed, coordination only
                    }
                },
                "enabled": True
            }
        ]

    # ========================================================================
    # Skill Instructions (Content)
    # ========================================================================

    def _get_database_migrations_instructions(self) -> str:
        """Database migrations skill instructions"""
        return """# APM Database Migrations

## Overview
SQLite migration best practices for APM database schema evolution.

## Principles
1. **Idempotent operations**: Safe to run multiple times
2. **Data preservation**: Never lose existing data
3. **Rollback safety**: Migrations can be reversed
4. **Backward compatibility**: Gradual schema evolution

## Pattern
```sql
-- Migration: 0050_add_skills_tables.sql

-- Check if table exists
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT,
    instructions TEXT NOT NULL,
    resources TEXT,  -- JSON
    provider_config TEXT,  -- JSON
    enabled INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_enabled ON skills(enabled);
```

## Best Practices
- Always use `CREATE TABLE IF NOT EXISTS`
- Always use `CREATE INDEX IF NOT EXISTS`
- Use TEXT for JSON data (SQLite limitation)
- Add constraints inline (PRIMARY KEY, NOT NULL, UNIQUE)
- Use triggers for updated_at timestamps
- Test migrations on copy of database first

## Anti-Patterns
❌ DROP TABLE without backup
❌ ALTER TABLE without data migration
❌ Missing IF NOT EXISTS checks
❌ Breaking changes without version bump
"""

    def _get_database_schema_design_instructions(self) -> str:
        """Database schema design skill instructions"""
        return """# APM Database Schema Design

## Three-Tier Architecture

### Layer 1: Pydantic Models (Type Safety)
```python
from pydantic import BaseModel, Field

class Skill(BaseModel):
    id: Optional[int] = None
    name: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    display_name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    category: Optional[SkillCategory] = None
    instructions: str = Field(min_length=1)
    resources: Optional[Dict[str, Any]] = None
    provider_config: Optional[Dict[str, Any]] = None
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### Layer 2: SQLite Adapters (Conversion)
```python
class SkillAdapter:
    @staticmethod
    def to_db(skill: Skill) -> Dict[str, Any]:
        return {
            "name": skill.name,
            "display_name": skill.display_name,
            "description": skill.description,
            "category": skill.category.value if skill.category else None,
            "instructions": skill.instructions,
            "resources": json.dumps(skill.resources) if skill.resources else None,
            "provider_config": json.dumps(skill.provider_config) if skill.provider_config else None,
            "enabled": 1 if skill.enabled else 0,
            "created_at": skill.created_at.isoformat(),
            "updated_at": skill.updated_at.isoformat()
        }

    @staticmethod
    def from_db(data: Dict[str, Any]) -> Skill:
        return Skill(
            id=data["id"],
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            category=SkillCategory(data["category"]) if data["category"] else None,
            instructions=data["instructions"],
            resources=json.loads(data["resources"]) if data["resources"] else None,
            provider_config=json.loads(data["provider_config"]) if data["provider_config"] else None,
            enabled=bool(data["enabled"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
```

### Layer 3: Business Methods (CRUD)
```python
def create_skill(service, skill: Skill) -> Skill:
    db_data = SkillAdapter.to_db(skill)
    cursor = service.conn.execute(
        "INSERT INTO skills (...) VALUES (...)",
        (...)
    )
    service.conn.commit()
    skill.id = cursor.lastrowid
    return skill
```

## Design Principles
1. **Type safety first**: Pydantic validation catches errors early
2. **Clear separation**: Models ≠ Database ≠ Business Logic
3. **Single responsibility**: Each layer has one job
4. **Testability**: Each layer can be tested independently
"""

    def _get_sqlite_query_optimization_instructions(self) -> str:
        """SQLite query optimization skill instructions"""
        return """# SQLite Query Optimization

## Index Strategy

### Covering Indexes
```sql
-- Query: SELECT name, category FROM skills WHERE enabled = 1
-- Optimal index (covering):
CREATE INDEX idx_skills_enabled_covering ON skills(enabled, name, category);
```

### Composite Indexes
```sql
-- Query: SELECT * FROM agent_skills WHERE agent_id = ? AND skill_id = ?
-- Optimal index:
CREATE INDEX idx_agent_skills_composite ON agent_skills(agent_id, skill_id);
```

## Query Patterns

### Efficient JOINs
```sql
-- Use indexes on JOIN columns
SELECT s.*, ags.priority
FROM skills s
JOIN agent_skills ags ON s.id = ags.skill_id
WHERE ags.agent_id = ?
ORDER BY ags.priority DESC;
```

### Pagination
```sql
-- Use LIMIT/OFFSET with ORDER BY
SELECT * FROM skills
WHERE enabled = 1
ORDER BY category, name
LIMIT 20 OFFSET 40;
```

## Best Practices
1. **Index foreign keys**: Always index JOIN columns
2. **Use EXPLAIN QUERY PLAN**: Verify index usage
3. **Avoid SELECT ***: Only select needed columns
4. **Limit result sets**: Use LIMIT for pagination
5. **Order consistently**: ORDER BY indexed columns

## Anti-Patterns
❌ Missing indexes on WHERE clauses
❌ SELECT * with large tables
❌ OFFSET pagination without indexes
❌ OR conditions (use IN instead)
"""

    def _get_documentation_doc020_instructions(self) -> str:
        """Documentation DOC-020 compliance skill instructions"""
        return """# APM Documentation - DOC-020 Compliance

## CRITICAL RULE: Database-First Documents

**ALWAYS use**: `apm document add` command
**NEVER use**: Write/Edit/Bash for docs/ directory

## Rule: DOC-020
- **Enforcement**: BLOCK (hard failure)
- **Category**: Documentation Principles
- **Priority**: CRITICAL

## Correct Pattern

### ✅ ALWAYS Do This:
```bash
apm document add \\
  --entity-type=work-item \\
  --entity-id=158 \\
  --category=planning \\
  --type=requirements \\
  --title="Phase 1 Specification" \\
  --description="Comprehensive specification for Phase 1" \\
  --content="$(cat <<'EOF'
# Phase 1 Specification

## Overview
...
EOF
)"
```

### ❌ NEVER Do This:
```python
# PROHIBITED - Violation of DOC-020
Write(file_path="docs/features/spec.md", content="...")
Edit(file_path="docs/guide.md", old_string="...", new_string="...")
Bash(command="echo '...' > docs/file.md")
```

## Required Fields
| Field | Required | Example |
|-------|----------|---------|
| `--entity-type` | ✅ | `work-item`, `task`, `project` |
| `--entity-id` | ✅ | `158` |
| `--category` | ✅ | `planning`, `architecture`, `guides` |
| `--type` | ✅ | `requirements`, `design_doc`, `user_guide` |
| `--title` | ✅ | `Phase 1 Specification` |
| `--content` | ✅ | Full markdown content |
| `--description` | Recommended | Brief summary |

## File Path Patterns
```
docs/
  ├── features/           # category: planning, type: requirements
  ├── architecture/       # category: architecture
  │   ├── design/        # type: design_doc
  │   └── adrs/          # type: adr
  ├── guides/            # category: guides
  │   ├── user/          # type: user_guide
  │   ├── developer/     # type: developer_guide
  │   └── admin/         # type: admin_guide
  ├── reference/         # category: reference
  ├── processes/         # category: processes
  └── operations/        # category: operations
```

## Why This Rule Exists
1. **Database is source of truth**: All documents tracked
2. **Entity linkage**: Documents linked to work items, tasks
3. **Metadata completeness**: Category, type, title maintained
4. **Consistent file naming**: Standard path patterns enforced
5. **Document lifecycle**: Creation, updates, archival tracked
"""

    def _get_technical_writing_patterns_instructions(self) -> str:
        """Technical writing patterns skill instructions"""
        return """# Technical Writing Patterns

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
"""

    def _get_markdown_conventions_instructions(self) -> str:
        """Markdown conventions skill instructions"""
        return r"""# APM Markdown Conventions

## Headings
```markdown
# H1: Document title (one per file)
## H2: Major sections
### H3: Subsections
#### H4: Rare, use sparingly
```

## Code Blocks
```markdown
```python
# Always specify language
def example():
    pass
```

```bash
# Shell commands
apm work-item list
```
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
"""

    def _get_work_item_lifecycle_instructions(self) -> str:
        """Work item lifecycle skill instructions"""
        return """# APM Work Item Lifecycle

## Phase Progression
```
D1_DISCOVERY → P1_PLAN → I1_IMPLEMENTATION → R1_REVIEW → O1_OPERATIONS → E1_EVOLUTION
```

## Phase Gates

### D1_DISCOVERY (Define Requirements)
**Gate Requirements**:
- business_context ≥50 chars
- acceptance_criteria ≥3
- risks ≥1
- 6W confidence ≥0.70

**Commands**:
```bash
apm work-item create "Feature Name" --type=feature
apm work-item next <id>  # Advance to P1
```

### P1_PLAN (Create Implementation Plan)
**Gate Requirements**:
- Tasks created (≥1 per AC)
- Effort estimates (≤4 hours each)
- Dependencies mapped
- Risk mitigations planned

**Commands**:
```bash
apm work-item next <id>  # Advance to I1
```

### I1_IMPLEMENTATION (Build & Test)
**Gate Requirements**:
- Tests updated
- Code complete
- Docs updated
- Migrations applied

### R1_REVIEW (Quality Validation)
**Gate Requirements**:
- AC verified
- Tests pass (100%)
- Quality checks passed
- Code review approved

### O1_OPERATIONS (Deploy & Monitor)
**Gate Requirements**:
- Version bumped
- Deployed
- Health checks passing
- Monitoring active

### E1_EVOLUTION (Continuous Improvement)
**Gate Requirements**:
- Telemetry analyzed
- Improvements identified
- Feedback captured
"""

    def _get_task_workflow_instructions(self) -> str:
        """Task workflow skill instructions"""
        return """# APM Task Workflow

## Task States
```
draft → validated → accepted → in_progress → review → completed
```

## Agent Operating Protocol

### STEP 1 - START
```bash
apm task start <task-id>  # Transition to ACTIVE
```

### STEP 2 - WORK
```bash
apm task update <task-id> --quality-metadata='{
  "progress": "Implementing feature X",
  "tests_passing": true,
  "coverage_percent": 85
}'
```

### STEP 3 - COMPLETE
```bash
apm task update <task-id> --quality-metadata='{
  "completed": true,
  "deliverables": ["file1.py", "file2.py"],
  "tests_passing": true,
  "coverage_percent": 90
}'
apm task submit-review <task-id>  # Transition to REVIEW
apm task approve <task-id>  # Transition to DONE
```

## Hybrid Command Interface

**Automatic Progression** (Recommended):
```bash
apm task next <id>  # Auto-advances to next logical state
```

**Explicit Control** (When needed):
```bash
apm task validate <id>
apm task accept <id> --agent <role>
apm task start <id>
apm task submit-review <id>
apm task approve <id>
apm task request-changes <id> --reason "..."
```
"""

    def _get_agent_delegation_instructions(self) -> str:
        """Agent delegation skill instructions"""
        return """# APM Agent Delegation

## Three-Tier Architecture

### Tier 1: Master Orchestrator
- Routes work by phase
- Never implements directly
- Always delegates via Task tool

### Tier 2: Phase Orchestrators (6)
- definition-orch (D1)
- planning-orch (P1)
- implementation-orch (I1)
- review-test-orch (R1)
- release-ops-orch (O1)
- evolution-orch (E1)

### Tier 3: Specialist Agents (~15)
- aipm-python-cli-developer
- aipm-database-developer
- aipm-testing-specialist
- aipm-documentation-specialist
- aipm-quality-validator

### Tier 4: Sub-Agents (~25)
- context-delivery (MANDATORY at session start)
- intent-triage
- ac-writer
- test-runner
- quality-gatekeeper

## Delegation Pattern

```python
Task(
  subagent_type="aipm-python-cli-developer",
  description="Implement CLI command",
  prompt=\"\"\"MANDATORY: Follow Agent Operating Protocol

BEFORE STARTING:
  1. Run: apm task start <task-id>

DURING WORK:
  2. Update: apm task update <task-id> --quality-metadata='{...}'

AFTER COMPLETION:
  3. Complete: apm task update <task-id> --quality-metadata='{"completed": true, ...}'
  4. Transition: apm task submit-review <task-id> && apm task approve <task-id>

YOUR TASK:
  Implement [command] following three-layer pattern:
  - Models (Pydantic)
  - Adapters (SQLite conversion)
  - Methods (business logic)

  Task ID: <task-id>
  Requirements: [details]
\"\"\"
)
```

## Best Practices
1. **Always start with context-delivery**: Get current state
2. **Route by phase**: Use phase orchestrators
3. **Be specific**: Provide clear task description
4. **Include protocol**: Reference Agent Operating Protocol
5. **Provide context**: Include work item/task IDs
"""
