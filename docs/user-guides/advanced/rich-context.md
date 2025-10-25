# Rich Context

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](advanced/memory-system.md) | [Next →](advanced/detection-packs.md)

## Introduction

The Rich Context System in APM (Agent Project Manager) provides comprehensive contextual information for your projects, work items, tasks, and ideas. This guide will help you understand how to use the rich context system effectively.

## What is Rich Context?

Rich context goes beyond basic project information to provide structured, detailed context that helps AI agents understand:

- **Business Context**: Why this work matters, who it impacts, and what value it provides
- **Technical Context**: How it should be implemented, what technologies to use, and what constraints exist
- **Quality Context**: What standards must be met, what tests are required, and what success looks like
- **Stakeholder Context**: Who is involved, how to communicate, and who makes decisions

## Getting Started

### Prerequisites

- APM (Agent Project Manager) project initialized
- Work items and tasks created
- Basic understanding of APM (Agent Project Manager) concepts

### First Steps

1. **Check Current Context**: See what context already exists
2. **Add Rich Context**: Add structured context to your work items
3. **Assemble Context**: View comprehensive context for AI agents
4. **Validate Context**: Ensure context is complete and accurate

## Basic Operations

### Viewing Context

To see what context exists for a work item:

```bash
apm context rich list --entity-type work_item --entity-id 123
```

This shows all rich context entries for work item 123.

### Creating Context

To add business context to a work item:

```bash
apm context rich create \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --data '{
    "analysis": "This feature addresses customer feedback about slow loading times",
    "stakeholders": ["Product Manager", "Engineering Lead", "Customer Success"],
    "priority": "high",
    "business_value": "Expected 20% improvement in user satisfaction"
  }'
```

### Assembling Complete Context

To see all context assembled for a task:

```bash
apm context rich assemble --entity-type task --entity-id 456
```

This shows hierarchical context from project → work item → task.

## Context Types Guide

### Business Pillars Context

Use this for business analysis and strategic context.

**When to use:**
- Starting a new work item
- Explaining business value
- Documenting stakeholder impact

**Example data:**
```json
{
  "analysis": "This feature will reduce customer support tickets by 30%",
  "stakeholders": ["Customer Success Manager", "Support Team Lead"],
  "priority": "medium",
  "business_value": "£10K annual cost savings",
  "risks": ["User adoption", "Technical complexity"]
}
```

### Technical Context

Use this for technical specifications and implementation details.

**When to use:**
- Planning implementation
- Documenting technical decisions
- Setting performance requirements

**Example data:**
```json
{
  "architecture": "Microservices with API gateway",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
  "dependencies": ["Authentication service", "Payment gateway"],
  "performance_requirements": ["<200ms API response", "99.9% uptime"],
  "security_requirements": ["OAuth2", "Rate limiting", "Input validation"]
}
```

### Quality Gates Context

Use this for quality requirements and testing criteria.

**When to use:**
- Defining acceptance criteria
- Setting quality standards
- Planning testing approach

**Example data:**
```json
{
  "quality_requirements": ["Performance", "Security", "Usability", "Accessibility"],
  "testing_criteria": ["Unit tests-BAK >90% coverage", "Integration tests-BAK", "E2E tests-BAK"],
  "compliance": ["GDPR", "WCAG 2.1 AA"],
  "acceptance_criteria": [
    "All tests-BAK pass",
    "Performance targets met",
    "Security scan clean",
    "Accessibility audit passed"
  ]
}
```

### Market Research Context

Use this for market analysis and competitive intelligence.

**When to use:**
- New feature planning
- Competitive analysis
- Market opportunity assessment

**Example data:**
```json
{
  "market_size": "£50M TAM in UK market",
  "competitors": ["Competitor A", "Competitor B", "Competitor C"],
  "customer_segments": ["Enterprise", "SMB", "Startups"],
  "trends": ["AI adoption", "Cloud migration", "Remote work"],
  "opportunities": ["Feature gap in competitor products", "Pricing advantage"]
}
```

## Workflow Examples

### Starting a New Work Item

1. **Create the work item**:
   ```bash
   apm work-item create "Implement user authentication" --type feature
   ```

2. **Add business context**:
   ```bash
   apm context rich create \
     --entity-type work_item \
     --entity-id 123 \
     --context-type business_pillars_context \
     --data '{
       "analysis": "Required for GDPR compliance and user data protection",
       "stakeholders": ["Legal Team", "Product Manager", "Security Team"],
       "priority": "high",
       "business_value": "Enables EU market expansion"
     }'
   ```

3. **Add technical context**:
   ```bash
   apm context rich create \
     --entity-type work_item \
     --entity-id 123 \
     --context-type technical_context \
     --data '{
       "architecture": "OAuth2 with JWT tokens",
       "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
       "dependencies": ["OAuth provider", "User database"],
       "security_requirements": ["Password hashing", "Session management", "CSRF protection"]
     }'
   ```

4. **Add quality context**:
   ```bash
   apm context rich create \
     --entity-type work_item \
     --entity-id 123 \
     --context-type quality_gates_context \
     --data '{
       "quality_requirements": ["Security", "Performance", "Usability"],
       "testing_criteria": ["Unit tests-BAK", "Security tests-BAK", "User acceptance tests-BAK"],
       "compliance": ["GDPR", "SOC2"],
       "acceptance_criteria": ["Security audit passed", "Performance targets met"]
     }'
   ```

### Converting an Idea to Work Item

1. **Create an idea**:
   ```bash
   apm idea create "Add dark mode support" --description "Users have requested dark mode for better accessibility"
   ```

2. **Add idea context**:
   ```bash
   apm context rich create \
     --entity-type idea \
     --entity-id 456 \
     --context-type idea_context \
     --data '{
       "business_case": "Improves accessibility and user experience",
       "feasibility": "High - CSS variables already implemented",
       "implementation_plan": "2-week development cycle",
       "success_metrics": ["User adoption", "Accessibility score improvement"]
     }'
   ```

3. **Convert to work item** (context transfers automatically):
   ```bash
   apm idea convert 456 --to-work-item
   ```

### Planning a Task

1. **Create a task**:
   ```bash
   apm task create "Implement login form" --type implementation --effort 4
   ```

2. **View assembled context**:
   ```bash
   apm context rich assemble --entity-type task --entity-id 789
   ```

3. **Add task-specific context**:
   ```bash
   apm context rich create \
     --entity-type task \
     --entity-id 789 \
     --context-type implementation_context \
     --data '{
       "implementation_approach": "React components with form validation",
       "code_patterns": ["Controlled components", "Custom hooks"],
       "development_guidelines": ["TypeScript required", "Unit tests-BAK required"],
       "deployment_strategy": "Feature flag enabled"
     }'
   ```

## Best Practices

### Context Data Quality

1. **Be Specific**: Provide concrete details rather than vague descriptions
2. **Include Metrics**: Add measurable success criteria where possible
3. **Update Regularly**: Keep context current as requirements change
4. **Validate Data**: Use the validation command to check completeness

### Context Organization

1. **Use Appropriate Types**: Choose the right context type for your information
2. **Hierarchical Structure**: Let context flow from project → work item → task
3. **Avoid Duplication**: Don't repeat information across multiple context types
4. **Link Related Context**: Reference related work items or tasks in context data

### Performance Tips

1. **Selective Assembly**: Only assemble context types you need
2. **Batch Operations**: Create multiple contexts in one session
3. **Cache Results**: Context assembly results can be cached for repeated use
4. **Clean Up**: Remove outdated context data regularly

## Troubleshooting

### Common Issues

**Context not showing up:**
- Check entity type and ID are correct
- Verify context was created successfully
- Use `apm context rich list` to see all contexts

**Assembly errors:**
- Ensure entity exists in database
- Check context types are valid
- Verify database connection

**Validation failures:**
- Review context data structure
- Check required fields are present
- Ensure JSON format is valid

### Getting Help

1. **Check logs**: Look for error messages in command output
2. **Validate context**: Use validation commands to check data
3. **Test with simple data**: Start with minimal context data
4. **Review examples**: Check documentation for correct data formats

## Advanced Usage

### Custom Context Types

While the system provides standard context types, you can create custom context data structures:

```json
{
  "custom_field": "Custom value",
  "project_specific": "Project-specific information",
  "team_preferences": ["Preference 1", "Preference 2"]
}
```

### Context Templates

Create reusable context templates for common scenarios:

```bash
# Save context as template
apm context rich create \
  --entity-type work_item \
  --entity-id 123 \
  --context-type business_pillars_context \
  --data @templates/business-context.json
```

### Integration with AI Agents

Rich context is automatically used by AI agents when:
- Starting new sessions
- Working on tasks
- Generating documentation
- Making decisions

The system assembles relevant context and provides it to agents for better decision-making.

## Examples and Templates

### Business Context Template

```json
{
  "analysis": "[Business analysis and rationale]",
  "stakeholders": ["[List of stakeholders]"],
  "priority": "[high|medium|low]",
  "business_value": "[Quantified business value]",
  "risks": ["[List of business risks]"],
  "success_metrics": ["[How success will be measured]"]
}
```

### Technical Context Template

```json
{
  "architecture": "[Architecture description]",
  "tech_stack": ["[List of technologies]"],
  "dependencies": ["[External dependencies]"],
  "performance_requirements": ["[Performance criteria]"],
  "security_requirements": ["[Security requirements]"],
  "scalability_considerations": ["[Scalability factors]"]
}
```

### Quality Context Template

```json
{
  "quality_requirements": ["[Quality aspects to consider]"],
  "testing_criteria": ["[Testing requirements]"],
  "compliance": ["[Compliance requirements]"],
  "acceptance_criteria": ["[Acceptance criteria]"],
  "review_process": "[Review and approval process]"
}
```

## Document Management Integration

APM (Agent Project Manager) includes a comprehensive document management system that complements rich context by linking actual documents to your entities.

### Why Use Document Management?

While rich context provides structured data, documents provide:
- **Detailed Specifications**: Full technical specifications, designs, and architecture diagrams
- **External Artifacts**: PDFs, presentations, spreadsheets, and other file formats
- **Version History**: Track document evolution over time
- **File Validation**: Ensure documents exist and are accessible
- **Metadata Tracking**: Document type, format, creator, file size, and content hash

### Quick Start with Documents

**Add a document to a work item:**
```bash
apm document add \
  --entity-type=work-item \
  --entity-id=123 \
  --file-path="docs/architecture/system-design.md" \
  --type=architecture \
  --title="System Architecture Design"
```

**List all documents for an entity:**
```bash
apm document list --entity-type=work-item --entity-id=123
```

**Show document details:**
```bash
apm document show 25 --include-content
```

### Document Types

The system supports 24 document types organized by category:

**Planning Documents:**
- `idea` - Initial concepts and proposals
- `requirements` - Requirements specifications
- `user_story` - User stories and narratives
- `stakeholder_analysis` - Stakeholder mapping
- `market_research_report` - Market research findings
- `competitive_analysis` - Competitive landscape analysis

**Architecture & Design:**
- `architecture` - System architecture documents
- `design` - Design specifications and diagrams
- `technical_specification` - Technical specifications
- `adr` - Architecture Decision Records

**Implementation:**
- `specification` - General specifications
- `api_doc` - API documentation
- `implementation_plan` - Implementation planning
- `refactoring_guide` - Refactoring guidelines

**Testing & Quality:**
- `test_plan` - Testing plans and strategies
- `quality_gates_specification` - Quality gate definitions

**Operations:**
- `deployment_guide` - Deployment procedures
- `migration_guide` - Migration and upgrade guides
- `runbook` - Operational runbooks
- `admin_guide` - Administrator documentation

**User-Facing:**
- `user_guide` - User documentation
- `troubleshooting` - Troubleshooting guides
- `changelog` - Release notes

### Auto-Detection Features

The system automatically detects document metadata:

**Type Detection** from path patterns:
```bash
# Path contains "architecture/" → auto-detected as architecture
docs/architecture/payment-system.md

# Path contains "api/" → auto-detected as api_doc
docs/api/payment-api-spec.yaml

# Path contains "requirements/" → auto-detected as requirements
docs/requirements/payment-requirements.md
```

**Format Detection** from file extensions:
```bash
.md → markdown
.pdf → pdf
.yaml → yaml
.json → json
.html → html
.docx → docx
.xlsx → xlsx
.pptx → pptx
```

**Title Generation** from filename:
```bash
# Input: api-specification.md
# Output: "Api Specification"
```

### Workflow Integration

**Combine with Rich Context:**

1. **Create work item with rich context**:
   ```bash
   # Create work item
   apm work-item create "Payment System" --type feature

   # Add business context
   apm context rich create \
     --entity-type work_item \
     --entity-id 123 \
     --context-type business_pillars_context \
     --data '{"analysis": "Customer requested feature"}'
   ```

2. **Link supporting documents**:
   ```bash
   # Add requirements document
   apm document add \
     --entity-type=work-item \
     --entity-id=123 \
     --file-path="docs/requirements/payment-requirements.md"

   # Add architecture document
   apm document add \
     --entity-type=work-item \
     --entity-id=123 \
     --file-path="docs/architecture/payment-architecture.md"
   ```

3. **View complete context**:
   ```bash
   # Rich context data
   apm context rich assemble --entity-type work_item --entity-id 123

   # Document references
   apm document list --entity-type=work-item --entity-id=123

   # Work item with everything
   apm work-item show 123
   ```

### Document Management Commands

**Add Documents:**
```bash
# With auto-detection
apm document add --entity-type=work-item --entity-id=123 \
  --file-path="docs/design/user-flow.md"

# With explicit metadata
apm document add --entity-type=task --entity-id=456 \
  --file-path="docs/implementation/auth-impl.md" \
  --type=implementation_plan \
  --title="Authentication Implementation" \
  --description="Detailed implementation steps"
```

**List Documents:**
```bash
# All documents for entity
apm document list --entity-type=work-item --entity-id=123

# Filter by type
apm document list --type=architecture

# Filter by format
apm document list --format=pdf

# JSON output for scripting
apm document list --format=json
```

**Update Documents:**
```bash
# Update metadata
apm document update 25 --title="Updated Title"

# Update file path
apm document update 25 --file-path="docs/new-location.md"

# Update multiple fields
apm document update 25 \
  --title="New Title" \
  --type=design \
  --description="Updated design document"
```

**Delete Documents:**
```bash
# Delete reference (keep file)
apm document delete 25

# Delete reference and file
apm document delete 25 --delete-file
```

### Best Practices

**1. Organize Files by Type:**
```
docs/
├── architecture/     # Architecture documents
├── design/          # Design specifications
├── api/            # API documentation
├── requirements/   # Requirements
├── testing/        # Test plans
└── user-guides/    # User documentation
```

**2. Use Auto-Detection:**
```bash
# ✅ Good - Let system auto-detect
apm document add --entity-type=work-item --entity-id=123 \
  --file-path="docs/architecture/system-design.md"

# ❌ Unnecessary - Manual specification
apm document add --entity-type=work-item --entity-id=123 \
  --file-path="docs/architecture/system-design.md" \
  --type=architecture --format=markdown --title="System Design"
```

**3. Add Descriptions:**
```bash
# Provide context through descriptions
apm document add --entity-type=work-item --entity-id=123 \
  --file-path="docs/architecture/payment-system.md" \
  --description="Payment system architecture including fraud detection, \
processing, and reconciliation components"
```

**4. Link Documents Early:**
```bash
# Add documents when creating entities
apm work-item add --title="Payment System" --type=feature
apm document add --entity-type=work-item --entity-id=123 \
  --file-path="docs/requirements/payment-requirements.md"
```

**5. Keep Documents Updated:**
```bash
# Update metadata when content changes
apm document update 25 \
  --title="Payment API Specification v2.0" \
  --description="Updated with webhook endpoints"
```

### Document Quality Gates

Use documents to support quality gates:

```bash
# 1. Add quality gates specification
apm document add \
  --entity-type=work-item \
  --entity-id=123 \
  --file-path="docs/quality/payment-quality-gates.yaml" \
  --type=quality_gates_specification

# 2. Add test results
apm document add \
  --entity-type=work-item \
  --entity-id=123 \
  --file-path="docs/testing/payment-test-results.md" \
  --type=test_plan

# 3. Validate work item
apm work-item validate 123
```

### Common Workflows

**Feature Development:**
```bash
# 1. Create work item
apm work-item add --title="Feature" --type=feature

# 2. Add requirements
apm document add --entity-type=work-item --entity-id=<id> \
  --file-path="docs/requirements/<name>.md"

# 3. Add architecture
apm document add --entity-type=work-item --entity-id=<id> \
  --file-path="docs/architecture/<name>.md"

# 4. Add design
apm document add --entity-type=work-item --entity-id=<id> \
  --file-path="docs/design/<name>.md"

# 5. Add implementation plan
apm document add --entity-type=work-item --entity-id=<id> \
  --file-path="docs/implementation/<name>.md"
```

**Idea to Work Item:**
```bash
# 1. Create idea with documents
apm idea create "Mobile App"
apm document add --entity-type=idea --entity-id=<id> \
  --file-path="docs/ideas/mobile-concept.md"

# 2. Convert to work item (documents transfer)
apm idea create-work-item <id>

# 3. Add work item documents
apm document add --entity-type=work-item --entity-id=<new-id> \
  --file-path="docs/architecture/mobile-architecture.md"
```

### Troubleshooting

**File Not Found:**
```bash
# Verify file exists
ls -la docs/api-spec.md

# Use relative path from project root
apm document add --entity-type=work-item --entity-id=5 \
  --file-path="docs/api-spec.md"  # Relative path
```

**Wrong Type Auto-Detection:**
```bash
# Option 1: Specify type explicitly
apm document add --entity-type=work-item --entity-id=5 \
  --file-path="docs/my-design.md" \
  --type=design

# Option 2: Reorganize files to match patterns
mv docs/my-design.md docs/design/my-design.md
```

**Entity Not Found:**
```bash
# Verify entity exists
apm work-item show 5
apm task show 12

# Create entity first if needed
apm work-item add --title="New Feature" --type=feature
```

### See Also

- **Detailed Documentation**: `agentpm/cli/commands/document/README.md`
- **Examples**: `docs/examples/document-management-cli.md`
- **Context Assembly**: `apm context show`
- **Work Items**: `apm work-item show <id>`

## Conclusion

The Rich Context System combined with Document Management provides powerful capabilities for managing comprehensive project context. By following this guide and using both systems effectively, you can:

- Provide better context to AI agents (rich context + documents)
- Improve project documentation (structured data + file references)
- Ensure consistent quality standards (quality gates + test documents)
- Track business value and impact (business context + research documents)
- Maintain stakeholder alignment (stakeholder context + communication documents)

Start with basic context types and document linking, then gradually add more detailed information as you become comfortable with the system. The rich context and document references will help your AI agents work more effectively and provide better results for your projects.

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Rich Context](advanced/memory-system.md)
- [➡️ Next: Detection Packs](advanced/detection-packs.md)

---
