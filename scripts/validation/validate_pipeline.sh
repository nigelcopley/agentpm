#!/bin/bash

# AIPM Validation Pipeline Master Script (Simplified)
# Orchestrates comprehensive validation for CLI_V1 compliance and production readiness
# Part of Track 3: Validation Pipeline Setup - Launch Readiness Program Week 1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${CYAN}${BOLD}$1${NC}"; }

# Validation targets and thresholds
ARCHITECTURE_HEALTH_TARGET=95
CLI_PERFORMANCE_TARGET=200  # milliseconds
DUPLICATION_RATIO_TARGET=5  # percentage

# Global results tracking
TOTAL_VALIDATIONS=0
PASSED_VALIDATIONS=0
FAILED_VALIDATIONS=0

# Quick validation check (subset for CI/CD)
run_quick_validation() {
    log_info "Running quick validation check..."

    local quick_failures=0

    # Quick CLI performance check (simple timing)
    log_info "Checking CLI performance..."
    # Use Python for cross-platform millisecond timing
    local start_time=$(python -c "import time; print(int(time.time() * 1000))")
    if cd "$PROJECT_ROOT" && apm --help >/dev/null 2>&1; then
        local end_time=$(python -c "import time; print(int(time.time() * 1000))")
        local cli_time=$((end_time - start_time))

        if [ $cli_time -le $CLI_PERFORMANCE_TARGET ]; then
            log_success "✅ CLI performance OK (${cli_time}ms ≤ ${CLI_PERFORMANCE_TARGET}ms)"
        else
            log_error "❌ CLI performance FAILED (${cli_time}ms > ${CLI_PERFORMANCE_TARGET}ms)"
            quick_failures=$((quick_failures + 1))
        fi
    else
        log_error "❌ CLI command failed"
        quick_failures=$((quick_failures + 1))
    fi

    # Quick syntax check
    log_info "Checking Python syntax..."
    if find "$PROJECT_ROOT/aipm-cli" -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null; then
        log_success "✅ Python syntax OK"
    else
        log_error "❌ Python syntax errors detected"
        quick_failures=$((quick_failures + 1))
    fi

    echo
    if [ $quick_failures -eq 0 ]; then
        log_success "✅ Quick validation PASSED"
        return 0
    else
        log_error "❌ Quick validation FAILED ($quick_failures issues)"
        return 1
    fi
}

# Pre-commit validation (lightweight checks)
run_precommit_validation() {
    log_info "Running pre-commit validation..."

    local precommit_failures=0

    # Basic syntax check
    if find "$PROJECT_ROOT/aipm-cli" -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null; then
        log_success "✅ Python syntax OK"
    else
        log_error "❌ Python syntax errors detected"
        precommit_failures=$((precommit_failures + 1))
    fi

    # Basic import check
    if cd "$PROJECT_ROOT/aipm-cli" && python3 -c "import aipm_cli" 2>/dev/null; then
        log_success "✅ Imports OK"
    else
        log_error "❌ Import errors detected"
        precommit_failures=$((precommit_failures + 1))
    fi

    echo
    if [ $precommit_failures -eq 0 ]; then
        log_success "✅ Pre-commit validation PASSED"
        return 0
    else
        log_error "❌ Pre-commit validation FAILED ($precommit_failures issues)"
        return 1
    fi
}

# Run individual validation
run_individual_validation() {
    local validation_type="$1"
    local script_name="$2"
    local args="${3:-validate}"

    log_header "═══════════════════════════════════════════════════════════════"
    log_header "$(echo $validation_type | tr '[:lower:]' '[:upper:]') VALIDATION"
    log_header "═══════════════════════════════════════════════════════════════"

    TOTAL_VALIDATIONS=$((TOTAL_VALIDATIONS + 1))

    if [ ! -f "$SCRIPT_DIR/$script_name" ]; then
        log_error "$validation_type validator not found: $script_name"
        FAILED_VALIDATIONS=$((FAILED_VALIDATIONS + 1))
        return 1
    fi

    local start_time=$(date +%s)

    if "$SCRIPT_DIR/$script_name" $args; then
        log_success "$validation_type validation PASSED"
        PASSED_VALIDATIONS=$((PASSED_VALIDATIONS + 1))
        local result=0
    else
        log_error "$validation_type validation FAILED"
        FAILED_VALIDATIONS=$((FAILED_VALIDATIONS + 1))
        local result=1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "$validation_type validation completed in ${duration}s"

    echo
    return $result
}

# Generate simple validation report
generate_simple_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/validation_pipeline_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    local overall_status="FAILED"
    if [ $PASSED_VALIDATIONS -eq $TOTAL_VALIDATIONS ]; then
        overall_status="PASSED"
    fi

    cat > "$report_file" << EOF
# AIPM Validation Pipeline Report

**Generated**: $timestamp
**Overall Status**: $overall_status
**CLI_V1 Compliance**: $([ "$overall_status" = "PASSED" ] && echo "✅ ACHIEVED" || echo "❌ NOT ACHIEVED")

## Summary

- **Total Validations**: $TOTAL_VALIDATIONS
- **Passed**: $PASSED_VALIDATIONS
- **Failed**: $FAILED_VALIDATIONS

### Production Readiness

$([ "$overall_status" = "PASSED" ] && cat << 'READY'
✅ **PRODUCTION READY**

All validation gates satisfied. System ready for production deployment.
READY
)

$([ "$overall_status" != "PASSED" ] && cat << 'NOT_READY'
❌ **NOT PRODUCTION READY**

$FAILED_VALIDATIONS validation(s) failed. Remediation required before deployment.
NOT_READY
)

---
*Generated by AIPM Validation Pipeline*
EOF

    echo "$report_file"
}

# Display simple validation dashboard
display_simple_dashboard() {
    echo
    log_header "════════════════════════════════════════════════════════════════════════════════"
    log_header "                        AIPM VALIDATION PIPELINE DASHBOARD"
    log_header "                         CLI_V1 COMPLIANCE & PRODUCTION READINESS"
    log_header "════════════════════════════════════════════════════════════════════════════════"
    echo

    local overall_status="FAILED"
    local status_color=$RED
    if [ $PASSED_VALIDATIONS -eq $TOTAL_VALIDATIONS ]; then
        overall_status="PASSED"
        status_color=$GREEN
    fi

    echo -e "${BOLD}OVERALL STATUS: ${status_color}$overall_status${NC} ($PASSED_VALIDATIONS/$TOTAL_VALIDATIONS validations passed)"
    echo

    if [ "$overall_status" = "PASSED" ]; then
        echo -e "${GREEN}${BOLD}🎉 CLI_V1 COMPLIANCE ACHIEVED - PRODUCTION READY${NC}"
        echo -e "${GREEN}   All validation gates satisfied. System ready for production deployment.${NC}"
    else
        echo -e "${RED}${BOLD}🚨 CLI_V1 COMPLIANCE NOT ACHIEVED - PRODUCTION BLOCKED${NC}"
        echo -e "${RED}   $FAILED_VALIDATIONS validation(s) failed. Remediation required before deployment.${NC}"
    fi

    echo
}

# Comprehensive validation pipeline execution
run_validation_pipeline() {
    local pipeline_start_time=$(date +%s)

    log_header "🚀 STARTING AIPM VALIDATION PIPELINE"
    log_header "Track 3: Validation Pipeline Setup - Launch Readiness Program Week 1"
    echo

    # Initialize tracking
    TOTAL_VALIDATIONS=0
    PASSED_VALIDATIONS=0
    FAILED_VALIDATIONS=0

    # Run all validations
    run_individual_validation "Architecture Health" "validate_architecture_health.sh" "validate $ARCHITECTURE_HEALTH_TARGET"
    run_individual_validation "CLI Performance" "validate_cli_performance.sh" "validate $CLI_PERFORMANCE_TARGET"
    run_individual_validation "Security Compliance" "validate_security_compliance.sh" "validate"
    run_individual_validation "Service Duplication" "validate_service_duplication.sh" "validate $DUPLICATION_RATIO_TARGET"
    run_individual_validation "Compliance Gates" "validate_compliance_gates.sh" "validate"

    # Generate report
    local report_file=$(generate_simple_report)

    # Display dashboard
    display_simple_dashboard

    local pipeline_end_time=$(date +%s)
    local total_duration=$((pipeline_end_time - pipeline_start_time))

    echo
    log_info "Comprehensive validation report: $report_file"
    log_info "Total validation pipeline duration: ${total_duration}s"
    echo

    if [ $FAILED_VALIDATIONS -eq 0 ]; then
        log_success "🎉 ALL VALIDATIONS PASSED - CLI_V1 COMPLIANCE ACHIEVED"
        return 0
    else
        log_error "❌ $FAILED_VALIDATIONS VALIDATION(S) FAILED - CLI_V1 COMPLIANCE NOT ACHIEVED"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-full}" in
        "full"|"pipeline")
            run_validation_pipeline
            ;;
        "quick")
            run_quick_validation
            ;;
        "precommit"|"pre-commit")
            run_precommit_validation
            ;;
        "architecture")
            run_individual_validation "Architecture Health" "validate_architecture_health.sh" "validate"
            ;;
        "performance")
            run_individual_validation "CLI Performance" "validate_cli_performance.sh" "validate"
            ;;
        "security")
            run_individual_validation "Security Compliance" "validate_security_compliance.sh" "validate"
            ;;
        "duplication")
            run_individual_validation "Service Duplication" "validate_service_duplication.sh" "validate"
            ;;
        "compliance")
            run_individual_validation "Compliance Gates" "validate_compliance_gates.sh" "validate"
            ;;
        *)
            echo "Usage: $0 [full|quick|precommit|architecture|performance|security|duplication|compliance]"
            echo ""
            echo "Validation Modes:"
            echo "  full         - Complete validation pipeline (default)"
            echo "  quick        - Fast validation for CI/CD"
            echo "  precommit    - Lightweight pre-commit checks"
            echo ""
            echo "Individual Validations:"
            echo "  architecture - Architecture health validation"
            echo "  performance  - CLI performance validation"
            echo "  security     - Security compliance validation"
            echo "  duplication  - Code duplication validation"
            echo "  compliance   - Compliance gates validation"
            echo ""
            echo "Examples:"
            echo "  $0 full        # Run complete validation pipeline"
            echo "  $0 quick       # Quick validation check"
            echo "  $0 precommit   # Pre-commit validation"
            echo "  $0 performance # CLI performance only"
            exit 1
            ;;
    esac
}

main "$@"