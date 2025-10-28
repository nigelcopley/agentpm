"""
Tests for Subagent Registry

Tests subagent registration, lookup, and invocation guide generation.
"""

import pytest
from agentpm.providers.anthropic.claude_code.runtime.subagents import (
    SubagentRegistry,
    SubagentSpec,
    SubagentCapability,
    get_subagent_registry,
    reset_subagent_registry,
)


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reset_subagent_registry()
    reg = get_subagent_registry()
    yield reg
    reg.clear()


@pytest.fixture
def sample_spec():
    """Create sample subagent spec."""
    return SubagentSpec(
        name="test-implementer",
        description="Creates comprehensive unit tests",
        capabilities=[SubagentCapability.TESTING],
        tier=1,
        invocation_template="Create tests for [component]"
    )


class TestSubagentRegistryBasics:
    """Test basic registry operations."""

    def test_registry_singleton(self):
        """Registry should be singleton."""
        reset_subagent_registry()
        reg1 = get_subagent_registry()
        reg2 = get_subagent_registry()
        assert reg1 is reg2

    def test_registry_initialization(self, registry):
        """Registry should initialize empty."""
        assert len(registry.list_subagents()) == 0

    def test_register_subagent(self, registry, sample_spec):
        """Should register subagent successfully."""
        registry.register_subagent(sample_spec)
        assert len(registry.list_subagents()) == 1
        assert registry.get_subagent("test-implementer") is not None

    def test_register_duplicate_subagent(self, registry, sample_spec):
        """Should raise error on duplicate registration."""
        registry.register_subagent(sample_spec)
        with pytest.raises(ValueError, match="already registered"):
            registry.register_subagent(sample_spec)

    def test_unregister_subagent(self, registry, sample_spec):
        """Should unregister subagent successfully."""
        registry.register_subagent(sample_spec)
        registry.unregister_subagent("test-implementer")
        assert len(registry.list_subagents()) == 0

    def test_unregister_nonexistent_subagent(self, registry):
        """Should raise error on unregistering nonexistent subagent."""
        with pytest.raises(KeyError, match="not found"):
            registry.unregister_subagent("nonexistent")


class TestSubagentLookup:
    """Test subagent lookup operations."""

    def test_get_subagent_existing(self, registry, sample_spec):
        """Should retrieve registered subagent."""
        registry.register_subagent(sample_spec)
        spec = registry.get_subagent("test-implementer")
        assert spec is not None
        assert spec.name == "test-implementer"

    def test_get_subagent_nonexistent(self, registry):
        """Should return None for nonexistent subagent."""
        spec = registry.get_subagent("nonexistent")
        assert spec is None

    def test_list_subagents_empty(self, registry):
        """Should return empty list when no subagents."""
        assert registry.list_subagents() == []

    def test_list_subagents_multiple(self, registry):
        """Should list all registered subagents."""
        specs = [
            SubagentSpec(
                name=f"agent-{i}",
                description=f"Agent {i}",
                capabilities=[SubagentCapability.TESTING],
                tier=1,
                invocation_template="Test"
            )
            for i in range(3)
        ]
        for spec in specs:
            registry.register_subagent(spec)

        all_specs = registry.list_subagents()
        assert len(all_specs) == 3
        assert all(spec in all_specs for spec in specs)


class TestSubagentFiltering:
    """Test subagent filtering by capability and tier."""

    @pytest.fixture
    def populated_registry(self, registry):
        """Registry with multiple subagents."""
        specs = [
            SubagentSpec(
                name="code-implementer",
                description="Implements code",
                capabilities=[SubagentCapability.IMPLEMENTATION],
                tier=1,
                invocation_template="Implement [feature]"
            ),
            SubagentSpec(
                name="test-implementer",
                description="Creates tests",
                capabilities=[SubagentCapability.TESTING],
                tier=1,
                invocation_template="Create tests"
            ),
            SubagentSpec(
                name="implementation-orch",
                description="Orchestrates implementation",
                capabilities=[SubagentCapability.IMPLEMENTATION],
                tier=0,
                invocation_template="Orchestrate implementation"
            ),
        ]
        for spec in specs:
            registry.register_subagent(spec)
        return registry

    def test_get_by_capability(self, populated_registry):
        """Should filter by capability."""
        implementers = populated_registry.get_subagents_by_capability(
            SubagentCapability.IMPLEMENTATION
        )
        assert len(implementers) == 2
        assert all(
            SubagentCapability.IMPLEMENTATION in spec.capabilities
            for spec in implementers
        )

    def test_get_by_capability_no_matches(self, populated_registry):
        """Should return empty list for unmatched capability."""
        docs = populated_registry.get_subagents_by_capability(
            SubagentCapability.DOCUMENTATION
        )
        assert len(docs) == 0

    def test_get_by_tier(self, populated_registry):
        """Should filter by tier."""
        specialists = populated_registry.get_subagents_by_tier(1)
        assert len(specialists) == 2
        assert all(spec.tier == 1 for spec in specialists)

    def test_get_by_tier_orchestrators(self, populated_registry):
        """Should get tier 0 orchestrators."""
        orchestrators = populated_registry.get_subagents_by_tier(0)
        assert len(orchestrators) == 1
        assert orchestrators[0].name == "implementation-orch"


class TestInvocationGuide:
    """Test invocation guide generation."""

    def test_guide_empty_registry(self, registry):
        """Should handle empty registry."""
        guide = registry.get_invocation_guide()
        assert "No subagents registered" in guide

    def test_guide_generation(self, registry, sample_spec):
        """Should generate invocation guide."""
        registry.register_subagent(sample_spec)
        guide = registry.get_invocation_guide()

        # Check structure
        assert "# AIPM Subagents" in guide
        assert "test-implementer" in guide
        assert "Creates comprehensive unit tests" in guide
        assert "Create tests for [component]" in guide

    def test_guide_multiple_capabilities(self, registry):
        """Should group by capability."""
        specs = [
            SubagentSpec(
                name="code-impl",
                description="Implements code",
                capabilities=[SubagentCapability.IMPLEMENTATION],
                tier=1,
                invocation_template="Implement"
            ),
            SubagentSpec(
                name="test-impl",
                description="Creates tests",
                capabilities=[SubagentCapability.TESTING],
                tier=1,
                invocation_template="Test"
            ),
        ]
        for spec in specs:
            registry.register_subagent(spec)

        guide = registry.get_invocation_guide()
        assert "IMPLEMENTATION" in guide
        assert "TESTING" in guide

    def test_guide_includes_examples(self, registry, sample_spec):
        """Should include usage examples."""
        registry.register_subagent(sample_spec)
        guide = registry.get_invocation_guide()

        assert "Usage Examples" in guide
        assert "Natural Language Invocation" in guide
        assert "Programmatic Invocation" in guide


class TestRegistryClear:
    """Test registry clearing."""

    def test_clear_registry(self, registry, sample_spec):
        """Should clear all subagents."""
        registry.register_subagent(sample_spec)
        assert len(registry.list_subagents()) == 1

        registry.clear()
        assert len(registry.list_subagents()) == 0

    def test_clear_empty_registry(self, registry):
        """Should handle clearing empty registry."""
        registry.clear()
        assert len(registry.list_subagents()) == 0


class TestSubagentSpec:
    """Test SubagentSpec model."""

    def test_spec_creation(self):
        """Should create spec with valid data."""
        spec = SubagentSpec(
            name="test-agent",
            description="Test agent",
            capabilities=[SubagentCapability.TESTING],
            tier=1,
            invocation_template="Test [component]"
        )
        assert spec.name == "test-agent"
        assert spec.tier == 1

    def test_spec_default_capabilities(self):
        """Should handle empty capabilities."""
        spec = SubagentSpec(
            name="test-agent",
            description="Test agent",
            tier=1,
            invocation_template="Test"
        )
        assert spec.capabilities == []

    def test_spec_default_metadata(self):
        """Should handle empty metadata."""
        spec = SubagentSpec(
            name="test-agent",
            description="Test agent",
            tier=1,
            invocation_template="Test"
        )
        assert spec.metadata == {}

    def test_spec_tier_validation(self):
        """Should validate tier range."""
        with pytest.raises(ValueError):
            SubagentSpec(
                name="test-agent",
                description="Test agent",
                tier=5,  # Invalid tier
                invocation_template="Test"
            )
