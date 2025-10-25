#!/bin/bash

# Architecture Health Validation Script
# Monitors and validates AIPM architecture health score against 95/100 target
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

# Architecture health metrics
calculate_architecture_health() {
    log_info "Calculating architecture health metrics..."

    local total_score=0
    local max_score=100

    # 1. Service Interface Compliance (15 points)
    log_info "Checking service interface compliance..."
    local interface_score=0

    # Check for CoreServiceInterface implementations in the correct location
    if [ -f "$AIPM_CLI_ROOT/aipm_cli/services/interfaces.py" ]; then
        # Count main service files that implement CoreServiceInterface or other ServiceInterface derivatives
        local main_service_files=(
            "$AIPM_CLI_ROOT/aipm_cli/services/database/service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/management/service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/projects/service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/workflow/service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/agent_management/agent_service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/context/service.py"
            "$AIPM_CLI_ROOT/aipm_cli/services/quality/service.py"
        )

        local compliant_services=0
        local total_services=${#main_service_files[@]}

        for service_file in "${main_service_files[@]}"; do
            if [ -f "$service_file" ] && grep -q "ServiceInterface" "$service_file"; then
                compliant_services=$((compliant_services + 1))
                log_info "  ✅ $(basename "$(dirname "$service_file")"): Interface compliant"
            elif [ -f "$service_file" ]; then
                log_warning "  ❌ $(basename "$(dirname "$service_file")"): Missing interface compliance"
            fi
        done

        if [ $total_services -gt 0 ]; then
            interface_score=$((compliant_services * 15 / total_services))
        fi

        log_info "  Interface compliance: $compliant_services/$total_services services"
    else
        log_error "  ServiceInterface definitions not found"
    fi

    total_score=$((total_score + interface_score))
    log_info "Service interface compliance: $interface_score/15"

    # 2. Code Organization Score (20 points)
    log_info "Checking code organization..."
    local org_score=0

    # Check for proper module structure
    if [ -d "$AIPM_CLI_ROOT/aipm_cli/services" ] &&
       [ -d "$AIPM_CLI_ROOT/aipm_cli/adapters" ] &&
       [ -d "$AIPM_CLI_ROOT/aipm_cli/orchestrator" ]; then
        org_score=$((org_score + 10))
    fi

    # Check for proper separation of concerns
    local cli_files=$(find "$AIPM_CLI_ROOT/aipm_cli/adapters/cli" -name "*.py" | wc -l)
    local service_files=$(find "$AIPM_CLI_ROOT/aipm_cli/services" -name "*.py" | wc -l)

    if [ $cli_files -ge 3 ] && [ $service_files -ge 5 ]; then
        org_score=$((org_score + 10))
    fi

    total_score=$((total_score + org_score))
    log_info "Code organization: $org_score/20"

    # 3. Test Coverage Score (20 points)
    log_info "Checking test coverage..."
    local test_score=0

    # Count test files vs source files
    local test_files=$(find "$AIPM_CLI_ROOT/tests" -name "test_*.py" 2>/dev/null | wc -l || echo 0)
    local source_files=$(find "$AIPM_CLI_ROOT/aipm_cli" -name "*.py" | grep -v __pycache__ | wc -l)

    if [ $source_files -gt 0 ]; then
        local coverage_ratio=$((test_files * 100 / source_files))
        if [ $coverage_ratio -ge 90 ]; then
            test_score=20
        elif [ $coverage_ratio -ge 70 ]; then
            test_score=15
        elif [ $coverage_ratio -ge 50 ]; then
            test_score=10
        elif [ $coverage_ratio -ge 30 ]; then
            test_score=5
        fi
    fi

    total_score=$((total_score + test_score))
    log_info "Test coverage: $test_score/20 (test files: $test_files, source files: $source_files)"

    # 4. Code Duplication Score (15 points)
    log_info "Checking code duplication..."
    local dup_score=0

    # Calculate duplication ratio
    local total_lines=$(find "$AIPM_CLI_ROOT/aipm_cli" -name "*.py" -exec wc -l {} \; | awk '{sum += $1} END {print sum}' || echo 1000)
    local duplicate_lines=$("$SCRIPT_DIR/validate_service_duplication.sh" get-ratio 2>/dev/null || echo 50)

    # Convert duplication percentage to score (lower is better)
    if [ $duplicate_lines -le 5 ]; then
        dup_score=15
    elif [ $duplicate_lines -le 10 ]; then
        dup_score=12
    elif [ $duplicate_lines -le 15 ]; then
        dup_score=8
    elif [ $duplicate_lines -le 20 ]; then
        dup_score=4
    fi

    total_score=$((total_score + dup_score))
    log_info "Code duplication: $dup_score/15 (duplication ratio: ${duplicate_lines}%)"

    # 5. Performance Score (15 points)
    log_info "Checking performance metrics..."
    local perf_score=0

    # Test CLI performance
    local cli_time=$("$SCRIPT_DIR/validate_cli_performance.sh" measure 2>/dev/null || echo 300)

    if [ $cli_time -le 200 ]; then
        perf_score=15
    elif [ $cli_time -le 300 ]; then
        perf_score=12
    elif [ $cli_time -le 500 ]; then
        perf_score=8
    elif [ $cli_time -le 1000 ]; then
        perf_score=4
    fi

    total_score=$((total_score + perf_score))
    log_info "Performance: $perf_score/15 (CLI response: ${cli_time}ms)"

    # 6. Security Score (15 points)
    log_info "Checking security compliance..."
    local sec_score=0

    # Check for security module
    if [ -d "$AIPM_CLI_ROOT/aipm_cli/security" ]; then
        sec_score=$((sec_score + 5))
    fi

    # Check for input validation
    if [ -f "$AIPM_CLI_ROOT/aipm_cli/security/input_validator.py" ]; then
        sec_score=$((sec_score + 5))
    fi

    # Check for output sanitization
    if [ -f "$AIPM_CLI_ROOT/aipm_cli/security/output_sanitizer.py" ]; then
        sec_score=$((sec_score + 5))
    fi

    total_score=$((total_score + sec_score))
    log_info "Security: $sec_score/15"

    echo $total_score
}

# Generate architecture health report
generate_health_report() {
    local score=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/architecture_health_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# AIPM Architecture Health Report

**Generated**: $timestamp
**Score**: $score/100
**Status**: $([ $score -ge 95 ] && echo "EXCELLENT" || ([ $score -ge 80 ] && echo "GOOD" || ([ $score -ge 60 ] && echo "FAIR" || echo "NEEDS IMPROVEMENT")))

## Health Metrics

### Overall Architecture Health: $score/100

$([ $score -ge 95 ] && echo "✅ **EXCELLENT** - Architecture meets production standards" || echo "⚠️  **NEEDS ATTENTION** - Architecture below 95/100 target")

### Detailed Breakdown

- **Service Interface Compliance**: Evaluated based on CoreServiceInterface adoption
- **Code Organization**: Assessed module structure and separation of concerns
- **Test Coverage**: Measured test-to-source file ratio and coverage depth
- **Code Duplication**: Analyzed duplicate code patterns and DRY compliance
- **Performance**: CLI response time and system efficiency metrics
- **Security**: Security module implementation and vulnerability protection

### Recommendations

$([ $score -lt 95 ] && cat << 'RECOMMENDATIONS'
#### Priority Actions Required

1. **Service Interface Standardization**
   - Ensure all services implement CoreServiceInterface
   - Standardize service method signatures and return types

2. **Test Coverage Enhancement**
   - Target >90% test coverage for all new code
   - Implement integration tests for critical workflows

3. **Performance Optimization**
   - Maintain CLI response times <200ms
   - Optimize service coordination overhead

4. **Code Quality Improvement**
   - Reduce code duplication to <5%
   - Implement automated quality gates

RECOMMENDATIONS
)

## Compliance Status

- **CI-001**: Agent-first workflow compliance
- **CI-002**: Quality context standards
- **CI-003**: Framework agnosticism
- **CI-004**: Test coverage requirements
- **CI-005**: Security standards
- **CI-006**: Documentation completeness

---
*Generated by AIPM Architecture Health Validator*
EOF

    echo "$report_file"
}

# Validate architecture health against target
validate_health() {
    local target_score=${1:-95}

    log_info "Starting architecture health validation..."
    log_info "Target score: $target_score/100"
    echo

    local current_score=$(calculate_architecture_health)

    echo
    log_info "Architecture health calculation complete"
    log_info "Current score: $current_score/100"

    # Generate detailed report
    local report_file=$(generate_health_report $current_score)
    log_info "Detailed report generated: $report_file"

    echo
    echo "========================================"
    echo "ARCHITECTURE HEALTH VALIDATION RESULTS"
    echo "========================================"
    echo "Score: $current_score/100"
    echo "Target: $target_score/100"
    echo

    if [ $current_score -ge $target_score ]; then
        log_success "✅ VALIDATION PASSED - Architecture health meets target ($current_score >= $target_score)"
        echo
        echo "Architecture is production-ready and maintains required quality standards."
        return 0
    else
        log_error "❌ VALIDATION FAILED - Architecture health below target ($current_score < $target_score)"
        echo
        echo "Architecture requires improvement to meet production standards."
        echo "Review the detailed report for specific recommendations: $report_file"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-validate}" in
        "calculate")
            calculate_architecture_health
            ;;
        "report")
            local score=$(calculate_architecture_health)
            generate_health_report $score
            ;;
        "validate")
            validate_health ${2:-95}
            ;;
        *)
            echo "Usage: $0 [calculate|report|validate] [target_score]"
            echo ""
            echo "Commands:"
            echo "  calculate  - Calculate current architecture health score"
            echo "  report     - Generate detailed health report"
            echo "  validate   - Validate against target score (default: 95)"
            echo ""
            echo "Examples:"
            echo "  $0 validate 95    # Validate against 95/100 target"
            echo "  $0 calculate      # Get current score only"
            echo "  $0 report         # Generate detailed report"
            exit 1
            ;;
    esac
}

main "$@"