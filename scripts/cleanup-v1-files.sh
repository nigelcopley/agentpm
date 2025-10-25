#!/bin/bash
# cleanup-v1-files.sh
# Run AFTER apm migrate-v1-to-v2 succeeds
# DO NOT run before migration!
#
# Work Item: WI-40 (V2 Consolidation)
# Task: #220 (Refactoring)

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧹 Manual V1 File Cleanup"
echo "========================"
echo ""
echo "Project Root: $PROJECT_ROOT"
echo ""
echo "⚠️  WARNING: Only run this if 'apm migrate-v1-to-v2' succeeded!"
echo "   Otherwise, use rollback procedures instead."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Create archive directory
ARCHIVE_DIR="$PROJECT_ROOT/.aipm/v1-archive"
mkdir -p "$ARCHIVE_DIR"

echo ""
echo "📦 Archiving V1 files..."

# Archive _RULES/
if [ -d "$PROJECT_ROOT/_RULES" ]; then
    echo "   Moving _RULES/ to archive..."
    mv "$PROJECT_ROOT/_RULES" "$ARCHIVE_DIR/_RULES"
else
    echo "   ⚠️  _RULES/ not found (already archived?)"
fi

# Archive STATUS.md
if [ -f "$PROJECT_ROOT/STATUS.md" ]; then
    echo "   Moving STATUS.md to archive..."
    mv "$PROJECT_ROOT/STATUS.md" "$ARCHIVE_DIR/STATUS.md"
else
    echo "   ⚠️  STATUS.md not found (already archived?)"
fi

# Archive NEXT-SESSION.md
if [ -f "$PROJECT_ROOT/NEXT-SESSION.md" ]; then
    echo "   Moving NEXT-SESSION.md to archive..."
    mv "$PROJECT_ROOT/NEXT-SESSION.md" "$ARCHIVE_DIR/NEXT-SESSION.md"
else
    echo "   ⚠️  NEXT-SESSION.md not found (already archived?)"
fi

echo ""
echo "✅ V1 files archived to: $ARCHIVE_DIR"
echo ""
echo "Verification:"
[ ! -d "$PROJECT_ROOT/_RULES" ] && echo "   ✅ _RULES/ removed from root" || echo "   ❌ _RULES/ still in root"
[ ! -f "$PROJECT_ROOT/STATUS.md" ] && echo "   ✅ STATUS.md removed from root" || echo "   ❌ STATUS.md still in root"
[ ! -f "$PROJECT_ROOT/NEXT-SESSION.md" ] && echo "   ✅ NEXT-SESSION.md removed from root" || echo "   ❌ NEXT-SESSION.md still in root"

echo ""
echo "📝 Next Steps:"
echo "   1. Verify V2 queries work: apm rules list"
echo "   2. Verify session history: apm work-item show-history <id>"
echo "   3. Commit changes: git add . && git commit -m 'chore: Archive V1 files after migration'"
