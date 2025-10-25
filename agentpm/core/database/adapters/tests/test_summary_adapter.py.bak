import pytest
import json
from datetime import datetime

from agentpm.core.database.models import Summary
from agentpm.core.database.enums import EntityType, SummaryType
from agentpm.core.database.adapters import SummaryAdapter


class TestSummaryAdapter:
    """Test the SummaryAdapter for database conversion."""
    
    def test_to_db_basic(self):
        """Test converting a basic summary to database format."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary for database conversion.",
            created_by="agent-1"
        )
        
        db_dict = SummaryAdapter.to_db(summary)
        
        assert db_dict["entity_type"] == "work_item"
        assert db_dict["entity_id"] == 1
        assert db_dict["summary_type"] == "work_item_progress"
        assert db_dict["summary_text"] == "Test summary for database conversion."
        assert db_dict["created_by"] == "agent-1"
        assert "created_at" in db_dict
        assert isinstance(db_dict["created_at"], str)
    
    def test_to_db_with_metadata(self):
        """Test converting a summary with context_metadata to database format."""
        metadata = {
            "decisions": ["Use React", "Use TypeScript"],
            "blockers": [{"blocker": "API not ready", "resolution": "Mock data"}],
            "metrics": {"completion": 75.5}
        }
        
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with metadata.",
            context_metadata=metadata,
            created_by="agent-1"
        )
        
        db_dict = SummaryAdapter.to_db(summary)
        
        assert db_dict["context_metadata"] is not None
        assert isinstance(db_dict["context_metadata"], str)
        
        # Verify it's valid JSON
        parsed_metadata = json.loads(db_dict["context_metadata"])
        assert parsed_metadata == metadata
    
    def test_to_db_empty_metadata(self):
        """Test converting a summary with empty context_metadata to database format."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with empty metadata.",
            context_metadata={},
            created_by="agent-1"
        )
        
        db_dict = SummaryAdapter.to_db(summary)
        
        # Empty dict should be converted to None for database
        assert db_dict["context_metadata"] is None
    
    def test_to_db_none_metadata(self):
        """Test converting a summary with None context_metadata to database format."""
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with None metadata.",
            created_by="agent-1"
        )
        
        db_dict = SummaryAdapter.to_db(summary)
        
        assert db_dict["context_metadata"] is None
    
    def test_to_db_custom_timestamp(self):
        """Test converting a summary with custom timestamp to database format."""
        custom_time = datetime(2024, 1, 15, 10, 30, 0)
        summary = Summary(
            entity_type=EntityType.WORK_ITEM,
            entity_id=1,
            summary_type=SummaryType.WORK_ITEM_PROGRESS,
            summary_text="Test summary with custom timestamp.",
            created_at=custom_time,
            created_by="agent-1"
        )
        
        db_dict = SummaryAdapter.to_db(summary)
        
        assert db_dict["created_at"] == "2024-01-15T10:30:00"
    
    def test_from_db_basic(self):
        """Test converting a basic database row to Summary model."""
        db_row = {
            "id": 1,
            "entity_type": "work_item",
            "entity_id": 1,
            "summary_type": "work_item_progress",
            "summary_text": "Test summary from database.",
            "context_metadata": None,
            "session_id": None,
            "created_at": "2024-01-15T10:30:00",
            "created_by": "agent-1"
        }
        
        summary = SummaryAdapter.from_row(db_row)
        
        assert summary.id == 1
        assert summary.entity_type == EntityType.WORK_ITEM
        assert summary.entity_id == 1
        assert summary.summary_type == SummaryType.WORK_ITEM_PROGRESS
        assert summary.summary_text == "Test summary from database."
        assert summary.context_metadata is None
        assert summary.session_id is None
        assert summary.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert summary.created_by == "agent-1"
    
    def test_from_db_with_metadata(self):
        """Test converting a database row with context_metadata to Summary model."""
        metadata = {
            "decisions": ["Use React", "Use TypeScript"],
            "blockers": [{"blocker": "API not ready", "resolution": "Mock data"}]
        }
        
        db_row = {
            "id": 1,
            "entity_type": "project",
            "entity_id": 1,
            "summary_type": "project_milestone",
            "summary_text": "Test summary with metadata from database.",
            "context_metadata": json.dumps(metadata),
            "session_id": 123,
            "created_at": "2024-01-15T10:30:00",
            "created_by": "agent-1"
        }
        
        summary = SummaryAdapter.from_row(db_row)
        
        assert summary.id == 1
        assert summary.entity_type == EntityType.PROJECT
        assert summary.entity_id == 1
        assert summary.summary_type == SummaryType.PROJECT_MILESTONE
        assert summary.summary_text == "Test summary with metadata from database."
        assert summary.context_metadata == metadata
        assert summary.session_id == 123
        assert summary.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert summary.created_by == "agent-1"
    
    def test_from_db_invalid_json_metadata(self):
        """Test converting a database row with invalid JSON metadata."""
        db_row = {
            "id": 1,
            "entity_type": "work_item",
            "entity_id": 1,
            "summary_type": "work_item_progress",
            "summary_text": "Test summary with invalid JSON metadata.",
            "context_metadata": "invalid json {",
            "session_id": None,
            "created_at": "2024-01-15T10:30:00",
            "created_by": "agent-1"
        }
        
        # Should gracefully handle invalid JSON by setting metadata to None
        summary = SummaryAdapter.from_row(db_row)
        assert summary.context_metadata is None
    
    def test_round_trip_conversion(self):
        """Test that to_db and from_db are inverse operations."""
        original_summary = Summary(
            entity_type=EntityType.TASK,
            entity_id=1,
            summary_type=SummaryType.TASK_COMPLETION,
            summary_text="Test summary for round trip conversion.",
            context_metadata={
                "decisions": ["Use async/await"],
                "blockers": [],
                "metrics": {"completion": 100.0}
            },
            session_id=456,
            created_by="agent-2"
        )
        
        # Convert to database format
        db_dict = SummaryAdapter.to_db(original_summary)
        
        # Convert back to model
        restored_summary = SummaryAdapter.from_row(db_dict)
        
        # Should be equivalent (ignoring id and created_at auto-setting)
        assert restored_summary.entity_type == original_summary.entity_type
        assert restored_summary.entity_id == original_summary.entity_id
        assert restored_summary.summary_type == original_summary.summary_type
        assert restored_summary.summary_text == original_summary.summary_text
        assert restored_summary.context_metadata == original_summary.context_metadata
        assert restored_summary.session_id == original_summary.session_id
        assert restored_summary.created_by == original_summary.created_by
    
    def test_all_entity_types_conversion(self):
        """Test conversion for all entity types."""
        entity_types = [
            (EntityType.PROJECT, "project"),
            (EntityType.WORK_ITEM, "work_item"),
            (EntityType.TASK, "task"),
            (EntityType.IDEA, "idea")
        ]
        
        for entity_type, db_value in entity_types:
            summary = Summary(
                entity_type=entity_type,
                entity_id=1,
                summary_type=SummaryType.WORK_ITEM_PROGRESS,
                summary_text=f"Test summary for {entity_type.value}.",
                created_by="agent-1"
            )
            
            db_dict = SummaryAdapter.to_db(summary)
            assert db_dict["entity_type"] == db_value
            
            restored_summary = SummaryAdapter.from_row(db_dict)
            assert restored_summary.entity_type == entity_type
    
    def test_all_summary_types_conversion(self):
        """Test conversion for all summary types."""
        summary_types = [
            (SummaryType.PROJECT_MILESTONE, "project_milestone"),
            (SummaryType.SESSION_HANDOVER, "session_handover"),
            (SummaryType.WORK_ITEM_PROGRESS, "work_item_progress"),
            (SummaryType.TASK_COMPLETION, "task_completion")
        ]
        
        for summary_type, db_value in summary_types:
            summary = Summary(
                entity_type=EntityType.WORK_ITEM,
                entity_id=1,
                summary_type=summary_type,
                summary_text=f"Test summary of type {summary_type.value}.",
                created_by="agent-1"
            )
            
            db_dict = SummaryAdapter.to_db(summary)
            assert db_dict["summary_type"] == db_value
            
            restored_summary = SummaryAdapter.from_row(db_dict)
            assert restored_summary.summary_type == summary_type
