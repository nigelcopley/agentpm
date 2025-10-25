#!/bin/bash

# Task Overlap Detection Script
# Identifies potential duplicate or overlapping tasks across the task lifecycle

set -e

# Function to calculate word overlap similarity between two titles
calculate_similarity() {
    local title1="$1"
    local title2="$2"

    # Convert to lowercase and extract words
    local words1=$(echo "$title1" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alpha:]' '\n' | grep -v '^$')
    local words2=$(echo "$title2" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alpha:]' '\n' | grep -v '^$')

    # Count total unique words
    local total_words=$(echo -e "$words1\n$words2" | sort -u | wc -l)

    # Count common words
    local common_words=$(echo -e "$words1\n$words2" | sort | uniq -d | wc -l)

    # Calculate similarity ratio (common words / total unique words)
    if [ "$total_words" -gt 0 ]; then
        echo "scale=2; $common_words / $total_words" | bc -l
    else
        echo "0"
    fi
}

# Function to extract task objective for deeper comparison
extract_objective() {
    local task_file="$1"
    sed -n '/## 🎯 Objective/,/##/p' "$task_file" | grep -v "^##" | head -5 | tr '\n' ' '
}

# Function to check for overlapping tasks
check_task_overlap() {
    local new_task="$1"
    local threshold="${2:-0.6}"  # Default similarity threshold

    if [ ! -f "$new_task" ]; then
        echo "❌ ERROR: Task file not found: $new_task"
        return 1
    fi

    local task_title=$(grep "^# " "$new_task" | head -1 | sed 's/^# //')
    local task_objective=$(extract_objective "$new_task")

    echo "🔍 Checking for overlapping tasks..."
    echo "Task: $task_title"
    echo "Threshold: $threshold"
    echo ""

    local overlaps_found=0
    local temp_file=$(mktemp)

    # Check all task directories for similar titles
    find docs/artifacts/tasks -name "*.md" -type f ! -path "*/README.md" | while read file; do
        # Skip the file we're checking
        if [ "$file" = "$new_task" ]; then
            continue
        fi

        local existing_title=$(grep "^# " "$file" | head -1 | sed 's/^# //')
        local existing_objective=$(extract_objective "$file")

        # Calculate title similarity
        local title_similarity=$(calculate_similarity "$task_title" "$existing_title")

        # Calculate objective similarity if both exist
        local objective_similarity="0"
        if [ -n "$task_objective" ] && [ -n "$existing_objective" ]; then
            objective_similarity=$(calculate_similarity "$task_objective" "$existing_objective")
        fi

        # Check if either similarity exceeds threshold
        local max_similarity=$(echo "$title_similarity $objective_similarity" | awk '{print ($1 > $2) ? $1 : $2}')

        if [ $(echo "$max_similarity >= $threshold" | bc -l) -eq 1 ]; then
            echo "⚠️  POTENTIAL OVERLAP DETECTED (similarity: $max_similarity)" >> "$temp_file"
            echo "   File: $file" >> "$temp_file"
            echo "   Title: $existing_title" >> "$temp_file"
            echo "   Location: $(dirname "$file" | sed 's|docs/artifacts/tasks/||')" >> "$temp_file"
            echo "" >> "$temp_file"
            overlaps_found=$((overlaps_found + 1))
        fi
    done

    # Display results
    if [ -s "$temp_file" ]; then
        echo "🚨 OVERLAP ANALYSIS RESULTS:"
        echo "=============================="
        cat "$temp_file"
        echo "📋 RECOMMENDED ACTIONS:"
        echo "1. Review the similar tasks listed above"
        echo "2. Determine if this is a duplicate or genuinely different"
        echo "3. If duplicate: cancel new task and reference existing one"
        echo "4. If different: add distinguishing details to title/objective"
        echo "5. Use the decision matrix in WORKFLOW_RULES.md for guidance"
        echo ""
        rm "$temp_file"
        return 1
    else
        echo "✅ No overlapping tasks detected"
        rm "$temp_file"
        return 0
    fi
}

# Function to run overlap detection on all tasks in to_review
check_all_pending_overlaps() {
    echo "🔍 Running overlap detection on all pending tasks..."
    echo "=================================================="

    local issues_found=0

    for task in docs/artifacts/tasks/to_review/*.md; do
        if [ "$task" != "docs/artifacts/tasks/to_review/README.md" ] && [ -f "$task" ]; then
            echo ""
            echo "Checking: $(basename "$task")"
            echo "----------------------------------------"
            if ! check_task_overlap "$task" 0.6; then
                issues_found=$((issues_found + 1))
            fi
        fi
    done

    echo ""
    echo "=================================================="
    if [ $issues_found -eq 0 ]; then
        echo "✅ No overlaps detected in pending tasks"
        return 0
    else
        echo "⚠️  Found $issues_found potential overlaps requiring review"
        return 1
    fi
}

# Main script logic
case "${1:-}" in
    "check")
        if [ -z "$2" ]; then
            echo "Usage: $0 check <task_file> [threshold]"
            echo "Example: $0 check docs/artifacts/tasks/to_review/my_task.md 0.6"
            exit 1
        fi
        check_task_overlap "$2" "${3:-0.6}"
        ;;
    "check-all")
        check_all_pending_overlaps
        ;;
    *)
        echo "AIPM Task Overlap Detection Script"
        echo "=================================="
        echo ""
        echo "Usage:"
        echo "  $0 check <task_file> [threshold]     Check specific task for overlaps"
        echo "  $0 check-all                        Check all pending tasks for overlaps"
        echo ""
        echo "Examples:"
        echo "  $0 check docs/artifacts/tasks/to_review/my_task.md"
        echo "  $0 check docs/artifacts/tasks/to_review/my_task.md 0.7"
        echo "  $0 check-all"
        echo ""
        echo "Threshold: 0.0 (no similarity) to 1.0 (identical), default 0.6"
        ;;
esac