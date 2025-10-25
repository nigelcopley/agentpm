#!/bin/bash
#
# Document Registration Script (Shell Version)
#
# Registers valuable untracked documents into the database.
# Reads file paths from /tmp/files_to_register.txt and uses the apm CLI.
#
# This is a simpler shell-based version that uses the apm document add command.
#

# Don't exit on error - we want to continue registering even if some fail
set +e

INPUT_FILE="/tmp/files_to_register.txt"
PROJECT_ROOT="/Users/nigelcopley/.project_manager/aipm-v2"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Input file not found: $INPUT_FILE"
    echo "   Waiting for pattern-applier to create the file..."
    exit 1
fi

# Count total valid file paths (excluding headers)
# Only process docs/ and root .md files
TOTAL=$(grep -E "^(docs/|[A-Z0-9_-]+\.md$)" "$INPUT_FILE" | wc -l | tr -d ' ')
echo "📄 Found $TOTAL files to register"
echo ""

SUCCESS=0
FAILED=0
SKIPPED=0

# Function to detect document type from path
detect_doc_type() {
    local filepath="$1"
    local path_lower=$(echo "$filepath" | tr '[:upper:]' '[:lower:]')

    # Check for specific patterns
    case "$path_lower" in
        *adr/*|*decision/*|*decisions/*)
            echo "adr" ;;
        *architecture/*)
            echo "architecture" ;;
        *design/*)
            echo "design" ;;
        *requirements/*|*requirement/*)
            echo "requirements" ;;
        *user-guide/*|*user_guide/*)
            echo "user_guide" ;;
        *admin-guide/*|*admin_guide/*)
            echo "admin_guide" ;;
        *api-doc/*|*api_doc/*|*api/*)
            echo "api_doc" ;;
        *specification/*|*spec/*)
            echo "specification" ;;
        *test-plan/*|*test_plan/*)
            echo "test_plan" ;;
        *runbook/*)
            echo "runbook" ;;
        *migration-guide/*|*migration_guide/*)
            echo "migration_guide" ;;
        *troubleshooting/*)
            echo "troubleshooting" ;;
        *implementation-plan/*|*implementation_plan/*)
            echo "implementation_plan" ;;
        *planning/*)
            echo "requirements" ;;
        *guides/*)
            echo "user_guide" ;;
        *reference/*)
            echo "specification" ;;
        *processes/*)
            echo "test_plan" ;;
        *operations/*)
            echo "runbook" ;;
        *governance/*)
            echo "quality_gates_specification" ;;
        *communication/*)
            echo "market_research_report" ;;
        *)
            echo "other" ;;
    esac
}

# Function to generate title from path
generate_title() {
    local filepath="$1"
    local filename=$(basename "$filepath" .md)
    # Replace hyphens and underscores with spaces, capitalize words
    echo "$filename" | sed 's/[-_]/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1'
}

# Process each file
while IFS= read -r filepath; do
    # Skip empty lines
    [ -z "$filepath" ] && continue

    # Skip header lines and section markers (lines that don't start with valid paths)
    # Only process docs/ paths and root .md files for now
    # (Python/test files need different handling due to path validation prompts)
    if [[ ! "$filepath" =~ ^(docs/|[A-Z0-9_-]+\.md$) ]]; then
        ((SKIPPED++))
        continue
    fi

    # Detect document type
    doctype=$(detect_doc_type "$filepath")

    # Generate title
    title=$(generate_title "$filepath")

    # Register using apm CLI
    if apm document add \
        --entity-type=project \
        --entity-id=1 \
        --file-path="$filepath" \
        --type="$doctype" \
        --title="$title" \
        --created-by="system_cleanup" \
        --no-validate-file \
        > /dev/null 2>&1; then

        echo "✅ Registered: $filepath (type: $doctype)"
        ((SUCCESS++))
    else
        echo "❌ Failed: $filepath"
        ((FAILED++))
    fi

done < "$INPUT_FILE"

# Print summary
echo ""
echo "=========================================="
echo "📊 Registration Summary"
echo "=========================================="
echo "✅ Successfully registered: $SUCCESS"
echo "❌ Failed: $FAILED"
echo "📝 Total: $TOTAL"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "⚠️  Some documents failed to register. Check errors above."
    exit 1
else
    echo "✅ All documents registered successfully!"
    exit 0
fi
