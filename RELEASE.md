# AgentPM Release Guide

## Pre-Release Checklist

### 1. Version Management
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Commit version changes: `git commit -m "chore: bump version to X.Y.Z"`
- [ ] Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`

### 2. Quality Verification
```bash
# Run tests
pytest

# Run linting
ruff check agentpm/
black --check agentpm/

# Type checking
mypy agentpm/

# Build package
python -m build

# Verify package contents
tar tzf dist/agentpm-X.Y.Z.tar.gz | head -50
```

### 3. Test Installation
```bash
# Create clean virtual environment
python -m venv /tmp/test-agentpm
source /tmp/test-agentpm/bin/activate

# Install from local build
pip install dist/agentpm-X.Y.Z-py3-none-any.whl

# Verify CLI works
apm --version
apm --help

# Test basic commands
mkdir /tmp/test-project
cd /tmp/test-project
apm init "Test Project" .

# Cleanup
deactivate
rm -rf /tmp/test-agentpm /tmp/test-project
```

## PyPI Release

### First Time Setup
```bash
# Install build tools
pip install --upgrade build twine

# Configure PyPI credentials (one time)
# Create ~/.pypirc with:
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

### Release to TestPyPI (Staging)
```bash
# Build distribution
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps agentpm

# Verify it works
apm --version
```

### Release to PyPI (Production)
```bash
# Build clean distribution
rm -rf dist/ build/ *.egg-info
python -m build

# Check distribution
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/agentpm/

# Test installation from PyPI
pip install agentpm

# Verify
apm --version
```

### Post-Release
```bash
# Push to GitHub
git push origin main --tags

# Create GitHub release
gh release create vX.Y.Z \
  --title "AgentPM vX.Y.Z" \
  --notes "$(cat CHANGELOG.md | sed -n '/## \[X.Y.Z\]/,/## \[/p' | head -n -1)" \
  dist/agentpm-X.Y.Z.tar.gz \
  dist/agentpm-X.Y.Z-py3-none-any.whl
```

## Version Numbering

Follow Semantic Versioning (semver.org):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Current: `0.1.0` (Initial public release)

## Distribution Files

After `python -m build`, you should have:
```
dist/
├── agentpm-X.Y.Z-py3-none-any.whl  (wheel, preferred)
└── agentpm-X.Y.Z.tar.gz            (source distribution)
```

## Testing Checklist

Before releasing, verify:
- [ ] `apm init` creates project with database
- [ ] `apm work-item create` creates work items
- [ ] `apm task create` creates tasks
- [ ] `apm agents generate` generates agent files
- [ ] `apm status` displays dashboard
- [ ] Database migrations work
- [ ] Web interface starts: `apm web start`
- [ ] All core workflows function

## Rollback Procedure

If issues are discovered post-release:
```bash
# Remove from PyPI (contact PyPI support)
# Can't delete, but can yank:
# Visit: https://pypi.org/manage/project/agentpm/releases/

# Or release hotfix
# Bump patch version: 0.1.0 → 0.1.1
# Follow release process
```

## Support Channels

- GitHub Issues: https://github.com/nigelcopley/agentpm/issues
- Documentation: https://agentpm.dev
- Email: support@agentpm.dev (if configured)

---

**Last Updated**: 2025-10-25
**Maintainer**: Nigel Copley
