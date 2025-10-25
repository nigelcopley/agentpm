# Document Publishing Workflow - Quick Reference

**Related**: [Publishing Workflow Specification](./publishing-workflow-specification.md)

---

## Lifecycle States (6 Total)

| State | Description | Location | Visibility |
|-------|-------------|----------|------------|
| **DRAFT** | Initial creation | `.agentpm/docs/` | Author only |
| **REVIEW** | Under review | `.agentpm/docs/` | Reviewers |
| **APPROVED** | Review passed | `.agentpm/docs/` | Internal |
| **PUBLISHED** | Public copy exists | `.agentpm/docs/` + `docs/` | Public |
| **ARCHIVED** | Deprecated | `.agentpm/docs/` | Archive |
| **REJECTED** | Review failed | `.agentpm/docs/` (auto-reverts to DRAFT) | Author |

---

## State Transitions (Cheat Sheet)

```
DRAFT → REVIEW        apm document submit-review <id>
REVIEW → APPROVED     apm document approve <id>
REVIEW → REJECTED     apm document reject <id> --reason="..."
REJECTED → DRAFT      (automatic on reject)
APPROVED → PUBLISHED  apm document publish <id>  OR  auto-publish
PUBLISHED → APPROVED  apm document unpublish <id>
ANY → ARCHIVED        apm document archive <id>
```

---

## Auto-Publish Rules (When Does It Publish Automatically?)

### ✅ Always Auto-Publish on Approval

- `guides.user_guide` → User-facing documentation
- `guides.admin_guide` → Administrator guides
- `reference.api_doc` → API documentation
- `reference.specification` → Public specifications

### ⏳ Auto-Publish on Work Item Phase

| Document Type | Publishes When Work Item Reaches |
|---------------|----------------------------------|
| `architecture.adr` | **O1_OPERATIONS** |
| `architecture.technical_spec` | **O1_OPERATIONS** |
| `processes.migration_guide` | **O1_OPERATIONS** |
| `processes.deployment_guide` | **O1_OPERATIONS** |

### ❌ Never Auto-Publish (Manual Only)

- `communication.session_summary` (always private)
- `communication.status_report`
- `processes.implementation_plan`
- `architecture.design_doc`

---

## Review Requirements by Type

| Document Type | Review Required? | Min Reviewers | Max Time |
|---------------|------------------|---------------|----------|
| `user_guide` | ✅ Yes | 1 | 48 hours |
| `api_doc` | ✅ Yes | 1 | 24 hours |
| `adr` | ✅ Yes | **2** | 72 hours |
| `session_summary` | ❌ No | 0 | N/A |
| Default | ✅ Yes | 1 | 48 hours |

---

## Common Workflows

### Workflow 1: Quick Internal Document (No Review)

```bash
# Create session summary
apm document add \
  --work-item 164 \
  --category communication \
  --type session_summary \
  --title "Session Summary - 2025-10-25"

# Done! Stays in .agentpm/docs/, no review needed
```

### Workflow 2: User Guide (Auto-Publish)

```bash
# 1. Create guide
apm document add \
  --work-item 164 \
  --category guides \
  --type user_guide \
  --title "Getting Started"

# 2. Submit for review
apm document submit-review 123

# 3. Reviewer approves
apm document approve 123

# ✅ AUTO-PUBLISHED to docs/guides/user_guide/getting-started.md
```

### Workflow 3: ADR (Phase-Triggered Publish)

```bash
# 1. Create ADR
apm document add \
  --work-item 164 \
  --category architecture \
  --type adr \
  --title "Use PostgreSQL for Analytics"

# 2. Submit for review (requires 2 reviewers for ADRs)
apm document submit-review 124

# 3. First reviewer approves
apm document approve 124  # (as reviewer 1)

# 4. Second reviewer approves
apm document approve 124  # (as reviewer 2)

# ⏳ Document APPROVED but NOT published yet

# 5. Later, when work item reaches O1_OPERATIONS
apm work-item next 164

# ✅ AUTO-PUBLISHED when work item reaches O1_OPERATIONS phase
```

### Workflow 4: Review Rejection

```bash
# 1. Reviewer rejects
apm document reject 125 --reason "Examples are outdated"

# 🔄 Document auto-reverts to DRAFT

# 2. Author fixes issues
apm document update 125 --content "... updated ..."

# 3. Resubmit for review
apm document submit-review 125

# 4. Approve
apm document approve 125  # Auto-publishes if applicable
```

### Workflow 5: Emergency Unpublish

```bash
# Published document has critical error
apm document unpublish 126 --reason "Found security issue"

# Public copy removed from docs/
# Source preserved in .agentpm/docs/
# Document reverted to APPROVED state

# Fix the issue
apm document update 126 --content "... fixed ..."

# Republish
apm document publish 126
```

---

## CLI Commands Reference

### Review Commands

```bash
apm document submit-review <id> [--reviewer EMAIL] [--priority high|normal|low]
apm document approve <id> [--comment TEXT] [--publish-now]
apm document reject <id> --reason TEXT
```

### Publication Commands

```bash
apm document publish <id> [--force]
apm document unpublish <id> [--reason TEXT]
apm document sync [--dry-run] [--category CAT] [--type TYPE]
```

### Archive Commands

```bash
apm document archive <id> [--reason TEXT] [--remove-public]
apm document unarchive <id>
```

### Query Commands

```bash
apm document list [--lifecycle STATE] [--visibility VIS] [--review-status STATUS]
apm document show <id>
apm document audit <id> [--limit N] [--action ACTION]
```

### Visibility Commands

```bash
apm document set-visibility <id> --visibility private|public|internal [--force]
```

---

## File Locations

| Visibility | Draft/Review/Approved Location | Published Location |
|------------|-------------------------------|-------------------|
| **PRIVATE** | `.agentpm/docs/{category}/{type}/{filename}` | N/A (never published) |
| **PUBLIC** | `.agentpm/docs/{category}/{type}/{filename}` | `docs/{category}/{type}/{filename}` |
| **INTERNAL** | `.agentpm/docs/{category}/{type}/{filename}` | `docs/{category}/{type}/{filename}` (if context allows) |

**Source of Truth**: `.agentpm/docs/` (database-backed)
**Public Copy**: `docs/` (synced from source)

---

## Audit Trail

Every action is logged:

```bash
# View document history
apm document audit 123

# Output:
# 2025-10-25 14:30 | publish      | system              | approved → published
# 2025-10-25 14:25 | approve      | tech-lead@acme.com  | review → approved
# 2025-10-25 12:15 | submit_review| author@acme.com     | draft → review
# 2025-10-25 10:00 | create       | doc-writer-agent    | null → draft
```

Audit log includes:
- Action performed
- Actor (user or agent)
- State transition (from → to)
- Timestamp
- Details (paths, reasons, etc.)
- Comments

---

## Permissions

| Action | Who Can Perform |
|--------|----------------|
| Create document | Author, Agents |
| Submit for review | Author, Agents |
| Approve | Assigned reviewer, Work item owner |
| Reject | Assigned reviewer |
| Publish | Author (if approved), Admin, System (auto) |
| Unpublish | Author, Admin |
| Archive | Author, Admin |
| Unarchive | Admin only |

---

## Database Schema (Key Fields)

```sql
document_references:
  -- Lifecycle
  lifecycle_stage TEXT           -- 'draft', 'review', 'approved', 'published', 'archived', 'rejected'
  visibility TEXT                -- 'private', 'public', 'internal'

  -- Review
  review_status TEXT             -- 'pending', 'approved', 'rejected'
  reviewer_id TEXT
  reviewer_assigned_at TIMESTAMP
  review_completed_at TIMESTAMP
  review_comment TEXT

  -- Publication
  published_path TEXT
  published_date TIMESTAMP
  unpublished_date TIMESTAMP

  -- Auto-publish
  auto_publish BOOLEAN
  auto_publish_rule TEXT

document_audit_log:
  document_id INTEGER
  action TEXT
  actor TEXT
  timestamp TIMESTAMP
  from_state TEXT
  to_state TEXT
  details JSON
  comment TEXT
```

---

## Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `Document must be APPROVED to publish` | Cannot publish draft/review documents | Complete review process first |
| `Only PUBLIC documents can be published` | Private documents cannot go to docs/ | Change visibility or keep private |
| `Review required for this document type` | Cannot skip review | Submit for review |
| `Insufficient reviewer approvals` | ADRs need 2 reviewers | Get second approval |
| `Document not found` | Invalid document ID | Check ID with `apm document list` |

---

## Best Practices

1. **Always provide rejection reasons** - Helps authors understand issues
2. **Use auto-publish for user guides** - Reduces manual work
3. **Review ADRs with 2+ reviewers** - Architectural decisions need consensus
4. **Run sync periodically** - Catches drift: `apm document sync --dry-run`
5. **Check audit logs** - Understand document history: `apm document audit <id>`
6. **Set visibility early** - Determines publish behavior
7. **Link to work items** - Enables phase-based auto-publish

---

## Troubleshooting

### Document Won't Publish

1. Check lifecycle: `apm document show <id>`
   - Must be APPROVED or PUBLISHED
2. Check visibility: Must be PUBLIC or INTERNAL
3. Check permissions: User must have publish rights

### Auto-Publish Not Triggering

1. Check document type matches auto-publish rules
2. Verify visibility is PUBLIC
3. For phase-based: Check work item phase
4. Review audit log for errors: `apm document audit <id>`

### Sync Issues

1. Run sync with dry-run: `apm document sync --dry-run`
2. Check for missing files
3. Check for content mismatches
4. Manually republish: `apm document unpublish <id> && apm document publish <id>`

---

## See Also

- [Full Publishing Workflow Specification](./publishing-workflow-specification.md)
- [State Machine Diagram](./publishing-workflow-state-machine.mmd)
- [Auto-Publish Decision Tree](./auto-publish-decision-tree.mmd)
