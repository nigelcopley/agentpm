#!/bin/bash

# Feature Validation Script
# Ensures features meet requirements for their current state and transitions

validate_feature() {
    local feature_file="$1"
    local errors=0
    local warnings=0

    echo "Validating feature: $(basename $feature_file)"
    echo "========================================"

    # Check file exists
    if [ ! -f "$feature_file" ]; then
        echo "❌ ERROR: Feature file not found: $feature_file"
        return 1
    fi

    # Determine current state from directory structure
    local current_state=$(basename $(dirname "$feature_file"))
    echo "📂 Current State: $current_state"
    echo ""

    # Validate based on current state
    case $current_state in
        "ideas")
            validate_idea_state "$feature_file"
            ;;
        "proposed")
            validate_proposed_state "$feature_file"
            ;;
        "validated")
            validate_validated_state "$feature_file"
            ;;
        "accepted")
            validate_accepted_state "$feature_file"
            ;;
        "implemented")
            validate_implemented_state "$feature_file"
            ;;
        "archived")
            validate_archived_state "$feature_file"
            ;;
        *)
            echo "❌ ERROR: Unknown state directory: $current_state"
            return 1
            ;;
    esac

    return $?
}

validate_idea_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating IDEAS state requirements..."
    echo "----------------------------------------"

    # Check for basic sections
    check_section_exists "Feature Concept" "$feature_file" || ((errors++))
    check_section_exists "Value Hypothesis" "$feature_file" || ((errors++))
    check_section_exists "Target Users" "$feature_file" || ((errors++))

    # Check for required metadata
    check_metadata "Status" "ideas" "$feature_file" || ((errors++))
    check_metadata "Priority" "" "$feature_file" || ((errors++))
    check_metadata "Owner" "" "$feature_file" || ((errors++))

    # Check for workflow rules link
    if ! grep -q "FEATURE_WORKFLOW_RULES" "$feature_file"; then
        echo "⚠️  WARNING: Missing Feature Workflow Rules link"
        ((warnings++))
    else
        echo "✅ Feature Workflow Rules linked"
    fi

    # Count placeholders (should be minimal but some are acceptable)
    validate_placeholder_count "$feature_file" 10 || ((errors++))

    return $errors
}

validate_proposed_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating PROPOSED state requirements..."
    echo "--------------------------------------------"

    # Must use appropriate template
    if ! grep -q "Template.*template" "$feature_file"; then
        echo "❌ ERROR: No template specified in metadata"
        ((errors++))
    else
        echo "✅ Template specified"
    fi

    # Check for comprehensive sections
    check_section_exists "Executive Summary" "$feature_file" || ((errors++))
    check_section_exists "6W.*Intelligence" "$feature_file" || ((errors++))
    check_section_exists "Technical Context" "$feature_file" || ((errors++))
    check_section_exists "Success.*Metrics" "$feature_file" || ((errors++))

    # Check 6W subsections
    check_section_exists "WHO" "$feature_file" || ((errors++))
    check_section_exists "WHAT" "$feature_file" || ((errors++))
    check_section_exists "WHEN" "$feature_file" || ((errors++))
    check_section_exists "WHERE" "$feature_file" || ((errors++))
    check_section_exists "WHY" "$feature_file" || ((errors++))
    check_section_exists "HOW" "$feature_file" || ((errors++))

    # Check metadata completeness
    check_metadata "Status" "proposed" "$feature_file" || ((errors++))
    check_metadata "Priority" "" "$feature_file" || ((errors++))
    check_metadata "Complexity" "" "$feature_file" || ((errors++))
    check_metadata "Business Value" "" "$feature_file" || ((errors++))
    check_metadata "Technical Risk" "" "$feature_file" || ((errors++))

    # Stricter placeholder validation
    validate_placeholder_count "$feature_file" 5 || ((errors++))

    return $errors
}

validate_validated_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating VALIDATED state requirements..."
    echo "---------------------------------------------"

    # All proposed requirements plus validation results
    validate_proposed_state "$feature_file"
    local proposed_errors=$?
    ((errors += proposed_errors))

    # Check for validation results
    check_section_exists "Validation Results" "$feature_file" || ((errors++))

    # Check for specific validation gates
    if ! grep -q -i "technical.*feasibility" "$feature_file"; then
        echo "❌ ERROR: Missing technical feasibility validation"
        ((errors++))
    else
        echo "✅ Technical feasibility documented"
    fi

    if ! grep -q -i "business.*case" "$feature_file"; then
        echo "❌ ERROR: Missing business case validation"
        ((errors++))
    else
        echo "✅ Business case validation documented"
    fi

    # Check metadata updates
    check_metadata "Status" "validated" "$feature_file" || ((errors++))

    # Very strict placeholder validation
    validate_placeholder_count "$feature_file" 2 || ((errors++))

    return $errors
}

validate_accepted_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating ACCEPTED state requirements..."
    echo "--------------------------------------------"

    # All validated requirements plus implementation planning
    validate_validated_state "$feature_file"
    local validated_errors=$?
    ((errors += validated_errors))

    # Check for implementation planning
    check_section_exists "Implementation Plan" "$feature_file" || ((errors++))
    check_section_exists "Acceptance Criteria" "$feature_file" || ((errors++))

    # Check for technical lead assignment
    if ! grep -q "Technical Lead" "$feature_file"; then
        echo "❌ ERROR: Missing Technical Lead assignment"
        ((errors++))
    else
        echo "✅ Technical Lead assigned"
    fi

    # Check metadata updates
    check_metadata "Status" "accepted" "$feature_file" || ((errors++))

    # No placeholders allowed
    validate_placeholder_count "$feature_file" 0 || ((errors++))

    # Check for task generation readiness
    echo ""
    echo "📋 Checking task generation readiness..."
    if [ -d "docs/artifacts/tasks/to_review" ]; then
        local feature_name=$(basename "$feature_file" .md)
        if ls docs/artifacts/tasks/to_review/epic_${feature_name}_* 2>/dev/null; then
            echo "✅ Tasks already generated for this feature"
        else
            echo "⚠️  WARNING: No tasks found - should auto-generate on acceptance"
        fi
    fi

    return $errors
}

validate_implemented_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating IMPLEMENTED state requirements..."
    echo "-----------------------------------------------"

    # All accepted requirements plus completion evidence
    validate_accepted_state "$feature_file"
    local accepted_errors=$?
    ((errors += accepted_errors))

    # Check for completion documentation
    check_section_exists "Implementation Results" "$feature_file" || ((errors++))
    check_section_exists "Success Metrics" "$feature_file" || ((errors++))

    # Check metadata updates
    check_metadata "Status" "implemented" "$feature_file" || ((errors++))

    if ! grep -q "Implementation Date" "$feature_file"; then
        echo "❌ ERROR: Missing Implementation Date"
        ((errors++))
    else
        echo "✅ Implementation Date documented"
    fi

    return $errors
}

validate_archived_state() {
    local feature_file="$1"
    local errors=0

    echo "🔍 Validating ARCHIVED state requirements..."
    echo "--------------------------------------------"

    # Check for archive metadata
    if ! grep -q "Archive Reason" "$feature_file"; then
        echo "❌ ERROR: Missing Archive Reason"
        ((errors++))
    else
        echo "✅ Archive Reason documented"
    fi

    if ! grep -q "Archive Date" "$feature_file"; then
        echo "❌ ERROR: Missing Archive Date"
        ((errors++))
    else
        echo "✅ Archive Date documented"
    fi

    # Check metadata
    check_metadata "Status" "archived" "$feature_file" || ((errors++))

    return $errors
}

# Helper functions

check_section_exists() {
    local section_pattern="$1"
    local file="$2"

    if grep -q "## .*$section_pattern" "$file"; then
        echo "✅ Section found: $section_pattern"
        return 0
    else
        echo "❌ ERROR: Required section missing: $section_pattern"
        return 1
    fi
}

check_metadata() {
    local field="$1"
    local expected_value="$2"
    local file="$3"

    if grep -q "^\*\*$field\*\*:" "$file"; then
        if [ -n "$expected_value" ]; then
            if grep -q "^\*\*$field\*\*:.*$expected_value" "$file"; then
                echo "✅ $field: $expected_value"
                return 0
            else
                echo "❌ ERROR: $field should be '$expected_value'"
                return 1
            fi
        else
            echo "✅ $field defined"
            return 0
        fi
    else
        echo "❌ ERROR: Missing $field metadata"
        return 1
    fi
}

validate_placeholder_count() {
    local file="$1"
    local max_allowed="$2"

    # Count placeholders (excluding valid markdown links and paths)
    local placeholder_count=$(grep -o '\[[^]]*\]' "$file" |
                              grep -v 'http' |
                              grep -v '\.\.' |
                              grep -v 'FEATURE_WORKFLOW_RULES' |
                              grep -v 'WORKFLOW_RULES' |
                              grep -v '✅' |
                              grep -v '❌' |
                              grep -v '⏳' |
                              grep -v '^#' |
                              wc -l)

    if [ $placeholder_count -gt $max_allowed ]; then
        echo "❌ ERROR: Too many unfilled placeholders ($placeholder_count found, max $max_allowed allowed)"
        echo "   Examples of unfilled placeholders found:"
        grep -o '\[[^]]*\]' "$file" | grep -v 'http' | grep -v '\.\.' | head -5 | while read placeholder; do
            echo "   - $placeholder"
        done
        return 1
    else
        echo "✅ Placeholder check passed ($placeholder_count/$max_allowed placeholders)"
        return 0
    fi
}

# State transition validation

validate_state_transition() {
    local feature_file="$1"
    local target_state="$2"
    local current_state=$(basename $(dirname "$feature_file"))

    echo "🔄 Validating state transition: $current_state → $target_state"
    echo "------------------------------------------------------------"

    # Check if transition is allowed
    case "$current_state→$target_state" in
        "ideas→proposed")
            echo "✅ Valid transition: ideas → proposed"
            validate_proposed_state "$feature_file"
            ;;
        "ideas→archived")
            echo "✅ Valid transition: ideas → archived"
            return 0
            ;;
        "proposed→validated")
            echo "✅ Valid transition: proposed → validated"
            validate_validated_state "$feature_file"
            ;;
        "proposed→archived")
            echo "✅ Valid transition: proposed → archived"
            return 0
            ;;
        "validated→accepted")
            echo "✅ Valid transition: validated → accepted"
            validate_accepted_state "$feature_file"
            ;;
        "validated→archived")
            echo "✅ Valid transition: validated → archived"
            return 0
            ;;
        "accepted→implemented")
            echo "✅ Valid transition: accepted → implemented"
            validate_implemented_state "$feature_file"
            ;;
        "accepted→archived")
            echo "✅ Valid transition: accepted → archived"
            return 0
            ;;
        "implemented→archived")
            echo "✅ Valid transition: implemented → archived"
            return 0
            ;;
        *)
            echo "❌ ERROR: Invalid transition: $current_state → $target_state"
            echo "Check FEATURE_WORKFLOW_RULES.md for valid transitions"
            return 1
            ;;
    esac
}

# Batch operations

validate_all_features() {
    local total_errors=0

    echo "🔍 BATCH VALIDATION: All Features"
    echo "=================================="

    for state_dir in docs/artifacts/features/*/; do
        local state=$(basename "$state_dir")
        if [ "$state" = "README.md" ] || [ "$state" = "FEATURE_WORKFLOW_RULES.md" ]; then
            continue
        fi

        echo ""
        echo "📂 Validating $state features..."
        echo "$(printf '=%.0s' {1..40})"

        for feature_file in "$state_dir"*.md; do
            if [ -f "$feature_file" ]; then
                echo ""
                validate_feature "$feature_file"
                local result=$?
                if [ $result -ne 0 ]; then
                    ((total_errors += result))
                fi
            fi
        done
    done

    echo ""
    echo "🏁 BATCH VALIDATION COMPLETE"
    echo "============================"
    if [ $total_errors -eq 0 ]; then
        echo "✅ All features passed validation"
    else
        echo "❌ Total validation errors: $total_errors"
    fi

    return $total_errors
}

generate_feature_report() {
    echo "📊 FEATURE PIPELINE REPORT"
    echo "=========================="
    echo ""

    for state in ideas proposed validated accepted implemented archived; do
        local count=$(find "docs/artifacts/features/$state" -name "*.md" 2>/dev/null | wc -l)
        printf "%-12s: %3d features\n" "$(echo $state | tr 'a-z' 'A-Z')" "$count"
    done

    echo ""
    echo "📈 WORKFLOW METRICS"
    echo "==================="

    # Calculate basic metrics
    local total_active=$(find docs/artifacts/features/{ideas,proposed,validated,accepted} -name "*.md" 2>/dev/null | wc -l)
    local total_completed=$(find docs/artifacts/features/implemented -name "*.md" 2>/dev/null | wc -l)
    local total_all=$(find docs/features -name "*.md" ! -name "README.md" ! -name "FEATURE_WORKFLOW_RULES.md" 2>/dev/null | wc -l)

    echo "Total Active Features: $total_active"
    echo "Total Implemented: $total_completed"
    echo "Total All Features: $total_all"

    if [ $total_all -gt 0 ]; then
        local completion_rate=$(( total_completed * 100 / total_all ))
        echo "Completion Rate: $completion_rate%"
    fi
}

# Main execution

if [ "$#" -eq 0 ]; then
    echo "Feature Validation Script"
    echo "========================="
    echo ""
    echo "Usage:"
    echo "  $0 <feature-file.md>              # Validate single feature"
    echo "  $0 --transition <file> <state>    # Validate state transition"
    echo "  $0 --all                          # Validate all features"
    echo "  $0 --report                       # Generate pipeline report"
    echo ""
    echo "Examples:"
    echo "  $0 docs/artifacts/features/proposed/new_feature.md"
    echo "  $0 --transition docs/artifacts/features/proposed/feature.md validated"
    echo "  $0 --all"
    echo "  $0 --report"
    echo ""
    echo "States: ideas, proposed, validated, accepted, implemented, archived"
    exit 1
fi

case "$1" in
    "--all")
        validate_all_features
        exit $?
        ;;
    "--report")
        generate_feature_report
        exit 0
        ;;
    "--transition")
        if [ "$#" -ne 3 ]; then
            echo "❌ ERROR: --transition requires feature file and target state"
            echo "Usage: $0 --transition <feature-file> <target-state>"
            exit 1
        fi
        validate_state_transition "$2" "$3"
        exit $?
        ;;
    *)
        validate_feature "$1"
        exit $?
        ;;
esac