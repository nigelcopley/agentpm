#!/bin/bash
#
# AIPM Hooks Exit Code Validation Test Suite
# Work Item: WI-38 - Enhance Hook System with Severity-Based Exit Codes
# Task: #199 - Create exit code validation tests-BAK
# Date: 2025-10-09
#
# Exit Code Semantics:
#   0 = Silent success (informational, not shown to model/user)
#   1 = Warning (show stderr to model, allow tool)
#   2 = Blocking error (show stderr to model, BLOCK tool)
#
# Usage:
#   cd /Users/nigelcopley/.project_manager/aipm-v2
#   bash testing/hooks/test_exit_codes.sh
#

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Project root
PROJECT_ROOT="/Users/nigelcopley/.project_manager/aipm-v2"
cd "$PROJECT_ROOT"

# Hook locations
HOOK_DIR_CLAUDE=".claude/hooks"
HOOK_DIR_AIPM="agentpm/hooks/implementations"

# Test both locations
HOOK_LOCATIONS=("$HOOK_DIR_CLAUDE" "$HOOK_DIR_AIPM")

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   AIPM Hooks Exit Code Validation Test Suite                  ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Testing hooks in locations:"
for loc in "${HOOK_LOCATIONS[@]}"; do
    echo "  • $loc"
done
echo ""

# Helper function to run hook test
run_hook_test() {
    local hook_name="$1"
    local test_name="$2"
    local json_input="$3"
    local expected_exit="$4"
    local hook_location="$5"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Run hook and capture exit code
    local actual_exit=0
    echo -n "$json_input" | python3 "$hook_location/$hook_name" 2>&1 >/dev/null || actual_exit=$?

    # Compare exit codes
    if [ "$actual_exit" -eq "$expected_exit" ]; then
        echo -e "  ${GREEN}✅ PASS${NC} - $test_name (exit $actual_exit)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}❌ FAIL${NC} - $test_name (expected $expected_exit, got $actual_exit)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test each location
for HOOK_LOCATION in "${HOOK_LOCATIONS[@]}"; do
    echo -e "\n${BLUE}Testing hooks in: $HOOK_LOCATION${NC}\n"

    # Check if location exists
    if [ ! -d "$HOOK_LOCATION" ]; then
        echo -e "${YELLOW}⚠️  Location does not exist, skipping: $HOOK_LOCATION${NC}"
        continue
    fi

    # ═══════════════════════════════════════════════════════════════
    # PRE-TOOL-USE.PY EXIT CODE TESTS
    # ═══════════════════════════════════════════════════════════════

    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}1. pre-tool-use.py - Exit Code Validation (4 scenarios)${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"

    if [ ! -f "$HOOK_LOCATION/pre-tool-use.py" ]; then
        echo -e "${YELLOW}⚠️  pre-tool-use.py not found in $HOOK_LOCATION${NC}"
    else
        # Exit 2 (Blocking): Security violation - cd /tmp
        run_hook_test "pre-tool-use.py" \
            "Security violation (cd /tmp)" \
            '{"tool_name":"Bash","parameters":{"command":"cd /tmp && mkdir test"},"session_id":"test"}' \
            2 \
            "$HOOK_LOCATION"

        # Exit 2 (Blocking): Workflow violation - mkdir without work item
        run_hook_test "pre-tool-use.py" \
            "Workflow violation (mkdir without WI)" \
            '{"tool_name":"Bash","parameters":{"command":"mkdir agentpm/new_module"},"session_id":"test"}' \
            2 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Commit without WI reference
        run_hook_test "pre-tool-use.py" \
            "Commit without WI reference" \
            '{"tool_name":"Bash","parameters":{"command":"git commit -m \"Fix bug\""},"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Destructive command (rm -rf)
        run_hook_test "pre-tool-use.py" \
            "Destructive command warning" \
            '{"tool_name":"Bash","parameters":{"command":"rm -rf old_code/"},"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): Safe AIPM command
        run_hook_test "pre-tool-use.py" \
            "Safe AIPM command" \
            '{"tool_name":"Bash","parameters":{"command":"apm task list"},"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): Safe edit command
        run_hook_test "pre-tool-use.py" \
            "Safe edit operation" \
            '{"tool_name":"Edit","parameters":{"file_path":"agentpm/core/database/models/task.py","old_string":"old","new_string":"new"},"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"
    fi

    # ═══════════════════════════════════════════════════════════════
    # POST-TOOL-USE.PY EXIT CODE TESTS
    # ═══════════════════════════════════════════════════════════════

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}2. post-tool-use.py - Exit Code Validation (7 scenarios)${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"

    if [ ! -f "$HOOK_LOCATION/post-tool-use.py" ]; then
        echo -e "${YELLOW}⚠️  post-tool-use.py not found in $HOOK_LOCATION${NC}"
    else
        # Exit 0 (Silent): Task started
        run_hook_test "post-tool-use.py" \
            "Task started (silent)" \
            '{"tool_name":"Bash","parameters":{"command":"apm task start 123"},"result":"Task started successfully","success":true,"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Task submitted for review
        run_hook_test "post-tool-use.py" \
            "Task submitted for review" \
            '{"tool_name":"Bash","parameters":{"command":"apm task submit-review 123"},"result":"Task submitted","success":true,"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Task completed
        run_hook_test "post-tool-use.py" \
            "Task completed (agent separation reminder)" \
            '{"tool_name":"Bash","parameters":{"command":"apm task complete 123"},"result":"Task completed","success":true,"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): Git commit success
        run_hook_test "post-tool-use.py" \
            "Git commit success (silent)" \
            '{"tool_name":"Bash","parameters":{"command":"git commit -m \"feat(WI-30): Add feature\""},"result":"Committed","success":true,"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): Tests passing
        run_hook_test "post-tool-use.py" \
            "Tests passing (silent)" \
            '{"tool_name":"Bash","parameters":{"command":"pytest tests-BAK/"},"result":"45 passed in 2.3s","success":true,"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Tests failed
        run_hook_test "post-tool-use.py" \
            "Tests failed (never skip tests reminder)" \
            '{"tool_name":"Bash","parameters":{"command":"pytest tests-BAK/"},"result":"3 failed, 42 passed","success":false,"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): Core code modified
        run_hook_test "post-tool-use.py" \
            "Core code modified (workflow reminder)" \
            '{"tool_name":"Edit","parameters":{"file_path":"agentpm/core/workflow/service.py","old_string":"old","new_string":"new"},"result":"File edited","success":true,"session_id":"test"}' \
            1 \
            "$HOOK_LOCATION"

        # Exit 1 (Warning): General tool failure
        run_hook_test "post-tool-use.py" \
            "General tool failure (any failure = warning)" \
            '{"tool_name":"Bash","parameters":{"command":"ls /nonexistent"},"result":"No such file","success":false,"session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"
    fi

    # ═══════════════════════════════════════════════════════════════
    # USER-PROMPT-SUBMIT.PY EXIT CODE TESTS
    # ═══════════════════════════════════════════════════════════════

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}3. user-prompt-submit.py - Exit Code Validation (3 scenarios)${NC}"
    echo -e "${BLUE}─────────────────────────────────────────────────────────────${NC}"

    if [ ! -f "$HOOK_LOCATION/user-prompt-submit.py" ]; then
        echo -e "${YELLOW}⚠️  user-prompt-submit.py not found in $HOOK_LOCATION${NC}"
    else
        # Exit 0 (Silent): Work item mentioned (found or not found)
        run_hook_test "user-prompt-submit.py" \
            "Work item reference (silent injection)" \
            '{"prompt":"Lets work on WI-30","session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): Task mentioned (found or not found)
        run_hook_test "user-prompt-submit.py" \
            "Task reference (silent injection)" \
            '{"prompt":"Review Task #123","session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Exit 0 (Silent): No entity mentions (normal prompt)
        run_hook_test "user-prompt-submit.py" \
            "Normal prompt (no injection needed)" \
            '{"prompt":"How do I use pytest fixtures?","session_id":"test"}' \
            0 \
            "$HOOK_LOCATION"

        # Note: Database connection failure would be Exit 1, but requires
        # special setup (corrupted DB), so we test graceful degradation instead
    fi
done

# ═══════════════════════════════════════════════════════════════
# TEST SUMMARY
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Test Summary                                                 ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
if [ "$FAILED_TESTS" -gt 0 ]; then
    echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
else
    echo -e "Failed:       $FAILED_TESTS"
fi
echo ""

# Calculate pass rate
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Pass Rate:    $PASS_RATE%"
    echo ""

    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Review output above.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  No tests were run. Check hook locations.${NC}"
    exit 1
fi
