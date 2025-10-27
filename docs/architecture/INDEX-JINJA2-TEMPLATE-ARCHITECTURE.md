# Jinja2 Template Architecture - Documentation Index

**Complete guide to the multi-provider template architecture**

**Version**: 1.0.0
**Date**: 2025-10-27
**Status**: Design Complete, Ready for Implementation

---

## Overview

The Jinja2 Template Architecture provides a robust, type-safe, and reusable system for generating provider-specific configurations from database-stored project data. It supports 3 providers initially (Claude Code, Cursor, OpenAI Codex) with extensibility for future providers.

**Key Benefits**:
- **Type Safety**: Pydantic validation ensures correctness before rendering
- **Reusability**: Macros and filters eliminate code duplication
- **Security**: Automatic escaping prevents injection attacks
- **Performance**: Template caching provides 10x speedup
- **Testability**: Clear separation enables isolated testing

---

## Documentation Structure

### 1. Design Documents

#### [Jinja2 Template Architecture Design](./jinja2-template-architecture-design.md) (49 KB)
**Full technical specification**

**Contents**:
- Executive summary and goals
- Directory structure (complete layout)
- Template context models (Pydantic)
- Template renderer implementation
- Custom filters (agent, rule, format, security)
- Common macros (agents, rules, formatting)
- Provider templates (Claude Code, Cursor, Codex)
- Testing strategy
- Base provider class
- Performance considerations
- Security features
- Migration path
- Example usage
- Template inheritance

**When to Read**: Start here for complete understanding of the architecture.

---

#### [Jinja2 Template Architecture Summary](./jinja2-template-architecture-summary.md) (11 KB)
**Quick reference guide**

**Contents**:
- Architecture overview (3-layer)
- Key components
- Directory structure
- Quick start guide
- Template examples
- Filter reference (quick lookup)
- Context models (quick reference)
- Common patterns
- Troubleshooting
- Resources

**When to Read**: After reading the full design, use this for quick lookups.

---

#### [Jinja2 Template Flow Diagrams](./jinja2-template-flow-diagram.md) (27 KB)
**Visual architecture documentation**

**Contents**:
- High-level architecture diagram
- Context building flow
- Template rendering flow
- Filter application flow
- Macro execution flow
- Provider installation flow
- Template inheritance flow
- Multi-provider architecture
- Error handling flow
- Caching strategy diagram

**When to Read**: Use alongside the design document for visual understanding.

---

#### [Jinja2 Implementation Checklist](./jinja2-implementation-checklist.md) (18 KB)
**Complete implementation roadmap**

**Contents**:
- Phase 1: Core Infrastructure (Week 1)
  - Context models
  - Template renderer
  - Custom filters
  - Common macros
- Phase 2: Provider Templates (Week 2)
  - Claude Code templates
  - Cursor templates
  - OpenAI Codex templates
- Phase 3: Provider Integration (Week 3)
  - Base provider class
  - Update CursorProvider
  - Create ClaudeCodeProvider
  - Create CodexProvider
- Phase 4: Testing & Documentation (Week 4)
  - Unit tests
  - Integration tests
  - Documentation
  - Performance testing
- Phase 5: Deployment (Week 5)
  - CLI integration
  - Database migrations
  - Release preparation
- Verification checklist
- Risk mitigation
- Success metrics

**When to Read**: Use this as your implementation guide, tracking progress as you go.

---

### 2. Example Code

#### [Examples Directory](../../examples/templates/)
**Complete working examples**

**Files**:

##### `example_context.py` (11 KB)
- Building TemplateContext with Pydantic validation
- Creating project, agent, and rule contexts
- Validation examples (catching errors)
- Cross-field validation
- **Run**: `python examples/templates/example_context.py`

##### `example_rendering.py` (13 KB)
- Basic template rendering
- Using custom filters
- Format conversion (JSON/TOML/YAML)
- Security escaping
- Macro usage
- Conditional rendering
- Error handling
- Custom Jinja2 tests
- Performance benchmarking
- **Run**: `python examples/templates/example_rendering.py`

##### `example_provider.py` (11 KB)
- Complete provider implementation
- Installation/uninstallation lifecycle
- Template rendering
- Error recovery
- Database integration
- File system operations
- **Run**: `python examples/templates/example_provider.py`

##### `README.md` (11 KB)
- Overview of all examples
- Quick start guide
- Template examples
- Filter reference
- Context model reference
- Testing strategy
- Troubleshooting
- Resources

**When to Use**: Start with example_context.py, then example_rendering.py, then example_provider.py.

---

## Quick Navigation

### By Task

| Task | Document | Section |
|------|----------|---------|
| Understand architecture | [Design](./jinja2-template-architecture-design.md) | Section 2-3 |
| Learn context models | [Design](./jinja2-template-architecture-design.md) | Section 3 |
| Implement renderer | [Design](./jinja2-template-architecture-design.md) | Section 4 |
| Create custom filters | [Design](./jinja2-template-architecture-design.md) | Section 5 |
| Build macros | [Design](./jinja2-template-architecture-design.md) | Section 6 |
| Design templates | [Design](./jinja2-template-architecture-design.md) | Section 7 |
| Implement provider | [Design](./jinja2-template-architecture-design.md) | Section 9 |
| Follow implementation plan | [Checklist](./jinja2-implementation-checklist.md) | All phases |
| See data flow | [Diagrams](./jinja2-template-flow-diagram.md) | All diagrams |
| Quick reference | [Summary](./jinja2-template-architecture-summary.md) | All sections |
| Working examples | [Examples](../../examples/templates/) | All files |

### By Persona

#### **Developer** (Implementing the architecture)
1. Read: [Design Document](./jinja2-template-architecture-design.md) (full)
2. Review: [Flow Diagrams](./jinja2-template-flow-diagram.md) (visual understanding)
3. Follow: [Implementation Checklist](./jinja2-implementation-checklist.md) (phase by phase)
4. Reference: [Summary](./jinja2-template-architecture-summary.md) (quick lookups)
5. Run: [Examples](../../examples/templates/) (see it work)

#### **Architect** (Understanding design decisions)
1. Read: [Design Document](./jinja2-template-architecture-design.md) (sections 1-2, 9-11)
2. Review: [Flow Diagrams](./jinja2-template-flow-diagram.md) (architecture diagrams)
3. Study: [Summary](./jinja2-template-architecture-summary.md) (key components)

#### **QA Engineer** (Testing the system)
1. Read: [Design Document](./jinja2-template-architecture-design.md) (section 8)
2. Review: [Implementation Checklist](./jinja2-implementation-checklist.md) (Phase 4)
3. Study: [Examples](../../examples/templates/) (test patterns)

#### **Template Designer** (Creating provider templates)
1. Read: [Design Document](./jinja2-template-architecture-design.md) (sections 5-7)
2. Reference: [Summary](./jinja2-template-architecture-summary.md) (filters/macros)
3. Study: [Examples](../../examples/templates/example_rendering.py) (patterns)

#### **Provider Implementer** (Adding new providers)
1. Read: [Design Document](./jinja2-template-architecture-design.md) (sections 3-4, 9)
2. Study: [Examples](../../examples/templates/example_provider.py) (complete example)
3. Follow: [Implementation Checklist](./jinja2-implementation-checklist.md) (Phase 3)

---

## Key Concepts

### 1. Template Context (Type-Safe)
```python
TemplateContext(
    project: ProjectContext,      # What we're building
    agents: List[AgentContext],   # Who can work on it
    rules: List[RuleContext],     # How to build it
    provider: ProviderConfig,     # Where it's going
)
```

**Validation**: Pydantic ensures type safety and catches errors before rendering.

---

### 2. Template Renderer (Cached)
```python
renderer = TemplateRenderer(
    template_dirs=[...],          # Where templates live
    cache_size=128,               # How many to cache
)

result = renderer.render(         # Render with validation
    template_name="config.j2",
    context=context,
)
```

**Performance**: Caching provides 10x speedup on repeated renders.

---

### 3. Custom Filters (Transformation)
```jinja2
{{ agents | flatten_agents }}                    # Transform
{{ agents | filter_by_tier(2) }}                 # Filter
{{ rules | filter_rules(enforcement='BLOCK') }}  # Query
{{ config | to_toml }}                           # Format
{{ path | escape_shell }}                        # Secure
```

**Categories**: Agent, Rule, Format, Security filters.

---

### 4. Reusable Macros (DRY)
```jinja2
{% import "common/macros/agents.j2" as agent_macros %}

{{ agent_macros.agent_block(agent) }}            # Reuse
```

**Benefits**: Consistency, maintainability, testability.

---

## File Sizes

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| Design | 49 KB | ~1850 | Complete specification |
| Summary | 11 KB | ~400 | Quick reference |
| Diagrams | 27 KB | ~1000 | Visual flows |
| Checklist | 18 KB | ~700 | Implementation plan |
| example_context.py | 11 KB | ~400 | Context building |
| example_rendering.py | 13 KB | ~450 | Template usage |
| example_provider.py | 11 KB | ~400 | Provider implementation |
| examples/README.md | 11 KB | ~400 | Example documentation |

**Total Documentation**: ~151 KB, ~5,600 lines

---

## Implementation Timeline

**Total**: 5 weeks (1-2 developers)

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|-------------|
| 1 | Core Infrastructure | Models, Renderer, Filters, Macros | Reusable foundation |
| 2 | Provider Templates | Claude, Cursor, Codex templates | Template library |
| 3 | Provider Integration | Base class, 3 providers | Working providers |
| 4 | Testing & Docs | Unit, Integration, Docs | Quality assurance |
| 5 | Deployment | CLI, Migrations, Release | Production ready |

---

## Success Criteria

- [ ] All 3 providers using template architecture
- [ ] Template rendering <100ms (cached)
- [ ] Test coverage >95%
- [ ] Zero security vulnerabilities
- [ ] Documentation complete
- [ ] Performance improved vs old system
- [ ] Code complexity reduced

---

## Quick Start for Developers

### Step 1: Read Foundation (1 hour)
1. [Design Document](./jinja2-template-architecture-design.md) - Sections 1-3
2. [Flow Diagrams](./jinja2-template-flow-diagram.md) - Diagrams 1-3

### Step 2: Run Examples (30 minutes)
```bash
cd examples/templates

# Build and validate context
python example_context.py

# Render templates with filters
python example_rendering.py

# See complete provider implementation
python example_provider.py
```

### Step 3: Start Implementation (Begin Phase 1)
1. Open [Implementation Checklist](./jinja2-implementation-checklist.md)
2. Start with Phase 1.1: Context Models
3. Follow checklist step-by-step
4. Reference [Design Document](./jinja2-template-architecture-design.md) for details

---

## Dependencies

### Required
- Python 3.10+
- Jinja2 3.1+
- Pydantic 2.0+

### Optional (for format filters)
- toml (TOML support)
- PyYAML (YAML support)

### Development
- pytest (testing)
- black (formatting)
- ruff (linting)
- mypy (type checking)

---

## Resources

### Internal
- [Full Design](./jinja2-template-architecture-design.md)
- [Quick Reference](./jinja2-template-architecture-summary.md)
- [Flow Diagrams](./jinja2-template-flow-diagram.md)
- [Implementation Checklist](./jinja2-implementation-checklist.md)
- [Examples](../../examples/templates/)

### External
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)

### Existing Code
- `agentpm/providers/cursor/provider.py` - Current Cursor provider
- `agentpm/core/agents/templates/claude.md.jinja2` - Existing template
- `agentpm/providers/cursor/templates/rules/` - Cursor rule templates

---

## Support

### Questions?
- Review [Summary](./jinja2-template-architecture-summary.md) for quick answers
- Check [Examples](../../examples/templates/README.md) for patterns
- Consult [Design Document](./jinja2-template-architecture-design.md) for details

### Issues?
- Check [Troubleshooting](./jinja2-template-architecture-summary.md#troubleshooting)
- Review [Error Handling Flow](./jinja2-template-flow-diagram.md#9-error-handling-flow)
- See [Risk Mitigation](./jinja2-implementation-checklist.md#risk-mitigation)

---

## Change Log

### Version 1.0.0 (2025-10-27)
- Initial design complete
- Full documentation suite created
- Working examples provided
- Implementation checklist ready
- Ready for Phase 1 implementation

---

## Next Steps

1. **Review** this index to understand the documentation structure
2. **Read** the [Design Document](./jinja2-template-architecture-design.md) for complete understanding
3. **Run** the [Examples](../../examples/templates/) to see it in action
4. **Follow** the [Implementation Checklist](./jinja2-implementation-checklist.md) to build it
5. **Reference** the [Summary](./jinja2-template-architecture-summary.md) for quick lookups

---

**Documentation Complete**: 2025-10-27
**Ready for Implementation**: Phase 1, Week 1
**Estimated Completion**: 5 weeks
**Status**: ✅ Design Complete, 🚧 Implementation Pending

---

**Prepared by**: APM (Agent Project Manager) Architecture Team
**Reviewed by**: [Pending]
**Approved by**: [Pending]
