# Document Migration Runbook

Operational guide for migrating document paths to comply with the Universal Documentation System structure.

---

## Table of Contents

1. [When to Migrate](#when-to-migrate)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Dry-Run Analysis](#dry-run-analysis)
4. [Execution Steps](#execution-steps)
5. [Verification Procedures](#verification-procedures)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

---

## When to Migrate

### Migration Scenarios

Run document path migration when:

1. **Initial Enforcement** - Adding path validation to existing project
2. **Compliance Audit** - Regular compliance checks show violations
3. **Reorganization** - Restructuring documentation hierarchy
4. **Post-Import** - After importing documents from external sources
5. **Quality Gates** - Path compliance becomes a quality requirement

### Pre-Migration Assessment

Before migrating, assess the current state:

```bash
# Check total documents
apm document list | wc -l

# Check compliance rate (rough estimate)
find docs -type f -name "*.md" | wc -l

# View sample non-compliant paths
apm document list | grep -v "^docs/"
```

**Decision Criteria**:
- **< 10% non-compliant**: Migrate immediately
- **10-30% non-compliant**: Schedule migration, review categories
- **> 30% non-compliant**: Review category mapping first, then migrate

---

## Pre-Migration Checklist

### 1. Database Backup

**CRITICAL**: Always backup the database before migration.

```bash
# Backup database
cp .aipm/aipm.db .aipm/aipm.db.backup-$(date +%Y%m%d-%H%M%S)

# Verify backup
ls -lh .aipm/aipm.db.backup-*

# Test backup integrity
sqlite3 .aipm/aipm.db.backup-* "SELECT COUNT(*) FROM document_references;"
```

### 2. Dry-Run Analysis

**MANDATORY**: Run dry-run to preview all changes.

```bash
apm document migrate-to-structure --dry-run > migration-plan.txt

# Review plan
cat migration-plan.txt

# Count migrations
grep "FROM:" migration-plan.txt | wc -l
```

### 3. Category Mapping Review

Verify category mappings are correct:

```bash
# Show category mapping
python3 << 'EOF'
from agentpm.cli.commands.document.add import CATEGORY_MAPPING
import json
print(json.dumps(CATEGORY_MAPPING, indent=2))
EOF
```

Check if any document types lack mappings:

```python
from agentpm.core.database.enums import DocumentType
from agentpm.cli.commands.document.add import CATEGORY_MAPPING

for doc_type in DocumentType:
    if doc_type.value not in CATEGORY_MAPPING:
        print(f"⚠️  Missing mapping: {doc_type.value}")
```

### 4. Filesystem Verification

Ensure all document files exist:

```bash
# Find missing files
for doc in $(apm document list --format=json | jq -r '.[].file_path'); do
    if [ ! -f "$doc" ]; then
        echo "Missing: $doc"
    fi
done
```

### 5. Work Item Context

Check which work items will be affected:

```bash
# Work items with non-compliant documents
apm document list --format=json | \
  jq -r '.[] | select(.file_path | startswith("docs/") | not) | .entity_id' | \
  sort -u
```

---

## Dry-Run Analysis

### Running Dry-Run

```bash
# Run dry-run with full output
apm document migrate-to-structure --dry-run

# Save output for review
apm document migrate-to-structure --dry-run > migration-plan-$(date +%Y%m%d).txt
```

### Interpreting Output

**Sample Output**:

```
========================================
DRY RUN - No changes will be made
========================================

📊 Migration Analysis:
  Total documents: 62
  Non-compliant: 50 (80.6%)
  Compliant: 12 (19.4%)

🔍 Sample migrations (first 10):

1. WI-112 Implementation Strategy
   FROM: WI-112-IMPLEMENTATION-STRATEGY.md
   TO:   docs/planning/implementation_plan/WI-112-IMPLEMENTATION-STRATEGY.md
   AUTO: ✅ (default category: planning)

2. Database Schema Design
   FROM: schema/database-design.md
   TO:   docs/architecture/design/database-design.md
   AUTO: ✅ (inferred from 'design' type)

[... more migrations ...]

📈 Category Distribution:
  planning: 18 documents (36%)
  architecture: 15 documents (30%)
  guides: 8 documents (16%)
  operations: 5 documents (10%)
  communication: 4 documents (8%)

⚠️  Manual Review Recommended:
  - 3 documents with ambiguous types
  - 2 documents with custom paths
```

### Key Metrics to Review

1. **Total documents**: Sanity check count
2. **Compliance rate**: Current vs. post-migration
3. **Category distribution**: Verify balanced distribution
4. **Auto-detected mappings**: Check for accuracy
5. **Manual review items**: Identify special cases

### Identifying Issues

**Red flags to investigate**:

```bash
# Documents mapping to 'communication' (default fallback)
grep "default category: communication" migration-plan.txt

# Very long paths (potential nesting issues)
awk '{if (length($0) > 100) print}' migration-plan.txt

# Documents with unusual filenames
grep -E "[^a-zA-Z0-9_.-]" migration-plan.txt
```

---

## Execution Steps

### Step 1: Final Backup

```bash
# Create timestamped backup
BACKUP_FILE=".aipm/aipm.db.backup-migration-$(date +%Y%m%d-%H%M%S)"
cp .aipm/aipm.db "$BACKUP_FILE"

# Verify backup
sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM document_references;"

# Store backup location
echo "$BACKUP_FILE" > .aipm/last-migration-backup.txt
```

### Step 2: Execute Migration

```bash
# Execute migration
apm document migrate-to-structure

# Save execution log
apm document migrate-to-structure 2>&1 | tee migration-execution-$(date +%Y%m%d).log
```

**Expected Output**:

```
🔄 Document Path Migration

Analyzing documents...
  Total: 62
  Non-compliant: 50
  
Migrating paths...
  ✅ Migrated: WI-112-IMPLEMENTATION-STRATEGY.md
  ✅ Migrated: schema/database-design.md
  ✅ Migrated: guides/setup.md
  [... progress ...]
  ⚠️  Skipped: custom-file.md (manual review needed)
  
Migration Complete:
  ✅ Successfully migrated: 45 documents
  ⚠️  Skipped (manual review): 5 documents
  ❌ Failed (errors): 0 documents
  
📊 Compliance Improvement:
  Before: 19.4% compliant (12/62 documents)
  After:  89.6% compliant (55/62 documents)
  Improvement: +70.2 percentage points
```

### Step 3: Review Migration Log

```bash
# Check for errors
grep "❌" migration-execution-*.log

# Check skipped files
grep "⚠️  Skipped" migration-execution-*.log

# View summary
tail -20 migration-execution-*.log
```

### Step 4: Handle Skipped Documents

For documents that were skipped:

```bash
# List skipped documents
apm document list --format=json | \
  jq -r '.[] | select(.file_path | startswith("docs/") | not) | 
         "\(.id): \(.file_path) (type: \(.document_type // "unknown"))"'

# Manually fix each
apm document update <doc-id> --file-path="docs/correct/path/here.md"
```

---

## Verification Procedures

### Immediate Verification

**1. Database Consistency**:

```bash
# Check all documents in database
apm document list | wc -l

# Verify no data loss
sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM document_references;"

# Compare with backup
BACKUP=$(cat .aipm/last-migration-backup.txt)
echo "Before migration:"
sqlite3 "$BACKUP" "SELECT COUNT(*) FROM document_references;"
echo "After migration:"
sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM document_references;"
```

**2. Path Compliance**:

```bash
# Check compliance rate
python3 << 'EOF'
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.cli.utils.services import get_database_service

db = get_database_service('.')
docs = doc_methods.list_all_document_references(db)

compliant = sum(1 for d in docs if d.file_path.startswith('docs/'))
total = len(docs)

print(f"Compliance: {compliant}/{total} ({100*compliant/total:.1f}%)")
EOF
```

**3. File Existence**:

```bash
# Verify all paths exist (or were marked as non-validated)
apm document list --format=json | \
  jq -r '.[].file_path' | \
  while read path; do
    if [ ! -f "$path" ]; then
      echo "Missing: $path"
    fi
  done
```

### Detailed Verification

**1. Category Distribution**:

```bash
# Check category balance
python3 << 'EOF'
from collections import Counter
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.cli.utils.services import get_database_service

db = get_database_service('.')
docs = doc_methods.list_all_document_references(db)

categories = [d.file_path.split('/')[1] for d in docs if d.file_path.startswith('docs/')]
counts = Counter(categories)

for category, count in counts.most_common():
    print(f"{category}: {count} documents")
EOF
```

**2. Work Item Links**:

```bash
# Verify work item links intact
for wi_id in $(seq 1 150); do
  docs=$(apm document list --entity-type=work_item --entity-id=$wi_id 2>/dev/null | wc -l)
  if [ $docs -gt 0 ]; then
    echo "WI-$wi_id: $docs documents"
  fi
done
```

**3. Metadata Integrity**:

```bash
# Check for null/missing metadata
sqlite3 .aipm/aipm.db << 'SQL'
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN title IS NULL THEN 1 ELSE 0 END) as missing_title,
  SUM(CASE WHEN document_type IS NULL THEN 1 ELSE 0 END) as missing_type,
  SUM(CASE WHEN content_hash IS NULL THEN 1 ELSE 0 END) as missing_hash
FROM document_references;
SQL
```

### Smoke Tests

**Test Document Operations**:

```bash
# Test add
apm document add \
  --entity-type=work_item \
  --entity-id=113 \
  --file-path="docs/operations/runbook/test-document.md" \
  --type=runbook \
  --title="Test Document" \
  --no-validate-file

# Test list
apm document list --entity-type=work_item --entity-id=113

# Test show
DOC_ID=$(apm document list --entity-type=work_item --entity-id=113 --format=json | jq -r '.[0].id')
apm document show $DOC_ID

# Test update
apm document update $DOC_ID --title="Updated Test Document"

# Test delete
apm document delete $DOC_ID
```

---

## Rollback Procedures

### When to Rollback

Rollback if:
- Data loss detected (document count mismatch)
- Critical paths broken (>10% invalid paths)
- Application errors (database constraints violated)
- Work item links broken (entity relationships lost)

### Rollback Steps

**Option 1: Database Restore** (Recommended)

```bash
# Stop any running AIPM processes
pkill -f "apm"

# Get backup file
BACKUP=$(cat .aipm/last-migration-backup.txt)

# Verify backup integrity
sqlite3 "$BACKUP" "PRAGMA integrity_check;"

# Restore backup
cp "$BACKUP" .aipm/aipm.db

# Verify restoration
sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM document_references;"

# Remove migration flag
rm .aipm/last-migration-backup.txt

# Restart services
apm status
```

**Option 2: Manual Reversal** (If backup lost)

```bash
# Extract old paths from migration log
grep "FROM:" migration-execution-*.log | \
  awk '{print $2}' > old-paths.txt

# Restore each document path (requires manual effort)
# This is why backups are CRITICAL
```

### Post-Rollback Verification

```bash
# Verify rollback success
echo "Document count:"
sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM document_references;"

# Check compliance rate (should match pre-migration)
python3 << 'EOF'
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.cli.utils.services import get_database_service

db = get_database_service('.')
docs = doc_methods.list_all_document_references(db)

compliant = sum(1 for d in docs if d.file_path.startswith('docs/'))
total = len(docs)

print(f"Compliance: {compliant}/{total} ({100*compliant/total:.1f}%)")
EOF
```

---

## Troubleshooting

### Issue: Migration Fails Immediately

**Symptoms**: Migration aborts with database error

**Diagnosis**:
```bash
# Check database integrity
sqlite3 .aipm/aipm.db "PRAGMA integrity_check;"

# Check for locks
lsof | grep aipm.db
```

**Solution**:
```bash
# Kill locking processes
pkill -f "apm"

# Retry migration
apm document migrate-to-structure
```

### Issue: Some Documents Not Migrated

**Symptoms**: Migration completes but compliance < 100%

**Diagnosis**:
```bash
# Find non-migrated documents
apm document list --format=json | \
  jq -r '.[] | select(.file_path | startswith("docs/") | not) | 
         "\(.id): \(.file_path) (type: \(.document_type // "unknown"))"'
```

**Solution**:
```bash
# Review each document
for doc_id in $(apm document list --format=json | jq -r '.[] | select(.file_path | startswith("docs/") | not) | .id'); do
  echo "Reviewing document $doc_id:"
  apm document show $doc_id
  
  # Manually update
  read -p "Enter correct path: " new_path
  apm document update $doc_id --file-path="$new_path"
done
```

### Issue: Category Mismatches

**Symptoms**: Documents in wrong categories

**Diagnosis**:
```bash
# Check category distribution
python3 << 'EOF'
from collections import Counter
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.cli.utils.services import get_database_service

db = get_database_service('.')
docs = doc_methods.list_all_document_references(db)

# Group by type and inferred category
type_category = [(d.document_type, d.file_path.split('/')[1] if d.file_path.startswith('docs/') else 'none') 
                 for d in docs if d.document_type]

for (dtype, cat), count in Counter(type_category).most_common():
    print(f"{dtype} → {cat}: {count}")
EOF
```

**Solution**:
```bash
# Update CATEGORY_MAPPING if needed
# Edit: agentpm/cli/commands/document/add.py

# Re-run migration
apm document migrate-to-structure
```

### Issue: Duplicate Paths

**Symptoms**: Multiple documents with same path

**Diagnosis**:
```bash
# Find duplicates
sqlite3 .aipm/aipm.db << 'SQL'
SELECT file_path, COUNT(*) as count
FROM document_references
GROUP BY file_path
HAVING count > 1;
SQL
```

**Solution**:
```bash
# Review duplicates
for path in $(sqlite3 .aipm/aipm.db "SELECT file_path FROM document_references GROUP BY file_path HAVING COUNT(*) > 1;"); do
  echo "Duplicate path: $path"
  sqlite3 .aipm/aipm.db "SELECT id, entity_type, entity_id, title FROM document_references WHERE file_path='$path';"
  
  # Decide which to keep/merge
done
```

### Issue: Migration Takes Too Long

**Symptoms**: Migration appears hung

**Diagnosis**:
```bash
# Check database size
ls -lh .aipm/aipm.db

# Monitor progress (in another terminal)
watch -n 5 'sqlite3 .aipm/aipm.db "SELECT COUNT(*) FROM document_references WHERE file_path LIKE \"docs/%\""'
```

**Solution**:
```bash
# Cancel migration (Ctrl+C)
# Run in batches instead
python3 << 'EOF'
from agentpm.core.database.methods import document_references as doc_methods
from agentpm.cli.utils.services import get_database_service

db = get_database_service('.')
docs = doc_methods.list_all_document_references(db)

# Process in batches of 100
batch_size = 100
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    # Process batch...
    print(f"Processed {i+len(batch)}/{len(docs)}")
EOF
```

---

## Post-Migration Tasks

### 1. Update Documentation

```bash
# Update README with new structure
# Update team wiki/confluence
# Notify team of new path requirements
```

### 2. Configure Quality Gates

```bash
# Enable path validation in CI/CD
# Add pre-commit hooks for path validation
# Update agent SOPs with path requirements
```

### 3. Clean Up Old Paths

```bash
# After verification period, clean up old paths
# Archive migration logs
# Document lessons learned
```

### 4. Monitor Compliance

```bash
# Weekly compliance check
apm document list --format=json | \
  jq -r '.[] | select(.file_path | startswith("docs/") | not) | "\(.id): \(.file_path)"'

# Set up automated compliance reporting
```

---

## Best Practices

### Before Migration

1. **Always backup database** (cannot be stressed enough)
2. **Run dry-run multiple times** (until familiar with changes)
3. **Review category mapping** (ensure accuracy)
4. **Communicate with team** (schedule downtime if needed)
5. **Test in staging** (if available)

### During Migration

1. **Monitor progress** (watch for errors)
2. **Don't interrupt** (let migration complete)
3. **Save logs** (for troubleshooting)
4. **Be patient** (large datasets take time)

### After Migration

1. **Verify immediately** (check counts, paths, metadata)
2. **Test operations** (add, list, show, update, delete)
3. **Review skipped** (handle manually)
4. **Update documentation** (reflect new structure)
5. **Monitor for issues** (first few days critical)

---

## Emergency Contacts

If migration issues occur:

1. **Database corruption**: Restore from backup immediately
2. **Data loss**: Contact database admin, restore from backup
3. **Application errors**: Check logs, report issues on GitHub
4. **Performance issues**: Review query plans, add indexes

---

## Appendix: SQL Queries

### Useful Diagnostic Queries

**Non-compliant paths**:
```sql
SELECT id, file_path, document_type
FROM document_references
WHERE file_path NOT LIKE 'docs/%'
  AND file_path NOT LIKE 'README%'
  AND file_path NOT LIKE 'CHANGELOG%'
  AND file_path NOT LIKE 'LICENSE%'
  AND file_path NOT LIKE 'CONTRIBUTING%'
  AND file_path NOT LIKE '.claude/agents/%'
  AND file_path NOT LIKE '_RULES/%';
```

**Category distribution**:
```sql
SELECT 
  SUBSTR(file_path, 6, INSTR(SUBSTR(file_path, 6), '/') - 1) as category,
  COUNT(*) as count
FROM document_references
WHERE file_path LIKE 'docs/%'
GROUP BY category
ORDER BY count DESC;
```

**Document type distribution**:
```sql
SELECT 
  document_type,
  COUNT(*) as count
FROM document_references
WHERE document_type IS NOT NULL
GROUP BY document_type
ORDER BY count DESC;
```

**Recent migrations** (if tracking metadata):
```sql
SELECT id, file_path, updated_at
FROM document_references
WHERE updated_at > datetime('now', '-1 hour')
ORDER BY updated_at DESC;
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-19
**Related**: WI-113 (Document Path Validation Enforcement)
