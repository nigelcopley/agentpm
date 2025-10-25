# APM (Agent Project Manager) Documentation Structure - Unified Synthesis

## Executive Summary

After analyzing three LLM recommendations (Claude, Gemini, Cursor), this document presents a **unified hybrid approach** that combines:

- **Claude's simplicity**: 8 top-level directories, minimal nesting
- **Gemini's discoverability**: Type-first organization with clear categorization
- **Cursor's automation**: Database-driven metadata with auto-detection

**Key Innovation**: Physical structure optimized for human creators (type-first, 2 levels deep), logical structure optimized for consumers (system tags, component metadata, searchable).

**Result**: 8 directories + database metadata + auto-detection = Simple to use, powerful to query, scalable from 5 to 500+ people.

---

## 1. Unified Structure Proposal

### Final Directory Layout

```
docs/
├── 01-quickstart/              # New user entry point (getting started guides)
│   ├── README.md               # Quick start overview
│   ├── installation.md
│   ├── first-steps.md
│   └── common-workflows.md
│
├── 02-guides/                  # How-to guides, tutorials (task-oriented)
│   ├── README.md               # Guide index
│   ├── user/                   # End-user guides
│   │   ├── work-items.md
│   │   ├── tasks.md
│   │   └── workflows.md
│   └── developer/              # Developer guides
│       ├── database-setup.md
│       ├── adding-commands.md
│       └── testing.md
│
├── 03-architecture/            # System design, patterns, technical decisions
│   ├── README.md               # Architecture overview
│   ├── overview.md             # High-level system design
│   ├── three-tier-orchestration.md
│   ├── database/               # Database system architecture
│   │   ├── README.md           # Database landing page
│   │   ├── schema.md
│   │   └── migrations.md
│   ├── agents/                 # Agent system architecture
│   │   ├── README.md
│   │   ├── orchestration.md
│   │   └── delegation.md
│   ├── workflow/               # Workflow system architecture
│   │   ├── README.md
│   │   ├── state-machine.md
│   │   └── phase-gates.md
│   ├── context/                # Context system architecture
│   ├── rules/                  # Rules system architecture
│   ├── plugins/                # Plugin system architecture
│   └── security/               # Security architecture
│
├── 04-reference/               # API documentation, command reference (auto-generated)
│   ├── README.md               # Reference index
│   ├── cli/                    # CLI command reference
│   │   ├── work-items.md       # Auto-generated from CLI
│   │   ├── tasks.md
│   │   └── rules.md
│   ├── api/                    # Python API reference
│   │   ├── models.md           # Auto-generated from docstrings
│   │   ├── methods.md
│   │   └── adapters.md
│   └── database/               # Database schema reference
│       └── schema.md           # Auto-generated from SQLite
│
├── 05-development/             # Developer workflows, contributing, tooling
│   ├── README.md               # Development guide index
│   ├── contributing.md
│   ├── development-workflow.md
│   ├── testing-strategy.md
│   └── release-process.md
│
├── 06-decisions/               # ALL ADRs (Architecture Decision Records)
│   ├── README.md               # ADR index (auto-generated)
│   ├── ADR-001-database-first.md
│   ├── ADR-002-hexagonal-architecture.md
│   ├── ADR-003-agent-orchestration.md
│   └── ...                     # Flat, numbered, chronological
│
└── .archive/                   # Completed work items, superseded content
    ├── legacy/                 # Historical docs (pre-V2)
    └── superseded/             # Replaced by newer versions
```

### Document Type Definitions

| Type | Description | Location | Examples |
|------|-------------|----------|----------|
| **quickstart** | Getting started, onboarding, first steps | `01-quickstart/` | installation.md, first-steps.md |
| **guide** | How-to, tutorials, task-oriented | `02-guides/` | work-items.md, testing.md |
| **architecture** | System design, patterns, technical structure | `03-architecture/` | schema.md, state-machine.md |
| **reference** | API docs, command reference (auto-generated) | `04-reference/` | cli/work-items.md, api/models.md |
| **development** | Contributing, workflows, tooling, processes | `05-development/` | contributing.md, release-process.md |
| **decision** | ADRs, architectural decisions, trade-offs | `06-decisions/` | ADR-001-database-first.md |
| **archive** | Superseded content, completed work, legacy | `.archive/` | legacy/v1-docs/, superseded/old-design.md |

### System/Component Tags

Documents are tagged with system/component metadata for cross-cutting queries:

**Systems** (top-level):
- `database` - Schema, migrations, adapters
- `workflow` - State machine, phases, gates
- `agents` - Orchestration, delegation, personas
- `context` - 6W, evidence, confidence
- `rules` - Enforcement, validation, compliance
- `plugins` - Extension system, hooks
- `cli` - Commands, interface, user experience
- `security` - Authentication, authorization, encryption

**Components** (fine-grained):
- Auto-detected from file paths and content
- Examples: `work-items`, `tasks`, `evidence`, `migrations`, `rules-engine`

### Metadata Schema

Every document has metadata (stored in database):

```yaml
# YAML frontmatter (optional, overrides auto-detection)
---
title: "Database Schema Design"
doc_type: architecture          # Required
system: database                # Optional (auto-detected if missing)
component: schema               # Optional
phase: null                     # D1, P1, I1, R1, O1, E1 (if phase-specific)
status: active                  # draft, active, superseded, archived
tags: [database, schema, migrations, sqlite]
work_item_id: null              # Link to originating work item
auto_detected: false            # Metadata manually specified
created: 2025-01-15
updated: 2025-10-18
---
```

### Placement Decision Tree

**Question 1: What type of document is this?**
- **Getting started, onboarding** → `01-quickstart/`
- **How-to, tutorial, guide** → `02-guides/user/` or `02-guides/developer/`
- **System design, architecture** → `03-architecture/{system}/`
- **Architectural decision** → `06-decisions/ADR-{number}-{title}.md`
- **API/command reference** → `04-reference/cli/` or `04-reference/api/`
- **Development process, contributing** → `05-development/`

**Question 2: (For architecture/guides) What system?**
Auto-detected from:
- File path: `docs/03-architecture/database/` → `system: database`
- Content keywords: "workflow", "context", "agent", etc.
- Manual frontmatter: `system: database`

**Special Cases**:
- **ADR** → ALWAYS `06-decisions/` (flat, numbered ADR-001, ADR-002, etc.)
- **Auto-generated** → ALWAYS `04-reference/`
- **Superseded** → Move to `.archive/superseded/` with ADR explaining why
- **Legacy** → Move to `.archive/legacy/` with index

**Maximum 3 questions, ~10 seconds for humans, ~0 seconds for auto-detection.**

---

## 3. Enforcement via Rules and Quality Gates

To ensure these standards are followed, we will use AIPM's own Rules and Quality Gates to automate enforcement and guide users.

### A. Automated Rules

These rules will run automatically (e.g., via git hooks or tool calls) to provide immediate feedback.

1.  **`Rule: Enforce-Doc-Placement`**
    *   **Trigger:** An agent or user attempts to create a file inside the `docs/` directory.
    *   **Action:** The rule intercepts the action and validates the target path against the Placement Decision Tree.
    *   **Guidance:** If the location is incorrect, the action is rejected with a helpful error message (e.g., `Error: Architectural Decision Records (ADRs) must be placed in 'docs/06-decisions/'.`).

2.  **`Rule: Require-Doc-Metadata`**
    *   **Trigger:** A new markdown file is created in `docs/`.
    *   **Action:** The rule parses the file to ensure a valid YAML front matter block exists and contains all required fields (`title`, `component`, `type`, `status`, `owner`).
    *   **Guidance:** If metadata is missing or invalid, the operation fails with a clear error (e.g., `Error: Document is missing required 'status' field in its metadata.`).

3.  **`Rule: Prevent-Orphaned-Docs`**
    *   **Trigger:** A file is created on the filesystem in `docs/`.
    *   **Action:** The rule ensures a corresponding entry is created in the `documents` database table via `apm docs scan` or a direct API call.
    *   **Guidance:** If no database entry is made, the system flags the file as an "orphan" that needs to be indexed.

### B. Quality Gates

Quality Gates block workflow progression, ensuring documentation is treated as a first-class citizen.

1.  **`Gate: Doc-Exists-For-Feature`**
    *   **Phase:** Before a feature can move from `Implementation` to `Review`.
    *   **Check:** Verifies that at least one `guide` or `architecture` document in the database is linked to the feature's `work_item_id`.
    *   **Result:** If no documentation is linked, the gate fails, and the feature cannot be promoted.

2.  **`Gate: Doc-Is-Reviewed`**
    *   **Phase:** Before a feature can move from `Review` to `Release`.
    *   **Check:** For all documents linked to the feature, it verifies the `status` in the metadata is `in-review` or `living`, not `draft`.
    *   **Result:** Fails the gate if critical documentation is still in a draft state.

---

## 4. Implementation Plan

### Phase 1: Foundation (Week 1, Days 1-2)

**Objective**: Build database infrastructure and basic CLI commands

**Tasks**:
1. Create database migration for `documents` table
2. Implement document models (Pydantic)
3. Implement document adapters (SQLite conversion)
4. Implement document methods (CRUD operations)
5. Build CLI commands:
   - `apm docs list [--type TYPE] [--system SYSTEM] [--status STATUS]`
   - `apm docs show <id>`
   - `apm docs search <query>`
   - `apm docs scan` (scan docs/ directory, populate database)
6. Implement path-based auto-detection
7. Write unit tests for document system

**Deliverables**:
- Database schema updated
- CLI commands functional
- Auto-detection working (path-based only)
- Zero files moved (infrastructure only)

**Success Criteria**:
- `apm docs scan` populates database from existing docs/
- `apm docs list` returns documents with metadata
- `apm docs search "database"` finds relevant docs

### Phase 2: Structure Creation (Week 1, Days 3-4)

**Objective**: Create new directory structure and migrate high-value docs

**Tasks**:
1. Create 8 top-level directories with README.md
2. Create system subdirectories in `03-architecture/`
3. Write placement decision tree documentation
4. Implement content-based detection (YAML frontmatter, keywords)
5. Migrate critical documents (~20-30 files):
   - `01-quickstart/`: Installation, first steps
   - `02-guides/`: Core user/developer guides
   - `03-architecture/`: Main architecture docs
   - `06-decisions/`: Consolidate all ADRs (from 6 locations → 1)
6. Update internal links in migrated docs
7. Add auto-detection confidence scoring

**Deliverables**:
- New directory structure created
- High-value docs migrated
- Content-based detection functional
- Decision tree documented

**Success Criteria**:
- New structure navigable
- Critical docs accessible in new locations
- Auto-detection confidence ≥0.7 for migrated docs
- All ADRs in single location with index

### Phase 3: Full Migration (Week 1, Days 5-7)

**Objective**: Migrate all 61 directories to new structure

**Tasks**:
1. Audit all existing docs/ subdirectories (61 total)
2. Map each directory to new location using decision tree
3. Migrate all documents with metadata:
   - Update file paths
   - Update database records
   - Update internal links
   - Add frontmatter if missing
4. Consolidate work items → `work/`
5. Archive superseded content → `.archive/superseded/`
6. Archive legacy content → `.archive/legacy/`
7. Delete empty directories
8. Generate document indices (README.md files)
9. Update all project references to old paths

**Deliverables**:
- All 61 directories migrated
- Old structure removed
- All links updated
- Indices generated

**Success Criteria**:
- Zero broken internal links
- All docs findable via `apm docs search`
- Work items separated from permanent docs
- Legacy content archived with context

### Phase 4: Enhancement (Week 2+)

**Objective**: Add advanced features and automation

**Tasks**:
1. Hook integration (pre/post tool use):
   - Suggest document location when agent creates file in docs/
   - Validate frontmatter when saving
   - Auto-update database on file changes
2. Auto-generation for reference docs:
   - CLI command reference from argparse
   - API reference from docstrings
   - Database schema from SQLite
3. Search enhancements:
   - Full-text search in content
   - Fuzzy matching for queries
   - Relationship inference (links between docs)
4. Quality checks:
   - Detect orphaned documents (not in database)
   - Detect missing metadata
   - Suggest improvements

**Deliverables**:
- Hooks integrated
- Auto-generation working
- Enhanced search
- Quality checks automated

**Success Criteria**:
- Reference docs auto-update on code changes
- Agents guided to correct locations
- Search finds relevant docs quickly
- Quality maintained automatically

---

## 3. Comparison Matrix

| Dimension | Claude (FLAT + LIFECYCLE) | Gemini (MATRIX) | Cursor (HIERARCHICAL) | **Unified Hybrid** |
|-----------|---------------------------|-----------------|------------------------|-------------------|
| **Top-level dirs** | 8 | 10+ | Database-driven | **8** ✅ |
| **Nesting depth** | 2 levels | 3 levels | 2-3 levels | **2 levels** ✅ |
| **Decision time** | ~2 seconds (8 choices) | ~5-8 seconds (10+ choices) | 0 seconds (auto-detect) | **~10 sec human, 0 sec agent** ✅ |
| **Navigation** | Very simple (2 clicks) | Moderate (3 clicks) | Query-based | **Simple physical, rich queries** ✅ |
| **Complexity** | Low (8 dirs) | High (10+ categories) | Medium (hidden by DB) | **Low (8 dirs) + hidden metadata** ✅ |
| **Scalability** | Poor (breaks at 50+ people) | Good (designed for large orgs) | Excellent (database scales) | **Excellent** ✅ |
| **Discoverability** | Good for small teams | Good multi-dimensional | Excellent via queries | **Excellent** ✅ |
| **Maintenance** | High (files grow, manual split) | Medium (many directories) | Low (auto-organized) | **Low (auto-detection)** ✅ |
| **Agent compliance** | High (few choices) | Medium (more errors) | High (system-guided) | **High (auto-detect + guide)** ✅ |
| **Infrastructure cost** | None | None | High (DB, CLI, hooks) | **Medium (1 week initial)** ⚠️ |
| **Work item handling** | Flat in work-items/ | Scattered by type | Database-driven | **Separated work/ directory** ✅ |
| **ADR consolidation** | Single decisions/ dir | Multiple locations | Database tags | **Single 06-decisions/ dir** ✅ |
| **Component docs** | Single file per component | Split by type × component | Database tags | **Landing page + detailed** ✅ |
| **Auto-generation** | Manual | Manual | Supported | **Supported (Phase 4)** ✅ |
| **Search** | File system only | File system only | Database queries | **Database queries** ✅ |

### What We Take From Each

**From Claude**:
- ✅ 8 top-level directories (simplicity)
- ✅ Work-centric organization (separate work/ area)
- ✅ Flat ADR structure (decisions/ directory)
- ✅ Minimal nesting (2 levels max)
- ❌ Single file per component (too large, rejected)

**From Gemini**:
- ✅ Type-first organization (guides, architecture, reference)
- ✅ Numbered directories (suggested reading order)
- ✅ Multi-dimensional indexing (but via metadata, not directories)
- ✅ Clear categorization by document purpose
- ❌ Deep nesting (3 levels → 2 levels, rejected)
- ❌ Type × component matrix (creates duplication, rejected)

**From Cursor**:
- ✅ Database-driven metadata
- ✅ Auto-detection from paths + content
- ✅ CLI commands for search and management
- ✅ System/component tagging
- ✅ Query-based discovery
- ❌ Full 8×12 matrix exposure (hidden by auto-detect, simplified)

### What We Reject and Why

**Rejected from Claude**:
- ❌ **Single file per component** (e.g., `system/database.md` for all database docs)
  - **Why**: Files become too large (1000+ lines), hard to navigate, slow to load
  - **Alternative**: Landing page (README.md) + detailed files by topic

**Rejected from Gemini**:
- ❌ **3-level nesting** (e.g., `03-architecture/database/schema/migrations.md`)
  - **Why**: Too much clicking, decision fatigue, harder for agents
  - **Alternative**: 2-level max (`03-architecture/database/migrations.md`)
- ❌ **Type × component duplication** (same component in multiple type directories)
  - **Why**: Maintenance burden, conflicting updates, unclear source of truth
  - **Alternative**: Single location, rich metadata enables multi-dimensional queries

**Rejected from Cursor**:
- ❌ **Explicit 8×12 matrix** (creating all 96 combinations upfront)
  - **Why**: Over-engineering, empty directories, overwhelming
  - **Alternative**: Create directories as needed, metadata provides logical matrix

---

## 4. Answers to 5 Key Questions

### Q1: Work Item Consolidation Strategy

**Problem**: Work items create directory proliferation, mix transient with permanent docs.

**Solution**: Separate staging area with graduation path

**Strategy**:
1. **Active work items** → `work/WI-{id}-{name}/`
   - Contains: notes.md, design.md, research.md, evidence.md
   - Status: draft, work-in-progress
   - Lifecycle: Created when work item starts, deleted when completed

2. **Upon work item completion**:
   - Valuable artifacts graduate to permanent locations:
     - Design docs → `03-architecture/{system}/`
     - How-to guides → `02-guides/`
     - ADRs → `06-decisions/`
   - Transient artifacts archived → `.archive/completed-work/WI-{id}/`
   - Work directory deleted

3. **Database tracking**:
   - Documents have `work_item_id` foreign key
   - Query: `apm docs list --work-item 123` shows all related docs
   - Audit trail maintained even after graduation

**Benefits**:
- Clear separation of transient vs. permanent
- Prevents work-item sprawl in permanent structure
- Maintains traceability via database
- Agents know exactly where to put drafts

### Q2: Design Archive Strategy

**Problem**: Active designs vs. superseded designs vs. legacy designs.

**Solution**: Status-based lifecycle management

**Strategy**:
1. **Active designs** → `03-architecture/{system}/`
   - Status: `active`
   - Maintained, up-to-date, authoritative

2. **Superseded designs** → `.archive/superseded/{system}/`
   - Status: `superseded`
   - Accompanied by ADR explaining why superseded
   - Example: `.archive/superseded/database/v1-schema.md` + `06-decisions/ADR-042-schema-v2.md`
   - Linked from current design: "See .archive/superseded/database/v1-schema.md for historical context"

3. **Legacy designs (pre-V2)** → `.archive/legacy/`
   - Status: `archived`
   - Historical value only, not actively referenced
   - Indexed in `.archive/legacy/README.md`

**Lifecycle**:
```
work/WI-{id}/design.md (draft)
  → 03-architecture/{system}/feature.md (active)
  → .archive/superseded/{system}/feature-v1.md (superseded)
  → .archive/legacy/ (archived, rarely)
```

**Benefits**:
- Clear distinction between current and historical
- Preserves institutional knowledge
- ADRs provide context for why things changed
- No confusion about which design is authoritative

### Q3: Legacy Content Handling

**Problem**: ~200-300 files from V1, external analyses, outdated guides.

**Solution**: Structured archive with index and search

**Strategy**:
1. **Audit all legacy content**:
   - Identify: Pre-V2 docs, external analyses, outdated guides
   - Categorize: Still valuable vs. obsolete vs. historical only

2. **Triage into 3 buckets**:
   - **Upgrade**: Still valuable, needs updating → Migrate to new structure with updates
   - **Archive**: Historical value, keep for reference → `.archive/legacy/`
   - **Delete**: Obsolete, no value → Remove entirely

3. **Archive structure**:
   ```
   .archive/
   ├── legacy/
   │   ├── README.md               # Index of legacy content
   │   ├── v1-documentation/       # Old AIPM V1 docs
   │   ├── external-analyses/      # Third-party analysis docs
   │   └── superseded-guides/      # Old guides replaced by new versions
   └── superseded/                 # Active docs that were replaced
       ├── database/
       ├── workflow/
       └── ...
   ```

4. **Index generation**:
   - `.archive/legacy/README.md` auto-generated with:
     - File list with dates
     - Brief description of each
     - Why archived (superseded by X, obsolete, historical only)
   - Searchable: `apm docs search "legacy workflow"`

**Benefits**:
- Nothing lost (can always recover)
- Clear signal that content is historical
- Searchable if needed
- Doesn't clutter active documentation

### Q4: Component README Approach

**Problem**: One large file vs. scattered files vs. duplicated content?

**Solution**: Landing page + detailed files pattern

**Strategy**:
1. **Landing page** (README.md in each component directory):
   - Overview of the component (1-2 paragraphs)
   - Key concepts (bulleted list)
   - Links to detailed documentation
   - Links to related guides and references
   - Examples:
     ```
     03-architecture/database/README.md
     03-architecture/agents/README.md
     03-architecture/workflow/README.md
     ```

2. **Detailed files** (in same directory):
   - One file per major topic
   - Examples:
     ```
     03-architecture/database/
     ├── README.md           # Landing page
     ├── schema.md           # Detailed schema documentation
     ├── migrations.md       # Migration system
     ├── adapters.md         # Adapter pattern
     └── optimization.md     # Performance optimization
     ```

3. **Cross-references** (via metadata):
   - Related guides: `02-guides/developer/database-setup.md`
   - Related reference: `04-reference/api/database-api.md`
   - Related decisions: `06-decisions/ADR-001-database-first.md`
   - Query: `apm docs list --system database` shows all

**Template for component README**:
```markdown
# {Component Name}

## Overview
Brief description of the component (1-2 paragraphs).

## Key Concepts
- Concept 1: Brief explanation
- Concept 2: Brief explanation
- Concept 3: Brief explanation

## Architecture Documentation
- [Schema Design](schema.md) - Database schema and relationships
- [Migration System](migrations.md) - How migrations work
- [Adapters](adapters.md) - Pydantic ↔ SQLite conversion

## Related Guides
- [Database Setup Guide](../../02-guides/developer/database-setup.md)
- [Writing Migrations](../../02-guides/developer/migrations.md)

## Related Reference
- [Database API](../../04-reference/api/database-api.md)
- [CLI: apm db](../../04-reference/cli/database.md)

## Architectural Decisions
- [ADR-001: Database-First Architecture](../../06-decisions/ADR-001-database-first.md)
- [ADR-015: SQLite Choice](../../06-decisions/ADR-015-sqlite.md)

## Quick Links
- Source: `agentpm/core/database/`
- Tests: `tests/core/database/`
- Schema: `agentpm/core/database/schema.sql`
```

**Benefits**:
- Clear entry point for each component
- Detailed docs separated by topic (manageable file sizes)
- No duplication (single source of truth)
- Rich cross-references via metadata
- Scalable (add new detailed files as needed)

### Q5: Auto-Generation Priorities

**Problem**: What to generate first? How to maintain?

**Solution**: Phased approach, high-value first

**Priority 1: CLI Command Reference** (Highest value, easiest)
- Generate from argparse definitions
- Location: `04-reference/cli/`
- Files:
  - `work-items.md` - All `apm work-item` commands
  - `tasks.md` - All `apm task` commands
  - `rules.md` - All `apm rules` commands
  - `docs.md` - All `apm docs` commands
- Update trigger: Pre-release hook
- Effort: 2-3 days

**Priority 2: Database Schema Reference** (High value, medium effort)
- Generate from SQLite schema
- Location: `04-reference/database/schema.md`
- Content:
  - Table definitions with field types
  - Indexes and constraints
  - Foreign key relationships
  - Example queries
- Update trigger: After migration runs
- Effort: 1-2 days

**Priority 3: API Reference** (Medium value, higher effort)
- Generate from Python docstrings
- Location: `04-reference/api/`
- Files:
  - `models.md` - Pydantic models
  - `methods.md` - Business logic methods
  - `adapters.md` - Database adapters
- Tools: Sphinx, mkdocs, or custom parser
- Update trigger: Pre-release hook
- Effort: 3-5 days

**Priority 4: Document Indices** (Medium value, low effort)
- Generate README.md files with document lists
- Locations:
  - `06-decisions/README.md` - All ADRs chronologically
  - `.archive/legacy/README.md` - Legacy content index
  - Each component README links section
- Update trigger: Post-document-creation hook
- Effort: 1 day

**Priority 5: Metrics and Stats** (Lower value, medium effort)
- Documentation coverage metrics
- Link validation reports
- Staleness detection (last updated > 6 months)
- Location: `04-reference/metrics/`
- Update trigger: Weekly cron job
- Effort: 2-3 days

**Maintenance Strategy**:
1. **Critical docs** (CLI, schema): Auto-regenerate on every release
2. **API docs**: Auto-regenerate on major version changes
3. **Indices**: Auto-regenerate on document creation/deletion
4. **Metrics**: Weekly batch job
5. **Manual docs**: Never auto-generate (guides, architecture, decisions)

**Implementation Approach**:
```python
# agentpm/core/docs/generators/cli_reference.py
def generate_cli_reference():
    """Generate CLI command reference from argparse."""
    for command_group in ['work-item', 'task', 'rules', 'docs']:
        parser = get_parser_for_command(command_group)
        markdown = parser_to_markdown(parser)
        write_file(f'docs/04-reference/cli/{command_group}.md', markdown)

# Hook integration
# agentpm/core/hooks/post_release.py
def post_release_hook():
    generate_cli_reference()
    generate_schema_reference()
    generate_api_reference()
    validate_all_links()
```

---

## 5. Success Metrics

How we'll know the new structure is working:

### Week 1 (Immediate)
- ✅ All 61 directories migrated to 8 top-level directories
- ✅ All ADRs in single location (`06-decisions/`)
- ✅ Work items separated (`work/` staging area)
- ✅ Zero broken internal links
- ✅ Database populated with document metadata
- ✅ `apm docs search` returns relevant results

### Month 1 (Short-term)
- ✅ Agents consistently use correct locations (>90% accuracy)
- ✅ New documents auto-detected with confidence >0.7
- ✅ CLI reference auto-generated and up-to-date
- ✅ Developers find docs in <30 seconds
- ✅ No new directory proliferation

### Month 3 (Medium-term)
- ✅ Full auto-generation pipeline operational
- ✅ Hook integration guides agent behavior
- ✅ Documentation coverage >80% of codebase
- ✅ Onboarding time reduced by 50% (new developers)
- ✅ Search finds 95%+ of relevant docs

### Month 6 (Long-term)
- ✅ Structure scales without modification (tested with 2x content)
- ✅ Maintenance burden <2 hours/week
- ✅ Zero manual link updates (automated)
- ✅ Quality checks catch 100% of issues
- ✅ Team satisfaction >8/10 with documentation

---

## 6. Migration Checklist

### Pre-Migration
- [ ] Review this synthesis document with team
- [ ] Get approval on unified structure
- [ ] Create backup of current `docs/` directory
- [ ] Create new branch for migration

### Phase 1: Foundation (Days 1-2)
- [ ] Create database migration file
- [ ] Implement document models (Pydantic)
- [ ] Implement document adapters (SQLite)
- [ ] Implement document methods (CRUD)
- [ ] Build CLI: `apm docs list`
- [ ] Build CLI: `apm docs show`
- [ ] Build CLI: `apm docs search`
- [ ] Build CLI: `apm docs scan`
- [ ] Implement path-based auto-detection
- [ ] Write unit tests
- [ ] Run migration: `apm db upgrade`
- [ ] Test: `apm docs scan` populates database

### Phase 2: Structure Creation (Days 3-4)
- [ ] Create 8 top-level directories
- [ ] Create system subdirectories in `03-architecture/`
- [ ] Write README.md for each directory
- [ ] Document placement decision tree
- [ ] Implement content-based detection
- [ ] Migrate quickstart docs → `01-quickstart/`
- [ ] Migrate core guides → `02-guides/`
- [ ] Migrate architecture docs → `03-architecture/`
- [ ] Consolidate ADRs → `06-decisions/` (all 6 locations)
- [ ] Update internal links in migrated docs
- [ ] Test auto-detection confidence scores
- [ ] Generate ADR index

### Phase 3: Full Migration (Days 5-7)
- [ ] Audit all 61 existing directories
- [ ] Map each to new location using decision tree
- [ ] Migrate all remaining documents
- [ ] Move work items → `work/`
- [ ] Move superseded content → `.archive/superseded/`
- [ ] Move legacy content → `.archive/legacy/`
- [ ] Generate legacy index
- [ ] Update all internal links (automated script)
- [ ] Delete empty directories
- [ ] Update project references (CLAUDE.md, README.md, etc.)
- [ ] Run link validator
- [ ] Test search: `apm docs search` for common queries
- [ ] Commit migration

### Phase 4: Enhancement (Week 2+)
- [ ] Implement pre-tool-use hook (suggest location)
- [ ] Implement post-tool-use hook (validate metadata)
- [ ] Build CLI reference auto-generation
- [ ] Build schema reference auto-generation
- [ ] Build API reference auto-generation
- [ ] Implement full-text search
- [ ] Implement relationship inference
- [ ] Build quality checks (orphaned docs, missing metadata)
- [ ] Set up weekly metrics generation
- [ ] Document hook system for future extensions

### Post-Migration
- [ ] Team training on new structure
- [ ] Update agent prompts to reference new structure
- [ ] Monitor agent compliance for 1 week
- [ ] Gather feedback from team
- [ ] Iterate on decision tree if needed
- [ ] Celebrate! 🎉

---

## 7. Conclusion

This unified synthesis combines the best aspects of all three recommendations:

**Simplicity** (Claude): 8 directories, 2 levels deep, clear decision tree
**Discoverability** (Gemini): Type-first organization, clear categorization
**Automation** (Cursor): Database metadata, auto-detection, powerful queries

The result is a documentation structure that:
- ✅ Works for 5-person teams (simple, low overhead)
- ✅ Scales to 500+ person orgs (rich metadata, powerful search)
- ✅ Guides agents to correct locations (auto-detection)
- ✅ Makes finding docs fast (<30 seconds)
- ✅ Requires minimal maintenance (auto-organized)
- ✅ Executable within 1 week (phased approach)

**Key Innovation**: Decouple physical structure (optimized for creation) from logical structure (optimized for consumption). Physical structure is simple (8 dirs), logical structure is rich (system, component, phase, tags).

This is the optimal solution for APM (Agent Project Manager)'s documentation architecture.

---

**Version**: 1.0.0
**Date**: 2025-10-18
**Authors**: Synthesis of Claude, Gemini, Cursor recommendations by System Architect agent
**Status**: Ready for implementation