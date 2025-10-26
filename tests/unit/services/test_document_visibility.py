"""
Unit Tests for Document Visibility Policy Engine

Tests the three-layer architecture:
  Layer 1 (Models): VisibilityPolicy, ProjectVisibilityContext, VisibilityEvaluation
  Layer 2 (Services): VisibilityPolicyEngine
  Layer 3 (Adapters): VisibilityPolicyAdapter

Part of Work Item #164: Auto-Generate Document File Paths
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.adapters.visibility_policy_adapter import VisibilityPolicyAdapter
from agentpm.core.services.document_visibility import VisibilityPolicyEngine
from agentpm.core.models.document_visibility import (
    VisibilityPolicy,
    ProjectVisibilityContext,
    VisibilityEvaluation,
    AutoPublishResult,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db():
    """Create in-memory test database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    db = DatabaseService(db_path)

    # Create document_visibility_policies table if not exists
    # This table doesn't exist in migrations yet, so we create it for testing
    with db.transaction() as conn:
        # Check if table exists
        result = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='document_visibility_policies'
        """).fetchone()

        if not result:
            conn.execute("""
                CREATE TABLE document_visibility_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    default_visibility TEXT DEFAULT 'private',
                    default_audience TEXT DEFAULT 'internal',
                    requires_review INTEGER DEFAULT 0,
                    auto_publish_on_approved INTEGER DEFAULT 0,
                    base_score INTEGER DEFAULT 50,
                    force_private INTEGER DEFAULT 0,
                    force_public INTEGER DEFAULT 0,
                    description TEXT,
                    rationale TEXT,
                    auto_publish_trigger TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    UNIQUE(category, doc_type)
                )
            """)

    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def engine(db):
    """Create visibility policy engine"""
    return VisibilityPolicyEngine(db)


@pytest.fixture
def sample_policy():
    """Sample visibility policy for testing (uses test_* to avoid conflicts with default policies)"""
    return VisibilityPolicy(
        category="test_category",
        doc_type="test_type",
        default_visibility="private",
        default_audience="internal",
        requires_review=False,
        auto_publish_on_approved=False,
        base_score=20,
        force_private=True,
        force_public=False,
        description="Test policy for unit tests",
        rationale="This is a test policy"
    )


# ============================================================================
# MODEL TESTS
# ============================================================================

class TestVisibilityPolicy:
    """Test VisibilityPolicy Pydantic model"""

    def test_create_policy(self):
        """Test creating a visibility policy"""
        policy = VisibilityPolicy(
            category="guides",
            doc_type="user_guide",
            base_score=90,
            force_public=True
        )

        assert policy.category == "guides"
        assert policy.doc_type == "user_guide"
        assert policy.base_score == 90
        assert policy.force_public is True
        assert policy.force_private is False

    def test_policy_validation_visibility(self):
        """Test visibility validation"""
        with pytest.raises(ValueError, match="Invalid visibility"):
            VisibilityPolicy(
                category="test",
                doc_type="test",
                default_visibility="invalid"
            )

    def test_policy_validation_audience(self):
        """Test audience validation"""
        with pytest.raises(ValueError, match="Invalid audience"):
            VisibilityPolicy(
                category="test",
                doc_type="test",
                default_audience="invalid"
            )

    def test_policy_validation_base_score(self):
        """Test base score validation (must be 0-100)"""
        with pytest.raises(ValueError):
            VisibilityPolicy(
                category="test",
                doc_type="test",
                base_score=-10
            )

        with pytest.raises(ValueError):
            VisibilityPolicy(
                category="test",
                doc_type="test",
                base_score=150
            )


class TestProjectVisibilityContext:
    """Test ProjectVisibilityContext model"""

    def test_create_context(self):
        """Test creating project context"""
        context = ProjectVisibilityContext(
            team_size="large",
            dev_stage="production",
            collaboration_model="open_source"
        )

        assert context.team_size == "large"
        assert context.dev_stage == "production"
        assert context.collaboration_model == "open_source"

    def test_context_validation_team_size(self):
        """Test team size validation"""
        with pytest.raises(ValueError, match="Invalid team_size"):
            ProjectVisibilityContext(team_size="invalid")

    def test_context_validation_dev_stage(self):
        """Test dev stage validation"""
        with pytest.raises(ValueError, match="Invalid dev_stage"):
            ProjectVisibilityContext(dev_stage="invalid")

    def test_context_validation_collaboration_model(self):
        """Test collaboration model validation"""
        with pytest.raises(ValueError, match="Invalid collaboration_model"):
            ProjectVisibilityContext(collaboration_model="invalid")


# ============================================================================
# ADAPTER TESTS
# ============================================================================

class TestVisibilityPolicyAdapter:
    """Test VisibilityPolicyAdapter database operations"""

    def test_create_policy(self, db, sample_policy):
        """Test creating policy in database"""
        created = VisibilityPolicyAdapter.create(db, sample_policy)

        assert created.id is not None
        assert created.category == "test_category"
        assert created.doc_type == "test_type"
        assert created.base_score == 20
        assert created.force_private is True

    def test_get_policy(self, db, sample_policy):
        """Test getting policy by ID"""
        created = VisibilityPolicyAdapter.create(db, sample_policy)
        fetched = VisibilityPolicyAdapter.get(db, created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.category == created.category

    def test_get_policy_not_found(self, db):
        """Test getting non-existent policy"""
        result = VisibilityPolicyAdapter.get(db, 9999)
        assert result is None

    def test_get_by_type(self, db, sample_policy):
        """Test getting policy by category and doc_type"""
        VisibilityPolicyAdapter.create(db, sample_policy)
        fetched = VisibilityPolicyAdapter.get_by_type(db, "test_category", "test_type")

        assert fetched is not None
        assert fetched.category == "test_category"
        assert fetched.doc_type == "test_type"

    def test_list_policies(self, db, sample_policy):
        """Test listing all policies"""
        # Get initial count (default policies from migration)
        initial_policies = VisibilityPolicyAdapter.list(db)
        initial_count = len(initial_policies)

        VisibilityPolicyAdapter.create(db, sample_policy)

        policy2 = VisibilityPolicy(
            category="test_category2",
            doc_type="test_type2",
            base_score=65
        )
        VisibilityPolicyAdapter.create(db, policy2)

        policies = VisibilityPolicyAdapter.list(db)
        assert len(policies) == initial_count + 2

    def test_list_policies_by_category(self, db, sample_policy):
        """Test listing policies filtered by category"""
        VisibilityPolicyAdapter.create(db, sample_policy)

        policy2 = VisibilityPolicy(
            category="test_category2",
            doc_type="test_type2",
            base_score=65
        )
        VisibilityPolicyAdapter.create(db, policy2)

        test_policies = VisibilityPolicyAdapter.list(db, category="test_category")
        assert len(test_policies) == 1
        assert test_policies[0].category == "test_category"

    def test_update_policy(self, db, sample_policy):
        """Test updating policy"""
        created = VisibilityPolicyAdapter.create(db, sample_policy)

        created.base_score = 30
        created.description = "Updated description"

        updated = VisibilityPolicyAdapter.update(db, created)

        assert updated is not None
        assert updated.base_score == 30
        assert updated.description == "Updated description"

    def test_delete_policy(self, db, sample_policy):
        """Test deleting policy"""
        created = VisibilityPolicyAdapter.create(db, sample_policy)

        deleted = VisibilityPolicyAdapter.delete(db, created.id)
        assert deleted is True

        # Verify deleted
        fetched = VisibilityPolicyAdapter.get(db, created.id)
        assert fetched is None


# ============================================================================
# SERVICE TESTS - SCORING ALGORITHM
# ============================================================================

class TestScoringAlgorithm:
    """Test visibility score calculation"""

    def test_score_calculation_base(self, db, engine):
        """Test base score without modifiers"""
        policy = VisibilityPolicy(
            category="test",
            doc_type="test",
            base_score=50
        )
        VisibilityPolicyAdapter.create(db, policy)

        # With review lifecycle (no modifier)
        result = engine.determine_visibility("test", "test", "review")

        # Base score 50 + solo (-20) + development (-10) + private (-30) + review (0) = -10 → 0 (clamped)
        # But score calculation doesn't clamp internally, just for thresholding
        assert result.base_score == 50

    def test_score_with_team_size_modifiers(self, db):
        """Test team size modifiers"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        # Solo: -20
        engine_solo = VisibilityPolicyEngine(db)
        engine_solo.project_context.team_size = "solo"
        result = engine_solo.determine_visibility("test", "test", "review")
        assert "team_size" in result.context_modifiers
        assert result.context_modifiers["team_size"] == -20

    def test_score_with_dev_stage_modifiers(self, db):
        """Test development stage modifiers"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        engine_prod = VisibilityPolicyEngine(db)
        engine_prod.project_context.dev_stage = "production"
        result = engine_prod.determine_visibility("test", "test", "review")
        assert "dev_stage" in result.context_modifiers
        assert result.context_modifiers["dev_stage"] == 15

    def test_score_with_collaboration_modifiers(self, db):
        """Test collaboration model modifiers"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        engine_os = VisibilityPolicyEngine(db)
        engine_os.project_context.collaboration_model = "open_source"
        result = engine_os.determine_visibility("test", "test", "review")
        assert "collaboration_model" in result.context_modifiers
        assert result.context_modifiers["collaboration_model"] == 30


# ============================================================================
# SERVICE TESTS - VISIBILITY DETERMINATION
# ============================================================================

class TestVisibilityDetermination:
    """Test visibility level determination"""

    def test_force_private_override(self, db, engine):
        """Test force_private overrides scoring"""
        # Use test_* to avoid conflicts with default policies
        policy = VisibilityPolicy(
            category="test_force",
            doc_type="test_private",
            base_score=90,  # High score
            force_private=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.determine_visibility("test_force", "test_private", "approved")

        assert result.visibility == "private"
        assert result.final_score == 0
        assert "force_private" in result.rationale

    def test_force_public_override(self, db, engine):
        """Test force_public overrides scoring when approved"""
        # Use test_* to avoid conflicts with default policies
        policy = VisibilityPolicy(
            category="test_force",
            doc_type="test_public",
            base_score=20,  # Low score
            force_public=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.determine_visibility("test_force", "test_public", "approved")

        assert result.visibility == "public"
        assert result.final_score == 100
        assert "force_public" in result.rationale

    def test_draft_lifecycle_override(self, db, engine):
        """Test draft lifecycle always private"""
        # Use test_* to avoid conflicts with default policies
        policy = VisibilityPolicy(
            category="test_lifecycle",
            doc_type="test_draft",
            base_score=90,
            force_public=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.determine_visibility("test_lifecycle", "test_draft", "draft")

        assert result.visibility == "private"
        assert "draft" in result.rationale.lower()

    def test_archived_lifecycle_override(self, db, engine):
        """Test archived lifecycle always private"""
        # Use test_* to avoid conflicts with default policies
        policy = VisibilityPolicy(
            category="test_lifecycle",
            doc_type="test_archived",
            base_score=90,
            force_public=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.determine_visibility("test_lifecycle", "test_archived", "archived")

        assert result.visibility == "private"
        assert "archived" in result.rationale.lower()

    def test_score_threshold_private(self, db):
        """Test score < 40 → private"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        # Create engine with context that produces low score
        engine = VisibilityPolicyEngine(db)
        engine.project_context.team_size = "solo"  # -20
        engine.project_context.dev_stage = "development"  # -10
        engine.project_context.collaboration_model = "private"  # -30
        # Base 50 - 20 - 10 - 30 + 0 (review) = -10 → private

        result = engine.determine_visibility("test", "test", "review")
        assert result.visibility == "private"

    def test_score_threshold_public(self, db):
        """Test score >= 60 → public"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        # Create engine with context that produces high score
        engine = VisibilityPolicyEngine(db)
        engine.project_context.team_size = "large"  # +20
        engine.project_context.dev_stage = "production"  # +15
        engine.project_context.collaboration_model = "open_source"  # +30
        # Base 50 + 20 + 15 + 30 + 10 (approved) = 125 → public

        result = engine.determine_visibility("test", "test", "approved")
        assert result.visibility == "public"

    def test_missing_policy_uses_default(self, db, engine):
        """Test missing policy uses safe defaults"""
        result = engine.determine_visibility("unknown", "unknown", "draft")

        assert result.visibility == "private"
        assert result.base_score == 50  # Default

    def test_audience_team_threshold(self, db):
        """Test audience 'team' for scores 30-49"""
        policy = VisibilityPolicy(category="test_audience", doc_type="test_team", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        engine = VisibilityPolicyEngine(db)
        engine.project_context.team_size = "solo"  # -20
        engine.project_context.dev_stage = "development"  # -10
        engine.project_context.collaboration_model = "internal"  # 0
        # Base 50 - 20 - 10 + 0 (review) = 20, but we want 30-49 range
        # Adjust base score to hit that range
        policy2 = VisibilityPolicy(category="test_audience2", doc_type="test_team2", base_score=60)
        VisibilityPolicyAdapter.create(db, policy2)

        result = engine.determine_visibility("test_audience2", "test_team2", "review")
        # Base 60 - 20 - 10 = 30 → team audience
        assert result.audience == "team"

    def test_audience_users_threshold(self, db):
        """Test audience 'users' for scores 70-84"""
        policy = VisibilityPolicy(category="test_audience", doc_type="test_users", base_score=70)
        VisibilityPolicyAdapter.create(db, policy)

        engine = VisibilityPolicyEngine(db)
        engine.project_context.team_size = "medium"  # +10
        engine.project_context.dev_stage = "staging"  # 0
        engine.project_context.collaboration_model = "internal"  # 0
        # Base 70 + 10 + 0 + 0 (review) = 80 → users audience

        result = engine.determine_visibility("test_audience", "test_users", "review")
        assert result.audience == "users"

    def test_rationale_includes_policy_rationale(self, db, engine):
        """Test that policy rationale is included in evaluation rationale"""
        policy = VisibilityPolicy(
            category="test_rationale",
            doc_type="test_doc",
            base_score=50,
            rationale="This is a custom policy rationale for testing"
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.determine_visibility("test_rationale", "test_doc", "review")

        assert "Policy rationale" in result.rationale
        assert "custom policy rationale" in result.rationale


# ============================================================================
# SERVICE TESTS - AUTO-PUBLISH
# ============================================================================

class TestAutoPublish:
    """Test auto-publish trigger detection"""

    def test_auto_publish_on_approved(self, db, engine):
        """Test on_approved trigger"""
        # Use test_* to avoid conflicts, but set auto_publish_on_approved=True
        policy = VisibilityPolicy(
            category="test_auto",
            doc_type="test_approved",
            auto_publish_on_approved=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.should_auto_publish("test_auto", "test_approved", "approved")

        assert result.should_publish is True
        assert result.trigger_type == "on_approved"

    def test_auto_publish_already_published(self, db, engine):
        """Test already published returns False"""
        # Use test_* to avoid conflicts
        policy = VisibilityPolicy(
            category="test_auto",
            doc_type="test_published",
            auto_publish_on_approved=True
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.should_auto_publish("test_auto", "test_published", "published")

        assert result.should_publish is False
        assert "already published" in result.trigger_reason

    def test_auto_publish_on_work_item_phase_R1(self, db, engine):
        """Test on_work_item_phase_R1 trigger - uses default policy from migration"""
        # architecture.design_doc is in AUTO_PUBLISH_ON_WORK_ITEM_PHASE_R1 list
        # It already exists from migration, so we just test against it directly

        result = engine.should_auto_publish(
            "architecture", "design_doc", "approved", work_item_phase="R1_REVIEW"
        )

        assert result.should_publish is True
        assert result.trigger_type == "on_work_item_phase_R1"

    def test_auto_publish_on_work_item_phase_O1(self, db, engine):
        """Test on_work_item_phase_O1 trigger - uses default policy from migration"""
        # architecture.adr is in AUTO_PUBLISH_ON_WORK_ITEM_PHASE_O1 list
        # It already exists from migration, so we just test against it directly

        result = engine.should_auto_publish(
            "architecture", "adr", "approved", work_item_phase="O1_OPERATIONS"
        )

        assert result.should_publish is True
        assert result.trigger_type == "on_work_item_phase_O1"

    def test_manual_publish_required(self, db, engine):
        """Test manual publish required (no triggers)"""
        # Use test_* to avoid conflicts
        policy = VisibilityPolicy(
            category="test_manual",
            doc_type="test_no_auto",
            auto_publish_on_approved=False
        )
        VisibilityPolicyAdapter.create(db, policy)

        result = engine.should_auto_publish("test_manual", "test_no_auto", "approved")

        assert result.should_publish is False
        assert "manual publish required" in result.trigger_reason


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEnd:
    """Test complete visibility evaluation workflows"""

    def test_user_guide_workflow(self, db, engine):
        """Test user guide: force_public, auto-publish on approved - uses default policy"""
        # guides.user_guide already exists from migration with force_public=True
        # No need to create policy, just test against default

        # Draft → private
        result_draft = engine.determine_visibility("guides", "user_guide", "draft")
        assert result_draft.visibility == "private"

        # Approved → public (force_public)
        result_approved = engine.determine_visibility("guides", "user_guide", "approved")
        assert result_approved.visibility == "public"
        assert result_approved.requires_review is True

        # Auto-publish check
        auto_publish = engine.should_auto_publish("guides", "user_guide", "approved")
        assert auto_publish.should_publish is True

    def test_idea_workflow(self, db, engine):
        """Test idea: force_private, never auto-publish - uses default policy"""
        # planning.idea already exists from migration with force_private=True
        # No need to create policy, just test against default

        # Draft → private
        result_draft = engine.determine_visibility("planning", "idea", "draft")
        assert result_draft.visibility == "private"

        # Approved → still private (force_private)
        result_approved = engine.determine_visibility("planning", "idea", "approved")
        assert result_approved.visibility == "private"

        # Auto-publish check → no
        auto_publish = engine.should_auto_publish("planning", "idea", "approved")
        assert auto_publish.should_publish is False

    def test_adr_workflow(self, db):
        """Test ADR: context-aware, auto-publish on O1 - uses default policy"""
        # architecture.adr already exists from migration with base_score=65
        # No need to create policy, just test against default

        # Open source production context → high score
        engine_public = VisibilityPolicyEngine(db)
        engine_public.project_context.team_size = "large"  # +20
        engine_public.project_context.dev_stage = "production"  # +15
        engine_public.project_context.collaboration_model = "open_source"  # +30

        result = engine_public.determine_visibility("architecture", "adr", "approved")
        # Base 65 + 20 + 15 + 30 + 10 = 140 → public
        assert result.visibility == "public"

        # Auto-publish on O1_OPERATIONS
        auto_publish = engine_public.should_auto_publish(
            "architecture", "adr", "approved", work_item_phase="O1_OPERATIONS"
        )
        assert auto_publish.should_publish is True
        assert auto_publish.trigger_type == "on_work_item_phase_O1"


# ============================================================================
# CACHE TESTS
# ============================================================================

class TestCaching:
    """Test policy caching"""

    def test_policy_caching(self, db, engine):
        """Test policies are cached after first load"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        # First call - loads from database
        result1 = engine.determine_visibility("test", "test", "draft")

        # Second call - should use cache
        result2 = engine.determine_visibility("test", "test", "draft")

        assert result1.visibility == result2.visibility

    def test_clear_cache(self, db, engine):
        """Test clearing policy cache"""
        policy = VisibilityPolicy(category="test", doc_type="test", base_score=50)
        VisibilityPolicyAdapter.create(db, policy)

        # Load into cache
        engine.determine_visibility("test", "test", "draft")

        # Clear cache
        engine.clear_cache()

        # Should reload from database
        result = engine.determine_visibility("test", "test", "draft")
        assert result is not None
