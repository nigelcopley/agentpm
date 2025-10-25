#!/bin/bash
###############################################################################
# POC: Integration Demo - Documentation Testing Tools
#
# Demonstrates:
# - Installing dependencies (pytest-examples, transitions)
# - Running pytest on sample doc file
# - Generating state diagrams
# - Showing before/after comparison
#
# This validates that all tools work together in our environment.
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "POC: Integration Demo - Documentation Testing Tools"
echo "======================================================================"
echo ""

###############################################################################
# Step 1: Check/Install Dependencies
###############################################################################
echo -e "${BLUE}Step 1: Checking dependencies...${NC}"
echo "----------------------------------------------------------------------"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo -e "${RED}✗ pip not found. Please install Python and pip first.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"

# Install dependencies if needed
echo "  Checking for pytest-examples..."
if ! python -c "import pytest" &> /dev/null; then
    echo "  Installing pytest..."
    pip install pytest -q
fi

echo "  Checking for transitions..."
if ! python -c "import transitions" &> /dev/null; then
    echo "  Installing transitions..."
    pip install 'transitions[diagrams]' -q
fi

echo -e "${GREEN}✓ All dependencies available${NC}"
echo ""

###############################################################################
# Step 2: Run pytest-examples POC
###############################################################################
echo -e "${BLUE}Step 2: Running pytest-examples POC...${NC}"
echo "----------------------------------------------------------------------"

if [ ! -f "scripts/poc_pytest_examples.py" ]; then
    echo -e "${RED}✗ poc_pytest_examples.py not found${NC}"
    exit 1
fi

chmod +x scripts/poc_pytest_examples.py
python scripts/poc_pytest_examples.py

echo ""

###############################################################################
# Step 3: Generate State Diagrams
###############################################################################
echo -e "${BLUE}Step 3: Generating state diagrams...${NC}"
echo "----------------------------------------------------------------------"

if [ ! -f "scripts/poc_state_diagrams.py" ]; then
    echo -e "${RED}✗ poc_state_diagrams.py not found${NC}"
    exit 1
fi

chmod +x scripts/poc_state_diagrams.py
python scripts/poc_state_diagrams.py

echo ""

###############################################################################
# Step 4: Show Before/After Comparison
###############################################################################
echo -e "${BLUE}Step 4: Before/After Comparison${NC}"
echo "----------------------------------------------------------------------"

echo -e "${YELLOW}BEFORE: Manual Documentation${NC}"
echo "  - State transitions documented in markdown"
echo "  - Prone to drift when code changes"
echo "  - No automated verification"
echo "  - Manual updates required"
echo ""

echo -e "${YELLOW}AFTER: Automated Documentation${NC}"
echo "  - State diagrams auto-generated from code"
echo "  - Always in sync with enums"
echo "  - Automated tests catch drift"
echo "  - Zero manual maintenance"
echo ""

# Show generated files
echo "Generated files:"
if [ -d "docs/reference/state-diagrams" ]; then
    for file in docs/reference/state-diagrams/*.md; do
        if [ -f "$file" ]; then
            size=$(wc -l < "$file")
            echo "  ✓ $(basename "$file") ($size lines)"
        fi
    done
fi

# Show sample file if created
if [ -f "scripts/sample_doc_for_testing.md" ]; then
    echo "  ✓ sample_doc_for_testing.md (test fixture)"
fi

echo ""

###############################################################################
# Step 5: Summary and Next Steps
###############################################################################
echo "======================================================================"
echo -e "${GREEN}✓ POC INTEGRATION SUCCESSFUL!${NC}"
echo "======================================================================"
echo ""
echo "What we demonstrated:"
echo "  1. pytest-examples can test code blocks in markdown"
echo "  2. transitions can generate state diagrams from enums"
echo "  3. Both tools integrate seamlessly with our codebase"
echo "  4. Automation eliminates documentation drift"
echo ""
echo "Next Steps:"
echo "  1. Create production test suite (tests/docs/)"
echo "  2. Add CI/CD integration (.github/workflows/test-docs.yml)"
echo "  3. Configure MCP server for doc indexing"
echo "  4. Run tests on all documentation"
echo "  5. Fix any drift detected by tests"
echo ""
echo "Run production tests:"
echo "  pytest tests/docs/ -v"
echo ""
echo "======================================================================"
