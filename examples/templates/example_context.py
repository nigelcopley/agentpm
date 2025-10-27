"""
Example: Building Template Context

This example demonstrates how to build a complete TemplateContext
for rendering provider configurations.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from agentpm.providers.base.context import (
    TemplateContext,
    ProjectContext,
    AgentContext,
    RuleContext,
    ProviderConfig,
    EnforcementLevel,
)


def build_sample_context() -> TemplateContext:
    """
    Build a sample template context for demonstration.

    Returns:
        Validated TemplateContext ready for rendering
    """

    # 1. Project metadata
    project = ProjectContext(
        id=1,
        name="E-Commerce Platform",
        path=Path("/home/user/projects/ecommerce"),
        business_domain="E-Commerce",
        app_type="Web Application",
        languages=["Python", "TypeScript"],
        frameworks=["Django", "React", "PostgreSQL"],
        database="PostgreSQL",
        testing_frameworks=["pytest", "Jest"],
        methodology="Agile",
        tech_stack=[
            "Python 3.11",
            "Django 4.2",
            "React 18",
            "PostgreSQL 15",
            "Redis",
            "Celery",
        ],
    )

    # 2. Agents (3-tier architecture)

    # Tier 3: Orchestrator
    orchestrator = AgentContext(
        id=1,
        role="master-orchestrator",
        display_name="Master Orchestrator",
        description="Coordinates all work across phases",
        tier=3,
        agent_type="orchestrator",
        capabilities=[
            "Phase routing",
            "Agent coordination",
            "Gate validation",
            "Strategic planning",
        ],
        is_active=True,
        delegates_to=["implementation-orch", "testing-specialist"],
        activation_triggers=[
            "New work item created",
            "Phase transition needed",
            "Cross-agent coordination required",
        ],
        mcp_tools={
            "routing": [
                {"name": "apm-context", "usage": "Load project context"},
                {"name": "apm-agents", "usage": "Query available agents"},
            ],
        },
        parallel_capable=True,
        metadata={
            "priority": 100,
            "always_active": True,
        },
    )

    # Tier 2: Specialists
    implementer = AgentContext(
        id=2,
        role="backend-implementer",
        display_name="Backend Implementation Specialist",
        description="Django backend implementation expert",
        tier=2,
        agent_type="implementer",
        capabilities=[
            "Django models and views",
            "REST API development",
            "Database design",
            "Background tasks (Celery)",
        ],
        is_active=True,
        reports_to="master-orchestrator",
        delegates_to=["database-developer", "api-tester"],
        activation_triggers=[
            "IMPLEMENTATION task assigned",
            "Backend feature requested",
            "API endpoint needed",
        ],
        mcp_tools={
            "development": [
                {"name": "Read", "usage": "Read existing code"},
                {"name": "Edit", "usage": "Modify code files"},
                {"name": "Bash", "usage": "Run Django commands"},
            ],
        },
        parallel_capable=False,
        metadata={
            "specialization": "Django + PostgreSQL",
            "experience_level": "expert",
        },
    )

    tester = AgentContext(
        id=3,
        role="testing-specialist",
        display_name="Testing Quality Specialist",
        description="Comprehensive testing expert (Python + JS)",
        tier=2,
        agent_type="tester",
        capabilities=[
            "pytest test suites",
            "Jest unit tests",
            "Integration testing",
            "Coverage analysis",
        ],
        is_active=True,
        reports_to="master-orchestrator",
        activation_triggers=[
            "TESTING task assigned",
            "Code review requested",
            "Coverage below threshold",
        ],
        mcp_tools={
            "testing": [
                {"name": "Bash", "usage": "Run test commands"},
                {"name": "Read", "usage": "Analyze test results"},
            ],
        },
        parallel_capable=True,
        metadata={
            "coverage_target": 90,
            "test_frameworks": ["pytest", "Jest"],
        },
    )

    # Tier 1: Sub-agents
    analyzer = AgentContext(
        id=4,
        role="code-analyzer",
        display_name="Code Analysis Sub-Agent",
        description="Analyzes code quality and patterns",
        tier=1,
        agent_type="analyzer",
        capabilities=[
            "Static analysis",
            "Pattern detection",
            "Complexity metrics",
            "Security scanning",
        ],
        is_active=True,
        reports_to="testing-specialist",
        activation_triggers=[
            "Quality gate validation",
            "Pre-commit analysis",
        ],
        parallel_capable=True,
        metadata={
            "analysis_depth": "comprehensive",
        },
    )

    agents = [orchestrator, implementer, tester, analyzer]

    # 3. Rules (from database)

    rules = [
        RuleContext(
            rule_id="DP-001",
            name="time-boxing",
            description="IMPLEMENTATION tasks must be ≤4.0 hours. Break larger tasks into smaller units.",
            category="development_principles",
            enforcement_level=EnforcementLevel.BLOCK,
            priority=100,
            config={
                "max_hours": 4.0,
                "task_types": ["IMPLEMENTATION"],
            },
        ),
        RuleContext(
            rule_id="TES-004",
            name="testing-quality",
            description="Minimum 90% test coverage required for all new code.",
            category="testing",
            enforcement_level=EnforcementLevel.BLOCK,
            priority=95,
            config={
                "min_coverage": 90,
                "exclude_patterns": ["migrations/*", "tests/*"],
            },
        ),
        RuleContext(
            rule_id="SEC-001",
            name="input-validation",
            description="All external inputs must be validated using Pydantic models.",
            category="security",
            enforcement_level=EnforcementLevel.BLOCK,
            priority=90,
            config={
                "validation_framework": "pydantic",
            },
        ),
        RuleContext(
            rule_id="DOC-020",
            name="database-first-documents",
            description="All documentation must be created via 'apm document add' command.",
            category="documentation",
            enforcement_level=EnforcementLevel.BLOCK,
            priority=85,
        ),
        RuleContext(
            rule_id="CI-002",
            name="context-quality",
            description="Work items require ≥70% 6W confidence before implementation.",
            category="continuous_integration",
            enforcement_level=EnforcementLevel.WARN,
            priority=80,
            config={
                "min_confidence": 0.70,
                "six_w_fields": ["WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW"],
            },
        ),
    ]

    # 4. Provider configuration
    provider = ProviderConfig(
        provider_name="anthropic",
        provider_version="1.0.0",
        features_enabled={
            "agents": True,
            "rules": True,
            "hooks": True,
            "memory_sync": False,
        },
        custom_settings={
            "model": "claude-sonnet-4-5",
            "max_tokens": 200000,
        },
    )

    # 5. Build complete context
    context = TemplateContext(
        project=project,
        agents=agents,
        rules=rules,
        provider=provider,
        metadata={
            "generator": "APM (Agent Project Manager)",
            "environment": "development",
            "features": ["hexagonal-architecture", "database-first"],
        },
        generated_at=datetime.utcnow(),
    )

    return context


def validate_context_example():
    """
    Demonstrate Pydantic validation catching errors.
    """
    try:
        # Invalid tier
        invalid_agent = AgentContext(
            role="invalid",
            display_name="Invalid Agent",
            description="Test",
            tier=5,  # Invalid: must be 1, 2, or 3
            agent_type="test",
        )
    except ValueError as e:
        print(f"Validation error caught: {e}")

    try:
        # Invalid enforcement level
        invalid_rule = RuleContext(
            rule_id="INVALID",  # Invalid: must match pattern
            name="test",
            description="Test rule",
            category="test",
            enforcement_level="INVALID",  # Invalid enum value
            priority=50,
        )
    except ValueError as e:
        print(f"Validation error caught: {e}")


def cross_field_validation_example():
    """
    Demonstrate cross-field validation (agent delegation).
    """
    try:
        # Agent delegates to unknown agent
        context = TemplateContext(
            project=ProjectContext(
                id=1,
                name="Test",
                path=Path("/tmp/test"),
            ),
            agents=[
                AgentContext(
                    role="orchestrator",
                    display_name="Orchestrator",
                    description="Test",
                    tier=3,
                    agent_type="orchestrator",
                    delegates_to=["unknown-agent"],  # This agent doesn't exist
                ),
            ],
            rules=[],
            provider=ProviderConfig(
                provider_name="test",
                provider_version="1.0.0",
            ),
        )
    except ValueError as e:
        print(f"Cross-field validation error caught: {e}")


if __name__ == "__main__":
    # Build sample context
    context = build_sample_context()

    print("=" * 60)
    print("SAMPLE TEMPLATE CONTEXT")
    print("=" * 60)
    print()

    print(f"Project: {context.project.name}")
    print(f"Languages: {', '.join(context.project.languages)}")
    print(f"Frameworks: {', '.join(context.project.frameworks)}")
    print()

    print(f"Agents: {len(context.agents)}")
    for agent in context.agents:
        print(f"  - {agent.role} (Tier {agent.tier}): {agent.display_name}")
    print()

    print(f"Rules: {len(context.rules)}")
    for rule in context.rules:
        print(f"  - {rule.rule_id}: {rule.name} ({rule.enforcement_level})")
    print()

    print(f"Provider: {context.provider.provider_name} v{context.provider.provider_version}")
    print(f"Generated: {context.generated_at.isoformat()}")
    print()

    # Demonstrate validation
    print("=" * 60)
    print("VALIDATION EXAMPLES")
    print("=" * 60)
    print()

    validate_context_example()
    print()

    cross_field_validation_example()
