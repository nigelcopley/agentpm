#!/bin/bash
# AgentPM Release Verification Script
# Comprehensive checks before release

set -e

echo "========================================="
echo "AgentPM Release Verification"
echo "========================================="
echo ""

cd /Users/nigelcopley/Projects/AgentPM

# Track failures
FAILURES=0

# 1. Check critical files exist
echo "1. Checking critical files..."
CRITICAL_FILES=(
    "pyproject.toml"
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "MANIFEST.in"
    "agentpm/__init__.py"
    "agentpm/cli/main.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file MISSING!"
        FAILURES=$((FAILURES + 1))
    fi
done
echo ""

# 2. Verify package name in pyproject.toml
echo "2. Verifying package configuration..."
if grep -q 'name = "agentpm"' pyproject.toml; then
    echo "   ✓ Package name is 'agentpm'"
else
    echo "   ✗ Package name incorrect!"
    FAILURES=$((FAILURES + 1))
fi

if grep -q 'version = "0.1.0"' pyproject.toml; then
    echo "   ✓ Version is '0.1.0'"
else
    echo "   ✗ Version incorrect!"
    FAILURES=$((FAILURES + 1))
fi

if grep -q 'apm = "agentpm.cli:main"' pyproject.toml; then
    echo "   ✓ CLI entry point correct"
else
    echo "   ✗ CLI entry point incorrect!"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 3. Check for old references
echo "3. Checking for old 'aipm_v2' references in code..."
OLD_REFS=$(find agentpm -type f -name "*.py" -exec grep -l "aipm_v2" {} \; 2>/dev/null | wc -l)
if [ "$OLD_REFS" -eq 0 ]; then
    echo "   ✓ No old 'aipm_v2' references found"
else
    echo "   ⚠️  Found $OLD_REFS files with 'aipm_v2' references"
    find agentpm -type f -name "*.py" -exec grep -l "aipm_v2" {} \; | head -5 | sed 's/^/      /'
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 4. Check directory structure
echo "4. Verifying directory structure..."
REQUIRED_DIRS=(
    "agentpm"
    "agentpm/cli"
    "agentpm/core"
    "agentpm/services"
    "tests"
    "docs"
    "_RULES"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/"
    else
        echo "   ✗ $dir/ MISSING!"
        FAILURES=$((FAILURES + 1))
    fi
done
echo ""

# 5. Verify no build artifacts
echo "5. Checking for build artifacts (should be clean)..."
ARTIFACTS=(
    "dist/"
    "build/"
    "*.egg-info"
)

FOUND_ARTIFACTS=0
for artifact in "${ARTIFACTS[@]}"; do
    if ls $artifact 2>/dev/null | grep -q .; then
        echo "   ⚠️  Found: $artifact"
        FOUND_ARTIFACTS=$((FOUND_ARTIFACTS + 1))
    fi
done

if [ $FOUND_ARTIFACTS -eq 0 ]; then
    echo "   ✓ No build artifacts (clean)"
else
    echo "   ℹ️  Run './CLEANUP_FOR_RELEASE.sh' to clean"
fi
echo ""

# 6. Test imports
echo "6. Testing Python imports..."
if python3 -c "import agentpm" 2>/dev/null; then
    echo "   ✓ import agentpm"
else
    echo "   ✗ Cannot import agentpm (run: pip install -e .)"
    FAILURES=$((FAILURES + 1))
fi

if python3 -c "import agentpm.cli" 2>/dev/null; then
    echo "   ✓ import agentpm.cli"
else
    echo "   ✗ Cannot import agentpm.cli"
    FAILURES=$((FAILURES + 1))
fi

if python3 -c "import agentpm.core.database" 2>/dev/null; then
    echo "   ✓ import agentpm.core.database"
else
    echo "   ✗ Cannot import agentpm.core.database"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# 7. Check git status
echo "7. Checking git status..."
if git diff --quiet; then
    echo "   ✓ No uncommitted changes in tracked files"
else
    echo "   ⚠️  Uncommitted changes in tracked files"
fi

UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
if [ "$UNTRACKED" -eq 0 ]; then
    echo "   ✓ No untracked files"
else
    echo "   ℹ️  $UNTRACKED untracked files (review with: git status)"
fi
echo ""

# 8. Verify dependencies
echo "8. Checking dependencies..."
DEPS=("click" "rich" "pydantic" "pyyaml" "questionary" "jinja2" "networkx")
MISSING_DEPS=0

for dep in "${DEPS[@]}"; do
    if python3 -c "import ${dep//-/_}" 2>/dev/null; then
        echo "   ✓ $dep"
    else
        echo "   ⚠️  $dep not installed (optional for build)"
        MISSING_DEPS=$((MISSING_DEPS + 1))
    fi
done
echo ""

# Summary
echo "========================================="
if [ $FAILURES -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED!"
    echo "========================================="
    echo ""
    echo "Ready for release! Next steps:"
    echo "1. Build: python -m build"
    echo "2. Check: twine check dist/*"
    echo "3. Test: Upload to TestPyPI"
    echo "4. Release: Upload to PyPI"
    exit 0
else
    echo "✗ FAILED: $FAILURES critical issues found"
    echo "========================================="
    echo ""
    echo "Please fix the issues above before releasing."
    exit 1
fi
