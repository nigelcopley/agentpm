# BaseProvider Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AgentPM Configuration Generation                   │
│                                                                               │
│  ┌─────────────────────┐           ┌──────────────────────────────────────┐ │
│  │   AGENTS.md         │           │       Database (SQLite)               │ │
│  │   (Universal)       │──────────▶│  ┌─────────────────────────────────┐ │ │
│  │                     │  Import   │  │ agents   rules   projects       │ │ │
│  │  - Agent definitions│           │  │ contexts  metadata  features    │ │ │
│  │  - SOPs            │           │  └─────────────────────────────────┘ │ │
│  │  - Capabilities    │           │                                        │ │
│  └─────────────────────┘           └──────────────────────────────────────┘ │
│                                                  │                            │
│                                                  │ Query                      │
│                                                  ▼                            │
│                            ┌──────────────────────────────────┐             │
│                            │  ProviderGenerationService       │             │
│                            │  (Bridge Layer)                  │             │
│                            │                                  │             │
│                            │  - Load agents from DB           │             │
│                            │  - Load rules from DB            │             │
│                            │  - Build GenerationContext       │             │
│                            │  - Orchestrate generation        │             │
│                            └──────────────────────────────────┘             │
│                                                  │                            │
│                                                  │ Delegates to               │
│                                                  ▼                            │
│                ┌────────────────────────────────────────────────────┐       │
│                │       BaseProviderGenerator (ABC)                  │       │
│                │                                                     │       │
│                │  + generate_from_agents(context) → Result         │       │
│                │  + validate_config(context) → (bool, errors)       │       │
│                │  + format_context(context) → Dict                  │       │
│                │  + get_output_paths(context) → List[Path]          │       │
│                │  + get_provider_metadata() → Dict                  │       │
│                │                                                     │       │
│                │  # validate_agents() - common validation           │       │
│                │  # validate_rules() - common validation            │       │
│                │  # write_file() - file generation                  │       │
│                │  # generate_file_hash() - SHA-256 integrity        │       │
│                └────────────────────────────────────────────────────┘       │
│                                       ▲                                      │
│                                       │ Extends                               │
│                       ┌───────────────┴───────────────┐                     │
│                       │                               │                      │
│          ┌────────────────────────┐   ┌─────────────────────────────┐      │
│          │ TemplateBasedMixin     │   │  ProgrammaticGenerator      │      │
│          │                        │   │  (Code-based, no templates) │      │
│          │ + Jinja2 integration   │   │                             │      │
│          │ + Template filters     │   │  + Direct code generation   │      │
│          │ + render_template()    │   │  + No template overhead     │      │
│          └────────────────────────┘   └─────────────────────────────┘      │
│                       ▲                               ▲                      │
│                       │ Uses                          │ Uses                 │
│        ┌──────────────┴──────────────┐ ┌─────────────┴─────────────┐       │
│        │                             │ │                            │        │
│   ┌────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│   │ Claude Code    │  │    Cursor       │  │   OpenAI Codex          │    │
│   │ Generator      │  │   Generator     │  │   Generator             │    │
│   │                │  │                 │  │                         │    │
│   │ Output:        │  │ Output:         │  │ Output:                 │    │
│   │ .claude/       │  │ .cursorrules    │  │ .openai/                │    │
│   │   agents/*.md  │  │ (single file)   │  │   config.json           │    │
│   │   CLAUDE.md    │  │                 │  │   prompts/              │    │
│   └────────────────┘  └─────────────────┘  └─────────────────────────┘    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────┐
│   Request   │  apm generate config --provider claude-code
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Load Data from Database                            │
│                                                              │
│  DatabaseService.connect()                                  │
│    → SELECT * FROM agents WHERE project_id=? AND active=1   │
│    → SELECT * FROM rules WHERE project_id=? AND enabled=1   │
│    → SELECT * FROM projects WHERE id=?                      │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Build GenerationContext                            │
│                                                              │
│  GenerationContext(                                         │
│    agents=[Agent(...), Agent(...)],                        │
│    project_rules=[Rule(...), Rule(...)],                   │
│    universal_context=UniversalContext(                     │
│      project=Project(...),                                  │
│      tech_stack=['python', 'react'],                       │
│      frameworks=['fastapi', 'pytest']                       │
│    ),                                                       │
│    provider_config=ProviderConfig(...)                     │
│  )                                                          │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Validate Configuration                             │
│                                                              │
│  generator.validate_config(context)                         │
│    → Validate agents (required fields, format)              │
│    → Validate rules (enforcement levels, categories)        │
│    → Provider-specific checks                               │
│                                                              │
│  Returns: (is_valid=True, errors=[])                        │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Format Context for Templates                       │
│                                                              │
│  generator.format_context(context)                          │
│    → Group agents by tier                                   │
│    → Group rules by category                                │
│    → Extract behavioral rules                               │
│    → Build template variables                               │
│                                                              │
│  Returns: {                                                 │
│    'agents_by_tier': {...},                                │
│    'rules_by_category': {...},                             │
│    'project': {...},                                        │
│    ...                                                      │
│  }                                                          │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Generate Files                                     │
│                                                              │
│  generator.generate_from_agents(context)                    │
│                                                              │
│  For each agent:                                            │
│    1. Render template(agent_file.md.j2, context)           │
│    2. Generate SHA-256 hash                                 │
│    3. Create FileOutput(path, content, hash)               │
│                                                              │
│  Returns: GenerationResult(                                 │
│    files=[                                                  │
│      FileOutput(                                            │
│        path='.claude/agents/python-dev.md',                │
│        content='# Python Developer...',                     │
│        content_hash='a1b2c3...'                            │
│      ),                                                     │
│      ...                                                    │
│    ],                                                       │
│    success=True                                             │
│  )                                                          │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Write Files to Disk                                │
│                                                              │
│  For each FileOutput:                                       │
│    1. Create parent directories                             │
│    2. Write content to path                                 │
│    3. Verify file hash                                      │
│                                                              │
│  Output:                                                    │
│    .claude/agents/orchestrator-definition.md               │
│    .claude/agents/specialist-python.md                     │
│    .claude/agents/utility-context.md                       │
│    .claude/CLAUDE.md                                        │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Success   │  Generated 4 files (12,345 bytes)
└─────────────┘
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Component Interaction Flow                        │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   CLI        │  apm generate config --provider claude-code
└──────┬───────┘
       │
       │ 1. Create service
       ▼
┌─────────────────────────────────────────────┐
│  ProviderGenerationService                  │
│                                             │
│  __init__(db_service: DatabaseService)      │
└──────┬──────────────────────────────────────┘
       │
       │ 2. Load data
       ▼
┌─────────────────────────────────────────────┐
│  DatabaseService                            │
│                                             │
│  Methods:                                   │
│    - agent_methods.list_agents()           │
│    - rule_methods.list_rules()             │
│    - project_methods.get_project()         │
└──────┬──────────────────────────────────────┘
       │
       │ 3. Build context
       ▼
┌─────────────────────────────────────────────┐
│  GenerationContext                          │
│                                             │
│  Contains:                                  │
│    - agents: List[Agent]                   │
│    - rules: List[Rule]                     │
│    - universal_context: UniversalContext   │
│    - provider_config: ProviderConfig       │
└──────┬──────────────────────────────────────┘
       │
       │ 4. Generate
       ▼
┌─────────────────────────────────────────────┐
│  ClaudeCodeGenerator                        │
│  (extends BaseProviderGenerator)            │
│                                             │
│  Methods:                                   │
│    1. validate_config()                    │
│    2. format_context()                     │
│    3. render_template()                    │
│    4. get_output_paths()                   │
│    5. write_file()                         │
└──────┬──────────────────────────────────────┘
       │
       │ 5. Return result
       ▼
┌─────────────────────────────────────────────┐
│  GenerationResult                           │
│                                             │
│  Contains:                                  │
│    - files: List[FileOutput]               │
│    - success: bool                          │
│    - errors: List[str]                     │
│    - statistics: Dict                       │
└─────────────────────────────────────────────┘
```

## Template Rendering Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Template Rendering Architecture                 │
└─────────────────────────────────────────────────────────────┘

Template File (agent_file.md.j2):
┌─────────────────────────────────────────────────────────────┐
│ # {{ agent.display_name }}                                  │
│                                                              │
│ **Role:** {{ agent.role }}                                  │
│ **Tier:** {{ agent.tier.value }}                           │
│                                                              │
│ ## Description                                              │
│ {{ agent.description }}                                     │
│                                                              │
│ ## Capabilities                                             │
│ {% for capability in agent.capabilities %}                  │
│ - {{ capability }}                                          │
│ {% endfor %}                                                │
│                                                              │
│ ## Project Rules                                            │
│ {% for category, rules in rules_by_category.items() %}     │
│ ### {{ category|title }}                                    │
│ {% for rule in rules %}                                     │
│ - **{{ rule.rule_id }}**: {{ rule.name }}                  │
│   ({{ rule.enforcement_level.value }})                     │
│ {% endfor %}                                                │
│ {% endfor %}                                                │
│                                                              │
│ ## Standard Operating Procedure                             │
│ {{ agent.sop_content }}                                     │
└─────────────────────────────────────────────────────────────┘
                          ▼
                    Jinja2 Renderer
                          ▼
Generated Output (.claude/agents/python-dev.md):
┌─────────────────────────────────────────────────────────────┐
│ # Python Developer                                          │
│                                                              │
│ **Role:** aipm-python-cli-developer                        │
│ **Tier:** specialist                                        │
│                                                              │
│ ## Description                                              │
│ Implements Python CLI commands following three-layer        │
│ architecture pattern.                                        │
│                                                              │
│ ## Capabilities                                             │
│ - Python development (3.10+)                                │
│ - CLI command implementation                                │
│ - Database operations                                       │
│ - Test-driven development                                   │
│                                                              │
│ ## Project Rules                                            │
│ ### Development Principles                                  │
│ - **DP-001**: time-boxing-implementation (BLOCK)           │
│ - **DP-002**: hexagonal-architecture (BLOCK)               │
│                                                              │
│ ### Testing Standards                                       │
│ - **TES-001**: test-coverage-90-percent (LIMIT)            │
│ - **TES-002**: aaa-pattern-required (BLOCK)                │
│                                                              │
│ ## Standard Operating Procedure                             │
│ 1. Read task requirements                                   │
│ 2. Create Pydantic models                                   │
│ 3. Implement database adapters                              │
│ 4. Write business logic methods                             │
│ 5. Create tests (AAA pattern)                               │
│ 6. Document with docstrings                                 │
└─────────────────────────────────────────────────────────────┘
                          ▼
                 SHA-256 Hashing
                          ▼
                    FileOutput
┌─────────────────────────────────────────────────────────────┐
│ path: .claude/agents/python-dev.md                          │
│ content: "# Python Developer\n\n**Role:**..."              │
│ content_hash: "a1b2c3d4e5f6..."                            │
│ size_bytes: 1234                                            │
└─────────────────────────────────────────────────────────────┘
```

## Provider Comparison Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Provider Feature Matrix                           │
├────────────────┬──────────────┬──────────────┬─────────────────────────┤
│   Feature      │ Claude Code  │   Cursor     │   OpenAI Codex          │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Output Format  │ Directory    │ Single File  │ Multi-File              │
│                │ (.claude/)   │ (.cursorrules│ (.openai/)              │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Agent Files    │ ✅ Multiple  │ ❌ N/A       │ ✅ Multiple             │
│                │ .md files    │              │ .json files             │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Slash Commands │ ✅ Yes       │ ❌ No        │ ✅ Yes                  │
│                │ (.claude/    │              │ (custom format)         │
│                │  commands/)  │              │                         │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Hooks          │ ✅ Yes       │ ❌ No        │ ⚠️  Limited             │
│                │ (Python)     │              │ (webhooks only)         │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Memory         │ ✅ Yes       │ ❌ No        │ ✅ Yes                  │
│                │ (.claude/    │              │ (conversation history)  │
│                │  memory/)    │              │                         │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Subagents      │ ✅ Yes       │ ❌ No        │ ⚠️  Assistants API      │
│                │ (Task tool)  │              │                         │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Custom Tools   │ ✅ Yes       │ ❌ No        │ ✅ Yes                  │
│                │ (Python)     │              │ (Function calling)      │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Context Files  │ ✅ Yes       │ ⚠️  Inline   │ ✅ Yes                  │
│                │ (CLAUDE.md)  │ (in rules)   │ (system prompts)        │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Template       │ Jinja2       │ Jinja2       │ JSON Schema             │
│ Engine         │              │              │ (programmatic)          │
├────────────────┼──────────────┼──────────────┼─────────────────────────┤
│ Validation     │ SHA-256      │ SHA-256      │ JSON Schema             │
│                │ + structure  │ + syntax     │ validation              │
└────────────────┴──────────────┴──────────────┴─────────────────────────┘

Legend:
  ✅ Full support
  ⚠️  Partial support
  ❌ Not supported
```

## Error Handling Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   Error Handling Strategy                     │
└──────────────────────────────────────────────────────────────┘

Generation Request
       │
       ▼
┌──────────────────────────────┐
│  Validation Phase            │
│                              │
│  ❌ Invalid agent role       │ ──▶ ValidationError
│  ❌ Missing required fields  │ ──▶ ValidationError
│  ❌ Invalid rule format      │ ──▶ ValidationError
└──────────────────────────────┘
       │ ✅ Validation passed
       ▼
┌──────────────────────────────┐
│  Template Rendering Phase    │
│                              │
│  ❌ Template not found       │ ──▶ TemplateNotFoundError
│  ❌ Syntax error in template │ ──▶ TemplateSyntaxError
│  ❌ Missing variable         │ ──▶ UndefinedError
└──────────────────────────────┘
       │ ✅ Rendering succeeded
       ▼
┌──────────────────────────────┐
│  File Writing Phase          │
│                              │
│  ❌ Permission denied        │ ──▶ PermissionError
│  ❌ Disk full                │ ──▶ OSError
│  ❌ Invalid path             │ ──▶ FileNotFoundError
└──────────────────────────────┘
       │ ✅ Files written
       ▼
┌──────────────────────────────┐
│  Verification Phase          │
│                              │
│  ❌ Hash mismatch            │ ──▶ IntegrityError
│  ❌ File size mismatch       │ ──▶ IntegrityError
└──────────────────────────────┘
       │ ✅ Verification passed
       ▼
    Success!

All errors are captured in GenerationResult:
┌─────────────────────────────────────────────────┐
│ GenerationResult(                               │
│   success=False,                                │
│   errors=[                                      │
│     "Validation failed: Agent role required",  │
│     "Template error: variable 'foo' undefined" │
│   ],                                            │
│   validation_errors=[...],                      │
│   validation_warnings=[...]                     │
│ )                                               │
└─────────────────────────────────────────────────┘
```

## Extension Points

```
┌──────────────────────────────────────────────────────────────┐
│              How to Add a New Provider                        │
└──────────────────────────────────────────────────────────────┘

Step 1: Create provider configuration
┌─────────────────────────────────────────────────────────────┐
│ config = ProviderConfig(                                    │
│     name="my-provider",                                     │
│     display_name="My Provider",                            │
│     output_format=OutputFormat.DIRECTORY,                  │
│     config_directory=Path(".myprovider"),                  │
│     supported_features=[...]                                │
│ )                                                           │
└─────────────────────────────────────────────────────────────┘

Step 2: Extend BaseProviderGenerator
┌─────────────────────────────────────────────────────────────┐
│ class MyProviderGenerator(BaseProviderGenerator):          │
│                                                             │
│     def generate_from_agents(self, context):               │
│         # Implement generation logic                       │
│         ...                                                 │
│                                                             │
│     def validate_config(self, context):                    │
│         # Implement validation                             │
│         ...                                                 │
│                                                             │
│     def format_context(self, context):                     │
│         # Transform context for templates                  │
│         ...                                                 │
│                                                             │
│     def get_output_paths(self, context):                   │
│         # Determine file paths                             │
│         ...                                                 │
└─────────────────────────────────────────────────────────────┘

Step 3: Create templates (optional)
┌─────────────────────────────────────────────────────────────┐
│ templates/                                                  │
│   my_provider_config.j2                                    │
│   my_provider_agent.j2                                     │
└─────────────────────────────────────────────────────────────┘

Step 4: Register with CLI
┌─────────────────────────────────────────────────────────────┐
│ @click.command()                                            │
│ @click.option('--provider', type=click.Choice([            │
│     'claude-code', 'cursor', 'openai', 'my-provider'       │
│ ]))                                                         │
│ def generate_config(provider):                             │
│     if provider == 'my-provider':                          │
│         generator = MyProviderGenerator()                  │
│     ...                                                     │
└─────────────────────────────────────────────────────────────┘

Step 5: Test
┌─────────────────────────────────────────────────────────────┐
│ apm generate config --provider my-provider                  │
└─────────────────────────────────────────────────────────────┘
```

## Summary

This architecture provides:

1. **Modularity** - Clean separation between providers
2. **Extensibility** - Easy to add new providers
3. **Validation** - Multiple layers of validation
4. **Integrity** - SHA-256 hashing for verification
5. **Flexibility** - Template-based or programmatic
6. **Type Safety** - Full Pydantic models
7. **Error Handling** - Comprehensive error capture
8. **Database Integration** - Direct connection to AgentPM DB

The design follows SOLID principles and provides a clear path for implementing Claude Code, Cursor, and OpenAI Codex generators from a unified source.
