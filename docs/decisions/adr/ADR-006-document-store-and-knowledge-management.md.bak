# ADR-006: Document Store and Knowledge Management

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable fast document discovery and prevent redundant knowledge creation

---

## Context

### The Knowledge Duplication Problem

During complex project development, teams create massive amounts of documentation:
- Architecture Decision Records (ADRs)
- API specifications
- Database schemas
- Design documents
- Implementation guides
- Test plans
- Troubleshooting guides
- Meeting notes

**Current Problem:**

```
Week 1: Developer writes "JWT Authentication Design.md"
├─ Stores in: docs/architecture/auth-jwt-design.md
└─ Contains: Token structure, refresh strategy, security considerations

Week 3: Different developer works on API auth
├─ Searches for: "authentication documentation"
├─ Can't find JWT design doc (wrong keywords, wrong location)
├─ Writes: "API Authentication Spec.md"
└─ Duplicates 70% of JWT design content ❌

Week 5: Third developer debugging auth issues
├─ Searches for: "JWT troubleshooting"
├─ Finds neither document (buried in 200+ markdown files)
├─ Spends 3 hours debugging known issue
└─ Issue was documented in JWT design doc ❌

Week 8: Audit for compliance
├─ Question: "Where are authentication decisions documented?"
├─ Team: "Somewhere in docs/ folder..."
├─ Spend 2 days hunting through files
└─ Miss critical security decision buried in meeting notes ❌
```

**Result:**
- Knowledge scattered across filesystem
- Duplicate documentation (wasted effort)
- Can't find existing docs (slow development)
- No fast search (grep takes 5-10 seconds on large codebases)
- No knowledge of what documents exist
- Critical information lost in noise

### Requirements

1. **Fast Discovery**: Find relevant docs in <100ms (not 5-10 seconds)
2. **Prevent Duplication**: Know if doc already exists before creating
3. **Semantic Search**: Find by concept, not just exact keywords
4. **Document Metadata**: Track purpose, status, related docs
5. **Cross-Reference**: Link documents to work items, tasks, decisions
6. **Version Aware**: Track document evolution over time

---

## Decision

We will implement a **Document Store with Metadata Index** that provides:

1. **Metadata Database**: Fast indexed lookups without scanning filesystem
2. **Document Registry**: Catalog of all documents with searchable metadata
3. **Semantic Tagging**: Auto-tag documents with concepts and entities
4. **Cross-References**: Link documents to work items, decisions, code files
5. **Smart Search**: Multi-field search with relevance scoring
6. **Version Tracking**: Document evolution with git integration

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Document Store Architecture                │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Document Metadata Database (Fast Indexed Lookups)     │ │
│  │                                                        │ │
│  │  documents                                             │ │
│  │   ├─ document_id (UUID)                               │ │
│  │   ├─ title, file_path, content_hash                   │ │
│  │   ├─ document_type: ADR | spec | guide | plan        │ │
│  │   ├─ status: draft | review | approved | superseded  │ │
│  │   ├─ created_at, updated_at, version                  │ │
│  │   ├─ author, reviewed_by                              │ │
│  │   └─ summary (≤200 words, searchable)                │ │
│  │                                                        │ │
│  │  document_tags (auto-generated + manual)              │ │
│  │   ├─ document_id, tag                                 │ │
│  │   ├─ tag_type: concept | technology | entity         │ │
│  │   ├─ confidence: float (auto-tag confidence)         │ │
│  │   └─ Examples: jwt, authentication, database, api    │ │
│  │                                                        │ │
│  │  document_references (cross-links)                    │ │
│  │   ├─ document_id, references_document_id             │ │
│  │   ├─ reference_type: supersedes | extends | related  │ │
│  │   ├─ work_item_id, decision_id, task_id (FKs)       │ │
│  │   └─ relevance_score: float                          │ │
│  │                                                        │ │
│  │  document_searches (cache search results)             │ │
│  │   ├─ query_hash, document_ids                        │ │
│  │   ├─ relevance_scores                                 │ │
│  │   └─ cached_at, hit_count                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                              │
│  ┌───────────────────────────┼────────────────────────────┐ │
│  │ Document Intelligence      │                            │ │
│  │                           │                            │ │
│  │  ┌────────────────┐  ┌───▼──────────┐  ┌───────────┐ │ │
│  │  │ Auto-Tagging   │  │ Duplicate     │  │ Search    │ │ │
│  │  │ (Extract tags  │  │ Detection     │  │ Engine    │ │ │
│  │  │  from content) │  │ (Find similar)│  │ (Multi-   │ │ │
│  │  └────────────────┘  └───────────────┘  │  field)   │ │ │
│  │                                          └───────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                              │
│  ┌───────────────────────────▼────────────────────────────┐ │
│  │ Filesystem (Actual Documents)                          │ │
│  │                                                        │ │
│  │  docs/                                                 │ │
│  │   ├─ adrs/                                            │ │
│  │   ├─ specifications/                                   │ │
│  │   ├─ architecture/                                     │ │
│  │   ├─ guides/                                          │ │
│  │   └─ plans/                                           │ │
│  │                                                        │ │
│  │  Note: Metadata in database, content on disk          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Document Model

```python
@dataclass
class Document:
    """
    Metadata for a document in the project.

    Actual content stored on filesystem, metadata in database.
    Enables fast search without scanning entire filesystem.
    """

    # Identification
    id: str  # UUID
    project_id: int
    file_path: str  # Relative to project root
    content_hash: str  # SHA256 of content

    # Metadata
    title: str
    document_type: Literal[
        "adr",           # Architecture Decision Record
        "spec",          # Technical specification
        "api",           # API documentation
        "guide",         # How-to guide, tutorial
        "plan",          # Implementation plan
        "design",        # Design document
        "meeting",       # Meeting notes
        "research",      # Research findings
        "troubleshoot"   # Troubleshooting guide
    ]
    status: Literal[
        "draft",         # Work in progress
        "review",        # Ready for review
        "approved",      # Approved and current
        "superseded",    # Replaced by newer doc
        "archived"       # Historical, not current
    ]

    # Content
    summary: str  # ≤200 words, searchable
    keywords: List[str]  # Manual keywords
    tags: List[DocumentTag]  # Auto-generated tags

    # Authorship
    author: str  # Agent or human
    created_at: datetime
    updated_at: datetime
    version: int  # Increments on update
    git_commit: Optional[str]  # Git hash when created/updated

    # Review
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]

    # Relationships
    work_item_id: Optional[int]  # Related work item
    task_id: Optional[int]  # Related task
    decision_ids: List[str]  # Decisions documented in this doc

    # References (other documents)
    supersedes: Optional[str]  # Previous version document_id
    superseded_by: Optional[str]  # Newer version document_id
    related_docs: List[str]  # Related document_ids

    # Search optimization
    search_vector: Optional[str]  # Full-text search vector
    last_searched: Optional[datetime]
    search_hit_count: int  # How often found in search

@dataclass
class DocumentTag:
    """
    Tag for categorizing and searching documents.

    Auto-generated from content + manual additions.
    """

    tag: str  # e.g., "jwt", "authentication", "database"
    tag_type: Literal[
        "concept",      # High-level concept (authentication, caching)
        "technology",   # Specific tech (postgresql, django, react)
        "entity",       # Project entity (User model, JWT token)
        "pattern"       # Design pattern (service layer, repository)
    ]
    confidence: float  # 0.0-1.0 (for auto-generated tags)
    source: Literal["auto", "manual"]  # How was tag created

@dataclass
class DocumentReference:
    """
    Cross-reference between documents or to other entities.
    """

    from_document_id: str
    to_document_id: Optional[str]  # Another document
    work_item_id: Optional[int]  # Work item
    decision_id: Optional[str]  # Decision
    task_id: Optional[int]  # Task
    code_file: Optional[str]  # Source code file

    reference_type: Literal[
        "supersedes",    # This doc replaces referenced doc
        "extends",       # This doc builds on referenced doc
        "related",       # General relationship
        "implements",    # This doc implements referenced spec
        "documents"      # This doc documents referenced entity
    ]

    relevance_score: float  # How relevant is this reference (0.0-1.0)
```

### Document Intelligence Services

#### 1. Auto-Tagging Service

```python
class DocumentAutoTaggingService:
    """
    Automatically extract tags from document content.

    Analyzes:
    - Technology mentions (Django, PostgreSQL, React)
    - Concepts (authentication, caching, testing)
    - Entities (models, services, APIs)
    - Patterns (repository, service layer, factory)
    """

    def extract_tags(self, document: Document) -> List[DocumentTag]:
        """
        Extract tags from document content.

        Process:
        1. Read document content
        2. Extract technology names (Django, React, PostgreSQL)
        3. Identify concepts (authentication, caching, API)
        4. Find entities (User model, JWT token, TenantMiddleware)
        5. Detect patterns (service layer, repository, factory)
        6. Calculate confidence scores
        7. Return sorted by confidence

        Example output for JWT auth doc:
        [
            DocumentTag("jwt", "technology", 0.95, "auto"),
            DocumentTag("authentication", "concept", 0.90, "auto"),
            DocumentTag("token", "entity", 0.85, "auto"),
            DocumentTag("security", "concept", 0.80, "auto"),
            DocumentTag("django", "technology", 0.75, "auto")
        ]
        """

        content = Path(document.file_path).read_text()

        tags = []

        # 1. Technology detection (high confidence for exact matches)
        for tech in KNOWN_TECHNOLOGIES:
            if re.search(rf'\b{tech}\b', content, re.IGNORECASE):
                confidence = 0.9 if content.lower().count(tech) > 3 else 0.7
                tags.append(DocumentTag(tech, "technology", confidence, "auto"))

        # 2. Concept extraction (from header analysis)
        headers = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        for header in headers:
            concepts = self._extract_concepts_from_text(header)
            for concept in concepts:
                tags.append(DocumentTag(concept, "concept", 0.8, "auto"))

        # 3. Entity recognition (capitalized technical terms)
        entities = self._extract_entities(content)
        for entity in entities:
            tags.append(DocumentTag(entity, "entity", 0.75, "auto"))

        # 4. Pattern detection (design patterns mentioned)
        for pattern in DESIGN_PATTERNS:
            if pattern.lower() in content.lower():
                tags.append(DocumentTag(pattern, "pattern", 0.85, "auto"))

        # Deduplicate and sort by confidence
        tags = self._deduplicate_tags(tags)
        tags.sort(key=lambda t: t.confidence, reverse=True)

        return tags[:20]  # Top 20 tags

    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """
        Extract conceptual terms.

        Examples: "authentication", "caching", "optimization"
        """
        # Use NLP or keyword matching
        concepts = []
        for concept_keyword in CONCEPT_KEYWORDS:
            if concept_keyword in text.lower():
                concepts.append(concept_keyword)
        return concepts

    def _extract_entities(self, content: str) -> List[str]:
        """
        Extract technical entities (models, services, classes).

        Examples: "User", "AuthService", "JWTMiddleware"
        """
        # Find CamelCase or snake_case technical terms
        entities = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', content)
        entities += re.findall(r'\b([a-z]+_[a-z_]+)\b', content)
        return list(set(entities))[:10]  # Top 10 entities
```

#### 2. Duplicate Detection Service

```python
class DocumentDuplicateDetectionService:
    """
    Detect similar or duplicate documents before creation.

    Prevents redundant documentation.
    """

    def find_similar_documents(
        self,
        title: str,
        summary: str,
        tags: List[str],
        threshold: float = 0.7
    ) -> List[Tuple[Document, float]]:
        """
        Find documents similar to proposed new document.

        Similarity calculated from:
        - Title similarity (30%)
        - Tag overlap (40%)
        - Summary similarity (30%)

        Returns: List of (document, similarity_score) tuples

        Example:
        find_similar_documents(
            title="JWT Authentication Implementation",
            summary="Design for JWT token-based authentication...",
            tags=["jwt", "authentication", "token", "security"]
        )

        Returns:
        [
            (Document("JWT Authentication Design"), 0.92),  # Very similar!
            (Document("API Authentication Spec"), 0.68),    # Somewhat similar
            (Document("User Login Flow"), 0.52)             # Less similar
        ]

        If similarity > 0.8: Warn user about potential duplicate
        """

        # Get all approved/draft documents of same type
        candidate_docs = db.query(Document).filter(
            Document.document_type.in_(["adr", "spec", "design"]),
            Document.status.in_(["approved", "draft", "review"])
        ).all()

        similarities = []

        for doc in candidate_docs:
            # Calculate similarity
            title_sim = self._calculate_title_similarity(title, doc.title)
            tag_sim = self._calculate_tag_overlap(tags, [t.tag for t in doc.tags])
            summary_sim = self._calculate_summary_similarity(summary, doc.summary)

            # Weighted average
            overall_sim = (
                title_sim * 0.3 +
                tag_sim * 0.4 +
                summary_sim * 0.3
            )

            if overall_sim >= threshold:
                similarities.append((doc, overall_sim))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Simple word overlap similarity"""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        return overlap / total if total > 0 else 0.0

    def _calculate_tag_overlap(self, tags1: List[str], tags2: List[str]) -> float:
        """Tag overlap (Jaccard similarity)"""
        set1 = set(t.lower() for t in tags1)
        set2 = set(t.lower() for t in tags2)
        overlap = len(set1 & set2)
        total = len(set1 | set2)
        return overlap / total if total > 0 else 0.0

    def _calculate_summary_similarity(self, summary1: str, summary2: str) -> float:
        """Word overlap in summaries"""
        words1 = set(summary1.lower().split())
        words2 = set(summary2.lower().split())
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        return overlap / total if total > 0 else 0.0
```

#### 3. Smart Search Service

```python
class DocumentSearchService:
    """
    Fast multi-field search across document metadata.

    No need to scan filesystem - all searchable data in database.
    """

    def search(
        self,
        query: str,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 20
    ) -> SearchResult:
        """
        Search documents with multi-field matching.

        Query matches:
        - Title (exact and partial)
        - Summary (full-text)
        - Tags (exact match)
        - Keywords (exact match)

        Example:
        search(
            query="jwt authentication",
            document_type="adr",
            tags=["security"]
        )

        Returns in <100ms (indexed database queries)

        Results ranked by relevance:
        1. Title exact match (highest)
        2. Tag exact match
        3. Summary contains all words
        4. Summary contains some words (lowest)
        """

        # Build query
        q = db.query(Document)

        # Filter by type
        if document_type:
            q = q.filter(Document.document_type == document_type)

        # Filter by status
        if status:
            q = q.filter(Document.status == status)
        else:
            # Default: exclude archived
            q = q.filter(Document.status != "archived")

        # Filter by date range
        if date_range:
            q = q.filter(Document.created_at.between(*date_range))

        # Search in title, summary, tags
        query_words = query.lower().split()

        # Title search (highest priority)
        title_matches = q.filter(
            or_(*[Document.title.ilike(f"%{word}%") for word in query_words])
        ).all()

        # Tag search
        if tags:
            tag_matches = q.join(DocumentTag).filter(
                DocumentTag.tag.in_([t.lower() for t in tags])
            ).all()
        else:
            tag_matches = []

        # Summary search
        summary_matches = q.filter(
            or_(*[Document.summary.ilike(f"%{word}%") for word in query_words])
        ).all()

        # Combine and rank
        results = self._rank_results(
            title_matches=title_matches,
            tag_matches=tag_matches,
            summary_matches=summary_matches,
            query=query
        )

        return SearchResult(
            query=query,
            total_results=len(results),
            results=results[:limit],
            search_time_ms=elapsed_ms
        )

    def _rank_results(
        self,
        title_matches: List[Document],
        tag_matches: List[Document],
        summary_matches: List[Document],
        query: str
    ) -> List[Tuple[Document, float]]:
        """
        Rank search results by relevance.

        Scoring:
        - Title exact match: 1.0
        - Title partial match: 0.8
        - Tag match: 0.7
        - Summary all words: 0.6
        - Summary some words: 0.4
        """

        scores = {}

        # Score title matches
        for doc in title_matches:
            if query.lower() == doc.title.lower():
                scores[doc.id] = max(scores.get(doc.id, 0), 1.0)
            else:
                scores[doc.id] = max(scores.get(doc.id, 0), 0.8)

        # Score tag matches
        for doc in tag_matches:
            scores[doc.id] = max(scores.get(doc.id, 0), 0.7)

        # Score summary matches
        query_words = set(query.lower().split())
        for doc in summary_matches:
            summary_words = set(doc.summary.lower().split())
            match_ratio = len(query_words & summary_words) / len(query_words)
            score = 0.4 + (match_ratio * 0.2)  # 0.4-0.6
            scores[doc.id] = max(scores.get(doc.id, 0), score)

        # Get documents and sort by score
        all_docs = title_matches + tag_matches + summary_matches
        doc_dict = {doc.id: doc for doc in all_docs}

        ranked = [
            (doc_dict[doc_id], score)
            for doc_id, score in scores.items()
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked
```

### CLI Commands

```bash
# Register document (auto-tags, detects duplicates)
apm doc register docs/architecture/jwt-auth.md \
  --type=design \
  --summary="JWT token-based authentication design for multi-tenant platform" \
  --work-item=5

# Output:
# ✅ Document registered: JWT Authentication Design
# 🏷️  Auto-tags: jwt (0.95), authentication (0.90), token (0.85), security (0.80)
# ⚠️  Similar documents found:
#    1. "API Authentication Spec" (72% similar) - docs/api/auth-spec.md
#    Continue? [y/N]

# Search documents
apm doc search "jwt authentication"

# Output:
# 🔍 Found 3 documents (0.08s):
#
# 1. JWT Authentication Design (relevance: 0.95)
#    Type: design | Status: approved
#    Location: docs/architecture/jwt-auth.md
#    Tags: jwt, authentication, token, security
#    Summary: JWT token-based authentication design...
#
# 2. API Authentication Spec (relevance: 0.68)
#    Type: spec | Status: approved
#    Location: docs/api/auth-spec.md
#
# 3. User Login Flow (relevance: 0.52)
#    Type: guide | Status: draft
#    Location: docs/guides/user-login.md

# List documents by type
apm doc list --type=adr --status=approved

# Find related documents
apm doc related docs/architecture/jwt-auth.md

# Output:
# 📚 Related documents:
#
# Directly referenced:
#  • API Authentication Spec (implements this design)
#  • Security Best Practices (referenced by this doc)
#
# Work item related (WI-5):
#  • Multi-Tenant Database Design
#  • Tenant Isolation Strategy
#
# Tag related (jwt, authentication):
#  • OAuth2 Integration Guide
#  • Session Management Spec

# Update document metadata
apm doc update docs/architecture/jwt-auth.md \
  --status=superseded \
  --superseded-by=docs/architecture/jwt-auth-v2.md

# Generate document report
apm doc report --work-item=5

# Output:
# 📊 Documentation Report: Work Item #5
#
# Documents: 12 total
#  • ADRs: 3
#  • Specs: 4
#  • Guides: 3
#  • Plans: 2
#
# Status:
#  • Approved: 8
#  • Draft: 3
#  • Review: 1
#
# Coverage:
#  • Database: 100% (3 docs)
#  • Authentication: 100% (4 docs)
#  • API: 75% (3/4 features)
#  • Testing: 50% (1 doc, need more)
#
# Recommendations:
#  ⚠️  Add testing documentation
#  ⚠️  Update "User Login Flow" (draft for 2 weeks)
```

---

## Consequences

### Positive

1. **Fast Search**
   - <100ms searches (vs 5-10s with grep)
   - Indexed database queries
   - No filesystem scanning

2. **Prevent Duplication**
   - Detect similar docs before creation
   - Save wasted effort
   - Maintain single source of truth

3. **Better Organization**
   - Know what documents exist
   - Understand document relationships
   - Track document evolution

4. **Cross-Referencing**
   - Link docs to work items, decisions, tasks
   - Find all related documentation
   - Complete knowledge graph

5. **Quality Tracking**
   - Document status (draft → review → approved)
   - Review workflow
   - Superseded document tracking

### Negative

1. **Registration Overhead**
   - Must register documents in database
   - Extra step after creating doc
   - Risk of unregistered docs

2. **Sync Issues**
   - Document content vs metadata can drift
   - File moves break references
   - Need to handle renames/deletes

3. **Storage Duplication**
   - Metadata in database
   - Content on filesystem
   - Summaries stored twice

4. **Tagging Quality**
   - Auto-tags may be inaccurate
   - Requires manual review/correction
   - Tag vocabulary can become messy

### Mitigation Strategies

1. **Auto-Registration**
   - Git hooks register new .md files automatically
   - File watcher detects changes
   - CLI reminds to register

2. **Sync Management**
   - Content hash detects changes
   - Update metadata on content change
   - Handle file moves/renames gracefully

3. **Storage Optimization**
   - Compress summaries
   - Store only searchable metadata
   - Archive old document versions

4. **Tag Quality**
   - Manual tag review workflow
   - Tag confidence thresholds
   - Tag vocabulary management

---

## Implementation Plan

### Phase 1: Core Document Store (Week 1-2)

```yaml
Week 1: Database & Models
  Tasks:
    - Create documents table
    - Create document_tags table
    - Create document_references table
    - Add indices for search

  Deliverables:
    - Migration: 0019_add_document_store.py
    - Models: Document, DocumentTag, DocumentReference
    - Tests: test_document_models.py

  Success Criteria:
    - CRUD operations work
    - Queries <100ms
    - Relationships correct

Week 2: Registration & Auto-Tagging
  Tasks:
    - Implement DocumentAutoTaggingService
    - CLI: apm doc register
    - Auto-registration git hook
    - Tag extraction

  Deliverables:
    - agentpm/core/documents/auto_tagging.py
    - CLI commands
    - Git hooks
    - Tests

  Success Criteria:
    - Documents can be registered
    - Auto-tagging achieves >80% accuracy
    - Git hook works
```

### Phase 2: Search & Discovery (Week 3-4)

```yaml
Week 3: Search Implementation
  Tasks:
    - Implement DocumentSearchService
    - Multi-field search
    - Relevance ranking
    - Search result caching

  Deliverables:
    - agentpm/core/documents/search.py
    - CLI: apm doc search
    - Search tests-BAK
    - Performance benchmarks

  Success Criteria:
    - Search <100ms (P95)
    - Relevance ranking accurate
    - Handles typos gracefully

Week 4: Duplicate Detection
  Tasks:
    - Implement DuplicateDetectionService
    - Similarity calculation
    - Duplicate warnings
    - Integration with registration

  Deliverables:
    - agentpm/core/documents/duplicates.py
    - Duplicate detection tests-BAK
    - CLI warnings
    - User prompts

  Success Criteria:
    - Detects duplicates >80% similar
    - No false positives <60% similar
    - User can override if needed
```

### Phase 3: Cross-Referencing (Week 5-6)

```yaml
Week 5: Document References
  Tasks:
    - Implement cross-reference system
    - Link to work items, decisions, tasks
    - Related document discovery
    - Reference visualization

  Deliverables:
    - Document reference models
    - CLI: apm doc related
    - Reference graph visualization
    - Tests

  Success Criteria:
    - Can link docs to any entity
    - Related docs discovered accurately
    - Graph visualization works

Week 6: Version Tracking
  Tasks:
    - Git integration
    - Document evolution tracking
    - Superseded document handling
    - Version comparison

  Deliverables:
    - Git integration
    - Version tracking
    - CLI: apm doc history
    - Comparison tool

  Success Criteria:
    - Tracks document changes
    - Can view evolution
    - Handles superseded docs
```

### Phase 4: Quality & Reports (Week 7-8)

```yaml
Week 7: Document Quality
  Tasks:
    - Review workflow
    - Status management
    - Quality metrics
    - Approval process

  Deliverables:
    - Review workflow implementation
    - CLI: apm doc review
    - Quality dashboard
    - Approval tracking

  Success Criteria:
    - Review workflow works
    - Quality metrics tracked
    - Approval process clear

Week 8: Reports & Analytics
  Tasks:
    - Document coverage reports
    - Gap analysis
    - Usage analytics
    - Integration testing

  Deliverables:
    - CLI: apm doc report
    - Coverage analysis
    - Usage metrics
    - E2E tests-BAK

  Success Criteria:
    - Reports show coverage gaps
    - Analytics track usage
    - All features tested
```

---

## Usage Examples

### Example 1: Registering New Document

```bash
# Create new architecture decision
vim docs/adrs/ADR-007-caching-strategy.md

# Register with AIPM
apm doc register docs/adrs/ADR-007-caching-strategy.md \
  --type=adr \
  --summary="Caching strategy using Redis for session data and PostgreSQL for persistent data" \
  --work-item=10

# Output:
✅ Analyzing document...
📄 Title: ADR-007: Caching Strategy
🏷️  Auto-tags detected:
   • redis (confidence: 0.95, type: technology)
   • caching (confidence: 0.90, type: concept)
   • postgresql (confidence: 0.85, type: technology)
   • session (confidence: 0.80, type: concept)

⚠️  Similar documents found:
   1. "Database Performance Optimization" (68% similar)
      Location: docs/architecture/db-performance.md
      Tags: postgresql, caching, performance
      This doc mentions Redis caching briefly.

   Continue registration? [Y/n] y

✅ Document registered successfully!
   Document ID: doc_abc123
   Status: draft
   Auto-tags: 4 tags added
   Linked to Work Item #10
```

### Example 2: Searching Before Creating

```bash
# Developer about to write "API Rate Limiting" doc
# First, search if it exists:

apm doc search "rate limiting api"

# Output:
🔍 Searching documents... (0.09s)

Found 2 documents:

1. API Rate Limiting Design (relevance: 0.92) ⭐
   Type: design | Status: approved | Updated: 2 weeks ago
   Location: docs/architecture/api-rate-limiting.md
   Tags: api, rate-limiting, throttling, redis
   Summary: Token bucket algorithm for API rate limiting,
            100 req/min per tenant, Redis-backed...
   Work Item: #8 | Decision: DEC-015

2. API Gateway Configuration (relevance: 0.65)
   Type: spec | Status: approved | Updated: 1 month ago
   Location: docs/specs/api-gateway-spec.md
   Tags: api, gateway, routing

💡 Tip: Document #1 already covers rate limiting.
   Consider updating it instead of creating new doc.

# Developer reads existing doc, realizes it covers their needs
# Saves 2 hours of duplicate work! ✅
```

### Example 3: Finding Related Documentation

```bash
# Working on authentication task
# Need to find all related docs

apm doc related --work-item=5

# Output:
📚 Documents for Work Item #5: Multi-Tenant Authentication

Core Documentation (3 docs):
 ✅ JWT Authentication Design (ADR-003)
    Status: approved | docs/adrs/ADR-003-jwt-auth.md

 ✅ API Authentication Spec
    Status: approved | docs/specs/api-auth.md

 📝 Token Refresh Strategy
    Status: draft | docs/architecture/token-refresh.md

Related by Tags (authentication, jwt):
 • OAuth2 Integration Guide (docs/guides/oauth2.md)
 • Security Best Practices (docs/security/best-practices.md)

Referenced Decisions:
 • DEC-008: Use JWT over session-based auth
 • DEC-012: Token expiry times (15min/7day)

Code References:
 • middleware/auth.py (implements JWT middleware)
 • services/auth_service.py (token generation)

💡 Tip: 1 document in draft status for 2 weeks.
   Consider completing or archiving.
```

---

## Related Documents

- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Overall system
- **ADR-001**: Provider Abstraction Architecture
- **ADR-002**: Context Compression Strategy
- **ADR-003**: Sub-Agent Communication Protocol
- **ADR-004**: Evidence Storage and Retrieval
- **ADR-005**: Multi-Provider Session Management

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Metadata in database, content on filesystem | Fast search + simple storage |
| 2025-10-12 | Auto-tagging with confidence scores | Balance automation + quality |
| 2025-10-12 | Duplicate detection before registration | Prevent wasted effort |
| 2025-10-12 | Cross-reference to work items/decisions | Complete knowledge graph |
| 2025-10-12 | Git integration for version tracking | Leverage existing VCS |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype document registration
3. Test search performance
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
