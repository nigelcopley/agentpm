# Context-Aware Document Visibility Policy System - Design Specification

**Version:** 1.0.0
**Date:** 2025-10-25
**Status:** Design Complete

---

## Executive Summary

This design specifies a **context-aware document visibility policy system** that automatically determines whether documents should be private (`.agentpm/docs/`) or public (`docs/`) based on:

1. **Document type** (user guide, planning doc, architecture, etc.)
2. **Project context** (team size, development stage, collaboration model)
3. **Document lifecycle** (draft, review, published, archived)
4. **Audience** (internal, team, contributors, users, public)

The system integrates with APM's database-first architecture and supports automated publishing workflows with quality gates.

---

## 1. Architecture Overview

### 1.1 Core Principles

1. **Database-First**: Visibility policies stored in database, not files
2. **Context-Aware**: Decisions based on project context + document metadata
3. **Lifecycle-Driven**: Documents progress through draft → review → published → archived
4. **Source of Truth**: `.agentpm/docs/` is source, `docs/` is published copy
5. **Agent-Friendly**: Clear rules for automated decision-making

### 1.2 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   APM Document Visibility System            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Policy     │  │   Context    │  │   Publisher     │  │
│  │   Matrix     │─▶│   Evaluator  │─▶│   Engine        │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│         │                  │                    │          │
│         ▼                  ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Database (agents.db)                    │  │
│  │  - document_references (visibility metadata)         │  │
│  │  - document_visibility_policies (project config)     │  │
│  │  - document_audit_log (publication history)          │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                                       │          │
│         ▼                                       ▼          │
│  ┌───────────────┐                    ┌──────────────────┐ │
│  │ .agentpm/docs/│                    │     docs/        │ │
│  │ (private)     │────────copy───────▶│   (public)       │ │
│  │ SOURCE        │                    │   PUBLISHED      │ │
│  └───────────────┘                    └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 File System Layout

```
project-root/
├── .agentpm/
│   ├── docs/                          # Private documents (source of truth)
│   │   ├── planning/
│   │   │   ├── requirements/
│   │   │   ├── investigation_report/
│   │   │   └── research_report/
│   │   ├── architecture/
│   │   │   ├── design_doc/
│   │   │   ├── adr/
│   │   │   └── technical_spec/
│   │   ├── guides/
│   │   │   ├── user_guide/          # Draft versions
│   │   │   ├── developer_guide/
│   │   │   └── admin_guide/
│   │   ├── processes/
│   │   │   ├── test_plan/
│   │   │   ├── implementation_plan/
│   │   │   └── migration_guide/
│   │   ├── operations/
│   │   │   ├── runbook/
│   │   │   └── deployment_guide/
│   │   ├── communication/
│   │   │   ├── session_summary/
│   │   │   └── status_report/
│   │   └── governance/
│   │       └── quality_gates_spec/
│   ├── agents.db                      # Database
│   └── config.yaml                    # Bootstrap configuration
│
└── docs/                              # Public documents (published copies)
    ├── guides/
    │   ├── user_guide/               # Published user guides
    │   ├── developer_guide/
    │   ├── admin_guide/
    │   └── troubleshooting/
    ├── reference/
    │   ├── api_doc/
    │   └── specification/
    └── processes/
        ├── migration_guide/
        ├── integration_guide/
        └── refactoring_guide/
```

---

## 2. Database Schema

### 2.1 Migration: Add Visibility Fields to `document_references`

```sql
-- Migration: 001_add_document_visibility.sql

-- Add visibility fields to existing document_references table
ALTER TABLE document_references ADD COLUMN visibility TEXT DEFAULT 'private';
ALTER TABLE document_references ADD COLUMN audience TEXT DEFAULT 'internal';
ALTER TABLE document_references ADD COLUMN lifecycle_stage TEXT DEFAULT 'draft';
ALTER TABLE document_references ADD COLUMN auto_publish BOOLEAN DEFAULT 0;
ALTER TABLE document_references ADD COLUMN publication_date TEXT DEFAULT NULL;
ALTER TABLE document_references ADD COLUMN source_path TEXT DEFAULT NULL;
ALTER TABLE document_references ADD COLUMN public_path TEXT DEFAULT NULL;
ALTER TABLE document_references ADD COLUMN last_synced TEXT DEFAULT NULL;
ALTER TABLE document_references ADD COLUMN review_status TEXT DEFAULT NULL;
ALTER TABLE document_references ADD COLUMN reviewer_agent TEXT DEFAULT NULL;

-- Add indexes for queries
CREATE INDEX idx_document_visibility ON document_references(visibility);
CREATE INDEX idx_document_lifecycle ON document_references(lifecycle_stage);
CREATE INDEX idx_document_audience ON document_references(audience);

-- Add constraints
CREATE TABLE document_visibility_check AS SELECT 1 WHERE
  (SELECT COUNT(*) FROM document_references
   WHERE visibility NOT IN ('private', 'public', 'restricted')) = 0;
```

### 2.2 New Table: `document_visibility_policies`

```sql
-- Project-level visibility policy configuration
CREATE TABLE document_visibility_policies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  policy_name TEXT NOT NULL UNIQUE,       -- e.g., "default", "production"
  team_size TEXT DEFAULT 'solo',          -- solo | small | medium | large
  dev_stage TEXT DEFAULT 'development',   -- development | staging | production
  collaboration_model TEXT DEFAULT 'private',  -- private | internal | open_source
  auto_publish_on_approval BOOLEAN DEFAULT 0,
  require_review_before_publish BOOLEAN DEFAULT 1,
  default_visibility TEXT DEFAULT 'private',
  visibility_overrides TEXT DEFAULT '{}',  -- JSON: {"category.type": "public"}
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  is_active BOOLEAN DEFAULT 1
);

-- Insert default policy
INSERT INTO document_visibility_policies (
  policy_name, team_size, dev_stage, collaboration_model
) VALUES (
  'default', 'solo', 'development', 'private'
);
```

### 2.3 New Table: `document_audit_log`

```sql
-- Track all publication events for audit trail
CREATE TABLE document_audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  action TEXT NOT NULL,                -- publish | unpublish | update | review
  previous_visibility TEXT,
  new_visibility TEXT,
  previous_lifecycle TEXT,
  new_lifecycle TEXT,
  actor_agent TEXT,                    -- Which agent performed action
  reason TEXT,
  timestamp TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (document_id) REFERENCES document_references(id)
);

CREATE INDEX idx_audit_document ON document_audit_log(document_id);
CREATE INDEX idx_audit_action ON document_audit_log(action);
CREATE INDEX idx_audit_timestamp ON document_audit_log(timestamp);
```

### 2.4 Enhanced `document_references` Schema

```sql
-- Complete schema with visibility fields
CREATE TABLE document_references (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- Core fields (existing)
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  category TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),

  -- NEW: Visibility fields
  visibility TEXT DEFAULT 'private',        -- private | public | restricted
  audience TEXT DEFAULT 'internal',         -- internal | team | contributors | users | public
  lifecycle_stage TEXT DEFAULT 'draft',     -- draft | review | approved | published | archived
  auto_publish BOOLEAN DEFAULT 0,           -- Auto-copy to docs/ when approved
  publication_date TEXT DEFAULT NULL,       -- When published to docs/
  source_path TEXT DEFAULT NULL,            -- .agentpm/docs/... (source of truth)
  public_path TEXT DEFAULT NULL,            -- docs/... (published copy)
  last_synced TEXT DEFAULT NULL,            -- Last sync time
  review_status TEXT DEFAULT NULL,          -- pending | approved | changes_requested
  reviewer_agent TEXT DEFAULT NULL,         -- Agent who reviewed

  -- Constraints
  CHECK(visibility IN ('private', 'public', 'restricted')),
  CHECK(audience IN ('internal', 'team', 'contributors', 'users', 'public')),
  CHECK(lifecycle_stage IN ('draft', 'review', 'approved', 'published', 'archived'))
);
```

---

## 3. Visibility Policy Matrix

### 3.1 Policy Structure

```python
# agentpm/core/documents/visibility/policy.py

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class VisibilityPolicy:
    """Policy for a specific document type."""
    default_visibility: str  # 'private' | 'public' | 'restricted'
    default_audience: str    # 'internal' | 'team' | 'contributors' | 'users' | 'public'
    allow_public: bool       # Can ever be public
    require_review: bool     # Needs review before publish
    auto_publish_on: list    # ['approval', 'gate_pass', 'phase_advance']
    base_score: int          # 0-100 for context scoring


DOCUMENT_VISIBILITY_POLICIES: Dict[str, Dict[str, VisibilityPolicy]] = {
    # ============================================================
    # PLANNING - Always Private (Internal Process)
    # ============================================================
    'planning': {
        'idea': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=10
        ),
        'requirements': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=15
        ),
        'user_story': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=10
        ),
        'use_case': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'research_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=15
        ),
        'analysis_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'investigation_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=15
        ),
        'assessment_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'feasibility_study': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'competitive_analysis': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=10
        ),
    },

    # ============================================================
    # ARCHITECTURE - Private Until Stable, Then Public
    # ============================================================
    'architecture': {
        'architecture_doc': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=True,
            require_review=True,
            auto_publish_on=['phase_advance'],  # Publish at O1
            base_score=50
        ),
        'design_doc': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=45
        ),
        'adr': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=55
        ),
        'technical_spec': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=True,
            require_review=True,
            auto_publish_on=['phase_advance'],
            base_score=60
        ),
    },

    # ============================================================
    # GUIDES - Always Public (Users Need Them)
    # ============================================================
    'guides': {
        'user_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=90
        ),
        'admin_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=85
        ),
        'developer_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='contributors',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=85
        ),
        'troubleshooting': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=95
        ),
        'faq': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=90
        ),
        'other': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=75
        ),
    },

    # ============================================================
    # REFERENCE - Always Public (External Access)
    # ============================================================
    'reference': {
        'api_doc': VisibilityPolicy(
            default_visibility='public',
            default_audience='public',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=95
        ),
        'specification': VisibilityPolicy(
            default_visibility='public',
            default_audience='public',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=90
        ),
    },

    # ============================================================
    # PROCESSES - Mixed (Depends on Audience)
    # ============================================================
    'processes': {
        'implementation_plan': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'refactoring_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='contributors',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=70
        ),
        'migration_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='users',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=85
        ),
        'integration_guide': VisibilityPolicy(
            default_visibility='public',
            default_audience='contributors',
            allow_public=True,
            require_review=True,
            auto_publish_on=['approval'],
            base_score=80
        ),
        'test_plan': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=25
        ),
        'test_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'coverage_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'validation_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=25
        ),
    },

    # ============================================================
    # GOVERNANCE - Always Private (Sensitive)
    # ============================================================
    'governance': {
        'business_pillars': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=5
        ),
        'market_research': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=5
        ),
        'stakeholder_analysis': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=10
        ),
        'quality_gates_spec': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=15
        ),
    },

    # ============================================================
    # OPERATIONS - Private (Sensitive Systems Info)
    # ============================================================
    'operations': {
        'runbook': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,  # Can override to True if needed
            require_review=True,
            auto_publish_on=[],
            base_score=30
        ),
        'deployment_guide': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,  # Can override to True
            require_review=True,
            auto_publish_on=[],
            base_score=35
        ),
        'monitoring_guide': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=25
        ),
        'incident_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=10
        ),
    },

    # ============================================================
    # COMMUNICATION - Private (Internal Status)
    # ============================================================
    'communication': {
        'session_summary': VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=15
        ),
        'status_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'progress_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
        'milestone_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,  # Can override for stakeholder visibility
            require_review=False,
            auto_publish_on=[],
            base_score=30
        ),
        'retrospective_report': VisibilityPolicy(
            default_visibility='private',
            default_audience='team',
            allow_public=False,
            require_review=False,
            auto_publish_on=[],
            base_score=20
        ),
    },
}
```

### 3.2 Context Scoring System

```python
# agentpm/core/documents/visibility/context.py

from typing import Dict, Any

class ContextScorer:
    """Evaluates context to determine visibility score."""

    # Context multipliers
    TEAM_SIZE_MULTIPLIERS = {
        'solo': 0.5,      # Solo dev: lean toward private
        'small': 0.8,     # Small team: moderate sharing
        'medium': 1.0,    # Medium team: balanced
        'large': 1.3,     # Large team: lean toward public
    }

    DEV_STAGE_BONUSES = {
        'development': 0,    # Dev: keep private
        'staging': 10,       # Staging: preparing for public
        'production': 25,    # Production: should be public
    }

    COLLABORATION_BONUSES = {
        'private': 0,        # Private: minimize public docs
        'internal': 15,      # Internal: share within team
        'open_source': 35,   # Open source: maximize transparency
    }

    LIFECYCLE_BONUSES = {
        'draft': 0,          # Draft: private
        'review': 5,         # Review: considering publication
        'approved': 10,      # Approved: ready for public
        'published': 15,     # Published: already public
        'archived': -20,     # Archived: remove from public
    }

    def calculate_visibility_score(
        self,
        base_score: int,
        team_size: str,
        dev_stage: str,
        collaboration_model: str,
        lifecycle_stage: str = 'draft'
    ) -> int:
        """
        Calculate visibility score from context.

        Returns:
            0-100 score where:
            - 0-40: private
            - 40-60: restricted (team only)
            - 60-100: public
        """
        score = base_score

        # Apply team size multiplier
        score *= self.TEAM_SIZE_MULTIPLIERS.get(team_size, 1.0)

        # Add stage bonus
        score += self.DEV_STAGE_BONUSES.get(dev_stage, 0)

        # Add collaboration bonus
        score += self.COLLABORATION_BONUSES.get(collaboration_model, 0)

        # Add lifecycle bonus
        score += self.LIFECYCLE_BONUSES.get(lifecycle_stage, 0)

        # Clamp to 0-100
        return max(0, min(100, int(score)))

    def score_to_visibility(self, score: int) -> str:
        """Convert score to visibility level."""
        if score >= 60:
            return 'public'
        elif score >= 40:
            return 'restricted'
        else:
            return 'private'

    def score_to_audience(self, score: int, policy: VisibilityPolicy) -> str:
        """Convert score to audience level."""
        if score >= 80:
            return 'public'
        elif score >= 60:
            return 'users'
        elif score >= 40:
            return 'contributors'
        elif score >= 20:
            return 'team'
        else:
            return 'internal'
```

---

## 4. Path Generation Logic

### 4.1 Path Generator

```python
# agentpm/core/documents/visibility/paths.py

import re
from pathlib import Path
from typing import Tuple, Optional
from agentpm.core.documents.visibility.policy import DOCUMENT_VISIBILITY_POLICIES
from agentpm.core.documents.visibility.context import ContextScorer

def slugify(text: str) -> str:
    """Convert title to filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class DocumentPathGenerator:
    """Generates file paths for documents based on visibility."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.private_base = project_root / '.agentpm' / 'docs'
        self.public_base = project_root / 'docs'
        self.scorer = ContextScorer()

    def generate_paths(
        self,
        category: str,
        doc_type: str,
        title: str,
        project_config: Dict[str, Any],
        lifecycle_stage: str = 'draft',
        visibility_override: Optional[str] = None
    ) -> Tuple[Path, Path, str, str]:
        """
        Generate source and public paths for document.

        Args:
            category: Document category (guides, planning, etc.)
            doc_type: Document type (user_guide, adr, etc.)
            title: Document title
            project_config: Project visibility configuration
            lifecycle_stage: Current lifecycle stage
            visibility_override: Force specific visibility

        Returns:
            (source_path, public_path, visibility, audience)
        """
        # Get policy for document type
        policy = self._get_policy(category, doc_type)

        # Determine visibility
        if visibility_override:
            visibility = visibility_override
            audience = policy.default_audience
        else:
            visibility, audience = self._determine_visibility(
                policy, project_config, lifecycle_stage
            )

        # Generate filename
        filename = slugify(title) + '.md'

        # Build paths
        subdir = Path(category) / doc_type
        source_path = self.private_base / subdir / filename

        if visibility == 'public':
            public_path = self.public_base / subdir / filename
        else:
            public_path = None

        return source_path, public_path, visibility, audience

    def _get_policy(self, category: str, doc_type: str) -> VisibilityPolicy:
        """Get policy for document type."""
        category_policies = DOCUMENT_VISIBILITY_POLICIES.get(category, {})
        return category_policies.get(doc_type, VisibilityPolicy(
            default_visibility='private',
            default_audience='internal',
            allow_public=False,
            require_review=True,
            auto_publish_on=[],
            base_score=30
        ))

    def _determine_visibility(
        self,
        policy: VisibilityPolicy,
        project_config: Dict[str, Any],
        lifecycle_stage: str
    ) -> Tuple[str, str]:
        """Determine visibility from policy and context."""
        # Check override
        override_key = f"{policy.category}.{policy.type}"
        overrides = project_config.get('visibility_overrides', {})
        if override_key in overrides:
            return overrides[override_key], policy.default_audience

        # Calculate context score
        score = self.scorer.calculate_visibility_score(
            base_score=policy.base_score,
            team_size=project_config.get('team_size', 'solo'),
            dev_stage=project_config.get('dev_stage', 'development'),
            collaboration_model=project_config.get('collaboration_model', 'private'),
            lifecycle_stage=lifecycle_stage
        )

        # Convert score to visibility
        visibility = self.scorer.score_to_visibility(score)
        audience = self.scorer.score_to_audience(score, policy)

        # Respect allow_public constraint
        if not policy.allow_public and visibility == 'public':
            visibility = 'restricted'

        return visibility, audience
```

### 4.2 Document Frontmatter

Every document file should include YAML frontmatter:

```markdown
---
# Document Metadata (synced with database)
doc_id: 123
visibility: public
audience: users
lifecycle_stage: published
publication_date: 2025-10-25T10:30:00Z
last_updated: 2025-10-25T10:30:00Z

# Document Classification
category: guides
type: user_guide
title: "Getting Started with APM"

# Work Item Association
entity_type: work_item
entity_id: 158

# Review Status
review_status: approved
reviewer_agent: quality-gatekeeper
---

# Getting Started with APM

Your document content here...
```

---

## 5. Publishing Workflow

### 5.1 Lifecycle State Machine

```
┌─────────┐
│  DRAFT  │ ◀─── Document created (private by default)
└────┬────┘
     │ apm document submit-review <id>
     ▼
┌─────────┐
│ REVIEW  │ ◀─── Assigned to reviewer agent
└────┬────┘
     │ apm document approve <id>
     │ OR apm document request-changes <id>
     ▼
┌──────────┐
│ APPROVED │ ◀─── Review passed, ready to publish
└────┬─────┘
     │ apm document publish <id>
     │ OR auto-publish (if enabled)
     ▼
┌───────────┐
│ PUBLISHED │ ◀─── Copied to docs/, visible to audience
└────┬──────┘
     │ apm document unpublish <id>
     ▼
┌──────────┐
│ ARCHIVED │ ◀─── Removed from docs/, kept in .agentpm/docs/
└──────────┘
```

### 5.2 Publishing Engine

```python
# agentpm/core/documents/visibility/publisher.py

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from agentpm.core.db import Database
from agentpm.core.documents.models import Document

class DocumentPublisher:
    """Handles document publishing workflow."""

    def __init__(self, db: Database, project_root: Path):
        self.db = db
        self.project_root = project_root

    def submit_for_review(
        self,
        document_id: int,
        reviewer_agent: str = 'quality-gatekeeper'
    ) -> None:
        """Submit document for review."""
        self.db.execute(
            """
            UPDATE document_references
            SET lifecycle_stage = 'review',
                review_status = 'pending',
                reviewer_agent = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (reviewer_agent, datetime.now().isoformat(), document_id)
        )

        self._log_audit(document_id, 'submit_review', reviewer_agent)

    def approve_document(
        self,
        document_id: int,
        approver_agent: str,
        auto_publish: bool = None
    ) -> None:
        """Approve document after review."""
        doc = self._get_document(document_id)

        # Update to approved
        self.db.execute(
            """
            UPDATE document_references
            SET lifecycle_stage = 'approved',
                review_status = 'approved',
                updated_at = ?
            WHERE id = ?
            """,
            (datetime.now().isoformat(), document_id)
        )

        self._log_audit(document_id, 'approve', approver_agent)

        # Auto-publish if enabled
        if auto_publish is None:
            auto_publish = doc.auto_publish

        if auto_publish and doc.visibility == 'public':
            self.publish_document(document_id, approver_agent)

    def request_changes(
        self,
        document_id: int,
        reviewer_agent: str,
        reason: str
    ) -> None:
        """Request changes to document."""
        self.db.execute(
            """
            UPDATE document_references
            SET lifecycle_stage = 'draft',
                review_status = 'changes_requested',
                updated_at = ?
            WHERE id = ?
            """,
            (datetime.now().isoformat(), document_id)
        )

        self._log_audit(document_id, 'request_changes', reviewer_agent, reason)

    def publish_document(
        self,
        document_id: int,
        publisher_agent: str
    ) -> Optional[Path]:
        """
        Publish document to public docs/.

        Returns:
            Path to published file, or None if not publishable
        """
        doc = self._get_document(document_id)

        # Verify can publish
        if doc.visibility != 'public':
            raise ValueError(f"Document {document_id} is not public")

        if doc.lifecycle_stage not in ['approved', 'published']:
            raise ValueError(f"Document {document_id} not approved for publication")

        if not doc.source_path or not Path(doc.source_path).exists():
            raise ValueError(f"Document {document_id} source file not found")

        # Copy to public location
        source = Path(doc.source_path)
        if doc.public_path:
            public = Path(doc.public_path)
        else:
            # Generate public path
            public = self._generate_public_path(source)

        # Ensure parent directory exists
        public.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source, public)

        # Update database
        now = datetime.now().isoformat()
        self.db.execute(
            """
            UPDATE document_references
            SET lifecycle_stage = 'published',
                publication_date = ?,
                public_path = ?,
                last_synced = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (now, str(public), now, now, document_id)
        )

        self._log_audit(document_id, 'publish', publisher_agent)

        return public

    def unpublish_document(
        self,
        document_id: int,
        actor_agent: str,
        reason: str = None
    ) -> None:
        """Unpublish document (remove from docs/, keep in .agentpm/docs/)."""
        doc = self._get_document(document_id)

        if doc.public_path and Path(doc.public_path).exists():
            Path(doc.public_path).unlink()

        self.db.execute(
            """
            UPDATE document_references
            SET lifecycle_stage = 'archived',
                public_path = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (datetime.now().isoformat(), document_id)
        )

        self._log_audit(document_id, 'unpublish', actor_agent, reason)

    def sync_published_documents(self, dry_run: bool = False) -> dict:
        """
        Sync all published documents from source to public.

        Returns:
            Report of sync actions
        """
        published_docs = self.db.execute(
            """
            SELECT id, source_path, public_path
            FROM document_references
            WHERE lifecycle_stage = 'published'
              AND visibility = 'public'
            """
        ).fetchall()

        report = {
            'synced': [],
            'skipped': [],
            'errors': []
        }

        for doc_id, source_path, public_path in published_docs:
            try:
                source = Path(source_path)
                public = Path(public_path) if public_path else None

                if not source.exists():
                    report['errors'].append((doc_id, 'Source file not found'))
                    continue

                if not public:
                    report['skipped'].append((doc_id, 'No public path'))
                    continue

                if not dry_run:
                    public.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, public)

                    self.db.execute(
                        """
                        UPDATE document_references
                        SET last_synced = ?
                        WHERE id = ?
                        """,
                        (datetime.now().isoformat(), doc_id)
                    )

                report['synced'].append((doc_id, str(public)))

            except Exception as e:
                report['errors'].append((doc_id, str(e)))

        return report

    def _get_document(self, document_id: int) -> Document:
        """Fetch document from database."""
        result = self.db.execute(
            "SELECT * FROM document_references WHERE id = ?",
            (document_id,)
        ).fetchone()

        if not result:
            raise ValueError(f"Document {document_id} not found")

        return Document(**dict(result))

    def _generate_public_path(self, source_path: Path) -> Path:
        """Generate public path from source path."""
        # .agentpm/docs/category/type/file.md → docs/category/type/file.md
        relative = source_path.relative_to(self.project_root / '.agentpm' / 'docs')
        return self.project_root / 'docs' / relative

    def _log_audit(
        self,
        document_id: int,
        action: str,
        actor_agent: str,
        reason: str = None
    ) -> None:
        """Log action to audit table."""
        doc = self._get_document(document_id)

        self.db.execute(
            """
            INSERT INTO document_audit_log (
                document_id, action, previous_visibility, new_visibility,
                previous_lifecycle, new_lifecycle, actor_agent, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id, action,
                doc.visibility, doc.visibility,
                doc.lifecycle_stage, doc.lifecycle_stage,
                actor_agent, reason
            )
        )
```

---

## 6. CLI Commands

### 6.1 Command Specifications

```python
# agentpm/cli/commands/document/visibility.py

import click
from pathlib import Path
from agentpm.core.documents.visibility.publisher import DocumentPublisher
from agentpm.core.db import get_database

@click.group()
def document():
    """Document visibility and publishing commands."""
    pass

@document.command()
@click.argument('document_id', type=int)
@click.option('--reviewer', default='quality-gatekeeper', help='Reviewer agent')
def submit_review(document_id: int, reviewer: str):
    """Submit document for review."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    publisher.submit_for_review(document_id, reviewer)
    click.echo(f"✓ Document {document_id} submitted for review by {reviewer}")

@document.command()
@click.argument('document_id', type=int)
@click.option('--auto-publish/--no-auto-publish', default=None,
              help='Auto-publish after approval')
def approve(document_id: int, auto_publish: bool):
    """Approve document after review."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    publisher.approve_document(document_id, 'user', auto_publish)
    click.echo(f"✓ Document {document_id} approved")

@document.command()
@click.argument('document_id', type=int)
@click.option('--reason', required=True, help='Reason for changes')
def request_changes(document_id: int, reason: str):
    """Request changes to document."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    publisher.request_changes(document_id, 'user', reason)
    click.echo(f"✓ Changes requested for document {document_id}")

@document.command()
@click.argument('document_id', type=int)
def publish(document_id: int):
    """Publish document to public docs/."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    try:
        public_path = publisher.publish_document(document_id, 'user')
        click.echo(f"✓ Document {document_id} published to {public_path}")
    except ValueError as e:
        click.echo(f"✗ Error: {e}", err=True)

@document.command()
@click.argument('document_id', type=int)
@click.option('--reason', help='Reason for unpublishing')
def unpublish(document_id: int, reason: str):
    """Unpublish document (remove from docs/)."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    publisher.unpublish_document(document_id, 'user', reason)
    click.echo(f"✓ Document {document_id} unpublished")

@document.command()
@click.option('--dry-run', is_flag=True, help='Show what would be synced')
def sync(dry_run: bool):
    """Sync all published documents from .agentpm/docs/ to docs/."""
    db = get_database()
    publisher = DocumentPublisher(db, Path.cwd())

    report = publisher.sync_published_documents(dry_run)

    if dry_run:
        click.echo("DRY RUN - No files modified")

    click.echo(f"\nSynced: {len(report['synced'])} documents")
    for doc_id, path in report['synced']:
        click.echo(f"  ✓ {doc_id}: {path}")

    if report['skipped']:
        click.echo(f"\nSkipped: {len(report['skipped'])} documents")
        for doc_id, reason in report['skipped']:
            click.echo(f"  - {doc_id}: {reason}")

    if report['errors']:
        click.echo(f"\nErrors: {len(report['errors'])} documents", err=True)
        for doc_id, error in report['errors']:
            click.echo(f"  ✗ {doc_id}: {error}", err=True)

@document.command()
@click.argument('document_id', type=int)
@click.option('--visibility', type=click.Choice(['private', 'public', 'restricted']),
              required=True, help='New visibility')
def set_visibility(document_id: int, visibility: str):
    """Change document visibility."""
    db = get_database()

    db.execute(
        """
        UPDATE document_references
        SET visibility = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (visibility, document_id)
    )

    click.echo(f"✓ Document {document_id} visibility changed to {visibility}")
```

### 6.2 Configuration Commands

```python
# agentpm/cli/commands/config/visibility_policy.py

@click.group()
def config():
    """Configuration management."""
    pass

@config.command()
def show_visibility_policy():
    """Show current visibility policy."""
    db = get_database()

    policy = db.execute(
        "SELECT * FROM document_visibility_policies WHERE is_active = 1"
    ).fetchone()

    if policy:
        click.echo(f"Team Size: {policy['team_size']}")
        click.echo(f"Dev Stage: {policy['dev_stage']}")
        click.echo(f"Collaboration Model: {policy['collaboration_model']}")
        click.echo(f"Auto-publish on Approval: {policy['auto_publish_on_approval']}")
        click.echo(f"Require Review: {policy['require_review_before_publish']}")

@config.command()
@click.option('--team-size', type=click.Choice(['solo', 'small', 'medium', 'large']))
@click.option('--dev-stage', type=click.Choice(['development', 'staging', 'production']))
@click.option('--collaboration', type=click.Choice(['private', 'internal', 'open_source']))
def set_visibility_policy(team_size: str, dev_stage: str, collaboration: str):
    """Update visibility policy configuration."""
    db = get_database()

    updates = []
    params = []

    if team_size:
        updates.append("team_size = ?")
        params.append(team_size)
    if dev_stage:
        updates.append("dev_stage = ?")
        params.append(dev_stage)
    if collaboration:
        updates.append("collaboration_model = ?")
        params.append(collaboration)

    if updates:
        db.execute(
            f"UPDATE document_visibility_policies SET {', '.join(updates)}, updated_at = datetime('now') WHERE is_active = 1",
            tuple(params)
        )
        click.echo("✓ Visibility policy updated")
```

---

## 7. Agent Instructions

### 7.1 Updated CLAUDE.md Section

Add to Section 3 (Specialist Agent Delegation):

```markdown
### **Document Creation with Visibility**

**When**: Creating any documentation
**Delegate to**:
\`\`\`
Task(
  subagent_type="documentation-writer-agent",
  description="Create [document type] with appropriate visibility",
  prompt="Create [document type] for [entity]:

  Document Details:
  - Title: [title]
  - Category: [category]  # planning | architecture | guides | reference | processes | operations | communication | governance
  - Type: [doc_type]      # See policy matrix for types
  - Content: [specify content sections]

  Visibility Settings:
  - Document will be created in .agentpm/docs/ (private by default)
  - Visibility determined by project context and document type
  - Public documents require review before publishing
  - Use 'apm document publish <id>' after approval

  Context: [entity details, requirements, audience]"
)
\`\`\`

**Document Type Selection Guide**:

**User-Facing (always public after review)**:
- guides.user_guide: User guides
- guides.troubleshooting: Troubleshooting guides
- guides.faq: FAQ documents
- reference.api_doc: API documentation
- processes.migration_guide: Migration guides for users

**Developer-Facing (public for contributors)**:
- guides.developer_guide: Developer guides
- processes.refactoring_guide: Refactoring guides
- processes.integration_guide: Integration guides

**Internal Process (always private)**:
- planning.*: All planning documents
- communication.*: Status reports, session summaries
- governance.*: Business strategy, quality gates
- operations.*: Runbooks, deployment guides (unless team override)

**Architecture (private until published)**:
- architecture.adr: Architecture Decision Records
- architecture.design_doc: Design documents
- architecture.technical_spec: Technical specifications
```

### 7.2 Agent Decision Matrix

```python
# Agents use this logic to determine document placement

def agent_determine_visibility(doc_type: str, category: str) -> dict:
    """
    Agent helper to determine document visibility settings.

    Returns:
        {
            'initial_visibility': 'private|public',
            'requires_review': bool,
            'can_auto_publish': bool,
            'recommended_audience': 'internal|team|users|public'
        }
    """

    # User guides → public after review
    if category == 'guides' and doc_type in ['user_guide', 'troubleshooting', 'faq']:
        return {
            'initial_visibility': 'private',  # Draft starts private
            'requires_review': True,
            'can_auto_publish': True,
            'recommended_audience': 'users'
        }

    # API docs → public after review
    if category == 'reference' and doc_type == 'api_doc':
        return {
            'initial_visibility': 'private',
            'requires_review': True,
            'can_auto_publish': True,
            'recommended_audience': 'public'
        }

    # Architecture → private until explicitly published
    if category == 'architecture':
        return {
            'initial_visibility': 'private',
            'requires_review': True,
            'can_auto_publish': False,  # Manual publish decision
            'recommended_audience': 'team'
        }

    # Planning, governance, communication → always private
    if category in ['planning', 'governance', 'communication']:
        return {
            'initial_visibility': 'private',
            'requires_review': False,
            'can_auto_publish': False,
            'recommended_audience': 'internal'
        }

    # Operations → private by default (can override)
    if category == 'operations':
        return {
            'initial_visibility': 'private',
            'requires_review': True,
            'can_auto_publish': False,
            'recommended_audience': 'team'
        }

    # Default → private, manual review
    return {
        'initial_visibility': 'private',
        'requires_review': True,
        'can_auto_publish': False,
        'recommended_audience': 'team'
    }
```

---

## 8. Project Configuration Schema

### 8.1 Database Storage (Recommended)

Store configuration in `project_metadata` table or dedicated `document_visibility_policies` table:

```python
# Default configuration (inserted at apm init)
DEFAULT_VISIBILITY_POLICY = {
    'policy_name': 'default',
    'team_size': 'solo',
    'dev_stage': 'development',
    'collaboration_model': 'private',
    'auto_publish_on_approval': False,
    'require_review_before_publish': True,
    'default_visibility': 'private',
    'visibility_overrides': {}
}
```

### 8.2 Config File Bootstrap (Optional)

`.agentpm/config.yaml` can bootstrap database configuration:

```yaml
# .agentpm/config.yaml

document_visibility_policy:
  # Project context
  team_size: small              # solo | small | medium | large
  dev_stage: development        # development | staging | production
  collaboration_model: internal  # private | internal | open_source

  # Publishing behavior
  auto_publish_on_approval: true
  require_review_before_publish: true

  # Override defaults for specific document types
  visibility_overrides:
    # Make operations docs public for team
    operations.runbook: public
    operations.deployment_guide: public

    # Keep quality gates visible to team
    governance.quality_gates_spec: restricted

    # Make ADRs public once approved
    architecture.adr: public

  # Export settings
  export_public_docs_to: docs/
  keep_private_docs_in: .agentpm/docs/

  # Sync behavior
  auto_sync_on_publish: true
  sync_on_work_item_complete: true
```

---

## 9. Integration with Work Item Lifecycle

### 9.1 Phase-Based Publishing Triggers

Documents can auto-publish when work items reach certain phases:

```python
# agentpm/core/workflow/phase_transitions.py

DOCUMENT_PUBLISH_TRIGGERS = {
    'D1_DISCOVERY': [],  # Nothing published yet
    'P1_PLAN': [],       # Planning docs stay private
    'I1_IMPLEMENTATION': [
        # Publish API docs when implementation complete
        ('reference', 'api_doc'),
    ],
    'R1_REVIEW': [
        # Publish user guides after review
        ('guides', 'user_guide'),
        ('guides', 'troubleshooting'),
    ],
    'O1_OPERATIONS': [
        # Publish all critical docs before deployment
        ('architecture', 'technical_spec'),
        ('processes', 'migration_guide'),
        ('guides', 'admin_guide'),
    ],
    'E1_EVOLUTION': [],  # Docs already published
}

def auto_publish_on_phase_advance(work_item_id: int, new_phase: str):
    """Auto-publish documents when work item advances phase."""
    triggers = DOCUMENT_PUBLISH_TRIGGERS.get(new_phase, [])

    if not triggers:
        return

    # Find documents for this work item matching trigger types
    docs = db.execute(
        """
        SELECT id, category, type
        FROM document_references
        WHERE entity_type = 'work_item'
          AND entity_id = ?
          AND lifecycle_stage IN ('approved', 'published')
          AND visibility = 'public'
        """,
        (work_item_id,)
    ).fetchall()

    publisher = DocumentPublisher(db, project_root)

    for doc_id, category, doc_type in docs:
        if (category, doc_type) in triggers:
            publisher.publish_document(doc_id, f'{new_phase}-auto-publish')
```

### 9.2 Quality Gate: Documentation Published

Add quality gate to O1 phase:

```python
# Rule: DOC-030 - Critical Documentation Published

def check_critical_docs_published(work_item_id: int) -> bool:
    """
    Verify critical user-facing documentation is published before O1.

    Required:
    - User guides
    - API documentation (if applicable)
    - Migration guides (if applicable)
    - Admin guides (if applicable)
    """

    required_doc_types = [
        ('guides', 'user_guide'),
        ('reference', 'api_doc'),
    ]

    for category, doc_type in required_doc_types:
        doc = db.execute(
            """
            SELECT id, lifecycle_stage
            FROM document_references
            WHERE entity_type = 'work_item'
              AND entity_id = ?
              AND category = ?
              AND type = ?
            """,
            (work_item_id, category, doc_type)
        ).fetchone()

        if doc and doc['lifecycle_stage'] != 'published':
            return False

    return True
```

---

## 10. Example Scenarios

### 10.1 Scenario: Solo Developer (Development Stage)

```yaml
# Configuration
team_size: solo
dev_stage: development
collaboration_model: private

# Behavior
- planning/* → .agentpm/docs/planning/ (private)
- architecture/* → .agentpm/docs/architecture/ (private)
- guides/user_guide → .agentpm/docs/guides/user_guide/ (draft)
  → Can publish manually when ready
- reference/api_doc → .agentpm/docs/reference/api_doc/ (draft)
  → Can publish manually when ready

# Most docs stay private until explicitly shared
```

### 10.2 Scenario: Small Team (Staging)

```yaml
# Configuration
team_size: small
dev_stage: staging
collaboration_model: internal

# Behavior
- planning/* → .agentpm/docs/planning/ (private)
- architecture/adr → .agentpm/docs/architecture/adr/ (restricted)
  → Visible to team, not public yet
- guides/user_guide → docs/guides/user_guide/ (public)
  → Auto-published on approval
- reference/api_doc → docs/reference/api_doc/ (public)
  → Auto-published on approval

# Team docs (architecture) visible internally
# User-facing docs go public
```

### 10.3 Scenario: Open Source (Production)

```yaml
# Configuration
team_size: large
dev_stage: production
collaboration_model: open_source

# Behavior
- planning/requirements → .agentpm/docs/planning/ (private)
  → Internal planning stays private
- architecture/adr → docs/architecture/adr/ (public)
  → Published ADRs visible to all
- guides/* → docs/guides/ (public)
  → All guides public
- reference/* → docs/reference/ (public)
  → All reference docs public
- governance/* → .agentpm/docs/governance/ (private)
  → Business strategy stays private
- operations/runbook → .agentpm/docs/operations/ (restricted)
  → OR docs/operations/ if override set

# Maximum transparency except sensitive governance
```

---

## 11. Implementation Checklist

### Phase 1: Database Schema (Week 1)
- [ ] Create migration `001_add_document_visibility.sql`
- [ ] Add fields to `document_references` table
- [ ] Create `document_visibility_policies` table
- [ ] Create `document_audit_log` table
- [ ] Update Pydantic models with new fields
- [ ] Update adapters for visibility fields

### Phase 2: Policy Engine (Week 2)
- [ ] Implement `DOCUMENT_VISIBILITY_POLICIES` matrix
- [ ] Implement `ContextScorer` class
- [ ] Implement `DocumentPathGenerator` class
- [ ] Write unit tests for policy evaluation
- [ ] Write unit tests for context scoring

### Phase 3: Publishing Workflow (Week 3)
- [ ] Implement `DocumentPublisher` class
- [ ] Implement lifecycle state machine
- [ ] Implement `publish_document()` method
- [ ] Implement `unpublish_document()` method
- [ ] Implement `sync_published_documents()` method
- [ ] Add frontmatter generation/parsing
- [ ] Write integration tests

### Phase 4: CLI Commands (Week 4)
- [ ] Implement `apm document submit-review <id>`
- [ ] Implement `apm document approve <id>`
- [ ] Implement `apm document request-changes <id>`
- [ ] Implement `apm document publish <id>`
- [ ] Implement `apm document unpublish <id>`
- [ ] Implement `apm document sync [--dry-run]`
- [ ] Implement `apm document set-visibility <id>`
- [ ] Implement `apm config show-visibility-policy`
- [ ] Implement `apm config set-visibility-policy`

### Phase 5: Agent Integration (Week 5)
- [ ] Update `documentation-writer-agent` with visibility logic
- [ ] Update `documentation-reader-agent` to use visibility
- [ ] Update `quality-gatekeeper` to check document gates
- [ ] Add visibility instructions to CLAUDE.md
- [ ] Create agent decision matrix helper
- [ ] Update documentation

### Phase 6: Work Item Integration (Week 6)
- [ ] Implement phase-based auto-publish triggers
- [ ] Add DOC-030 quality gate (critical docs published)
- [ ] Update release-ops-orch to check doc gates
- [ ] Add publish triggers to phase transitions
- [ ] Test full lifecycle integration

---

## 12. Success Metrics

### Quantitative Metrics
1. **Automation Rate**: >80% of documents auto-placed correctly
2. **Manual Overrides**: <10% of documents need visibility override
3. **Publishing Efficiency**: 90% reduction in manual publishing steps
4. **Review Compliance**: 100% of public docs reviewed before publish
5. **Sync Accuracy**: 100% of published docs synced correctly

### Qualitative Metrics
1. **Agent Clarity**: Agents can determine visibility without human input
2. **User Experience**: Users find public docs easily
3. **Developer Experience**: Contributors understand doc structure
4. **Audit Trail**: All publication events logged and trackable
5. **Flexibility**: System adapts to project context changes

---

## 13. Future Enhancements

### Version 2.0
- [ ] Document versioning (multiple published versions)
- [ ] Scheduled publishing (publish at specific time)
- [ ] Audience-based access control (OAuth/RBAC)
- [ ] Document templates with pre-set visibility
- [ ] Bulk operations (publish all related docs)

### Version 3.0
- [ ] Web UI for document management
- [ ] Document preview before publish
- [ ] Collaborative editing workflow
- [ ] Document analytics (views, downloads)
- [ ] Integration with external doc platforms (ReadTheDocs, GitBook)

---

## 14. Appendix

### A. Complete Policy Matrix Reference

See Section 3.1 for complete `DOCUMENT_VISIBILITY_POLICIES` matrix.

### B. Database Schema Reference

See Section 2 for complete database schema with all tables and indexes.

### C. CLI Command Reference

See Section 6 for all CLI commands with usage examples.

### D. Agent Instructions

See Section 7 for complete agent delegation patterns and decision matrix.

---

**End of Design Specification**

**Next Steps**:
1. Review and approve design
2. Create implementation work items for each phase
3. Begin Phase 1 (Database Schema) implementation
4. Iterate based on testing and feedback
