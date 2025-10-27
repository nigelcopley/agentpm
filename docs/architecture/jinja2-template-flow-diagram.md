# Jinja2 Template Architecture - Flow Diagrams

Visual representations of the template architecture data flow and component interactions.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐          │
│  │Projects │  │ Agents  │  │  Rules  │  │Providers │          │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘          │
└───────┼───────────┼───────────┼─────────────┼────────────────┘
        │           │           │             │
        └───────────┴───────────┴─────────────┘
                    │
        ┌───────────▼────────────┐
        │   Context Builder      │
        │   (Pydantic Models)    │
        │                        │
        │  - ProjectContext      │
        │  - AgentContext        │
        │  - RuleContext         │
        │  - ProviderConfig      │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  TemplateContext       │
        │  (Validated)           │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │  TemplateRenderer      │
        │                        │
        │  - Load Templates      │
        │  - Apply Filters       │
        │  - Execute Macros      │
        │  - Render Output       │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │    RenderResult        │
        │                        │
        │  - Success/Errors      │
        │  - Rendered Content    │
        │  - Warnings            │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │   Provider Layer       │
        │                        │
        │  .claude/              │
        │  .cursor/              │
        │  config.toml           │
        └────────────────────────┘
```

---

## 2. Context Building Flow

```
┌─────────────────┐
│ Provider.install│
│    (called)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ _load_project_context(project_path) │
└────────┬────────────────────────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌─────────────────┐              ┌──────────────────┐
│ Query Database  │              │ Build Pydantic   │
│                 │              │ Models           │
│ SELECT * FROM   │──────────────▶                  │
│ - projects      │              │ ProjectContext   │
│ - agents        │              │ AgentContext[]   │
│ - rules         │              │ RuleContext[]    │
│ - providers     │              │ ProviderConfig   │
└─────────────────┘              └────────┬─────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Pydantic        │
                                 │ Validation      │
                                 │                 │
                                 │ - Type checking │
                                 │ - Field rules   │
                                 │ - Cross-field   │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ TemplateContext │
                                 │ (Validated)     │
                                 └─────────────────┘
```

---

## 3. Template Rendering Flow

```
┌──────────────────┐
│ TemplateContext  │
│ (Input)          │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│ renderer.render(template, ctx)   │
└────────┬─────────────────────────┘
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌──────────────────┐            ┌────────────────────┐
│ Get Template     │            │ Check Cache        │
│                  │            │                    │
│ Load from:       │            │ LRU Cache          │
│ - File system    │◀───────────│ (compiled)         │
│ - Cache (if hit) │            │                    │
└────────┬─────────┘            └────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Compile Template (if needed) │
│                              │
│ - Parse Jinja2 syntax        │
│ - Build AST                  │
│ - Optimize                   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Render with Context          │
│                              │
│ 1. Variable substitution     │
│ 2. Apply filters             │
│ 3. Execute macros            │
│ 4. Evaluate conditions       │
│ 5. Iterate loops             │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Auto-Escape (Security)       │
│                              │
│ - HTML/XML entities          │
│ - Shell commands             │
│ - TOML strings               │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Validate Output              │
│                              │
│ - Check for empty            │
│ - Check for unrendered tags  │
│ - Check for placeholders     │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Security Checks              │
│                              │
│ - Shell injection patterns   │
│ - Secret exposure patterns   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────┐
│ RenderResult     │
│                  │
│ - success: bool  │
│ - content: str   │
│ - errors: []     │
│ - warnings: []   │
└──────────────────┘
```

---

## 4. Filter Application Flow

```
┌────────────────────────────┐
│ Template Variable          │
│ {{ agents | filter }}      │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Jinja2 Filter Pipeline     │
└──────────┬─────────────────┘
           │
           ├────────────────────────────┐
           │                            │
           ▼                            ▼
┌────────────────────┐      ┌────────────────────┐
│ Built-in Filters   │      │ Custom Filters     │
│                    │      │                    │
│ - join             │      │ - flatten_agents   │
│ - length           │      │ - filter_by_tier   │
│ - default          │      │ - filter_rules     │
│ - capitalize       │      │ - to_toml          │
└────────────────────┘      │ - escape_shell     │
                            └────────┬───────────┘
                                     │
                                     ▼
                            ┌─────────────────────┐
                            │ Filter Function     │
                            │                     │
                            │ def filter_by_tier( │
                            │   agents, tier      │
                            │ ):                  │
                            │   return [a for a   │
                            │     if tier == t]   │
                            └────────┬────────────┘
                                     │
                                     ▼
                            ┌─────────────────────┐
                            │ Filtered Data       │
                            │ (List[Agent])       │
                            └─────────────────────┘
```

---

## 5. Macro Execution Flow

```
┌────────────────────────────┐
│ Template Macro Call        │
│ {{ agent_macros.header() }}│
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Load Macro File            │
│ {% import "macros/..." %}  │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Macro Definition           │
│                            │
│ {% macro header(agent) %}  │
│   # {{ agent.name }}       │
│   ...                      │
│ {% endmacro %}             │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Macro Execution            │
│                            │
│ 1. Bind parameters         │
│ 2. Execute template block  │
│ 3. Apply filters           │
│ 4. Return rendered text    │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Inline Rendered Content    │
└────────────────────────────┘
```

---

## 6. Provider Installation Flow

```
┌────────────────────┐
│ provider.install() │
└─────────┬──────────┘
          │
          ▼
┌──────────────────────────────┐
│ 1. Load Context              │
│    _load_project_context()   │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ 2. Apply Config Overrides    │
│    Update provider settings  │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ 3. Render All Configs        │
│    render_configs(context)   │
│                              │
│    ┌─────────────────────┐  │
│    │ claude_md.j2        │  │
│    │ agent.j2            │  │
│    │ settings.j2         │  │
│    │ hooks/*.j2          │  │
│    └─────────────────────┘  │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────────────┐
│ 4. Validate Results          │
│    Check success/errors      │
└─────────┬────────────────────┘
          │
          ├────── Success ──────┐
          │                     │
          ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ 5. Write Files   │  │ Log Errors       │
│                  │  │ Return False     │
│ .provider/       │  └──────────────────┘
│   config.md      │
│   agents.md      │
│   rules.md       │
└─────────┬────────┘
          │
          ▼
┌──────────────────────────────┐
│ 6. Record in Database        │
│    provider_installations    │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────┐
│ Return True      │
└──────────────────┘
```

---

## 7. Template Inheritance Flow

```
┌──────────────────────────────┐
│ Child Template               │
│ (cursor/templates/rules.j2)  │
│                              │
│ {% extends "common/base.j2" %}
│                              │
│ {% block content %}          │
│   ...child content...        │
│ {% endblock %}               │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Load Base Template           │
│ (common/base.j2)             │
│                              │
│ {% block header %}           │
│   # Default Header           │
│ {% endblock %}               │
│                              │
│ {% block content %}          │
│   {# Empty, override me #}   │
│ {% endblock %}               │
│                              │
│ {% block footer %}           │
│   ---                        │
│   Generated by APM (Agent Project Manager)          │
│ {% endblock %}               │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Merge Templates              │
│                              │
│ 1. Start with base structure │
│ 2. Override child blocks     │
│ 3. Keep non-overridden blocks│
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Rendered Output              │
│                              │
│ # Default Header             │
│                              │
│ ...child content...          │
│                              │
│ ---                          │
│ Generated by APM (Agent Project Manager)            │
└──────────────────────────────┘
```

---

## 8. Multi-Provider Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SHARED LAYER                         │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Base Models  │  │  Renderer    │  │Common Macros │ │
│  │  (Pydantic)  │  │  (Cached)    │  │  (Jinja2)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │          Custom Filters (Shared)               │   │
│  │  agent_filters | rule_filters | format_filters │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌────────────┐ ┌──────────────┐
│ Claude Code   │ │  Cursor    │ │ OpenAI Codex │
│  Provider     │ │  Provider  │ │   Provider   │
├───────────────┤ ├────────────┤ ├──────────────┤
│ Templates:    │ │ Templates: │ │ Templates:   │
│               │ │            │ │              │
│ claude_md.j2  │ │.cursorrules│ │ agents_md.j2 │
│ agent.j2      │ │.cursorign. │ │ config.toml  │
│ settings.j2   │ │ modes/*.j2 │ │              │
│ hooks/*.j2    │ │ rules/*.j2 │ │              │
└───────┬───────┘ └─────┬──────┘ └──────┬───────┘
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌────────────┐ ┌──────────────┐
│ .claude/      │ │ .cursor/   │ │ config.toml  │
│   CLAUDE.md   │ │ .cursorrules│ │              │
│   agents/*.md │ │ .cursorign.│ │              │
│   settings.js.│ │ modes/*.mdc│ │              │
│   hooks/*.py  │ │ rules/*.mdc│ │              │
└───────────────┘ └────────────┘ └──────────────┘
```

---

## 9. Error Handling Flow

```
┌──────────────────┐
│ render_template()│
└────────┬─────────┘
         │
         ├─────────── Try ─────────┐
         │                         │
         ▼                         │
┌─────────────────┐               │
│ Load Template   │               │
└────────┬────────┘               │
         │                         │
         ▼                         │
┌─────────────────┐               │
│ Validate Context│               │
└────────┬────────┘               │
         │                         │
         ▼                         │
┌─────────────────┐               │
│ Render          │               │
└────────┬────────┘               │
         │                         │
         ▼                         │
┌─────────────────┐               │
│ Validate Output │               │
└────────┬────────┘               │
         │                         │
         ▼                         │
┌─────────────────┐               │
│ Security Check  │               │
└────────┬────────┘               │
         │                         │
         ├────── Catch ────────────┘
         │                         │
         ▼                         ▼
┌────────────────┐      ┌──────────────────┐
│ Success        │      │ Error Handling   │
│                │      │                  │
│ RenderResult(  │      │ - TemplateNotFound
│   success=True │      │ - UndefinedError │
│   content=...  │      │ - SyntaxError    │
│   warnings=[]  │      │ - ValidationError│
│ )              │      │                  │
└────────────────┘      │ RenderResult(    │
                        │   success=False  │
                        │   errors=[...]   │
                        │ )                │
                        └──────────────────┘
```

---

## 10. Caching Strategy

```
┌─────────────────────────┐
│ First render_template() │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Template not in cache   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Load from filesystem            │
│ Parse Jinja2 syntax             │
│ Compile to Python bytecode      │
│ (Expensive operation)           │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Store in LRU Cache              │
│ Key: template_name              │
│ Value: Compiled template object │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Render with context             │
│ (Fast: just variable filling)   │
└─────────────────────────────────┘

┌──────────────────────────┐
│ Subsequent renders       │
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│ Template in cache? ✓    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Retrieve from cache             │
│ (O(1) lookup)                   │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Render with context             │
│ (Fast: skip parsing/compilation)│
└─────────────────────────────────┘

┌─────────────────────────┐
│ Performance Improvement │
├─────────────────────────┤
│ First render:  ~50ms    │
│ Cached render: ~5ms     │
│ Speedup:       10x      │
└─────────────────────────┘
```

---

## Legend

```
┌─────┐
│ Box │  = Process/Component
└─────┘

   │
   ▼     = Data/Control Flow

┌──┬──┐
│  │  │  = Decision Point
└──┴──┘

═════   = Database/Storage
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-27
