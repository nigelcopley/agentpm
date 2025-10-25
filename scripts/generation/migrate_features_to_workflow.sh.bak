#!/bin/bash

# Feature Migration Script
# Migrates existing features to the new workflow structure
# Usage: ./tools/migrate_features_to_workflow.sh

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly FEATURES_DIR="$PROJECT_ROOT/docs/features"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Feature analysis and categorization
analyze_feature() {
    local feature_file="$1"
    local feature_name=$(basename "$feature_file" .md)

    # Send log output to stderr to avoid capturing it
    log_info "Analyzing: $feature_name" >&2

    # Read first few lines to understand the feature
    local content=$(head -20 "$feature_file")

    # Determine if it's a spec, feature, or idea
    if [[ "$content" =~ (spec|specification|protocol|integration) ]]; then
        echo "proposed"  # Technical specs are detailed enough for proposed state
    elif [[ "$content" =~ (# .*Feature|## .*Feature|Business.*Brief) ]]; then
        echo "proposed"  # Business features with full brief format
    elif [[ "$content" =~ (comprehensive|detailed|implementation) ]]; then
        echo "proposed"  # Comprehensive features are proposed
    else
        echo "ideas"     # Simple features go to ideas
    fi
}

# Add workflow metadata to feature
add_workflow_metadata() {
    local feature_file="$1"
    local target_state="$2"
    local temp_file="$feature_file.tmp"

    log_info "Adding workflow metadata to $(basename "$feature_file")"

    # Read the file and add metadata after the title
    {
        # Read until first line starting with #
        while IFS= read -r line; do
            echo "$line"
            if [[ "$line" =~ ^# ]]; then
                # Add workflow metadata after title
                echo ""
                echo "**Template**: $(determine_template "$feature_file")"
                echo "**Stage**: $target_state"
                echo "**Priority**: Medium"
                echo "**Owner**: Legacy Migration"
                echo "**Created**: $(date +%Y-%m-%d)"
                echo "**Last Updated**: $(date +%Y-%m-%d)"
                echo "**Workflow Rules**: [FEATURE_WORKFLOW_RULES.md](FEATURE_WORKFLOW_RULES.md)"
                break
            fi
        done < "$feature_file"

        # Read rest of file
        tail -n +2 "$feature_file" | sed '1,/^#/d'

    } > "$temp_file"

    mv "$temp_file" "$feature_file"
}

# Determine appropriate template based on content
determine_template() {
    local feature_file="$1"
    local content=$(head -50 "$feature_file")

    if [[ "$content" =~ (protocol|api|integration|server|LSP|MCP) ]]; then
        echo "integration_spec_template.md"
    elif [[ "$content" =~ (business|user|ROI|market|competitive) ]]; then
        echo "business_feature_template.md"
    else
        echo "technical_feature_template.md"
    fi
}

# Migrate a single feature
migrate_feature() {
    local feature_file="$1"
    local feature_name=$(basename "$feature_file" .md)
    local target_state=$(analyze_feature "$feature_file")
    local target_dir="$FEATURES_DIR/$target_state"
    local target_file="$target_dir/$feature_name.md"

    log_info "Migrating $feature_name → $target_state state"

    # Ensure target directory exists
    mkdir -p "$target_dir"

    # Copy file to new location
    cp "$feature_file" "$target_file"

    # Add workflow metadata
    add_workflow_metadata "$target_file" "$target_state"

    log_success "Migrated: $feature_name → $target_state/"

    # Validate the migrated feature
    if "$SCRIPT_DIR/validate_feature.sh" "$target_file" > /dev/null 2>&1; then
        log_success "Validation passed for $feature_name"
    else
        log_warning "Validation failed for $feature_name - manual review needed"
    fi
}

# Main migration function
migrate_all_features() {
    local features_migrated=0
    local features_skipped=0

    log_info "Starting feature migration to workflow structure"
    log_info "Working directory: $FEATURES_DIR"
    echo

    # Find all markdown files in features directory (not in subdirectories)
    for feature_file in "$FEATURES_DIR"/*.md; do
        # Skip if file doesn't exist (empty glob)
        [[ -f "$feature_file" ]] || continue

        local feature_name=$(basename "$feature_file" .md)

        # Skip README and workflow rules
        if [[ "$feature_name" == "README" ]] || [[ "$feature_name" == "FEATURE_WORKFLOW_RULES" ]]; then
            log_info "Skipping: $feature_name (system file)"
            ((features_skipped++))
            continue
        fi

        # Check if already migrated
        local migrated=false
        for state_dir in "$FEATURES_DIR"/{ideas,proposed,validated,accepted,implemented,archived}; do
            if [[ -f "$state_dir/$feature_name.md" ]]; then
                log_info "Skipping: $feature_name (already migrated to $(basename "$state_dir"))"
                migrated=true
                ((features_skipped++))
                break
            fi
        done

        if [[ "$migrated" == "false" ]]; then
            migrate_feature "$feature_file"
            ((features_migrated++))
        fi
    done

    echo
    log_success "Migration completed"
    log_info "Features migrated: $features_migrated"
    log_info "Features skipped: $features_skipped"

    # Generate post-migration report
    echo
    log_info "Post-migration workflow report:"
    "$SCRIPT_DIR/validate_feature.sh" --report
}

# Create migration backup
create_backup() {
    local backup_dir="$PROJECT_ROOT/backup/features_$(date +%Y%m%d_%H%M%S)"

    log_info "Creating backup: $backup_dir"
    mkdir -p "$backup_dir"

    # Copy all current feature files
    for feature_file in "$FEATURES_DIR"/*.md; do
        [[ -f "$feature_file" ]] || continue
        cp "$feature_file" "$backup_dir/"
    done

    log_success "Backup created: $backup_dir"
}

# Main script execution
main() {
    echo "Feature Migration to Workflow Structure"
    echo "======================================="
    echo

    # Ensure we're in the right directory
    if [[ ! -d "$FEATURES_DIR" ]]; then
        log_error "Features directory not found: $FEATURES_DIR"
        exit 1
    fi

    # Check if workflow directories exist
    if [[ ! -d "$FEATURES_DIR/ideas" ]]; then
        log_error "Workflow directories not found. Run: mkdir -p docs/artifacts/features/{ideas,proposed,validated,accepted,implemented,archived}"
        exit 1
    fi

    # Create backup
    create_backup

    # Run migration
    migrate_all_features

    echo
    log_success "Migration completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Review migrated features for correct categorization"
    echo "2. Run: tools/validate_feature.sh --all"
    echo "3. Update any features that need workflow metadata fixes"
    echo "4. Begin using the new workflow for future features"
}

# Help function
usage() {
    cat << EOF
Feature Migration Script

Migrates existing features from flat structure to workflow-based structure.

Usage:
    $0                  # Run full migration
    $0 --help          # Show this help
    $0 --dry-run       # Show what would be migrated (not implemented)

The script will:
1. Create a backup of existing features
2. Analyze each feature to determine appropriate workflow state
3. Move features to appropriate state directories
4. Add required workflow metadata
5. Validate migrated features
6. Generate a post-migration report

Workflow states:
- ideas/        - Basic feature concepts
- proposed/     - Detailed specifications
- validated/    - Verified and feasible
- accepted/     - Approved for development
- implemented/  - Completed features
- archived/     - Rejected/cancelled features

EOF
}

# Parse command line arguments
if [[ $# -gt 0 ]]; then
    case "$1" in
        "--help"|"-h")
            usage
            exit 0
            ;;
        "--dry-run")
            log_info "Dry run mode not yet implemented"
            exit 1
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
fi

# Execute main function
main