# Changelog

All notable changes to APM (Agent Project Manager) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-25

### Changed
- **BREAKING**: Rebranded from "AIPM V2" to "AgentPM" (Agent Project Manager)
  - Package renamed: `aipm-v2` → `agentpm`
  - Python module: `aipm_v2` → `agentpm`
  - CLI command remains: `apm` (backward compatible)
  - All references updated from "AIPM V2" to "APM (Agent Project Manager)"
- **Project location**: Moved from `~/.project_manager/aipm-v2` to `~/Projects/AgentPM`
- **Repository**: Updated to `github.com/nigelcopley/agentpm`

### Added
- Initial public release preparation
- PyPI packaging configuration
- `MANIFEST.in` for distribution
- `LICENSE` file (Apache 2.0)
- `RELEASE.md` with complete release procedures
- `INSTALL_VERIFICATION.sh` for testing installations

### Fixed
- Document path validation enforcement (#113)
  - Consolidated DocumentReference models with strict path validation
  - Added database CHECK constraint for docs/ prefix enforcement
  - Migrated 49 non-compliant documents to proper structure (87.5% success)
  - Enhanced CLI with path guidance and auto-suggestions
  - Updated 45 agent SOPs with path structure examples
  - Created comprehensive test suite with >90% coverage target
  - Improved compliance from 16.4% to 89.6% (73 point improvement)

