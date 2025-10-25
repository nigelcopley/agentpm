#!/bin/bash
#
# Document Registration Status Check
#
# Displays current status of document registration process
#

echo "📊 Document Registration Status Check"
echo "======================================"
echo ""

# Check if input file exists
INPUT_FILE="/tmp/files_to_register.txt"
if [ -f "$INPUT_FILE" ]; then
    FILE_COUNT=$(wc -l < "$INPUT_FILE" | tr -d ' ')
    echo "✅ Input file exists: $INPUT_FILE"
    echo "   Files to register: $FILE_COUNT"
else
    echo "⏳ Input file not yet created: $INPUT_FILE"
    echo "   Status: Waiting for pattern-applier"
fi
echo ""

# Check current database state
DB_FILE="/Users/nigelcopley/.project_manager/aipm-v2/.aipm/data/aipm.db"
if [ -f "$DB_FILE" ]; then
    echo "📁 Database Status:"
    echo "   Location: $DB_FILE"

    # Total documents
    TOTAL_DOCS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM document_references;")
    echo "   Total documents: $TOTAL_DOCS"

    # System cleanup documents
    SYSTEM_DOCS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM document_references WHERE created_by='system_cleanup';")
    echo "   System cleanup docs: $SYSTEM_DOCS"

    # By creator
    echo ""
    echo "   📝 Documents by creator:"
    sqlite3 "$DB_FILE" "SELECT '      ' || created_by || ': ' || COUNT(*) FROM document_references GROUP BY created_by;"
else
    echo "❌ Database not found: $DB_FILE"
fi
echo ""

# Check script availability
echo "🔧 Available Scripts:"
SCRIPT_DIR="/Users/nigelcopley/.project_manager/aipm-v2"
for script in register_documents.sh register_documents.py wait_and_register.sh; do
    if [ -x "$SCRIPT_DIR/$script" ]; then
        echo "   ✅ $script"
    else
        echo "   ❌ $script (not found or not executable)"
    fi
done
echo ""

# Recommendations
echo "💡 Next Steps:"
if [ -f "$INPUT_FILE" ]; then
    echo "   ✅ Ready to register! Run:"
    echo "      ./register_documents.sh"
else
    echo "   ⏳ Wait for pattern-applier to complete, then run:"
    echo "      ./wait_and_register.sh"
    echo "   Or run manually when ready:"
    echo "      ./register_documents.sh"
fi
echo ""
