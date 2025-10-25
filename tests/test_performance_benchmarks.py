"""
Performance Benchmark Tests

This module contains performance benchmark tests to validate that the agent system
improvements meet the target performance goals.

Target: TaskStart performance <100ms (current: 145ms)
"""

import pytest
import asyncio
import time
import tempfile
import sqlite3
import statistics
from pathlib import Path
from unittest.mock import Mock

from agentpm.core.performance.optimizer import PerformanceOptimizer, create_performance_optimizer
from agentpm.core.agents.simplified.workflow_orchestrator import WorkflowOrchestrator, create_workflow_orchestrator
from agentpm.core.agents.simplified.phase_orchestrator import PhaseOrchestrator, create_phase_orchestrator
from agentpm.core.agents.simplified.quality_orchestrator import QualityOrchestrator, create_quality_orchestrator
from agentpm.database.enums import WorkItemStatus, Phase


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for benchmarking"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test database with required tables
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                status TEXT,
                effort_hours REAL
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
        for i in range(100):  # Insert 100 records for realistic testing
            conn.execute(f"""
                INSERT INTO tasks (id, name, type, status, effort_hours) 
                VALUES ({i}, 'Task {i}', 'implementation', 'active', {i % 10 + 1})
            """)
            conn.execute(f"""
                INSERT INTO work_items (id, name, type, phase, status) 
                VALUES ({i}, 'Work Item {i}', 'feature', 'i1_implementation', 'active')
            """)
            conn.execute(f"""
                INSERT INTO projects (id, name, description, created_at) 
                VALUES ({i}, 'Project {i}', 'Description {i}', '2025-01-01')
            """)
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def performance_optimizer(self, temp_db):
        """Create performance optimizer for benchmarking"""
        return PerformanceOptimizer(temp_db)
    
    @pytest.mark.asyncio
    async def test_taskstart_performance_benchmark(self, performance_optimizer):
        """Benchmark TaskStart performance - target <100ms"""
        # Run multiple iterations to get reliable metrics
        iterations = 50
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            result = await performance_optimizer.optimize_taskstart(1, 1, 1)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            execution_times.append(execution_time)
            
            assert result["status"] == "success"
            assert result["performance_target_met"] is True
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        p95_time = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile
        p99_time = statistics.quantiles(execution_times, n=100)[98]  # 99th percentile
        
        print(f"\nTaskStart Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        print(f"  99th Percentile: {p99_time:.2f}ms")
        
        # Assertions for performance targets
        assert avg_time < 100, f"Average execution time {avg_time:.2f}ms exceeds 100ms target"
        assert p95_time < 100, f"95th percentile {p95_time:.2f}ms exceeds 100ms target"
        assert p99_time < 150, f"99th percentile {p99_time:.2f}ms exceeds 150ms limit"
        
        # Performance improvement assertion
        original_time = 145  # Original TaskStart time
        improvement = ((original_time - avg_time) / original_time) * 100
        print(f"  Performance Improvement: {improvement:.1f}%")
        assert improvement > 30, f"Performance improvement {improvement:.1f}% below 30% target"
    
    @pytest.mark.asyncio
    async def test_database_query_performance_benchmark(self, performance_optimizer):
        """Benchmark database query performance - target <40ms"""
        iterations = 100
        query_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Test individual database operations
            await performance_optimizer._load_task_optimized(1)
            await performance_optimizer._load_work_item_optimized(1)
            await performance_optimizer._load_project_optimized(1)
            
            query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            query_times.append(query_time)
        
        # Calculate statistics
        avg_time = statistics.mean(query_times)
        min_time = min(query_times)
        max_time = max(query_times)
        p95_time = statistics.quantiles(query_times, n=20)[18]
        
        print(f"\nDatabase Query Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        
        # Assertions for performance targets
        assert avg_time < 40, f"Average query time {avg_time:.2f}ms exceeds 40ms target"
        assert p95_time < 50, f"95th percentile {p95_time:.2f}ms exceeds 50ms limit"
    
    @pytest.mark.asyncio
    async def test_cache_performance_benchmark(self, performance_optimizer):
        """Benchmark cache performance - target >90% hit rate"""
        # Warm up cache
        await performance_optimizer.optimize_taskstart(1, 1, 1)
        
        # Test cache hit rate
        iterations = 1000
        cache_hits = 0
        
        start_time = time.time()
        
        for i in range(iterations):
            result = await performance_optimizer.optimize_taskstart(1, 1, 1)
            if result.get("cache_hits", 0) > 0:
                cache_hits += 1
        
        total_time = (time.time() - start_time) * 1000
        hit_rate = (cache_hits / iterations) * 100
        avg_time_per_request = total_time / iterations
        
        print(f"\nCache Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Cache Hits: {cache_hits}")
        print(f"  Hit Rate: {hit_rate:.2f}%")
        print(f"  Average Time per Request: {avg_time_per_request:.2f}ms")
        print(f"  Total Time: {total_time:.2f}ms")
        
        # Assertions for cache performance
        assert hit_rate > 90, f"Cache hit rate {hit_rate:.2f}% below 90% target"
        assert avg_time_per_request < 10, f"Average time per request {avg_time_per_request:.2f}ms exceeds 10ms limit"
    
    @pytest.mark.asyncio
    async def test_parallel_processing_benchmark(self, performance_optimizer):
        """Benchmark parallel processing performance"""
        # Test sequential vs parallel execution
        iterations = 50
        
        # Sequential execution
        sequential_times = []
        for i in range(iterations):
            start_time = time.time()
            
            task = await performance_optimizer._load_task_optimized(1)
            work_item = await performance_optimizer._load_work_item_optimized(1)
            project = await performance_optimizer._load_project_optimized(1)
            
            sequential_time = (time.time() - start_time) * 1000
            sequential_times.append(sequential_time)
        
        # Parallel execution
        parallel_times = []
        for i in range(iterations):
            start_time = time.time()
            
            task, work_item, project = await asyncio.gather(
                performance_optimizer._load_task_optimized(1),
                performance_optimizer._load_work_item_optimized(1),
                performance_optimizer._load_project_optimized(1)
            )
            
            parallel_time = (time.time() - start_time) * 1000
            parallel_times.append(parallel_time)
        
        # Calculate statistics
        avg_sequential = statistics.mean(sequential_times)
        avg_parallel = statistics.mean(parallel_times)
        improvement = ((avg_sequential - avg_parallel) / avg_sequential) * 100
        
        print(f"\nParallel Processing Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average Sequential: {avg_sequential:.2f}ms")
        print(f"  Average Parallel: {avg_parallel:.2f}ms")
        print(f"  Performance Improvement: {improvement:.1f}%")
        
        # Assertions for parallel processing
        assert improvement > 20, f"Parallel processing improvement {improvement:.1f}% below 20% target"
        assert avg_parallel < avg_sequential, "Parallel execution should be faster than sequential"
    
    @pytest.mark.asyncio
    async def test_memory_usage_benchmark(self, performance_optimizer):
        """Benchmark memory usage - target <500MB"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations to test memory usage
        for i in range(1000):
            await performance_optimizer.optimize_taskstart(1, 1, 1)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\nMemory Usage Benchmark Results:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Memory Increase: {memory_increase:.2f}MB")
        
        # Assertions for memory usage
        assert final_memory < 500, f"Final memory usage {final_memory:.2f}MB exceeds 500MB target"
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_benchmark(self, performance_optimizer):
        """Benchmark concurrent request handling"""
        # Test concurrent request handling
        concurrent_requests = 50
        
        start_time = time.time()
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_requests):
            task = performance_optimizer.optimize_taskstart(1, 1, 1)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        total_time = (time.time() - start_time) * 1000
        avg_time_per_request = total_time / concurrent_requests
        
        # Check all results
        successful_requests = sum(1 for result in results if result["status"] == "success")
        success_rate = (successful_requests / concurrent_requests) * 100
        
        print(f"\nConcurrent Requests Benchmark Results:")
        print(f"  Concurrent Requests: {concurrent_requests}")
        print(f"  Total Time: {total_time:.2f}ms")
        print(f"  Average Time per Request: {avg_time_per_request:.2f}ms")
        print(f"  Successful Requests: {successful_requests}")
        print(f"  Success Rate: {success_rate:.2f}%")
        
        # Assertions for concurrent handling
        assert success_rate > 95, f"Success rate {success_rate:.2f}% below 95% target"
        assert avg_time_per_request < 100, f"Average time per request {avg_time_per_request:.2f}ms exceeds 100ms limit"
    
    @pytest.mark.asyncio
    async def test_agent_validation_performance_benchmark(self, performance_optimizer):
        """Benchmark agent validation performance - target <15ms"""
        iterations = 100
        validation_times = []
        
        context = {"task": {"id": 1}, "work_item": {"id": 1}, "project": {"id": 1}}
        
        for i in range(iterations):
            start_time = time.time()
            
            result = await performance_optimizer._validate_agents_optimized(context)
            
            validation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            validation_times.append(validation_time)
            
            assert result["valid"] is True
        
        # Calculate statistics
        avg_time = statistics.mean(validation_times)
        min_time = min(validation_times)
        max_time = max(validation_times)
        p95_time = statistics.quantiles(validation_times, n=20)[18]
        
        print(f"\nAgent Validation Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        
        # Assertions for validation performance
        assert avg_time < 15, f"Average validation time {avg_time:.2f}ms exceeds 15ms target"
        assert p95_time < 20, f"95th percentile {p95_time:.2f}ms exceeds 20ms limit"
    
    @pytest.mark.asyncio
    async def test_context_assembly_performance_benchmark(self, performance_optimizer):
        """Benchmark context assembly performance - target <30ms"""
        iterations = 100
        assembly_times = []
        
        task = {"id": 1, "name": "Test Task", "type": "implementation", "status": "active", "effort_hours": 4.0}
        work_item = {"id": 1, "name": "Test WI", "type": "feature", "phase": "i1_implementation", "status": "active"}
        project = {"id": 1, "name": "Test Project", "description": "Test Description", "created_at": "2025-01-01"}
        
        for i in range(iterations):
            start_time = time.time()
            
            result = await performance_optimizer._assemble_context_parallel(task, work_item, project)
            
            assembly_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            assembly_times.append(assembly_time)
            
            assert "task" in result
            assert "work_item" in result
            assert "project" in result
        
        # Calculate statistics
        avg_time = statistics.mean(assembly_times)
        min_time = min(assembly_times)
        max_time = max(assembly_times)
        p95_time = statistics.quantiles(assembly_times, n=20)[18]
        
        print(f"\nContext Assembly Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        
        # Assertions for assembly performance
        assert avg_time < 30, f"Average assembly time {avg_time:.2f}ms exceeds 30ms target"
        assert p95_time < 40, f"95th percentile {p95_time:.2f}ms exceeds 40ms limit"
    
    def test_performance_optimizer_factory_benchmark(self, temp_db):
        """Benchmark performance optimizer factory creation"""
        iterations = 100
        creation_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            optimizer = create_performance_optimizer(temp_db)
            optimizer.close()
            
            creation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            creation_times.append(creation_time)
        
        # Calculate statistics
        avg_time = statistics.mean(creation_times)
        min_time = min(creation_times)
        max_time = max(creation_times)
        
        print(f"\nPerformance Optimizer Factory Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        
        # Assertions for factory performance
        assert avg_time < 50, f"Average creation time {avg_time:.2f}ms exceeds 50ms limit"
        assert max_time < 100, f"Maximum creation time {max_time:.2f}ms exceeds 100ms limit"


class TestAgentSystemPerformanceIntegration:
    """Integration performance tests for the complete agent system"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for integration benchmarking"""
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
        for i in range(50):
            conn.execute(f"""
                INSERT INTO tasks (id, name, type, status) 
                VALUES ({i}, 'Task {i}', 'implementation', 'active')
            """)
            conn.execute(f"""
                INSERT INTO work_items (id, name, type, phase, status) 
                VALUES ({i}, 'Work Item {i}', 'feature', 'i1_implementation', 'active')
            """)
            conn.execute(f"""
                INSERT INTO projects (id, name, description, created_at) 
                VALUES ({i}, 'Project {i}', 'Description {i}', '2025-01-01')
            """)
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_complete_system_performance_benchmark(self, temp_db):
        """Benchmark complete system performance"""
        # Create all components
        db_service = Mock()
        performance_optimizer = PerformanceOptimizer(temp_db)
        quality_orchestrator = QualityOrchestrator(db_service)
        phase_orchestrator = PhaseOrchestrator(db_service, quality_orchestrator)
        workflow_orchestrator = WorkflowOrchestrator(db_service, performance_optimizer)
        
        # Create sample work item
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Performance Test Work Item"
        work_item.status = WorkItemStatus.ACTIVE
        work_item.phase = Phase.I1_IMPLEMENTATION
        
        # Benchmark complete workflow
        iterations = 20
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Test complete workflow coordination
            result = await workflow_orchestrator.coordinate_workflow(work_item)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            execution_times.append(execution_time)
            
            assert result["status"] == "success"
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        p95_time = statistics.quantiles(execution_times, n=20)[18]
        
        print(f"\nComplete System Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        print(f"  95th Percentile: {p95_time:.2f}ms")
        
        # Assertions for complete system performance
        assert avg_time < 100, f"Average execution time {avg_time:.2f}ms exceeds 100ms target"
        assert p95_time < 150, f"95th percentile {p95_time:.2f}ms exceeds 150ms limit"
        
        # Cleanup
        performance_optimizer.close()
    
    @pytest.mark.asyncio
    async def test_agent_consolidation_performance_benchmark(self, temp_db):
        """Benchmark agent consolidation performance improvement"""
        # Test that the new simplified agents perform better than the original system
        
        db_service = Mock()
        quality_orchestrator = QualityOrchestrator(db_service)
        phase_orchestrator = PhaseOrchestrator(db_service, quality_orchestrator)
        
        work_item = Mock()
        work_item.id = 1
        work_item.name = "Test Work Item"
        
        # Benchmark phase orchestration for all phases
        iterations = 10
        total_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Test all phases
            for phase in Phase:
                result = await phase_orchestrator.orchestrate_phase(phase, work_item)
                assert result["status"] == "success"
            
            total_time = (time.time() - start_time) * 1000
            total_times.append(total_time)
        
        # Calculate statistics
        avg_time = statistics.mean(total_times)
        min_time = min(total_times)
        max_time = max(total_times)
        
        print(f"\nAgent Consolidation Performance Benchmark Results:")
        print(f"  Iterations: {iterations}")
        print(f"  Phases per Iteration: {len(Phase)}")
        print(f"  Average Total Time: {avg_time:.2f}ms")
        print(f"  Average per Phase: {avg_time / len(Phase):.2f}ms")
        print(f"  Minimum: {min_time:.2f}ms")
        print(f"  Maximum: {max_time:.2f}ms")
        
        # Assertions for consolidation performance
        avg_per_phase = avg_time / len(Phase)
        assert avg_per_phase < 20, f"Average time per phase {avg_per_phase:.2f}ms exceeds 20ms limit"
        assert max_time < 200, f"Maximum total time {max_time:.2f}ms exceeds 200ms limit"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
