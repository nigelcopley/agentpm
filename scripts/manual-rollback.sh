#!/bin/bash
# manual-rollback.sh
# Restore V1 files from backup (use most recent backup)
#
# Work Item: WI-40 (V2 Consolidation)
# Task: #220 (Refactoring)

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/.agentpm/v1-backup"
ARCHIVE_DIR="$PROJECT_ROOT/.agentpm/v1-archive"

echo "🔄 Manual V1 Rollback"
echo "===================="
echo ""
echo "Project Root: $PROJECT_ROOT"
echo "Backup Directory: $BACKUP_DIR"
echo ""
echo "⚠️  WARNING: This will restore V1 files and database!"
echo "   Any V2 changes since migration will be lost."
echo ""

# Find most recent backup
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ No backup directory found: $BACKUP_DIR"
    echo "   Cannot rollback without backup."
    exit 1
fi

LATEST_BACKUP=$(ls -t "$BACKUP_DIR" 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found in $BACKUP_DIR"
    echo "   Cannot rollback without backup."
    exit 1
fi

echo "Latest Backup: $LATEST_BACKUP"
BACKUP_PATH="$BACKUP_DIR/$LATEST_BACKUP"

# Show backup contents
echo ""
echo "Backup Contents:"
[ -f "$BACKUP_PATH/agentpm.db.backup" ] && echo "   ✅ agentpm.db.backup" || echo "   ❌ agentpm.db.backup (MISSING)"
[ -d "$BACKUP_PATH/_RULES" ] && echo "   ✅ _RULES/" || echo "   ⚠️  _RULES/ (missing)"
[ -f "$BACKUP_PATH/STATUS.md" ] && echo "   ✅ STATUS.md" || echo "   ⚠️  STATUS.md (missing)"
[ -f "$BACKUP_PATH/NEXT-SESSION.md" ] && echo "   ✅ NEXT-SESSION.md" || echo "   ⚠️  NEXT-SESSION.md (missing)"

echo ""
read -p "Proceed with rollback? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

echo ""
echo "🔄 Rolling back to: $LATEST_BACKUP"

# Step 1: Restore database
echo "   Restoring database..."
if [ -f "$BACKUP_PATH/agentpm.db.backup" ]; then
    mkdir -p "$PROJECT_ROOT/.agentpm/data"
    cp "$BACKUP_PATH/agentpm.db.backup" "$PROJECT_ROOT/.agentpm/data/agentpm.db"
    echo "      ✅ Database restored"
else
    echo "      ❌ Database backup not found - cannot restore"
    exit 1
fi

# Step 2: Restore _RULES/
echo "   Restoring _RULES/..."
if [ -d "$BACKUP_PATH/_RULES" ]; then
    rm -rf "$PROJECT_ROOT/_RULES"
    cp -r "$BACKUP_PATH/_RULES" "$PROJECT_ROOT/_RULES"
    echo "      ✅ _RULES/ restored"
else
    echo "      ⚠️  _RULES/ backup not found - skipping"
fi

# Step 3: Restore STATUS.md
echo "   Restoring STATUS.md..."
if [ -f "$BACKUP_PATH/STATUS.md" ]; then
    cp "$BACKUP_PATH/STATUS.md" "$PROJECT_ROOT/STATUS.md"
    echo "      ✅ STATUS.md restored"
else
    echo "      ⚠️  STATUS.md backup not found - skipping"
fi

# Step 4: Restore NEXT-SESSION.md
echo "   Restoring NEXT-SESSION.md..."
if [ -f "$BACKUP_PATH/NEXT-SESSION.md" ]; then
    cp "$BACKUP_PATH/NEXT-SESSION.md" "$PROJECT_ROOT/NEXT-SESSION.md"
    echo "      ✅ NEXT-SESSION.md restored"
else
    echo "      ⚠️  NEXT-SESSION.md backup not found - skipping"
fi

# Step 5: Verify restoration
echo ""
echo "✅ Rollback complete!"
echo ""
echo "Verification:"
[ -d "$PROJECT_ROOT/_RULES" ] && echo "   ✅ _RULES/ restored" || echo "   ❌ _RULES/ missing"
[ -f "$PROJECT_ROOT/STATUS.md" ] && echo "   ✅ STATUS.md restored" || echo "   ⚠️  STATUS.md missing"
[ -f "$PROJECT_ROOT/NEXT-SESSION.md" ] && echo "   ✅ NEXT-SESSION.md restored" || echo "   ⚠️  NEXT-SESSION.md missing"
[ -f "$PROJECT_ROOT/.agentpm/data/agentpm.db" ] && echo "   ✅ Database restored" || echo "   ❌ Database missing"

echo ""
echo "📝 Next Steps:"
echo "   1. Verify V1 files work: ls -la _RULES/"
echo "   2. Test database: apm status"
echo "   3. If issues persist, check backup at: $BACKUP_PATH"
