"""
Tests for Claude Plugin Registry

Validates plugin registration, discovery, and capability-based routing.
"""

import pytest

from agentpm.services.claude_integration.plugins import (
    ClaudePluginRegistry,
    ClaudePlugin,
    PluginCapability,
    BaseClaudePlugin,
    reset_registry,
)


class MockHooksPlugin(BaseClaudePlugin):
    """Mock plugin for testing hook capabilities."""

    def __init__(self):
        super().__init__(name="test-hooks")
        self.register_capability(PluginCapability.HOOKS)
        self.call_count = 0

    def handle(self, input_data):
        self.call_count += 1
        return {"status": "success", "data": input_data}


class MockMemoryPlugin(BaseClaudePlugin):
    """Mock plugin for testing memory capabilities."""

    def __init__(self):
        super().__init__(name="test-memory")
        self.register_capability(PluginCapability.MEMORY)
        self.register_capability(PluginCapability.CHECKPOINTING)

    def handle(self, input_data):
        return {"status": "success", "scope": input_data.get("scope")}


class MockCommandsPlugin(BaseClaudePlugin):
    """Mock plugin for testing command capabilities."""

    def __init__(self):
        super().__init__(name="test-commands")
        self.register_capability(PluginCapability.COMMANDS)

    def handle(self, input_data):
        return {"status": "success", "command": input_data.get("command")}


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reset_registry()
    reg = ClaudePluginRegistry()
    yield reg
    reg.clear()


@pytest.fixture
def hooks_plugin():
    """Create mock hooks plugin."""
    return MockHooksPlugin()


@pytest.fixture
def memory_plugin():
    """Create mock memory plugin."""
    return MockMemoryPlugin()


@pytest.fixture
def commands_plugin():
    """Create mock commands plugin."""
    return MockCommandsPlugin()


class TestPluginRegistration:
    """Test plugin registration and unregistration."""

    def test_register_plugin(self, registry, hooks_plugin):
        """Should register plugin successfully."""
        registry.register_plugin(hooks_plugin)

        assert registry.has_plugin("test-hooks")
        assert registry.get_plugin_count() == 1

    def test_register_multiple_plugins(self, registry, hooks_plugin, memory_plugin):
        """Should register multiple plugins."""
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(memory_plugin)

        assert registry.get_plugin_count() == 2
        assert registry.has_plugin("test-hooks")
        assert registry.has_plugin("test-memory")

    def test_register_duplicate_plugin(self, registry, hooks_plugin):
        """Should reject duplicate plugin registration."""
        registry.register_plugin(hooks_plugin)

        with pytest.raises(ValueError, match="already registered"):
            registry.register_plugin(hooks_plugin)

    def test_unregister_plugin(self, registry, hooks_plugin):
        """Should unregister plugin successfully."""
        registry.register_plugin(hooks_plugin)
        assert registry.has_plugin("test-hooks")

        registry.unregister_plugin("test-hooks")
        assert not registry.has_plugin("test-hooks")
        assert registry.get_plugin_count() == 0

    def test_unregister_nonexistent_plugin(self, registry):
        """Should raise error for nonexistent plugin."""
        with pytest.raises(KeyError, match="not registered"):
            registry.unregister_plugin("nonexistent")


class TestPluginDiscovery:
    """Test plugin discovery by name and capability."""

    def test_get_plugin_by_name(self, registry, hooks_plugin):
        """Should retrieve plugin by name."""
        registry.register_plugin(hooks_plugin)

        plugin = registry.get_plugin("test-hooks")
        assert plugin is not None
        assert plugin.name == "test-hooks"

    def test_get_nonexistent_plugin(self, registry):
        """Should return None for nonexistent plugin."""
        plugin = registry.get_plugin("nonexistent")
        assert plugin is None

    def test_get_plugins_by_capability_hooks(self, registry, hooks_plugin, memory_plugin):
        """Should find plugins by hooks capability."""
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(memory_plugin)

        plugins = registry.get_plugins_by_capability(PluginCapability.HOOKS)
        assert len(plugins) == 1
        assert plugins[0].name == "test-hooks"

    def test_get_plugins_by_capability_memory(self, registry, hooks_plugin, memory_plugin):
        """Should find plugins by memory capability."""
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(memory_plugin)

        plugins = registry.get_plugins_by_capability(PluginCapability.MEMORY)
        assert len(plugins) == 1
        assert plugins[0].name == "test-memory"

    def test_get_plugins_by_capability_multiple(self, registry, memory_plugin):
        """Should find plugin with multiple capabilities."""
        registry.register_plugin(memory_plugin)

        # Memory plugin supports both MEMORY and CHECKPOINTING
        memory_plugins = registry.get_plugins_by_capability(PluginCapability.MEMORY)
        checkpoint_plugins = registry.get_plugins_by_capability(PluginCapability.CHECKPOINTING)

        assert len(memory_plugins) == 1
        assert len(checkpoint_plugins) == 1
        assert memory_plugins[0] is checkpoint_plugins[0]

    def test_get_plugins_empty_capability(self, registry, hooks_plugin):
        """Should return empty list for unsupported capability."""
        registry.register_plugin(hooks_plugin)

        plugins = registry.get_plugins_by_capability(PluginCapability.SUBAGENTS)
        assert len(plugins) == 0


class TestPluginListing:
    """Test plugin listing and metadata."""

    def test_list_empty_registry(self, registry):
        """Should return empty list for no plugins."""
        plugins = registry.list_plugins()
        assert plugins == []

    def test_list_single_plugin(self, registry, hooks_plugin):
        """Should list single plugin with capabilities."""
        registry.register_plugin(hooks_plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test-hooks"
        assert "hooks" in plugins[0]["capabilities"]

    def test_list_multiple_plugins(self, registry, hooks_plugin, memory_plugin, commands_plugin):
        """Should list all plugins with capabilities."""
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(memory_plugin)
        registry.register_plugin(commands_plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 3

        # Find memory plugin
        memory_info = next(p for p in plugins if p["name"] == "test-memory")
        assert "memory" in memory_info["capabilities"]
        assert "checkpointing" in memory_info["capabilities"]

    def test_plugin_count(self, registry, hooks_plugin, memory_plugin):
        """Should track plugin count correctly."""
        assert registry.get_plugin_count() == 0

        registry.register_plugin(hooks_plugin)
        assert registry.get_plugin_count() == 1

        registry.register_plugin(memory_plugin)
        assert registry.get_plugin_count() == 2

        registry.unregister_plugin("test-hooks")
        assert registry.get_plugin_count() == 1


class TestPluginProtocol:
    """Test ClaudePlugin protocol compliance."""

    def test_base_plugin_supports(self):
        """Should check capability support correctly."""
        plugin = MockHooksPlugin()

        assert plugin.supports(PluginCapability.HOOKS)
        assert not plugin.supports(PluginCapability.MEMORY)
        assert not plugin.supports(PluginCapability.COMMANDS)

    def test_base_plugin_supports_string(self):
        """Should support capability check by string."""
        plugin = MockHooksPlugin()

        assert plugin.supports("hooks")
        assert not plugin.supports("memory")
        assert not plugin.supports("invalid")

    def test_base_plugin_handle(self):
        """Should handle input data correctly."""
        plugin = MockHooksPlugin()

        result = plugin.handle({"type": "test", "data": "value"})
        assert result["status"] == "success"
        assert result["data"]["type"] == "test"
        assert plugin.call_count == 1

    def test_base_plugin_multiple_capabilities(self):
        """Should support multiple capabilities."""
        plugin = MockMemoryPlugin()

        assert plugin.supports(PluginCapability.MEMORY)
        assert plugin.supports(PluginCapability.CHECKPOINTING)
        assert not plugin.supports(PluginCapability.HOOKS)


class TestRegistryClear:
    """Test registry clearing functionality."""

    def test_clear_registry(self, registry, hooks_plugin, memory_plugin):
        """Should clear all plugins."""
        registry.register_plugin(hooks_plugin)
        registry.register_plugin(memory_plugin)
        assert registry.get_plugin_count() == 2

        registry.clear()
        assert registry.get_plugin_count() == 0
        assert registry.list_plugins() == []

    def test_clear_empty_registry(self, registry):
        """Should handle clearing empty registry."""
        registry.clear()
        assert registry.get_plugin_count() == 0
