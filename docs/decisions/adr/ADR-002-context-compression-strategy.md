# ADR-002: Context Compression Strategy

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable 10x context capacity through sub-agent delegation

---

## Context

### The Context Explosion Problem

AI coding assistants (Claude, Codex, Gemini) have token limits that constrain the context they can process. For complex projects, the required context quickly exceeds these limits:

**Example: Multi-Tenant E-Commerce Platform**
```
Full Context Required:
├─ Project Context:        ~50,000 tokens
│  ├─ Tech stack details
│  ├─ Coding standards
│  ├─ Architecture principles
│  ├─ Deployment configs
│  └─ Team conventions
│
├─ Work Item Context:      ~80,000 tokens
│  ├─ Feature specifications
│  ├─ Architecture decisions (ADRs)
│  ├─ Database schema
│  ├─ API contracts
│  └─ Integration patterns
│
├─ Task Context:           ~70,000 tokens
│  ├─ Implementation details
│  ├─ Code files involved
│  ├─ Patterns to follow
│  ├─ Test requirements
│  └─ Dependencies
│
└─ Total: 200,000+ tokens

AI Token Limits:
- Claude Sonnet: 200K input tokens
- GPT-4 Turbo: 128K tokens
- Gemini Pro: 32K tokens
- Codex: 8K tokens

Problem: Can't fit full context in single session
```

### Current Pain Points

1. **Context Truncation**
   - AI loses critical details (architecture decisions, patterns, constraints)
   - Leads to inconsistent implementations
   - Causes rework and quality issues

2. **Repeated Explanations**
   - Users must re-explain context every session
   - "What's the tech stack?" "What patterns do we use?"
   - Wastes time, frustrates users

3. **No Sub-Agent Context**
   - When using Task tool to delegate to sub-agents
   - Sub-agents start with zero context
   - Must re-provide context manually (more tokens!)

4. **Scale Limits**
   - Simple projects (< 10K LOC) work fine
   - Complex projects (> 100K LOC) fail
   - Enterprise projects (> 500K LOC) impossible

### Requirements

1. **10x Context Capacity**: Support 200K+ tokens of context in 20K tokens
2. **Zero Context Loss**: Full context preserved, nothing forgotten
3. **Sub-Agent Efficiency**: Sub-agents compress 50K → 1.2K (97% reduction)
4. **Cross-Session Persistence**: Context survives across sessions
5. **Intelligent Layering**: Load only relevant context for current task

---

## Decision

We will implement a **Hierarchical Context Compression System** using:

1. **Sub-Agent Delegation Pattern**: Offload heavy analysis to sub-agents
2. **Compressed Report Format**: Sub-agents return 1-2K token summaries
3. **Context Layering**: Load context progressively (project → work item → task)
4. **Intelligent Caching**: Cache compressed results for reuse
5. **Database as Context Store**: Full context in database, compressed views in memory

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│           Main Orchestrator (AI Coding Assistant)          │
│                                                            │
│  Context Budget: 20,000 tokens                            │
│  ├─ Project snapshot:       3,000 tokens                  │
│  ├─ Work item snapshot:     5,000 tokens                  │
│  ├─ Task snapshot:          8,000 tokens                  │
│  └─ Sub-agent reports:      4,000 tokens                  │
│                                                            │
│  Can now hold full context for complex projects!          │
└──────────────┬─────────────────────────────────────────────┘
               │
               │ Delegates heavy analysis
               │
    ┌──────────┴──────────┬──────────────┬─────────────┐
    │                     │              │             │
┌───▼──────────────┐ ┌───▼────────┐ ┌───▼───────┐ ┌──▼──────┐
│ codebase-        │ │ database-  │ │ rules-    │ │ test-   │
│ navigator        │ │ schema-    │ │ compliance│ │ pattern-│
│                  │ │ explorer   │ │ checker   │ │ analyzer│
│ Input: 50K tokens│ │ Input: 30K │ │ Input: 20K│ │ Input:  │
│ Output: 1.2K     │ │ Output:    │ │ Output:   │ │ 25K     │
│                  │ │ 1.2K       │ │ 1.0K      │ │ Output: │
│ Compression:     │ │ Compression│ │ Compres-  │ │ 1.1K    │
│ 97.6%            │ │ 96.0%      │ │ sion: 95% │ │ Compres-│
│                  │ │            │ │           │ │ sion:   │
│                  │ │            │ │           │ │ 95.6%   │
└──────────────────┘ └────────────┘ └───────────┘ └─────────┘
         │                  │             │             │
         │                  │             │             │
    ┌────▼──────────────────▼─────────────▼─────────────▼───┐
    │            Database (Full Context Storage)            │
    │                                                        │
    │  • 200,000+ tokens of full context                    │
    │  • All code, decisions, patterns, constraints         │
    │  • Sub-agents query and compress on-demand            │
    │  • Main orchestrator never sees full context          │
    └────────────────────────────────────────────────────────┘
```

### Compression Techniques

#### 1. Hierarchical Layering
```python
class ContextAssemblyService:
    """
    Assembles context in layers, loading only what's needed.
    """

    def assemble_minimal_context(self, task_id: int) -> MinimalContext:
        """
        Minimum context to start work (~5K tokens)

        Includes:
        - Project name, tech stack summary
        - Work item objective (1 sentence)
        - Task title and type
        - Agent assignment

        Use case: Quick context check, simple tasks
        """

    def assemble_standard_context(self, task_id: int) -> StandardContext:
        """
        Standard context for most work (~15K tokens)

        Includes:
        - Project: Tech stack, key standards, architecture style
        - Work item: Objective, key decisions, patterns
        - Task: Implementation notes, code files, constraints

        Use case: Normal development work
        """

    def assemble_comprehensive_context(self, task_id: int) -> ComprehensiveContext:
        """
        Full context with sub-agent analysis (~20K tokens)

        Includes:
        - Standard context (15K tokens)
        - Sub-agent reports:
          • Codebase analysis (1.2K)
          • Schema overview (1.2K)
          • Compliance check (1.0K)
          • Test patterns (1.1K)
        - Document references (0.5K):
          • Related ADRs, specs, guides (via document store)
          • Fast lookup (<100ms) vs filesystem scan (5-10s)
          • Document summaries only (full content on-demand)

        Use case: Complex work requiring deep understanding
        """
```

#### 2. Sub-Agent Compression Pattern

**Example: Codebase Navigation Sub-Agent**

```python
class CodebaseNavigatorAgent:
    """
    Sub-agent that analyzes codebase and returns compressed report.
    """

    def analyze(self, query: str, work_item_id: int) -> CompressedReport:
        """
        Full analysis process (50K+ tokens internally)

        Steps:
        1. Load work item context (knows what we're building)
        2. Search entire codebase (grep, AST analysis)
        3. Analyze patterns, relationships, dependencies
        4. Extract key findings
        5. Compress to 1.2K token report

        Query: "Find all tenant-scoped models and relationships"

        Internal processing (50,000 tokens):
        - Searches 150 Python files
        - Analyzes 50 models
        - Traces 200 relationships
        - Identifies 15 patterns
        - Reviews 30 migrations

        Compressed output (1,200 tokens):
        """
        return CompressedReport(
            summary="18 tenant-scoped models found, all inherit TenantMixin",
            key_models=[
                "Tenant (models/tenant.py:15-80) - Core tenant model",
                "Domain (models/domain.py:10-45) - Custom domains per tenant",
                "TenantUser (models/user.py:20-90) - Tenant-specific users"
            ],
            relationships=[
                "Tenant → Domain (1:n via tenant_id FK)",
                "Tenant → TenantUser (1:n via tenant_id FK)",
                "TenantUser → User (1:1 via user_ptr)"
            ],
            patterns=[
                "TenantMixin: Base class for tenant-scoped models",
                "tenant_context(): Context manager for tenant isolation",
                "Row-level security via tenant_id filtering"
            ],
            files=[
                "models/tenant.py:15-80",
                "models/domain.py:10-45",
                "models/user.py:20-90",
                "middleware/tenant.py:30-120"
            ],
            recommendations=[
                "New models should inherit TenantMixin",
                "Use tenant_context() for queries",
                "Add tenant_id to all new models"
            ],
            confidence=0.95,
            token_count=1200
        )
```

#### 3. Structured Compression Format

```python
@dataclass
class CompressedReport:
    """
    Standard format for all sub-agent outputs.

    Design principles:
    - Structured data (not prose) for efficiency
    - Key findings only (no details unless critical)
    - Actionable recommendations
    - File references with line numbers
    - Confidence scoring
    """

    # One-line summary (≤15 words)
    summary: str

    # 3-5 key findings (≤25 words each)
    key_findings: List[str]

    # Relationships/connections (structured)
    relationships: List[str]

    # Patterns to follow (code examples if needed)
    patterns: List[Pattern]

    # File locations (path:line format)
    files: List[str]

    # Actionable recommendations (3-5 items)
    recommendations: List[str]

    # Confidence in findings (0.0-1.0)
    confidence: float

    # Actual token count
    token_count: int

    def validate(self):
        """Ensure report meets compression targets"""
        assert self.token_count <= 2000, "Report too large"
        assert len(self.summary.split()) <= 15, "Summary too long"
        assert self.confidence >= 0.5, "Low confidence"
```

#### 4. Context Caching Strategy

```python
class ContextCache:
    """
    Caches compressed context to avoid redundant sub-agent calls.
    """

    def get_cached_report(
        self,
        agent_name: str,
        query_hash: str,
        work_item_id: int,
        max_age: timedelta
    ) -> Optional[CompressedReport]:
        """
        Return cached report if:
        - Same agent, query, and work item
        - Age < max_age (default: 1 hour)
        - Work item hasn't changed since cache

        Saves: 5-10 seconds per sub-agent call
        """

    def cache_report(
        self,
        agent_name: str,
        query_hash: str,
        work_item_id: int,
        report: CompressedReport
    ):
        """
        Cache report for reuse within session and across sessions.

        Invalidation triggers:
        - Work item updated
        - Code changes committed
        - Manual cache clear
        """
```

### Compression Targets

| Context Source | Full Size | Compressed | Reduction | Method |
|---------------|-----------|------------|-----------|---------|
| Project context | 50,000 | 3,000 | 94% | Hierarchical summary |
| Work item context | 80,000 | 5,000 | 93.75% | Key decisions + patterns |
| Task context | 70,000 | 8,000 | 88.6% | Implementation focus |
| Codebase analysis | 50,000 | 1,200 | 97.6% | Sub-agent compression |
| Schema analysis | 30,000 | 1,200 | 96.0% | Sub-agent compression |
| Rules compliance | 20,000 | 1,000 | 95.0% | Sub-agent compression |
| Test patterns | 25,000 | 1,100 | 95.6% | Sub-agent compression |
| **Total** | **325,000** | **20,500** | **93.7%** | **Combined** |

---

## Consequences

### Positive

1. **10x Context Capacity**
   - Can handle 200K+ tokens of context in 20K tokens
   - Enables complex project development (previously impossible)
   - No more "context too large" errors

2. **Zero Context Loss**
   - Full context preserved in database
   - Sub-agents have access to everything
   - Main orchestrator gets compressed summaries
   - Nothing is forgotten or truncated

3. **Faster Session Starts**
   - Load compressed context in <1s
   - No need to re-explain everything
   - Sub-agents only called when needed

4. **Better Quality**
   - AI has access to all relevant context
   - Decisions based on complete information
   - Consistent with architecture and patterns

5. **Cross-Session Continuity**
   - Context persists across sessions
   - New sessions start with full context
   - Any agent can continue any work

### Negative

1. **Sub-Agent Overhead**
   - Initial sub-agent calls take 5-10 seconds
   - Must wait for compression
   - Mitigated by caching

2. **Compression Quality Risk**
   - Information loss during compression
   - Sub-agents might miss nuances
   - Mitigated by structured format + validation

3. **Cache Invalidation Complexity**
   - Need to detect when cache is stale
   - Code changes, schema changes, etc.
   - Risk of serving outdated context

4. **Database Query Load**
   - Sub-agents query database heavily
   - Could impact performance at scale
   - Mitigated by indexing + connection pooling

### Mitigation Strategies

1. **Sub-Agent Performance**
   - Aggressive caching (1-hour TTL)
   - Parallel sub-agent execution
   - Lazy loading (only call when needed)
   - Pre-warm cache for active work items

2. **Compression Quality**
   - Standardized report format
   - Validation thresholds (confidence, token count)
   - Human review of compressed reports (spot-check)
   - Iterative refinement of compression algorithms

3. **Cache Management**
   - Git hooks trigger cache invalidation
   - Schema changes clear relevant caches
   - Manual cache clear command
   - Cache freshness indicators in UI

4. **Database Performance**
   - Proper indexing (work_item_id, task_id, agent_id)
   - Connection pooling
   - Read replicas for sub-agents
   - Query optimization

---

## Implementation Plan

### Phase 1: Core Compression Framework (Week 1-2)

```yaml
Week 1: Data Structures & Interfaces
  Tasks:
    - Define CompressedReport dataclass
    - Define MinimalContext, StandardContext, ComprehensiveContext
    - Create ContextAssemblyService interface
    - Implement context layering logic

  Deliverables:
    - agentpm/core/context/compression.py
    - agentpm/core/context/assembly.py
    - agentpm/core/context/models.py
    - Tests for context assembly

  Success Criteria:
    - Context loads in <1s
    - Layering works (minimal → standard → comprehensive)
    - Token counts validated

Week 2: Sub-Agent Framework
  Tasks:
    - Create SubAgent base class
    - Implement Task tool integration
    - Build report validation system
    - Create compression benchmarks

  Deliverables:
    - agentpm/core/agents/sub_agent.py
    - agentpm/core/agents/compression.py
    - Compression benchmark suite
    - Sub-agent testing framework

  Success Criteria:
    - Sub-agents can return compressed reports
    - Validation catches oversized reports
    - Benchmarks measure compression ratios
```

### Phase 2: Sub-Agent Implementation (Week 3-6)

```yaml
Week 3-4: Core Analysis Sub-Agents
  Agents:
    - CodebaseNavigatorAgent (50K → 1.2K)
    - DatabaseSchemaExplorerAgent (30K → 1.2K)
    - RulesComplianceCheckerAgent (20K → 1K)

  Implementation:
    - Query interface for each agent
    - Compression algorithms
    - Report generation
    - Integration with main orchestrator

  Success Criteria:
    - Each agent achieves 95%+ compression
    - Reports are actionable and accurate
    - Cache hit rate >70% after warmup

Week 5-6: Specialized Sub-Agents
  Agents:
    - WorkflowAnalyzerAgent (15K → 900 tokens)
    - PluginSystemAnalyzerAgent (50K → 1.5K)
    - TestPatternAnalyzerAgent (25K → 1.1K)
    - DocumentationAnalyzerAgent (30K → 1.3K)

  Success Criteria:
    - All 7 sub-agents operational
    - Combined compression: 200K → 8.2K (96%)
    - Sub-agent execution time <10s (P95)
```

### Phase 3: Caching & Optimization (Week 7-8)

```yaml
Week 7: Cache Implementation
  Tasks:
    - Build ContextCache system
    - Implement cache invalidation logic
    - Add cache warming for active work
    - Create cache metrics dashboard

  Deliverables:
    - agentpm/core/context/cache.py
    - Cache invalidation hooks
    - Cache warming service
    - Cache metrics

  Success Criteria:
    - Cache hit rate >80% after warmup
    - Cache invalidation works correctly
    - Cached responses <100ms

Week 8: Performance Optimization
  Tasks:
    - Database query optimization
    - Parallel sub-agent execution
    - Connection pooling
    - Compression algorithm tuning

  Deliverables:
    - Optimized database indices
    - Parallel execution framework
    - Performance benchmarks
    - Optimization report

  Success Criteria:
    - Context assembly <1s (P95)
    - Sub-agent calls <5s (P95)
    - Database queries <100ms (P95)
    - Parallel execution 3x faster
```

### Phase 4: Validation & Testing (Week 9-10)

```yaml
Week 9: Quality Validation
  Tasks:
    - Build compression quality tests-BAK
    - Human evaluation of compressed reports
    - A/B testing (compressed vs full context)
    - Edge case testing

  Deliverables:
    - Quality test suite
    - Human evaluation rubric
    - A/B test results
    - Edge case documentation

  Success Criteria:
    - Compression accuracy >90%
    - Human evaluators rate reports >4/5
    - No critical information loss detected
    - Edge cases handled gracefully

Week 10: Integration Testing
  Tasks:
    - End-to-end workflow tests-BAK
    - Multi-session persistence tests-BAK
    - Cross-agent context tests-BAK
    - Provider integration tests-BAK

  Deliverables:
    - E2E test suite
    - Multi-session test scenarios
    - Cross-agent test cases
    - Provider compatibility tests-BAK

  Success Criteria:
    - All workflows work with compressed context
    - Context persists correctly across sessions
    - Sub-agents share context successfully
    - Works with all providers (Claude, Cursor, Aider)
```

---

## Compression Examples

### Example 1: Codebase Analysis

**Input Query:**
"Find all authentication-related code and patterns"

**Full Context (50,000 tokens):**
```
models/user.py (1,200 lines):
  class User(AbstractBaseUser):
      username = models.CharField(max_length=150, unique=True)
      email = models.EmailField(unique=True)
      # ... 50 more fields
      # ... 30 methods

  class UserProfile(models.Model):
      user = models.OneToOneField(User, on_delete=models.CASCADE)
      # ... 20 fields

auth/backends.py (500 lines):
  class JWTAuthBackend(BaseBackend):
      # ... complete implementation

auth/middleware.py (800 lines):
  class AuthenticationMiddleware:
      # ... complete implementation

# ... 50 more files with auth code
```

**Compressed Output (1,200 tokens):**
```python
CompressedReport(
    summary="JWT-based auth with session fallback, 8 models, 4 backends, 2 middleware",

    key_findings=[
        "Primary: JWT tokens (access + refresh) via auth/jwt.py:45-200",
        "Fallback: Django sessions for admin panel",
        "User model: Custom (models/user.py:15-120) with email auth",
        "2FA: TOTP via django-otp (auth/totp.py:30-80)"
    ],

    relationships=[
        "User → UserProfile (1:1)",
        "User → UserSession (1:n for multi-device)",
        "User → TwoFactorDevice (1:n for backup codes)"
    ],

    patterns=[
        "JWTMixin: Adds JWT methods to User model",
        "AuthService: Business logic layer (auth/services.py:20-150)",
        "Refresh token rotation: New refresh on every access token use"
    ],

    files=[
        "models/user.py:15-120 (User model)",
        "auth/jwt.py:45-200 (JWT implementation)",
        "auth/backends.py:30-120 (JWTAuthBackend)",
        "auth/middleware.py:15-80 (AuthMiddleware)",
        "auth/services.py:20-150 (AuthService)"
    ],

    recommendations=[
        "New auth features: Add to AuthService layer",
        "Token expiry: Access 15min, refresh 7 days",
        "Testing: Use auth/tests-BAK/factories.py for test users"
    ],

    confidence=0.92,
    token_count=1200
)
```

### Example 2: Database Schema Analysis

**Full Schema (30,000 tokens):**
- 50 models with all fields, constraints, indices
- 80 migrations with full code
- All relationships, foreign keys, many-to-many tables

**Compressed Output (1,200 tokens):**
```python
CompressedReport(
    summary="Multi-tenant schema: 18 tenant-scoped models, 32 shared models, all use TenantMixin",

    key_findings=[
        "Tenant isolation: tenant_id column + row-level security",
        "Shared models: User, Organization, Subscription (no tenant_id)",
        "Critical FKs: All tenant-scoped models → Tenant(tenant_id)",
        "Recent migration: 0045_add_tenant_domain (2025-10-10)"
    ],

    relationships=[
        "Tenant → Domain (1:n) for custom domains",
        "Tenant → TenantUser (1:n) via tenant_id",
        "TenantUser → User (1:1) via user_ptr",
        "Tenant → Subscription (n:1) shared model"
    ],

    patterns=[
        "TenantMixin: Adds tenant_id FK + tenant_context manager",
        "SoftDeleteMixin: is_deleted + deleted_at timestamps",
        "TimestampMixin: created_at + updated_at auto-managed"
    ],

    files=[
        "models/tenant.py:15-80 (Tenant + TenantMixin)",
        "migrations/0045_add_tenant_domain.py (latest)",
        "managers/tenant.py:20-60 (TenantManager)"
    ],

    recommendations=[
        "New models: Inherit TenantMixin if tenant-scoped",
        "Queries: Always use tenant_context() manager",
        "Migrations: Test with multi-tenant test data"
    ],

    confidence=0.95,
    token_count=1180
)
```

---

## Alternatives Considered

### Alternative 1: Full Context Always
**Approach:** Load full 200K+ tokens, no compression

**Pros:**
- No information loss
- No compression overhead
- Simpler implementation

**Cons:**
- Doesn't work (exceeds token limits)
- Slow to load
- Expensive (token costs)

**Rejected because:** Infeasible for complex projects

### Alternative 2: Manual Context Selection
**Approach:** User manually specifies what context to load

**Pros:**
- User controls what's included
- Can optimize per task

**Cons:**
- Burden on user (defeats purpose)
- User doesn't know what's needed
- Inconsistent context quality

**Rejected because:** Creates more problems than it solves

### Alternative 3: AI-Powered Summarization
**Approach:** Use AI to summarize full context

**Pros:**
- Automated compression
- Can handle any content

**Cons:**
- Expensive (summarizing 200K tokens costs $$$)
- Slow (30-60 seconds per summary)
- Quality inconsistent
- Recursion problem (need context to summarize context)

**Rejected because:** Too expensive and slow

### Alternative 4: Vector Embeddings + Retrieval
**Approach:** Embed all context, retrieve relevant chunks

**Pros:**
- Semantic retrieval
- Scales to large codebases

**Cons:**
- Complex infrastructure (vector DB)
- Retrieval quality issues (may miss critical context)
- Expensive to maintain embeddings
- No structured understanding

**Rejected because:** Over-engineered, misses structured relationships

---

## Validation Metrics

### Compression Metrics
```yaml
Compression Ratio:
  Target: >90% reduction (200K → <20K)
  Measurement: token_count_before / token_count_after
  Threshold: Must achieve 90% or fail validation

Information Retention:
  Target: >90% of critical information preserved
  Measurement: Human evaluation + A/B testing
  Threshold: AI produces equivalent results with compressed context

Quality Scores:
  Target: >4.0/5.0 from human evaluators
  Measurement: Rubric-based evaluation
  Threshold: Compressed reports rated "good" or "excellent"
```

### Performance Metrics
```yaml
Context Assembly Time:
  Target: <1s (P95)
  Measurement: End-to-end context load time
  Threshold: Must be faster than reading full context

Sub-Agent Execution:
  Target: <5s per sub-agent (P95)
  Measurement: Query → compressed report time
  Threshold: Must be cached after first call

Cache Hit Rate:
  Target: >80% after warmup
  Measurement: Cached responses / total requests
  Threshold: Cache must significantly reduce load
```

### Quality Metrics
```yaml
Context Accuracy:
  Target: >95% of queries answered correctly
  Measurement: Correctness of AI responses using compressed context
  Threshold: Equivalent to full context results

Decision Quality:
  Target: No reduction in decision quality
  Measurement: Architecture decisions made with compressed context
  Threshold: Same quality as with full context

Bug Introduction Rate:
  Target: No increase in bugs
  Measurement: Bugs per 1000 lines of code
  Threshold: Same or better than full context
```

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Overall system spec
- **ADR-001**: Provider Abstraction Architecture
- **ADR-003**: Sub-Agent Communication Protocol
- **Sub-Agent Development Guide**: How to build compression agents

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Use sub-agent delegation for compression | Only approach that scales to 200K+ tokens |
| 2025-10-12 | Structured report format over prose | More efficient, easier to validate |
| 2025-10-12 | Hierarchical context layering | Load only what's needed for task |
| 2025-10-12 | Aggressive caching (1-hour TTL) | Sub-agent calls are expensive |
| 2025-10-12 | Database as source of truth | Enables cross-session, cross-agent context |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype one sub-agent (codebase-navigator)
3. Measure compression ratio and quality
4. Approve and begin full implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
