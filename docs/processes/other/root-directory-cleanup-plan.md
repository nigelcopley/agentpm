# Root Directory Cleanup Plan

**Date:** 2025-01-27  
**Status:** Implementation Plan  
**Context:** Clean up root directory by moving/removing files that don't belong there

---

## Files to Clean Up

### 1. Test Files (Move to tests/)
- `test_acyclic_depth.py` → `tests/unit/detection/test_acyclic_depth.py`
- `test_duplicate_nodes.py` → `tests/unit/detection/test_duplicate_nodes.py`
- `test_sbom_service.py` → `tests/unit/detection/test_sbom_service.py`

### 2. Investigation/Analysis Scripts (Move to scripts/analysis/)
- `investigate_depth.py` → `scripts/analysis/investigate_depth.py`

### 3. Utility Scripts (Move to scripts/)
- `update_imports.py` → `scripts/update_imports.py`

### 4. Release/Deployment Scripts (Move to scripts/release/)
- `CLEANUP_FOR_RELEASE.sh` → `scripts/release/cleanup_for_release.sh`
- `INSTALL_VERIFICATION.sh` → `scripts/release/install_verification.sh`
- `RELEASE_VERIFICATION.sh` → `scripts/release/release_verification.sh`

### 5. Repository Management Scripts (Move to scripts/repo/)
- `OPTION_A_NEW_REPO.sh` → `scripts/repo/option_a_new_repo.sh`
- `OPTION_B_RENAME_REPO.sh` → `scripts/repo/option_b_rename_repo.sh`
- `rename_module.sh` → `scripts/repo/rename_module.sh`

### 6. Web Development Files (Move to agentpm/web/)
- `tailwind-v4-test-standalone.html` → `agentpm/web/tailwind-v4-test-standalone.html`

### 7. Database Files (Keep in root - these are project databases)
- `aipm.db` - Keep (legacy database)
- `aipm_v2.db` - Keep (current database)

### 8. Configuration Files (Keep in root - these are project configs)
- `package.json` - Keep (Node.js project config)
- `package-lock.json` - Keep (Node.js lock file)
- `postcss.config.js` - Keep (PostCSS config)
- `tailwind.config.js` - Keep (Tailwind CSS config)
- `vite.config.js` - Keep (Vite build config)

---

## Directory Structure to Create

```
scripts/
├── analysis/
│   └── investigate_depth.py
├── release/
│   ├── cleanup_for_release.sh
│   ├── install_verification.sh
│   └── release_verification.sh
└── repo/
    ├── option_a_new_repo.sh
    ├── option_b_rename_repo.sh
    └── rename_module.sh

tests/unit/detection/
├── test_acyclic_depth.py
├── test_duplicate_nodes.py
└── test_sbom_service.py

agentpm/web/
└── tailwind-v4-test-standalone.html
```

---

## Files to Keep in Root

### Project Configuration Files
- `package.json` - Node.js project configuration
- `package-lock.json` - Node.js dependency lock file
- `postcss.config.js` - PostCSS configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `vite.config.js` - Vite build tool configuration
- `pyproject.toml` - Python project configuration
- `requirements-dev.txt` - Python development dependencies
- `MANIFEST.in` - Python package manifest
- `LICENSE` - Project license

### Project Databases
- `aipm.db` - Legacy database
- `aipm_v2.db` - Current database

### Project Documentation
- `README.md` - Project readme
- `CHANGELOG.md` - Project changelog
- `CLAUDE.md` - Claude-specific documentation (as requested)
- `GEMINI.md` - Gemini-specific documentation (as requested)

### Build Artifacts
- `agentpm.egg-info/` - Python package metadata
- `htmlcov/` - Test coverage reports
- `node_modules/` - Node.js dependencies

---

## Implementation Steps

1. Create necessary directories
2. Move files to appropriate locations
3. Update any references to moved files
4. Verify all moved files work in new locations
5. Commit changes

---

## Success Criteria

- Root directory contains only essential project files
- All scripts are properly organized in scripts/ directory
- All test files are in tests/ directory
- All web files are in agentpm/web/ directory
- No broken references to moved files
