"""
Test CRUD operations for tasks and work items.

Tests the new delete operations and enhanced list functionality.
"""

import pytest
import tempfile
import os
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.adapters import TaskAdapter, WorkItemAdapter, ProjectAdapter
from agentpm.core.database.models import Task, WorkItem, Project
from agentpm.core.database.enums import TaskType, TaskStatus, WorkItemType, WorkItemStatus


class TestCRUDOperations:
    """Test CRUD operations for tasks and work items."""

    @pytest.fixture
    def db_service(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create database service
        service = DatabaseService(db_path)
        service._initialize_schema()
        
        yield service
        
        # Cleanup
        os.unlink(db_path)

    @pytest.fixture
    def test_project(self, db_service):
        """Create a test project."""
        project = Project(
            name="Test Project",
            description="Test project for CRUD operations",
            path="/tmp/test_project"
        )
        return ProjectAdapter.create(db_service, project)

    @pytest.fixture
    def test_work_item(self, db_service, test_project):
        """Create a test work item."""
        work_item = WorkItem(
            project_id=test_project.id,
            name="Test Work Item",
            description="Test work item for CRUD operations",
            type=WorkItemType.FEATURE,
            priority=3
        )
        return WorkItemAdapter.create(db_service, work_item)

    @pytest.fixture
    def test_task(self, db_service, test_work_item):
        """Create a test task."""
        task = Task(
            work_item_id=test_work_item.id,
            name="Test Task",
            description="Test task for CRUD operations",
            type=TaskType.IMPLEMENTATION,
            effort_hours=3.0,
            priority=3
        )
        return TaskAdapter.create(db_service, task)

    def test_task_delete_operation(self, db_service, test_task):
        """Test task delete operation."""
        task_id = test_task.id
        
        # Verify task exists
        retrieved_task = TaskAdapter.get(db_service, task_id)
        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        
        # Delete task
        success = TaskAdapter.delete(db_service, task_id)
        assert success is True
        
        # Verify task is deleted
        deleted_task = TaskAdapter.get(db_service, task_id)
        assert deleted_task is None

    def test_task_delete_nonexistent(self, db_service):
        """Test deleting a non-existent task."""
        success = TaskAdapter.delete(db_service, 99999)
        assert success is False

    def test_work_item_delete_operation(self, db_service, test_work_item, test_task):
        """Test work item delete operation (should cascade to tasks)."""
        work_item_id = test_work_item.id
        task_id = test_task.id
        
        # Verify work item and task exist
        retrieved_wi = WorkItemAdapter.get(db_service, work_item_id)
        retrieved_task = TaskAdapter.get(db_service, task_id)
        assert retrieved_wi is not None
        assert retrieved_task is not None
        
        # Delete work item (should cascade to task)
        success = WorkItemAdapter.delete(db_service, work_item_id)
        assert success is True
        
        # Verify work item is deleted
        deleted_wi = WorkItemAdapter.get(db_service, work_item_id)
        assert deleted_wi is None
        
        # Verify task is also deleted (cascade)
        deleted_task = TaskAdapter.get(db_service, task_id)
        assert deleted_task is None

    def test_work_item_delete_nonexistent(self, db_service):
        """Test deleting a non-existent work item."""
        success = WorkItemAdapter.delete(db_service, 99999)
        assert success is False

    def test_task_list_with_filters(self, db_service, test_work_item):
        """Test task list with various filters."""
        # Create multiple tasks with different properties
        task1 = Task(
            work_item_id=test_work_item.id,
            name="Implementation Task",
            type=TaskType.IMPLEMENTATION,
            status=TaskStatus.ACTIVE,
            priority=1
        )
        task2 = Task(
            work_item_id=test_work_item.id,
            name="Testing Task",
            type=TaskType.TESTING,
            status=TaskStatus.DRAFT,
            priority=2
        )
        task3 = Task(
            work_item_id=test_work_item.id,
            name="Design Task",
            type=TaskType.DESIGN,
            status=TaskStatus.ACTIVE,
            priority=1
        )
        
        TaskAdapter.create(db_service, task1)
        TaskAdapter.create(db_service, task2)
        TaskAdapter.create(db_service, task3)
        
        # Test filtering by work item
        tasks = TaskAdapter.list(db_service, work_item_id=test_work_item.id)
        assert len(tasks) == 3
        
        # Test filtering by status (should be done in CLI, but test the adapter method)
        all_tasks = TaskAdapter.list(db_service, work_item_id=test_work_item.id)
        active_tasks = [t for t in all_tasks if t.status == TaskStatus.ACTIVE]
        assert len(active_tasks) == 2
        
        # Test filtering by type
        implementation_tasks = [t for t in all_tasks if t.type == TaskType.IMPLEMENTATION]
        assert len(implementation_tasks) == 1
        assert implementation_tasks[0].name == "Implementation Task"

    def test_work_item_list_with_filters(self, db_service, test_project):
        """Test work item list with various filters."""
        # Create multiple work items with different properties
        wi1 = WorkItem(
            project_id=test_project.id,
            name="Feature Work Item",
            type=WorkItemType.FEATURE,
            status=WorkItemStatus.ACTIVE,
            priority=1
        )
        wi2 = WorkItem(
            project_id=test_project.id,
            name="Bugfix Work Item",
            type=WorkItemType.BUGFIX,
            status=WorkItemStatus.DRAFT,
            priority=2
        )
        wi3 = WorkItem(
            project_id=test_project.id,
            name="Research Work Item",
            type=WorkItemType.RESEARCH,
            status=WorkItemStatus.ACTIVE,
            priority=1
        )
        
        WorkItemAdapter.create(db_service, wi1)
        WorkItemAdapter.create(db_service, wi2)
        WorkItemAdapter.create(db_service, wi3)
        
        # Test filtering by project
        work_items = WorkItemAdapter.list(db_service, project_id=test_project.id)
        assert len(work_items) == 3
        
        # Test filtering by status (should be done in CLI, but test the adapter method)
        all_work_items = WorkItemAdapter.list(db_service, project_id=test_project.id)
        active_work_items = [wi for wi in all_work_items if wi.status == WorkItemStatus.ACTIVE]
        assert len(active_work_items) == 2
        
        # Test filtering by type
        feature_work_items = [wi for wi in all_work_items if wi.type == WorkItemType.FEATURE]
        assert len(feature_work_items) == 1
        assert feature_work_items[0].name == "Feature Work Item"

    def test_bulk_operations_simulation(self, db_service, test_work_item):
        """Test bulk operations by simulating the logic."""
        # Create multiple tasks
        tasks = []
        for i in range(5):
            task = Task(
                work_item_id=test_work_item.id,
                name=f"Bulk Task {i+1}",
                type=TaskType.IMPLEMENTATION,
                status=TaskStatus.DRAFT,
                priority=3
            )
            created_task = TaskAdapter.create(db_service, task)
            tasks.append(created_task)
        
        # Verify all tasks exist
        all_tasks = TaskAdapter.list(db_service, work_item_id=test_work_item.id)
        assert len(all_tasks) == 5
        
        # Simulate bulk update (update all to active)
        updated_count = 0
        for task in all_tasks:
            try:
                TaskAdapter.update(db_service, task.id, status=TaskStatus.ACTIVE)
                updated_count += 1
            except Exception:
                pass
        
        assert updated_count == 5
        
        # Verify all tasks are now active
        updated_tasks = TaskAdapter.list(db_service, work_item_id=test_work_item.id)
        for task in updated_tasks:
            assert task.status == TaskStatus.ACTIVE
        
        # Simulate bulk delete (delete all tasks)
        deleted_count = 0
        for task in updated_tasks:
            try:
                success = TaskAdapter.delete(db_service, task.id)
                if success:
                    deleted_count += 1
            except Exception:
                pass
        
        assert deleted_count == 5
        
        # Verify all tasks are deleted
        remaining_tasks = TaskAdapter.list(db_service, work_item_id=test_work_item.id)
        assert len(remaining_tasks) == 0
