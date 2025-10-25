# WI-25 – Migration Framework Upgrade Notes

## Current State
- `agentpm/core/database/migrations/manager.py` and `registry.py` already provide discovery, execution, and tracking utilities.
- Migration loader lives in `agentpm/core/database/migrations/loader.py` but lacks validation of file signatures, descriptions, and post-run checks.
- Existing migrations (e.g., `migration_0018.py`, `migration_0020.py`) are large and self-contained but there is no CLI workflow for running or rolling back beyond Python API usage.
- Documentation references: `MIGRATION-0018-REFACTOR-SUMMARY.md` and `docs/components/database/adrs/005-migration-framework.md` describe desired professional migration standards (versioned scripts, rollback support, change tracking).

## Gaps Identified
1. No dedicated CLI entry point for listing/applying/rolling back migrations.
2. Lack of checksum/signature validation when loading migration modules.
3. No automated post-migration validation (schema diff, enum drift check).
4. Minimal documentation on migration workflow for contributors.

## Proposed Actions
- Design governance rules for migration authoring (naming, descriptions, validation steps).
- Implement CLI commands (`apm migrate list/run/rollback`) that wrap `MigrationManager`.
- Add validation utilities to ensure migrations expose `upgrade()`/`downgrade()` and optionally `validate_post()` hooks.
- Introduce automated tests covering migration discovery, execution, and rollback.
- Produce updated contributor documentation covering the migration workflow.

## References
- `agentpm/core/database/migrations/manager.py`
- `agentpm/core/database/migrations/registry.py`
- `agentpm/core/database/migrations/loader.py`
- `MIGRATION-0018-REFACTOR-SUMMARY.md`
- `docs/components/database/adrs/005-migration-framework.md`

