---
# Skill Metadata (Level 1)
name: apm-database-schema-design
display_name: APM Database Schema Design
description: Three-tier architecture: Pydantic models, SQLite adapters, business methods with type safety
category: database
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
created_at: 2025-10-27T18:34:16.596555
updated_at: 2025-10-27T18:34:16.596556
---

# APM Database Schema Design

## Description
Three-tier architecture: Pydantic models, SQLite adapters, business methods with type safety

**Category**: database

---

## Instructions (Level 2)

# APM Database Schema Design

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

---

## Resources (Level 3)

### Examples
- `agentpm/core/database/models/skill.py`
- `agentpm/core/database/adapters/skill_adapter.py`
- `agentpm/core/database/methods/skills.py`

### Templates
- `model_template.py`
- `adapter_template.py`
- `methods_template.py`

### Documentation
- [docs/architecture/three-tier-architecture.md](docs/architecture/three-tier-architecture.md)


---

## Usage in Agent Delegation

When delegating to an agent that needs this skill:

```python
Task(
  subagent_type="<agent-role>",
  description="Task requiring APM Database Schema Design",
  prompt=\"\"\"
  Apply apm-database-schema-design skill:

  Context: [Provide context]
  Requirements: [Provide requirements]

  Follow the patterns and best practices from the APM Database Schema Design skill.
  \"\"\"
)
```

---

**Skill ID**: 2
**Generated**: 2025-10-27T18:35:40.564370
**Status**: Enabled
