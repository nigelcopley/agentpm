#!/bin/bash

# CLI Performance Validation Script
# Monitors and validates AIPM CLI response times against <200ms requirement
# Part of Track 3: Validation Pipeline Setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# Performance targets (in milliseconds)
TARGET_HELP_TIME=200
TARGET_STATUS_TIME=200
TARGET_LIST_TIME=200
WARNING_THRESHOLD=150

# Cross-platform timing function
get_time_ms() {
    if command -v python3 >/dev/null 2>&1; then
        # Use Python for cross-platform millisecond precision
        python3 -c "import time; print(int(time.time() * 1000))"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux systems support %3N
        date +%s%3N
    elif command -v gdate >/dev/null 2>&1; then
        # macOS with GNU coreutils installed
        gdate +%s%3N
    else
        # Fallback: use seconds * 1000 for millisecond approximation
        echo $(($(date +%s) * 1000))
    fi
}

# Test CLI commands and measure response times
measure_cli_performance() {
    local command="$1"
    local iterations=${2:-3}

    log_info "Measuring performance for: apm $command"

    local total_time=0
    local min_time=999999
    local max_time=0

    for i in $(seq 1 $iterations); do
        # Measure command execution time in milliseconds
        local start_time=$(get_time_ms)

        if [ "$command" = "--help" ]; then
            apm --help >/dev/null 2>&1
        elif [ "$command" = "status" ]; then
            apm status >/dev/null 2>&1
        elif [ "$command" = "agents list" ]; then
            apm agents list >/dev/null 2>&1
        elif [ "$command" = "objectives list" ]; then
            apm objectives list >/dev/null 2>&1
        elif [ "$command" = "task list" ]; then
            apm task list >/dev/null 2>&1
        else
            log_error "Unknown command: $command"
            return 1
        fi

        local end_time=$(get_time_ms)
        local execution_time=$((end_time - start_time))

        total_time=$((total_time + execution_time))

        if [ $execution_time -lt $min_time ]; then
            min_time=$execution_time
        fi

        if [ $execution_time -gt $max_time ]; then
            max_time=$execution_time
        fi

        echo "  Iteration $i: ${execution_time}ms" >&2
    done

    local avg_time=$((total_time / iterations))

    echo "RESULTS:$command:$avg_time:$min_time:$max_time"
    return 0
}

# Comprehensive CLI performance testing
run_performance_tests() {
    log_info "Starting comprehensive CLI performance testing..."
    echo

    local commands=(
        "--help"
        "status"
        "agents list"
        "objectives list"
        "task list"
    )

    local results_file="/tmp/aipm_performance_results.txt"
    : > "$results_file"

    local total_tests=0
    local passed_tests=0
    local failed_tests=0

    for command in "${commands[@]}"; do
        total_tests=$((total_tests + 1))

        log_info "Testing command: apm $command"

        # Measure performance - capture only the RESULTS line
        local result=$(measure_cli_performance "$command" 3 2>/dev/null | grep "^RESULTS:")
        echo "$result" >> "$results_file"

        # Parse results
        local avg_time=$(echo "$result" | cut -d: -f3)
        local min_time=$(echo "$result" | cut -d: -f4)
        local max_time=$(echo "$result" | cut -d: -f5)

        # Determine target based on command
        local target_time=$TARGET_HELP_TIME
        case "$command" in
            "status") target_time=$TARGET_STATUS_TIME ;;
            "agents list"|"objectives list"|"task list") target_time=$TARGET_LIST_TIME ;;
        esac

        log_info "  Average: ${avg_time}ms | Min: ${min_time}ms | Max: ${max_time}ms | Target: ${target_time}ms"

        # Validate against target
        if [ $avg_time -le $target_time ]; then
            if [ $avg_time -le $WARNING_THRESHOLD ]; then
                log_success "  ✅ EXCELLENT - Well below target"
            else
                log_success "  ✅ PASSED - Within target"
            fi
            passed_tests=$((passed_tests + 1))
        else
            log_error "  ❌ FAILED - Exceeds target (${avg_time}ms > ${target_time}ms)"
            failed_tests=$((failed_tests + 1))
        fi

        echo
    done

    echo "$results_file"
}

# Generate performance report
generate_performance_report() {
    local results_file="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/cli_performance_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# AIPM CLI Performance Report

**Generated**: $timestamp
**Test Results**: $(basename "$results_file")

## Performance Metrics

### CLI Response Time Requirements
- **Target**: <200ms for all commands
- **Warning Threshold**: >150ms
- **Critical Threshold**: >200ms

### Test Results

| Command | Average (ms) | Min (ms) | Max (ms) | Target (ms) | Status |
|---------|--------------|----------|----------|-------------|---------|
EOF

    # Process results and add to report
    while IFS=: read -r prefix command avg min max; do
        if [ "$prefix" = "RESULTS" ]; then
            local status="✅ PASS"
            local target=200

            case "$command" in
                "--help"|"status"|"agents list"|"objectives list"|"task list")
                    target=200
                    ;;
            esac

            if [ "$avg" -gt "$target" ]; then
                status="❌ FAIL"
            elif [ "$avg" -gt "$WARNING_THRESHOLD" ]; then
                status="⚠️ WARN"
            fi

            echo "| apm $command | $avg | $min | $max | $target | $status |" >> "$report_file"
        fi
    done < "$results_file"

    cat >> "$report_file" << EOF

### Performance Analysis

#### Response Time Distribution
- Commands meeting target (<200ms): $(grep "✅" "$report_file" | wc -l)
- Commands with warnings (150-200ms): $(grep "⚠️" "$report_file" | wc -l)
- Commands failing target (>200ms): $(grep "❌" "$report_file" | wc -l)

#### Key Findings
EOF

    # Add findings based on results
    local max_avg_time=$(grep "RESULTS:" "$results_file" | cut -d: -f3 | sort -n | tail -1)
    local min_avg_time=$(grep "RESULTS:" "$results_file" | cut -d: -f3 | sort -n | head -1)

    cat >> "$report_file" << EOF

- **Fastest Command**: ${min_avg_time}ms average response time
- **Slowest Command**: ${max_avg_time}ms average response time
- **Performance Consistency**: $([ $((max_avg_time - min_avg_time)) -lt 50 ] && echo "Good - low variance between commands" || echo "Variable - some commands significantly slower")

### Recommendations

$([ $max_avg_time -gt 200 ] && cat << 'RECOMMENDATIONS'
#### Performance Optimization Required

1. **Identify Bottlenecks**
   - Profile slow commands to identify performance issues
   - Check database query efficiency
   - Review service initialization overhead

2. **Optimization Strategies**
   - Implement command-level caching
   - Optimize database connections
   - Reduce import overhead
   - Implement lazy loading for heavy services

3. **Monitoring**
   - Set up continuous performance monitoring
   - Implement performance regression testing
   - Add performance alerts for CI/CD pipeline

RECOMMENDATIONS
)

---
*Generated by AIPM CLI Performance Validator*
EOF

    echo "$report_file"
}

# Validate CLI performance against targets
validate_performance() {
    local target_time=${1:-200}

    log_info "Starting CLI performance validation..."
    log_info "Target response time: ${target_time}ms"
    echo

    # Run comprehensive tests-BAK
    local results_file=$(run_performance_tests)

    # Generate detailed report
    local report_file=$(generate_performance_report "$results_file")
    log_info "Detailed report generated: $report_file"

    echo
    echo "========================================"
    echo "CLI PERFORMANCE VALIDATION RESULTS"
    echo "========================================"

    # Analyze results
    local total_commands=0
    local passed_commands=0
    local max_time=0

    while IFS=: read -r prefix command avg min max_result; do
        if [ "$prefix" = "RESULTS" ]; then
            total_commands=$((total_commands + 1))

            if [ "$avg" -le "$target_time" ]; then
                passed_commands=$((passed_commands + 1))
            fi

            if [ "$avg" -gt "$max_time" ]; then
                max_time=$avg
            fi
        fi
    done < "$results_file"

    echo "Commands tested: $total_commands"
    echo "Commands passing: $passed_commands"
    echo "Commands failing: $((total_commands - passed_commands))"
    echo "Slowest command: ${max_time}ms"
    echo

    # Clean up temporary file
    rm -f "$results_file"

    if [ $passed_commands -eq $total_commands ]; then
        log_success "✅ VALIDATION PASSED - All commands meet performance targets"
        echo
        echo "CLI performance is optimal and meets production requirements."
        return 0
    else
        log_error "❌ VALIDATION FAILED - $((total_commands - passed_commands)) commands exceed target"
        echo
        echo "CLI performance requires optimization. Review report for details: $report_file"
        return 1
    fi
}

# Get single measurement for other scripts
measure_single() {
    local command="${1:---help}"
    local result=$(measure_cli_performance "$command" 1)
    echo "$result" | cut -d: -f3
}

# Main execution
main() {
    case "${1:-validate}" in
        "measure")
            measure_single "${2:---help}"
            ;;
        "test")
            run_performance_tests
            ;;
        "validate")
            validate_performance ${2:-200}
            ;;
        *)
            echo "Usage: $0 [measure|test|validate] [target_ms|command]"
            echo ""
            echo "Commands:"
            echo "  measure [command]  - Measure single command performance"
            echo "  test              - Run comprehensive performance tests"
            echo "  validate [target] - Validate against target time (default: 200ms)"
            echo ""
            echo "Examples:"
            echo "  $0 validate 200     # Validate all commands against 200ms"
            echo "  $0 measure status   # Measure 'apm status' performance"
            echo "  $0 test            # Run all performance tests"
            exit 1
            ;;
    esac
}

main "$@"