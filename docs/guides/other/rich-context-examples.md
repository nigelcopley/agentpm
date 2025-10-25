# Rich Context System Examples and Best Practices

## Overview

This document provides practical examples and best practices for using the Rich Context System in APM (Agent Project Manager). These examples demonstrate real-world scenarios and show how to effectively use rich context to improve AI agent performance and project outcomes.

## Example Scenarios

### Scenario 1: E-commerce Feature Development

#### Context: Adding Product Recommendations

**Business Context:**
```json
{
  "analysis": "Product recommendations will increase average order value by 15% and improve user engagement. This addresses customer feedback about difficulty finding related products.",
  "stakeholders": [
    "Product Manager - Sarah Chen",
    "Engineering Lead - Mike Rodriguez", 
    "Data Scientist - Alex Kim",
    "UX Designer - Lisa Wang"
  ],
  "priority": "high",
  "business_value": "Expected £2M additional revenue annually",
  "risks": [
    "Algorithm performance impact on page load times",
    "Privacy concerns with user data usage",
    "Integration complexity with existing recommendation engine"
  ],
  "success_metrics": [
    "15% increase in average order value",
    "20% improvement in click-through rate",
    "Page load time remains under 2 seconds"
  ]
}
```

**Technical Context:**
```json
{
  "architecture": "Microservices with real-time recommendation API",
  "tech_stack": [
    "Python 3.11",
    "FastAPI",
    "PostgreSQL with pgvector",
    "Redis for caching",
    "Apache Kafka for events"
  ],
  "dependencies": [
    "Existing product catalog service",
    "User behavior tracking service",
    "Machine learning recommendation engine",
    "CDN for static assets"
  ],
  "performance_requirements": [
    "API response time < 100ms",
    "Recommendation generation < 50ms",
    "Cache hit rate > 90%",
    "System availability 99.9%"
  ],
  "security_requirements": [
    "User data anonymization",
    "GDPR compliance for EU users",
    "Rate limiting on API endpoints",
    "Input validation and sanitization"
  ],
  "scalability_considerations": [
    "Horizontal scaling of recommendation service",
    "Database sharding for product data",
    "CDN distribution for global users",
    "Auto-scaling based on traffic patterns"
  ]
}
```

**Quality Gates Context:**
```json
{
  "quality_requirements": [
    "Performance",
    "Security", 
    "Usability",
    "Accessibility",
    "Data Privacy"
  ],
  "testing_criteria": [
    "Unit tests-BAK with >90% coverage",
    "Integration tests-BAK for API endpoints",
    "Performance tests-BAK under load",
    "Security penetration testing",
    "A/B testing for recommendation algorithms",
    "Accessibility testing (WCAG 2.1 AA)"
  ],
  "compliance": [
    "GDPR",
    "CCPA", 
    "PCI DSS",
    "SOC 2 Type II"
  ],
  "acceptance_criteria": [
    "All performance targets met",
    "Security audit passed",
    "Accessibility compliance verified",
    "A/B test shows statistical significance",
    "Code review approved by 2+ engineers"
  ],
  "review_process": "Technical design review → Code review → QA testing → Security review → Product acceptance"
}
```

### Scenario 2: Mobile App Feature

#### Context: Push Notification System

**Business Context:**
```json
{
  "analysis": "Push notifications will re-engage dormant users and drive 25% increase in daily active users. Critical for user retention strategy.",
  "stakeholders": [
    "Product Manager - Jennifer Liu",
    "Mobile Team Lead - David Park",
    "Backend Engineer - Maria Santos",
    "Marketing Manager - Tom Wilson"
  ],
  "priority": "medium",
  "business_value": "£500K additional revenue from re-engaged users",
  "risks": [
    "User opt-out rates if notifications are too frequent",
    "Platform-specific implementation complexity",
    "Battery drain concerns on mobile devices"
  ],
  "success_metrics": [
    "25% increase in daily active users",
    "Notification open rate > 15%",
    "User opt-out rate < 5%",
    "App store rating maintained above 4.5"
  ]
}
```

**Technical Context:**
```json
{
  "architecture": "Event-driven system with Firebase Cloud Messaging",
  "tech_stack": [
    "React Native",
    "Node.js",
    "Firebase Cloud Messaging",
    "MongoDB",
    "Redis",
    "AWS SNS"
  ],
  "dependencies": [
    "User preference service",
    "Content management system",
    "Analytics tracking service",
    "A/B testing platform"
  ],
  "performance_requirements": [
    "Notification delivery < 5 seconds",
    "Batch processing of 10K+ notifications",
    "99.5% delivery success rate",
    "Real-time user preference updates"
  ],
  "security_requirements": [
    "User consent management",
    "Data encryption in transit and at rest",
    "Secure token management",
    "Rate limiting on notification API"
  ]
}
```

### Scenario 3: Data Analytics Dashboard

#### Context: Real-time Analytics Platform

**Business Context:**
```json
{
  "analysis": "Real-time analytics dashboard will enable data-driven decision making and improve operational efficiency by 30%.",
  "stakeholders": [
    "Head of Data - Rachel Green",
    "Product Manager - James Brown",
    "Frontend Engineer - Emma Davis",
    "Data Engineer - Carlos Mendez"
  ],
  "priority": "high",
  "business_value": "£1M cost savings through improved operational efficiency",
  "risks": [
    "Data accuracy and consistency issues",
    "Performance impact on production systems",
    "Complex data visualization requirements"
  ],
  "success_metrics": [
    "30% improvement in operational efficiency",
    "Dashboard load time < 3 seconds",
    "Data accuracy > 99.9%",
    "User adoption rate > 80%"
  ]
}
```

**Technical Context:**
```json
{
  "architecture": "Lambda architecture with real-time and batch processing",
  "tech_stack": [
    "React",
    "D3.js",
    "Apache Kafka",
    "Apache Spark",
    "ClickHouse",
    "Redis",
    "Docker"
  ],
  "dependencies": [
    "Data warehouse",
    "Event streaming platform",
    "User authentication service",
    "Configuration management system"
  ],
  "performance_requirements": [
    "Dashboard load time < 3 seconds",
    "Real-time data updates every 30 seconds",
    "Support for 1000+ concurrent users",
    "Data processing latency < 1 minute"
  ],
  "security_requirements": [
    "Role-based access control",
    "Data encryption",
    "Audit logging",
    "GDPR compliance for EU data"
  ]
}
```

## Best Practices

### 1. Context Data Quality

#### Do: Provide Specific, Actionable Information

**Good Example:**
```json
{
  "analysis": "This feature addresses 3 specific customer pain points: (1) 40% of users abandon checkout due to slow payment processing, (2) 25% of users can't find their preferred payment method, (3) 15% of users experience payment failures without clear error messages.",
  "stakeholders": [
    "Product Manager - Sarah Chen (sarah.chen@company.com)",
    "Engineering Lead - Mike Rodriguez (mike.rodriguez@company.com)",
    "Payment Team Lead - Alex Kim (alex.kim@company.com)"
  ],
  "priority": "high",
  "business_value": "Expected 20% reduction in checkout abandonment, resulting in £500K additional monthly revenue",
  "success_metrics": [
    "Checkout abandonment rate reduced from 40% to 32%",
    "Payment method coverage increased to 95%",
    "Payment failure rate reduced from 15% to 8%",
    "Customer satisfaction score improved by 0.5 points"
  ]
}
```

**Bad Example:**
```json
{
  "analysis": "This feature is important for users",
  "stakeholders": ["Product team", "Engineering team"],
  "priority": "high",
  "business_value": "Will help the business",
  "success_metrics": ["Users will like it"]
}
```

#### Do: Include Quantifiable Metrics

**Good Example:**
```json
{
  "performance_requirements": [
    "API response time < 200ms (95th percentile)",
    "Database query time < 50ms (average)",
    "System availability 99.9% (monthly)",
    "Concurrent users supported: 10,000"
  ],
  "success_metrics": [
    "User engagement increased by 25% (measured by daily active users)",
    "Conversion rate improved by 15% (measured by completed transactions)",
    "Customer satisfaction score improved by 0.8 points (measured by NPS survey)"
  ]
}
```

### 2. Context Organization

#### Do: Use Hierarchical Context Structure

```python
# Project-level context (applies to all work items)
project_context = {
    "company_goals": "Increase market share by 20% in Q4",
    "technical_standards": "All APIs must use OpenAPI 3.0",
    "security_policy": "GDPR compliance required for all features"
}

# Work item-level context (applies to all tasks in work item)
work_item_context = {
    "feature_scope": "User authentication and authorization",
    "target_users": "Enterprise customers",
    "integration_requirements": "Must integrate with existing SSO system"
}

# Task-level context (specific to individual task)
task_context = {
    "implementation_details": "Use OAuth2 with JWT tokens",
    "testing_requirements": "Unit tests-BAK with >90% coverage",
    "deployment_strategy": "Blue-green deployment"
}
```

#### Do: Link Related Context

```json
{
  "analysis": "This feature is part of the Q4 user engagement initiative (see WI-45) and builds on the authentication system implemented in WI-38.",
  "dependencies": [
    "WI-38: User Authentication System (completed)",
    "WI-42: Database Performance Optimization (in progress)",
    "WI-45: Q4 User Engagement Initiative (planned)"
  ],
  "related_features": [
    "User profile management (WI-39)",
    "Notification preferences (WI-41)",
    "Activity tracking (WI-43)"
  ]
}
```

### 3. Context Assembly Best Practices

#### Do: Selective Context Assembly

```python
# Only assemble needed context types for performance
context = assembly_service.assemble_rich_context(
    entity_type=EntityType.TASK,
    entity_id=task_id,
    context_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT
        # Don't assemble all context types if not needed
    ]
)
```

#### Do: Cache Assembled Context

```python
# Cache context for frequently accessed entities
@lru_cache(maxsize=100)
def get_cached_context(entity_type: EntityType, entity_id: int):
    return assembly_service.assemble_rich_context(
        entity_type=entity_type,
        entity_id=entity_id
    )
```

### 4. Context Validation

#### Do: Validate Context Completeness

```python
# Check context completeness before starting work
validation_result = context_methods.validate_rich_context_completeness(
    service=db,
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item_id,
    required_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT,
        ContextType.QUALITY_GATES_CONTEXT
    ]
)

if validation_result['completeness_score'] < 0.8:
    print(f"Warning: Context completeness is {validation_result['completeness_score']:.2f}")
    print(f"Missing types: {validation_result['missing_types']}")
```

### 5. Context for AI Agents

#### Do: Provide Agent-Specific Context

```python
# Assemble context optimized for AI agent consumption
agent_context = {
    "task_summary": "Implement user authentication API endpoint",
    "business_context": {
        "why_important": "Required for GDPR compliance and user data protection",
        "stakeholders": ["Legal Team", "Product Manager", "Security Team"],
        "success_criteria": ["GDPR compliance", "Security audit passed"]
    },
    "technical_context": {
        "implementation_approach": "OAuth2 with JWT tokens",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "performance_requirements": ["<200ms API response", "99.9% uptime"]
    },
    "quality_context": {
        "testing_requirements": ["Unit tests-BAK >90% coverage", "Security tests-BAK"],
        "review_process": "Code review → Security review → Product acceptance"
    }
}
```

#### Do: Include Implementation Guidance

```json
{
  "implementation_context": {
    "implementation_approach": "Test-driven development with incremental delivery",
    "code_patterns": [
      "Repository pattern for data access",
      "Factory pattern for service creation",
      "Observer pattern for event handling"
    ],
    "development_guidelines": [
      "Follow existing code style and conventions",
      "Write comprehensive unit tests-BAK",
      "Document all public APIs",
      "Use dependency injection for testability"
    ],
    "deployment_strategy": "Blue-green deployment with feature flags",
    "monitoring": [
      "Application performance monitoring",
      "Error tracking and alerting",
      "Business metrics tracking"
    ]
  }
}
```

## Common Patterns

### Pattern 1: Feature Development Workflow

```python
# 1. Create work item with business context
work_item = create_work_item("User Authentication Feature")

business_context = create_rich_context(
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item.id,
    context_type=ContextType.BUSINESS_PILLARS_CONTEXT,
    context_data={
        "analysis": "Required for GDPR compliance",
        "stakeholders": ["Legal Team", "Product Manager"],
        "priority": "high",
        "business_value": "Enables EU market expansion"
    }
)

# 2. Add technical context
technical_context = create_rich_context(
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item.id,
    context_type=ContextType.TECHNICAL_CONTEXT,
    context_data={
        "architecture": "OAuth2 with JWT tokens",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "security_requirements": ["Password hashing", "Session management"]
    }
)

# 3. Create tasks with inherited context
task = create_task("Implement login endpoint", work_item_id=work_item.id)

# 4. Assemble complete context for AI agent
complete_context = assembly_service.assemble_rich_context(
    entity_type=EntityType.TASK,
    entity_id=task.id
)
```

### Pattern 2: Idea to Work Item Conversion

```python
# 1. Create idea with context
idea = create_idea("Dark Mode Support")

idea_context = create_rich_context(
    entity_type=EntityType.IDEA,
    entity_id=idea.id,
    context_type=ContextType.IDEA_CONTEXT,
    context_data={
        "business_case": "Improves accessibility and user experience",
        "feasibility": "High - CSS variables already implemented",
        "implementation_plan": "2-week development cycle",
        "success_metrics": ["User adoption", "Accessibility score improvement"]
    }
)

# 2. Convert to work item (context transfers automatically)
work_item = convert_idea_to_work_item(idea.id, transfer_context=True)

# 3. Add additional context for work item
work_item_context = create_rich_context(
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item.id,
    context_type=ContextType.TECHNICAL_CONTEXT,
    context_data={
        "implementation_approach": "CSS custom properties with theme switching",
        "browser_support": "Modern browsers with CSS custom properties support",
        "performance_impact": "Minimal - CSS-only solution"
    }
)
```

### Pattern 3: Quality Gates Integration

```python
# 1. Define quality requirements
quality_context = create_rich_context(
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item.id,
    context_type=ContextType.QUALITY_GATES_CONTEXT,
    context_data={
        "quality_requirements": ["Performance", "Security", "Accessibility"],
        "testing_criteria": [
            "Unit tests-BAK >90% coverage",
            "Integration tests-BAK for all endpoints",
            "Security penetration testing",
            "Accessibility testing (WCAG 2.1 AA)"
        ],
        "compliance": ["GDPR", "SOC2"],
        "acceptance_criteria": [
            "All tests-BAK pass",
            "Performance targets met",
            "Security audit passed",
            "Accessibility compliance verified"
        ]
    }
)

# 2. Validate quality gates before completion
validation_result = validate_rich_context_completeness(
    entity_type=EntityType.WORK_ITEM,
    entity_id=work_item.id,
    required_types=[ContextType.QUALITY_GATES_CONTEXT]
)

if validation_result['is_complete']:
    # Proceed with work item completion
    complete_work_item(work_item.id)
else:
    # Address missing quality requirements
    print(f"Missing quality requirements: {validation_result['missing_types']}")
```

## Anti-Patterns to Avoid

### 1. Vague or Generic Context

**Avoid:**
```json
{
  "analysis": "This is important",
  "stakeholders": ["Team"],
  "priority": "high",
  "business_value": "Good for business"
}
```

**Instead:**
```json
{
  "analysis": "This feature addresses the top customer complaint about slow page loading, which affects 60% of our users and results in 25% cart abandonment.",
  "stakeholders": [
    "Product Manager - Sarah Chen (primary decision maker)",
    "Engineering Lead - Mike Rodriguez (technical implementation)",
    "UX Designer - Lisa Wang (user experience)"
  ],
  "priority": "high",
  "business_value": "Expected 25% reduction in cart abandonment, resulting in £200K additional monthly revenue"
}
```

### 2. Overly Complex Context Data

**Avoid:**
```json
{
  "analysis": "This feature is part of a complex multi-phase initiative that involves multiple teams and systems, with various dependencies and requirements that need to be coordinated across different time zones and stakeholders, while maintaining compliance with various regulations and standards..."
}
```

**Instead:**
```json
{
  "analysis": "This feature enables real-time collaboration for document editing",
  "dependencies": [
    "WebSocket infrastructure (completed)",
    "Document storage service (in progress)",
    "User permission system (planned)"
  ],
  "compliance": ["GDPR", "SOC2"]
}
```

### 3. Missing Context Updates

**Avoid:**
- Creating context once and never updating it
- Not reflecting changes in requirements or scope
- Ignoring feedback from stakeholders

**Instead:**
- Regularly review and update context
- Track context changes in version control
- Validate context accuracy with stakeholders

### 4. Context Duplication

**Avoid:**
- Repeating the same information across multiple context types
- Storing redundant data in different context entries
- Not leveraging hierarchical context inheritance

**Instead:**
- Use hierarchical context structure
- Reference related context rather than duplicating
- Leverage context inheritance from project → work item → task

## Performance Optimization

### 1. Selective Context Assembly

```python
# Only assemble needed context types
context = assembly_service.assemble_rich_context(
    entity_type=EntityType.TASK,
    entity_id=task_id,
    context_types=[
        ContextType.BUSINESS_PILLARS_CONTEXT,
        ContextType.TECHNICAL_CONTEXT
        # Don't assemble all types if not needed
    ]
)
```

### 2. Context Caching

```python
# Cache frequently accessed context
@lru_cache(maxsize=100)
def get_cached_context(entity_type: EntityType, entity_id: int):
    return assembly_service.assemble_rich_context(
        entity_type=entity_type,
        entity_id=entity_id
    )
```

### 3. Batch Operations

```python
# Create multiple contexts in one transaction
with db.transaction():
    for context_data in contexts_to_create:
        create_rich_context(
            service=db,
            entity_type=context_data['entity_type'],
            entity_id=context_data['entity_id'],
            context_type=context_data['context_type'],
            context_data=context_data['data']
        )
```

## Conclusion

These examples and best practices demonstrate how to effectively use the Rich Context System to:

1. **Provide Comprehensive Context**: Give AI agents the information they need to make informed decisions
2. **Maintain Data Quality**: Ensure context data is specific, actionable, and up-to-date
3. **Optimize Performance**: Use selective assembly and caching for better performance
4. **Follow Best Practices**: Organize context hierarchically and avoid common pitfalls

By following these patterns and practices, you can maximize the value of the Rich Context System and improve the effectiveness of AI agents working on your projects.


