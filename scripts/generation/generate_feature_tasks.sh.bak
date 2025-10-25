#!/bin/bash

# Feature Task Generation Script
# Auto-generates comprehensive task breakdowns when features move to accepted state

generate_feature_tasks() {
    local feature_file="$1"
    local feature_name=$(basename "$feature_file" .md)
    local timestamp=$(date +%Y%m%d_%H%M%S)

    echo "🚀 Generating tasks for feature: $feature_name"
    echo "================================================"

    # Validate feature is in accepted state
    if [[ $(dirname "$feature_file") != *"/accepted" ]]; then
        echo "❌ ERROR: Feature must be in 'accepted' state to generate tasks"
        echo "Current location: $(dirname "$feature_file")"
        return 1
    fi

    # Ensure tasks directory exists
    mkdir -p docs/artifacts/tasks/to_review

    # Extract feature metadata
    local priority=$(grep "^\*\*Priority\*\*:" "$feature_file" | sed 's/.*: *//' | tr -d '*')
    local complexity=$(grep "^\*\*Complexity\*\*:" "$feature_file" | sed 's/.*: *//' | tr -d '*')
    local business_value=$(grep "^\*\*Business Value\*\*:" "$feature_file" | sed 's/.*: *//' | tr -d '*')
    local technical_lead=$(grep "^\*\*Technical Lead\*\*:" "$feature_file" | sed 's/.*: *//' | tr -d '*')
    local target_release=$(grep "^\*\*Target Release\*\*:" "$feature_file" | sed 's/.*: *//' | tr -d '*')

    # Default values if not found
    [ -z "$priority" ] && priority="Medium"
    [ -z "$complexity" ] && complexity="Medium"
    [ -z "$business_value" ] && business_value="Medium"
    [ -z "$technical_lead" ] && technical_lead="TBD"
    [ -z "$target_release" ] && target_release="TBD"

    # Calculate effort based on complexity
    local effort
    case $complexity in
        "Simple") effort="1-2 weeks" ;;
        "Medium") effort="3-4 weeks" ;;
        "Complex") effort="6-8 weeks" ;;
        "Epic") effort="10+ weeks" ;;
        *) effort="TBD" ;;
    esac

    echo "📊 Feature Metadata:"
    echo "   Priority: $priority"
    echo "   Complexity: $complexity"
    echo "   Business Value: $business_value"
    echo "   Technical Lead: $technical_lead"
    echo "   Estimated Effort: $effort"
    echo ""

    # 1. Create Feature Implementation Epic
    create_feature_epic "$feature_name" "$timestamp" "$priority" "$effort" "$business_value" "$technical_lead" "$feature_file"

    # 2. Create Planning Tasks
    create_planning_tasks "$feature_name" "$timestamp" "$priority" "$technical_lead" "$feature_file"

    # 3. Create Development Tasks
    create_development_tasks "$feature_name" "$timestamp" "$priority" "$complexity" "$technical_lead" "$feature_file"

    # 4. Create Testing Tasks
    create_testing_tasks "$feature_name" "$timestamp" "$priority" "$technical_lead" "$feature_file"

    # 5. Create Deployment Tasks
    create_deployment_tasks "$feature_name" "$timestamp" "$priority" "$target_release" "$technical_lead" "$feature_file"

    echo ""
    echo "✅ Task generation completed for feature: $feature_name"
    echo "📋 Generated tasks can be found in: docs/artifacts/tasks/to_review/"
    echo ""
    echo "Next steps:"
    echo "1. Review generated tasks in docs/artifacts/tasks/to_review/"
    echo "2. Customize tasks based on specific feature requirements"
    echo "3. Validate tasks using: tools/validate_task.sh"
    echo "4. Move ready tasks to docs/artifacts/tasks/todo/"
}

create_feature_epic() {
    local feature_name="$1"
    local timestamp="$2"
    local priority="$3"
    local effort="$4"
    local business_value="$5"
    local technical_lead="$6"
    local feature_file="$7"

    local epic_file="docs/artifacts/tasks/to_review/epic_${feature_name}_${timestamp}.md"

    cat > "$epic_file" << EOF
# Epic: Implement ${feature_name}

**Template**: todo_feature.md
**Priority**: $priority
**Effort**: $effort
**Impact**: $business_value Impact
**Owner**: $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../WORKFLOW_RULES.md](../WORKFLOW_RULES.md)
**Source Feature**: [../artifacts/features/accepted/${feature_name}.md](../artifacts/features/accepted/${feature_name}.md)

## 🎯 Objective

Implement the complete ${feature_name} feature as specified in the accepted feature proposal. This epic encompasses all development, testing, and deployment activities required to deliver the feature to production.

**Success Definition**: Feature is fully implemented, tested, and deployed according to the acceptance criteria defined in the feature specification.

## 📋 Executive Summary

This epic implements the ${feature_name} feature that was accepted for development. The implementation will follow the technical approach and architecture defined in the feature specification, ensuring all acceptance criteria are met and quality standards are maintained.

**Key Deliverables**:
- Complete feature implementation
- Comprehensive test coverage
- Updated documentation
- Successful production deployment

## 📊 Implementation Plan

### Phase 1: Planning & Design
- Technical architecture review
- Detailed implementation planning
- Resource allocation and timeline refinement
- Risk assessment and mitigation planning

### Phase 2: Development
- Core feature implementation
- Integration with existing systems
- Unit and integration testing
- Code review and quality assurance

### Phase 3: Testing & Validation
- Comprehensive testing execution
- User acceptance testing
- Performance validation
- Security review

### Phase 4: Deployment & Launch
- Production deployment
- Monitoring and alerting setup
- Documentation updates
- Success metrics tracking

## ✅ Acceptance Criteria

The following criteria must be met for this epic to be considered complete:

### Functional Requirements
- [ ] All feature functionality implemented as specified
- [ ] Integration with existing systems working correctly
- [ ] User interface/experience meets design requirements
- [ ] All acceptance criteria from feature spec satisfied

### Quality Requirements
- [ ] Code coverage >90% for new functionality
- [ ] All automated tests passing
- [ ] Performance requirements met
- [ ] Security review completed and passed

### Deployment Requirements
- [ ] Feature deployed to production successfully
- [ ] Monitoring and alerting configured
- [ ] Documentation updated
- [ ] Success metrics tracking implemented

## 🚨 Risks & Dependencies

### High-Risk Items
- Complex integration points requiring careful coordination
- Performance impact on existing systems
- User adoption and change management

### Dependencies
- Completion of prerequisite technical debt items
- Availability of required development resources
- Third-party service integrations (if applicable)

### Mitigation Strategies
- Early identification and resolution of technical blockers
- Regular stakeholder communication and alignment
- Incremental delivery and validation approach

## 📝 Related Tasks

This epic is broken down into the following task categories:
- Planning tasks: epic_${feature_name}_planning_*
- Development tasks: epic_${feature_name}_development_*
- Testing tasks: epic_${feature_name}_testing_*
- Deployment tasks: epic_${feature_name}_deployment_*

## 📈 Success Metrics

### Implementation Metrics
- Feature delivery timeline adherence
- Code quality metrics (coverage, complexity)
- Defect discovery and resolution rate

### Business Metrics
- User adoption and engagement rates
- Performance impact measurements
- Business value realization tracking

---

**Epic Owner**: $technical_lead
**Feature Specification**: [${feature_name}](../artifacts/features/accepted/${feature_name}.md)
**Epic Created**: $(date +%Y-%m-%d)
**Estimated Completion**: TBD (to be refined during planning)
EOF

    echo "✅ Created epic: $epic_file"
}

create_planning_tasks() {
    local feature_name="$1"
    local timestamp="$2"
    local priority="$3"
    local technical_lead="$4"
    local feature_file="$5"

    # Technical Architecture Review Task
    local arch_task="docs/artifacts/tasks/to_review/epic_${feature_name}_planning_architecture_${timestamp}.md"

    cat > "$arch_task" << EOF
# Planning: Technical Architecture Review for ${feature_name}

**Template**: todo_research.md
**Priority**: $priority
**Effort**: 3-5 days
**Impact**: Critical for implementation success
**Owner**: $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Conduct comprehensive technical architecture review for ${feature_name} feature implementation, validating the proposed approach and identifying detailed implementation requirements.

## 📋 Acceptance Criteria

- [ ] Technical architecture validated and refined
- [ ] Implementation approach confirmed feasible
- [ ] Integration points clearly defined
- [ ] Performance requirements validated
- [ ] Security considerations documented
- [ ] Technical risks identified and mitigated
- [ ] Detailed implementation plan created

## 🔍 Research Areas

### Architecture Validation
- Review proposed technical approach from feature spec
- Validate integration with existing system architecture
- Identify potential architectural improvements or concerns

### Implementation Planning
- Break down implementation into detailed technical tasks
- Identify required code changes and new components
- Plan database schema changes (if applicable)

### Integration Analysis
- Document all integration points and dependencies
- Validate API contracts and data flows
- Identify potential integration challenges

## 📊 Deliverables

1. **Technical Architecture Document**
   - Detailed system design
   - Component interaction diagrams
   - Database schema changes
   - API specifications

2. **Implementation Plan**
   - Task breakdown with estimates
   - Development sequence and dependencies
   - Risk mitigation strategies

3. **Integration Specifications**
   - API contracts and protocols
   - Data transformation requirements
   - Error handling strategies

## 📝 Success Criteria

- Architecture review approved by senior technical staff
- Implementation plan validated by development team
- All technical risks identified and mitigation planned
- Clear path forward for development phase
EOF

    echo "✅ Created planning task: $arch_task"

    # Resource Planning Task
    local resource_task="docs/artifacts/tasks/to_review/epic_${feature_name}_planning_resources_${timestamp}.md"

    cat > "$resource_task" << EOF
# Planning: Resource Allocation for ${feature_name}

**Template**: base_template.md
**Priority**: $priority
**Effort**: 1-2 days
**Impact**: Essential for project execution
**Owner**: $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Plan and allocate development resources for ${feature_name} implementation, ensuring adequate staffing and timeline management.

## 📋 Acceptance Criteria

- [ ] Development team members identified and assigned
- [ ] Individual roles and responsibilities defined
- [ ] Timeline and milestone schedule created
- [ ] Capacity planning validated against other commitments
- [ ] Stakeholder communication plan established

## 📊 Resource Analysis

### Team Composition
- Lead Developer: [To be assigned]
- Frontend Developer(s): [To be assigned]
- Backend Developer(s): [To be assigned]
- QA Engineer: [To be assigned]
- DevOps Engineer: [If needed]

### Timeline Planning
- Planning Phase: [Duration TBD]
- Development Phase: [Duration TBD]
- Testing Phase: [Duration TBD]
- Deployment Phase: [Duration TBD]

### Capacity Validation
- Review team member availability
- Identify potential scheduling conflicts
- Plan for vacation/leave coverage
- Assess skill gaps and training needs

## 📝 Deliverables

1. **Resource Allocation Plan**
   - Team member assignments
   - Role definitions and responsibilities
   - Capacity utilization analysis

2. **Project Timeline**
   - Detailed milestone schedule
   - Critical path identification
   - Buffer time allocation

3. **Communication Plan**
   - Stakeholder update schedule
   - Status reporting format
   - Issue escalation procedures
EOF

    echo "✅ Created resource planning task: $resource_task"
}

create_development_tasks() {
    local feature_name="$1"
    local timestamp="$2"
    local priority="$3"
    local complexity="$4"
    local technical_lead="$5"
    local feature_file="$6"

    # Core Implementation Task
    local core_task="docs/artifacts/tasks/to_review/epic_${feature_name}_development_core_${timestamp}.md"

    cat > "$core_task" << EOF
# Development: Core Implementation of ${feature_name}

**Template**: todo_feature.md
**Priority**: $priority
**Effort**: $(get_development_effort "$complexity")
**Impact**: High - Core feature functionality
**Owner**: $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Implement the core functionality of ${feature_name} according to the technical specifications and acceptance criteria defined in the feature specification.

## 📋 Acceptance Criteria

### Functional Implementation
- [ ] All core feature functionality implemented
- [ ] Business logic correctly implemented
- [ ] Data persistence layer working correctly
- [ ] Error handling implemented comprehensively

### Code Quality
- [ ] Code follows established patterns and conventions
- [ ] Comprehensive unit tests written (>90% coverage)
- [ ] Integration tests for key workflows
- [ ] Code reviewed and approved

### Performance
- [ ] Performance requirements met
- [ ] No degradation to existing system performance
- [ ] Efficient database queries and caching

## 🔧 Implementation Details

### Core Components
[To be detailed based on technical architecture review]

### Data Models
[To be specified based on feature requirements]

### Business Logic
[To be implemented based on feature specification]

### Integration Points
[To be developed based on integration analysis]

## 🚨 Technical Risks

- Integration complexity with existing systems
- Performance impact on current functionality
- Data migration requirements (if applicable)
- Third-party service dependencies

## 📝 Development Checklist

### Setup
- [ ] Development environment configured
- [ ] Feature branch created from main
- [ ] Local database schema updated

### Implementation
- [ ] Core business logic implemented
- [ ] Data access layer implemented
- [ ] API endpoints created (if applicable)
- [ ] User interface components built

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests implemented
- [ ] Manual testing completed
- [ ] Performance testing conducted

### Quality Assurance
- [ ] Code review completed
- [ ] Static analysis tools passed
- [ ] Security review completed
- [ ] Documentation updated
EOF

    echo "✅ Created core development task: $core_task"

    # Integration Task (if needed)
    local integration_task="docs/artifacts/tasks/to_review/epic_${feature_name}_development_integration_${timestamp}.md"

    cat > "$integration_task" << EOF
# Development: Integration Implementation for ${feature_name}

**Template**: base_template.md
**Priority**: $priority
**Effort**: 1-2 weeks
**Impact**: High - System integration
**Owner**: $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Implement all integration points required for ${feature_name} to work seamlessly with existing system components and external services.

## 📋 Acceptance Criteria

- [ ] All internal system integrations working correctly
- [ ] External service integrations implemented and tested
- [ ] Error handling for integration failures
- [ ] Monitoring and logging for integration points
- [ ] Integration tests passing

## 🔗 Integration Points

### Internal Integrations
- [Integration point 1 - to be specified]
- [Integration point 2 - to be specified]

### External Integrations
- [External service 1 - if applicable]
- [External service 2 - if applicable]

### Data Flows
- [Data flow 1 - to be documented]
- [Data flow 2 - to be documented]

## 🧪 Testing Strategy

- Integration test suite development
- Mock services for external dependencies
- Error scenario testing
- Performance testing for integration points

## 📝 Implementation Checklist

- [ ] Internal API integrations implemented
- [ ] External service clients implemented
- [ ] Error handling and retry logic
- [ ] Integration monitoring and logging
- [ ] Integration tests written and passing
EOF

    echo "✅ Created integration development task: $integration_task"
}

create_testing_tasks() {
    local feature_name="$1"
    local timestamp="$2"
    local priority="$3"
    local technical_lead="$4"
    local feature_file="$5"

    # Comprehensive Testing Task
    local testing_task="docs/artifacts/tasks/to_review/epic_${feature_name}_testing_comprehensive_${timestamp}.md"

    cat > "$testing_task" << EOF
# Testing: Comprehensive Testing for ${feature_name}

**Template**: base_template.md
**Priority**: $priority
**Effort**: 1-2 weeks
**Impact**: Critical - Quality assurance
**Owner**: QA Engineer / $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Execute comprehensive testing strategy for ${feature_name} to ensure quality, performance, and reliability standards are met before production deployment.

## 📋 Acceptance Criteria

### Test Coverage
- [ ] Unit test coverage >90% for new code
- [ ] Integration tests for all major workflows
- [ ] End-to-end tests for user journeys
- [ ] Performance tests meeting requirements

### Quality Gates
- [ ] All automated tests passing
- [ ] Manual testing scenarios completed
- [ ] User acceptance testing passed
- [ ] Security testing completed
- [ ] Accessibility testing passed (if UI components)

### Documentation
- [ ] Test plan documented
- [ ] Test results recorded
- [ ] Defects identified and resolved
- [ ] Performance benchmarks established

## 🧪 Testing Strategy

### Automated Testing
1. **Unit Tests**
   - Business logic validation
   - Data access layer testing
   - Individual component testing

2. **Integration Tests**
   - API endpoint testing
   - Database integration testing
   - External service integration testing

3. **End-to-End Tests**
   - Complete user workflows
   - Cross-browser testing (if applicable)
   - Mobile responsiveness (if applicable)

### Manual Testing
1. **Functional Testing**
   - Feature functionality validation
   - Edge case testing
   - Error scenario testing

2. **Usability Testing**
   - User experience validation
   - Accessibility compliance
   - Performance from user perspective

### Performance Testing
1. **Load Testing**
   - Expected usage patterns
   - Peak load scenarios
   - Resource utilization monitoring

2. **Stress Testing**
   - System breaking points
   - Recovery behavior
   - Performance degradation analysis

## 📊 Test Execution Plan

### Phase 1: Automated Test Development
- Write and maintain unit tests
- Develop integration test suite
- Create end-to-end test scenarios

### Phase 2: Manual Test Execution
- Execute functional test scenarios
- Perform usability and accessibility testing
- Validate performance characteristics

### Phase 3: User Acceptance Testing
- Coordinate with stakeholders
- Execute UAT scenarios
- Document feedback and resolution

## 🚨 Quality Gates

### Pre-Production Gates
- All critical and high priority tests passing
- Performance benchmarks met
- Security vulnerabilities resolved
- Accessibility standards met

### Production Readiness
- Monitoring and alerting configured
- Rollback procedures validated
- Success metrics defined
- Support documentation complete

## 📝 Testing Checklist

### Test Development
- [ ] Test plan created and approved
- [ ] Automated tests implemented
- [ ] Test data prepared
- [ ] Test environments configured

### Test Execution
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] End-to-end tests passing
- [ ] Performance tests meeting requirements
- [ ] Security tests completed
- [ ] Manual testing scenarios executed

### Quality Validation
- [ ] All critical defects resolved
- [ ] Performance benchmarks achieved
- [ ] User acceptance testing passed
- [ ] Production readiness validated
EOF

    echo "✅ Created comprehensive testing task: $testing_task"
}

create_deployment_tasks() {
    local feature_name="$1"
    local timestamp="$2"
    local priority="$3"
    local target_release="$4"
    local technical_lead="$5"
    local feature_file="$6"

    # Deployment Planning Task
    local deploy_task="docs/artifacts/tasks/to_review/epic_${feature_name}_deployment_${timestamp}.md"

    cat > "$deploy_task" << EOF
# Deployment: Production Deployment of ${feature_name}

**Template**: todo_deployment.md
**Priority**: $priority
**Effort**: 3-5 days
**Impact**: High - Feature delivery
**Owner**: DevOps Engineer / $technical_lead
**Created**: $(date +%Y-%m-%d)
**Status**: to_review
**Target Release**: $target_release
**Workflow Rules**: [../../WORKFLOW_RULES.md](../../WORKFLOW_RULES.md)
**Parent Epic**: [epic_${feature_name}_${timestamp}.md](epic_${feature_name}_${timestamp}.md)

## 🎯 Objective

Successfully deploy ${feature_name} to production environment, ensuring smooth rollout with monitoring, rollback capabilities, and post-deployment validation.

## 📋 Acceptance Criteria

### Deployment Execution
- [ ] Feature deployed to production successfully
- [ ] All services running correctly
- [ ] Database migrations applied successfully (if applicable)
- [ ] Configuration updates deployed

### Monitoring & Observability
- [ ] Application monitoring configured
- [ ] Performance metrics tracking active
- [ ] Error alerting configured
- [ ] Log aggregation working

### Validation
- [ ] Smoke tests passing in production
- [ ] Feature functionality validated
- [ ] Performance monitoring showing expected metrics
- [ ] No critical issues detected

### Documentation & Communication
- [ ] Deployment runbook updated
- [ ] Release notes published
- [ ] Stakeholders notified
- [ ] Support team briefed

## 🚀 Deployment Strategy

### Pre-Deployment
1. **Environment Preparation**
   - Production environment readiness check
   - Database backup creation
   - Configuration validation

2. **Deployment Package Preparation**
   - Code build and packaging
   - Deployment scripts validation
   - Migration scripts testing

### Deployment Execution
1. **Rolling Deployment** (if applicable)
   - Gradual service updates
   - Health check validation
   - Traffic routing management

2. **Database Migrations** (if applicable)
   - Schema change deployment
   - Data migration execution
   - Migration rollback preparation

### Post-Deployment
1. **Validation & Monitoring**
   - Smoke test execution
   - Performance monitoring
   - Error rate monitoring

2. **Rollback Preparedness**
   - Rollback procedure validation
   - Quick rollback triggers defined
   - Emergency response plan

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] Production environment health check
- [ ] Database backup completed
- [ ] Deployment package prepared and tested
- [ ] Rollback procedure validated
- [ ] Stakeholder notification sent

### Deployment
- [ ] Maintenance mode enabled (if required)
- [ ] Application deployment completed
- [ ] Database migrations applied
- [ ] Configuration updates deployed
- [ ] Services restarted and healthy

### Post-Deployment
- [ ] Smoke tests passing
- [ ] Performance metrics normal
- [ ] Error rates within expected ranges
- [ ] Monitoring and alerting active
- [ ] Feature functionality validated
- [ ] Release notes published

### Rollback Plan
- [ ] Rollback triggers defined
- [ ] Rollback procedure documented
- [ ] Database rollback scripts prepared
- [ ] Emergency contact list updated

## 🔍 Monitoring & Validation

### Key Metrics to Monitor
- Application response times
- Error rates and patterns
- Resource utilization (CPU, memory, disk)
- Database performance metrics
- Feature adoption rates

### Success Criteria
- Response times within performance requirements
- Error rates <1% for critical paths
- No degradation to existing functionality
- User adoption tracking active

## 📞 Support & Communication

### Stakeholder Communication
- [ ] Deployment announcement sent
- [ ] Feature benefits communicated
- [ ] Support contact information provided
- [ ] Feedback channels established

### Internal Team Briefing
- [ ] Support team trained on new feature
- [ ] Operations team briefed on monitoring
- [ ] Development team on-call schedule updated
- [ ] Documentation wiki updated

## 🚨 Risk Management

### Deployment Risks
- Service disruption during deployment
- Database migration failures
- Configuration errors
- Performance degradation

### Mitigation Strategies
- Comprehensive pre-deployment testing
- Gradual rollout with monitoring
- Immediate rollback capability
- 24/7 monitoring during initial rollout

### Emergency Procedures
- Rollback execution procedure
- Incident response team contacts
- Communication escalation plan
- Post-incident review process
EOF

    echo "✅ Created deployment task: $deploy_task"
}

get_development_effort() {
    local complexity="$1"
    case $complexity in
        "Simple") echo "1-2 weeks" ;;
        "Medium") echo "3-4 weeks" ;;
        "Complex") echo "4-6 weeks" ;;
        "Epic") echo "6+ weeks" ;;
        *) echo "TBD" ;;
    esac
}

# Main execution
if [ "$#" -eq 0 ]; then
    echo "Feature Task Generation Script"
    echo "============================="
    echo ""
    echo "Usage:"
    echo "  $0 <feature-file.md>     # Generate tasks for accepted feature"
    echo ""
    echo "Example:"
    echo "  $0 docs/artifacts/features/accepted/new_dashboard.md"
    echo ""
    echo "Requirements:"
    echo "- Feature must be in 'accepted' state (docs/artifacts/features/accepted/)"
    echo "- Feature must have required metadata (Priority, Complexity, etc.)"
    echo "- Target directory docs/artifacts/tasks/to_review/ must exist"
    exit 1
fi

generate_feature_tasks "$1"
exit $?