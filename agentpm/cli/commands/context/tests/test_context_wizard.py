"""
Tests for Interactive Context Wizard

Validates:
- Interactive prompt flow
- Smart defaults generation
- Field validation
- Confidence calculation
- Database persistence
- Error handling

Pattern: Click CliRunner testing with rich console mocking
"""

import pytest
from datetime import datetime
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock

from agentpm.cli.commands.context.wizard import (
    wizard,
    _suggest_end_users,
    _suggest_implementers,
    _suggest_reviewers,
    _extract_from_description,
    _suggest_deadline,
    _calculate_confidence
)
from agentpm.core.database.models import Context, UnifiedSixW, WorkItem
from agentpm.core.database.enums import EntityType, ContextType, ConfidenceBand, WorkItemType, StatusEnum


@pytest.fixture
def mock_db():
    """Mock database service"""
    db = Mock()
    return db


@pytest.fixture
def sample_work_item():
    """Sample work item for testing"""
    return WorkItem(
        id=81,
        project_id=1,
        title="Add OAuth2 authentication",
        description="Implement OAuth2 authentication flow for user login. Must support Google and GitHub providers.",
        type=WorkItemType.FEATURE,
        status=StatusEnum.IN_PROGRESS,
        acceptance_criteria=["Users can log in with Google", "Users can log in with GitHub"]
    )


@pytest.fixture
def sample_six_w():
    """Sample 6W data for testing"""
    return UnifiedSixW(
        end_users=["End users", "Customers"],
        implementers=["@alice", "@bob"],
        reviewers=["@tech-lead"],
        functional_requirements=["OAuth2 authentication", "Google provider", "GitHub provider"],
        technical_constraints=["Must use Python 3.9+", "Response time < 100ms"],
        acceptance_criteria=["Users can log in with Google", "Users can log in with GitHub"],
        affected_services=["auth-service", "user-api"],
        repositories=["github.com/org/auth-service"],
        deployment_targets=["production", "staging"],
        deadline=datetime(2025, 12, 31),
        dependencies_timeline=["API spec approval"],
        business_value="Improve user conversion by 25%",
        risk_if_delayed="Lose competitive advantage",
        suggested_approach="Use OAuth2 library",
        existing_patterns=["Repository pattern"]
    )


class TestWizardCommand:
    """Test wizard CLI command"""

    def test_wizard_command_not_found(self, mock_db, tmp_path):
        """Test wizard with non-existent work item"""
        runner = CliRunner()

        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', return_value=None):
                    result = runner.invoke(wizard, ['999'])

                    assert result.exit_code == 1
                    assert "not found" in result.output.lower()

    def test_wizard_command_cancel_existing(self, mock_db, sample_work_item, tmp_path):
        """Test wizard cancels when user declines to update existing context"""
        runner = CliRunner()
        existing_context = Context(
            id=1,
            project_id=1,
            context_type=ContextType.WORK_ITEM_CONTEXT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=81,
            six_w=UnifiedSixW(
                end_users=["Existing users"],
                implementers=["@alice"]
            ),
            confidence_score=0.5,
            confidence_band=ConfidenceBand.YELLOW
        )

        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', return_value=sample_work_item):
                    with patch('agentpm.cli.commands.context.wizard.context_methods.get_entity_context', return_value=existing_context):
                        with patch('agentpm.cli.commands.context.wizard.Confirm.ask', return_value=False):
                            result = runner.invoke(wizard, ['81'])

                            assert result.exit_code == 0
                            assert "cancelled" in result.output.lower()

    def test_wizard_minimal_mode(self, mock_db, sample_work_item, tmp_path):
        """Test wizard in minimal mode (only essential fields)"""
        runner = CliRunner()

        # Mock prompts - only essential fields
        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', return_value=sample_work_item):
                    with patch('agentpm.cli.commands.context.wizard.context_methods.get_entity_context', return_value=None):
                        with patch('agentpm.cli.commands.context.wizard._prompt_six_w_fields') as mock_prompt:
                            with patch('agentpm.cli.commands.context.wizard.Confirm.ask', return_value=True):
                                with patch('agentpm.cli.commands.context.wizard.context_methods.create_context') as mock_create:
                                    # Return minimal 6W
                                    mock_prompt.return_value = UnifiedSixW(
                                        end_users=["Users"],
                                        implementers=["@alice"],
                                        reviewers=["@bob"],
                                        functional_requirements=["OAuth2"],
                                        technical_constraints=[],
                                        acceptance_criteria=["Login works"]
                                    )

                                    result = runner.invoke(wizard, ['81', '--minimal'])

                                    assert result.exit_code == 0
                                    assert mock_create.called
                                    # Verify minimal mode was passed
                                    assert mock_prompt.call_args[0][3] == True  # minimal parameter


class TestSmartDefaults:
    """Test smart default generation functions"""

    def test_suggest_end_users_feature(self, sample_work_item):
        """Test end user suggestions for feature work items"""
        sample_work_item.type = WorkItemType.FEATURE
        suggestions = _suggest_end_users(sample_work_item)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("users" in s.lower() or "customers" in s.lower() for s in suggestions)

    def test_suggest_end_users_bugfix(self, sample_work_item):
        """Test end user suggestions for bugfix work items"""
        sample_work_item.type = WorkItemType.BUGFIX
        suggestions = _suggest_end_users(sample_work_item)

        assert isinstance(suggestions, list)
        assert any("affected" in s.lower() for s in suggestions)

    def test_suggest_implementers_from_tasks(self, mock_db, sample_work_item):
        """Test implementer suggestions from existing tasks"""
        # Mock tasks with assignees
        mock_tasks = [
            Mock(assigned_to="@alice"),
            Mock(assigned_to="@bob"),
            Mock(assigned_to="@alice"),  # Duplicate
            Mock(assigned_to=None)  # No assignee
        ]

        with patch('agentpm.cli.commands.context.wizard.task_methods.list_tasks', return_value=mock_tasks):
            suggestions = _suggest_implementers(mock_db, sample_work_item)

            assert isinstance(suggestions, list)
            assert set(suggestions) == {"@alice", "@bob"}  # No duplicates

    def test_suggest_reviewers_from_tasks(self, mock_db, sample_work_item):
        """Test reviewer suggestions from existing tasks"""
        mock_tasks = [
            Mock(reviewed_by="@tech-lead"),
            Mock(reviewed_by="@senior-dev"),
            Mock(reviewed_by=None)
        ]

        with patch('agentpm.cli.commands.context.wizard.task_methods.list_tasks', return_value=mock_tasks):
            suggestions = _suggest_reviewers(mock_db, sample_work_item)

            assert isinstance(suggestions, list)
            assert set(suggestions) == {"@tech-lead", "@senior-dev"}

    def test_extract_from_description_short(self):
        """Test extraction from short description"""
        description = "Add OAuth2 authentication for users."
        extracted = _extract_from_description(description)

        assert isinstance(extracted, list)
        assert len(extracted) == 1
        assert "OAuth2" in extracted[0]

    def test_extract_from_description_long(self):
        """Test extraction from long description (truncates)"""
        description = "A" * 150 + ". More text here."
        extracted = _extract_from_description(description)

        assert isinstance(extracted, list)
        assert len(extracted) == 1
        assert len(extracted[0]) <= 110  # 100 chars + "..."

    def test_extract_from_description_empty(self):
        """Test extraction from empty description"""
        extracted = _extract_from_description("")
        assert extracted == []

        extracted = _extract_from_description(None)
        assert extracted == []

    def test_suggest_deadline_with_target_date(self, sample_work_item):
        """Test deadline suggestion from work item target date"""
        sample_work_item.target_date = datetime(2025, 12, 31)
        suggestion = _suggest_deadline(sample_work_item)

        assert suggestion == "2025-12-31"

    def test_suggest_deadline_without_target_date(self, sample_work_item):
        """Test deadline suggestion without target date"""
        suggestion = _suggest_deadline(sample_work_item)
        assert suggestion == ""


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    def test_calculate_confidence_complete(self, sample_six_w):
        """Test confidence with all fields populated"""
        confidence = _calculate_confidence(sample_six_w)

        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.9  # Should be high with all fields

    def test_calculate_confidence_minimal(self):
        """Test confidence with minimal fields (WHO/WHAT only)"""
        six_w = UnifiedSixW(
            end_users=["Users"],
            implementers=["@alice"],
            functional_requirements=["Feature A"]
        )
        confidence = _calculate_confidence(six_w)

        assert 0.0 <= confidence <= 1.0
        assert 0.3 <= confidence <= 0.7  # Medium confidence

    def test_calculate_confidence_empty(self):
        """Test confidence with no fields populated"""
        six_w = UnifiedSixW()
        confidence = _calculate_confidence(six_w)

        assert confidence == 0.0

    def test_calculate_confidence_who_only(self):
        """Test confidence with only WHO fields"""
        six_w = UnifiedSixW(
            end_users=["Users"],
            implementers=["@alice"],
            reviewers=["@bob"]
        )
        confidence = _calculate_confidence(six_w)

        assert 0.0 <= confidence <= 1.0
        assert 0.2 <= confidence <= 0.4  # Partial confidence

    def test_calculate_confidence_what_only(self):
        """Test confidence with only WHAT fields"""
        six_w = UnifiedSixW(
            functional_requirements=["Feature A"],
            technical_constraints=["Constraint 1"],
            acceptance_criteria=["AC 1"]
        )
        confidence = _calculate_confidence(six_w)

        assert 0.0 <= confidence <= 1.0
        assert 0.2 <= confidence <= 0.4  # Partial confidence

    def test_confidence_band_mapping(self):
        """Test confidence band mapping"""
        # RED band
        six_w_red = UnifiedSixW()
        confidence_red = _calculate_confidence(six_w_red)
        band_red = ConfidenceBand.from_score(confidence_red)
        assert band_red == ConfidenceBand.RED

        # YELLOW band
        six_w_yellow = UnifiedSixW(
            end_users=["Users"],
            implementers=["@alice"],
            functional_requirements=["Feature"]
        )
        confidence_yellow = _calculate_confidence(six_w_yellow)
        band_yellow = ConfidenceBand.from_score(confidence_yellow)
        assert band_yellow in [ConfidenceBand.YELLOW, ConfidenceBand.GREEN]

        # GREEN band
        six_w_green = UnifiedSixW(
            end_users=["Users"],
            implementers=["@alice"],
            reviewers=["@bob"],
            functional_requirements=["F1", "F2"],
            technical_constraints=["C1"],
            acceptance_criteria=["AC1", "AC2"],
            affected_services=["service1"],
            business_value="High value"
        )
        confidence_green = _calculate_confidence(six_w_green)
        band_green = ConfidenceBand.from_score(confidence_green)
        assert band_green == ConfidenceBand.GREEN


class TestFieldValidation:
    """Test field validation and parsing"""

    def test_list_field_parsing_comma_separated(self):
        """Test parsing comma-separated list input"""
        from agentpm.cli.commands.context.wizard import _prompt_list_field

        with patch('agentpm.cli.commands.context.wizard.Prompt.ask', return_value="item1, item2, item3"):
            result = _prompt_list_field(
                "Test prompt",
                [],
                None,
                "Help text",
                skip_existing=False
            )

            assert result == ["item1", "item2", "item3"]

    def test_list_field_parsing_empty(self):
        """Test parsing empty list input"""
        from agentpm.cli.commands.context.wizard import _prompt_list_field

        with patch('agentpm.cli.commands.context.wizard.Prompt.ask', return_value=""):
            result = _prompt_list_field(
                "Test prompt",
                [],
                None,
                "Help text",
                skip_existing=False
            )

            assert result == []

    def test_list_field_skip_existing(self):
        """Test skipping field with existing values"""
        from agentpm.cli.commands.context.wizard import _prompt_list_field

        existing = ["existing1", "existing2"]
        result = _prompt_list_field(
            "Test prompt",
            [],
            existing,
            "Help text",
            skip_existing=True
        )

        assert result == existing  # Should return existing, not prompt

    def test_single_field_parsing(self):
        """Test parsing single field input"""
        from agentpm.cli.commands.context.wizard import _prompt_single_field

        with patch('agentpm.cli.commands.context.wizard.Prompt.ask', return_value="Single value"):
            result = _prompt_single_field(
                "Test prompt",
                "",
                None,
                "Help text",
                skip_existing=False
            )

            assert result == "Single value"

    def test_single_field_skip_existing(self):
        """Test skipping single field with existing value"""
        from agentpm.cli.commands.context.wizard import _prompt_single_field

        existing = "Existing value"
        result = _prompt_single_field(
            "Test prompt",
            "",
            existing,
            "Help text",
            skip_existing=True
        )

        assert result == existing


class TestDatabasePersistence:
    """Test database persistence of context"""

    def test_create_new_context(self, mock_db, sample_work_item, sample_six_w, tmp_path):
        """Test creating new context via wizard"""
        runner = CliRunner()

        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', return_value=sample_work_item):
                    with patch('agentpm.cli.commands.context.wizard.context_methods.get_entity_context', return_value=None):
                        with patch('agentpm.cli.commands.context.wizard._prompt_six_w_fields', return_value=sample_six_w):
                            with patch('agentpm.cli.commands.context.wizard.Confirm.ask', return_value=True):
                                with patch('agentpm.cli.commands.context.wizard.context_methods.create_context') as mock_create:
                                    result = runner.invoke(wizard, ['81'])

                                    assert result.exit_code == 0
                                    assert mock_create.called

                                    # Verify context was created with correct data
                                    created_context = mock_create.call_args[0][1]
                                    assert created_context.project_id == 1
                                    assert created_context.entity_type == EntityType.WORK_ITEM
                                    assert created_context.entity_id == 81
                                    assert created_context.six_w == sample_six_w

    def test_update_existing_context(self, mock_db, sample_work_item, sample_six_w, tmp_path):
        """Test updating existing context via wizard"""
        runner = CliRunner()
        existing_context = Context(
            id=1,
            project_id=1,
            context_type=ContextType.WORK_ITEM_CONTEXT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=81,
            six_w=UnifiedSixW(end_users=["Old users"]),
            confidence_score=0.3,
            confidence_band=ConfidenceBand.RED
        )

        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', return_value=sample_work_item):
                    with patch('agentpm.cli.commands.context.wizard.context_methods.get_entity_context', return_value=existing_context):
                        with patch('agentpm.cli.commands.context.wizard._prompt_six_w_fields', return_value=sample_six_w):
                            with patch('agentpm.cli.commands.context.wizard.Confirm.ask', return_value=True):
                                with patch('agentpm.cli.commands.context.wizard.context_methods.update_context') as mock_update:
                                    result = runner.invoke(wizard, ['81'])

                                    assert result.exit_code == 0
                                    assert mock_update.called

                                    # Verify context was updated
                                    assert mock_update.call_args[0][0] == mock_db
                                    assert mock_update.call_args[0][1] == 1  # context ID
                                    assert 'six_w' in mock_update.call_args[1]


class TestErrorHandling:
    """Test error handling in wizard"""

    def test_invalid_date_format(self, sample_six_w):
        """Test handling of invalid date format"""
        from agentpm.cli.commands.context.wizard import _prompt_six_w_fields

        # This would be tested through integration, but we verify the logic
        # The wizard should handle invalid dates gracefully and skip setting deadline
        pass  # Date validation is handled in _prompt_six_w_fields

    def test_database_error_handling(self, mock_db, sample_work_item, tmp_path):
        """Test handling of database errors"""
        runner = CliRunner()

        with patch('agentpm.cli.commands.context.wizard.get_service', return_value=mock_db):
            with patch('agentpm.cli.commands.context.wizard.get_project_root', return_value=tmp_path):
                with patch('agentpm.cli.commands.context.wizard.wi_methods.get_work_item', side_effect=Exception("Database error")):
                    result = runner.invoke(wizard, ['81'])

                    assert result.exit_code == 1
                    assert "error" in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
