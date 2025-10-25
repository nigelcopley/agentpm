"""
Pytest configuration for branding tests.

Provides fixtures and markers for branding validation.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "branding: tests that validate APM branding consistency"
    )
    config.addinivalue_line(
        "markers",
        "codebase_scan: tests that scan codebase for branding issues"
    )


@pytest.fixture
def branding_terms():
    """Dictionary of expected branding terms."""
    return {
        'product_name': 'APM',
        'full_name': 'Agent Project Manager',
        'domain': 'apm.run',
        'tagline': 'Multi-Agent Project Management for Your Terminal',
        'legacy_name': 'AIPM',  # To detect and flag
        'command': 'apm',
    }


@pytest.fixture
def legacy_patterns():
    """Patterns that indicate legacy AIPM branding."""
    return [
        'APM (Agent Project Manager)',
        'APM project',
        'Agent Project Manager',
    ]
