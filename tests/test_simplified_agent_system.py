"""
Tests for Simplified Agent System

This module contains comprehensive tests for the simplified agent system including
workflow orchestrator, phase orchestrator, quality orchestrator, and performance optimizer.

Target: 95% coverage for critical paths, 85% for user-facing code, 90% for data layer, 95% for security
"""

import pytest
import asyncio
import time
import tempfile
import sqlite3
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Import the modules under test
from agentpm.core.agents.simplified.workflow_orchestrator import (
    WorkflowOrchestrator, WorkflowDecision, WorkflowContext, create_workflow_orchestrator
)
from agentpm.core.agents.simplified.phase_orchestrator import (
    PhaseOrchestrator, PhaseGateStatus, PhaseGate, PhaseContext, create_phase_orchestrator
)
from agentpm.core.agents.simplified.quality_orchestrator import (
    QualityOrchestrator, QualityGateType, QualityLevel, QualityGate, QualityMetrics, create_quality_orchestrator
)
from agentpm.core.performance.optimizer import (
    PerformanceOptimizer, LRUCache, MultiLevelCache, DatabaseConnectionPool, 
    CacheLevel, PerformanceMetrics, create_performance_optimizer
)
from agentpm.database.enums import WorkItemStatus, Phase, TaskStatus


class TestWorkflowOrchestrator:
    """Test suite for WorkflowOrchestrator"""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service"""
        return Mock()
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock performance monitor"""
        return Mock()
    
    @pytest.fixture
    def workflow_orchestrator(self, mock_db_service, mock_performance_monitor):
        """Create workflow orchestrator instance"""
        return WorkflowOrchestrator(mock_db_service, mock_performance_monitor)
    
    @pytest.fixture
    def sample_work_item(self):
        """Sample work item for testing"""
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Test Work Item"
        work_item.status = WorkItemStatus.ACTIVE
        work_item.phase = Phase.I1_IMPLEMENTATION
        return work_item
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_success(self, workflow_orchestrator, sample_work_item):
        """Test successful workflow coordination"""
        # Mock the internal methods
        workflow_orchestrator._create_workflow_context = AsyncMock(return_value=Mock())
        workflow_orchestrator._make_high_level_decisions = AsyncMock(return_value=WorkflowDecision.PROCEED)
        workflow_orchestrator._execute_workflow = AsyncMock(return_value={"action": "proceed"})
        workflow_orchestrator._monitor_performance = AsyncMock()
        
        result = await workflow_orchestrator.coordinate_workflow(sample_work_item)
        
        assert result["status"] == "success"
        assert result["decision"] == "proceed"
        assert "execution_time" in result
        assert result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_coordinate_workflow_error(self, workflow_orchestrator, sample_work_item):
        """Test workflow coordination with error"""
        # Mock error in context creation
        workflow_orchestrator._create_workflow_context = AsyncMock(side_effect=Exception("Test error"))
        workflow_orchestrator._handle_errors = AsyncMock()
        
        result = await workflow_orchestrator.coordinate_workflow(sample_work_item)
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_make_high_level_decisions_proceed(self, workflow_orchestrator):
        """Test high-level decision making - proceed"""
        context = Mock()
        context.error_context = None
        context.performance_metrics = {"execution_time": 1.0}
        context.work_item = Mock()
        context.work_item.status = WorkItemStatus.ACTIVE
        
        workflow_orchestrator._is_performance_degraded = Mock(return_value=False)
        workflow_orchestrator._are_phase_requirements_met = Mock(return_value=True)
        
        decision = await workflow_orchestrator.make_high_level_decisions(context)
        
        assert decision == WorkflowDecision.PROCEED
    
    @pytest.mark.asyncio
    async def test_make_high_level_decisions_escalate(self, workflow_orchestrator):
        """Test high-level decision making - escalate"""
        context = Mock()
        context.error_context = {"error": "Test error"}
        
        decision = await workflow_orchestrator.make_high_level_decisions(context)
        
        assert decision == WorkflowDecision.ESCALATE
    
    @pytest.mark.asyncio
    async def test_make_high_level_decisions_pause(self, workflow_orchestrator):
        """Test high-level decision making - pause"""
        context = Mock()
        context.error_context = None
        context.performance_metrics = {"execution_time": 10.0}  # Degraded performance
        context.work_item = Mock()
        context.work_item.status = WorkItemStatus.ACTIVE
        
        workflow_orchestrator._is_performance_degraded = Mock(return_value=True)
        
        decision = await workflow_orchestrator.make_high_level_decisions(context)
        
        assert decision == WorkflowDecision.PAUSE
    
    @pytest.mark.asyncio
    async def test_handle_errors_timeout(self, workflow_orchestrator):
        """Test error handling - timeout"""
        error_context = {"error_type": "timeout"}
        
        result = await workflow_orchestrator.handle_errors(error_context)
        
        assert result["recovery_action"] == "retry"
        assert result["backoff_seconds"] == 5
        assert result["max_retries"] == 3
    
    @pytest.mark.asyncio
    async def test_handle_errors_validation_failure(self, workflow_orchestrator):
        """Test error handling - validation failure"""
        error_context = {"error_type": "validation_failure"}
        
        result = await workflow_orchestrator.handle_errors(error_context)
        
        assert result["recovery_action"] == "escalate"
        assert "manual intervention" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_handle_errors_agent_unavailable(self, workflow_orchestrator):
        """Test error handling - agent unavailable"""
        error_context = {"error_type": "agent_unavailable"}
        
        result = await workflow_orchestrator.handle_errors(error_context)
        
        assert result["recovery_action"] == "retry"
        assert result["backoff_seconds"] == 10
        assert result["max_retries"] == 2
    
    @pytest.mark.asyncio
    async def test_handle_errors_performance_degradation(self, workflow_orchestrator):
        """Test error handling - performance degradation"""
        error_context = {"error_type": "performance_degradation"}
        
        result = await workflow_orchestrator.handle_errors(error_context)
        
        assert result["recovery_action"] == "pause"
        assert "Performance degradation" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_handle_errors_unknown(self, workflow_orchestrator):
        """Test error handling - unknown error"""
        error_context = {"error_type": "unknown_error"}
        
        result = await workflow_orchestrator.handle_errors(error_context)
        
        assert result["recovery_action"] == "escalate"
        assert "Unknown error" in result["reason"]
    
    def test_is_performance_degraded_true(self, workflow_orchestrator):
        """Test performance degradation detection - true"""
        metrics = {"execution_time": 10.0}  # Above 5.0 threshold
        
        result = workflow_orchestrator._is_performance_degraded(metrics)
        
        assert result is True
    
    def test_is_performance_degraded_false(self, workflow_orchestrator):
        """Test performance degradation detection - false"""
        metrics = {"execution_time": 2.0}  # Below 5.0 threshold
        
        result = workflow_orchestrator._is_performance_degraded(metrics)
        
        assert result is False
    
    def test_are_phase_requirements_met(self, workflow_orchestrator):
        """Test phase requirements check"""
        context = Mock()
        
        result = workflow_orchestrator._are_phase_requirements_met(context)
        
        assert result is True  # Placeholder implementation returns True
    
    def test_create_workflow_orchestrator_factory(self, mock_db_service):
        """Test workflow orchestrator factory function"""
        orchestrator = create_workflow_orchestrator(mock_db_service)
        
        assert isinstance(orchestrator, WorkflowOrchestrator)
        assert orchestrator.db_service == mock_db_service


class TestPhaseOrchestrator:
    """Test suite for PhaseOrchestrator"""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service"""
        return Mock()
    
    @pytest.fixture
    def mock_quality_orchestrator(self):
        """Mock quality orchestrator"""
        return Mock()
    
    @pytest.fixture
    def phase_orchestrator(self, mock_db_service, mock_quality_orchestrator):
        """Create phase orchestrator instance"""
        return PhaseOrchestrator(mock_db_service, mock_quality_orchestrator)
    
    @pytest.fixture
    def sample_work_item(self):
        """Sample work item for testing"""
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Test Work Item"
        work_item.phase = Phase.I1_IMPLEMENTATION
        return work_item
    
    @pytest.mark.asyncio
    async def test_orchestrate_phase_success(self, phase_orchestrator, sample_work_item):
        """Test successful phase orchestration"""
        # Mock internal methods
        phase_orchestrator._create_phase_context = AsyncMock(return_value=Mock())
        phase_orchestrator._enforce_phase_gates = AsyncMock(return_value={"gate1": {"passed": True}})
        phase_orchestrator._execute_phase_logic = AsyncMock(return_value={"phase": "implementation"})
        phase_orchestrator._check_transition_readiness = AsyncMock(return_value=True)
        
        result = await phase_orchestrator.orchestrate_phase(Phase.I1_IMPLEMENTATION, sample_work_item)
        
        assert result["status"] == "success"
        assert result["phase"] == "i1_implementation"
        assert "gate_results" in result
        assert "phase_result" in result
        assert result["transition_ready"] is True
    
    @pytest.mark.asyncio
    async def test_orchestrate_phase_error(self, phase_orchestrator, sample_work_item):
        """Test phase orchestration with error"""
        # Mock error in context creation
        phase_orchestrator._create_phase_context = AsyncMock(side_effect=Exception("Test error"))
        
        result = await phase_orchestrator.orchestrate_phase(Phase.I1_IMPLEMENTATION, sample_work_item)
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_enforce_phase_gates(self, phase_orchestrator, sample_work_item):
        """Test phase gate enforcement"""
        # Mock internal methods
        phase_orchestrator._create_phase_context = AsyncMock(return_value=Mock())
        phase_orchestrator._enforce_phase_gates = AsyncMock(return_value={"gate1": {"passed": True}})
        
        result = await phase_orchestrator.enforce_phase_gates(Phase.I1_IMPLEMENTATION, sample_work_item)
        
        assert "gate1" in result
        assert result["gate1"]["passed"] is True
    
    @pytest.mark.asyncio
    async def test_manage_phase_transitions_success(self, phase_orchestrator, sample_work_item):
        """Test successful phase transition management"""
        # Mock internal methods
        phase_orchestrator._is_transition_allowed = Mock(return_value=True)
        phase_orchestrator._execute_transition_logic = AsyncMock(return_value={"transition": "success"})
        phase_orchestrator._update_work_item_phase = AsyncMock()
        
        result = await phase_orchestrator.manage_phase_transitions(
            Phase.P1_PLAN, Phase.I1_IMPLEMENTATION, sample_work_item
        )
        
        assert result["status"] == "success"
        assert result["from_phase"] == "p1_plan"
        assert result["to_phase"] == "i1_implementation"
    
    @pytest.mark.asyncio
    async def test_manage_phase_transitions_not_allowed(self, phase_orchestrator, sample_work_item):
        """Test phase transition management - transition not allowed"""
        phase_orchestrator._is_transition_allowed = Mock(return_value=False)
        
        result = await phase_orchestrator.manage_phase_transitions(
            Phase.I1_IMPLEMENTATION, Phase.D1_DISCOVERY, sample_work_item
        )
        
        assert result["status"] == "error"
        assert "not allowed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_discovery_phase(self, phase_orchestrator):
        """Test discovery phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_discovery_phase(context)
        
        assert result["phase"] == "discovery"
        assert "actions" in result
        assert "deliverables" in result
        assert len(result["actions"]) > 0
        assert len(result["deliverables"]) > 0
    
    @pytest.mark.asyncio
    async def test_handle_planning_phase(self, phase_orchestrator):
        """Test planning phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_planning_phase(context)
        
        assert result["phase"] == "planning"
        assert "actions" in result
        assert "deliverables" in result
    
    @pytest.mark.asyncio
    async def test_handle_implementation_phase(self, phase_orchestrator):
        """Test implementation phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_implementation_phase(context)
        
        assert result["phase"] == "implementation"
        assert "actions" in result
        assert "deliverables" in result
    
    @pytest.mark.asyncio
    async def test_handle_review_phase(self, phase_orchestrator):
        """Test review phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_review_phase(context)
        
        assert result["phase"] == "review"
        assert "actions" in result
        assert "deliverables" in result
    
    @pytest.mark.asyncio
    async def test_handle_operations_phase(self, phase_orchestrator):
        """Test operations phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_operations_phase(context)
        
        assert result["phase"] == "operations"
        assert "actions" in result
        assert "deliverables" in result
    
    @pytest.mark.asyncio
    async def test_handle_evolution_phase(self, phase_orchestrator):
        """Test evolution phase handling"""
        context = Mock()
        
        result = await phase_orchestrator._handle_evolution_phase(context)
        
        assert result["phase"] == "evolution"
        assert "actions" in result
        assert "deliverables" in result
    
    def test_is_transition_allowed_valid(self, phase_orchestrator):
        """Test valid phase transition"""
        result = phase_orchestrator._is_transition_allowed(
            Phase.D1_DISCOVERY, Phase.P1_PLAN
        )
        
        assert result is True
    
    def test_is_transition_allowed_invalid(self, phase_orchestrator):
        """Test invalid phase transition"""
        result = phase_orchestrator._is_transition_allowed(
            Phase.I1_IMPLEMENTATION, Phase.D1_DISCOVERY
        )
        
        assert result is False
    
    def test_get_phase_gates(self, phase_orchestrator):
        """Test getting phase gates"""
        gates = phase_orchestrator._get_phase_gates(Phase.D1_DISCOVERY)
        
        assert len(gates) > 0
        assert all(isinstance(gate, PhaseGate) for gate in gates)
    
    def test_create_phase_orchestrator_factory(self, mock_db_service):
        """Test phase orchestrator factory function"""
        orchestrator = create_phase_orchestrator(mock_db_service)
        
        assert isinstance(orchestrator, PhaseOrchestrator)
        assert orchestrator.db_service == mock_db_service


class TestQualityOrchestrator:
    """Test suite for QualityOrchestrator"""
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock database service"""
        return Mock()
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Mock metrics collector"""
        return Mock()
    
    @pytest.fixture
    def quality_orchestrator(self, mock_db_service, mock_metrics_collector):
        """Create quality orchestrator instance"""
        return QualityOrchestrator(mock_db_service, mock_metrics_collector)
    
    @pytest.fixture
    def sample_work_item(self):
        """Sample work item for testing"""
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Test Work Item"
        return work_item
    
    @pytest.mark.asyncio
    async def test_enforce_quality_gates_success(self, quality_orchestrator, sample_work_item):
        """Test successful quality gate enforcement"""
        # Mock internal methods
        quality_orchestrator._get_gates_by_type = Mock(return_value=[])
        quality_orchestrator._validate_gates = AsyncMock(return_value={})
        quality_orchestrator._track_quality_metrics = AsyncMock()
        quality_orchestrator._generate_quality_report = AsyncMock(return_value={"pass_rate": 100})
        
        result = await quality_orchestrator.enforce_quality_gates(
            QualityGateType.FUNCTIONAL, sample_work_item
        )
        
        assert result["status"] == "success"
        assert result["gate_type"] == "functional"
        assert "validation_results" in result
        assert "quality_report" in result
    
    @pytest.mark.asyncio
    async def test_enforce_quality_gates_error(self, quality_orchestrator, sample_work_item):
        """Test quality gate enforcement with error"""
        # Mock error in gate enforcement
        quality_orchestrator._get_gates_by_type = Mock(side_effect=Exception("Test error"))
        
        result = await quality_orchestrator.enforce_quality_gates(
            QualityGateType.FUNCTIONAL, sample_work_item
        )
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_gates(self, quality_orchestrator, sample_work_item):
        """Test gate validation"""
        gates = [
            QualityGate(
                name="test_gate",
                description="Test gate",
                gate_type=QualityGateType.FUNCTIONAL,
                level=QualityLevel.HIGH,
                required=True,
                validation_function="validate_test"
            )
        ]
        
        # Mock validation function
        quality_orchestrator._validate_test = AsyncMock(return_value={"passed": True})
        quality_orchestrator.validation_functions["validate_test"] = quality_orchestrator._validate_test
        
        result = await quality_orchestrator.validate_gates(gates, sample_work_item)
        
        assert "test_gate" in result
        assert result["test_gate"]["passed"] is True
    
    @pytest.mark.asyncio
    async def test_validate_gates_missing_function(self, quality_orchestrator, sample_work_item):
        """Test gate validation with missing validation function"""
        gates = [
            QualityGate(
                name="test_gate",
                description="Test gate",
                gate_type=QualityGateType.FUNCTIONAL,
                level=QualityLevel.HIGH,
                required=True,
                validation_function="missing_function"
            )
        ]
        
        result = await quality_orchestrator.validate_gates(gates, sample_work_item)
        
        assert "test_gate" in result
        assert result["test_gate"]["passed"] is False
        assert "not found" in result["test_gate"]["error"]
    
    @pytest.mark.asyncio
    async def test_validate_gates_exception(self, quality_orchestrator, sample_work_item):
        """Test gate validation with exception"""
        gates = [
            QualityGate(
                name="test_gate",
                description="Test gate",
                gate_type=QualityGateType.FUNCTIONAL,
                level=QualityLevel.HIGH,
                required=True,
                validation_function="validate_test"
            )
        ]
        
        # Mock validation function that raises exception
        quality_orchestrator._validate_test = AsyncMock(side_effect=Exception("Validation error"))
        quality_orchestrator.validation_functions["validate_test"] = quality_orchestrator._validate_test
        
        result = await quality_orchestrator.validate_gates(gates, sample_work_item)
        
        assert "test_gate" in result
        assert result["test_gate"]["passed"] is False
        assert "Validation error" in result["test_gate"]["error"]
    
    @pytest.mark.asyncio
    async def test_track_quality_metrics(self, quality_orchestrator, sample_work_item):
        """Test quality metrics tracking"""
        # Mock internal methods
        quality_orchestrator._track_functional_quality = AsyncMock(return_value={"functional_completeness": 0.95})
        quality_orchestrator._track_performance_quality = AsyncMock(return_value={"response_time": 95.0})
        quality_orchestrator._track_security_quality = AsyncMock(return_value={"vulnerability_count": 0})
        quality_orchestrator._track_compliance_quality = AsyncMock(return_value={"standards_compliance": 0.92})
        quality_orchestrator._store_quality_metrics = AsyncMock()
        
        result = await quality_orchestrator.track_quality_metrics(sample_work_item)
        
        assert "functional_completeness" in result
        assert "response_time" in result
        assert "vulnerability_count" in result
        assert "standards_compliance" in result
    
    @pytest.mark.asyncio
    async def test_ensure_compliance(self, quality_orchestrator, sample_work_item):
        """Test compliance checking"""
        # Mock internal methods
        quality_orchestrator._check_functional_compliance = AsyncMock(return_value={"compliant": True, "score": 0.95})
        quality_orchestrator._check_performance_compliance = AsyncMock(return_value={"compliant": True, "score": 0.90})
        quality_orchestrator._check_security_compliance = AsyncMock(return_value={"compliant": True, "score": 0.98})
        quality_orchestrator._check_regulatory_compliance = AsyncMock(return_value={"compliant": True, "score": 0.92})
        
        result = await quality_orchestrator.ensure_compliance(sample_work_item)
        
        assert "functional" in result
        assert "performance" in result
        assert "security" in result
        assert "regulatory" in result
        
        assert result["functional"]["compliant"] is True
        assert result["performance"]["compliant"] is True
        assert result["security"]["compliant"] is True
        assert result["regulatory"]["compliant"] is True
    
    @pytest.mark.asyncio
    async def test_validate_acceptance_criteria(self, quality_orchestrator, sample_work_item):
        """Test acceptance criteria validation"""
        gate = QualityGate(
            name="acceptance_criteria_met",
            description="All acceptance criteria are met",
            gate_type=QualityGateType.FUNCTIONAL,
            level=QualityLevel.CRITICAL,
            required=True,
            validation_function="validate_acceptance_criteria"
        )
        
        result = await quality_orchestrator._validate_acceptance_criteria(sample_work_item, gate)
        
        assert result["passed"] is True
        assert result["value"] == 1.0
        assert result["threshold"] == 1.0
        assert "All acceptance criteria met" in result["message"]
    
    @pytest.mark.asyncio
    async def test_validate_response_time(self, quality_orchestrator, sample_work_item):
        """Test response time validation"""
        gate = QualityGate(
            name="response_time",
            description="Response time meets requirements",
            gate_type=QualityGateType.PERFORMANCE,
            level=QualityLevel.HIGH,
            required=True,
            validation_function="validate_response_time",
            threshold=100.0
        )
        
        result = await quality_orchestrator._validate_response_time(sample_work_item, gate)
        
        assert result["passed"] is True  # 95ms < 100ms threshold
        assert result["value"] == 95.0
        assert result["threshold"] == 100.0
        assert "Response time: 95.0ms" in result["message"]
    
    @pytest.mark.asyncio
    async def test_validate_throughput(self, quality_orchestrator, sample_work_item):
        """Test throughput validation"""
        gate = QualityGate(
            name="throughput",
            description="Throughput meets requirements",
            gate_type=QualityGateType.PERFORMANCE,
            level=QualityLevel.MEDIUM,
            required=True,
            validation_function="validate_throughput",
            threshold=1000.0
        )
        
        result = await quality_orchestrator._validate_throughput(sample_work_item, gate)
        
        assert result["passed"] is True  # 1200 req/s > 1000 req/s threshold
        assert result["value"] == 1200.0
        assert result["threshold"] == 1000.0
        assert "Throughput: 1200.0 req/s" in result["message"]
    
    @pytest.mark.asyncio
    async def test_validate_memory_usage(self, quality_orchestrator, sample_work_item):
        """Test memory usage validation"""
        gate = QualityGate(
            name="memory_usage",
            description="Memory usage within limits",
            gate_type=QualityGateType.PERFORMANCE,
            level=QualityLevel.MEDIUM,
            required=True,
            validation_function="validate_memory_usage",
            threshold=500.0
        )
        
        result = await quality_orchestrator._validate_memory_usage(sample_work_item, gate)
        
        assert result["passed"] is True  # 450MB < 500MB threshold
        assert result["value"] == 450.0
        assert result["threshold"] == 500.0
        assert "Memory usage: 450.0MB" in result["message"]
    
    @pytest.mark.asyncio
    async def test_validate_security_scan(self, quality_orchestrator, sample_work_item):
        """Test security scan validation"""
        gate = QualityGate(
            name="security_scan",
            description="Security scan passes",
            gate_type=QualityGateType.SECURITY,
            level=QualityLevel.CRITICAL,
            required=True,
            validation_function="validate_security_scan"
        )
        
        result = await quality_orchestrator._validate_security_scan(sample_work_item, gate)
        
        assert result["passed"] is True
        assert result["value"] == 1.0
        assert result["threshold"] == 1.0
        assert "Security scan passed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_validate_vulnerabilities(self, quality_orchestrator, sample_work_item):
        """Test vulnerability validation"""
        gate = QualityGate(
            name="vulnerability_check",
            description="No critical vulnerabilities",
            gate_type=QualityGateType.SECURITY,
            level=QualityLevel.CRITICAL,
            required=True,
            validation_function="validate_vulnerabilities"
        )
        
        result = await quality_orchestrator._validate_vulnerabilities(sample_work_item, gate)
        
        assert result["passed"] is True
        assert result["value"] == 0.0
        assert result["threshold"] == 0.0
        assert "No critical vulnerabilities found" in result["message"]
    
    def test_get_gates_by_type(self, quality_orchestrator):
        """Test getting gates by type"""
        gates = quality_orchestrator._get_gates_by_type(QualityGateType.FUNCTIONAL)
        
        assert len(gates) > 0
        assert all(gate.gate_type == QualityGateType.FUNCTIONAL for gate in gates)
    
    def test_create_quality_orchestrator_factory(self, mock_db_service):
        """Test quality orchestrator factory function"""
        orchestrator = create_quality_orchestrator(mock_db_service)
        
        assert isinstance(orchestrator, QualityOrchestrator)
        assert orchestrator.db_service == mock_db_service


class TestPerformanceOptimizer:
    """Test suite for PerformanceOptimizer"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test database with required tables
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE work_items (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                phase TEXT,
                status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                created_at TEXT
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO tasks (id, name, type, status) VALUES (1, 'Test Task', 'implementation', 'active')")
        conn.execute("INSERT INTO work_items (id, name, type, phase, status) VALUES (1, 'Test WI', 'feature', 'i1_implementation', 'active')")
        conn.execute("INSERT INTO projects (id, name, description, created_at) VALUES (1, 'Test Project', 'Test Description', '2025-01-01')")
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def performance_optimizer(self, temp_db):
        """Create performance optimizer instance"""
        return PerformanceOptimizer(temp_db)
    
    def test_lru_cache_basic_operations(self):
        """Test LRU cache basic operations"""
        cache = LRUCache(size=3, ttl=60)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test cache miss
        assert cache.get("key2") is None
        
        # Test TTL expiration
        cache.set("key3", "value3", ttl=0.001)  # 1ms TTL
        time.sleep(0.002)  # Wait for expiration
        assert cache.get("key3") is None
        
        # Test LRU eviction
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_lru_cache_stats(self):
        """Test LRU cache statistics"""
        cache = LRUCache(size=10, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.stats()
        
        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert stats["ttl"] == 60
    
    def test_multi_level_cache_basic_operations(self):
        """Test multi-level cache basic operations"""
        cache = MultiLevelCache()
        
        # Test set and get
        cache.set("key1", "value1", CacheLevel.L1)
        assert cache.get("key1") == "value1"
        
        # Test cache miss
        assert cache.get("key2") is None
        
        # Test promotion from L2 to L1
        cache.set("key3", "value3", CacheLevel.L2)
        assert cache.get("key3") == "value3"
        # Should now be in L1 cache
        assert cache.l1_cache.get("key3") == "value3"
    
    def test_multi_level_cache_stats(self):
        """Test multi-level cache statistics"""
        cache = MultiLevelCache()
        
        cache.set("key1", "value1", CacheLevel.L1)
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.stats()
        
        assert stats["hit_counters"]["l1"] == 1
        assert stats["hit_counters"]["miss"] == 1
        assert stats["overall_hit_rate"] == 0.5
    
    def test_database_connection_pool(self, temp_db):
        """Test database connection pool"""
        pool = DatabaseConnectionPool(temp_db, pool_size=2)
        
        # Test getting and returning connections
        conn1 = pool.get_connection()
        conn2 = pool.get_connection()
        
        assert len(pool.available_connections) == 0
        assert len(pool.used_connections) == 2
        
        pool.return_connection(conn1)
        
        assert len(pool.available_connections) == 1
        assert len(pool.used_connections) == 1
        
        # Test connection functionality
        cursor = conn2.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        assert count == 1
        
        pool.return_connection(conn2)
        pool.close_all()
    
    @pytest.mark.asyncio
    async def test_optimize_taskstart_success(self, performance_optimizer):
        """Test successful TaskStart optimization"""
        result = await performance_optimizer.optimize_taskstart(1, 1, 1)
        
        assert result["status"] == "success"
        assert "execution_time" in result
        assert "context" in result
        assert "agent_validation" in result
        assert result["performance_target_met"] is True
        assert result["execution_time"] < 0.1  # 100ms target
    
    @pytest.mark.asyncio
    async def test_optimize_taskstart_error(self, performance_optimizer):
        """Test TaskStart optimization with error"""
        # Test with non-existent IDs
        result = await performance_optimizer.optimize_taskstart(999, 999, 999)
        
        assert result["status"] == "success"  # Should handle missing data gracefully
        assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_load_task_optimized(self, performance_optimizer):
        """Test optimized task loading"""
        result = await performance_optimizer._load_task_optimized(1)
        
        assert "id" in result
        assert result["id"] == 1
        assert result["name"] == "Test Task"
    
    @pytest.mark.asyncio
    async def test_load_work_item_optimized(self, performance_optimizer):
        """Test optimized work item loading"""
        result = await performance_optimizer._load_work_item_optimized(1)
        
        assert "id" in result
        assert result["id"] == 1
        assert result["name"] == "Test WI"
    
    @pytest.mark.asyncio
    async def test_load_project_optimized(self, performance_optimizer):
        """Test optimized project loading"""
        result = await performance_optimizer._load_project_optimized(1)
        
        assert "id" in result
        assert result["id"] == 1
        assert result["name"] == "Test Project"
    
    @pytest.mark.asyncio
    async def test_assemble_context_parallel(self, performance_optimizer):
        """Test parallel context assembly"""
        task = {"id": 1, "name": "Test Task", "type": "implementation", "status": "active", "effort_hours": 4.0}
        work_item = {"id": 1, "name": "Test WI", "type": "feature", "phase": "i1_implementation", "status": "active"}
        project = {"id": 1, "name": "Test Project", "description": "Test Description", "created_at": "2025-01-01"}
        
        result = await performance_optimizer._assemble_context_parallel(task, work_item, project)
        
        assert "task" in result
        assert "work_item" in result
        assert "project" in result
        assert "assembled_at" in result
        
        assert result["task"]["id"] == 1
        assert result["work_item"]["id"] == 1
        assert result["project"]["id"] == 1
    
    @pytest.mark.asyncio
    async def test_validate_agents_optimized(self, performance_optimizer):
        """Test optimized agent validation"""
        context = {"task": {"id": 1}, "work_item": {"id": 1}, "project": {"id": 1}}
        
        result = await performance_optimizer._validate_agents_optimized(context)
        
        assert "valid" in result
        assert "agents_available" in result
        assert "validation_time" in result
        assert result["valid"] is True
        assert result["agents_available"] == 85
        assert result["validation_time"] < 0.03  # 30ms
    
    def test_get_performance_stats(self, performance_optimizer):
        """Test performance statistics"""
        # Add some test metrics
        performance_optimizer.performance_metrics = [
            PerformanceMetrics("test_op", 0.05, time.time(), True, {}),
            PerformanceMetrics("test_op", 0.03, time.time(), False, {}),
        ]
        
        stats = performance_optimizer.get_performance_stats()
        
        assert "total_operations" in stats
        assert "average_duration" in stats
        assert "min_duration" in stats
        assert "max_duration" in stats
        assert "cache_hit_rate" in stats
        assert "cache_stats" in stats
        assert "connection_pool_stats" in stats
        
        assert stats["total_operations"] == 2
        assert stats["average_duration"] == 0.04
        assert stats["min_duration"] == 0.03
        assert stats["max_duration"] == 0.05
        assert stats["cache_hit_rate"] == 0.5
    
    def test_clear_cache(self, performance_optimizer):
        """Test cache clearing"""
        # Add some data to cache
        performance_optimizer.cache.set("test_key", "test_value", CacheLevel.L1)
        assert performance_optimizer.cache.get("test_key") == "test_value"
        
        # Clear cache
        performance_optimizer.clear_cache()
        assert performance_optimizer.cache.get("test_key") is None
    
    def test_enable_disable_optimization(self, performance_optimizer):
        """Test enabling/disabling optimization"""
        assert performance_optimizer.optimization_enabled is True
        
        performance_optimizer.disable_optimization()
        assert performance_optimizer.optimization_enabled is False
        
        performance_optimizer.enable_optimization()
        assert performance_optimizer.optimization_enabled is True
    
    def test_close(self, performance_optimizer):
        """Test closing optimizer"""
        performance_optimizer.close()
        
        # Should close connection pool and clear cache
        assert len(performance_optimizer.connection_pool.available_connections) == 0
        assert len(performance_optimizer.connection_pool.used_connections) == 0
    
    def test_create_performance_optimizer_factory(self, temp_db):
        """Test performance optimizer factory function"""
        optimizer = create_performance_optimizer(temp_db)
        
        assert isinstance(optimizer, PerformanceOptimizer)
        assert optimizer.db_path == temp_db


class TestPerformanceDecorators:
    """Test suite for performance decorators"""
    
    @pytest.mark.asyncio
    async def test_cache_result_decorator(self):
        """Test cache result decorator"""
        from agentpm.core.performance.optimizer import cache_result
        
        call_count = 0
        
        @cache_result(ttl=60, level=CacheLevel.L1)
        async def expensive_operation(value):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"
        
        # First call should execute function
        result1 = await expensive_operation("test")
        assert result1 == "result_test"
        assert call_count == 1
        
        # Second call should use cache
        result2 = await expensive_operation("test")
        assert result2 == "result_test"
        assert call_count == 1  # Should not increment
        
        # Different parameter should execute function
        result3 = await expensive_operation("different")
        assert result3 == "result_different"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_measure_performance_decorator(self):
        """Test measure performance decorator"""
        from agentpm.core.performance.optimizer import measure_performance
        
        @measure_performance("test_operation")
        async def test_function():
            await asyncio.sleep(0.01)  # 10ms
            return "success"
        
        result = await test_function()
        
        assert result == "success"
        assert len(test_function._performance_metrics) == 1
        
        metric = test_function._performance_metrics[0]
        assert metric.operation == "test_operation"
        assert metric.duration >= 0.01
        assert metric.cache_hit is False
    
    @pytest.mark.asyncio
    async def test_measure_performance_decorator_error(self):
        """Test measure performance decorator with error"""
        from agentpm.core.performance.optimizer import measure_performance
        
        @measure_performance("test_operation")
        async def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await test_function()
        
        assert len(test_function._performance_metrics) == 1
        
        metric = test_function._performance_metrics[0]
        assert metric.operation == "test_operation_error"
        assert "error" in metric.details


# Integration tests
class TestAgentSystemIntegration:
    """Integration tests for the complete agent system"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for integration testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test database with required tables
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE work_items (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                phase TEXT,
                status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                created_at TEXT
            )
        """)
        
        # Insert test data
        conn.execute("INSERT INTO tasks (id, name, type, status) VALUES (1, 'Test Task', 'implementation', 'active')")
        conn.execute("INSERT INTO work_items (id, name, type, phase, status) VALUES (1, 'Test WI', 'feature', 'i1_implementation', 'active')")
        conn.execute("INSERT INTO projects (id, name, description, created_at) VALUES (1, 'Test Project', 'Test Description', '2025-01-01')")
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, temp_db):
        """Test complete workflow integration"""
        # Create all components
        db_service = Mock()
        performance_optimizer = PerformanceOptimizer(temp_db)
        quality_orchestrator = QualityOrchestrator(db_service)
        phase_orchestrator = PhaseOrchestrator(db_service, quality_orchestrator)
        workflow_orchestrator = WorkflowOrchestrator(db_service, performance_optimizer)
        
        # Create sample work item
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Integration Test Work Item"
        work_item.status = WorkItemStatus.ACTIVE
        work_item.phase = Phase.I1_IMPLEMENTATION
        
        # Test workflow coordination
        result = await workflow_orchestrator.coordinate_workflow(work_item)
        
        assert result["status"] == "success"
        assert "execution_time" in result
        assert result["execution_time"] < 0.1  # 100ms target
    
    @pytest.mark.asyncio
    async def test_performance_optimization_integration(self, temp_db):
        """Test performance optimization integration"""
        optimizer = PerformanceOptimizer(temp_db)
        
        # Test TaskStart optimization
        result = await optimizer.optimize_taskstart(1, 1, 1)
        
        assert result["status"] == "success"
        assert result["performance_target_met"] is True
        assert result["execution_time"] < 0.1  # 100ms target
        
        # Test performance stats
        stats = optimizer.get_performance_stats()
        assert "total_operations" in stats
        assert "average_duration" in stats
        assert "cache_hit_rate" in stats
    
    @pytest.mark.asyncio
    async def test_agent_consolidation_integration(self, temp_db):
        """Test agent consolidation integration"""
        # Test that the new simplified agents can handle the same functionality
        # as the original 85 agents
        
        db_service = Mock()
        quality_orchestrator = QualityOrchestrator(db_service)
        phase_orchestrator = PhaseOrchestrator(db_service, quality_orchestrator)
        
        # Test phase orchestration for all phases
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Test Work Item"
        
        for phase in Phase:
            result = await phase_orchestrator.orchestrate_phase(phase, work_item)
            assert result["status"] == "success"
            assert result["phase"] == phase.value
        
        # Test quality gate enforcement for all gate types
        for gate_type in QualityGateType:
            result = await quality_orchestrator.enforce_quality_gates(gate_type, work_item)
            assert result["status"] == "success"
            assert result["gate_type"] == gate_type.value


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
