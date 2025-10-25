"""
Comprehensive tests for Claude Code integration.

Tests all Claude Code components including plugins, hooks, subagents,
settings, slash commands, checkpointing, and memory tools.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import tempfile
import shutil

from agentpm.providers.anthropic.claude_code import (
    ClaudeCodeOrchestrator,
    ClaudeCodePluginManager,
    ClaudeCodeHooksManager,
    ClaudeCodeSubagentsManager,
    ClaudeCodeSettingsManager,
    ClaudeCodeSlashCommandsManager,
    ClaudeCodeCheckpointingManager,
    ClaudeCodeMemoryToolManager,
)
from agentpm.providers.anthropic.claude_code.models import (
    ClaudeCodeIntegration,
    PluginDefinition,
    HookDefinition,
    SubagentDefinition,
    SettingsDefinition,
    SlashCommandDefinition,
    CheckpointDefinition,
    MemoryToolDefinition,
    ClaudeCodeComponentType,
    HookEventType,
    SubagentCapability,
    SettingType,
    CheckpointType,
    MemoryToolType,
)


class TestClaudeCodeOrchestrator:
    """Test Claude Code orchestrator functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def orchestrator(self, mock_db_service):
        """Create orchestrator instance."""
        return ClaudeCodeOrchestrator(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_orchestrator_initialization(self, mock_db_service):
        """Test orchestrator initialization."""
        orchestrator = ClaudeCodeOrchestrator(mock_db_service)
        
        assert orchestrator.db == mock_db_service
        assert orchestrator.plugin_manager is not None
        assert orchestrator.hook_manager is not None
        assert orchestrator.subagent_manager is not None
        assert orchestrator.settings_manager is not None
        assert orchestrator.slash_command_manager is not None
        assert orchestrator.checkpointing_manager is not None
        assert orchestrator.memory_tool_manager is not None
        assert orchestrator._integration_cache == {}
        assert orchestrator._component_cache == {}
    
    def test_create_comprehensive_integration(self, orchestrator, temp_dir):
        """Test comprehensive integration creation."""
        with patch.object(orchestrator.plugin_manager, 'create_aipm_plugins') as mock_plugins, \
             patch.object(orchestrator.hook_manager, 'create_aipm_hooks') as mock_hooks, \
             patch.object(orchestrator.subagent_manager, 'create_aipm_subagents') as mock_subagents, \
             patch.object(orchestrator.settings_manager, 'create_aipm_settings') as mock_settings, \
             patch.object(orchestrator.slash_command_manager, 'create_aipm_slash_commands') as mock_slash, \
             patch.object(orchestrator.checkpointing_manager, 'create_aipm_checkpoints') as mock_checkpoints, \
             patch.object(orchestrator.memory_tool_manager, 'create_aipm_memory_configs') as mock_memory:
            
            # Mock return values
            mock_plugins.return_value = [PluginDefinition(name="test-plugin", description="Test plugin")]
            mock_hooks.return_value = [HookDefinition(name="test-hook", description="Test hook", event=HookEventType.PRE_TOOL_USE)]
            mock_subagents.return_value = [SubagentDefinition(name="test-subagent", description="Test subagent", role="test-role")]
            mock_settings.return_value = [SettingsDefinition(name="test-settings", description="Test settings")]
            mock_slash.return_value = [SlashCommandDefinition(name="test-command", description="Test command", command="/test")]
            mock_checkpoints.return_value = [CheckpointDefinition(name="test-checkpoint", description="Test checkpoint", checkpoint_type=CheckpointType.MANUAL)]
            mock_memory.return_value = [MemoryToolDefinition(name="test-memory", description="Test memory", memory_type=MemoryToolType.PERSISTENT)]
            
            # Create integration
            integration = orchestrator.create_comprehensive_integration(
                output_dir=temp_dir,
                project_id=1,
                integration_name="Test Integration"
            )
            
            # Verify integration
            assert integration.name == "Test Integration"
            assert integration.description == "Comprehensive APM (Agent Project Manager) integration with Claude Code"
            assert integration.version == "1.0.0"
            assert len(integration.plugins) == 1
            assert len(integration.hooks) == 1
            assert len(integration.subagents) == 1
            assert len(integration.settings) == 1
            assert len(integration.slash_commands) == 1
            assert len(integration.checkpoints) == 1
            assert len(integration.memory_tools) == 1
            assert integration.created_at is not None
            assert integration.updated_at is not None
            
            # Verify directories created
            claude_dir = temp_dir / ".claude"
            assert claude_dir.exists()
            assert (claude_dir / "plugins").exists()
            assert (claude_dir / "hooks").exists()
            assert (claude_dir / "subagents").exists()
            assert (claude_dir / "settings").exists()
            assert (claude_dir / "slash-commands").exists()
            assert (claude_dir / "checkpoints").exists()
            assert (claude_dir / "memory").exists()
            assert (claude_dir / "skills").exists()
            
            # Verify integration manifest
            manifest_file = claude_dir / "integration.json"
            assert manifest_file.exists()
            manifest_data = json.loads(manifest_file.read_text())
            assert manifest_data["name"] == "Test Integration"
            assert manifest_data["version"] == "1.0.0"
    
    def test_generate_project_integration(self, orchestrator, temp_dir):
        """Test project-specific integration generation."""
        with patch.object(orchestrator, 'create_comprehensive_integration') as mock_create:
            mock_integration = Mock()
            mock_create.return_value = mock_integration
            
            result = orchestrator.generate_project_integration(project_id=123, output_dir=temp_dir)
            
            mock_create.assert_called_once_with(
                output_dir=temp_dir,
                project_id=123,
                integration_name="APM (Agent Project Manager) Project 123 Integration"
            )
            assert result == mock_integration
    
    def test_generate_agent_integration(self, orchestrator, temp_dir):
        """Test agent-specific integration generation."""
        with patch.object(orchestrator, 'create_comprehensive_integration') as mock_create:
            mock_integration = Mock()
            mock_create.return_value = mock_integration
            
            result = orchestrator.generate_agent_integration(agent_role="test-agent", output_dir=temp_dir)
            
            mock_create.assert_called_once_with(
                output_dir=temp_dir,
                project_id=None,
                integration_name="APM (Agent Project Manager) test-agent Agent Integration"
            )
            assert result == mock_integration
    
    def test_validate_integration(self, orchestrator):
        """Test integration validation."""
        # Create valid integration
        integration = ClaudeCodeIntegration(
            name="Test Integration",
            description="Test description",
            plugins=[PluginDefinition(name="test-plugin", description="Test plugin")],
            hooks=[HookDefinition(name="test-hook", description="Test hook", event=HookEventType.PRE_TOOL_USE)],
            subagents=[SubagentDefinition(name="test-subagent", description="Test subagent", role="test-role")],
            settings=[SettingsDefinition(name="test-settings", description="Test settings")],
            slash_commands=[SlashCommandDefinition(name="test-command", description="Test command", command="/test")],
            checkpoints=[CheckpointDefinition(name="test-checkpoint", description="Test checkpoint", checkpoint_type=CheckpointType.MANUAL)],
            memory_tools=[MemoryToolDefinition(name="test-memory", description="Test memory", memory_type=MemoryToolType.PERSISTENT)]
        )
        
        # Validate integration
        results = orchestrator.validate_integration(integration)
        
        assert results["valid"] is True
        assert len(results["errors"]) == 0
        assert results["component_counts"]["plugins"] == 1
        assert results["component_counts"]["hooks"] == 1
        assert results["component_counts"]["subagents"] == 1
        assert results["component_counts"]["settings"] == 1
        assert results["component_counts"]["slash_commands"] == 1
        assert results["component_counts"]["checkpoints"] == 1
        assert results["component_counts"]["memory_tools"] == 1
    
    def test_validate_integration_with_errors(self, orchestrator):
        """Test integration validation with errors."""
        # Create invalid integration (missing name)
        integration = ClaudeCodeIntegration(
            name="",  # Invalid: empty name
            description="Test description",
            plugins=[PluginDefinition(name="", description="Test plugin")],  # Invalid: empty name
            hooks=[],
            subagents=[],
            settings=[],
            slash_commands=[],
            checkpoints=[],
            memory_tools=[]
        )
        
        # Validate integration
        results = orchestrator.validate_integration(integration)
        
        assert results["valid"] is False
        assert len(results["errors"]) > 0
        assert "Integration name is required" in results["errors"]
        assert "Plugin name is required" in results["errors"]
    
    def test_export_import_integration(self, orchestrator, temp_dir):
        """Test integration export and import."""
        # Create test integration
        integration = ClaudeCodeIntegration(
            name="Test Integration",
            description="Test description",
            plugins=[],
            hooks=[],
            subagents=[],
            settings=[],
            slash_commands=[],
            checkpoints=[],
            memory_tools=[]
        )
        
        # Export integration
        export_path = temp_dir / "test_integration.json"
        success = orchestrator.export_integration(integration, export_path, "json")
        
        assert success is True
        assert export_path.exists()
        
        # Import integration
        imported_integration = orchestrator.import_integration(export_path)
        
        assert imported_integration is not None
        assert imported_integration.name == "Test Integration"
        assert imported_integration.description == "Test description"
        
        # Verify integration is cached
        cached_integration = orchestrator.get_integration("Test Integration")
        assert cached_integration is not None
        assert cached_integration.name == "Test Integration"
    
    def test_list_integrations(self, orchestrator):
        """Test listing integrations."""
        # Initially empty
        integrations = orchestrator.list_integrations()
        assert len(integrations) == 0
        
        # Add integration to cache
        integration = ClaudeCodeIntegration(
            name="Test Integration",
            description="Test description",
            plugins=[],
            hooks=[],
            subagents=[],
            settings=[],
            slash_commands=[],
            checkpoints=[],
            memory_tools=[]
        )
        orchestrator._integration_cache["Test Integration"] = integration
        
        # List integrations
        integrations = orchestrator.list_integrations()
        assert len(integrations) == 1
        assert "Test Integration" in integrations
    
    def test_get_integration_stats(self, orchestrator):
        """Test getting integration statistics."""
        # Add test integrations
        integration1 = ClaudeCodeIntegration(
            name="Integration 1",
            description="Test integration 1",
            plugins=[PluginDefinition(name="plugin1", description="Plugin 1")],
            hooks=[HookDefinition(name="hook1", description="Hook 1", event=HookEventType.PRE_TOOL_USE)],
            subagents=[],
            settings=[],
            slash_commands=[],
            checkpoints=[],
            memory_tools=[]
        )
        
        integration2 = ClaudeCodeIntegration(
            name="Integration 2",
            description="Test integration 2",
            plugins=[],
            hooks=[],
            subagents=[SubagentDefinition(name="subagent1", description="Subagent 1", role="test-role")],
            settings=[],
            slash_commands=[],
            checkpoints=[],
            memory_tools=[]
        )
        
        orchestrator._integration_cache["Integration 1"] = integration1
        orchestrator._integration_cache["Integration 2"] = integration2
        
        # Get stats
        stats = orchestrator.get_integration_stats()
        
        assert stats["total_integrations"] == 2
        assert stats["total_components"] == 3  # 1 plugin + 1 hook + 1 subagent
        assert "Integration 1" in stats["component_breakdown"]
        assert "Integration 2" in stats["component_breakdown"]
        assert stats["component_breakdown"]["Integration 1"]["plugins"] == 1
        assert stats["component_breakdown"]["Integration 1"]["hooks"] == 1
        assert stats["component_breakdown"]["Integration 2"]["subagents"] == 1
    
    def test_cleanup_integration_cache(self, orchestrator):
        """Test integration cache cleanup."""
        # Add test data
        orchestrator._integration_cache["test1"] = Mock()
        orchestrator._integration_cache["test2"] = Mock()
        orchestrator._component_cache["test"] = [Mock()]
        
        # Cleanup cache
        cleaned_count = orchestrator.cleanup_integration_cache()
        
        assert cleaned_count == 2
        assert len(orchestrator._integration_cache) == 0
        assert len(orchestrator._component_cache) == 0


class TestClaudeCodePluginManager:
    """Test Claude Code plugin manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def plugin_manager(self, mock_db_service):
        """Create plugin manager instance."""
        return ClaudeCodePluginManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_plugin_manager_initialization(self, mock_db_service):
        """Test plugin manager initialization."""
        manager = ClaudeCodePluginManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._plugins_cache == {}
        assert manager._marketplace_cache == {}
    
    def test_create_aipm_plugins(self, plugin_manager, temp_dir):
        """Test AIPM plugin creation."""
        with patch.object(plugin_manager, '_create_core_plugins') as mock_core, \
             patch.object(plugin_manager, '_create_workflow_plugins') as mock_workflow, \
             patch.object(plugin_manager, '_create_agent_plugins') as mock_agent:
            
            # Mock return values
            mock_core.return_value = [PluginDefinition(name="core-plugin", description="Core plugin")]
            mock_workflow.return_value = [PluginDefinition(name="workflow-plugin", description="Workflow plugin")]
            mock_agent.return_value = [PluginDefinition(name="agent-plugin", description="Agent plugin")]
            
            # Create plugins
            plugins = plugin_manager.create_aipm_plugins(temp_dir, project_id=1)
            
            # Verify plugins
            assert len(plugins) == 3
            assert any(p.name == "core-plugin" for p in plugins)
            assert any(p.name == "workflow-plugin" for p in plugins)
            assert any(p.name == "agent-plugin" for p in plugins)
            
            # Verify method calls
            mock_core.assert_called_once_with(temp_dir, 1)
            mock_workflow.assert_called_once_with(temp_dir, 1)
            mock_agent.assert_called_once_with(temp_dir, 1)


class TestClaudeCodeHookManager:
    """Test Claude Code hook manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def hook_manager(self, mock_db_service):
        """Create hook manager instance."""
        return ClaudeCodeHookManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_hook_manager_initialization(self, mock_db_service):
        """Test hook manager initialization."""
        manager = ClaudeCodeHookManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._hooks_cache == {}
        assert manager._active_hooks == {}
    
    def test_create_aipm_hooks(self, hook_manager, temp_dir):
        """Test AIPM hook creation."""
        with patch.object(hook_manager, '_create_workflow_hooks') as mock_workflow, \
             patch.object(hook_manager, '_create_quality_hooks') as mock_quality, \
             patch.object(hook_manager, '_create_context_hooks') as mock_context:
            
            # Mock return values
            mock_workflow.return_value = [HookDefinition(name="workflow-hook", description="Workflow hook", event=HookEventType.PRE_TOOL_USE)]
            mock_quality.return_value = [HookDefinition(name="quality-hook", description="Quality hook", event=HookEventType.POST_TOOL_USE)]
            mock_context.return_value = [HookDefinition(name="context-hook", description="Context hook", event=HookEventType.SESSION_START)]
            
            # Create hooks
            hooks = hook_manager.create_aipm_hooks(temp_dir, project_id=1)
            
            # Verify hooks
            assert len(hooks) == 3
            assert any(h.name == "workflow-hook" for h in hooks)
            assert any(h.name == "quality-hook" for h in hooks)
            assert any(h.name == "context-hook" for h in hooks)
            
            # Verify method calls
            mock_workflow.assert_called_once_with(temp_dir, 1)
            mock_quality.assert_called_once_with(temp_dir, 1)
            mock_context.assert_called_once_with(temp_dir, 1)


class TestClaudeCodeSubagentManager:
    """Test Claude Code subagent manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def subagent_manager(self, mock_db_service):
        """Create subagent manager instance."""
        return ClaudeCodeSubagentManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_subagent_manager_initialization(self, mock_db_service):
        """Test subagent manager initialization."""
        manager = ClaudeCodeSubagentManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._subagents_cache == {}
        assert manager._active_subagents == {}
    
    def test_create_aipm_subagents(self, subagent_manager, temp_dir):
        """Test AIPM subagent creation."""
        with patch.object(subagent_manager, '_create_workflow_subagents') as mock_workflow, \
             patch.object(subagent_manager, '_create_specialized_subagents') as mock_specialized, \
             patch.object(subagent_manager, '_create_quality_subagents') as mock_quality:
            
            # Mock return values
            mock_workflow.return_value = [SubagentDefinition(name="workflow-subagent", description="Workflow subagent", role="workflow-agent")]
            mock_specialized.return_value = [SubagentDefinition(name="specialized-subagent", description="Specialized subagent", role="specialized-agent")]
            mock_quality.return_value = [SubagentDefinition(name="quality-subagent", description="Quality subagent", role="quality-agent")]
            
            # Create subagents
            subagents = subagent_manager.create_aipm_subagents(temp_dir, project_id=1)
            
            # Verify subagents
            assert len(subagents) == 3
            assert any(s.name == "workflow-subagent" for s in subagents)
            assert any(s.name == "specialized-subagent" for s in subagents)
            assert any(s.name == "quality-subagent" for s in subagents)
            
            # Verify method calls
            mock_workflow.assert_called_once_with(temp_dir, 1)
            mock_specialized.assert_called_once_with(temp_dir, 1)
            mock_quality.assert_called_once_with(temp_dir, 1)


class TestClaudeCodeSettingsManager:
    """Test Claude Code settings manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def settings_manager(self, mock_db_service):
        """Create settings manager instance."""
        return ClaudeCodeSettingsManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_settings_manager_initialization(self, mock_db_service):
        """Test settings manager initialization."""
        manager = ClaudeCodeSettingsManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._settings_cache == {}
        assert manager._active_settings == {}
    
    def test_create_aipm_settings(self, settings_manager, temp_dir):
        """Test AIPM settings creation."""
        with patch.object(settings_manager, '_create_workflow_settings') as mock_workflow, \
             patch.object(settings_manager, '_create_quality_settings') as mock_quality, \
             patch.object(settings_manager, '_create_context_settings') as mock_context:
            
            # Mock return values
            mock_workflow.return_value = [SettingsDefinition(name="workflow-settings", description="Workflow settings")]
            mock_quality.return_value = [SettingsDefinition(name="quality-settings", description="Quality settings")]
            mock_context.return_value = [SettingsDefinition(name="context-settings", description="Context settings")]
            
            # Create settings
            settings = settings_manager.create_aipm_settings(temp_dir, project_id=1)
            
            # Verify settings
            assert len(settings) == 3
            assert any(s.name == "workflow-settings" for s in settings)
            assert any(s.name == "quality-settings" for s in settings)
            assert any(s.name == "context-settings" for s in settings)
            
            # Verify method calls
            mock_workflow.assert_called_once_with(temp_dir, 1)
            mock_quality.assert_called_once_with(temp_dir, 1)
            mock_context.assert_called_once_with(temp_dir, 1)


class TestClaudeCodeSlashCommandManager:
    """Test Claude Code slash command manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def slash_command_manager(self, mock_db_service):
        """Create slash command manager instance."""
        return ClaudeCodeSlashCommandManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_slash_command_manager_initialization(self, mock_db_service):
        """Test slash command manager initialization."""
        manager = ClaudeCodeSlashCommandManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._commands_cache == {}
        assert manager._active_commands == {}
    
    def test_create_aipm_slash_commands(self, slash_command_manager, temp_dir):
        """Test AIPM slash command creation."""
        with patch.object(slash_command_manager, '_create_workflow_commands') as mock_workflow, \
             patch.object(slash_command_manager, '_create_quality_commands') as mock_quality, \
             patch.object(slash_command_manager, '_create_context_commands') as mock_context:
            
            # Mock return values
            mock_workflow.return_value = [SlashCommandDefinition(name="workflow-command", description="Workflow command", command="/workflow")]
            mock_quality.return_value = [SlashCommandDefinition(name="quality-command", description="Quality command", command="/quality")]
            mock_context.return_value = [SlashCommandDefinition(name="context-command", description="Context command", command="/context")]
            
            # Create slash commands
            commands = slash_command_manager.create_aipm_slash_commands(temp_dir, project_id=1)
            
            # Verify commands
            assert len(commands) == 3
            assert any(c.name == "workflow-command" for c in commands)
            assert any(c.name == "quality-command" for c in commands)
            assert any(c.name == "context-command" for c in commands)
            
            # Verify method calls
            mock_workflow.assert_called_once_with(temp_dir, 1)
            mock_quality.assert_called_once_with(temp_dir, 1)
            mock_context.assert_called_once_with(temp_dir, 1)


class TestClaudeCodeCheckpointingManager:
    """Test Claude Code checkpointing manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def checkpointing_manager(self, mock_db_service):
        """Create checkpointing manager instance."""
        return ClaudeCodeCheckpointingManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_checkpointing_manager_initialization(self, mock_db_service):
        """Test checkpointing manager initialization."""
        manager = ClaudeCodeCheckpointingManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._checkpoints_cache == {}
        assert manager._active_checkpoints == {}
        assert manager._checkpoint_storage == Path(".claude/checkpoints")
    
    def test_create_aipm_checkpoints(self, checkpointing_manager, temp_dir):
        """Test AIPM checkpoint creation."""
        with patch.object(checkpointing_manager, '_create_session_checkpoints') as mock_session, \
             patch.object(checkpointing_manager, '_create_workflow_checkpoints') as mock_workflow, \
             patch.object(checkpointing_manager, '_create_milestone_checkpoints') as mock_milestone, \
             patch.object(checkpointing_manager, '_create_quality_checkpoints') as mock_quality, \
             patch.object(checkpointing_manager, '_create_project_checkpoints') as mock_project:
            
            # Mock return values
            mock_session.return_value = [CheckpointDefinition(name="session-checkpoint", description="Session checkpoint", checkpoint_type=CheckpointType.SESSION)]
            mock_workflow.return_value = [CheckpointDefinition(name="workflow-checkpoint", description="Workflow checkpoint", checkpoint_type=CheckpointType.MANUAL)]
            mock_milestone.return_value = [CheckpointDefinition(name="milestone-checkpoint", description="Milestone checkpoint", checkpoint_type=CheckpointType.MILESTONE)]
            mock_quality.return_value = [CheckpointDefinition(name="quality-checkpoint", description="Quality checkpoint", checkpoint_type=CheckpointType.AUTO)]
            mock_project.return_value = [CheckpointDefinition(name="project-checkpoint", description="Project checkpoint", checkpoint_type=CheckpointType.MANUAL)]
            
            # Create checkpoints
            checkpoints = checkpointing_manager.create_aipm_checkpoints(temp_dir, project_id=1)
            
            # Verify checkpoints
            assert len(checkpoints) == 5
            assert any(c.name == "session-checkpoint" for c in checkpoints)
            assert any(c.name == "workflow-checkpoint" for c in checkpoints)
            assert any(c.name == "milestone-checkpoint" for c in checkpoints)
            assert any(c.name == "quality-checkpoint" for c in checkpoints)
            assert any(c.name == "project-checkpoint" for c in checkpoints)
            
            # Verify method calls
            mock_session.assert_called_once_with(temp_dir / "checkpoints")
            mock_workflow.assert_called_once_with(temp_dir / "checkpoints")
            mock_milestone.assert_called_once_with(temp_dir / "checkpoints")
            mock_quality.assert_called_once_with(temp_dir / "checkpoints")
            mock_project.assert_called_once_with(temp_dir / "checkpoints", 1)


class TestClaudeCodeMemoryToolManager:
    """Test Claude Code memory tool manager functionality."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service."""
        return Mock()
    
    @pytest.fixture
    def memory_tool_manager(self, mock_db_service):
        """Create memory tool manager instance."""
        return ClaudeCodeMemoryToolManager(mock_db_service)
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_memory_tool_manager_initialization(self, mock_db_service):
        """Test memory tool manager initialization."""
        manager = ClaudeCodeMemoryToolManager(mock_db_service)
        
        assert manager.db == mock_db_service
        assert manager._memory_cache == {}
        assert manager._memory_storage == Path(".claude/memory")
        assert manager._memory_index == {}
    
    def test_create_aipm_memory_configs(self, memory_tool_manager, temp_dir):
        """Test AIPM memory configuration creation."""
        with patch.object(memory_tool_manager, 'create_decision_memory_configs') as mock_decision, \
             patch.object(memory_tool_manager, 'create_learning_memory_configs') as mock_learning, \
             patch.object(memory_tool_manager, 'create_pattern_memory_configs') as mock_pattern, \
             patch.object(memory_tool_manager, 'create_context_memory_configs') as mock_context, \
             patch.object(memory_tool_manager, 'create_workflow_memory_configs') as mock_workflow, \
             patch.object(memory_tool_manager, 'create_project_memory_configs') as mock_project:
            
            # Mock return values
            mock_decision.return_value = [MemoryToolDefinition(name="decision-memory", description="Decision memory", memory_type=MemoryToolType.PERSISTENT)]
            mock_learning.return_value = [MemoryToolDefinition(name="learning-memory", description="Learning memory", memory_type=MemoryToolType.PERSISTENT)]
            mock_pattern.return_value = [MemoryToolDefinition(name="pattern-memory", description="Pattern memory", memory_type=MemoryToolType.PERSISTENT)]
            mock_context.return_value = [MemoryToolDefinition(name="context-memory", description="Context memory", memory_type=MemoryToolType.SESSION)]
            mock_workflow.return_value = [MemoryToolDefinition(name="workflow-memory", description="Workflow memory", memory_type=MemoryToolType.PERSISTENT)]
            mock_project.return_value = [MemoryToolDefinition(name="project-memory", description="Project memory", memory_type=MemoryToolType.PERSISTENT)]
            
            # Create memory configurations
            memory_configs = memory_tool_manager.create_aipm_memory_configs(temp_dir, project_id=1)
            
            # Verify memory configurations
            assert len(memory_configs) == 6
            assert any(m.name == "decision-memory" for m in memory_configs)
            assert any(m.name == "learning-memory" for m in memory_configs)
            assert any(m.name == "pattern-memory" for m in memory_configs)
            assert any(m.name == "context-memory" for m in memory_configs)
            assert any(m.name == "workflow-memory" for m in memory_configs)
            assert any(m.name == "project-memory" for m in memory_configs)
            
            # Verify method calls
            mock_decision.assert_called_once_with(temp_dir / "memory")
            mock_learning.assert_called_once_with(temp_dir / "memory")
            mock_pattern.assert_called_once_with(temp_dir / "memory")
            mock_context.assert_called_once_with(temp_dir / "memory")
            mock_workflow.assert_called_once_with(temp_dir / "memory")
            mock_project.assert_called_once_with(temp_dir / "memory", 1)
    
    def test_store_retrieve_memory(self, memory_tool_manager):
        """Test memory storage and retrieval."""
        # Store memory
        memory_data = {"test": "data", "number": 42}
        success = memory_tool_manager.store_memory(
            memory_key="test-key",
            memory_data=memory_data,
            memory_type=MemoryToolType.PERSISTENT,
            category="test"
        )
        
        assert success is True
        
        # Retrieve memory
        retrieved_data = memory_tool_manager.retrieve_memory("test-key")
        
        assert retrieved_data is not None
        assert retrieved_data == memory_data
    
    def test_search_memory(self, memory_tool_manager):
        """Test memory search functionality."""
        # Store test memories
        memory_tool_manager.store_memory("key1", {"content": "test data", "category": "test"}, MemoryToolType.PERSISTENT, "test")
        memory_tool_manager.store_memory("key2", {"content": "other data", "category": "other"}, MemoryToolType.PERSISTENT, "other")
        
        # Search memories
        results = memory_tool_manager.search_memory("test", category="test")
        
        assert len(results) >= 1
        assert any("test" in str(result.get("data", {})) for result in results)
    
    def test_delete_memory(self, memory_tool_manager):
        """Test memory deletion."""
        # Store memory
        memory_tool_manager.store_memory("delete-key", {"test": "data"}, MemoryToolType.PERSISTENT, "test")
        
        # Verify memory exists
        retrieved_data = memory_tool_manager.retrieve_memory("delete-key")
        assert retrieved_data is not None
        
        # Delete memory
        success = memory_tool_manager.delete_memory("delete-key")
        assert success is True
        
        # Verify memory is deleted
        retrieved_data = memory_tool_manager.retrieve_memory("delete-key")
        assert retrieved_data is None
    
    def test_get_memory_stats(self, memory_tool_manager):
        """Test memory statistics."""
        # Store some test memories
        memory_tool_manager.store_memory("key1", {"test": "data1"}, MemoryToolType.PERSISTENT, "test")
        memory_tool_manager.store_memory("key2", {"test": "data2"}, MemoryToolType.SESSION, "test")
        
        # Get stats
        stats = memory_tool_manager.get_memory_stats()
        
        assert "cache_entries" in stats
        assert "persistent_entries" in stats
        assert "total_entries" in stats
        assert "memory_usage" in stats
        assert "index_size" in stats
        assert stats["cache_entries"] >= 2
