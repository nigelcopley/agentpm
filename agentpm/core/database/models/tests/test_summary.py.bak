import pytest
from datetime import datetime
from pydantic import ValidationError

from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType


class TestSummaryModel:
    """Test the Summary Pydantic model."""
    
    def test_valid_summary_creation(self):
        """Test creating a valid summary."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Made significant progress on the feature implementation.",
            context_metadata={"decisions": ["Used React hooks"], "blockers": []},
            session_id=123,
            created_by="agent-1"
        )
        
        assert summary.entity_type == EntityType.WORK_ITEM
        assert summary.entity_id == 1
        assert summary.summary_type == SummaryType.WORK_ITEM_PROGRESS
        assert summary.summary_text == "Made significant progress on the feature implementation."
        assert summary.context_metadata == {"decisions": ["Used React hooks"], "blockers": []}
        assert summary.session_id == 123
        assert summary.created_by == "agent-1"
        assert summary.created_at is not None
        assert isinstance(summary.created_at, datetime)
    
    def test_minimal_summary_creation(self):
        """Test creating a summary with minimal required fields."""
        summary = Summary(
            entity_type=EntityType.PROJECT,
            entity_id=1,
            summary_type=SummaryType.PROJECT_MILESTONE,
            summary_text="Project milestone achieved successfully.",
            created_by="agent-1"
        )
        
        assert summary.entity_type == EntityType.PROJECT
        assert summary.entity_id == 1
        assert summary.summary_type == SummaryType.PROJECT_MILESTONE
        assert summary.summary_text == "Project milestone achieved successfully."
        assert summary.context_metadata is None
        assert summary.session_id is None
        assert summary.created_by == "agent-1"
        assert summary.created_at is not None
    
    def test_entity_id_validation(self):
        """Test entity_id validation (must be > 0)."""
        with pytest.raises(ValidationError) as exc_info:
            Summary(
                entity_type=EntityType.WORK_ITEM,
                entity_id=0,  # Invalid: must be > 0
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text="Test summary."
            )
        
        assert "entity_id" in str(exc_info.value)
    
    def test_summary_text_validation(self):
        """Test summary_text validation (must be at least 10 characters)."""
        with pytest.raises(ValidationError) as exc_info:
            Summary(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text="Short"  # Invalid: too short
            )
        
        assert "summary_text" in str(exc_info.value)
    
    def test_created_at_auto_set(self):
        """Test that created_at is automatically set if not provided."""
        before = datetime.now()
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with auto-created timestamp.",
            created_by="agent-1"
        )
        after = datetime.now()
        
        assert summary.created_at is not None
        assert before <= summary.created_at <= after
    
    def test_created_at_preserved(self):
        """Test that provided created_at is preserved."""
        custom_time = datetime(2024, 1, 15, 10, 30, 0)
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with custom timestamp.",
            created_at=custom_time,
            created_by="agent-1"
        )
        
        assert summary.created_at == custom_time
    
    def test_context_metadata_serialization(self):
        """Test that context_metadata can handle complex data structures."""
        complex_metadata = {
            "decisions": [
                {"decision": "Use React", "rationale": "Better performance"},
                {"decision": "Use TypeScript", "rationale": "Type safety"}
            ],
            "blockers": [
                {"blocker": "API not ready", "resolution": "Mock data for now"}
            ],
            "metrics": {
                "completion_percentage": 75.5,
                "estimated_hours": 8.0
            }
        }
        
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with complex metadata.",
            context_metadata=complex_metadata,
            created_by="agent-1"
        )
        
        assert summary.context_metadata == complex_metadata
    
    def test_all_entity_types(self):
        """Test that all entity types are supported."""
        entity_types = [EntityType.PROJECT, EntityType.WORK_ITEM, EntityType.TASK, EntityType.IDEA]
        
        for entity_type in entity_types:
            summary = Summary(
                entity_type=entity_type,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,  # Use a common type
                summary_text=f"Test summary for {entity_type.value}.",
                created_by="agent-1"
            )
            assert summary.entity_type == entity_type
    
    def test_all_summary_types(self):
        """Test that all summary types are supported."""
        summary_types = [
            SummaryType.PROJECT_MILESTONE,
            SummaryType.SESSION_HANDOVER,
            SummaryType.WORK_ITEM_PROGRESS,
            SummaryType.TASK_COMPLETION
        ]
        
        for summary_type in summary_types:
            summary = Summary(
                entity_type=EntityType.WORK_ITEM,  # Use a common entity type
                entity_id=1,
                summary_type=summary_type,
                summary_text=f"Test summary of type {summary_type.value}.",
                created_by="agent-1"
            )
            assert summary.summary_type == summary_type
    
    def test_model_dump(self):
        """Test that model_dump() works correctly."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary for model dump.",
            context_metadata={"test": "data"},
            session_id=123,
            created_by="agent-1"
        )
        
        data = summary.model_dump()
        
        assert data["entity_type"] == "work_item"
        assert data["entity_id"] == 1
        assert data["summary_type"] == "work_item_progress"
        assert data["summary_text"] == "Test summary for model dump."
        assert data["context_metadata"] == {"test": "data"}
        assert data["session_id"] == 123
        assert data["created_by"] == "agent-1"
        assert "created_at" in data
    
    def test_model_dump_exclude_unset(self):
        """Test that model_dump(exclude_unset=True) works correctly."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary for model dump exclude unset.",
            created_by="agent-1"
        )
        
        data = summary.model_dump(exclude_unset=True)
        
        # Should only include explicitly set fields
        assert "entity_type" in data
        assert "entity_id" in data
        assert "summary_type" in data
        assert "summary_text" in data
        assert "created_by" in data
        # created_at is auto-set but not explicitly set, so it's excluded
        assert "created_at" not in data
        assert "context_metadata" not in data  # Not set
        assert "session_id" not in data  # Not set
    
    def test_json_serialization(self):
        """Test that the model can be serialized to JSON."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary for JSON serialization.",
            context_metadata={"test": "data"},
            created_by="agent-1"
        )
        
        json_str = summary.model_dump_json()
        assert isinstance(json_str, str)
        assert "work_item" in json_str
        assert "work_item_progress" in json_str
        assert "Test summary for JSON serialization" in json_str
    
    def test_json_deserialization(self):
        """Test that the model can be deserialized from JSON."""
        json_data = {
            "entity_type": "work_item",
            "entity_id": 1,
            "summary_type": "work_item_progress",
            "summary_text": "Test summary for JSON deserialization.",
            "context_metadata": {"test": "data"},
            "created_by": "agent-1"
        }
        
        summary = Summary.model_validate(json_data)
        
        assert summary.entity_type == EntityType.WORK_ITEM
        assert summary.entity_id == 1
        assert summary.summary_type == SummaryType.WORK_ITEM_PROGRESS
        assert summary.summary_text == "Test summary for JSON deserialization."
        assert summary.context_metadata == {"test": "data"}
