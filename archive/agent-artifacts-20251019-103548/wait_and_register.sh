#!/bin/bash
#
# Wait for pattern-applier to complete, then register documents
#
# This script monitors for the creation of /tmp/files_to_register.txt
# and automatically runs the registration process when ready.
#

INPUT_FILE="/tmp/files_to_register.txt"
MAX_WAIT=300  # Maximum wait time in seconds (5 minutes)
CHECK_INTERVAL=2  # Check every 2 seconds

echo "⏳ Waiting for pattern-applier to create $INPUT_FILE..."
echo "   (Will wait up to $MAX_WAIT seconds)"
echo ""

elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    if [ -f "$INPUT_FILE" ]; then
        echo "✅ Input file found!"
        echo ""

        # Wait a moment to ensure file is fully written
        sleep 1

        # Run registration script
        echo "🚀 Starting document registration..."
        echo ""
        exec /Users/nigelcopley/.project_manager/aipm-v2/register_documents.sh
    fi

    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))

    # Show progress every 10 seconds
    if [ $((elapsed % 10)) -eq 0 ]; then
        echo "   Still waiting... (${elapsed}s elapsed)"
    fi
done

echo ""
echo "❌ Timeout: Input file not created within $MAX_WAIT seconds"
echo "   The pattern-applier may not have completed yet."
echo ""
echo "💡 You can:"
echo "   1. Wait and run this script again"
echo "   2. Check if pattern-applier is still running"
echo "   3. Manually run: ./register_documents.sh (once file is ready)"
exit 1
