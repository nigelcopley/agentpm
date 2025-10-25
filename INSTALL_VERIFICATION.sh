#!/bin/bash
# Installation verification script for AgentPM

set -e

echo "========================================="
echo "AgentPM Installation Verification"
echo "========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version)
echo "   ✓ $python_version"
echo ""

# Test package installation
echo "2. Installing AgentPM in editable mode..."
pip install -e . > /dev/null 2>&1
echo "   ✓ Package installed"
echo ""

# Verify CLI command
echo "3. Verifying 'apm' command..."
if command -v apm &> /dev/null; then
    version=$(apm --version 2>&1 || echo "unknown")
    echo "   ✓ apm command found: $version"
else
    echo "   ✗ apm command not found!"
    exit 1
fi
echo ""

# Test basic commands
echo "4. Testing core commands..."

# Create temporary test directory
test_dir=$(mktemp -d)
cd "$test_dir"

echo "   Testing: apm init"
apm init "Test Project" . > /dev/null 2>&1
if [ -d ".aipm" ]; then
    echo "   ✓ apm init works (.aipm directory created)"
else
    echo "   ✗ apm init failed"
    exit 1
fi

echo "   Testing: apm work-item create"
apm work-item create "Test Feature" --type feature > /dev/null 2>&1
echo "   ✓ apm work-item create works"

echo "   Testing: apm status"
apm status > /dev/null 2>&1
echo "   ✓ apm status works"

# Cleanup
cd - > /dev/null
rm -rf "$test_dir"
echo ""

# Check package structure
echo "5. Verifying package structure..."
required_modules=(
    "agentpm.cli"
    "agentpm.core.database"
    "agentpm.core.workflow"
    "agentpm.core.context"
    "agentpm.services"
)

for module in "${required_modules[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        echo "   ✓ $module"
    else
        echo "   ✗ $module (import failed)"
        exit 1
    fi
done
echo ""

echo "========================================="
echo "✓ All verification checks passed!"
echo "========================================="
echo ""
echo "AgentPM is ready for use."
echo "Try: apm --help"
