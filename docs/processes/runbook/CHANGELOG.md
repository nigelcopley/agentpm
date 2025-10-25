# Changelog

All notable changes to APM (Agent Project Manager) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-18

### Fixed

#### Database Schema
- Fixed critical migration schema mismatch where `agents.metadata` column was missing
- Migration 0027 now correctly adds metadata column with idempotency check
- Resolves errors appearing on every CLI command execution (#108)

#### CLI Commands
- Fixed agent generation import error in `apm init` command
- Removed deprecated template-based generation code
- Updated user guidance to reflect database-first architecture (#109)
- Init command now provides clear instructions for agent generation workflow

### Migration Notes
- **IMPORTANT**: Migration 0027 will automatically apply on upgrade
- Existing agent data will be preserved
- No manual intervention required
- Rollback available via downgrade if needed

### Testing
- Added 76 comprehensive tests (26 migration + 34 init + 16 integration)
- Test coverage: 100% for new code
- All tests passing

### Documentation
- Created database migrations guide (`docs/database/migrations-guide.md`)
- Updated init command documentation
- Added agent generation workflow guide
- Updated README with correct initialization sequence

## [0.1.0] - 2025-10-17

### Initial Release
- Database-driven project management system
- 50-agent architecture with phase-based orchestration
- Six-phase workflow (D1→P1→I1→R1→O1→E1)
- Quality gate system with rule validation
- Context-aware work item and task management
- Plugin system for extensibility
- Comprehensive CLI interface
