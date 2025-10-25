# ADR-001: Provider Abstraction Architecture

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable AIPM to work with any AI coding assistant (Claude Code, Cursor, Aider, Codex, Gemini)

---

## Context

AIPM needs to support multiple AI coding assistant providers (Claude Code, Cursor, Aider, GitHub Copilot, Google Gemini, and future providers). Each provider has different:

- **Context injection mechanisms** (hooks, config files, command-line args)
- **Session identification** (workspace detection, active files, task tracking)
- **Hook systems** (Python scripts, TypeScript, YAML config, command-line)
- **Context formats** (Markdown, JSON, structured data)

We need a provider-agnostic core that can work with ANY provider through a thin adapter layer.

### Current State
- AIPM core is tightly coupled to Claude Code
- Context assembly assumes CLAUDE.md format
- Session hooks are Python-specific
- No way to support other providers without rewriting core

### Requirements
1. **Provider Agnosticism**: Core logic must work with any AI provider
2. **Easy Provider Addition**: New providers via adapter, not core changes
3. **Consistent Experience**: Same AIPM functionality regardless of provider
4. **Provider-Specific Optimizations**: Adapters can leverage provider strengths
5. **Graceful Degradation**: Core features work even with limited provider support

---

## Decision

We will implement a **Provider Abstraction Layer** with the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                   AIPM Core (Provider-Agnostic)             │
│                                                             │
│  • Context Assembly (hierarchical, compressed)             │
│  • Session Management (lifecycle, learning)                │
│  • Work Management (work items, tasks, workflows)          │
│  • Quality Gates (CI-001 through CI-006)                   │
│  • Audit System (decisions, evidence, compliance)          │
│  • Agent Orchestration (sub-agents, delegation)            │
│                                                             │
│  Core operates through ProviderAdapter interface           │
│  No direct knowledge of specific providers                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ ProviderAdapter Interface
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
┌───▼────┐  ┌────▼───┐  ┌──────▼──┐  ┌──────▼──┐
│ Claude │  │ Cursor │  │  Aider  │  │  Codex  │
│  Code  │  │        │  │         │  │ /Gemini │
│ Adapter│  │ Adapter│  │ Adapter │  │ Adapter │
└────────┘  └────────┘  └─────────┘  └─────────┘
    │            │           │            │
┌───▼────┐  ┌───▼────┐  ┌──▼─────┐  ┌──▼──────┐
│.claude/│  │.cursor/│  │.aider/ │  │ Config  │
│ hooks  │  │ hooks  │  │ config │  │  Files  │
└────────┘  └────────┘  └────────┘  └─────────┘
```

### Provider Adapter Interface

```python
class ProviderAdapter(ABC):
    """
    Abstract base class for AI provider integrations.

    Each provider implements this interface to enable AIPM integration.
    Core AIPM code only interacts through this interface.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Unique identifier for this provider.

        Examples: 'claude-code', 'cursor', 'aider', 'codex'
        """

    @abstractmethod
    def get_session_context(self) -> SessionContext:
        """
        Identify current session context from provider.

        Returns:
            SessionContext with:
            - project_path: Path to project root
            - active_files: Currently open/edited files
            - active_task_hint: Task identifier (if provider supports)
            - session_id: Provider's session identifier
            - metadata: Provider-specific additional context
        """

    @abstractmethod
    def inject_context(
        self,
        context: UniversalContext,
        format: ContextFormat
    ) -> str:
        """
        Inject AIPM context into provider.

        Args:
            context: Universal context from AIPM core
            format: Requested format (markdown, json, structured)

        Returns:
            Formatted context string for provider
        """

    @abstractmethod
    def capture_session_learning(self) -> SessionLearning:
        """
        Capture what was learned during session.

        Returns:
            SessionLearning with:
            - decisions: Decisions made
            - patterns: Patterns discovered
            - code_changes: Files modified
            - evidence: Sources referenced
            - duration: Session duration
        """

    @abstractmethod
    def register_hooks(self) -> HookRegistration:
        """
        Register session lifecycle hooks.

        Returns:
            HookRegistration with:
            - session_start_path: Where to install start hook
            - session_end_path: Where to install end hook
            - continuous_update_path: Real-time update mechanism (optional)
            - hook_format: Script format (python, typescript, bash, yaml)
        """

    @abstractmethod
    def supports_feature(self, feature: ProviderFeature) -> bool:
        """
        Check if provider supports optional feature.

        Features:
            - REAL_TIME_UPDATES: Can update context during session
            - MULTI_FILE_CONTEXT: Supports multiple file context
            - STRUCTURED_OUTPUT: Can handle structured data
            - AGENT_DELEGATION: Supports sub-agent concept
            - SESSION_HISTORY: Maintains session history
        """
```

### Universal Context Format

```python
@dataclass
class UniversalContext:
    """
    Provider-agnostic context format.

    AIPM core produces this format.
    Adapters transform it for specific providers.
    """

    # Core context layers
    project: ProjectContext
    work_item: Optional[WorkItemContext]
    task: Optional[TaskContext]

    # Additional context
    decisions: List[Decision]
    patterns: List[Pattern]
    constraints: List[Constraint]
    agents: List[AgentSOP]

    # Metadata
    confidence: float  # 0.0-1.0
    freshness: datetime
    compression_ratio: float  # Token reduction achieved

    def to_markdown(self) -> str:
        """Format for Claude Code, Aider"""

    def to_json(self) -> Dict[str, Any]:
        """Format for Cursor, Codex"""

    def to_structured(self) -> StructuredContext:
        """Format for custom integrations"""
```

### Context Format Transformation

```python
class ContextFormatter:
    """
    Transforms UniversalContext to provider-specific formats.
    """

    def format_for_claude_code(self, context: UniversalContext) -> str:
        """
        Claude Code format (Markdown with special sections)

        Output:
        # Project Context
        **Tech Stack:** Django 4.2, React 18, PostgreSQL 15

        **Coding Standards:**
        - PEP 8 for Python
        - ESLint for TypeScript

        ## Work Item: Multi-Tenant Platform
        **Objective:** Build tenant isolation system
        **DoD:** All tenants isolated, tests-BAK passing

        ### Task: Tenant Middleware
        **Implementation:** Add TenantMiddleware to settings
        **Pattern:** Use tenant_context() manager
        """

    def format_for_cursor(self, context: UniversalContext) -> Dict[str, Any]:
        """
        Cursor format (JSON for .cursorrules)

        Output:
        {
          "project": {
            "name": "Multi-Tenant Platform",
            "tech_stack": ["Django", "React", "PostgreSQL"],
            "standards": {...}
          },
          "work_item": {
            "id": 5,
            "objective": "Build tenant isolation",
            "patterns": [...]
          },
          "task": {...}
        }
        """

    def format_for_aider(self, context: UniversalContext) -> str:
        """
        Aider format (Markdown for --read file)

        Output:
        PROJECT: Multi-Tenant Platform
        TECH: Django 4.2, React 18

        WORK ITEM: Tenant Isolation System
        TASK: Implement TenantMiddleware
        PATTERN: Use tenant_context() manager
        FILES: middleware/tenant.py, settings.py
        """
```

### Hook System Architecture

Each provider has different hook mechanisms:

#### Claude Code Hooks (Python)

```python
# .claude/hooks/session-start.py
from agentpm.providers import get_provider


def session_start():
    provider = get_provider('claude-code')
    session = provider.start_session()

    context = session.get_context(format='markdown')
    print(context)  # Auto-injected by Claude Code
```

#### Cursor Hooks (TypeScript)
```typescript
// .cursor/hooks/session-start.ts
import { AIPMProvider } from 'aipm-cursor-adapter';

export async function sessionStart() {
    const provider = new AIPMProvider('cursor');
    const session = await provider.startSession();

    const context = await session.getContext({ format: 'json' });
    return context;  // Loaded by Cursor
}
```

#### Aider Hooks (YAML Config)
```yaml
# .aider.conf.yml
hooks:
  session_start:
    command: "apm session start --provider=aider --format=markdown"
    output_to: "/tmp/aipm-context.md"
    inject_with: "--read /tmp/aipm-context.md"
```

---

## Consequences

### Positive

1. **Provider Independence**
   - Core AIPM logic completely decoupled from providers
   - Can support new providers without modifying core
   - Providers can be added/removed without breaking core

2. **Consistent User Experience**
   - Same AIPM commands work across all providers
   - Same context quality regardless of provider
   - Users can switch providers without relearning

3. **Provider-Specific Optimizations**
   - Adapters can leverage provider strengths
   - Example: Cursor's real-time updates, Aider's git integration
   - No "lowest common denominator" compromises

4. **Easy Provider Addition**
   - New provider = implement adapter interface
   - ~500 lines of code per adapter
   - Community can contribute adapters

5. **Graceful Degradation**
   - Optional features detected via `supports_feature()`
   - Core functionality works with minimal provider support
   - Advanced features enhance but not required

### Negative

1. **Adapter Maintenance Burden**
   - Each provider adapter needs maintenance
   - Provider updates may break adapters
   - Need to track provider API changes

2. **Testing Complexity**
   - Must test core with all provider adapters
   - Integration tests for each provider
   - Mock adapters for unit tests

3. **Feature Parity Challenges**
   - Not all providers support all features
   - Need clear documentation of feature support
   - Users may be confused by feature differences

4. **Performance Overhead**
   - Abstraction layer adds minor overhead
   - Context transformation costs
   - Mitigated by caching and optimization

### Mitigation Strategies

1. **Adapter Maintenance**
   - Maintain adapter compatibility matrix
   - Automated testing against provider versions
   - Community adapter ownership program

2. **Testing**
   - Mock adapter for unit tests
   - Docker-based integration tests
   - CI pipeline for all providers

3. **Feature Parity**
   - Clear documentation of feature support
   - Feature detection in CLI (`apm providers check`)
   - Graceful degradation messages

4. **Performance**
   - Cache transformed contexts
   - Lazy loading of provider adapters
   - Benchmark all adapters

---

## Implementation Plan

### Phase 1: Core Interface (Week 1-2)
```yaml
Tasks:
  - Define ProviderAdapter interface
  - Implement UniversalContext format
  - Create ContextFormatter
  - Build provider detection system

Deliverables:
  - agentpm/providers/base.py (ProviderAdapter)
  - agentpm/providers/context.py (UniversalContext)
  - agentpm/providers/formatters.py (ContextFormatter)
  - agentpm/providers/detection.py (provider detection)
```

### Phase 2: Reference Adapter (Week 3-4)
```yaml
Tasks:
  - Implement ClaudeCodeAdapter
  - Create hook templates
  - Test full integration
  - Document adapter development

Deliverables:
  - agentpm/providers/claude_code.py
  - .claude/hooks/session-start.py template
  - .claude/hooks/session-end.py template
  - docs/guides/provider-adapter-development.md
```

### Phase 3: Additional Adapters (Week 5-8)
```yaml
Week 5-6: Cursor Adapter
  - CursorAdapter implementation
  - .cursor/hooks/ templates
  - Integration testing

Week 7-8: Aider Adapter
  - AiderAdapter implementation
  - .aider.conf.yml template
  - Integration testing
```

### Phase 4: Validation & Documentation (Week 9-10)
```yaml
Tasks:
  - Comprehensive adapter testing
  - Feature parity documentation
  - Migration guides
  - Performance benchmarking

Deliverables:
  - Test suite for all adapters
  - Adapter compatibility matrix
  - Provider migration guide
  - Performance report
```

---

## Alternatives Considered

### Alternative 1: Provider-Specific Core
**Approach:** Separate AIPM implementations per provider

**Pros:**
- Optimal for each provider
- No abstraction overhead

**Cons:**
- 5x development effort
- Diverging implementations
- Maintenance nightmare

**Rejected because:** Unsustainable development burden

### Alternative 2: Lowest Common Denominator
**Approach:** Only support features common to all providers

**Pros:**
- Simpler implementation
- Guaranteed feature parity

**Cons:**
- Loses provider-specific strengths
- Limits innovation
- Poor user experience

**Rejected because:** Too limiting, misses provider advantages

### Alternative 3: Provider Plugins
**Approach:** Providers as plugins loaded at runtime

**Pros:**
- Dynamic provider addition
- No core dependencies

**Cons:**
- Complex plugin system
- Security concerns (arbitrary code)
- Harder to test

**Rejected because:** Overkill for known providers, security risk

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Overall system specification
- **ADR-002**: Context Compression Strategy
- **ADR-003**: Sub-Agent Communication Protocol
- **Provider Integration Guide**: Step-by-step adapter development

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Use abstract base class for adapter interface | Type safety, IDE support, clear contract |
| 2025-10-12 | Support markdown, JSON, structured formats | Covers all known provider needs |
| 2025-10-12 | Optional features via `supports_feature()` | Graceful degradation, no forced feature parity |
| 2025-10-12 | Provider detection via config + auto-detection | User control + convenience |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype ClaudeCodeAdapter
3. Validate interface with Cursor requirements
4. Approve and begin implementation

**Owner:** AIPM Architecture Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
