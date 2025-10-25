#!/bin/bash
# Validate code compliance with AGENT-CONTEXT.md patterns
# Usage: ./tools/validate_context_compliance.sh [file_or_directory]

set -e

TARGET="${1:-.}"
ERRORS=0

echo "🔍 Validating context compliance for: $TARGET"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Variable naming (SCREAMING_SNAKE_CASE)
echo "📋 Checking variable naming convention..."
if find "$TARGET" -name "*.py" -type f -exec grep -Hn "^[a-z][a-z_]* = " {} \; 2>/dev/null | grep -v "def \|class \|import \|from "; then
  echo -e "${RED}❌ FAIL:${NC} Found snake_case variables (should be SCREAMING_SNAKE_CASE)"
  echo "   Pattern: USER_NAME not user_name"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} All variables use SCREAMING_SNAKE_CASE"
fi
echo ""

# Check 2: Function naming (verbObjectFn pattern)
echo "📋 Checking function naming convention..."
WRONG_FUNCTIONS=$(find "$TARGET" -name "*.py" -type f -exec grep -Hn "^def [a-z_]*(" {} \; 2>/dev/null | grep -v "Fn(" || true)
if [ -n "$WRONG_FUNCTIONS" ]; then
  echo -e "${RED}❌ FAIL:${NC} Found incorrect function names (should end with Fn)"
  echo "$WRONG_FUNCTIONS" | head -5
  echo "   Pattern: calculateTotalFn not calculate_total"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} All functions use verbObjectFn pattern"
fi
echo ""

# Check 3: Docstring placement (below function)
echo "📋 Checking docstring placement..."
WRONG_DOCSTRINGS=$(find "$TARGET" -name "*.py" -type f -exec grep -Pzo "def [^\n]+\n\s+\"\"\"" {} \; 2>/dev/null || true)
if [ -n "$WRONG_DOCSTRINGS" ]; then
  echo -e "${YELLOW}⚠️  WARNING:${NC} Found docstrings ABOVE function body (should be BELOW)"
  echo "   Place docstrings after return statement, not after def line"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} Docstrings are placed below functions"
fi
echo ""

# Check 4: Line length (60 characters max)
echo "📋 Checking line length (max 60 chars)..."
LONG_LINES=$(find "$TARGET" -name "*.py" -type f -exec awk 'length > 60 {print FILENAME":"NR":"$0}' {} \; 2>/dev/null | head -5 || true)
if [ -n "$LONG_LINES" ]; then
  echo -e "${RED}❌ FAIL:${NC} Found lines exceeding 60 characters"
  echo "$LONG_LINES"
  echo "   Break long lines into multiple lines"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} All lines are ≤60 characters"
fi
echo ""

# Check 5: Test directory (test_suite/ not tests-BAK/)
echo "📋 Checking test directory naming..."
if [ -d "$TARGET/tests" ] || [ -d "./tests" ]; then
  echo -e "${RED}❌ FAIL:${NC} Found tests/ directory (should be test_suite/)"
  echo "   Rename: tests/ → test_suite/"
  ((ERRORS++))
elif [ -d "$TARGET/test_suite" ] || [ -d "./test_suite" ]; then
  echo -e "${GREEN}✅ PASS:${NC} Using correct test_suite/ directory"
else
  echo -e "${YELLOW}⚠️  INFO:${NC} No test directory found"
fi
echo ""

# Check 6: Test function prefix (validate_ not test_)
echo "📋 Checking test function naming..."
WRONG_TEST_PREFIX=$(find "$TARGET" -path "*/test_suite/*.py" -type f -exec grep -Hn "^def test_" {} \; 2>/dev/null || find "./test_suite" -name "*.py" -type f -exec grep -Hn "^def test_" {} \; 2>/dev/null || true)
if [ -n "$WRONG_TEST_PREFIX" ]; then
  echo -e "${RED}❌ FAIL:${NC} Found test_ prefix (should be validate_)"
  echo "$WRONG_TEST_PREFIX" | head -3
  echo "   Pattern: validate_calculateTotal not test_calculate_total"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} Test functions use validate_ prefix"
fi
echo ""

# Check 7: Test file naming (camelCase)
echo "📋 Checking test file naming..."
WRONG_TEST_FILES=$(find "$TARGET" -path "*/test_suite/test_*.py" -type f -exec basename {} \; 2>/dev/null | grep -E "test_[a-z_]+\.py" || find "./test_suite" -name "test_*.py" -type f -exec basename {} \; 2>/dev/null | grep -E "test_[a-z_]+\.py" || true)
if [ -n "$WRONG_TEST_FILES" ]; then
  echo -e "${RED}❌ FAIL:${NC} Found snake_case test files (should be camelCase)"
  echo "$WRONG_TEST_FILES"
  echo "   Pattern: test_ShoppingCart.py not test_shopping_cart.py"
  ((ERRORS++))
else
  echo -e "${GREEN}✅ PASS:${NC} Test files use camelCase naming"
fi
echo ""

# Summary
echo "================================"
if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
  echo "Code follows AGENT-CONTEXT.md patterns"
  exit 0
else
  echo -e "${RED}❌ $ERRORS CHECK(S) FAILED${NC}"
  echo "Review AGENT-CONTEXT.md and fix violations"
  exit 1
fi
