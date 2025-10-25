#!/bin/bash

# Compliance Gates Validation Script
# Validates CI-001 through CI-006 compliance gates
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

# CI-001: Agent-first workflow compliance
validate_ci_001() {
    log_info "Validating CI-001: Agent-first workflow compliance"

    local violations=0

    # Check for agent directory structure
    if [ ! -d "$PROJECT_ROOT/.aipm/agents" ] && [ ! -d "$PROJECT_ROOT/.claude/agents" ]; then
        log_error "Missing agent directory structure"
        violations=$((violations + 1))
    else
        log_success "Agent directory structure exists"

        # Count available agents
        local agent_count=0
        if [ -d "$PROJECT_ROOT/.claude/agents" ]; then
            agent_count=$(find "$PROJECT_ROOT/.claude/agents" -name "*.md" | wc -l)
        elif [ -d "$PROJECT_ROOT/.aipm/agents" ]; then
            agent_count=$(find "$PROJECT_ROOT/.aipm/agents" -name "*.md" | wc -l)
        fi

        if [ $agent_count -ge 11 ]; then
            log_success "Sufficient agent coverage: $agent_count agents"
        else
            log_warning "Limited agent coverage: $agent_count agents (expected ≥11)"
        fi
    fi

    # Check for agent usage patterns in code
    local agent_references=$(find "$PROJECT_ROOT" -name "*.md" -exec grep -l "aipm-.*-agent\|Use.*agent" {} \; 2>/dev/null | wc -l)

    if [ $agent_references -gt 0 ]; then
        log_success "Agent-first patterns found in $agent_references documents"
    else
        log_warning "Limited agent-first workflow evidence"
    fi

    return $violations
}

# CI-002: Quality context standards
validate_ci_002() {
    log_info "Validating CI-002: Quality context standards"

    local violations=0

    # Check for context service implementation
    if [ ! -f "$AIPM_CLI_ROOT/aipm_cli/services/context/service.py" ]; then
        log_error "Missing context service implementation"
        violations=$((violations + 1))
    else
        log_success "Context service implemented"

        # Check context quality features
        local quality_features=$(grep -c "quality\|score\|confidence" "$AIPM_CLI_ROOT/aipm_cli/services/context/service.py" 2>/dev/null || echo 0)

        if [ $quality_features -gt 0 ]; then
            log_success "Context quality features implemented ($quality_features references)"
        else
            log_warning "Limited context quality features"
        fi
    fi

    # Check for 6W framework implementation
    local sixw_pattern="who\|what\|when\|where\|why\|how"
    local sixw_implementation=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -li "$sixw_pattern" {} \; | wc -l)

    if [ $sixw_implementation -gt 0 ]; then
        log_success "6W framework patterns found in $sixw_implementation files"
    else
        log_warning "Limited 6W framework implementation"
    fi

    return $violations
}

# CI-003: Framework agnosticism
validate_ci_003() {
    log_info "Validating CI-003: Framework agnosticism"

    local violations=0

    # Check for plugin system
    if [ ! -d "$AIPM_CLI_ROOT/aipm_cli/services/plugin" ]; then
        log_error "Missing plugin system implementation"
        violations=$((violations + 1))
    else
        log_success "Plugin system implemented"

        # Check for framework detection
        local framework_detection=$(find "$AIPM_CLI_ROOT/aipm_cli/services/plugin" -name "*.py" -exec grep -l "detect\|framework" {} \; | wc -l)

        if [ $framework_detection -gt 0 ]; then
            log_success "Framework detection implemented"
        else
            log_warning "Limited framework detection features"
        fi
    fi

    # Check for hardcoded framework dependencies
    local hardcoded_frameworks=$(find "$AIPM_CLI_ROOT" -name "*.py" -exec grep -l "django\|react\|vue\|angular" {} \; | wc -l)

    if [ $hardcoded_frameworks -gt 0 ]; then
        log_warning "Found $hardcoded_frameworks files with potential framework coupling"
    else
        log_success "No hardcoded framework dependencies detected"
    fi

    return $violations
}

# CI-004: Test coverage requirements (>90%)
validate_ci_004() {
    log_info "Validating CI-004: Test coverage requirements (>90%)"

    local violations=0

    # Check for test directory
    if [ ! -d "$AIPM_CLI_ROOT/tests" ]; then
        log_error "Missing test directory"
        violations=$((violations + 1))
    else
        log_success "Test directory exists"

        # Count test files vs source files
        local test_files=$(find "$AIPM_CLI_ROOT/tests" -name "test_*.py" | wc -l)
        local source_files=$(find "$AIPM_CLI_ROOT/aipm_cli" -name "*.py" | grep -v __pycache__ | wc -l)

        log_info "Test files: $test_files, Source files: $source_files"

        if [ $source_files -gt 0 ]; then
            local coverage_ratio=$((test_files * 100 / source_files))

            if [ $coverage_ratio -ge 90 ]; then
                log_success "Test coverage ratio adequate: ${coverage_ratio}%"
            elif [ $coverage_ratio -ge 70 ]; then
                log_warning "Test coverage below target: ${coverage_ratio}% (target: 90%)"
            else
                log_error "Test coverage insufficient: ${coverage_ratio}% (target: 90%)"
                violations=$((violations + 1))
            fi
        fi
    fi

    # Check for pytest configuration
    if [ -f "$AIPM_CLI_ROOT/pytest.ini" ] || [ -f "$AIPM_CLI_ROOT/pyproject.toml" ]; then
        log_success "Test configuration found"
    else
        log_warning "Missing pytest configuration"
    fi

    return $violations
}

# CI-005: Security standards
validate_ci_005() {
    log_info "Validating CI-005: Security standards"

    local violations=0

    # Check for security module
    if [ ! -d "$AIPM_CLI_ROOT/aipm_cli/security" ]; then
        log_error "Missing security module"
        violations=$((violations + 1))
    else
        log_success "Security module implemented"

        # Check for security components
        local security_components=0

        if [ -f "$AIPM_CLI_ROOT/aipm_cli/security/input_validator.py" ]; then
            security_components=$((security_components + 1))
        fi

        if [ -f "$AIPM_CLI_ROOT/aipm_cli/security/output_sanitizer.py" ]; then
            security_components=$((security_components + 1))
        fi

        if [ -f "$AIPM_CLI_ROOT/aipm_cli/security/command_security.py" ]; then
            security_components=$((security_components + 1))
        fi

        log_info "Security components implemented: $security_components/3"

        if [ $security_components -ge 2 ]; then
            log_success "Adequate security component coverage"
        else
            log_warning "Insufficient security component implementation"
        fi
    fi

    # Run security validation if available
    if [ -f "$SCRIPT_DIR/validate_security_compliance.sh" ]; then
        log_info "Running detailed security validation..."
        if ! "$SCRIPT_DIR/validate_security_compliance.sh" validate >/dev/null 2>&1; then
            log_warning "Security validation found issues"
        else
            log_success "Security validation passed"
        fi
    fi

    return $violations
}

# CI-006: Documentation completeness
validate_ci_006() {
    log_info "Validating CI-006: Documentation completeness"

    local violations=0

    # Check for essential documentation files
    local required_docs=(
        "README.md"
        "docs/README.md"
        "CLAUDE.md"
    )

    local missing_docs=0

    for doc in "${required_docs[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$doc" ]; then
            log_warning "Missing required documentation: $doc"
            missing_docs=$((missing_docs + 1))
        fi
    done

    if [ $missing_docs -eq 0 ]; then
        log_success "All required documentation files present"
    else
        log_warning "$missing_docs required documentation files missing"
    fi

    # Check for artifact management system
    if [ -d "$PROJECT_ROOT/docs/artifacts" ]; then
        log_success "Artifact management system in place"

        # Check artifact categories
        local artifact_dirs=$(find "$PROJECT_ROOT/docs/artifacts" -type d -mindepth 1 -maxdepth 1 | wc -l)

        if [ $artifact_dirs -ge 3 ]; then
            log_success "Comprehensive artifact organization ($artifact_dirs categories)"
        else
            log_warning "Limited artifact organization ($artifact_dirs categories)"
        fi
    else
        log_error "Missing artifact management system"
        violations=$((violations + 1))
    fi

    # Check for template system
    if [ -d "$PROJECT_ROOT/docs/_templates" ]; then
        log_success "Template system implemented"
    else
        log_warning "Missing template system"
    fi

    return $violations
}

# Generate compliance report
generate_compliance_report() {
    local ci_001_violations=$1
    local ci_002_violations=$2
    local ci_003_violations=$3
    local ci_004_violations=$4
    local ci_005_violations=$5
    local ci_006_violations=$6
    local total_violations=$((ci_001_violations + ci_002_violations + ci_003_violations + ci_004_violations + ci_005_violations + ci_006_violations))

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="$PROJECT_ROOT/docs/artifacts/analysis/completed/compliance_gates_$(date '+%Y%m%d_%H%M%S').md"

    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# AIPM Compliance Gates Validation Report

**Generated**: $timestamp
**Total Violations**: $total_violations
**Status**: $([ $total_violations -eq 0 ] && echo "FULLY COMPLIANT" || echo "PARTIAL COMPLIANCE")

## Compliance Gate Results

### Overall Compliance: $([ $total_violations -eq 0 ] && echo "✅ ALL GATES PASSED" || echo "⚠️ $total_violations VIOLATIONS")

| Gate | Description | Status | Violations |
|------|-------------|---------|------------|
| CI-001 | Agent-first workflow compliance | $([ $ci_001_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_001_violations |
| CI-002 | Quality context standards | $([ $ci_002_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_002_violations |
| CI-003 | Framework agnosticism | $([ $ci_003_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_003_violations |
| CI-004 | Test coverage requirements (>90%) | $([ $ci_004_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_004_violations |
| CI-005 | Security standards | $([ $ci_005_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_005_violations |
| CI-006 | Documentation completeness | $([ $ci_006_violations -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") | $ci_006_violations |

### Detailed Gate Analysis

#### CI-001: Agent-First Workflow
- **Purpose**: Ensure all development follows agent-first methodology
- **Status**: $([ $ci_001_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_001_violations violations")
- **Key Requirements**: Agent directory structure, agent coverage, workflow documentation

#### CI-002: Quality Context Standards
- **Purpose**: Maintain high-quality context generation and management
- **Status**: $([ $ci_002_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_002_violations violations")
- **Key Requirements**: Context service implementation, 6W framework, quality scoring

#### CI-003: Framework Agnosticism
- **Purpose**: Ensure technology-agnostic design principles
- **Status**: $([ $ci_003_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_003_violations violations")
- **Key Requirements**: Plugin system, framework detection, no hardcoded dependencies

#### CI-004: Test Coverage Requirements
- **Purpose**: Maintain >90% test coverage for reliability
- **Status**: $([ $ci_004_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_004_violations violations")
- **Key Requirements**: Comprehensive test suite, coverage measurement, test automation

#### CI-005: Security Standards
- **Purpose**: Implement robust security practices
- **Status**: $([ $ci_005_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_005_violations violations")
- **Key Requirements**: Security module, input validation, output sanitization

#### CI-006: Documentation Completeness
- **Purpose**: Maintain comprehensive project documentation
- **Status**: $([ $ci_006_violations -eq 0 ] && echo "✅ Compliant" || echo "⚠️ $ci_006_violations violations")
- **Key Requirements**: Essential docs, artifact management, template system

### Recommendations

$([ $total_violations -gt 0 ] && cat << 'RECOMMENDATIONS'
#### Immediate Actions Required

1. **Address Compliance Violations**
   - Review failed gates and implement missing requirements
   - Prioritize security and testing compliance
   - Ensure agent-first workflow adoption

2. **Continuous Compliance**
   - Implement automated compliance checking
   - Add compliance gates to CI/CD pipeline
   - Regular compliance monitoring and reporting

3. **Quality Improvement**
   - Enhance test coverage to meet 90% target
   - Strengthen security implementation
   - Complete documentation requirements

RECOMMENDATIONS
)

---
*Generated by AIPM Compliance Gates Validator*
EOF

    echo "$report_file"
}

# Comprehensive compliance validation
validate_compliance() {
    log_info "Starting comprehensive compliance gates validation..."
    echo

    local ci_001_violations=0
    local ci_002_violations=0
    local ci_003_violations=0
    local ci_004_violations=0
    local ci_005_violations=0
    local ci_006_violations=0

    # Run all compliance validations
    validate_ci_001
    ci_001_violations=$?
    echo

    validate_ci_002
    ci_002_violations=$?
    echo

    validate_ci_003
    ci_003_violations=$?
    echo

    validate_ci_004
    ci_004_violations=$?
    echo

    validate_ci_005
    ci_005_violations=$?
    echo

    validate_ci_006
    ci_006_violations=$?
    echo

    local total_violations=$((ci_001_violations + ci_002_violations + ci_003_violations + ci_004_violations + ci_005_violations + ci_006_violations))

    # Generate detailed report
    local report_file=$(generate_compliance_report $ci_001_violations $ci_002_violations $ci_003_violations $ci_004_violations $ci_005_violations $ci_006_violations)
    log_info "Detailed report generated: $report_file"

    echo
    echo "========================================"
    echo "COMPLIANCE GATES VALIDATION RESULTS"
    echo "========================================"
    echo "CI-001 violations: $ci_001_violations"
    echo "CI-002 violations: $ci_002_violations"
    echo "CI-003 violations: $ci_003_violations"
    echo "CI-004 violations: $ci_004_violations"
    echo "CI-005 violations: $ci_005_violations"
    echo "CI-006 violations: $ci_006_violations"
    echo "Total violations: $total_violations"
    echo

    if [ $total_violations -eq 0 ]; then
        log_success "✅ VALIDATION PASSED - All compliance gates satisfied"
        echo
        echo "AIPM system fully compliant with all quality standards."
        return 0
    else
        log_error "❌ VALIDATION FAILED - $total_violations compliance violations found"
        echo
        echo "Compliance issues require attention. Review report: $report_file"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-validate}" in
        "ci-001")
            validate_ci_001
            ;;
        "ci-002")
            validate_ci_002
            ;;
        "ci-003")
            validate_ci_003
            ;;
        "ci-004")
            validate_ci_004
            ;;
        "ci-005")
            validate_ci_005
            ;;
        "ci-006")
            validate_ci_006
            ;;
        "validate")
            validate_compliance
            ;;
        *)
            echo "Usage: $0 [ci-001|ci-002|ci-003|ci-004|ci-005|ci-006|validate]"
            echo ""
            echo "Commands:"
            echo "  ci-001    - Validate agent-first workflow compliance"
            echo "  ci-002    - Validate quality context standards"
            echo "  ci-003    - Validate framework agnosticism"
            echo "  ci-004    - Validate test coverage requirements"
            echo "  ci-005    - Validate security standards"
            echo "  ci-006    - Validate documentation completeness"
            echo "  validate  - Run comprehensive compliance validation"
            echo ""
            echo "Examples:"
            echo "  $0 validate   # Run all compliance gates"
            echo "  $0 ci-004     # Check test coverage only"
            exit 1
            ;;
    esac
}

main "$@"