#!/bin/bash

# Feature Migration Script
# Categorizes and moves existing features into the new workflow structure

migrate_existing_features() {
    echo "🔄 FEATURE MIGRATION: Analyzing existing features"
    echo "=================================================="

    # Create backup
    local backup_dir="docs/features_backup_$(date +%Y%m%d_%H%M%S)"
    echo "📋 Creating backup at: $backup_dir"
    cp -r docs/artifacts/features "$backup_dir"

    # Track migration results
    local total_features=0
    local migrated_features=0
    local skipped_features=0

    # Analyze each feature file
    for feature_file in docs/artifacts/features/*.md; do
        if [ -f "$feature_file" ]; then
            local filename=$(basename "$feature_file")

            # Skip workflow rules and README
            if [[ "$filename" == "README.md" ]] || [[ "$filename" == "FEATURE_WORKFLOW_RULES.md" ]]; then
                continue
            fi

            ((total_features++))
            echo ""
            echo "🔍 Analyzing: $filename"
            echo "$(printf '=%.0s' {1..50})"

            # Analyze feature content and determine state
            local target_state=$(analyze_feature_state "$feature_file")

            if [ "$target_state" != "skip" ]; then
                migrate_feature_to_state "$feature_file" "$target_state"
                ((migrated_features++))
            else
                echo "⏭️  Skipping migration for $filename"
                ((skipped_features++))
            fi
        fi
    done

    # Generate migration report
    generate_migration_report "$total_features" "$migrated_features" "$skipped_features" "$backup_dir"
}

analyze_feature_state() {
    local feature_file="$1"
    local filename=$(basename "$feature_file")

    echo "📊 Content Analysis:"

    # Check for implementation indicators
    local has_implementation=$(grep -c -i "implement\|deploy\|production\|release\|delivered\|completed" "$feature_file")
    local has_acceptance_criteria=$(grep -c -i "acceptance.*criteria\|definition.*done" "$feature_file")
    local has_validation=$(grep -c -i "validation\|feasib\|approved\|validated" "$feature_file")
    local has_detailed_spec=$(grep -c "## .*6W\|## .*Technical\|## .*Architecture\|## .*Implementation" "$feature_file")
    local has_basic_concept=$(grep -c -i "problem\|solution\|concept\|idea" "$feature_file")

    echo "   Implementation indicators: $has_implementation"
    echo "   Acceptance criteria: $has_acceptance_criteria"
    echo "   Validation indicators: $has_validation"
    echo "   Detailed specification: $has_detailed_spec"
    echo "   Basic concept: $has_basic_concept"

    # Determine target state based on content analysis
    local target_state

    # Check for implemented features
    if [ $has_implementation -gt 3 ] && [ $has_acceptance_criteria -gt 0 ]; then
        target_state="implemented"
        echo "🚀 Classification: IMPLEMENTED (has implementation evidence + criteria)"

    # Check for accepted features (ready for development)
    elif [ $has_acceptance_criteria -gt 0 ] && [ $has_detailed_spec -gt 2 ]; then
        target_state="accepted"
        echo "✅ Classification: ACCEPTED (has criteria + detailed spec)"

    # Check for validated features
    elif [ $has_validation -gt 1 ] && [ $has_detailed_spec -gt 1 ]; then
        target_state="validated"
        echo "🔍 Classification: VALIDATED (has validation + good spec)"

    # Check for proposed features (detailed specs)
    elif [ $has_detailed_spec -gt 2 ]; then
        target_state="proposed"
        echo "📋 Classification: PROPOSED (detailed specification)"

    # Check for basic ideas
    elif [ $has_basic_concept -gt 0 ]; then
        target_state="ideas"
        echo "💡 Classification: IDEAS (basic concept only)"

    # Default to proposed if unclear
    else
        target_state="proposed"
        echo "📋 Classification: PROPOSED (default - needs review)"
    fi

    echo "$target_state"
}

migrate_feature_to_state() {
    local feature_file="$1"
    local target_state="$2"
    local filename=$(basename "$feature_file")

    echo "📁 Migration Action: $filename → $target_state/"

    # Prepare target file
    local target_file="docs/artifacts/features/$target_state/$filename"

    # Copy file to new location
    cp "$feature_file" "$target_file"

    # Update metadata in the migrated file
    update_feature_metadata "$target_file" "$target_state"

    # Remove original file
    rm "$feature_file"

    echo "✅ Migrated: $filename → docs/artifacts/features/$target_state/"

    # If feature moved to accepted state, offer to generate tasks
    if [ "$target_state" == "accepted" ]; then
        echo "🚀 Feature is in ACCEPTED state - tasks can be auto-generated"
        echo "   Run: tools/generate_feature_tasks.sh $target_file"
    fi
}

update_feature_metadata() {
    local feature_file="$1"
    local target_state="$2"

    # Add workflow rules link if missing
    if ! grep -q "FEATURE_WORKFLOW_RULES" "$feature_file"; then
        echo "" >> "$feature_file"
        echo "**Workflow Rules**: [../FEATURE_WORKFLOW_RULES.md](../FEATURE_WORKFLOW_RULES.md)" >> "$feature_file"
    fi

    # Update or add status metadata
    if grep -q "^\*\*Status\*\*:" "$feature_file"; then
        # Update existing status
        local temp_file=$(mktemp)
        sed "s/^\*\*Status\*\*:.*/\*\*Status\*\*: $target_state/" "$feature_file" > "$temp_file"
        mv "$temp_file" "$feature_file"
    else
        # Add status metadata after title
        local temp_file=$(mktemp)
        awk 'NR==1{print; print ""; print "**Status**: '$target_state'"; next}1' "$feature_file" > "$temp_file"
        mv "$temp_file" "$feature_file"
    fi

    # Add migration metadata
    local migration_note="

<!-- MIGRATION NOTE: Auto-migrated to $target_state state on $(date +%Y-%m-%d) -->
<!-- Original location: docs/artifacts/features/$(basename "$feature_file") -->
<!-- Review and update metadata as needed -->"

    echo "$migration_note" >> "$feature_file"
}

generate_migration_report() {
    local total_features="$1"
    local migrated_features="$2"
    local skipped_features="$3"
    local backup_dir="$4"

    echo ""
    echo "📊 MIGRATION COMPLETE"
    echo "===================="
    echo ""

    # Feature count by state
    echo "📈 Feature Distribution After Migration:"
    for state in ideas proposed validated accepted implemented archived; do
        local count=$(find "docs/artifacts/features/$state" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        printf "   %-12s: %3d features\n" "$(echo $state | tr 'a-z' 'A-Z')" "$count"
    done

    echo ""
    echo "📋 Migration Summary:"
    echo "   Total Features Analyzed: $total_features"
    echo "   Successfully Migrated: $migrated_features"
    echo "   Skipped: $skipped_features"
    echo ""
    echo "💾 Backup Location: $backup_dir"
    echo ""

    # Generate feature validation report
    echo "🔍 Running validation on migrated features..."
    ./tools/validate_feature.sh --all

    echo ""
    echo "✅ MIGRATION RECOMMENDATIONS:"
    echo "=============================="
    echo ""
    echo "1. Review migrated features for correct classification"
    echo "2. Update feature metadata (Priority, Complexity, etc.)"
    echo "3. Run validation: tools/validate_feature.sh --all"
    echo "4. For ACCEPTED features, generate tasks:"
    echo "   find docs/artifacts/features/accepted -name '*.md' -exec tools/generate_feature_tasks.sh {} \;"
    echo ""
    echo "5. Consider archiving old/obsolete features:"
    echo "   mv docs/artifacts/features/[state]/obsolete_feature.md docs/artifacts/features/archived/"
    echo ""
    echo "6. Review and customize auto-generated tasks in docs/artifacts/tasks/to_review/"
}

# Validation and assistance functions

validate_migration_readiness() {
    echo "🔍 MIGRATION READINESS CHECK"
    echo "============================"

    # Check if new directory structure exists
    local missing_dirs=0
    for state_dir in ideas proposed validated accepted implemented archived; do
        if [ ! -d "docs/artifacts/features/$state_dir" ]; then
            echo "❌ Missing directory: docs/artifacts/features/$state_dir"
            ((missing_dirs++))
        else
            echo "✅ Directory exists: docs/artifacts/features/$state_dir"
        fi
    done

    # Check if required scripts exist
    if [ ! -f "tools/validate_feature.sh" ]; then
        echo "❌ Missing validation script: tools/validate_feature.sh"
        ((missing_dirs++))
    else
        echo "✅ Validation script available"
    fi

    if [ ! -f "tools/generate_feature_tasks.sh" ]; then
        echo "❌ Missing task generation script: tools/generate_feature_tasks.sh"
        ((missing_dirs++))
    else
        echo "✅ Task generation script available"
    fi

    # Check for workflow rules
    if [ ! -f "docs/artifacts/features/FEATURE_WORKFLOW_RULES.md" ]; then
        echo "❌ Missing workflow rules: docs/artifacts/features/FEATURE_WORKFLOW_RULES.md"
        ((missing_dirs++))
    else
        echo "✅ Workflow rules available"
    fi

    echo ""
    if [ $missing_dirs -eq 0 ]; then
        echo "✅ READY TO MIGRATE"
        return 0
    else
        echo "❌ NOT READY - Fix missing components first"
        return 1
    fi
}

preview_migration() {
    echo "🔍 MIGRATION PREVIEW"
    echo "==================="
    echo ""
    echo "This preview shows how existing features would be classified:"
    echo ""

    for feature_file in docs/artifacts/features/*.md; do
        if [ -f "$feature_file" ]; then
            local filename=$(basename "$feature_file")

            # Skip workflow rules and README
            if [[ "$filename" == "README.md" ]] || [[ "$filename" == "FEATURE_WORKFLOW_RULES.md" ]]; then
                continue
            fi

            echo "📄 $filename"
            local target_state=$(analyze_feature_state "$feature_file")
            echo "   → Would move to: docs/artifacts/features/$target_state/"
            echo ""
        fi
    done

    echo "To proceed with actual migration, run: $0 --migrate"
}

# Interactive feature classifier
classify_feature_interactive() {
    local feature_file="$1"
    local filename=$(basename "$feature_file")

    echo "🤖 INTERACTIVE CLASSIFICATION: $filename"
    echo "$(printf '=%.0s' {1..50})"

    # Show automatic classification
    local auto_state=$(analyze_feature_state "$feature_file")
    echo ""
    echo "🎯 Automatic classification suggests: $auto_state"
    echo ""
    echo "Available states:"
    echo "  1) ideas      - Raw concepts and brainstorming"
    echo "  2) proposed   - Detailed proposals using templates"
    echo "  3) validated  - Verified and feasible features"
    echo "  4) accepted   - Approved for development"
    echo "  5) implemented - Completed features"
    echo "  6) archived   - Rejected/cancelled features"
    echo ""

    # Get user input
    read -p "Choose state (1-6) or press Enter to use automatic classification ($auto_state): " choice

    case $choice in
        1) echo "ideas" ;;
        2) echo "proposed" ;;
        3) echo "validated" ;;
        4) echo "accepted" ;;
        5) echo "implemented" ;;
        6) echo "archived" ;;
        *) echo "$auto_state" ;;
    esac
}

# Main execution
case "${1:-}" in
    "--migrate")
        echo "🚀 Starting automated feature migration..."
        validate_migration_readiness && migrate_existing_features
        ;;
    "--preview")
        echo "👀 Generating migration preview..."
        preview_migration
        ;;
    "--validate")
        echo "🔍 Validating migration readiness..."
        validate_migration_readiness
        ;;
    "--interactive")
        echo "🤖 Starting interactive migration..."
        if validate_migration_readiness; then
            echo "Interactive migration not yet implemented"
            echo "Use --migrate for automated migration or --preview to see planned changes"
        fi
        ;;
    "--help")
        echo "Feature Migration Script"
        echo "======================="
        echo ""
        echo "Usage:"
        echo "  $0 --migrate         # Perform automated migration"
        echo "  $0 --preview         # Show migration plan without executing"
        echo "  $0 --validate        # Check if system is ready for migration"
        echo "  $0 --interactive     # Interactive feature classification (TODO)"
        echo "  $0 --help            # Show this help"
        echo ""
        echo "The script will:"
        echo "1. Analyze existing features in docs/artifacts/features/"
        echo "2. Classify them into appropriate workflow states"
        echo "3. Move them to the correct subdirectories"
        echo "4. Update metadata and add workflow links"
        echo "5. Create a backup of the original structure"
        echo ""
        echo "States:"
        echo "  ideas       - Basic concepts and brainstorming"
        echo "  proposed    - Detailed specifications"
        echo "  validated   - Technically and business validated"
        echo "  accepted    - Approved for development (auto-generates tasks)"
        echo "  implemented - Completed and deployed"
        echo "  archived    - Rejected, cancelled, or deprecated"
        ;;
    *)
        echo "❓ Feature Migration Script"
        echo "========================="
        echo ""
        echo "Run '$0 --help' for usage information"
        echo "Run '$0 --validate' to check migration readiness"
        echo "Run '$0 --preview' to see planned changes"
        echo "Run '$0 --migrate' to perform the migration"
        echo ""

        # Quick status check
        echo "📊 Current Feature Status:"
        echo "   Features in root: $(find docs/artifacts/features -maxdepth 1 -name "*.md" ! -name "README.md" ! -name "FEATURE_WORKFLOW_RULES.md" | wc -l | tr -d ' ')"
        echo "   Workflow directories: $(find docs/artifacts/features -maxdepth 1 -type d | grep -v "^docs/artifacts/features$" | wc -l | tr -d ' ')"
        ;;
esac