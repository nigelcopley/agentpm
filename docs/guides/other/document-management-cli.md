# Document Management CLI Examples

Complete workflow examples demonstrating document management CLI commands in real-world scenarios.

## Table of Contents

1. [Feature Development Documentation Workflow](#1-feature-development-documentation-workflow)
2. [Research to Implementation Workflow](#2-research-to-implementation-workflow)
3. [Quality Gates Integration](#3-quality-gates-integration)
4. [Idea to Work Item Document Transfer](#4-idea-to-work-item-document-transfer)
5. [API Documentation Lifecycle](#5-api-documentation-lifecycle)
6. [Architecture Decision Records](#6-architecture-decision-records)
7. [Testing Documentation](#7-testing-documentation)
8. [Document Organization and Cleanup](#8-document-organization-and-cleanup)

---

## 1. Feature Development Documentation Workflow

**Scenario**: Developing a payment system feature with comprehensive documentation at each stage.

### Step 1: Create Work Item

```bash
# Create feature work item
apm work-item add \
    --title="Payment Processing System" \
    --type=feature \
    --description="Implement payment processing with fraud detection"

# Output: Created work item #42
```

### Step 2: Add Requirements Documentation

```bash
# Add requirements document
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/requirements/payment-system-requirements.md" \
    --type=requirements \
    --description="Payment system functional and non-functional requirements"

# Add stakeholder analysis
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/stakeholders/payment-stakeholders.md" \
    --type=stakeholder_analysis \
    --description="Key stakeholders and their requirements for payment system"
```

### Step 3: Add Architecture Documentation

```bash
# Add architecture document (auto-detects type from path)
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/architecture/payment-system-architecture.md"

# Add architecture decision records
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/adr/0001-payment-gateway-selection.md" \
    --title="ADR 1: Payment Gateway Selection"

apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/adr/0002-fraud-detection-strategy.md" \
    --title="ADR 2: Fraud Detection Strategy"
```

### Step 4: Add Design Documentation

```bash
# Add design documents
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/design/payment-ui-mockups.pdf" \
    --type=design \
    --description="UI mockups for payment flow"

apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/design/payment-database-schema.md" \
    --type=design \
    --description="Database schema for payment transactions"
```

### Step 5: Add API Documentation

```bash
# Add API specification
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/api/payment-api-spec.yaml" \
    --type=api_doc \
    --title="Payment API Specification"
```

### Step 6: Add Implementation Plan

```bash
# Add implementation plan
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/implementation/payment-implementation-plan.md" \
    --type=implementation_plan \
    --description="Phase-by-phase implementation plan with milestones"
```

### Step 7: Add Test Plan

```bash
# Add test plan
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/testing/payment-test-plan.md" \
    --type=test_plan \
    --description="Comprehensive test plan including integration and security testing"
```

### Step 8: Add Deployment Documentation

```bash
# Add deployment guide
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/deployment/payment-deployment-guide.md" \
    --type=deployment_guide \
    --description="Deployment steps, rollback procedures, and monitoring setup"

# Add runbook
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/operations/payment-runbook.md" \
    --type=runbook \
    --description="Operational procedures for payment system incidents"
```

### Step 9: Add User Documentation

```bash
# Add user guide
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/user-guides/payment-user-guide.md" \
    --type=user_guide \
    --description="End-user guide for payment features"

# Add troubleshooting guide
apm document add \
    --entity-type=work-item \
    --entity-id=42 \
    --file-path="docs/support/payment-troubleshooting.md" \
    --type=troubleshooting \
    --description="Common payment issues and solutions"
```

### Step 10: Review All Documents

```bash
# List all documents for work item
apm document list --entity-type=work-item --entity-id=42

# Output shows 12 documents across all categories
```

---

## 2. Research to Implementation Workflow

**Scenario**: Research phase producing documents that guide implementation.

### Phase 1: Research Documents

```bash
# Create research work item
apm work-item add \
    --title="Payment Gateway Research" \
    --type=research

# Output: Created work item #50

# Add market research
apm document add \
    --entity-type=work-item \
    --entity-id=50 \
    --file-path="docs/research/payment-market-analysis.pdf" \
    --type=market_research_report \
    --description="Analysis of payment gateway market and pricing"

# Add competitive analysis
apm document add \
    --entity-type=work-item \
    --entity-id=50 \
    --file-path="docs/research/payment-gateway-comparison.xlsx" \
    --type=competitive_analysis \
    --description="Feature and pricing comparison of top 5 payment gateways"

# Add technical evaluation
apm document add \
    --entity-type=work-item \
    --entity-id=50 \
    --file-path="docs/research/payment-technical-evaluation.md" \
    --type=technical_specification \
    --description="Technical evaluation criteria and scoring"
```

### Phase 2: Convert Research to Requirements

```bash
# Create implementation work item
apm work-item add \
    --title="Implement Stripe Payment Integration" \
    --type=feature

# Output: Created work item #51

# Link research documents to new work item
# (Manually reference or copy insights)
apm document add \
    --entity-type=work-item \
    --entity-id=51 \
    --file-path="docs/requirements/stripe-integration-requirements.md" \
    --type=requirements \
    --description="Requirements based on research from WI-50"

# Add implementation plan based on research
apm document add \
    --entity-type=work-item \
    --entity-id=51 \
    --file-path="docs/implementation/stripe-implementation-plan.md" \
    --type=implementation_plan \
    --description="Implementation plan based on technical evaluation"
```

### Phase 3: Implementation Task Documentation

```bash
# Create implementation task
apm task add \
    --title="Implement Stripe payment flow" \
    --work-item-id=51 \
    --type=implementation

# Output: Created task #123

# Add task-specific design
apm document add \
    --entity-type=task \
    --entity-id=123 \
    --file-path="docs/design/stripe-payment-flow-design.md" \
    --type=design \
    --description="Detailed design for Stripe payment flow implementation"

# Add API integration notes
apm document add \
    --entity-type=task \
    --entity-id=123 \
    --file-path="docs/api/stripe-api-integration.md" \
    --type=api_doc \
    --description="Stripe API endpoints and integration patterns"
```

---

## 3. Quality Gates Integration

**Scenario**: Documenting quality gates for a critical feature.

### Step 1: Define Quality Gates

```bash
# Create work item
apm work-item add \
    --title="User Authentication System" \
    --type=feature

# Output: Created work item #60

# Add quality gates specification
apm document add \
    --entity-type=work-item \
    --entity-id=60 \
    --file-path="docs/quality/auth-quality-gates.yaml" \
    --type=quality_gates_specification \
    --description="Security, performance, and reliability gates for authentication"
```

### Step 2: Quality Gates Content

Create `docs/quality/auth-quality-gates.yaml`:

```yaml
quality_gates:
  security:
    - name: "Password Hashing"
      requirement: "bcrypt with cost factor >= 12"
      validation: "Unit test + security audit"
      blocking: true

    - name: "Session Management"
      requirement: "Secure session tokens with expiration"
      validation: "Integration test + penetration test"
      blocking: true

  performance:
    - name: "Login Response Time"
      requirement: "< 200ms for 95th percentile"
      validation: "Load test with 1000 concurrent users"
      blocking: false

  reliability:
    - name: "Test Coverage"
      requirement: ">= 90% for auth module"
      validation: "pytest-cov report"
      blocking: true
```

### Step 3: Link Gate Validation Documents

```bash
# Add test results
apm document add \
    --entity-type=work-item \
    --entity-id=60 \
    --file-path="docs/testing/auth-test-results.md" \
    --type=test_plan \
    --description="Test results demonstrating quality gate compliance"

# Add security audit report
apm document add \
    --entity-type=work-item \
    --entity-id=60 \
    --file-path="docs/security/auth-security-audit.pdf" \
    --type=other \
    --title="Security Audit Report" \
    --description="Third-party security audit results"

# Add performance test results
apm document add \
    --entity-type=work-item \
    --entity-id=60 \
    --file-path="docs/testing/auth-performance-results.xlsx" \
    --type=test_plan \
    --description="Load test results showing performance gate compliance"
```

### Step 4: Validate Against Gates

```bash
# Review all quality documentation
apm document list --entity-type=work-item --entity-id=60 --type=test_plan

# Validate work item passes gates
apm work-item validate 60
```

---

## 4. Idea to Work Item Document Transfer

**Scenario**: Capturing idea documentation and transferring to work item.

### Step 1: Create Idea with Documents

```bash
# Create idea
apm idea add \
    --title="Mobile App for Customer Portal" \
    --description="Native mobile app for iOS and Android"

# Output: Created idea #15

# Add initial concept document
apm document add \
    --entity-type=idea \
    --entity-id=15 \
    --file-path="docs/ideas/mobile-app-concept.md" \
    --type=idea \
    --description="Initial concept and vision for mobile app"

# Add market research
apm document add \
    --entity-type=idea \
    --entity-id=15 \
    --file-path="docs/research/mobile-market-analysis.pdf" \
    --type=market_research_report \
    --description="Market size, competitors, and opportunity analysis"

# Add user research
apm document add \
    --entity-type=idea \
    --entity-id=15 \
    --file-path="docs/research/customer-interviews.md" \
    --type=user_story \
    --description="Summary of customer interviews and pain points"
```

### Step 2: Develop Idea Further

```bash
# Add requirements as idea matures
apm document add \
    --entity-type=idea \
    --entity-id=15 \
    --file-path="docs/requirements/mobile-app-requirements.md" \
    --type=requirements \
    --description="Initial requirements for mobile app features"

# Add technical feasibility
apm document add \
    --entity-type=idea \
    --entity-id=15 \
    --file-path="docs/technical/mobile-technical-feasibility.md" \
    --type=technical_specification \
    --description="Technical feasibility and platform considerations"
```

### Step 3: Review Idea Documents

```bash
# List all idea documents
apm document list --entity-type=idea --entity-id=15

# Output shows 5 documents
```

### Step 4: Convert to Work Item

```bash
# Convert idea to work item
apm idea create-work-item 15

# Output: Created work item #70 from idea #15
```

### Step 5: Verify Document Transfer

```bash
# List documents for new work item
apm document list --entity-type=work-item --entity-id=70

# All 5 documents now linked to work item
```

### Step 6: Add Work Item-Specific Documents

```bash
# Add architecture document (now that it's a real feature)
apm document add \
    --entity-type=work-item \
    --entity-id=70 \
    --file-path="docs/architecture/mobile-app-architecture.md" \
    --type=architecture

# Add implementation plan
apm document add \
    --entity-type=work-item \
    --entity-id=70 \
    --file-path="docs/implementation/mobile-app-plan.md" \
    --type=implementation_plan
```

---

## 5. API Documentation Lifecycle

**Scenario**: Managing API documentation from design through deployment.

### Phase 1: Design Phase

```bash
# Create API design work item
apm work-item add \
    --title="User Management API v2" \
    --type=feature

# Output: Created work item #80

# Add initial API design
apm document add \
    --entity-type=work-item \
    --entity-id=80 \
    --file-path="docs/api/user-api-v2-design.yaml" \
    --type=api_doc \
    --title="User API v2 - Initial Design"
```

### Phase 2: Review and Update

```bash
# Update API doc after review
apm document update 25 \
    --title="User API v2 - Revised Design" \
    --description="Updated after architecture review"

# Add OpenAPI specification
apm document add \
    --entity-type=work-item \
    --entity-id=80 \
    --file-path="docs/api/user-api-v2-openapi.yaml" \
    --type=api_doc \
    --title="User API v2 - OpenAPI 3.0 Spec"
```

### Phase 3: Implementation

```bash
# Create implementation task
apm task add \
    --title="Implement User API v2 endpoints" \
    --work-item-id=80 \
    --type=implementation

# Output: Created task #200

# Link API spec to task
apm document add \
    --entity-type=task \
    --entity-id=200 \
    --file-path="docs/api/user-api-v2-openapi.yaml" \
    --type=api_doc \
    --description="API spec for implementation reference"

# Add implementation notes
apm document add \
    --entity-type=task \
    --entity-id=200 \
    --file-path="docs/implementation/user-api-implementation-notes.md" \
    --type=implementation_plan \
    --description="Implementation notes and gotchas"
```

### Phase 4: Testing

```bash
# Create testing task
apm task add \
    --title="API integration testing" \
    --work-item-id=80 \
    --type=testing

# Output: Created task #201

# Add test plan
apm document add \
    --entity-type=task \
    --entity-id=201 \
    --file-path="docs/testing/user-api-test-plan.md" \
    --type=test_plan \
    --description="Integration and contract testing plan"

# Add test results
apm document add \
    --entity-type=task \
    --entity-id=201 \
    --file-path="docs/testing/user-api-test-results.md" \
    --type=test_plan \
    --description="Test execution results and coverage"
```

### Phase 5: Documentation

```bash
# Create documentation task
apm task add \
    --title="API documentation" \
    --work-item-id=80 \
    --type=documentation

# Output: Created task #202

# Add API documentation
apm document add \
    --entity-type=task \
    --entity-id=202 \
    --file-path="docs/user-guides/user-api-guide.md" \
    --type=user_guide \
    --description="Developer guide for User API v2"

# Add examples
apm document add \
    --entity-type=task \
    --entity-id=202 \
    --file-path="docs/api/user-api-examples.md" \
    --type=api_doc \
    --description="Code examples and use cases"
```

### Phase 6: Deployment

```bash
# Add deployment guide
apm document add \
    --entity-type=work-item \
    --entity-id=80 \
    --file-path="docs/deployment/user-api-v2-deployment.md" \
    --type=deployment_guide \
    --description="Deployment procedures and rollback plan"

# Add changelog
apm document add \
    --entity-type=work-item \
    --entity-id=80 \
    --file-path="docs/changelog/user-api-v2.md" \
    --type=changelog \
    --description="User API v2 changelog and migration guide"
```

---

## 6. Architecture Decision Records

**Scenario**: Documenting architecture decisions for a microservices migration.

### Step 1: Create Architecture Work Item

```bash
# Create architecture planning work item
apm work-item add \
    --title="Microservices Architecture Migration" \
    --type=planning

# Output: Created work item #90
```

### Step 2: Add ADRs

```bash
# ADR 1: Microservices approach
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/adr/0001-microservices-architecture.md" \
    --type=adr \
    --title="ADR 1: Adopt Microservices Architecture"

# ADR 2: Service communication
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/adr/0002-async-messaging-pattern.md" \
    --type=adr \
    --title="ADR 2: Use Event-Driven Communication"

# ADR 3: Data management
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/adr/0003-database-per-service.md" \
    --type=adr \
    --title="ADR 3: Database per Service Pattern"

# ADR 4: API Gateway
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/adr/0004-api-gateway-selection.md" \
    --type=adr \
    --title="ADR 4: Select Kong as API Gateway"

# ADR 5: Service discovery
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/adr/0005-service-discovery-consul.md" \
    --type=adr \
    --title="ADR 5: Use Consul for Service Discovery"
```

### Step 3: Add Architecture Documentation

```bash
# Add overall architecture
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/architecture/microservices-architecture.md" \
    --type=architecture \
    --description="Overall microservices architecture diagram and explanation"

# Add migration plan
apm document add \
    --entity-type=work-item \
    --entity-id=90 \
    --file-path="docs/implementation/microservices-migration-plan.md" \
    --type=implementation_plan \
    --description="Phase-by-phase migration plan from monolith"
```

### Step 4: Review All ADRs

```bash
# List all ADRs
apm document list --entity-type=work-item --entity-id=90 --type=adr

# Output shows 5 ADRs in sequence
```

---

## 7. Testing Documentation

**Scenario**: Comprehensive testing documentation for a feature.

### Step 1: Create Feature Work Item

```bash
# Create feature work item
apm work-item add \
    --title="Shopping Cart Feature" \
    --type=feature

# Output: Created work item #100
```

### Step 2: Add Test Plan

```bash
# Add master test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-master-test-plan.md" \
    --type=test_plan \
    --description="Comprehensive test plan covering all test types"
```

### Step 3: Add Specific Test Plans

```bash
# Unit test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-unit-tests.md" \
    --type=test_plan \
    --description="Unit test cases for cart business logic"

# Integration test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-integration-tests.md" \
    --type=test_plan \
    --description="Integration tests for cart API and database"

# E2E test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-e2e-tests.md" \
    --type=test_plan \
    --description="End-to-end user journey tests"

# Performance test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-performance-tests.md" \
    --type=test_plan \
    --description="Load and stress testing scenarios"

# Security test plan
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/shopping-cart-security-tests.md" \
    --type=test_plan \
    --description="Security testing and vulnerability assessment"
```

### Step 4: Add Test Results

```bash
# Unit test results
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/results/unit-test-results.html" \
    --type=test_plan \
    --title="Unit Test Results" \
    --description="pytest HTML report with 95% coverage"

# Integration test results
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/results/integration-test-results.md" \
    --type=test_plan \
    --title="Integration Test Results"

# Performance test results
apm document add \
    --entity-type=work-item \
    --entity-id=100 \
    --file-path="docs/testing/results/performance-test-results.pdf" \
    --type=test_plan \
    --title="Performance Test Results" \
    --description="JMeter results showing 99th percentile < 100ms"
```

### Step 5: Review Test Documentation

```bash
# List all test documents
apm document list --entity-type=work-item --entity-id=100 --type=test_plan

# Output shows 8 test-related documents
```

---

## 8. Document Organization and Cleanup

**Scenario**: Organizing and maintaining document references.

### Scenario A: Reorganizing Files

```bash
# Original document
apm document add \
    --entity-type=work-item \
    --entity-id=110 \
    --file-path="docs/design-doc.md" \
    --type=design

# Output: Created document #30

# Move file to better location
mv docs/design-doc.md docs/design/payment-flow-design.md

# Update document reference
apm document update 30 \
    --file-path="docs/design/payment-flow-design.md" \
    --title="Payment Flow Design"
```

### Scenario B: Updating Stale Documents

```bash
# List all documents for work item
apm document list --entity-type=work-item --entity-id=110

# Update old specification
apm document update 31 \
    --title="Payment API Spec v2.1" \
    --description="Updated with new webhook endpoints"

# Show updated document
apm document show 31
```

### Scenario C: Removing Obsolete Documents

```bash
# List all documents
apm document list --entity-type=work-item --entity-id=110

# Delete obsolete document (keep file)
apm document delete 32

# Delete obsolete document and file
apm document delete 33 --delete-file
```

### Scenario D: Finding Documents by Type

```bash
# Find all architecture documents
apm document list --type=architecture

# Find all design documents for entity
apm document list --entity-type=work-item --entity-id=110 --type=design

# Find all markdown documents
apm document list --format=markdown
```

### Scenario E: Bulk Document Review

```bash
# List recent documents with limit
apm document list --limit=20

# Export to JSON for analysis
apm document list --format=json > documents.json

# Process with jq (example)
cat documents.json | jq '.[] | select(.document_type == "architecture")'
```

### Scenario F: Document Audit Trail

```bash
# Show document with full details
apm document show 25

# Check file exists
apm document show 25 | grep "File exists"

# Review document content
apm document show 25 --include-content
```

---

## Common Patterns Summary

### Pattern 1: Add Document with Auto-Detection

```bash
apm document add \
    --entity-type=work-item \
    --entity-id=<id> \
    --file-path="<path>"
# Type, format, and title auto-detected
```

### Pattern 2: Add Document with Full Metadata

```bash
apm document add \
    --entity-type=work-item \
    --entity-id=<id> \
    --file-path="<path>" \
    --type=<type> \
    --title="<title>" \
    --description="<description>"
```

### Pattern 3: List Entity Documents

```bash
apm document list \
    --entity-type=<type> \
    --entity-id=<id>
```

### Pattern 4: Update Document Metadata

```bash
apm document update <doc-id> \
    --title="<new-title>" \
    --description="<new-description>"
```

### Pattern 5: Filter Documents by Type

```bash
apm document list \
    --entity-type=<type> \
    --entity-id=<id> \
    --type=<doc-type>
```

### Pattern 6: Delete Document Reference Only

```bash
apm document delete <doc-id>
```

### Pattern 7: Delete Document and File

```bash
apm document delete <doc-id> --delete-file
```

---

## Integration with Workflows

### Work Item Creation → Documentation

```bash
# 1. Create work item
apm work-item add --title="Feature" --type=feature

# 2. Immediately add requirements
apm document add --entity-type=work-item --entity-id=<id> \
    --file-path="docs/requirements/<name>.md"

# 3. Add architecture
apm document add --entity-type=work-item --entity-id=<id> \
    --file-path="docs/architecture/<name>.md"
```

### Task Creation → Documentation

```bash
# 1. Create task
apm task add --title="Task" --work-item-id=<id> --type=implementation

# 2. Add design document
apm document add --entity-type=task --entity-id=<id> \
    --file-path="docs/design/<name>.md"

# 3. Add implementation notes
apm document add --entity-type=task --entity-id=<id> \
    --file-path="docs/implementation/<name>.md"
```

### Documentation Review Workflow

```bash
# 1. List all documents
apm document list --entity-type=work-item --entity-id=<id>

# 2. Review each document
apm document show <doc-id> --include-content

# 3. Update as needed
apm document update <doc-id> --description="Reviewed and approved"
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Status**: Production Ready
