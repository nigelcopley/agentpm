"""
Unit Tests for InitOrchestrator

Tests the initialization orchestration service with Pydantic models.

Pattern: Pytest with fixtures and mocking
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from agentpm.core.services.init_orchestrator import InitOrchestrator
from agentpm.core.models.init_models import (
    InitConfig,
    InitResult,
    InitProgress,
    InitPhase,
    InitMode,
)


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def init_config(temp_project_dir):
    """Create InitConfig for testing"""
    return InitConfig(
        project_name="TestProject",
        project_path=temp_project_dir,
        mode=InitMode.AUTO,
        skip_detection=True,
        skip_rules=True,
        skip_agents=True,
    )


@pytest.fixture
def progress_callback():
    """Mock progress callback"""
    return Mock()


class TestInitConfig:
    """Test InitConfig Pydantic model"""

    def test_init_config_creation(self, temp_project_dir):
        """Test creating InitConfig"""
        config = InitConfig(
            project_name="Test",
            project_path=temp_project_dir,
        )

        assert config.project_name == "Test"
        assert config.project_path == temp_project_dir
        assert config.mode == InitMode.AUTO
        assert config.skip_detection is False
        assert config.force_reset is False

    def test_init_config_validation(self):
        """Test InitConfig validation"""
        # Invalid project name (empty)
        with pytest.raises(ValueError):
            InitConfig(
                project_name="",
                project_path=Path("/tmp/test"),
            )


class TestInitProgress:
    """Test InitProgress Pydantic model"""

    def test_init_progress_creation(self):
        """Test creating InitProgress"""
        progress = InitProgress(
            phase=InitPhase.DATABASE,
            current_step=2,
            total_steps=6,
            message="Initializing database",
        )

        assert progress.phase == InitPhase.DATABASE
        assert progress.current_step == 2
        assert progress.total_steps == 6
        assert progress.message == "Initializing database"

    def test_init_progress_validation(self):
        """Test InitProgress validation"""
        # Invalid step (< 1)
        with pytest.raises(ValueError):
            InitProgress(
                phase=InitPhase.PREFLIGHT,
                current_step=0,
                total_steps=6,
                message="Test",
            )


class TestInitResult:
    """Test InitResult Pydantic model"""

    def test_init_result_success(self, temp_project_dir):
        """Test successful InitResult"""
        result = InitResult(
            success=True,
            project_name="Test",
            database_path=temp_project_dir / ".agentpm" / "data" / "agentpm.db",
            agents_generated=0,
            rules_loaded=50,
            technologies_detected=["python", "django"],
            duration_ms=1234.5,
        )

        assert result.success is True
        assert result.project_name == "Test"
        assert result.rules_loaded == 50
        assert result.technologies_detected == ["python", "django"]
        assert not result.has_errors()
        assert not result.has_warnings()

    def test_init_result_failure(self):
        """Test failed InitResult"""
        result = InitResult(
            success=False,
            project_name="Test",
            errors=["Database initialization failed"],
            warnings=["Detection failed"],
            duration_ms=500.0,
        )

        assert result.success is False
        assert result.has_errors()
        assert result.has_warnings()
        assert len(result.errors) == 1


class TestInitOrchestrator:
    """Test InitOrchestrator service"""

    def test_orchestrator_creation(self, init_config, progress_callback):
        """Test creating InitOrchestrator"""
        orchestrator = InitOrchestrator(
            config=init_config,
            progress_callback=progress_callback,
        )

        assert orchestrator.config == init_config
        assert orchestrator.progress_callback == progress_callback
        assert orchestrator.db is None
        assert orchestrator.project is None

    def test_preflight_checks_success(self, init_config):
        """Test preflight checks pass"""
        orchestrator = InitOrchestrator(config=init_config)

        # Should not raise
        orchestrator._preflight_checks()

    def test_preflight_checks_already_initialized(self, init_config):
        """Test preflight checks fail when already initialized"""
        # Create .agentpm directory
        (init_config.project_path / ".agentpm").mkdir()

        orchestrator = InitOrchestrator(config=init_config)

        with pytest.raises(RuntimeError, match="already initialized"):
            orchestrator._preflight_checks()

    def test_preflight_checks_force_reset(self, init_config):
        """Test preflight checks with force_reset"""
        # Create .agentpm directory
        agentpm_dir = init_config.project_path / ".agentpm"
        agentpm_dir.mkdir()

        # Enable force_reset
        init_config.force_reset = True

        orchestrator = InitOrchestrator(config=init_config)
        orchestrator._preflight_checks()

        # Directory should be removed
        assert not agentpm_dir.exists()

    def test_create_directories(self, init_config):
        """Test directory creation"""
        orchestrator = InitOrchestrator(config=init_config)
        orchestrator._create_directories()

        # Check directories created
        assert (init_config.project_path / ".agentpm").exists()
        assert (init_config.project_path / ".agentpm" / "data").exists()
        assert (init_config.project_path / ".agentpm" / "logs").exists()
        assert (init_config.project_path / ".agentpm" / "contexts").exists()
        assert (init_config.project_path / ".claude" / "agents").exists()

        # Check rollback plan
        assert len(orchestrator.rollback_plan.actions) > 0

    @patch("agentpm.core.services.init_orchestrator.DatabaseService")
    @patch("agentpm.core.services.init_orchestrator.project_methods")
    def test_initialize_database(
        self, mock_project_methods, mock_db_service, init_config
    ):
        """Test database initialization"""
        # Setup mocks
        mock_db = MagicMock()
        mock_db_service.return_value = mock_db

        mock_project = MagicMock()
        mock_project.id = 1
        mock_project_methods.create_project.return_value = mock_project

        # Create directories first
        (init_config.project_path / ".agentpm" / "data").mkdir(parents=True)

        orchestrator = InitOrchestrator(config=init_config)
        orchestrator._initialize_database()

        # Check database service created
        assert orchestrator.db == mock_db

        # Check project created
        assert orchestrator.project == mock_project

        # Check rollback plan
        assert any(
            action.action_type == "database_init"
            for action in orchestrator.rollback_plan.actions
        )

    @patch("agentpm.core.services.init_orchestrator.DetectionOrchestrator")
    def test_detect_technologies_skipped(self, mock_detection, init_config):
        """Test detection skipped when configured"""
        init_config.skip_detection = True

        orchestrator = InitOrchestrator(config=init_config)
        orchestrator._detect_technologies()

        # Detection should not run
        mock_detection.assert_not_called()

        # Should have empty detection result
        assert orchestrator.detection_result is not None
        assert len(orchestrator.detection_result.matches) == 0

    def test_update_progress(self, init_config, progress_callback):
        """Test progress updates"""
        orchestrator = InitOrchestrator(
            config=init_config, progress_callback=progress_callback
        )

        orchestrator._update_progress(
            current=1,
            total=6,
            message="Test message",
            phase=InitPhase.PREFLIGHT,
        )

        # Check callback called
        progress_callback.assert_called_once()

        # Check progress object
        progress = progress_callback.call_args[0][0]
        assert isinstance(progress, InitProgress)
        assert progress.phase == InitPhase.PREFLIGHT
        assert progress.current_step == 1
        assert progress.total_steps == 6

    def test_rollback(self, init_config):
        """Test rollback functionality"""
        orchestrator = InitOrchestrator(config=init_config)

        # Create directories
        orchestrator._create_directories()

        # Check directories exist
        assert (init_config.project_path / ".agentpm").exists()

        # Rollback
        orchestrator.rollback()

        # Check directories removed
        assert not (init_config.project_path / ".agentpm").exists()

    @patch("agentpm.core.services.init_orchestrator.DatabaseService")
    @patch("agentpm.core.services.init_orchestrator.project_methods")
    @patch("agentpm.core.services.init_orchestrator.DetectionOrchestrator")
    def test_orchestrate_success(
        self,
        mock_detection,
        mock_project_methods,
        mock_db_service,
        init_config,
    ):
        """Test complete orchestration success (without verification)"""
        # Setup mocks
        mock_db = MagicMock()
        mock_db.transaction.return_value.__enter__ = lambda self: MagicMock()
        mock_db.transaction.return_value.__exit__ = lambda self, *args: None
        mock_db_service.return_value = mock_db

        mock_project = MagicMock()
        mock_project.id = 1
        mock_project_methods.create_project.return_value = mock_project

        # Mock _verify_installation to avoid complex mocking of sqlite3 and file system
        orchestrator = InitOrchestrator(config=init_config)
        orchestrator._verify_installation = MagicMock()  # Skip verification for this test

        result = orchestrator.orchestrate()

        # Check result
        assert isinstance(result, InitResult)
        assert result.success is True
        assert result.project_name == "TestProject"
        assert result.duration_ms > 0
        assert not result.has_errors()

        # Check verification was called
        orchestrator._verify_installation.assert_called_once()

    @patch("agentpm.core.services.init_orchestrator.DatabaseService")
    def test_orchestrate_failure_with_rollback(self, mock_db_service, init_config):
        """Test orchestration failure triggers rollback"""
        # Make database initialization fail
        mock_db_service.side_effect = Exception("Database error")

        # Run orchestration
        orchestrator = InitOrchestrator(config=init_config)
        result = orchestrator.orchestrate()

        # Check result
        assert isinstance(result, InitResult)
        assert result.success is False
        assert result.has_errors()
        assert "Database error" in result.errors[0]

        # Check directories cleaned up
        assert not (init_config.project_path / ".agentpm").exists()


class TestRollbackPlan:
    """Test RollbackPlan functionality"""

    def test_add_action(self):
        """Test adding rollback actions"""
        from agentpm.core.models.init_models import RollbackPlan

        plan = RollbackPlan()
        plan.add_action("create_directory", "/tmp/test")

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == "create_directory"
        assert plan.actions[0].target == "/tmp/test"

    def test_get_rollback_order(self):
        """Test rollback order is reversed"""
        from agentpm.core.models.init_models import RollbackPlan

        plan = RollbackPlan()
        plan.add_action("action1", "target1")
        plan.add_action("action2", "target2")
        plan.add_action("action3", "target3")

        rollback_order = plan.get_rollback_order()

        assert len(rollback_order) == 3
        assert rollback_order[0].action_type == "action3"
        assert rollback_order[1].action_type == "action2"
        assert rollback_order[2].action_type == "action1"
