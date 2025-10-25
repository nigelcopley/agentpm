# APM (Agent Project Manager) Scripts Directory

This directory contains utility scripts for APM (Agent Project Manager) development, validation, and maintenance.

## Directory Structure

```
scripts/
├── validation/          # Quality validation and compliance checking scripts
├── generation/          # Code and artifact generation scripts
├── setup/              # Installation and configuration scripts
├── analysis/           # Analysis and reporting tools
├── debug/              # Debugging utilities
├── migration/          # Database and system migration tools
└── *.py               # Root-level Python utilities
```

## Validation Scripts (`validation/`)

Scripts for ensuring code quality, compliance, and system health:

- **validate_task.sh** - Validates task documents against workflow rules (referenced in CLAUDE.md)
- **validate_compliance_gates.sh** - Checks CI-001 through CI-006 gate compliance
- **validate_architecture_health.sh** - Validates architectural patterns and principles
- **validate_security_compliance.sh** - Security validation and vulnerability checks
- **validate_cli_performance.sh** - CLI performance testing and benchmarking
- **validate_context_compliance.sh** - Context structure validation
- **validate_pipeline.sh** - Pipeline health and integrity checks
- **validate_service_duplication.sh** - Detects service duplication and redundancy
- **validate_feature.sh** - Feature validation against workflow rules
- **overlap_detection.sh** - Detects overlapping work items and tasks

## Generation Scripts (`generation/`)

Scripts for generating code, tasks, and artifacts:

- **generate_feature_tasks.sh** - Generates tasks from feature specifications
- **migrate_existing_features.sh** - Migrates legacy features to new format
- **migrate_features_to_workflow.sh** - Migrates features to workflow-compliant structure

## Setup Scripts (`setup/`)

Scripts for system configuration and installation:

- **install_validation_hooks.sh** - Installs git hooks for validation

## Python Utilities

Root-level Python scripts for various development tasks:

- **populate_active_contexts.py** - Populates active context data
- **populate_agents_from_files.py** - Loads agent definitions into database
- **generate_all_agents.py** - Generates complete agent system
- **generate_rules_catalog.py** - Creates rules catalog
- **consolidation_analysis.py** - Analyzes code consolidation opportunities
- **service_functionality_tester.py** - Tests service layer functionality
- And more...

## Usage

### Validation
```bash
# Validate a task document
./scripts/validation/validate_task.sh docs/artifacts/tasks/todo/my-task.md

# Check compliance gates
./scripts/validation/validate_compliance_gates.sh

# Validate architecture
./scripts/validation/validate_architecture_health.sh
```

### Generation
```bash
# Generate tasks from a feature
./scripts/generation/generate_feature_tasks.sh path/to/feature.md
```

### Setup
```bash
# Install validation hooks
./scripts/setup/install_validation_hooks.sh
```

## Integration

These scripts are integrated into:
- **AIPM workflow** - Referenced in CLAUDE.md and task validation
- **Git hooks** - Pre-commit and pre-push validation
- **CI/CD pipeline** - Automated quality checks
- **Development workflow** - Manual quality validation

## Porting History

These scripts were ported from `/tools/` directory on 2025-10-18 to consolidate all APM (Agent Project Manager) utilities in a single location.

**Original location**: `/Users/nigelcopley/.project_manager/tools/`
**New location**: `/Users/nigelcopley/.project_manager/aipm-v2/scripts/`

## Maintenance

When adding new scripts:
1. Place them in the appropriate subdirectory
2. Make them executable: `chmod +x script.sh`
3. Update this README
4. Add validation to relevant workflow rules
5. Document integration points

---

**Last Updated**: 2025-10-18
**Maintainer**: AIPM Development Team
