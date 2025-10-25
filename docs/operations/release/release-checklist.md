# AgentPM 0.1.0 Release Checklist

**Status**: Ready for Release Testing
**Date**: 2025-10-25

---

## ✅ Completed Steps

- [x] Project moved to `/Users/nigelcopley/Projects/AgentPM`
- [x] Package rebranded from `aipm-v2` to `agentpm`
- [x] Python module renamed: `aipm_v2/` → `agentpm/`
- [x] All imports updated
- [x] All "APM (Agent Project Manager)" references updated to "APM (Agent Project Manager)"
- [x] `pyproject.toml` configured for PyPI
- [x] `MANIFEST.in` created
- [x] `LICENSE` file added (Apache 2.0)
- [x] `CHANGELOG.md` updated
- [x] `RELEASE.md` guide created
- [x] Installation verification script created

---

## 🚀 Immediate Next Steps

### 1. Test Local Installation (5 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Test installation
chmod +x INSTALL_VERIFICATION.sh
./INSTALL_VERIFICATION.sh

# If successful, you'll see:
# ✓ All verification checks passed!
```

### 2. Commit Changes (2 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Review changes
git status

# Add all changes
git add -A

# Commit with descriptive message
git commit -m "refactor: rebrand to AgentPM and prepare for v0.1.0 public release

- Rename package: aipm-v2 → agentpm
- Rename module: aipm_v2 → agentpm
- Move to ~/Projects/AgentPM
- Add PyPI packaging (MANIFEST.in, LICENSE)
- Add release documentation
- Update all references and imports
- Reset version to 0.1.0 for initial release

Breaking Changes:
- Package name changed (incompatible with aipm-v2 imports)
- Project location changed
- Repository URL updated

Migration: See MIGRATION_SUMMARY.md for details"

# Create version tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release of AgentPM"
```

### 3. Update GitHub Repository (5 minutes)

```bash
# Option A: Rename existing repository on GitHub
# 1. Go to: https://github.com/nigelcopley/agentpm/settings
# 2. Change repository name to: agentpm
# 3. Update local remote:
git remote set-url origin git@github.com:nigelcopley/agentpm.git

# Option B: Create new repository
# 1. Create new repo on GitHub: agentpm
# 2. Update remote:
git remote set-url origin git@github.com:nigelcopley/agentpm.git

# Push everything
git push origin main --tags
```

### 4. Build Package (3 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Install build tools (if not already installed)
pip install --upgrade build twine

# Build distribution packages
python -m build

# Verify build succeeded
ls -lh dist/
# You should see:
# - agentpm-0.1.0-py3-none-any.whl
# - agentpm-0.1.0.tar.gz

# Check package quality
twine check dist/*
# Should show: Checking dist/* ... PASSED
```

### 5. Test on TestPyPI (10 minutes) - RECOMMENDED

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*
# You'll need TestPyPI account and API token

# Create test environment
python -m venv /tmp/test-agentpm
source /tmp/test-agentpm/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps agentpm
pip install click rich pydantic pyyaml questionary jinja2 networkx  # Install deps separately

# Test it works
apm --version
apm --help

# Test functionality
mkdir /tmp/test-project
cd /tmp/test-project
apm init "Test Project" .
apm work-item create "Test Feature" --type feature
apm status

# Cleanup
deactivate
rm -rf /tmp/test-agentpm /tmp/test-project
```

### 6. Release to PyPI (5 minutes)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Final check
twine check dist/*

# Upload to production PyPI
twine upload dist/*
# You'll need PyPI account and API token

# Verify on PyPI
open https://pypi.org/project/agentpm/

# Test installation
pip install agentpm
apm --version
```

### 7. Create GitHub Release (3 minutes)

```bash
# Using GitHub CLI (if installed)
gh release create v0.1.0 \
  --title "AgentPM v0.1.0 - Initial Public Release" \
  --notes "$(cat CHANGELOG.md | sed -n '/## \[0.1.0\]/,/## \[/p' | head -n -1)" \
  dist/agentpm-0.1.0.tar.gz \
  dist/agentpm-0.1.0-py3-none-any.whl

# Or manually:
# 1. Go to: https://github.com/nigelcopley/agentpm/releases/new
# 2. Tag: v0.1.0
# 3. Title: "AgentPM v0.1.0 - Initial Public Release"
# 4. Description: Copy from CHANGELOG.md [0.1.0] section
# 5. Attach: dist/*.whl and dist/*.tar.gz
# 6. Publish release
```

---

## 📋 Pre-Release Verification

Before releasing, verify these work:

```bash
# Core functionality
apm --version
apm --help
apm init "Test" /tmp/test
apm work-item create "Test" --type feature
apm status

# Tests pass
pytest

# Linting passes
ruff check agentpm/
black --check agentpm/

# Type checking passes
mypy agentpm/

# Build succeeds
python -m build
```

---

## 🔑 Required Setup

### PyPI API Tokens

You'll need API tokens for:
1. **TestPyPI** (for testing): https://test.pypi.org/manage/account/token/
2. **PyPI** (for production): https://pypi.org/manage/account/token/

Store in `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

Permissions: `chmod 600 ~/.pypirc`

### GitHub Account
- Ensure you have push access to repository
- Consider creating GitHub Personal Access Token for `gh` CLI

---

## 🎯 Success Criteria

Release is successful when:
- [x] Package builds without errors
- [ ] Installation verification script passes
- [ ] Tests pass (pytest)
- [ ] TestPyPI installation works
- [ ] PyPI installation works
- [ ] GitHub release created with assets
- [ ] Documentation accessible
- [ ] CLI command `apm` works globally

---

## 🐛 Troubleshooting

### Build fails
```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info
python -m build
```

### Import errors after installation
```bash
# Check installed package
pip show agentpm
pip list | grep agentpm

# Reinstall
pip uninstall agentpm
pip install agentpm
```

### PyPI upload fails
```bash
# Check credentials in ~/.pypirc
# Verify package name not taken: https://pypi.org/project/agentpm/
# Try TestPyPI first
```

---

## 📞 Help & Resources

- **Release Guide**: See `RELEASE.md` for detailed procedures
- **Migration Details**: See `MIGRATION_SUMMARY.md`
- **PyPI Publishing Guide**: https://packaging.python.org/tutorials/packaging-projects/
- **Twine Documentation**: https://twine.readthedocs.io/

---

## ⏱️ Estimated Timeline

- **Testing (steps 1-5)**: ~25 minutes
- **PyPI Release (step 6)**: ~5 minutes
- **GitHub Release (step 7)**: ~3 minutes
- **Total**: ~35 minutes

---

**Ready to start?** Run step 1: `./INSTALL_VERIFICATION.sh`

**Last Updated**: 2025-10-25
