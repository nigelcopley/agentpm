#!/bin/bash

# Task Validation Script
# Ensures tasks are properly filled before moving to todo state

validate_task() {
    local task_file="$1"
    local errors=0

    echo "Validating task: $(basename $task_file)"
    echo "----------------------------------------"

    # Check file exists
    if [ ! -f "$task_file" ]; then
        echo "❌ ERROR: Task file not found: $task_file"
        return 1
    fi

    # Count placeholders (excluding valid markdown links and paths)
    local placeholder_count=$(grep -o '\[[^]]*\]' "$task_file" |
                              grep -v 'http' |
                              grep -v '\.\.' |
                              grep -v 'WORKFLOW_RULES' |
                              grep -v '✅' |
                              grep -v '❌' |
                              grep -v '⏳' |
                              grep -v '^\[ \]$' |
                              grep -v '^\[x\]$' |
                              grep -v '^\[X\]$' |
                              wc -l)

    if [ $placeholder_count -gt 5 ]; then
        echo "❌ ERROR: Too many unfilled placeholders ($placeholder_count found, max 5 allowed)"
        echo "   Examples of unfilled placeholders found:"
        grep -o '\[[^]]*\]' "$task_file" | grep -v 'http' | grep -v '\.\.' | grep -v '^\[ \]$' | grep -v '^\[x\]$' | grep -v '^\[X\]$' | head -5 | while read placeholder; do
            echo "   - $placeholder"
        done
        errors=$((errors + 1))
    else
        echo "✅ Placeholder check passed ($placeholder_count placeholders)"
    fi

    # Check for required sections
    echo ""
    echo "Checking required sections..."

    # Essential sections that must exist and have content
    for section in "Objective" "Executive Summary"; do
        if grep -q "## .*$section" "$task_file"; then
            # Check if section has actual content (not just placeholder text)
            local section_line=$(grep -n "## .*$section" "$task_file" | head -1 | cut -d: -f1)
            local next_section_line=$(tail -n +$((section_line + 1)) "$task_file" | grep -n "^##" | head -1 | cut -d: -f1)

            if [ -z "$next_section_line" ]; then
                next_section_line=$(wc -l < "$task_file")
            else
                next_section_line=$((section_line + next_section_line))
            fi

            local content=$(sed -n "$((section_line + 1)),$((next_section_line - 1))p" "$task_file" |
                          grep -v "^\s*$" |
                          grep -v "^\[.*\]$" |
                          wc -l)

            if [ $content -lt 2 ]; then
                echo "❌ ERROR: Section '$section' exists but lacks content"
                errors=$((errors + 1))
            else
                echo "✅ Section '$section' has content"
            fi
        else
            echo "❌ ERROR: Required section missing: $section"
            errors=$((errors + 1))
        fi
    done

    # Check for metadata
    echo ""
    echo "Checking metadata..."

    if ! grep -q "^\*\*Priority\*\*:" "$task_file"; then
        echo "❌ ERROR: Missing Priority metadata"
        errors=$((errors + 1))
    else
        echo "✅ Priority defined"
    fi

    if ! grep -q "^\*\*Document Status\*\*:" "$task_file"; then
        echo "❌ ERROR: Missing Document Status"
        errors=$((errors + 1))
    else
        echo "✅ Document Status defined"
    fi

    # Check for workflow rules link
    if ! grep -q "Workflow Rules" "$task_file"; then
        echo "⚠️  WARNING: Missing Workflow Rules link"
    else
        echo "✅ Workflow Rules linked"
    fi

    # Check for task overlaps using overlap detection script
    echo ""
    echo "Checking for task overlaps..."
    overlap_script="$(dirname "$0")/overlap_detection.sh"
    if [ -f "$overlap_script" ]; then
        if ! "$overlap_script" check "$task_file" 0.6; then
            echo "⚠️  WARNING: Potential task overlap detected"
            echo "   Review the similar tasks and ensure this is not a duplicate"
            echo "   Use overlap_detection.sh check-all to review all pending tasks"
        else
            echo "✅ No task overlaps detected"
        fi
    else
        echo "⚠️  WARNING: Overlap detection script not found"
    fi

    # Final verdict
    echo ""
    echo "========================================"
    if [ $errors -eq 0 ]; then
        echo "✅ VALIDATION PASSED - Task is ready for todo state"
        return 0
    else
        echo "❌ VALIDATION FAILED - $errors issues found"
        echo ""
        echo "This task cannot move to todo state until issues are resolved."
        echo "Please fill in placeholders and add missing content."
        return 1
    fi
}

# Main execution
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <task-file.md>"
    echo ""
    echo "Validates a task file for completeness before moving to todo state."
    echo "Checks for:"
    echo "  - Excessive placeholders (max 5 allowed)"
    echo "  - Required sections with actual content"
    echo "  - Metadata completeness"
    echo "  - Workflow rules link"
    exit 1
fi

validate_task "$1"
exit $?