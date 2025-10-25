#!/bin/bash

# Security Compliance Validation Script
# Validates security patterns and prevents regression of security fixes
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

# Security validation patterns
validate_input_sanitization() {
    log_info "Validating input sanitization patterns..."

    local violations=0

    # Check for input validator usage
    if [ ! -f "$AIPM_CLI_ROOT/aipm_cli/security/input_validator.py" ]; then
        log_error "Missing input validator module"
        violations=$((violations + 1))
    else
        log_success "Input validator module exists"

        # Check for proper import usage
        local cli_files=$(find "$AIPM_CLI_ROOT/aipm_cli/adapters/cli" -name "*.py")
        local validator_usage=0

        for file in $cli_files; do
            if grep -q "input_validator" "$file" || grep -q "validate_input" "$file"; then
                validator_usage=$((validator_usage + 1))
            fi
        done

        if [ $validator_usage -gt 0 ]; then
            log_success "Input validation used in $validator_usage CLI files"
        else
            log_warning "Input validation not found in CLI files"
        fi
    fi

    # Check for dangerous patterns
    log_info "Checking for dangerous input patterns..."

    local dangerous_patterns=(
        "eval("
        "exec("
        "subprocess.call.*shell=True"
        "os.system("
        "__import__"
        "compile("
    )

    local dangerous_found=0

    for pattern in "${dangerous_patterns[@]}"; do
        local matches=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -l "$pattern" {} \; 2>/dev/null | wc -l)
        if [ $matches -gt 0 ]; then
            log_error "Dangerous pattern found: $pattern (in $matches files)"
            dangerous_found=$((dangerous_found + 1))
            violations=$((violations + 1))
        fi
    done

    if [ $dangerous_found -eq 0 ]; then
        log_success "No dangerous input patterns detected"
    fi

    return $violations
}

validate_output_sanitization() {
    log_info "Validating output sanitization patterns..."

    local violations=0

    # Check for output sanitizer
    if [ ! -f "$AIPM_CLI_ROOT/aipm_cli/security/output_sanitizer.py" ]; then
        log_error "Missing output sanitizer module"
        violations=$((violations + 1))
    else
        log_success "Output sanitizer module exists"

        # Check for sanitizer usage in CLI output
        local output_usage=$(find "$AIPM_CLI_ROOT/aipm_cli" -name "*.py" -exec grep -l "output_sanitizer\|sanitize_output" {} \; | wc -l)

        if [ $output_usage -gt 0 ]; then
            log_success "Output sanitization used in $output_usage files"
        else
            log_warning "Output sanitization usage not detected"
        fi
    fi

    # Check for potential information disclosure
    log_info "Checking for information disclosure risks..."

    local disclosure_patterns=(
        "print.*password"
        "print.*secret"
        "print.*token"
        "log.*password"
        "log.*secret"
        "log.*token"
    )

    local disclosure_found=0

    for pattern in "${disclosure_patterns[@]}"; do
        local matches=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -li "$pattern" {} \; 2>/dev/null | wc -l)
        if [ $matches -gt 0 ]; then
            log_warning "Potential information disclosure: $pattern (in $matches files)"
            disclosure_found=$((disclosure_found + 1))
        fi
    done

    if [ $disclosure_found -eq 0 ]; then
        log_success "No information disclosure patterns detected"
    fi

    return $violations
}

validate_command_security() {
    log_info "Validating command security patterns..."

    local violations=0

    # Check for command security module
    if [ ! -f "$AIPM_CLI_ROOT/aipm_cli/security/command_security.py" ]; then
        log_error "Missing command security module"
        violations=$((violations + 1))
    else
        log_success "Command security module exists"
    fi

    # Check for secure command execution patterns
    log_info "Checking command execution security..."

    local command_files=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -l "subprocess\|os.system\|commands" {} \; 2>/dev/null)

    if [ -n "$command_files" ]; then
        local secure_commands=0
        local total_commands=0

        for file in $command_files; do
            local cmd_count=$(grep -c "subprocess\|os.system\|commands" "$file" 2>/dev/null || echo 0)
            total_commands=$((total_commands + cmd_count))

            if grep -q "shell=False\|shell=None" "$file" || ! grep -q "shell=True" "$file"; then
                secure_commands=$((secure_commands + 1))
            fi
        done

        if [ $total_commands -gt 0 ]; then
            log_info "Command execution found in $total_commands locations"

            # Check for shell=True usage (security risk)
            local shell_true_count=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -c "shell=True" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')

            if [ $shell_true_count -gt 0 ]; then
                log_error "Found $shell_true_count instances of shell=True (security risk)"
                violations=$((violations + 1))
            else
                log_success "No shell=True usage detected"
            fi
        fi
    else
        log_info "No command execution patterns found"
    fi

    return $violations
}

validate_path_security() {
    log_info "Validating path traversal security..."

    local violations=0

    # Check for path traversal vulnerabilities
    local traversal_patterns=(
        "\.\.\/"
        "\.\./"
        "../"
        "..\\\\"
    )

    local traversal_found=0

    for pattern in "${traversal_patterns[@]}"; do
        local matches=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -l "$pattern" {} \; 2>/dev/null | wc -l)
        if [ $matches -gt 0 ]; then
            log_warning "Potential path traversal pattern: $pattern (in $matches files)"
            traversal_found=$((traversal_found + 1))
        fi
    done

    if [ $traversal_found -eq 0 ]; then
        log_success "No path traversal patterns detected"
    fi

    # Check for proper path validation
    local path_validation=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -l "os.path.abspath\|pathlib\|Path(" {} \; | wc -l)

    if [ $path_validation -gt 0 ]; then
        log_success "Path validation patterns found in $path_validation files"
    else
        log_warning "Limited path validation detected"
    fi

    return $violations
}

validate_database_security() {
    log_info "Validating database security patterns..."

    local violations=0

    # Check for SQL injection prevention
    local db_files=$(find "$AIPM_CLI_ROOT" -name "*.py" -path "*/database/*")

    if [ -n "$db_files" ]; then
        local parameterized_queries=0
        local total_queries=0

        for file in $db_files; do
            # Check for parameterized queries (good)
            local param_count=$(grep -c "?" "$file" 2>/dev/null || echo 0)
            parameterized_queries=$((parameterized_queries + param_count))

            # Check for string formatting in SQL (bad)
            local format_count=$(grep -c "\.format\|%" "$file" 2>/dev/null || echo 0)
            total_queries=$((total_queries + format_count))
        done

        if [ $total_queries -gt 0 ]; then
            log_warning "Found $total_queries potential string formatting in database files"
        else
            log_success "No SQL string formatting detected"
        fi

        if [ $parameterized_queries -gt 0 ]; then
            log_success "Found $parameterized_queries parameterized query patterns"
        fi
    else
        log_info "No database files found for security analysis"
    fi

    return $violations
}

# Generate security compliance report
generate_security_report() {
    local total_violations=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/security_compliance_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# AIPM Security Compliance Report

**Generated**: $timestamp
**Violations**: $total_violations
**Status**: $([ $total_violations -eq 0 ] && echo "SECURE" || echo "NEEDS ATTENTION")

## Security Assessment

### Overall Security Status: $([ $total_violations -eq 0 ] && echo "✅ COMPLIANT" || echo "⚠️ $total_violations VIOLATIONS")

### Security Modules Validation

#### Input Sanitization
- Input validator module implementation
- Dangerous pattern detection
- CLI input validation coverage

#### Output Sanitization
- Output sanitizer module implementation
- Information disclosure prevention
- Sensitive data handling

#### Command Security
- Command execution security patterns
- Shell injection prevention
- Subprocess security validation

#### Path Security
- Path traversal vulnerability prevention
- Path validation implementation
- Directory access controls

#### Database Security
- SQL injection prevention
- Parameterized query usage
- Database access security

### Security Recommendations

$([ $total_violations -gt 0 ] && cat << 'RECOMMENDATIONS'
#### Immediate Actions Required

1. **Critical Vulnerabilities**
   - Address all identified security violations
   - Implement missing security modules
   - Review and fix dangerous patterns

2. **Security Hardening**
   - Enhance input validation coverage
   - Implement comprehensive output sanitization
   - Add security testing to CI pipeline

3. **Ongoing Security**
   - Regular security audits
   - Dependency vulnerability scanning
   - Security-focused code reviews

RECOMMENDATIONS
)

### Compliance Checklist

- [ ] Input validation implemented
- [ ] Output sanitization active
- [ ] Command security enforced
- [ ] Path traversal protection
- [ ] Database security validated
- [ ] No critical vulnerabilities

---
*Generated by AIPM Security Compliance Validator*
EOF

    echo "$report_file"
}

# Comprehensive security validation
validate_security() {
    log_info "Starting comprehensive security validation..."
    echo

    local total_violations=0

    # Run all security validations
    validate_input_sanitization
    total_violations=$((total_violations + $?))
    echo

    validate_output_sanitization
    total_violations=$((total_violations + $?))
    echo

    validate_command_security
    total_violations=$((total_violations + $?))
    echo

    validate_path_security
    total_violations=$((total_violations + $?))
    echo

    validate_database_security
    total_violations=$((total_violations + $?))
    echo

    # Generate detailed report
    local report_file=$(generate_security_report $total_violations)
    log_info "Detailed report generated: $report_file"

    echo
    echo "========================================"
    echo "SECURITY COMPLIANCE VALIDATION RESULTS"
    echo "========================================"
    echo "Total violations: $total_violations"
    echo

    if [ $total_violations -eq 0 ]; then
        log_success "✅ VALIDATION PASSED - No security violations detected"
        echo
        echo "Security compliance meets production standards."
        return 0
    else
        log_error "❌ VALIDATION FAILED - $total_violations security violations found"
        echo
        echo "Security issues require immediate attention. Review report: $report_file"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-validate}" in
        "input")
            validate_input_sanitization
            ;;
        "output")
            validate_output_sanitization
            ;;
        "command")
            validate_command_security
            ;;
        "path")
            validate_path_security
            ;;
        "database")
            validate_database_security
            ;;
        "validate")
            validate_security
            ;;
        *)
            echo "Usage: $0 [input|output|command|path|database|validate]"
            echo ""
            echo "Commands:"
            echo "  input     - Validate input sanitization patterns"
            echo "  output    - Validate output sanitization patterns"
            echo "  command   - Validate command execution security"
            echo "  path      - Validate path traversal protection"
            echo "  database  - Validate database security patterns"
            echo "  validate  - Run comprehensive security validation"
            echo ""
            echo "Examples:"
            echo "  $0 validate   # Run all security validations"
            echo "  $0 input      # Check input sanitization only"
            exit 1
            ;;
    esac
}

main "$@"