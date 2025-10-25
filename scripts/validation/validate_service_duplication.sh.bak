#!/bin/bash

# Service Duplication Validation Script
# Monitors code duplication ratio and prevents service duplication regression
# Part of Track 3: Validation Pipeline Setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AIPM_CLI_ROOT="$PROJECT_ROOT/aipm-cli"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Duplication thresholds
MAX_DUPLICATION_RATIO=5  # Maximum 5% duplication allowed
WARNING_DUPLICATION_RATIO=3  # Warning at 3% duplication

# Calculate code duplication ratio
calculate_duplication_ratio() {
    log_info "Calculating code duplication ratio..."

    local temp_file="/tmp/aipm_duplication_analysis.txt"
    local duplicate_lines=0
    local total_lines=0

    # Get all Python files
    local python_files=$(find "$AIPM_CLI_ROOT" -name "*.py" -not -path "*/tests/*" -not -path "*/__pycache__/*")

    if [ -z "$python_files" ]; then
        log_error "No Python files found for analysis"
        echo "0"
        return 1
    fi

    # Count total lines
    total_lines=$(echo "$python_files" | xargs wc -l | tail -1 | awk '{print $1}')

    log_info "Analyzing $total_lines lines of code..."

    # Create temporary file with all code
    : > "$temp_file"
    for file in $python_files; do
        echo "# FILE: $file" >> "$temp_file"
        cat "$file" >> "$temp_file"
        echo "" >> "$temp_file"
    done

    # Look for duplicate patterns (excluding comments and empty lines)
    local code_patterns=$(grep -v "^\s*#" "$temp_file" | grep -v "^\s*$" | sort | uniq -d)

    if [ -n "$code_patterns" ]; then
        # Count duplicated lines
        duplicate_lines=$(echo "$code_patterns" | wc -l)
    fi

    # Clean up
    rm -f "$temp_file"

    # Calculate percentage
    local duplication_ratio=0
    if [ $total_lines -gt 0 ]; then
        duplication_ratio=$((duplicate_lines * 100 / total_lines))
    fi

    log_info "Duplicate lines: $duplicate_lines"
    log_info "Total lines: $total_lines"
    log_info "Duplication ratio: ${duplication_ratio}%"

    echo "$duplication_ratio"
}

# Detect duplicate services
detect_duplicate_services() {
    log_info "Detecting duplicate services..."

    local services_dir="$AIPM_CLI_ROOT/aipm_cli/services"
    local duplicates_found=0

    if [ ! -d "$services_dir" ]; then
        log_error "Services directory not found: $services_dir"
        return 1
    fi

    # Find service files
    local service_files=$(find "$services_dir" -name "service.py" -o -name "*_service.py")

    if [ -z "$service_files" ]; then
        log_warning "No service files found"
        return 0
    fi

    log_info "Analyzing service files for duplicates..."

    # Create signature map for services
    local temp_signatures="/tmp/aipm_service_signatures.txt"
    : > "$temp_signatures"

    for service_file in $service_files; do
        local service_name=$(basename "$(dirname "$service_file")")

        # Extract method signatures
        local methods=$(grep -n "def " "$service_file" | grep -v "__init__" | awk '{print $2}' | cut -d'(' -f1)

        if [ -n "$methods" ]; then
            for method in $methods; do
                echo "$method:$service_name" >> "$temp_signatures"
            done
        fi
    done

    # Find duplicate method signatures
    local duplicate_methods=$(cut -d':' -f1 "$temp_signatures" | sort | uniq -d)

    if [ -n "$duplicate_methods" ]; then
        log_warning "Duplicate method signatures found:"

        for method in $duplicate_methods; do
            local services_with_method=$(grep "^$method:" "$temp_signatures" | cut -d':' -f2 | tr '\n' ' ')
            log_warning "  $method: $services_with_method"
            duplicates_found=$((duplicates_found + 1))
        done
    else
        log_success "No duplicate service methods detected"
    fi

    # Clean up
    rm -f "$temp_signatures"

    return $duplicates_found
}

# Detect duplicate CLI commands
detect_duplicate_commands() {
    log_info "Detecting duplicate CLI commands..."

    local cli_dir="$AIPM_CLI_ROOT/aipm_cli/adapters/cli"
    local duplicates_found=0

    if [ ! -d "$cli_dir" ]; then
        log_error "CLI directory not found: $cli_dir"
        return 1
    fi

    # Find CLI command files
    local cli_files=$(find "$cli_dir" -name "*.py" -not -name "__init__.py")

    if [ -z "$cli_files" ]; then
        log_warning "No CLI command files found"
        return 0
    fi

    log_info "Analyzing CLI commands for duplicates..."

    # Extract command names
    local temp_commands="/tmp/aipm_cli_commands.txt"
    : > "$temp_commands"

    for cli_file in $cli_files; do
        local commands
        commands=$(grep -n "@.*\.command" "$cli_file" | sed 's/.*@.*\.command.*['"'"'"]//g' | sed 's/['"'"'"].*//g')

        if [ -n "$commands" ]; then
            for command in $commands; do
                echo "$command:$(basename "$cli_file")" >> "$temp_commands"
            done
        fi
    done

    # Find duplicate commands
    local duplicate_commands=$(cut -d':' -f1 "$temp_commands" | sort | uniq -d)

    if [ -n "$duplicate_commands" ]; then
        log_warning "Duplicate CLI commands found:"

        for command in $duplicate_commands; do
            local files_with_command=$(grep "^$command:" "$temp_commands" | cut -d':' -f2 | tr '\n' ' ')
            log_warning "  $command: $files_with_command"
            duplicates_found=$((duplicates_found + 1))
        done
    else
        log_success "No duplicate CLI commands detected"
    fi

    # Clean up
    rm -f "$temp_commands"

    return $duplicates_found
}

# Analyze code complexity and maintainability
analyze_code_complexity() {
    log_info "Analyzing code complexity..."

    local python_files=$(find "$AIPM_CLI_ROOT" -name "*.py" -not -path "*/tests/*" -not -path "*/__pycache__/*")
    local high_complexity_files=0

    for file in $python_files; do
        # Count lines per function (simple complexity metric)
        local functions=$(grep -n "^def " "$file" | wc -l)
        local total_lines=$(wc -l < "$file")

        if [ $functions -gt 0 ]; then
            local avg_lines_per_function=$((total_lines / functions))

            if [ $avg_lines_per_function -gt 50 ]; then
                log_warning "High complexity file: $(basename "$file") (avg $avg_lines_per_function lines/function)"
                high_complexity_files=$((high_complexity_files + 1))
            fi
        fi
    done

    if [ $high_complexity_files -eq 0 ]; then
        log_success "No high complexity files detected"
    else
        log_warning "Found $high_complexity_files high complexity files"
    fi

    return $high_complexity_files
}

# Generate duplication report
generate_duplication_report() {
    local duplication_ratio=$1
    local service_duplicates=$2
    local command_duplicates=$3
    local complexity_issues=$4
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file
    report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/duplication_analysis_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# AIPM Code Duplication Analysis Report

**Generated**: $timestamp
**Duplication Ratio**: ${duplication_ratio}%
**Status**: $([ $duplication_ratio -le $MAX_DUPLICATION_RATIO ] && echo "COMPLIANT" || echo "EXCEEDS THRESHOLD")

## Duplication Analysis

### Overall Code Quality: $([ $duplication_ratio -le $WARNING_DUPLICATION_RATIO ] && echo "✅ EXCELLENT" || ([ $duplication_ratio -le $MAX_DUPLICATION_RATIO ] && echo "✅ ACCEPTABLE" || echo "❌ NEEDS IMPROVEMENT"))

### Metrics Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|---------|
| Code Duplication | ${duplication_ratio}% | ≤${MAX_DUPLICATION_RATIO}% | $([ $duplication_ratio -le $MAX_DUPLICATION_RATIO ] && echo "✅ PASS" || echo "❌ FAIL") |
| Service Duplicates | $service_duplicates | 0 | $([ $service_duplicates -eq 0 ] && echo "✅ PASS" || echo "⚠️ WARN") |
| Command Duplicates | $command_duplicates | 0 | $([ $command_duplicates -eq 0 ] && echo "✅ PASS" || echo "⚠️ WARN") |
| Complexity Issues | $complexity_issues | ≤5 | $([ $complexity_issues -le 5 ] && echo "✅ PASS" || echo "⚠️ WARN") |

### Detailed Findings

#### Code Duplication Analysis
- **Current Ratio**: ${duplication_ratio}% (Target: ≤${MAX_DUPLICATION_RATIO}%)
- **Assessment**: $([ $duplication_ratio -le $WARNING_DUPLICATION_RATIO ] && echo "Excellent - well below threshold" || ([ $duplication_ratio -le $MAX_DUPLICATION_RATIO ] && echo "Acceptable - within acceptable range" || echo "Concerning - exceeds maximum threshold"))

#### Service Architecture
- **Duplicate Services**: $service_duplicates detected
- **Architecture Health**: $([ $service_duplicates -eq 0 ] && echo "Clean service separation maintained" || echo "Service consolidation needed")

#### CLI Command Structure
- **Duplicate Commands**: $command_duplicates detected
- **Command Organization**: $([ $command_duplicates -eq 0 ] && echo "Well-organized command structure" || echo "Command consolidation recommended")

### Recommendations

$([ $duplication_ratio -gt $MAX_DUPLICATION_RATIO ] && cat << 'RECOMMENDATIONS'
#### Critical Actions Required

1. **Reduce Code Duplication**
   - Identify and extract common functionality
   - Create shared utility modules
   - Implement inheritance patterns where appropriate

2. **Service Consolidation**
   - Merge duplicate service implementations
   - Standardize service interfaces
   - Eliminate redundant functionality

3. **Quality Gates**
   - Implement pre-commit duplication checks
   - Add duplication monitoring to CI pipeline
   - Set up automated refactoring alerts

RECOMMENDATIONS
)

$([ $service_duplicates -gt 0 ] && cat << 'SERVICE_RECOMMENDATIONS'
#### Service Architecture Improvements

1. **Service Deduplication**
   - Review and merge duplicate service methods
   - Implement shared service base classes
   - Standardize service patterns

2. **Interface Standardization**
   - Adopt CoreServiceInterface consistently
   - Implement common service patterns
   - Reduce implementation variations

SERVICE_RECOMMENDATIONS
)

---
*Generated by AIPM Service Duplication Validator*
EOF

    echo "$report_file"
}

# Comprehensive duplication validation
validate_duplication() {
    local max_ratio=${1:-$MAX_DUPLICATION_RATIO}

    log_info "Starting comprehensive duplication validation..."
    log_info "Maximum duplication ratio: ${max_ratio}%"
    echo

    # Calculate overall duplication ratio
    local duplication_ratio=$(calculate_duplication_ratio)
    echo

    # Detect service duplicates
    detect_duplicate_services
    local service_duplicates=$?
    echo

    # Detect command duplicates
    detect_duplicate_commands
    local command_duplicates=$?
    echo

    # Analyze code complexity
    analyze_code_complexity
    local complexity_issues=$?
    echo

    # Generate detailed report
    local report_file=$(generate_duplication_report $duplication_ratio $service_duplicates $command_duplicates $complexity_issues)
    log_info "Detailed report generated: $report_file"

    echo
    echo "========================================"
    echo "DUPLICATION VALIDATION RESULTS"
    echo "========================================"
    echo "Code duplication ratio: ${duplication_ratio}%"
    echo "Service duplicates: $service_duplicates"
    echo "Command duplicates: $command_duplicates"
    echo "Complexity issues: $complexity_issues"
    echo

    local validation_passed=true

    if [ $duplication_ratio -gt $max_ratio ]; then
        log_error "❌ Code duplication exceeds threshold (${duplication_ratio}% > ${max_ratio}%)"
        validation_passed=false
    else
        log_success "✅ Code duplication within threshold (${duplication_ratio}% ≤ ${max_ratio}%)"
    fi

    if [ $service_duplicates -gt 0 ]; then
        log_warning "⚠️ Service duplicates detected: $service_duplicates"
    else
        log_success "✅ No service duplicates found"
    fi

    if [ $command_duplicates -gt 0 ]; then
        log_warning "⚠️ Command duplicates detected: $command_duplicates"
    else
        log_success "✅ No command duplicates found"
    fi

    if $validation_passed; then
        log_success "✅ VALIDATION PASSED - Duplication levels acceptable"
        echo
        echo "Code quality meets production standards."
        return 0
    else
        log_error "❌ VALIDATION FAILED - Duplication exceeds acceptable levels"
        echo
        echo "Code refactoring required. Review report: $report_file"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-validate}" in
        "get-ratio")
            calculate_duplication_ratio
            ;;
        "services")
            detect_duplicate_services
            ;;
        "commands")
            detect_duplicate_commands
            ;;
        "complexity")
            analyze_code_complexity
            ;;
        "validate")
            validate_duplication ${2:-$MAX_DUPLICATION_RATIO}
            ;;
        *)
            echo "Usage: $0 [get-ratio|services|commands|complexity|validate] [max_ratio]"
            echo ""
            echo "Commands:"
            echo "  get-ratio    - Calculate current duplication ratio"
            echo "  services     - Detect duplicate services"
            echo "  commands     - Detect duplicate CLI commands"
            echo "  complexity   - Analyze code complexity issues"
            echo "  validate     - Run comprehensive duplication validation"
            echo ""
            echo "Examples:"
            echo "  $0 validate 5    # Validate against 5% duplication limit"
            echo "  $0 get-ratio     # Get current duplication percentage"
            exit 1
            ;;
    esac
}

main "$@"