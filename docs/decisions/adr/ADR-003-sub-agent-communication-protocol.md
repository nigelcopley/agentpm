# ADR-003: Sub-Agent Communication Protocol

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable cross-agent context sharing and coordination

---

## Context

### The Cross-Agent Context Problem

AIPM uses multiple agents during complex project development:

**Main Orchestrator (You):**
- Routes work to appropriate agents
- Maintains overall session context
- Coordinates between specialist agents

**Specialist Agents (Implementation):**
- aipm-python-cli-developer
- aipm-database-developer
- aipm-frontend-developer
- aipm-testing-specialist
- etc.

**Sub-Agents (Context Compression):**
- aipm-codebase-navigator
- aipm-database-schema-explorer
- aipm-rules-compliance-checker
- etc.

**Current Problem:**

```
Session 1 (Main Orchestrator):
├─ Discovers: "Use JWT pattern for auth"
├─ Stores in database ✅
└─ Session ends

Session 2 (Task tool → aipm-python-cli-developer):
├─ Sub-agent launches with Task tool
├─ Has NO ACCESS to Session 1 discoveries ❌
├─ Can't see "Use JWT pattern" decision ❌
└─ Starts from scratch, may choose different pattern ❌

Result: Inconsistent implementations, wasted work, quality issues
```

### Requirements

1. **Cross-Session Context**: Decisions persist across sessions
2. **Cross-Agent Context**: All agents access same context
3. **Real-Time Updates**: Context updates immediately available
4. **Hierarchical Access**: Agents see only relevant context
5. **Audit Trail**: Track which agent learned what, when

---

## Decision

We will implement a **Database-Backed Context Sharing Protocol** with:

1. **Shared Context Store**: Database as single source of truth
2. **Context Loading Protocol**: Agents auto-load relevant context on initialization
3. **Context Update Protocol**: Agents save learnings back to database immediately
4. **Structured Communication**: Standard format for agent-to-agent messages
5. **Event System**: Notify agents when context changes

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Context Database                     │
│                  (Single Source of Truth)                │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Projects                                           │ │
│  │  ├─ Tech stack, standards, rules                  │ │
│  │  └─ Global patterns and constraints               │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Work Items                                         │ │
│  │  ├─ Objectives, acceptance criteria               │ │
│  │  ├─ Decisions (ADRs) with rationale              │ │
│  │  ├─ Discovered patterns                           │ │
│  │  └─ Constraints specific to this work             │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Tasks                                              │ │
│  │  ├─ Implementation details                        │ │
│  │  ├─ Code files involved                           │ │
│  │  ├─ Sub-task dependencies                         │ │
│  │  └─ Agent assignments                             │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Sessions                                           │ │
│  │  ├─ Active work item/task                         │ │
│  │  ├─ Current agent                                  │ │
│  │  ├─ Session learnings (continuous)                │ │
│  │  └─ Start/end timestamps                          │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Agent Learnings (Cross-Agent Knowledge)           │ │
│  │  ├─ learning_id, work_item_id, task_id           │ │
│  │  ├─ agent_id, session_id                          │ │
│  │  ├─ learning_type: decision | pattern | discovery│ │
│  │  ├─ content: What was learned                     │ │
│  │  └─ timestamp, confidence                         │ │
│  └────────────────────────────────────────────────────┘ │
└───────────┬──────────────┬──────────────┬───────────────┘
            │              │              │
    ┌───────▼──────┐  ┌───▼───────┐  ┌──▼────────────┐
    │ Main         │  │ Specialist│  │ Sub-Agent     │
    │ Orchestrator │  │ Agents    │  │ (Compression) │
    │              │  │           │  │               │
    │ Reads: ALL   │  │ Reads:    │  │ Reads:        │
    │ Writes: HIGH │  │ WORK_ITEM │  │ WORK_ITEM     │
    │ LEVEL        │  │ + TASK    │  │ (read-only)   │
    │              │  │           │  │               │
    │ • Session    │  │ Writes:   │  │ Writes:       │
    │   mgmt       │  │ TASK      │  │ Compressed    │
    │ • Routing    │  │ LEARNINGS │  │ reports only  │
    │ • Decisions  │  │           │  │               │
    └──────────────┘  └───────────┘  └───────────────┘
```

### Context Loading Protocol

#### Phase 1: Agent Initialization

```python
class AgentContextLoader:
    """
    Automatically loads relevant context when agent initializes.

    Every agent (main, specialist, sub-agent) calls this on start.
    """

    def load_context_for_task(self, task_id: int) -> AgentContext:
        """
        Load all relevant context for this task.

        Hierarchy:
        1. Project context (tech stack, standards, rules)
        2. Work item context (objectives, decisions, patterns)
        3. Task context (implementation details, files)
        4. Related learnings (from all previous agents)
        5. Related documents (ADRs, specs, guides via document store)

        Returns: AgentContext with everything this agent needs

        Document Integration:
        - Fast search (<100ms) for related docs by work_item_id and tags
        - Includes document summaries (not full content)
        - Agent can request full doc if needed (Read tool)
        - Prevents context bloat from full documentation
        """

        # Load hierarchical context
        project_ctx = self._load_project_context(task.project_id)
        work_item_ctx = self._load_work_item_context(task.work_item_id)
        task_ctx = self._load_task_context(task_id)

        # Load cross-agent learnings
        learnings = self._load_related_learnings(task.work_item_id)

        return AgentContext(
            project=project_ctx,
            work_item=work_item_ctx,
            task=task_ctx,
            learnings=learnings,
            loaded_at=datetime.now()
        )

    def _load_related_learnings(self, work_item_id: int) -> List[Learning]:
        """
        Load learnings from ALL agents who worked on this work item.

        Includes:
        - Decisions made (by any agent, any session)
        - Patterns discovered (by any agent)
        - Constraints identified (by any agent)
        - Discoveries (database schema, API contracts, etc.)

        Example learnings:
        - "Agent: aipm-database-developer, Session 15: Use UUID for primary keys"
        - "Agent: aipm-python-cli-developer, Session 18: All services use async/await"
        - "Agent: aipm-testing-specialist, Session 22: Use pytest-asyncio for async tests-BAK"
        """
        return db.query(
            Learning
        ).filter(
            Learning.work_item_id == work_item_id
        ).order_by(
            Learning.timestamp.desc()
        ).all()
```

#### Phase 2: Agent Work (with Context)

```python
class SpecialistAgent:
    """
    Example: aipm-python-cli-developer
    """

    def __init__(self, task_id: int):
        # AUTOMATICALLY load context on initialization
        self.context = AgentContextLoader().load_context_for_task(task_id)

        # Now agent has FULL context from all previous agents
        print(f"Loaded context:")
        print(f"  Project: {self.context.project.name}")
        print(f"  Tech stack: {self.context.project.tech_stack}")
        print(f"  Work item: {self.context.work_item.objective}")
        print(f"  Previous learnings: {len(self.context.learnings)}")

    def implement_feature(self):
        """
        Implement with full context awareness.

        Example: Implementing authentication
        """

        # Check for previous decisions
        auth_decisions = [
            l for l in self.context.learnings
            if 'auth' in l.content.lower()
        ]

        if auth_decisions:
            print(f"Previous auth decisions found:")
            for decision in auth_decisions:
                print(f"  - {decision.content} (by {decision.agent_id})")
                print(f"    Rationale: {decision.rationale}")

        # Check for patterns to follow
        patterns = self.context.work_item.patterns
        if patterns:
            print(f"Patterns to follow:")
            for pattern in patterns:
                print(f"  - {pattern.name}: {pattern.description}")

        # Implement with context
        # ... implementation code ...
```

### Context Update Protocol

#### Real-Time Learning Capture

```python
class AgentLearningRecorder:
    """
    Records learnings as agent works.

    Used by all agents to save discoveries back to database.
    """

    def record_decision(
        self,
        work_item_id: int,
        task_id: int,
        agent_id: str,
        session_id: int,
        decision: str,
        rationale: str,
        alternatives_considered: List[str],
        confidence: float = 0.8
    ) -> Learning:
        """
        Record an architectural or implementation decision.

        Example:
        record_decision(
            work_item_id=5,
            task_id=42,
            agent_id="aipm-database-developer",
            session_id=123,
            decision="Use UUID for primary keys instead of auto-increment integers",
            rationale="""
                UUID advantages:
                - Globally unique (safe for distributed systems)
                - No collision risk during merges
                - Better for multi-tenant isolation

                Trade-offs:
                - Slightly larger storage (16 bytes vs 4-8 bytes)
                - Not sequential (minor index performance impact)
            """,
            alternatives_considered=[
                "Auto-increment integers (rejected: merge conflicts)",
                "Snowflake IDs (rejected: overkill for our scale)"
            ],
            confidence=0.9
        )

        Immediately available to:
        - Same agent in same session ✅
        - Other agents in same session ✅
        - Future sessions ✅
        - Sub-agents ✅
        """

        learning = Learning(
            id=generate_id(),
            work_item_id=work_item_id,
            task_id=task_id,
            agent_id=agent_id,
            session_id=session_id,
            learning_type="decision",
            content=decision,
            rationale=rationale,
            alternatives=alternatives_considered,
            confidence=confidence,
            timestamp=datetime.now()
        )

        db.add(learning)
        db.commit()

        # Trigger event for other agents
        event_bus.publish("learning.recorded", learning)

        return learning

    def record_pattern(
        self,
        work_item_id: int,
        agent_id: str,
        pattern_name: str,
        pattern_description: str,
        code_example: Optional[str],
        when_to_use: str
    ) -> Learning:
        """
        Record a code pattern for reuse.

        Example:
        record_pattern(
            work_item_id=5,
            agent_id="aipm-python-cli-developer",
            pattern_name="ServiceLayer",
            pattern_description="Business logic isolation in service classes",
            code_example='''
            class AuthService:
                def __init__(self, db: Database):
                    self.db = db

                async def authenticate(self, email: str, password: str) -> User:
                    # Business logic here
            ''',
            when_to_use="All business logic must be in service layer, not views"
        )
        """

    def record_discovery(
        self,
        work_item_id: int,
        agent_id: str,
        discovery: str,
        impact: str,
        action_needed: Optional[str] = None
    ) -> Learning:
        """
        Record something discovered during work.

        Examples:
        - "Django middleware handles tenant context automatically"
        - "PostgreSQL has row-level security built-in"
        - "React 18 concurrent rendering breaks our modal system"
        """
```

### Structured Communication Format

```python
@dataclass
class Learning:
    """
    Standard format for all agent learnings.

    Stored in database, accessible by all agents.
    """

    # Identification
    id: str
    work_item_id: int
    task_id: Optional[int]
    agent_id: str  # Which agent learned this
    session_id: int  # Which session

    # Learning content
    learning_type: Literal["decision", "pattern", "discovery", "constraint"]
    content: str  # What was learned
    rationale: Optional[str]  # Why (for decisions)
    alternatives: Optional[List[str]]  # What else was considered

    # Context
    code_example: Optional[str]  # For patterns
    files_affected: Optional[List[str]]  # Which files involved
    related_learnings: Optional[List[str]]  # Links to other learnings

    # Metadata
    confidence: float  # 0.0-1.0
    timestamp: datetime
    supersedes: Optional[str]  # If this replaces previous learning

    # Validation
    validated_by: Optional[str]  # Agent or human who validated
    validated_at: Optional[datetime]

@dataclass
class AgentMessage:
    """
    For direct agent-to-agent communication (rare, mostly via database).
    """

    from_agent: str
    to_agent: str
    message_type: Literal["question", "request", "notification", "handoff"]
    content: str
    context: Dict[str, Any]
    requires_response: bool
    timestamp: datetime
```

### Event System for Context Updates

```python
class ContextEventBus:
    """
    Notifies agents when context changes.

    Use case: Agent A makes a decision, Agent B (working in parallel)
    should know about it immediately.
    """

    def publish(self, event_type: str, data: Any):
        """
        Publish context change event.

        Event types:
        - learning.recorded: New learning added
        - decision.made: Architecture decision made
        - pattern.discovered: New pattern identified
        - constraint.added: New constraint identified
        - context.invalidated: Previous learning superseded
        """

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to context changes.

        Example:
        event_bus.subscribe(
            "decision.made",
            lambda decision: print(f"New decision: {decision.content}")
        )
        """
```

---

## Consequences

### Positive

1. **Zero Context Loss Between Agents**
   - All agents access same learnings
   - No repeated work or contradictory decisions
   - Consistent implementations across agents

2. **Cross-Session Continuity**
   - Session 2 knows everything from Session 1
   - Any agent can continue any work
   - No "what happened before?" questions

3. **Parallel Agent Coordination**
   - Multiple agents can work simultaneously
   - Shared context prevents conflicts
   - Event system keeps everyone synchronized

4. **Full Audit Trail**
   - Every learning tracked with agent, session, timestamp
   - Can answer "who decided X and why?"
   - Compliance and review ready

5. **Continuous Learning**
   - System gets smarter with every session
   - Patterns accumulate over time
   - Future work benefits from past learnings

### Negative

1. **Database Dependency**
   - All agents must have database access
   - Network latency for remote agents
   - Single point of failure

2. **Context Synchronization Overhead**
   - Loading context on agent init (100-500ms)
   - Writing learnings to database (10-50ms per learning)
   - Event propagation delays (50-200ms)

3. **Context Explosion Risk**
   - Learnings accumulate indefinitely
   - Need to prune or archive old learnings
   - Query performance degrades with size

4. **Learning Quality Variance**
   - Not all agent learnings are high quality
   - May record incorrect or outdated information
   - Need validation and confidence scoring

### Mitigation Strategies

1. **Database Performance**
   - Connection pooling for agents
   - Proper indexing (work_item_id, agent_id, timestamp)
   - Read replicas for sub-agents (read-heavy)
   - Caching frequently accessed learnings

2. **Context Loading Optimization**
   - Lazy loading (only load when accessed)
   - Compression of large learnings
   - Selective loading (only relevant learnings)
   - Prefetching for known patterns

3. **Context Pruning**
   - Archive learnings older than 6 months
   - Supersede outdated learnings
   - Confidence-based filtering (hide low-confidence)
   - Human review of critical learnings

4. **Quality Assurance**
   - Confidence scoring required
   - Validation by quality-validator agent
   - Human review for high-impact decisions
   - Rollback mechanism for bad learnings

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

```yaml
Week 1: Database Schema & Models
  Tasks:
    - Create learnings table
    - Create agent_messages table (optional)
    - Add indices for performance
    - Implement Learning model

  Deliverables:
    - Migration: 0016_add_agent_learnings.py
    - Model: agentpm/core/database/models/learning.py
    - Tests: test_learning_model.py

  Success Criteria:
    - Learnings can be stored and retrieved
    - Queries perform <100ms
    - All fields validated

Week 2: Context Loading & Recording
  Tasks:
    - Implement AgentContextLoader
    - Implement AgentLearningRecorder
    - Create context loading tests-BAK
    - Performance optimization

  Deliverables:
    - agentpm/core/agents/context_loader.py
    - agentpm/core/agents/learning_recorder.py
    - Comprehensive test suite
    - Performance benchmarks

  Success Criteria:
    - Context loads in <500ms
    - Recording learnings <50ms
    - All agents can access context
```

### Phase 2: Agent Integration (Week 3-4)

```yaml
Week 3: Specialist Agent Integration
  Tasks:
    - Update all specialist agents to use context loader
    - Add learning recording to implementations
    - Test cross-agent context sharing
    - Integration tests-BAK

  Agents Updated:
    - aipm-python-cli-developer
    - aipm-database-developer
    - aipm-frontend-developer
    - aipm-testing-specialist

  Success Criteria:
    - All agents load context on init
    - All agents record learnings
    - Context shared correctly between agents

Week 4: Sub-Agent Integration
  Tasks:
    - Update sub-agents to use context loader
    - Ensure sub-agents see specialist learnings
    - Test compression with full context
    - Validate no regression in compression ratios

  Sub-Agents Updated:
    - aipm-codebase-navigator
    - aipm-database-schema-explorer
    - aipm-rules-compliance-checker
    - (all 7 sub-agents)

  Success Criteria:
    - Sub-agents have full context access
    - Compression still achieves 95%+
    - Sub-agent reports reference learnings
```

### Phase 3: Event System & Optimization (Week 5-6)

```yaml
Week 5: Event System
  Tasks:
    - Implement ContextEventBus
    - Add event publishing to recorder
    - Subscribe agents to relevant events
    - Test real-time notifications

  Deliverables:
    - agentpm/core/events/context_bus.py
    - Event handlers for all agents
    - Event system tests-BAK
    - Documentation

  Success Criteria:
    - Events propagate <200ms
    - Agents notified of context changes
    - No event loss or duplication

Week 6: Performance Optimization
  Tasks:
    - Implement learning caching
    - Optimize database queries
    - Add connection pooling
    - Benchmark all operations

  Deliverables:
    - Learning cache implementation
    - Query optimization report
    - Connection pool configuration
    - Performance test suite

  Success Criteria:
    - Context loading <200ms (cached)
    - Learning recording <20ms
    - Database queries <50ms (P95)
```

### Phase 4: Quality & Validation (Week 7-8)

```yaml
Week 7: Quality Assurance
  Tasks:
    - Implement confidence scoring
    - Add learning validation
    - Create review workflow
    - Build quality dashboard

  Deliverables:
    - Confidence scoring algorithm
    - Validation rules
    - Review interface (CLI)
    - Quality metrics

  Success Criteria:
    - All learnings have confidence scores
    - Low-confidence learnings flagged
    - Human can review and validate

Week 8: Integration Testing
  Tasks:
    - End-to-end cross-agent tests-BAK
    - Multi-session persistence tests-BAK
    - Parallel agent coordination tests-BAK
    - Provider compatibility tests-BAK

  Deliverables:
    - E2E test scenarios
    - Multi-session test suite
    - Parallel execution tests-BAK
    - Provider tests-BAK (Claude, Cursor, Aider)

  Success Criteria:
    - All scenarios pass
    - No context loss detected
    - Parallel agents coordinate correctly
```

---

## Usage Examples

### Example 1: Cross-Agent Decision Sharing

```python
# Session 1: Database developer makes decision
# Agent: aipm-database-developer

recorder = AgentLearningRecorder()
recorder.record_decision(
    work_item_id=5,
    task_id=42,
    agent_id="aipm-database-developer",
    session_id=101,
    decision="Use UUID for all primary keys",
    rationale="Global uniqueness, multi-tenant safe, no merge conflicts",
    alternatives_considered=[
        "Auto-increment (rejected: merge conflicts, not globally unique)",
        "Snowflake IDs (rejected: overkill for our scale)"
    ],
    confidence=0.9
)

# Session 2: Python developer sees decision automatically
# Agent: aipm-python-cli-developer

context = AgentContextLoader().load_context_for_task(task_id=43)

# Context includes database developer's decision
uuid_decisions = [
    l for l in context.learnings
    if 'uuid' in l.content.lower() and l.learning_type == "decision"
]

print(f"Found {len(uuid_decisions)} UUID-related decisions:")
for decision in uuid_decisions:
    print(f"  Decision: {decision.content}")
    print(f"  By: {decision.agent_id} in Session {decision.session_id}")
    print(f"  Rationale: {decision.rationale}")
    print(f"  Confidence: {decision.confidence}")

# Python developer implements consistent with decision
class User(Model):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Automatically uses UUID because decision is in context
```

### Example 2: Pattern Discovery and Reuse

```python
# Session 1: Developer discovers pattern
recorder.record_pattern(
    work_item_id=5,
    agent_id="aipm-python-cli-developer",
    pattern_name="TenantContextManager",
    pattern_description="Context manager for tenant-scoped queries",
    code_example="""
    @contextmanager
    def tenant_context(tenant_id: int):
        '''
        Automatically filter queries by tenant_id.

        Usage:
            with tenant_context(tenant_id):
                users = User.objects.all()  # Filtered automatically
        '''
        tenant_var.set(tenant_id)
        try:
            yield
        finally:
            tenant_var.set(None)
    """,
    when_to_use="All tenant-scoped database queries MUST use this"
)

# Session 2: Different developer sees pattern
context = AgentContextLoader().load_context_for_task(task_id=50)

patterns = [p for p in context.learnings if p.learning_type == "pattern"]
print(f"Available patterns: {len(patterns)}")

tenant_patterns = [p for p in patterns if 'tenant' in p.content.lower()]
if tenant_patterns:
    print("Tenant-related patterns:")
    for pattern in tenant_patterns:
        print(f"  - {pattern.content}")
        if pattern.code_example:
            print(f"    Example:\n{pattern.code_example}")

# Developer uses pattern consistently
with tenant_context(request.tenant_id):
    orders = Order.objects.filter(status='pending')
    # Automatically scoped to tenant
```

### Example 3: Sub-Agent Accessing Specialist Learnings

```python
# Sub-agent (codebase-navigator) sees all previous learnings

class CodebaseNavigatorAgent:
    def analyze(self, query: str, work_item_id: int) -> CompressedReport:
        # Load full context including all agent learnings
        context = AgentContextLoader().load_context_for_work_item(work_item_id)

        # Check for relevant learnings from specialists
        auth_learnings = [
            l for l in context.learnings
            if 'auth' in l.content.lower()
        ]

        print(f"Found {len(auth_learnings)} auth-related learnings:")
        for learning in auth_learnings:
            print(f"  - {learning.content} (by {learning.agent_id})")

        # Perform analysis WITH CONTEXT
        # Can reference previous decisions, patterns, constraints

        # Return compressed report that mentions context
        return CompressedReport(
            summary="JWT-based auth per decision by aipm-database-developer",
            key_findings=[
                "Auth pattern: JWTMixin from previous learning",
                "Uses tenant_context manager (established pattern)",
                # ... references learnings ...
            ],
            # ...
        )
```

---

## Alternatives Considered

### Alternative 1: File-Based Context
**Approach:** Save learnings to markdown files

**Pros:**
- Simple to implement
- Human-readable
- Git-versioned

**Cons:**
- No structured queries
- No cross-agent synchronization
- Merge conflicts
- No event system

**Rejected because:** Doesn't scale, no real-time sharing

### Alternative 2: Redis/Cache-Based
**Approach:** Use Redis for real-time context sharing

**Pros:**
- Very fast
- Real-time updates
- Pub/sub built-in

**Cons:**
- No durability (crash = data loss)
- No complex queries
- Separate infrastructure
- No audit trail

**Rejected because:** Need persistent storage and audit

### Alternative 3: Message Queue
**Approach:** Agents communicate via message queue (RabbitMQ, Kafka)

**Pros:**
- Decoupled agents
- Scalable
- Event-driven

**Cons:**
- Complex infrastructure
- Eventual consistency issues
- Over-engineered for problem
- Still need database for persistence

**Rejected because:** Too complex for requirements

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Overall system
- **ADR-001**: Provider Abstraction Architecture
- **ADR-002**: Context Compression Strategy
- **ADR-004**: Evidence Storage and Retrieval

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Database as single source of truth | Durable, queryable, proven |
| 2025-10-12 | Auto-load context on agent init | Zero config, always has context |
| 2025-10-12 | Structured Learning format | Queryable, validatable |
| 2025-10-12 | Event system for real-time updates | Parallel agent coordination |
| 2025-10-12 | Confidence scoring required | Quality assurance |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype context loader with one agent
3. Test cross-agent context sharing
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
