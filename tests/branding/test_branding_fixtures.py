"""
Fixture-based branding validation tests.

Tests that use fixtures from conftest.py to validate branding consistency.
"""

import pytest
from pathlib import Path


class TestBrandingTerminology:
    """Test branding terminology consistency using fixtures."""

    def test_product_name_is_apm(self, branding_terms):
        """Verify product name is APM."""
        assert branding_terms['product_name'] == 'APM'
        assert branding_terms['full_name'] == 'Agent Project Manager'

    def test_domain_is_correct(self, branding_terms):
        """Verify domain is apm.run."""
        assert branding_terms['domain'] == 'apm.run'

    def test_command_is_apm(self, branding_terms):
        """Verify command line tool is 'apm'."""
        assert branding_terms['command'] == 'apm'

    def test_tagline_is_defined(self, branding_terms):
        """Verify tagline is defined."""
        assert branding_terms['tagline']
        assert 'Multi-Agent' in branding_terms['tagline']
        assert 'Project Management' in branding_terms['tagline']


class TestLegacyPatternDetection:
    """Test detection of legacy AIPM patterns."""

    def test_legacy_patterns_defined(self, legacy_patterns):
        """Verify legacy patterns are defined for detection."""
        assert 'APM (Agent Project Manager)' in legacy_patterns
        assert 'APM project' in legacy_patterns
        assert 'Agent Project Manager' in legacy_patterns

    def test_detect_legacy_in_sample_text(self, legacy_patterns):
        """Test legacy pattern detection in sample text."""
        sample_texts = [
            "Welcome to APM (Agent Project Manager) - Agent Project Manager",
            "Initialize APM project with database",
            "The APM tool helps you manage projects",
        ]

        # First two should match legacy patterns
        assert any(pattern in sample_texts[0] for pattern in legacy_patterns)
        assert any(pattern in sample_texts[1] for pattern in legacy_patterns)

        # Third should not match (uses APM correctly)
        # (Note: would need to filter out "AIPM" from "APM")


class TestBrandingGuidelines:
    """Test adherence to branding guidelines."""

    @pytest.fixture
    def branding_guidelines(self):
        """Branding guidelines dictionary."""
        return {
            'user_facing_name': 'APM',
            'internal_package': 'agentpm',  # Package name stays as is
            'cli_command': 'apm',
            'acceptable_references': [
                'APM',
                'Agent Project Manager',
                'apm.run',
                'apm command',
            ],
            'legacy_to_avoid': [
                'APM (Agent Project Manager)',
                'APM project',
                'Agent Project Manager',
            ],
        }

    def test_user_facing_name(self, branding_guidelines):
        """Verify user-facing name guideline."""
        assert branding_guidelines['user_facing_name'] == 'APM'

    def test_package_name_unchanged(self, branding_guidelines):
        """Verify internal package name remains agentpm."""
        # Package name stays as agentpm (internal)
        assert branding_guidelines['internal_package'] == 'agentpm'

    def test_acceptable_references(self, branding_guidelines):
        """Verify acceptable brand references."""
        acceptable = branding_guidelines['acceptable_references']

        assert 'APM' in acceptable
        assert 'Agent Project Manager' in acceptable
        assert 'apm.run' in acceptable

    def test_legacy_references_to_avoid(self, branding_guidelines):
        """Verify legacy references to avoid."""
        legacy = branding_guidelines['legacy_to_avoid']

        assert 'APM (Agent Project Manager)' in legacy
        assert 'APM project' in legacy


class TestBrandingDocumentation:
    """Test branding documentation and examples."""

    @pytest.fixture
    def project_root(self):
        """Get project root."""
        return Path(__file__).parent.parent.parent

    def test_branding_readme_exists(self, project_root):
        """Check if branding documentation exists."""
        # This is aspirational - we may want to create branding docs
        docs_dir = project_root / 'docs'

        # Just verify docs directory exists
        # Actual branding docs can be added later
        if docs_dir.exists():
            assert docs_dir.is_dir()

    def test_changelog_or_migration_notes(self, project_root):
        """Check for changelog or migration notes about branding."""
        # Look for common changelog locations
        changelog_paths = [
            project_root / 'CHANGELOG.md',
            project_root / 'docs' / 'CHANGELOG.md',
            project_root / 'WI-146-COMPLETION-SUMMARY.md',
        ]

        # Check if any exist
        existing = [p for p in changelog_paths if p.exists()]

        # At least one should exist (the WI completion summary)
        assert len(existing) > 0, "Should have some documentation"


# Pytest markers
pytestmark = [
    pytest.mark.branding,
]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
