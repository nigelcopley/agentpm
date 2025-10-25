# File-Based vs Database-Driven System Inventory

**Analysis Date**: 2025-10-16
**Objective**: Identify file-based systems that should be database-driven for consistency and reliability

## Executive Summary

**Critical Findings**:
- **4 systems** currently use mixed file/database approaches (Rules, Contexts, Agents, Documents)
- **Rules System**: ✅ CORRECT - Database is source of truth, files only for initialization
- **Contexts System**: ⚠️ MIXED - Amalgamation files (.aipm/contexts/*.txt) still filesystem-based
- **Agents System**: ⚠️ MIXED - SOP content in database, but files still read at runtime
- **Documents System**: ✅ CORRECT - Database tracks references, files stored on filesystem
- **Templates System**: ✅ CORRECT - Read-only templates, appropriate for filesystem

**Database Schema Coverage**:
```
✅ rules (database source of truth)
✅ contexts (6W data in database)
✅ agents (metadata + SOP content in database)
✅ document_references (metadata in database, files on disk)
✅ sessions (fully database-driven)
✅ evidence_sources (metadata in database, content referenced)
```

---

## 1. Rules System

### Current Architecture
**Primary Location**: Database (`rules` table)
**File Usage**: `_RULES/` directory + `agentpm/core/rules/config/rules_catalog.yaml`
**Source of Truth**: ✅ **Database** (correct)

### Database Schema
```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    rule_id TEXT,           -- e.g., 'DP-001'
    name TEXT,
    description TEXT,
    category TEXT,
    enforcement_level TEXT, -- BLOCK, LIMIT, ENHANCE, GUIDE
    validation_logic TEXT,
    error_message TEXT,
    config TEXT,            -- JSON config
    enabled INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### File Usage Analysis
**File**: `agentpm/core/rules/loader.py`
```python
# CORRECT PATTERN (WI-40 compliant)
def _load_catalog(self) -> dict:
    """Load catalog from database only.

    At runtime, rules should ONLY come from the database.
    YAML file is only used during `apm init` to populate the database.
    """
    if self.project_id:
        # Use only database at runtime - no YAML fallback
        return self._load_from_database()

    raise RuntimeError(
        "Rules must be loaded from database. Run 'apm init' to populate."
    )
```

### Migration References
**Found 5 files** referencing `_RULES/` directory:
1. `agentpm/cli/commands/migrate_v1.py` - Migration script (historical)
2. `tests-BAK/integration/test_v2_consolidation.py` - Test (archived)
3. `scripts/define_mini_orchestrators.py` - Script (not production)
4. `agentpm/core/migrations/v1_detection.py` - Migration helper
5. `agentpm/core/migrations/migrate_rules.py` - Migration utility

**Status**: ✅ **CORRECT** - No production code reads `_RULES/` at runtime

### Obsolete Code Patterns
**NONE FOUND** - All runtime code uses database via:

```python
from agentpm.core.database.methods import rules

rules.list_rules(db, project_id=1)
rules.get_rule_by_rule_id(db, project_id=1, rule_id='DP-001')
```

### Recommendation
**NO ACTION REQUIRED** - Rules system is fully database-driven with correct separation:
- YAML catalog = initialization data source (apm init only)
- Database = runtime source of truth
- `_RULES/` directory = legacy/documentation only

---

## 2. Contexts System

### Current Architecture
**Primary Location**: Database (`contexts` table) + Filesystem (`.aipm/contexts/`)
**Mixed Usage**: ⚠️ **PROBLEMATIC**
- **6W Data**: Database (correct)
- **Amalgamation Files**: Filesystem (should be database?)

### Database Schema
```sql
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    context_type TEXT,           -- PROJECT_CONTEXT, TASK_CONTEXT, etc.
    file_path TEXT,              -- ⚠️ Still storing file paths
    file_hash TEXT,
    resource_type TEXT,
    entity_type TEXT,
    entity_id INTEGER,
    six_w_data TEXT,             -- JSON 6W data (WHO, WHAT, WHEN, WHERE, WHY, HOW)
    confidence_score REAL,
    confidence_band TEXT,
    confidence_factors TEXT,     -- JSON
    context_data TEXT,           -- JSON additional context
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### File Usage Analysis

#### Amalgamation Files (⚠️ PROBLEMATIC)
**Location**: `.aipm/contexts/*.txt`
**Examples**:
- `lang_python_classes.txt` - Python class definitions
- `lang_python_functions.txt` - Function signatures
- `framework_click_commands.txt` - CLI commands
- `framework_click_groups.txt` - Click groups
- `testing_pytest_fixtures.txt` - Pytest fixtures

**Code Pattern**:
```python
# From: agentpm/core/context/assembly_service.py:405
def _get_amalgamation_paths(self) -> Dict[str, str]:
    """Get code amalgamation file paths.

    Returns:
        {type: file_path} mapping
    """
    amalg_dir = self.project_path / '.aipm' / 'contexts'

    if not amalg_dir.exists():
        return {}

    # ⚠️ PROBLEM: Scanning filesystem at runtime
    amalgamations = {}
    for f in amalg_dir.glob('*.txt'):
        amalgamations[amalg_type] = str(f)  # Returning file paths

    return amalgamations
```

### Context Assembly Usage (MIXED)
**Found 13 files** using `.aipm/contexts/`:

**Primary Files**:
1. `agentpm/core/context/assembly_service.py` - ⚠️ Reads amalgamation files at runtime
2. `agentpm/core/context/role_filter.py` - Uses amalgamations from assembly service
3. `agentpm/core/plugins/orchestrator.py` - Generates amalgamation files
4. `agentpm/core/plugins/base/plugin_interface.py` - Plugin contract for amalgamations

**Pattern**:
```python
# Current pattern (MIXED)
amalgamations = self._get_amalgamation_paths()  # Returns file paths
# Later: Read files when needed
content = Path(amalg_path).read_text()

# Should be:
amalgamations = context_methods.get_amalgamations(db, project_id, entity_id)
# Returns: {type: content} directly from database
```

### File-to-Database Migration Path

#### Option 1: Store Amalgamation Content in Database
```sql
-- New table
CREATE TABLE amalgamations (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    entity_type TEXT,        -- PROJECT, WORK_ITEM, TASK
    entity_id INTEGER,
    amalgamation_type TEXT,  -- 'classes', 'functions', 'fixtures', etc.
    content TEXT,            -- Full amalgamation content
    content_hash TEXT,       -- SHA256 for change detection
    generated_at TIMESTAMP,
    refreshed_at TIMESTAMP,
    UNIQUE(project_id, entity_id, amalgamation_type)
)
```

**Advantages**:
- Single source of truth
- No filesystem dependencies
- Transactional updates
- Easier backup/restore

**Disadvantages**:
- Larger database size
- Harder to inspect/debug (can't just `cat` file)

#### Option 2: Store Amalgamation Metadata in Database (Hybrid)
```sql
-- Store references only
CREATE TABLE amalgamation_references (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    entity_id INTEGER,
    amalgamation_type TEXT,
    file_path TEXT,          -- Relative to project root
    file_hash TEXT,
    line_count INTEGER,
    size_bytes INTEGER,
    last_generated TIMESTAMP,
    UNIQUE(project_id, entity_id, amalgamation_type)
)
```

**Advantages**:
- Files remain inspectable
- Database tracks metadata
- Smaller database size

**Disadvantages**:
- Still filesystem-dependent
- Two-phase operations (DB + file)

#### Recommendation: Option 1 (Full Database Storage)
**Reasoning**:
1. Amalgamations are **generated artifacts**, not source code
2. Size is manageable (typically <100KB per amalgamation)
3. Consistency is more important than inspectability
4. Aligns with database-first architecture

### Obsolete Code Locations
**Files that should stop reading `.aipm/contexts/` directly**:
- `agentpm/core/context/assembly_service.py:405` - `_get_amalgamation_paths()`
- Any plugin that writes amalgamations to `.aipm/contexts/`

### Migration Strategy
```python
# Step 1: Create amalgamations table (new migration)
# Step 2: Update PluginOrchestrator to write to database
# Step 3: Update ContextAssemblyService to read from database
# Step 4: Migrate existing .aipm/contexts/ files to database
# Step 5: Deprecate filesystem amalgamations
```

---

## 3. Agents System

### Current Architecture
**Primary Location**: Database (`agents` table) + Filesystem (`.claude/agents/`)
**Mixed Usage**: ⚠️ **PROBLEMATIC**
- **Agent Metadata**: Database (correct)
- **SOP Content**: Database (`agents.sop_content`) + Files (`.claude/agents/*.md`)
- **Runtime Reads**: Still reading files despite database storage

### Database Schema
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    role TEXT,                  -- 'aipm-database-developer'
    display_name TEXT,
    description TEXT,
    sop_content TEXT,          -- ✅ SOP stored in database
    capabilities TEXT,         -- JSON list
    is_active INTEGER,
    agent_type TEXT,
    file_path TEXT,            -- ⚠️ Still storing file path
    generated_at TIMESTAMP,
    tier INTEGER,              -- 1=sub, 2=mini, 3=master
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### File Usage Analysis

#### Agent SOP Files (⚠️ PROBLEMATIC)
**Location**: `.claude/agents/*.md`
**Pattern**:
```python
# From: agentpm/core/context/sop_injector.py:46
def load_sop(self, project_id: int, agent_role: str, db=None) -> Optional[str]:
    """Load agent SOP from filesystem.

    Strategy:
    1. Check database for custom SOP path
    2. Fallback to .claude/agents/{role}.md
    3. Read file from filesystem
    """
    # ⚠️ PROBLEM: Reading from filesystem even when database has sop_content
    if db:
        agent = agents.get_agent_by_role(db, project_id, agent_role)
        if agent and agent.file_path:
            custom_sop_path = self.project_path / agent.file_path
            return self._read_sop_with_cache(custom_sop_path, agent_role)

    # Fallback to filesystem
    default_sop = self.project_path / '.claude' / 'agents' / f'{agent_role}.md'
    return self._read_sop_with_cache(default_sop, agent_role)
```

**ISSUE**: Code reads files even though `agents.sop_content` column exists

### Current Database Population
**From**: `agentpm/core/agents/generator.py:539`
```python
def generate_and_store_agents(db, project_id, ...):
    """Generate agents and store in database + filesystem."""

    # Create Agent model
    agent = Agent(
        role=agent_def.get('name'),
        # ... other fields ...
    )

    # Save to database
    created = agent_methods.create_agent(db, agent)

    # ⚠️ PROBLEM: Write SOP file after database save
    sop_content = agent_def.get('instructions')
    file_path = write_agent_sop_file(
        agent_output_dir,
        created.role,
        sop_content,
        project_rules=project_rules
    )

    # Mark as generated (updates file_path)
    agent_methods.mark_agent_generated(db, created.id, str(file_path))
```

**Issue**: Dual writes - database gets metadata, files get SOP content

### Database-First Refactoring Plan

#### Phase 1: Store SOP in Database (ALREADY DONE)
```sql
-- Schema already supports it
agents.sop_content TEXT  -- Already exists
```

#### Phase 2: Update Generation to Store SOP Content
```python
# agentpm/core/agents/generator.py
def generate_and_store_agents(db, project_id, ...):
    # Create Agent model WITH sop_content
    agent = Agent(
        role=agent_def.get('name'),
        sop_content=agent_def.get('instructions'),  # ✅ Store in database
        file_path=f".claude/agents/{agent_def.get('name')}.md"  # Keep for reference
    )

    # Save to database (includes sop_content)
    created = agent_methods.create_agent(db, agent)

    # OPTIONAL: Write file for human inspection (not for runtime use)
    if write_files_for_inspection:
        write_agent_sop_file(agent_output_dir, created.role, created.sop_content)
```

#### Phase 3: Update SOP Injection to Read from Database
```python
# agentpm/core/context/sop_injector.py
def load_sop(self, project_id: int, agent_role: str, db) -> Optional[str]:
    """Load agent SOP from DATABASE (not filesystem)."""
    if not db:
        raise ValueError("Database required for SOP loading")

    agent = agents.get_agent_by_role(db, project_id, agent_role)

    if not agent:
        return None

    if not agent.is_active:
        raise AgentValidationError(f"Agent '{agent_role}' is inactive")

    # ✅ Return SOP from database
    return agent.sop_content
```

### Obsolete Code Patterns
**Files that should stop reading `.claude/agents/*.md`**:
- `agentpm/core/context/sop_injector.py:46` - `load_sop()` method
- `agentpm/core/agents/generator.py:501` - `write_agent_sop_file()` (make optional)

**Found 19 files** referencing `.claude/agents/`:
- Most are scripts, tests, or agent generation code
- Only `sop_injector.py` reads files at runtime (CRITICAL)

### Migration Strategy
```python
# Step 1: Update agent_methods.create_agent() to accept sop_content
# Step 2: Update generate_and_store_agents() to pass sop_content
# Step 3: Update sop_injector.load_sop() to read from database
# Step 4: Make file writing optional (for inspection only)
# Step 5: Run migration to populate sop_content for existing agents
```

### Recommendation
**MIGRATE TO DATABASE** - SOP content should be database-first:
- Files = optional human-readable export
- Database = runtime source of truth
- Agents table already has `sop_content` column

---

## 4. Documents System

### Current Architecture
**Primary Location**: Database (`document_references` table) + Filesystem (actual files)
**Current Usage**: ✅ **CORRECT** (hybrid approach is appropriate)

### Database Schema
```sql
CREATE TABLE document_references (
    id INTEGER PRIMARY KEY,
    entity_type TEXT,         -- WORK_ITEM, TASK, IDEA
    entity_id INTEGER,
    file_path TEXT,           -- Relative path to actual document
    document_type TEXT,       -- PRD, DESIGN, TESTING, ANALYSIS, etc.
    title TEXT,
    description TEXT,
    file_size_bytes INTEGER,
    content_hash TEXT,        -- SHA256 for change detection
    format TEXT,              -- MD, PDF, DOCX, etc.
    created_by TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Usage Analysis
**Found 10 files** using `document_references`:

**Primary Usage**:
1. `agentpm/core/database/methods/document_references.py` - CRUD operations
2. `agentpm/core/database/adapters/document_reference_adapter.py` - Data mapping
3. `agentpm/core/context/assembly_service.py:663` - Context assembly
4. `agentpm/web/routes/research.py` - Web interface

**Pattern** (CORRECT):
```python
# Store metadata in database
doc_ref = DocumentReference(
    entity_type=EntityType.WORK_ITEM,
    entity_id=45,
    file_path='docs/work-items/wi-45-design.md',  # Relative path
    document_type=DocumentType.DESIGN,
    title='WI-45 Design Document',
    content_hash='sha256:...'
)
document_references.create_document(db, doc_ref)

# Read file content when needed
content = Path(doc_ref.file_path).read_text()
```

### Recommendation
**NO ACTION REQUIRED** - Documents system correctly uses:
- Database = metadata tracking, relationships, search
- Filesystem = actual document storage (files are large, varied formats)
- This is the correct pattern for document management

---

## 5. Templates System

### Current Architecture
**Location**: Filesystem only (`agentpm/templates/`)
**Usage**: ✅ **CORRECT** (read-only reference data)

### Directory Structure
```
agentpm/templates/
├── agents/             # Agent SOP templates
├── json/              # JSON templates (tasks, work_items)
├── work_items/        # Work item templates
└── tasks/             # Task templates
```

### Usage Analysis
**Found 2 files** using `Path(__file__).parent / "templates"`:
1. `tests-BAK/integration/test_agent_workflow.py` - Test fixture
2. `agentpm/cli/commands/agents/generate.py` - Agent generation

**Pattern** (CORRECT):
```python
# Read-only template loading
template_path = Path(__file__).parent / "templates" / "agents" / "implementer.md"
template_content = template_path.read_text()
# Fill template with project-specific data
filled = template_content.replace('[PLACEHOLDER]', actual_value)
```

### Recommendation
**NO ACTION REQUIRED** - Templates are:
- Read-only reference data
- Version-controlled with code
- Not project-specific (same for all projects)
- Appropriately filesystem-based

---

## 6. Sessions System

### Current Architecture
**Location**: Database only (`sessions` and `session_events` tables)
**Usage**: ✅ **CORRECT** (fully database-driven)

### Database Schema
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    project_id INTEGER,
    tool_name TEXT,
    llm_model TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    status TEXT,
    session_type TEXT,
    exit_reason TEXT,
    metadata TEXT,           -- JSON
    created_at TIMESTAMP
)

CREATE TABLE session_events (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    event_type TEXT,
    event_category TEXT,
    event_severity TEXT,
    session_id INTEGER,
    timestamp TEXT,
    source TEXT,
    event_data TEXT,         -- JSON
    work_item_id INTEGER,
    task_id INTEGER,
    created_at TIMESTAMP
)
```

### Usage Analysis
**No file-based patterns found** - All session data stored in database:

```python
from agentpm.core.database.methods import sessions

session = sessions.create_session(db, session_data)
sessions.add_event(db, event_data)
sessions.get_session_history(db, project_id)
```

### Recommendation
**NO ACTION REQUIRED** - Sessions are fully database-driven (correct pattern)

---

## 7. Evidence System

### Current Architecture
**Location**: Database (`evidence_sources` table) + External URLs
**Usage**: ✅ **CORRECT** (metadata in database, content referenced)

### Database Schema
```sql
CREATE TABLE evidence_sources (
    id INTEGER PRIMARY KEY,
    entity_type TEXT,         -- WORK_ITEM, TASK, IDEA
    entity_id INTEGER,
    url TEXT,                 -- External URL or internal file path
    source_type TEXT,         -- PRIMARY, SECONDARY, INTERNAL
    excerpt TEXT,             -- ≤500 chars
    captured_at TIMESTAMP,
    content_hash TEXT,
    confidence REAL,
    created_by TEXT,
    created_at TIMESTAMP
)
```

### Recommendation
**NO ACTION REQUIRED** - Evidence correctly stores:
- Metadata in database
- Content referenced by URL (external) or file path (internal)

---

## Summary Table

| System | Current State | Database Table | File Location | Source of Truth | Status | Action Required |
|--------|---------------|----------------|---------------|-----------------|--------|-----------------|
| **Rules** | Hybrid | `rules` | `_RULES/` + `rules_catalog.yaml` | ✅ Database | ✅ CORRECT | None - WI-40 complete |
| **Contexts (6W)** | Database | `contexts` | None | ✅ Database | ✅ CORRECT | None |
| **Contexts (Amalg)** | Filesystem | None | `.aipm/contexts/*.txt` | ⚠️ Files | ⚠️ MIXED | Migrate to database |
| **Agents (Meta)** | Database | `agents` | None | ✅ Database | ✅ CORRECT | None |
| **Agents (SOP)** | Mixed | `agents.sop_content` | `.claude/agents/*.md` | ⚠️ Files | ⚠️ MIXED | Read from database |
| **Documents** | Hybrid | `document_references` | `docs/`, etc. | ✅ Both | ✅ CORRECT | None - appropriate |
| **Templates** | Filesystem | None | `agentpm/templates/` | ✅ Files | ✅ CORRECT | None - appropriate |
| **Sessions** | Database | `sessions`, `session_events` | None | ✅ Database | ✅ CORRECT | None |
| **Evidence** | Database | `evidence_sources` | External URLs | ✅ Database | ✅ CORRECT | None |

---

## Priority Actions

### 1. HIGH PRIORITY: Fix Agent SOP Loading
**Issue**: `sop_injector.py` reads `.claude/agents/*.md` files instead of `agents.sop_content`

**Impact**:
- Dual maintenance burden (database + files)
- Risk of inconsistency
- Filesystem dependency for runtime

**Solution**:
```python
# agentpm/core/context/sop_injector.py
def load_sop(self, project_id: int, agent_role: str, db) -> Optional[str]:
    """Load SOP from database (not filesystem)."""
    agent = agents.get_agent_by_role(db, project_id, agent_role)
    if agent and agent.is_active:
        return agent.sop_content  # ✅ Read from database
    return None
```

**Files to Change**:
- `agentpm/core/context/sop_injector.py:46-110` - Replace filesystem read with database read
- `agentpm/core/agents/generator.py:539-626` - Populate `sop_content` in database
- Optional: Keep file writing for human inspection (debug mode)

**Migration**:
```sql
-- Populate sop_content from existing files
UPDATE agents
SET sop_content = (
    SELECT content FROM read_file(file_path)
)
WHERE sop_content IS NULL AND file_path IS NOT NULL;
```

### 2. MEDIUM PRIORITY: Migrate Amalgamations to Database
**Issue**: `.aipm/contexts/*.txt` files used at runtime

**Impact**:
- Filesystem dependency for context assembly
- Harder to track changes/versions
- No transactional guarantees

**Solution**:
Create `amalgamations` table and migrate generation logic

**Files to Change**:
- `agentpm/core/context/assembly_service.py:405-434` - Read from database
- `agentpm/core/plugins/orchestrator.py` - Write to database
- New: `agentpm/core/database/methods/amalgamations.py` - CRUD methods
- New: `agentpm/core/database/migrations/files/migration_00XX.py` - Schema

**Schema**:
```sql
CREATE TABLE amalgamations (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    entity_type TEXT,
    entity_id INTEGER,
    amalgamation_type TEXT,
    content TEXT,
    content_hash TEXT,
    line_count INTEGER,
    generated_at TIMESTAMP,
    refreshed_at TIMESTAMP,
    UNIQUE(project_id, entity_id, amalgamation_type)
)
```

### 3. LOW PRIORITY: Cleanup Obsolete File References
**Issue**: Scripts and tests still reference old file-based patterns

**Files to Review**:
- `agentpm/cli/commands/migrate_v1.py` - V1 migration (keep for historical)
- `agentpm/core/migrations/v1_detection.py` - V1 detection (keep for migration)
- `tests-BAK/**` - Archived tests (can delete)
- `scripts/**` - Utility scripts (verify usage)

**Action**: Audit and remove/update references to:
- `_RULES/` directory (except migrations)
- `.aipm/contexts/` direct file access
- `.claude/agents/` runtime file reads

---

## Implementation Roadmap

### Phase 1: Agent SOP Database Migration (Week 1)
1. ✅ Schema ready (`agents.sop_content` exists)
2. Update `sop_injector.py` to read from database
3. Update `generator.py` to populate `sop_content`
4. Migration script to populate existing agents
5. Optional: Keep file writing for debug/inspection

**Success Criteria**:
- All agent SOPs loaded from database
- No runtime filesystem reads for SOPs
- Files optional (generated for inspection only)

### Phase 2: Amalgamation Database Migration (Week 2-3)
1. Create `amalgamations` table schema
2. Implement `amalgamations.py` methods (CRUD)
3. Update `PluginOrchestrator` to write to database
4. Update `ContextAssemblyService` to read from database
5. Migration script to import `.aipm/contexts/*.txt`
6. Keep files for backward compatibility (deprecated)

**Success Criteria**:
- All amalgamations stored in database
- Context assembly reads from database
- `.aipm/contexts/` files deprecated (not deleted yet)

### Phase 3: Cleanup and Documentation (Week 4)
1. Update documentation to reflect database-first architecture
2. Remove or deprecate obsolete file-based code
3. Add database-first guidelines to contributor docs
4. Update test fixtures to use database

**Success Criteria**:
- Clear documentation on what goes in database vs files
- No ambiguity about source of truth
- Tests reflect current architecture

---

## Architectural Guidelines

### Database-First Decision Tree

**Use Database When**:
- ✅ Data changes at runtime (rules, sessions, work items)
- ✅ Data is queried frequently (contexts, agents)
- ✅ Data has relationships (tasks → work items → projects)
- ✅ Transactional consistency matters (events, state changes)
- ✅ Data is generated/derived (amalgamations, contexts)
- ✅ Multi-user access needed (future: collaboration)

**Use Filesystem When**:
- ✅ Static reference data (templates)
- ✅ Large binary files (PDFs, images)
- ✅ Human-edited content (documentation)
- ✅ Version-controlled artifacts (code)
- ✅ Read-only configuration (but reference in DB)

**Use Hybrid (Metadata DB + Files) When**:
- ✅ Large files with searchable metadata (documents)
- ✅ External content with local cache (evidence)
- ✅ Backup/export artifacts (database dumps)

### Source of Truth Principles

1. **Single Source of Truth**: One authoritative location per data type
2. **Database First**: When in doubt, store in database
3. **Files for Export**: Files can be generated from database
4. **Cache Carefully**: Caching files OK, but invalidation logic required
5. **No Dual Writes**: Avoid writing same data to DB + file
6. **Metadata in DB**: Even if content is in files, metadata goes to DB

---

## Code Smell Detection

### Anti-Patterns to Avoid

**1. Dual Writes (BAD)**
```python
# ❌ BAD: Writing to both database and file
agent = agent_methods.create_agent(db, agent_data)
write_agent_sop_file(agent_dir, agent.role, sop_content)
```

**2. Filesystem as Source of Truth (BAD)**
```python
# ❌ BAD: Reading from file when database has it
def load_sop(agent_role):
    file_path = f'.claude/agents/{agent_role}.md'
    return Path(file_path).read_text()
```

**3. Mixed Sources (BAD)**
```python
# ❌ BAD: Sometimes DB, sometimes file
def get_context(task_id):
    db_context = get_from_database(task_id)
    if not db_context:
        return read_from_file(f'.aipm/contexts/task_{task_id}.txt')
```

### Best Practices (GOOD)

**1. Database Primary (GOOD)**
```python
# ✅ GOOD: Database is source of truth
def load_sop(db, project_id, agent_role):
    agent = agents.get_agent_by_role(db, project_id, agent_role)
    return agent.sop_content if agent else None
```

**2. Files as Export (GOOD)**
```python
# ✅ GOOD: Files generated from database
def export_agent_sop(db, agent_id, output_dir):
    agent = agents.get_agent(db, agent_id)
    if agent.sop_content:
        file_path = output_dir / f'{agent.role}.md'
        file_path.write_text(agent.sop_content)
```

**3. Metadata in DB, Content in Files (GOOD)**
```python
# ✅ GOOD: Hybrid approach for documents
doc_ref = document_references.get_document(db, doc_id)
content = Path(doc_ref.file_path).read_text()  # File read is explicit
```

---

## Conclusion

**Current State**: MOSTLY CORRECT with 2 exceptions:
1. ⚠️ Agent SOPs read from files instead of database (HIGH priority fix)
2. ⚠️ Amalgamations stored in `.aipm/contexts/` instead of database (MEDIUM priority migration)

**Recommended Actions**:
1. **Week 1**: Fix agent SOP loading to use database
2. **Week 2-3**: Migrate amalgamations to database
3. **Week 4**: Documentation and cleanup

**Long-Term Vision**: Database-first architecture with:
- All dynamic/generated data in database
- Files used only for static references, large binaries, or human-edited docs
- Clear separation of concerns and single source of truth

**Compliance with WI-40**: Rules system is already fully database-driven (✅ correct pattern)
