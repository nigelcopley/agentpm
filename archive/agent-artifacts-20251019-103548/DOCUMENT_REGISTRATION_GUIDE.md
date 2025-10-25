# Document Registration Scripts

## Overview

This directory contains scripts for batch-registering valuable untracked documents into the APM (Agent Project Manager) database. These scripts are part of the documentation cleanup process and ensure proper document tracking.

## Prerequisites

1. **Pattern-Applier Completion**: These scripts depend on `/tmp/files_to_register.txt` being created by the pattern-applier agent
2. **APM (Agent Project Manager) CLI**: Must have `apm` command available in PATH
3. **Database Access**: Must have access to `.aipm/data/aipm.db`

## Available Scripts

### 1. `register_documents.sh` (Recommended)

**Simple, fast shell-based registration script.**

```bash
./register_documents.sh
```

**Features:**
- Reads file paths from `/tmp/files_to_register.txt`
- Auto-detects document type from path patterns
- Generates human-readable titles
- Uses `apm document add` CLI command
- Provides detailed progress and summary

**Document Type Detection:**
- `adr/`, `decision/` → `adr`
- `architecture/` → `architecture`
- `design/` → `design`
- `requirements/` → `requirements`
- `user-guide/` → `user_guide`
- `api-doc/`, `api/` → `api_doc`
- `specification/` → `specification`
- And more...

### 2. `register_documents.py`

**Python-based registration script with enhanced error handling.**

```bash
python3 register_documents.py
```

**Features:**
- Same functionality as shell version
- Better error reporting
- More maintainable for future enhancements
- Structured output

### 3. `wait_and_register.sh`

**Automated monitoring script that waits for pattern-applier.**

```bash
./wait_and_register.sh
```

**Features:**
- Monitors for `/tmp/files_to_register.txt` creation
- Automatically runs registration when ready
- 5-minute timeout with progress updates
- Useful for automated workflows

## Workflow

### Manual Workflow

1. **Wait for pattern-applier**:
   ```bash
   # Pattern-applier creates /tmp/files_to_register.txt
   ```

2. **Run registration**:
   ```bash
   ./register_documents.sh
   ```

3. **Verify results**:
   ```bash
   apm document list --entity-type=project --entity-id=1
   ```

### Automated Workflow

1. **Start monitoring**:
   ```bash
   ./wait_and_register.sh
   ```

2. **Script waits for input file and auto-registers**

## Document Registration Details

### Entity Configuration

All documents are registered as **project-level** documents:
- **Entity Type**: `project`
- **Entity ID**: `1` (default project)
- **Created By**: `system_cleanup`

### Path Structure

Documents should follow APM (Agent Project Manager) standard structure:
```
docs/{category}/{document_type}/{filename}
```

**Categories:**
- `architecture` - System design, technical architecture
- `planning` - Requirements, user stories, plans
- `guides` - User guides, tutorials, how-tos
- `reference` - API docs, specifications
- `processes` - Test plans, workflows
- `governance` - Quality gates, standards
- `operations` - Runbooks, deployment
- `communication` - Reports, analyses

### Document Types

The script maps paths to these document types:
- `requirements` - Requirements documents
- `architecture` - Architecture documents
- `design` - Design specifications
- `adr` - Architecture Decision Records
- `user_guide` - User guides
- `api_doc` - API documentation
- `specification` - Technical specifications
- `test_plan` - Test plans
- `runbook` - Operations runbooks
- `migration_guide` - Migration guides
- `other` - Other document types

## Output Format

### During Registration

```
📄 Found 45 files to register

✅ Registered: docs/architecture/design/system-overview.md (type: design)
✅ Registered: docs/guides/user_guide/getting-started.md (type: user_guide)
❌ Failed: docs/invalid/path.md
...
```

### Summary

```
==========================================
📊 Registration Summary
==========================================
✅ Successfully registered: 43
❌ Failed: 2
📝 Total: 45

⚠️  Some documents failed to register. Check errors above.
```

## Troubleshooting

### Input file not found

```
❌ Input file not found: /tmp/files_to_register.txt
   Waiting for pattern-applier to create the file...
```

**Solution**: Wait for pattern-applier to complete, or check if it's running.

### Registration failures

Common causes:
1. **Invalid entity ID**: Ensure project ID 1 exists
2. **Database locked**: Another process may be using the database
3. **Invalid document type**: Check DocumentType enum for valid values
4. **Path validation**: Ensure paths follow docs/ structure

### Verify database

```bash
# Check if documents were registered
sqlite3 .aipm/data/aipm.db "SELECT COUNT(*) FROM document_references WHERE created_by='system_cleanup';"

# List registered documents
apm document list --entity-type=project --entity-id=1
```

## Integration with APM (Agent Project Manager)

These scripts use the official `apm document add` CLI command, ensuring:
- ✅ Proper validation
- ✅ Database integrity
- ✅ Metadata tracking
- ✅ Security checks (path validation, hash calculation)
- ✅ Audit trail

## Next Steps

After successful registration:

1. **Verify in database**:
   ```bash
   apm document list --entity-type=project --entity-id=1
   ```

2. **Check document details**:
   ```bash
   apm document show <id>
   ```

3. **Update metadata if needed**:
   ```bash
   apm document update <id> --description="Updated description"
   ```

## File Locations

- **Scripts**: `/Users/nigelcopley/.project_manager/aipm-v2/`
  - `register_documents.sh` - Shell script
  - `register_documents.py` - Python script
  - `wait_and_register.sh` - Auto-monitoring script
- **Input**: `/tmp/files_to_register.txt` (created by pattern-applier)
- **Database**: `.aipm/data/aipm.db`

## Performance

**Expected performance:**
- ~1-2 documents per second
- 100 documents: ~1-2 minutes
- 500 documents: ~5-10 minutes

The shell script (`register_documents.sh`) is generally faster due to lower overhead.

## Cleanup

After successful registration, you may optionally remove temporary files:

```bash
rm /tmp/files_to_register.txt
```

The scripts themselves should be kept for future use or reference.
