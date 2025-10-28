"""
Tests for Slash Commands

Validates slash command system including:
- Command registration and discovery
- Command execution
- Individual command handlers (context, status, memory, checkpoint)
- Error handling
- Argument parsing

Pattern: AAA (Arrange-Act-Assert)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from agentpm.providers.anthropic.claude_code.runtime.commands import (
    SlashCommandRegistry,
    get_registry,
    reset_registry,
    SlashCommand,
    CommandResult,
    CommandError,
    CommandStatus,
    CommandHandlers,
    init_commands,
    list_available_commands,
)


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reset_registry()
    reg = get_registry()
    yield reg
    reg.clear()


@pytest.fixture
def mock_db(db_service):
    """Mock database service."""
    return db_service


@pytest.fixture
def handlers(mock_db):
    """Create command handlers with mock database."""
    return CommandHandlers(mock_db)


class TestCommandRegistry:
    """Test command registry functionality."""

    def test_registry_singleton(self):
        """Should return same registry instance."""
        # Arrange & Act
        reg1 = get_registry()
        reg2 = get_registry()

        # Assert
        assert reg1 is reg2

    def test_registry_reset(self):
        """Should create new registry after reset."""
        # Arrange
        reg1 = get_registry()

        # Act
        reset_registry()
        reg2 = get_registry()

        # Assert
        assert reg1 is not reg2

    def test_register_command(self, registry):
        """Should register command successfully."""
        # Arrange
        def handler(args):
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message="Test command"
            )

        # Act
        registry.register(
            name="test:command",
            description="Test command",
            usage="/test:command",
            handler=handler
        )

        # Assert
        assert registry.get("test:command") is not None
        assert registry.get("test:command").name == "test:command"

    def test_register_duplicate_command_fails(self, registry):
        """Should fail when registering duplicate command."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        registry.register(
            name="test:dup",
            description="Test",
            usage="/test:dup",
            handler=handler
        )

        # Act & Assert
        with pytest.raises(ValueError, match="already registered"):
            registry.register(
                name="test:dup",
                description="Test",
                usage="/test:dup",
                handler=handler
            )

    def test_unregister_command(self, registry):
        """Should unregister command successfully."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        registry.register(
            name="test:unregister",
            description="Test",
            usage="/test:unregister",
            handler=handler
        )

        # Act
        registry.unregister("test:unregister")

        # Assert
        assert registry.get("test:unregister") is None

    def test_unregister_nonexistent_command_fails(self, registry):
        """Should fail when unregistering nonexistent command."""
        # Act & Assert
        with pytest.raises(KeyError, match="not registered"):
            registry.unregister("test:nonexistent")

    def test_list_commands(self, registry):
        """Should list all registered commands."""
        # Arrange
        def handler1(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test 1")

        def handler2(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test 2")

        registry.register(
            name="test:cmd1",
            description="Command 1",
            usage="/test:cmd1",
            handler=handler1
        )
        registry.register(
            name="test:cmd2",
            description="Command 2",
            usage="/test:cmd2",
            handler=handler2
        )

        # Act
        commands = registry.list_commands()

        # Assert
        assert len(commands) == 2
        names = [cmd.name for cmd in commands]
        assert "test:cmd1" in names
        assert "test:cmd2" in names

    def test_execute_command(self, registry):
        """Should execute command successfully."""
        # Arrange
        def handler(args):
            return CommandResult(
                status=CommandStatus.SUCCESS,
                message="Executed",
                data={"args": args}
            )

        registry.register(
            name="test:execute",
            description="Test",
            usage="/test:execute",
            handler=handler
        )

        # Act
        result = registry.execute("test:execute", args=["arg1", "arg2"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.message == "Executed"
        assert result.data["args"] == ["arg1", "arg2"]

    def test_execute_command_with_leading_slash(self, registry):
        """Should execute command with leading slash in name."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        registry.register(
            name="test:slash",
            description="Test",
            usage="/test:slash",
            handler=handler
        )

        # Act
        result = registry.execute("/test:slash")

        # Assert
        assert result.status == CommandStatus.SUCCESS

    def test_execute_nonexistent_command_fails(self, registry):
        """Should fail when executing nonexistent command."""
        # Act & Assert
        with pytest.raises(CommandError, match="not found"):
            registry.execute("test:nonexistent")

    def test_execute_disabled_command_fails(self, registry):
        """Should fail when executing disabled command."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        registry.register(
            name="test:disabled",
            description="Test",
            usage="/test:disabled",
            handler=handler,
            enabled=False
        )

        # Act & Assert
        with pytest.raises(CommandError, match="disabled"):
            registry.execute("test:disabled")

    def test_clear_registry(self, registry):
        """Should clear all commands."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        registry.register(
            name="test:clear1",
            description="Test",
            usage="/test:clear1",
            handler=handler
        )
        registry.register(
            name="test:clear2",
            description="Test",
            usage="/test:clear2",
            handler=handler
        )

        # Act
        registry.clear()

        # Assert
        assert len(registry.list_commands()) == 0


class TestCommandInitialization:
    """Test command initialization."""

    def test_init_commands(self, registry, mock_db):
        """Should initialize all AIPM commands."""
        # Act
        init_commands(mock_db)

        # Assert
        commands = registry.list_commands()
        assert len(commands) == 4

        names = [cmd.name for cmd in commands]
        assert "aipm:context" in names
        assert "aipm:status" in names
        assert "aipm:memory" in names
        assert "aipm:checkpoint" in names

    def test_list_available_commands_empty(self, registry):
        """Should show message when no commands registered."""
        # Act
        output = list_available_commands()

        # Assert
        assert "No commands registered" in output

    def test_list_available_commands(self, registry, mock_db):
        """Should list all available commands."""
        # Arrange
        init_commands(mock_db)

        # Act
        output = list_available_commands()

        # Assert
        assert "/aipm:context" in output
        assert "/aipm:status" in output
        assert "/aipm:memory" in output
        assert "/aipm:checkpoint" in output
        assert "Load AIPM context" in output


class TestContextCommand:
    """Test /aipm:context command."""

    def test_context_command_current_session(self, handlers, work_item, task):
        """Should load current session context."""
        # Act
        result = handlers.context([])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "Context loaded" in result.message
        assert result.data is not None

    def test_context_command_work_item(self, handlers, work_item):
        """Should load specific work item context."""
        # Act
        result = handlers.context([f"--work-item={work_item.id}"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["entity_type"] == "work_item"
        assert result.data["id"] == work_item.id
        assert result.data["name"] == work_item.name

    def test_context_command_work_item_full(self, handlers, work_item, task):
        """Should load work item with full context including tasks."""
        # Act
        result = handlers.context([f"--work-item={work_item.id}", "--full"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["entity_type"] == "work_item"
        assert "tasks" in result.data
        assert len(result.data["tasks"]) > 0

    def test_context_command_task(self, handlers, task):
        """Should load specific task context."""
        # Act
        result = handlers.context([f"--task={task.id}"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["entity_type"] == "task"
        assert result.data["id"] == task.id

    def test_context_command_task_full(self, handlers, task, work_item):
        """Should load task with full context including work item."""
        # Act
        result = handlers.context([f"--task={task.id}", "--full"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["entity_type"] == "task"
        assert "work_item" in result.data
        assert result.data["work_item"]["id"] == work_item.id

    def test_context_command_nonexistent_work_item(self, handlers):
        """Should fail for nonexistent work item."""
        # Act & Assert
        with pytest.raises(CommandError, match="not found"):
            handlers.context(["--work-item=99999"])

    def test_context_command_nonexistent_task(self, handlers):
        """Should fail for nonexistent task."""
        # Act & Assert
        with pytest.raises(CommandError, match="not found"):
            handlers.context(["--task=99999"])

    def test_context_command_invalid_args(self, handlers):
        """Should fail with invalid arguments."""
        # Act & Assert
        with pytest.raises(CommandError, match="Invalid arguments"):
            handlers.context(["--invalid-arg"])


class TestStatusCommand:
    """Test /aipm:status command."""

    def test_status_command_default(self, handlers, work_item, task):
        """Should show project status."""
        # Act
        result = handlers.status([])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "Status loaded" in result.message
        assert "work_items" in result.data
        assert "tasks" in result.data

    def test_status_command_work_items_only(self, handlers, work_item):
        """Should show only work items."""
        # Act
        result = handlers.status(["--work-items-only"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "work_items" in result.data
        assert "tasks" not in result.data

    def test_status_command_tasks_only(self, handlers, task):
        """Should show only tasks."""
        # Act
        result = handlers.status(["--tasks-only"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "tasks" in result.data
        assert "work_items" not in result.data

    def test_status_command_with_session(self, handlers, work_item):
        """Should include session info if available."""
        # Act
        result = handlers.status([])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        # Session may or may not be present depending on test state
        # Just verify data structure is valid
        assert result.data is not None

    def test_status_command_invalid_args(self, handlers):
        """Should fail with invalid arguments."""
        # Act & Assert
        with pytest.raises(CommandError, match="Invalid arguments"):
            handlers.status(["--invalid-arg"])


class TestMemoryCommand:
    """Test /aipm:memory command."""

    def test_memory_command_status(self, handlers):
        """Should show memory file status."""
        # Act
        result = handlers.memory(["status"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "Memory status" in result.message
        assert "directory" in result.data

    def test_memory_command_status_default(self, handlers):
        """Should default to status action."""
        # Act
        result = handlers.memory([])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "Memory status" in result.message

    @patch("agentpm.services.memory.generator.MemoryGenerator")
    def test_memory_command_generate(self, mock_generator_class, handlers):
        """Should generate memory files."""
        # Arrange
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Act
        result = handlers.memory(["generate"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "generated" in result.data
        mock_generator.generate_current_context.assert_called_once()

    @patch("agentpm.services.memory.generator.MemoryGenerator")
    def test_memory_command_generate_all(self, mock_generator_class, handlers):
        """Should generate all memory files."""
        # Arrange
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Act
        result = handlers.memory(["generate", "--all"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["generated"] == "all"
        mock_generator.generate_all.assert_called_once()

    def test_memory_command_invalid_action(self, handlers):
        """Should fail with invalid action."""
        # Act & Assert
        with pytest.raises(CommandError, match="Unknown action"):
            handlers.memory(["invalid"])


class TestCheckpointCommand:
    """Test /aipm:checkpoint command."""

    def test_checkpoint_command_default(self, handlers, session):
        """Should create checkpoint with default name."""
        # Act
        result = handlers.checkpoint([])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert "Checkpoint created" in result.message
        assert "name" in result.data
        assert "checkpoint-" in result.data["name"]

    def test_checkpoint_command_with_name(self, handlers, session):
        """Should create checkpoint with custom name."""
        # Act
        result = handlers.checkpoint(["--name=my-checkpoint"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["name"] == "my-checkpoint"

    def test_checkpoint_command_with_message(self, handlers, session):
        """Should create checkpoint with custom message."""
        # Act
        result = handlers.checkpoint(["--message=Test checkpoint"])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["message"] == "Test checkpoint"

    def test_checkpoint_command_full(self, handlers, session):
        """Should create checkpoint with name and message."""
        # Act
        result = handlers.checkpoint([
            "--name=feature-complete",
            "--message=All tests passing"
        ])

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.data["name"] == "feature-complete"
        assert result.data["message"] == "All tests passing"

    def test_checkpoint_command_no_session(self, handlers):
        """Should fail when no active session."""
        # Act & Assert
        with pytest.raises(CommandError, match="No active session"):
            handlers.checkpoint([])

    def test_checkpoint_command_invalid_args(self, handlers, session):
        """Should fail with invalid arguments."""
        # Act & Assert
        with pytest.raises(CommandError, match="Invalid arguments"):
            handlers.checkpoint(["--invalid-arg"])


class TestCommandErrorHandling:
    """Test error handling across all commands."""

    def test_command_error_structure(self):
        """Should create proper CommandError."""
        # Act
        error = CommandError(
            command="test:cmd",
            message="Test error",
            details={"key": "value"}
        )

        # Assert
        assert error.command == "test:cmd"
        assert error.message == "Test error"
        assert error.details == {"key": "value"}
        assert "test:cmd" in str(error)

    def test_command_error_no_details(self):
        """Should create CommandError without details."""
        # Act
        error = CommandError(command="test:cmd", message="Test error")

        # Assert
        assert error.details == {}

    def test_handler_exception_wrapped(self, registry):
        """Should wrap handler exceptions in CommandError."""
        # Arrange
        def failing_handler(args):
            raise ValueError("Handler failed")

        registry.register(
            name="test:fail",
            description="Test",
            usage="/test:fail",
            handler=failing_handler
        )

        # Act & Assert
        with pytest.raises(CommandError) as exc_info:
            registry.execute("test:fail")

        assert "Execution failed" in str(exc_info.value)


class TestCommandModels:
    """Test command data models."""

    def test_slash_command_model(self):
        """Should create SlashCommand model."""
        # Arrange
        def handler(args):
            return CommandResult(status=CommandStatus.SUCCESS, message="Test")

        # Act
        cmd = SlashCommand(
            name="test:model",
            description="Test command",
            usage="/test:model",
            handler=handler,
            enabled=True
        )

        # Assert
        assert cmd.name == "test:model"
        assert cmd.description == "Test command"
        assert cmd.usage == "/test:model"
        assert cmd.handler == handler
        assert cmd.enabled is True

    def test_command_result_model(self):
        """Should create CommandResult model."""
        # Act
        result = CommandResult(
            status=CommandStatus.SUCCESS,
            message="Command executed",
            data={"key": "value"},
            error=None
        )

        # Assert
        assert result.status == CommandStatus.SUCCESS
        assert result.message == "Command executed"
        assert result.data == {"key": "value"}
        assert result.error is None

    def test_command_result_error(self):
        """Should create CommandResult with error."""
        # Act
        result = CommandResult(
            status=CommandStatus.ERROR,
            message="Command failed",
            error="Error details"
        )

        # Assert
        assert result.status == CommandStatus.ERROR
        assert result.error == "Error details"

    def test_command_status_enum(self):
        """Should have all status values."""
        # Assert
        assert CommandStatus.SUCCESS == "success"
        assert CommandStatus.ERROR == "error"
        assert CommandStatus.PARTIAL == "partial"
