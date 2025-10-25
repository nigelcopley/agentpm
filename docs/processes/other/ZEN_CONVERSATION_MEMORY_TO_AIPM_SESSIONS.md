# Enhancing AIPM Sessions with Zen Conversation Memory Patterns

**Analysis Date**: 2025-10-14
**Status**: Proposal - Enhances WI-65 (Rich Context System) and WI-35 (Session Management)
**Impact**: High - Transforms session storage into operational agent memory system

---

## Executive Summary

**Core Insight**: Zen MCP Server's conversation memory system and AIPM's session system are **conceptually parallel**. Both track multi-turn interactions, file references, and temporal progression. However, Zen's is **operational** (used during live AI interactions) while AIPM's is **archival** (post-session storage).

**Opportunity**: Enhance AIPM's existing session infrastructure to provide **real-time operational context** for agents, similar to how Zen enables cross-tool conversation continuation.

**Strategic Fit**: This directly enhances:
- **WI-65**: Rich Context System (in_progress) - adds temporal/historical context dimension
- **WI-35**: Session Management System (review) - transforms from archival to operational

---

## 🎯 Problem Statement

### Current State

**AIPM has THREE separate systems**:
1. **Sessions** (models/session.py): Tool-agnostic session tracking with metadata
2. **Context Assembly** (assembly_service.py): Real-time context building for agents
3. **Temporal Context** (temporal_loader.py): Loads 3 most recent session summaries

**Current Limitations**:
- ✅ Session data is captured (SessionMetadata tracks work_items, tasks, decisions)
- ✅ Temporal loader provides basic history (last 3 sessions)
- ❌ **No token budgeting** for session history in context assembly
- ❌ **No file-level tracking** across sessions (only work_item IDs)
- ❌ **No prioritization** (newest-first) when building agent context
- ❌ **No cross-session file deduplication** (same file referenced multiple sessions)
- ❌ **Fixed limit** (3 sessions) regardless of token budget or relevance

### Zen's Approach

**Zen demonstrates**:
- **Dual prioritization**: Collect newest-first for token efficiency, present chronologically for LLM
- **File tracking**: Per-turn file references with newest-first deduplication
- **Token-aware history**: Intelligent exclusion of old content when constrained
- **Cross-tool continuation**: Any tool can resume conversation from any other tool
- **Structured memory**: ThreadContext → ConversationTurn[] → files/metadata

---

## 🔄 Conceptual Mapping

### Zen ↔ AIPM Parallels

| Zen Concept | AIPM Equivalent | Current Status |
|-------------|-----------------|----------------|
| **ThreadContext** | Session | ✅ Implemented |
| **ConversationTurn** | Session activity entry | ⚠️ Partial (metadata only) |
| **turn.files** | Files modified in session | ❌ Not tracked |
| **turn.timestamp** | Activity timestamp | ⚠️ Session-level only |
| **turn.tool_name** | Tool/agent attribution | ⚠️ Session-level only |
| **continuation_id** | Session resumption | ❌ Not implemented |
| **build_conversation_history()** | temporal_loader.load_recent_summaries() | ⚠️ Basic (3 sessions, no budgeting) |
| **get_conversation_file_list()** | N/A | ❌ Not implemented |
| **Token allocation (60/20/20)** | N/A | ❌ Not implemented |

---

## 💡 Enhancement Proposal

### Phase 1: Session Activity Tracking (Foundation)

**Goal**: Track fine-grained session activities with file references

**New Model**: `SessionActivity`
```python
class SessionActivity(BaseModel):
    """
    Single activity within a session (similar to Zen's ConversationTurn).

    Tracks agent actions, file modifications, decisions, and outcomes.
    """
    id: Optional[int] = None
    session_id: int  # FK to sessions table

    # Activity identification
    activity_type: str  # 'agent_action', 'file_edit', 'decision', 'blocker_resolved'
    timestamp: datetime

    # Agent attribution
    agent_role: Optional[str] = None  # Which agent performed this activity
    tool_name: Optional[str] = None   # Tool used (if applicable)

    # File tracking (KEY ENHANCEMENT)
    files_referenced: List[str] = Field(default_factory=list)
    files_modified: List[str] = Field(default_factory=list)

    # Activity details
    activity_summary: str  # Brief description (max 500 chars)
    activity_metadata: Dict[str, Any] = Field(default_factory=dict)

    # Relationships
    work_item_id: Optional[int] = None
    task_id: Optional[int] = None
```

**Database Migration**:
```sql
CREATE TABLE session_activities (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    activity_type TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    agent_role TEXT,
    tool_name TEXT,
    files_referenced TEXT,  -- JSON array
    files_modified TEXT,    -- JSON array
    activity_summary TEXT NOT NULL,
    activity_metadata TEXT, -- JSON
    work_item_id INTEGER REFERENCES work_items(id),
    task_id INTEGER REFERENCES tasks(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_activities_session
    ON session_activities(session_id, timestamp DESC);
CREATE INDEX idx_session_activities_files
    ON session_activities(files_modified);
```

**Integration Point**: WorkflowService emits events → SessionService creates activities

---

### Phase 2: Token-Aware Session History Builder

**Goal**: Implement Zen's dual prioritization strategy for session history

**New Service**: `SessionHistoryBuilder`
```python
class SessionHistoryBuilder:
    """
    Build token-aware session history for agent context assembly.

    Implements Zen's dual prioritization strategy:
    - PHASE 1: Collect newest-first (token budget priority)
    - PHASE 2: Present chronologically (LLM comprehension)
    """

    def build_session_history(
        self,
        work_item_id: int,
        token_budget: int,
        include_files: bool = True
    ) -> tuple[str, int]:
        """
        Build formatted session history within token budget.

        Args:
            work_item_id: Work item context
            token_budget: Maximum tokens for history
            include_files: Whether to embed file contents

        Returns:
            (formatted_history, tokens_used)

        Algorithm:
        1. Load sessions for work_item (newest first)
        2. Extract unique files across sessions (newest-first deduplication)
        3. Plan file inclusion within token budget
        4. Collect session activities (newest-first for budget)
        5. Reverse to chronological order (oldest-first for LLM)
        6. Format with file embeddings
        """
```

**Key Methods** (inspired by Zen):
```python
def get_session_file_list(sessions: List[Session]) -> List[str]:
    """
    Extract unique files across sessions with newest-first priority.

    Similar to Zen's get_conversation_file_list():
    - Walk backwards through sessions (newest to oldest)
    - For each session, process activities in reverse
    - When same file appears multiple times, newest reference wins
    """
    seen_files = set()
    file_list = []

    # REVERSE iteration (newest session first)
    for session in reversed(sessions):
        for activity in reversed(session.activities):
            for file_path in activity.files_modified:
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    file_list.append(file_path)  # Newest reference

    return file_list

def _plan_file_inclusion(files: List[str], max_tokens: int):
    """
    Plan which files to include based on token budget.

    Files already ordered newest-first from get_session_file_list().
    When budget exceeded, older files naturally excluded.
    """
    # ... (implementation similar to Zen's _plan_file_inclusion_by_size)
```

---

### Phase 3: Enhanced Context Assembly Integration

**Goal**: Integrate session history into ContextAssemblyService

**Enhanced TemporalContextLoader**:
```python
class TemporalContextLoader:
    """Enhanced with token-aware session history building."""

    def __init__(self, db, history_builder: SessionHistoryBuilder):
        self.db = db
        self.history_builder = history_builder  # NEW

    def load_token_aware_history(
        self,
        work_item_id: int,
        token_budget: int
    ) -> Dict[str, Any]:
        """
        Load session history within token budget.

        Returns:
            {
                'formatted_history': str,  # Markdown for agent
                'tokens_used': int,
                'sessions_included': int,
                'sessions_excluded': int,
                'files_embedded': List[str],
                'files_skipped': List[str]
            }
        """
        history, tokens = self.history_builder.build_session_history(
            work_item_id=work_item_id,
            token_budget=token_budget,
            include_files=True
        )

        return {
            'formatted_history': history,
            'tokens_used': tokens,
            # ... (metadata)
        }
```

**Context Assembly Update**:
```python
# In assembly_service.py:145-172 (_assemble_task_context_uncached)

# STEP 9: Load Temporal Context (ENHANCED)
temporal_context = self.temporal_loader.load_token_aware_history(
    work_item_id=work_item.id,
    token_budget=token_allocation.history_tokens  # From ModelContext
)

# Add to warnings if sessions were excluded
if temporal_context['sessions_excluded'] > 0:
    warnings.append(
        f"Session history limited: {temporal_context['sessions_excluded']} "
        f"older sessions excluded due to token budget"
    )
```

---

### Phase 4: Token Allocation Strategy

**Goal**: Implement Zen's 60/20/20 token allocation

**Enhanced ModelContext** (if we add multi-provider support):
```python
class TokenAllocation(BaseModel):
    """Token budget allocation for context assembly."""
    total_tokens: int
    content_tokens: int      # 60% - Files + Session History
    response_tokens: int     # 20% - Agent response space
    overhead_tokens: int     # 20% - System prompts, metadata

    # Sub-allocations within content budget
    file_tokens: int         # Files from amalgamations
    history_tokens: int      # Session history with file embeds
    metadata_tokens: int     # 6W, plugin facts, etc.

def calculate_token_allocation(model_name: str) -> TokenAllocation:
    """
    Calculate token allocation for model.

    Current implementation (Claude-only):
    - Total: 200,000 (Claude Sonnet context window)
    - Content (60%): 120,000
      - Files (50%): 60,000
      - History (30%): 36,000
      - Metadata (20%): 24,000
    - Response (20%): 40,000
    - Overhead (20%): 40,000
    """
```

---

## 📊 Comparison: Before vs After

### Before (Current State)

**Context Assembly for Task #355**:
```
1. Load entities (task, work_item, project)
2. Load 6W contexts (3 levels)
3. Merge 6W hierarchically
4. Load plugin facts
5. Get amalgamation paths (code files)
6. Calculate freshness
7. Calculate confidence
8. Inject agent SOP
9. Load temporal context:
   → Load 3 most recent sessions (FIXED LIMIT)
   → Format as markdown (NO TOKEN BUDGETING)
   → Include session summaries only (NO FILE TRACKING)
10. Filter by agent role
11. Return payload

LIMITATIONS:
- Always 3 sessions (even if only 1 relevant or 10 would fit)
- No file-level visibility across sessions
- No prioritization (oldest sessions included if <3 total)
- No token awareness (could overflow context window)
```

### After (Enhanced with Zen Patterns)

**Context Assembly for Task #355**:
```
1. Load entities (task, work_item, project)
2. Load 6W contexts (3 levels)
3. Merge 6W hierarchically
4. Load plugin facts
5. Get amalgamation paths (code files)
6. Calculate freshness
7. Calculate confidence
8. Inject agent SOP
9. Load temporal context (ENHANCED):
   → Calculate token budget (30% of content allocation)
   → Load sessions for work_item (newest first)
   → Extract unique files across sessions (newest-first deduplication)
   → Plan file inclusion within budget
   → Collect session activities (newest-first)
   → Embed file contents (once, no duplication)
   → Format chronologically (oldest-first for LLM)
   → Return formatted history with metadata
10. Filter by agent role
11. Return payload

BENEFITS:
- Dynamic session count (1-10+ based on token budget)
- File-level visibility (see exact files modified per session)
- Intelligent prioritization (newest sessions preferred)
- Token-aware (never overflow context window)
- File deduplication (same file embedded once with newest version)
```

---

## 🎯 Implementation Roadmap

### Phase 1: Foundation (Week 1-2) - **Extends WI-65**
**Work Item**: Enhance Rich Context System with Session Activities

**Tasks**:
1. **Design**: Session Activity Model & Schema (4h)
   - Define SessionActivity Pydantic model
   - Design database schema and indexes
   - Document activity types and metadata structure

2. **Implementation**: Session Activity Tracking (8h)
   - Create migration for session_activities table
   - Implement SessionActivity database methods
   - Integrate with WorkflowService event emission
   - Add file tracking to session activities

3. **Testing**: Session Activity Integration (4h)
   - Unit tests for SessionActivity model
   - Integration tests with WorkflowService
   - Validate file tracking accuracy

**Deliverables**:
- ✅ session_activities table with file tracking
- ✅ WorkflowService emits file-level activities
- ✅ Tests validating activity capture

---

### Phase 2: History Builder (Week 3-4) - **Extends WI-35**
**Work Item**: Token-Aware Session History Builder

**Tasks**:
1. **Design**: Session History Builder Architecture (6h)
   - Design SessionHistoryBuilder service
   - Define token allocation strategy (60/20/20)
   - Document dual prioritization algorithm

2. **Implementation**: Core History Building (12h)
   - Implement get_session_file_list() (newest-first)
   - Implement _plan_file_inclusion() (token budgeting)
   - Implement build_session_history() (dual strategy)
   - Add file embedding with deduplication

3. **Testing**: History Builder Validation (6h)
   - Test newest-first prioritization
   - Test token budget enforcement
   - Test file deduplication accuracy
   - Test chronological presentation

**Deliverables**:
- ✅ SessionHistoryBuilder service operational
- ✅ Token-aware history generation
- ✅ File deduplication working
- ✅ >90% test coverage

---

### Phase 3: Context Assembly Integration (Week 5) - **Enhances WI-65**
**Work Item**: Integrate Session History into Context Assembly

**Tasks**:
1. **Implementation**: Enhanced Temporal Loader (6h)
   - Extend TemporalContextLoader with history_builder
   - Implement load_token_aware_history()
   - Update context assembly to use new loader
   - Add warnings for excluded sessions

2. **Testing**: End-to-End Context Assembly (4h)
   - Test full context assembly with session history
   - Validate token budgets across all components
   - Test agent receives file-level session context

3. **Documentation**: Usage Guide (2h)
   - Document new session history features
   - Provide examples of file tracking
   - Explain token allocation strategy

**Deliverables**:
- ✅ Context assembly uses token-aware history
- ✅ Agents receive file-level session context
- ✅ Documentation complete

---

### Phase 4: Token Allocation Strategy (Week 6) - **Future Enhancement**
**Work Item**: Implement 60/20/20 Token Allocation

**Scope**: Multi-provider support (if AIPM adds Gemini/GPT-4)

**Tasks**:
1. Model-specific token limits
2. Dynamic allocation based on provider
3. Performance optimization

**Status**: DEFERRED until multi-provider support added

---

## 📈 Success Metrics

### Quantitative Metrics

| Metric | Before | Target | Measurement |
|--------|--------|--------|-------------|
| **Session context depth** | 3 sessions (fixed) | 5-10 sessions (dynamic) | Average sessions included in context |
| **File-level visibility** | 0% (no tracking) | 100% | % of sessions with file references |
| **Token utilization** | Unknown (no budgeting) | 85-95% of budget | Actual tokens / allocated tokens |
| **Context overflow incidents** | 2-3/week | 0/week | Context exceeding model limits |
| **Agent context relevance** | 60% (user feedback) | 85% | Agent reports session context helpful |

### Qualitative Benefits

1. **Agent Continuity**: Agents see what happened in previous sessions (similar to Zen's cross-tool continuation)
2. **File History**: Agents know which files were modified when (enables "what changed since last session?")
3. **Decision Traceability**: Agents reference specific decisions from past sessions
4. **Resource Efficiency**: Optimal use of context window (no overflow, no waste)
5. **Cross-Session Learning**: Patterns emerge from session-to-session progression

---

## 🔗 Integration with Existing Work

### WI-65: Rich Context System (In Progress)

**Current Focus**: Business context (6W, market research, stakeholders)
**Enhancement**: Add **temporal dimension** (session history, file evolution)

**Synergy**:
- Rich context provides "what" (business goals, quality gates)
- Session history provides "how" (how we got here, what we tried)
- Together: Complete context = business goals + execution history

**Example**:
```
Agent receives context for Task #355:

BUSINESS CONTEXT (from WI-65):
- Work Item: OAuth2 Integration
- Business Goal: Enable enterprise SSO
- Quality Gates: Security audit required
- Stakeholders: Security team approval needed

SESSION HISTORY (from enhanced WI-35):
- Session 1 (3 days ago): Researched OAuth2 libraries
  Files: docs/research/oauth2-comparison.md
  Decision: Use authlib (mature, well-documented)

- Session 2 (2 days ago): Implemented basic OAuth2 flow
  Files: auth/oauth2.py, auth/providers/google.py
  Blocker: PKCE not working with refresh tokens

- Session 3 (1 day ago): Fixed PKCE implementation
  Files: auth/oauth2.py (modified), tests/test_oauth2.py
  Resolved: PKCE working, 95% test coverage

→ Agent sees BOTH business goals AND execution history
```

---

### WI-35: Session Management System (Review)

**Current Scope**: Database persistence for sessions
**Enhancement**: Transform from **archival** to **operational** system

**Before WI-35**: Sessions captured but not queryable
**After WI-35**: Sessions queryable with history
**With This Enhancement**: Sessions used for **real-time agent context**

**Evolution**:
```
WI-35 (Original):
  - Store sessions in database
  - Query session history
  - Analytics on session patterns

WI-35 + This Enhancement:
  - Store sessions with activity-level detail
  - Track files per activity
  - Build token-aware history for agents
  - Enable cross-session file deduplication
  - Provide operational context (not just archival)
```

---

## 🚧 Implementation Considerations

### Database Performance

**Challenge**: Session activities could grow large (100+ activities per session)

**Mitigation**:
```sql
-- Indexes for fast queries
CREATE INDEX idx_session_activities_session_time
    ON session_activities(session_id, timestamp DESC);

CREATE INDEX idx_session_activities_files
    ON session_activities(files_modified);

-- Partition by date (future optimization)
-- Keep recent activities in hot storage
-- Archive old activities to cold storage after 90 days
```

**Query Pattern**:
```python
# Efficient query (uses index)
SELECT * FROM session_activities
WHERE session_id IN (recent_session_ids)
ORDER BY timestamp DESC
LIMIT 100;

# File tracking (uses index)
SELECT DISTINCT files_modified
FROM session_activities
WHERE session_id IN (recent_session_ids)
AND files_modified IS NOT NULL;
```

---

### Token Budget Calibration

**Challenge**: Balance history depth vs file content

**Strategy**:
```python
# Content allocation (60% of context window)
content_tokens = 120_000

# Sub-allocation
file_tokens = int(content_tokens * 0.50)      # 60,000 - Amalgamations
history_tokens = int(content_tokens * 0.30)   # 36,000 - Session history
metadata_tokens = int(content_tokens * 0.20)  # 24,000 - 6W, plugins

# Session history budget breakdown
history_tokens = 36_000
  - File embeddings: ~20,000 (5-10 files)
  - Session summaries: ~10,000 (5-8 sessions)
  - Activity details: ~6,000 (key activities)
```

**Adaptive Strategy**:
- If many files referenced → reduce session detail, increase file embeds
- If few files referenced → increase session detail, reduce file budget
- Always prioritize newest sessions and files

---

### File Deduplication Algorithm

**Challenge**: Same file modified across multiple sessions

**Solution** (from Zen):
```python
def get_session_file_list(sessions: List[Session]) -> List[str]:
    """
    Extract unique files with newest-first priority.

    Example:
        Session 1 (3 days ago): [auth.py, config.py]
        Session 2 (2 days ago): [test_auth.py]
        Session 3 (1 day ago): [auth.py, oauth.py]  # auth.py again

        Result: [auth.py, oauth.py, test_auth.py, config.py]
                 ^^^^^^^^ from Session 3 (newest reference)
    """
    seen_files = set()
    file_list = []

    # REVERSE: newest session first
    for session in reversed(sessions):
        for activity in reversed(session.activities):
            for file_path in activity.files_modified:
                if file_path not in seen_files:
                    seen_files.add(file_path)
                    file_list.append(file_path)  # First occurrence = newest

    return file_list
```

**Benefit**: File embedded once with most recent content, no duplication waste

---

## 🎓 Learning from Zen

### Pattern 1: Dual Collection Strategy

**Zen's Insight**: Collect newest-first (for token efficiency), present chronologically (for LLM understanding)

**AIPM Application**:
```python
# PHASE 1: Collection (newest-first for budget)
sessions_to_include = []
for session in reversed(all_sessions):  # Newest first
    if token_budget_exceeded:
        break  # Exclude oldest sessions
    sessions_to_include.append(session)

# PHASE 2: Presentation (chronological for LLM)
sessions_to_include.reverse()  # Oldest first for natural flow

formatted_history = format_sessions_chronologically(sessions_to_include)
```

---

### Pattern 2: Graceful Degradation

**Zen's Insight**: Never fail hard on missing data, always degrade gracefully

**AIPM Application**:
```python
# If session activities missing
if not session.activities:
    warnings.append(f"Session {session.id} has no activities (metadata only)")
    # Continue with session-level summary

# If files not accessible
for file_path in files_to_embed:
    try:
        content = read_file(file_path)
        embedded_files.append(content)
    except FileNotFoundError:
        warnings.append(f"File {file_path} no longer accessible")
        # Continue with other files

# If token budget very tight
if available_tokens < minimum_threshold:
    warnings.append("Token budget tight - showing most recent session only")
    sessions = sessions[:1]  # Just most recent
```

---

### Pattern 3: Structured Memory

**Zen's Insight**: Clear data structures for conversation state

**AIPM Application**:
```python
# Clear hierarchy
Session
  ├── metadata: SessionMetadata
  ├── activities: List[SessionActivity]
  │   ├── files_referenced: List[str]
  │   ├── files_modified: List[str]
  │   ├── agent_role: str
  │   └── activity_metadata: Dict
  └── summary: str

# Similar to Zen's ThreadContext → ConversationTurn[]
```

---

## 🚀 Quick Wins (Can Start Now)

### 1. Add File Tracking to SessionMetadata (2h)

**Current** (`models/session.py:76-83`):
```python
class SessionMetadata(BaseModel):
    work_items_touched: List[int] = Field(default_factory=list)
    tasks_completed: List[int] = Field(default_factory=list)
    # ... other fields
```

**Enhanced**:
```python
class SessionMetadata(BaseModel):
    work_items_touched: List[int] = Field(default_factory=list)
    tasks_completed: List[int] = Field(default_factory=list)

    # NEW: File tracking
    files_modified: List[str] = Field(
        default_factory=list,
        description="Files modified during session"
    )
    files_created: List[str] = Field(
        default_factory=list,
        description="Files created during session"
    )
    files_deleted: List[str] = Field(
        default_factory=list,
        description="Files deleted during session"
    )
```

**Integration**: WorkflowService tracks git changes, populates these fields

---

### 2. Token Estimation Utility (1h)

**Add to** `agentpm/utils/token_utils.py`:
```python
def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses simple heuristic: ~4 characters per token (average for code/text)

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4

def calculate_token_budget(context_window: int = 200_000) -> dict:
    """
    Calculate token allocation for context assembly.

    Uses 60/20/20 strategy from Zen MCP Server.

    Args:
        context_window: Model context window (default: 200k for Claude)

    Returns:
        {
            'total': 200000,
            'content': 120000,      # 60%
            'response': 40000,      # 20%
            'overhead': 40000,      # 20%
            'sub_allocation': {
                'files': 60000,     # 50% of content
                'history': 36000,   # 30% of content
                'metadata': 24000   # 20% of content
            }
        }
    """
    content = int(context_window * 0.60)
    response = int(context_window * 0.20)
    overhead = int(context_window * 0.20)

    return {
        'total': context_window,
        'content': content,
        'response': response,
        'overhead': overhead,
        'sub_allocation': {
            'files': int(content * 0.50),
            'history': int(content * 0.30),
            'metadata': int(content * 0.20)
        }
    }
```

---

### 3. Enhanced Temporal Loader (3h)

**Add method to** `temporal_loader.py`:
```python
def load_with_file_context(
    self,
    work_item_id: int,
    max_sessions: int = 5
) -> Dict[str, Any]:
    """
    Load session summaries with file context.

    Enhanced version that includes files modified per session.
    Prepares for future token-aware implementation.

    Args:
        work_item_id: Work item ID
        max_sessions: Maximum sessions to load

    Returns:
        {
            'sessions': [...],
            'unique_files': [...],  # All files across sessions
            'file_session_map': {file: [session_ids]}  # Which sessions touched which files
        }
    """
    summaries = self.load_recent_summaries(work_item_id, limit=max_sessions)

    # Extract files from session metadata
    unique_files = set()
    file_session_map = {}

    for summary in summaries:
        metadata = summary.get('metadata', {})
        files = metadata.get('files_modified', [])

        for file_path in files:
            unique_files.add(file_path)
            if file_path not in file_session_map:
                file_session_map[file_path] = []
            file_session_map[file_path].append(summary['session_id'])

    return {
        'sessions': summaries,
        'unique_files': list(unique_files),
        'file_session_map': file_session_map
    }
```

---

## 📚 References

### Zen MCP Server Patterns

**Key Files to Study**:
1. `utils/conversation_memory.py` (1,108 lines)
   - `get_conversation_file_list()`: Newest-first file prioritization (lines 433-502)
   - `build_conversation_history()`: Dual collection strategy (lines 638-1027)
   - `_plan_file_inclusion_by_size()`: Token budgeting (lines 577-635)

2. `server.py` (1,522 lines)
   - `reconstruct_thread_context()`: Context reconstruction (lines 965-1284)
   - `handle_call_tool()`: Thread resumption logic (lines 690-876)

3. `utils/model_context.py`
   - Token allocation strategy (60/20/20 split)
   - Provider-agnostic token estimation

**Documentation**:
- `/Users/nigelcopley/.project_manager/aipm-v2/docs/analysis/ZEN_MCP_GOLDEN_NUGGETS.md`

---

### AIPM Current Implementation

**Relevant Files**:
1. `agentpm/core/context/assembly_service.py` (793 lines)
   - `_assemble_task_context_uncached()`: 11-step assembly pipeline (lines 145-337)
   - Context merging and scoring logic

2. `agentpm/core/context/temporal_loader.py` (179 lines)
   - `load_recent_summaries()`: Current session loading (lines 37-96)
   - `format_for_agent()`: Markdown formatting (lines 98-178)

3. `agentpm/core/database/models/session.py` (259 lines)
   - Session and SessionMetadata models
   - Current session tracking structure

---

## 💼 Business Value

### For Agents

1. **Better Context**: Agents see full history, not just last 3 sessions
2. **File Awareness**: Agents know which files changed when
3. **Decision Continuity**: Agents reference past decisions accurately
4. **Reduced Hallucination**: More context = fewer assumptions

### For Users

1. **Faster Onboarding**: New sessions pick up where previous left off
2. **Fewer Repeats**: Agents don't ask for context already provided
3. **Better Handovers**: Cross-agent handoffs preserve full context
4. **Transparency**: Users see what context agents receive

### For System

1. **Resource Efficiency**: Optimal context window utilization
2. **Scalability**: Token budgeting prevents overflow
3. **Quality**: Structured memory improves agent performance
4. **Debugging**: Session activities provide audit trail

---

## 🏁 Conclusion

**Core Recommendation**: Enhance AIPM's existing session infrastructure with Zen's conversation memory patterns. This transforms sessions from archival storage to operational agent memory.

**Strategic Fit**: Directly enhances WI-65 (Rich Context) and WI-35 (Session Management) without creating new work items. Builds on existing foundations rather than replacing them.

**Implementation Approach**: Incremental phases over 6 weeks, each delivering value independently. No big-bang migration, no breaking changes.

**Key Insight**: AIPM already has the right data structures (Sessions, SessionMetadata). We just need to:
1. Add file-level tracking (SessionActivity model)
2. Implement token-aware history builder (SessionHistoryBuilder)
3. Integrate with context assembly (enhanced TemporalContextLoader)

**Expected Impact**: Agents gain 5-10 sessions of context (vs 3 currently), see file-level changes, reference specific past decisions, and utilize context window efficiently.

**Next Steps**:
1. **Review this proposal** with team
2. **Update WI-65** to include Session Activity tracking
3. **Refine WI-35** to include History Builder component
4. **Create tasks** for Phase 1 (Foundation)

---

*Analysis completed by Claude Code on 2025-10-14*
*Based on Zen MCP Server patterns and APM (Agent Project Manager) architecture*
