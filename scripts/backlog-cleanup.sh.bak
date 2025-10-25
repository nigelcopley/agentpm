#!/bin/bash
# APM (Agent Project Manager) Backlog Cleanup Script
# Date: 2025-10-21
# Purpose: Execute backlog cleanup recommendations
# Reference: docs/planning/status_report/backlog-cleanup-review.md

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         APM (Agent Project Manager) Backlog Cleanup Script                       ║"
echo "║         Review: 48 items → 27 managed items                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CLOSED_COUNT=0
DONE_COUNT=0
ACTIVATED_COUNT=0
TAGGED_COUNT=0
ARCHIVED_COUNT=0

echo -e "${BLUE}=== Phase 1: Close Test Items ===${NC}"
echo "Closing 18 test work items..."
for id in 84 85 86 87 91 92 93 94 95 96 97 98 99 105 106 110 130 136; do
  echo -n "  Closing WI-$id..."
  apm work-item update $id --status=cancelled --note="Test work item - backlog cleanup 2025-10-21" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((CLOSED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
done
echo ""

echo -e "${BLUE}=== Phase 2: Mark Completed Items ===${NC}"
echo "Marking WI-133 as DONE (all 8 tasks completed)..."
echo -n "  WI-133: Document System Enhancement..."
apm work-item update 133 --status=done --note="All 8 tasks completed, feature operational. Backlog cleanup 2025-10-21" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e " ${GREEN}✓${NC}"
  ((DONE_COUNT++))
else
  echo -e " ${RED}✗${NC}"
fi
echo ""

echo -e "${BLUE}=== Phase 3: Close Obsolete Items ===${NC}"
echo "Closing obsolete/redundant work items..."
echo -n "  WI-80: work-item next command (already exists)..."
apm work-item update 80 --status=cancelled --note="Feature already implemented and operational. Backlog cleanup 2025-10-21" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e " ${GREEN}✓${NC}"
  ((CLOSED_COUNT++))
else
  echo -e " ${RED}✗${NC}"
fi

echo -n "  WI-82: idea next command (not needed)..."
apm work-item update 82 --status=cancelled --note="Not needed for v1.0/v1.1. Backlog cleanup 2025-10-21" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e " ${GREEN}✓${NC}"
  ((CLOSED_COUNT++))
else
  echo -e " ${RED}✗${NC}"
fi
echo ""

echo -e "${BLUE}=== Phase 4: Merge Duplicates ===${NC}"
echo "Consolidating duplicate planning items..."
echo -n "  WI-127: Enhancement Opportunities (merge into WI-128)..."
apm work-item update 127 --status=cancelled --note="Consolidated into WI-128 (Final Destination Roadmap Generation). Backlog cleanup 2025-10-21" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo -e " ${GREEN}✓${NC}"
  ((CLOSED_COUNT++))
else
  echo -e " ${RED}✗${NC}"
fi
echo ""

echo -e "${YELLOW}=== Phase 5: Activate Launch-Critical Items ===${NC}"
echo "⚠️  OPTIONAL: Activate WI-142, WI-143, WI-144 for v1.0 launch"
echo "   (Adds 20.5 hours to launch timeline)"
echo ""
read -p "Activate launch-critical items? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Activating launch-critical items..."

  echo -n "  WI-143: Preflight E2E Testing..."
  apm work-item update 143 --status=ready --priority=1 >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((ACTIVATED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi

  echo -n "  WI-144: Live Project E2E Testing..."
  apm work-item update 144 --status=ready --priority=1 >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((ACTIVATED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi

  echo -n "  WI-142: Extract AIPM as orcx (Public Repo)..."
  apm work-item update 142 --status=ready --priority=1 >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((ACTIVATED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
else
  echo "  Skipped activation (deferred for separate decision)"
fi
echo ""

echo -e "${BLUE}=== Phase 6: Tag v1.1 Items ===${NC}"
echo "Tagging 12 items for v1.1 post-launch..."

echo "  Priority 1 (Core Improvements)..."
for id in 129 128 124 139; do
  echo -n "    WI-$id..."
  apm work-item update $id --note="Deferred to v1.1 - Priority 1 per launch decision. Backlog cleanup 2025-10-21" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((TAGGED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
done

echo "  Priority 2 (Documentation & Quality)..."
for id in 141 111 135 122; do
  echo -n "    WI-$id..."
  apm work-item update $id --note="Deferred to v1.1 - Priority 2 (documentation/quality). Backlog cleanup 2025-10-21" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((TAGGED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
done

echo "  Priority 3 (Feature Enhancements)..."
for id in 79 101 83 131; do
  echo -n "    WI-$id..."
  apm work-item update $id --note="Deferred to v1.1 - Priority 3 (enhancements). Backlog cleanup 2025-10-21" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((TAGGED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
done
echo ""

echo -e "${BLUE}=== Phase 7: Archive v1.2+ Items ===${NC}"
echo "Archiving 10 items for v1.2+ future planning..."
for id in 64 67 73 68 69 70 71 72 66 107 121 123 75; do
  echo -n "  WI-$id..."
  apm work-item update $id --note="Deferred to v1.2+ - Future enhancements. Backlog cleanup 2025-10-21" --priority=5 >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✓${NC}"
    ((ARCHIVED_COUNT++))
  else
    echo -e " ${RED}✗${NC}"
  fi
done
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   Cleanup Complete!                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Results:${NC}"
echo "  ✓ Closed/Cancelled: $CLOSED_COUNT work items"
echo "  ✓ Marked Done:      $DONE_COUNT work item"
echo "  ✓ Activated:        $ACTIVATED_COUNT work items"
echo "  ✓ Tagged v1.1:      $TAGGED_COUNT work items"
echo "  ✓ Archived v1.2+:   $ARCHIVED_COUNT work items"
echo ""

TOTAL_PROCESSED=$((CLOSED_COUNT + DONE_COUNT + ACTIVATED_COUNT + TAGGED_COUNT + ARCHIVED_COUNT))
echo -e "${BLUE}Total Processed: $TOTAL_PROCESSED work items${NC}"
echo ""

echo "Next Steps:"
echo "  1. Review status: apm status"
echo "  2. Check activated items: apm work-item list --status=ready"
echo "  3. Review v1.1 backlog: apm work-item list --status=draft"
echo "  4. Create tasks for activated items (if any)"
echo ""
echo "Documentation:"
echo "  - Full Analysis: docs/planning/status_report/backlog-cleanup-review.md"
echo "  - Summary: docs/planning/status_report/BACKLOG-CLEANUP-SUMMARY.md"
echo ""
echo -e "${GREEN}Backlog cleanup complete! 🎉${NC}"
