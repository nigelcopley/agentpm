#!/bin/bash
# AgentPM Release Cleanup Script
# Removes development artifacts and prepares for clean release

set -e

echo "========================================="
echo "AgentPM Release Cleanup"
echo "========================================="
echo ""

cd /Users/nigelcopley/Projects/AgentPM

# 1. Remove Python cache and build artifacts
echo "1. Cleaning Python cache and build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
rm -rf build/ dist/ 2>/dev/null || true
echo "   ✓ Python artifacts cleaned"

# 2. Remove test and coverage artifacts
echo "2. Cleaning test and coverage artifacts..."
rm -rf .pytest_cache/ 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true
rm -rf .coverage coverage.xml 2>/dev/null || true
echo "   ✓ Test artifacts cleaned"

# 3. Remove linter and type checker cache
echo "3. Cleaning linter and type checker cache..."
rm -rf .mypy_cache/ 2>/dev/null || true
rm -rf .ruff_cache/ 2>/dev/null || true
echo "   ✓ Linter artifacts cleaned"

# 4. Remove temporary helper scripts
echo "4. Removing temporary helper scripts..."
rm -f rename_module.sh 2>/dev/null || true
rm -f update_imports.py 2>/dev/null || true
echo "   ✓ Helper scripts removed"

# 5. Clean testing directories
echo "5. Cleaning testing directories..."
if [ -d "testing" ]; then
    echo "   ⚠️  Found testing/ directory - consider removing or gitignoring"
fi
echo "   ✓ Testing directories checked"

# 6. Remove any .DS_Store files (macOS)
echo "6. Removing macOS artifacts..."
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "   ✓ macOS artifacts cleaned"

# 7. Clean analysis cache
echo "7. Cleaning analysis cache..."
if [ -d ".cache/analysis" ]; then
    rm -rf .cache/analysis/* 2>/dev/null || true
    echo "   ✓ Analysis cache cleaned"
fi

# 8. List what remains in root
echo ""
echo "8. Current root directory contents:"
ls -la | grep -v "^d" | tail -n +4 | awk '{print "   " $9}' || true

echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review git status: git status"
echo "2. Test installation: ./INSTALL_VERIFICATION.sh"
echo "3. Build package: python -m build"
