# Untracked Documents Archive

**Date**: 2025-10-19 10:26:41
**Reason**: Document system cleanup - files existed but were not registered in document_references table

## Contents

This archive contains markdown files that existed in the filesystem but were not tracked in the document registry database. These files were using invalid category paths (docs/components/, docs/migrations/, docs/artifacts/) which are not part of the approved documentation structure.

## Categories Archived

- **docs/components/**: Agent documentation and document system design docs
- **docs/migrations/**: Schema migration analysis documents  
- **docs/artifacts/**: Test optimization analysis

## Valid Categories

The approved documentation structure uses:
- docs/architecture/
- docs/guides/
- docs/reference/
- docs/decisions/
- docs/aipm/

## Retention

Review these files to determine if any should be:
1. Re-registered in the database under valid categories
2. Merged into existing documentation
3. Permanently archived/deleted

These files can be safely deleted after 30 days if not needed.
