# Pre-Release Checklist - AgentPM 0.1.0

**Goal**: Ensure a clean, professional installation ready for PyPI release

---

## Step 1: Clean Development Artifacts (2 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Run cleanup script
chmod +x CLEANUP_FOR_RELEASE.sh
./CLEANUP_FOR_RELEASE.sh
```

**What this removes:**
- ✓ `__pycache__/` directories
- ✓ `*.pyc`, `*.pyo` files
- ✓ `.pytest_cache/`, `htmlcov/`, `.coverage`
- ✓ `.mypy_cache/`, `.ruff_cache/`
- ✓ `build/`, `dist/`, `*.egg-info`
- ✓ Temporary helper scripts (rename_module.sh, update_imports.py)
- ✓ `.DS_Store` files

---

## Step 2: Verify Release Readiness (2 minutes)

```bash
# Run verification script
chmod +x RELEASE_VERIFICATION.sh
./RELEASE_VERIFICATION.sh
```

**What this checks:**
- ✓ Critical files present (pyproject.toml, LICENSE, README.md, etc.)
- ✓ Package name is 'agentpm' (not 'aipm-v2')
- ✓ Version is '0.1.0'
- ✓ No old 'aipm_v2' references in code
- ✓ Directory structure correct
- ✓ No build artifacts
- ✓ Python imports work
- ✓ Git status clean

**Expected result:** "✓ ALL CHECKS PASSED!"

---

## Step 3: Review Files to be Released (5 minutes)

### Files that WILL be in the PyPI package:
```bash
# Check what will be included
cat MANIFEST.in
```

**Included:**
- ✓ Source code: `agentpm/`
- ✓ Templates: `agentpm/templates/`
- ✓ Migrations: `agentpm/core/database/migrations/`
- ✓ Agent definitions: `.claude/agents/`
- ✓ Rules: `_RULES/`
- ✓ Documentation: `README.md`, `CHANGELOG.md`, `LICENSE`, `DEVELOPMENT.md`

**Excluded (automatically by MANIFEST.in):**
- ✗ Tests: `tests/`, `testing/`
- ✗ Development files: `.gitignore`, `.agentpmignore`, etc.
- ✗ Cache: `htmlcov/`, `.pytest_cache/`, etc.
- ✗ Virtual environments: `.venv/`
- ✗ Project data: `.agentpm/`

---

## Step 4: Review Git Status (3 minutes)

```bash
# Check what needs to be committed
git status

# Review changes
git diff

# Check untracked files
git ls-files --others --exclude-standard
```

**What to commit:**
- ✓ All rebranding changes (agentpm references)
- ✓ New release files (LICENSE, MANIFEST.in, etc.)
- ✓ Updated documentation (README.md, CHANGELOG.md)
- ✓ pyproject.toml changes

**What NOT to commit:**
- ✗ Build artifacts (dist/, build/)
- ✗ Cache files
- ✗ Temporary scripts (if still present)
- ✗ IDE files (.idea/, .vscode/ if not already gitignored)

---

## Step 5: Final File Review (5 minutes)

### Critical Files Checklist

**Configuration:**
- [ ] `pyproject.toml` - Package name: "agentpm", Version: "0.1.0"
- [ ] `MANIFEST.in` - Distribution manifest present
- [ ] `.gitignore` - Comprehensive exclusions

**Documentation:**
- [ ] `README.md` - Updated with AgentPM branding
- [ ] `CHANGELOG.md` - 0.1.0 release notes present
- [ ] `LICENSE` - Apache 2.0 present
- [ ] `DEVELOPMENT.md` - Developer guide present

**Release Guides:**
- [ ] `RELEASE.md` - Release procedures
- [ ] `RELEASE_CHECKLIST.md` - Step-by-step guide
- [ ] `MIGRATION_SUMMARY.md` - Migration documentation
- [ ] `INSTALL_VERIFICATION.sh` - Installation test script

**Source Code:**
- [ ] `agentpm/` directory present (not `aipm_v2/`)
- [ ] `agentpm/__init__.py` exists
- [ ] `agentpm/cli/main.py` exists
- [ ] All imports use `agentpm` (not `aipm_v2`)

---

## Step 6: Test Clean Installation (10 minutes)

```bash
# Create isolated test environment
python3 -m venv /tmp/agentpm-test
source /tmp/agentpm-test/bin/activate

# Install from local directory
cd /Users/nigelcopley/Projects/AgentPM
pip install -e .

# Run installation verification
./INSTALL_VERIFICATION.sh

# Test basic functionality
apm --version
apm --help

# Create test project
mkdir /tmp/test-project
cd /tmp/test-project
apm init "Test Project" .
apm work-item create "Test Feature" --type feature
apm status

# Cleanup
deactivate
rm -rf /tmp/agentpm-test /tmp/test-project
```

**Expected results:**
- ✓ Installation succeeds without errors
- ✓ `apm` command available
- ✓ `apm --version` shows correct version
- ✓ `apm init` creates project structure
- ✓ Database operations work

---

## Step 7: Build Package Test (5 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Install build tools (if not installed)
pip install --upgrade build twine

# Build distribution
python -m build

# Verify build outputs
ls -lh dist/
# Should show:
# - agentpm-0.1.0-py3-none-any.whl
# - agentpm-0.1.0.tar.gz

# Check package quality
twine check dist/*
# Should show: "PASSED"

# Inspect package contents
tar tzf dist/agentpm-0.1.0.tar.gz | head -30
```

**Expected results:**
- ✓ Build succeeds without errors
- ✓ Two files created (.whl and .tar.gz)
- ✓ `twine check` passes
- ✓ Package contains correct files (no test/, no .venv/, etc.)

---

## Step 8: Commit Release Preparation (5 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "refactor: prepare AgentPM v0.1.0 for public release

- Rebrand from aipm-v2 to agentpm
- Update all imports and references
- Add PyPI packaging (MANIFEST.in, LICENSE)
- Add release documentation and scripts
- Clean build artifacts
- Verify package structure

Breaking Changes:
- Package name: aipm-v2 → agentpm
- Module name: aipm_v2 → agentpm
- Repository location changed

See MIGRATION_SUMMARY.md for complete details"

# Create release tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Verify tag
git tag -l
git show v0.1.0
```

---

## Step 9: Final Pre-Release Checks

**Before pushing to GitHub and PyPI, verify:**

- [ ] All tests pass: `pytest`
- [ ] Linting passes: `ruff check agentpm/`
- [ ] Formatting correct: `black --check agentpm/`
- [ ] Type checking passes: `mypy agentpm/` (optional)
- [ ] Clean git status: `git status` shows no uncommitted changes
- [ ] Build succeeds: `python -m build`
- [ ] Package check passes: `twine check dist/*`
- [ ] Installation test passes: `./INSTALL_VERIFICATION.sh`
- [ ] All release documentation present

---

## Step 10: Push to GitHub

```bash
# Update remote URL (if needed)
git remote set-url origin git@github.com:nigelcopley/agentpm.git

# Push code and tags
git push origin main --tags

# Verify on GitHub
# Visit: https://github.com/nigelcopley/agentpm
```

---

## Success Criteria

✅ **Ready for PyPI Release when:**
1. All verification checks pass
2. Clean installation works in isolated environment
3. Package builds without errors
4. No old 'aipm_v2' references in code
5. Git repository clean and tagged
6. Documentation complete and accurate

---

## Quick Command Summary

```bash
# Complete cleanup and verification
./CLEANUP_FOR_RELEASE.sh
./RELEASE_VERIFICATION.sh

# Build and check
python -m build
twine check dist/*

# Test installation
./INSTALL_VERIFICATION.sh

# Commit and tag
git add -A
git commit -m "refactor: prepare AgentPM v0.1.0 for public release"
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Push
git push origin main --tags
```

---

**Estimated Total Time**: ~40 minutes
**Last Updated**: 2025-10-25
