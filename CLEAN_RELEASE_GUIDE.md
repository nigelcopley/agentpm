# Clean Release Guide - AgentPM 0.1.0

**Goal**: Get a pristine, production-ready installation for PyPI release

---

## 🚀 Quick Start (5 Minutes)

Run these three commands in order:

```bash
cd /Users/nigelcopley/Projects/AgentPM

# 1. Clean everything
chmod +x CLEANUP_FOR_RELEASE.sh && ./CLEANUP_FOR_RELEASE.sh

# 2. Verify ready for release
chmod +x RELEASE_VERIFICATION.sh && ./RELEASE_VERIFICATION.sh

# 3. Test installation works
chmod +x INSTALL_VERIFICATION.sh && ./INSTALL_VERIFICATION.sh
```

**Expected Result**: All three scripts show ✓ SUCCESS

---

## 📋 What Gets Cleaned

### Removed by Cleanup Script:
- ✓ `__pycache__/` directories (Python bytecode cache)
- ✓ `*.pyc`, `*.pyo` files (compiled Python)
- ✓ `.pytest_cache/`, `htmlcov/`, `.coverage` (test artifacts)
- ✓ `.mypy_cache/`, `.ruff_cache/` (type checker cache)
- ✓ `build/`, `dist/`, `*.egg-info` (build artifacts)
- ✓ `rename_module.sh`, `update_imports.py` (temporary helper scripts)
- ✓ `.DS_Store` files (macOS cruft)

### Protected (Not Removed):
- ✓ Source code: `agentpm/`
- ✓ Tests: `tests/`
- ✓ Documentation: `docs/`, `README.md`, etc.
- ✓ Configuration: `pyproject.toml`, `.gitignore`
- ✓ Git history: `.git/`
- ✓ Virtual environment: `.venv/` (gitignored)

---

## 🔍 Verification Checks

The verification script checks:

1. **Critical Files Present**
   - pyproject.toml, LICENSE, README.md, CHANGELOG.md
   - MANIFEST.in, agentpm/__init__.py, agentpm/cli/main.py

2. **Package Configuration**
   - Package name is 'agentpm' (not 'aipm-v2')
   - Version is '0.1.0'
   - CLI entry point: `apm = "agentpm.cli:main"`

3. **No Old References**
   - Scans for any remaining 'aipm_v2' imports
   - Verifies all code uses 'agentpm'

4. **Directory Structure**
   - agentpm/, tests/, docs/, _RULES/ present
   - Proper module organization

5. **No Build Artifacts**
   - dist/, build/, *.egg-info should not exist
   - Clean working directory

6. **Python Imports Work**
   - Can import agentpm
   - Can import agentpm.cli
   - Can import agentpm.core.database

7. **Git Status**
   - No uncommitted changes (or known pending changes)
   - Reviews untracked files

---

## 📦 What Gets Released to PyPI

### Included in Distribution (via MANIFEST.in):

**Source Code:**
```
agentpm/
├── __init__.py
├── cli/              # Command-line interface
├── core/             # Core functionality
├── services/         # Service layer
├── providers/        # Provider integrations
├── web/              # Flask web interface
├── utils/            # Utilities
└── templates/        # Jinja2 templates
```

**Configuration & Rules:**
```
.claude/agents/       # Agent definitions (50+ SOPs)
_RULES/               # Governance rules
```

**Documentation:**
```
README.md
CHANGELOG.md
LICENSE
DEVELOPMENT.md
```

### Excluded from Distribution:

```
tests/                # Test suite (development only)
testing/              # Test fixtures (development only)
.venv/                # Virtual environment
.aipm/                # Project database
htmlcov/              # Coverage reports
.pytest_cache/        # Test cache
.mypy_cache/          # Type checker cache
.git/                 # Git repository
*.pyc, __pycache__/   # Python cache
```

---

## ✅ Pre-Release Checklist

Before committing and releasing:

- [ ] Cleanup script ran successfully
- [ ] Verification script shows "ALL CHECKS PASSED"
- [ ] Installation test shows "All verification checks passed"
- [ ] No 'aipm_v2' references in agentpm/ code
- [ ] Version in pyproject.toml is '0.1.0'
- [ ] CHANGELOG.md has [0.1.0] release notes
- [ ] LICENSE file exists
- [ ] README.md has correct branding

---

## 🧪 Testing Your Clean Installation

### Test 1: Build Package
```bash
cd /Users/nigelcopley/Projects/AgentPM

# Install build tools
pip install --upgrade build twine

# Build distribution
python -m build

# Should create:
# - dist/agentpm-0.1.0-py3-none-any.whl
# - dist/agentpm-0.1.0.tar.gz

# Verify package
twine check dist/*
# Should show: "Checking dist/* ... PASSED"
```

### Test 2: Install from Wheel
```bash
# Create clean test environment
python3 -m venv /tmp/test-clean-install
source /tmp/test-clean-install/bin/activate

# Install from built wheel
pip install /Users/nigelcopley/Projects/AgentPM/dist/agentpm-0.1.0-py3-none-any.whl

# Test it works
apm --version
# Should show: apm, version 0.1.0

apm --help
# Should show command list

# Create test project
mkdir /tmp/test-proj
cd /tmp/test-proj
apm init "Test" .
# Should create .aipm/ directory

apm work-item create "Test Feature" --type feature
# Should create work item

apm status
# Should show project dashboard

# Cleanup
deactivate
rm -rf /tmp/test-clean-install /tmp/test-proj
```

### Test 3: Inspect Package Contents
```bash
cd /Users/nigelcopley/Projects/AgentPM

# List what's in the tarball
tar tzf dist/agentpm-0.1.0.tar.gz | head -50

# Verify it includes:
# ✓ agentpm/ source code
# ✓ README.md, LICENSE, CHANGELOG.md
# ✓ pyproject.toml

# Verify it EXCLUDES:
# ✗ tests/
# ✗ .venv/
# ✗ __pycache__/
# ✗ *.pyc files
```

---

## 🎯 Success Criteria

**Ready for PyPI release when:**

1. ✅ All three scripts (cleanup, verification, installation) pass
2. ✅ `python -m build` succeeds without errors
3. ✅ `twine check dist/*` passes
4. ✅ Test installation in clean venv works
5. ✅ `apm` command functions correctly
6. ✅ No old 'aipm_v2' references in code
7. ✅ Git status is clean (or intentionally staged)

---

## 📝 Next Steps After Clean Verification

Once verification passes:

```bash
# 1. Review what will be committed
git status
git diff

# 2. Commit release preparation
git add -A
git commit -m "refactor: prepare AgentPM v0.1.0 for public release"

# 3. Tag the release
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# 4. Push to GitHub
git remote set-url origin git@github.com:nigelcopley/agentpm.git
git push origin main --tags

# 5. Upload to PyPI (see RELEASE.md for details)
twine upload dist/*
```

---

## 🆘 Troubleshooting

### "Verification script fails"
```bash
# Re-run cleanup
./CLEANUP_FOR_RELEASE.sh

# Check specific errors in output
./RELEASE_VERIFICATION.sh

# Fix reported issues, then re-verify
```

### "Found old 'aipm_v2' references"
```bash
# Find them
grep -r "aipm_v2" agentpm/

# These should be in comments/docstrings only
# Update if they're in active code
```

### "Build fails"
```bash
# Clean everything
rm -rf build/ dist/ *.egg-info

# Reinstall build tools
pip install --upgrade build setuptools wheel

# Try again
python -m build
```

### "Installation test fails"
```bash
# Ensure package is installed in editable mode
pip install -e /Users/nigelcopley/Projects/AgentPM

# Then re-run
./INSTALL_VERIFICATION.sh
```

---

## 📚 Additional Documentation

- **RELEASE_CHECKLIST.md** - Complete step-by-step release process
- **PRE_RELEASE_CHECKLIST.md** - Detailed pre-release verification steps
- **RELEASE.md** - Comprehensive release procedures
- **MIGRATION_SUMMARY.md** - Details of the migration from aipm-v2

---

## ⏱️ Time Estimate

- **Cleanup**: 2 minutes
- **Verification**: 2 minutes
- **Testing**: 5 minutes
- **Review**: 5 minutes
- **Total**: ~15 minutes

---

**Ready to start?**

```bash
cd /Users/nigelcopley/Projects/AgentPM
./CLEANUP_FOR_RELEASE.sh
```

---

**Last Updated**: 2025-10-25
**Version**: 0.1.0
**Status**: Ready for Clean Installation Verification
