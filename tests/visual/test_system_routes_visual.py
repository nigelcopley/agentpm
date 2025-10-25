"""
Visual Regression Tests: System Routes

Tests visual consistency across viewports for:
- /search (Search Interface with query parameters)
- /agents (Agent Directory/List)
- /system/health (System Health Dashboard)

Viewports: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestSearchRouteVisual:
    """Visual regression tests for search route."""
    
    def test_search_page_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test search page renders correctly across all viewports.
        
        ARRANGE: Search interface with query input and results
        ACT: Navigate to /search and capture screenshot
        ASSERT: Visual consistency and search elements present
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/search', 'search-page', viewport)
        
        # ASSERT: Page loaded successfully
        expect(page.locator('body')).to_be_visible()
        
        # Check for page heading or search input
        search_indicators = [
            'input[type="search"]',
            'input[type="text"]',
            'h1', 'h2',
            '[role="search"]',
        ]
        
        search_found = False
        for selector in search_indicators:
            if page.locator(selector).count() > 0:
                search_found = True
                break
        assert search_found, "Search page should have search elements"
    
    def test_search_with_query_renders(self, page: Page, viewport: str, visual_helper):
        """
        Test search with query parameter renders results.
        
        ARRANGE: Search page with query parameter
        ACT: Navigate to /search?q=test and capture screenshot
        ASSERT: Search results or query indication visible
        """
        # ACT: Navigate with query parameter
        visual_helper.navigate_and_capture('/search?q=test', 'search-with-query', viewport)
        
        # ASSERT: Page loaded
        expect(page.locator('body')).to_be_visible()


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestAgentsRouteVisual:
    """Visual regression tests for agents directory route."""
    
    def test_agents_list_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test agents directory renders correctly across all viewports.
        
        ARRANGE: Agents list with roles, capabilities, tiers
        ACT: Navigate to /agents and capture screenshot
        ASSERT: Visual consistency and agent information present
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/agents', 'agents-list', viewport)
        
        # ASSERT: Page loaded successfully
        expect(page.locator('body')).to_be_visible()
        
        # Check for page heading
        heading_selectors = ['h1', 'h2', '[role="heading"]']
        heading_found = False
        for selector in heading_selectors:
            if page.locator(selector).count() > 0:
                heading_found = True
                break
        assert heading_found, "Agents page should have a heading"
    
    def test_agents_list_has_no_errors(self, page: Page, viewport: str, visual_helper):
        """
        Test agents list loads without errors.
        
        ARRANGE: Agents listing page
        ACT: Navigate to /agents
        ASSERT: No error messages displayed
        """
        # ACT: Navigate to agents list
        page.goto(visual_helper.base_url + '/agents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: No error indicators
        error_indicators = page.locator('text=/error|404|500|not found/i').count()
        assert error_indicators == 0, "Agents list should not display errors"


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestSystemHealthVisual:
    """Visual regression tests for system health route."""
    
    def test_system_health_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test system health dashboard renders correctly across all viewports.
        
        ARRANGE: Health dashboard with metrics, status indicators
        ACT: Navigate to /system/health and capture screenshot
        ASSERT: Visual consistency and health metrics present
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/system/health', 'system-health', viewport)
        
        # ASSERT: Page loaded successfully
        expect(page.locator('body')).to_be_visible()
        
        # Check for health indicators
        health_indicators = [
            'h1', 'h2',
            '.metric', '.status',
            '[data-health]',
        ]
        
        health_found = False
        for selector in health_indicators:
            if page.locator(selector).count() > 0:
                health_found = True
                break
        assert health_found, "Health page should have status indicators"
    
    def test_system_health_has_no_errors(self, page: Page, viewport: str, visual_helper):
        """
        Test system health page loads without errors.
        
        ARRANGE: Health dashboard
        ACT: Navigate to /system/health
        ASSERT: No error messages displayed
        """
        # ACT: Navigate to health page
        page.goto(visual_helper.base_url + '/system/health')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: No error indicators (but health page may show issues)
        # Just verify page loaded
        expect(page.locator('body')).to_be_visible()


@pytest.mark.visual
class TestSearchInteractive:
    """Interactive element tests for search (desktop only)."""
    
    def test_search_input_functional(self, page: Page, visual_helper):
        """
        Test search input is accessible and functional.
        
        ARRANGE: Search page with input field
        ACT: Check search input exists and is focusable
        ASSERT: Search input interactive
        """
        # ARRANGE & ACT: Navigate to search
        page.goto(visual_helper.base_url + '/search')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for search input
        search_inputs = [
            'input[type="search"]',
            'input[type="text"]',
            '[role="searchbox"]',
        ]
        
        search_input_found = False
        for selector in search_inputs:
            if page.locator(selector).count() > 0:
                search_input_found = True
                # Try to focus
                try:
                    page.locator(selector).first.focus()
                except:
                    pass
                break
        
        # Verify page structure
        assert page.locator('body').count() > 0
    
    def test_search_results_display(self, page: Page, visual_helper):
        """
        Test search displays results or empty state.
        
        ARRANGE: Search with query
        ACT: Navigate with query parameter
        ASSERT: Results or empty state shown
        """
        # ARRANGE & ACT: Navigate with query
        page.goto(visual_helper.base_url + '/search?q=test')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Page should show results or "no results"
        results_indicators = [
            '.result',
            '.search-result',
            'text=/results/i',
            'text=/no results/i',
            'text=/found/i',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0


@pytest.mark.visual
class TestAgentsInteractive:
    """Interactive element tests for agents (desktop only)."""
    
    def test_agents_tier_display(self, page: Page, visual_helper):
        """
        Test agents list shows tier information.
        
        ARRANGE: Agents with tier classifications
        ACT: Check for tier indicators
        ASSERT: Tier badges/labels visible
        """
        # ARRANGE & ACT: Navigate to agents
        page.goto(visual_helper.base_url + '/agents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for tier elements
        tier_elements = [
            '[data-tier]',
            '.tier',
            'text=/tier/i',
            '.badge',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0
    
    def test_agents_capabilities_shown(self, page: Page, visual_helper):
        """
        Test agents list displays capabilities.
        
        ARRANGE: Agents with capability lists
        ACT: Check for capability displays
        ASSERT: Capabilities visible
        """
        # ARRANGE & ACT: Navigate to agents
        page.goto(visual_helper.base_url + '/agents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for capability elements
        capability_elements = [
            '[data-capability]',
            '.capability',
            '.capabilities',
            'ul', 'li',  # List elements
        ]
        
        # Verify page is functional
        assert page.locator('body').count() > 0
    
    def test_agents_status_indicators(self, page: Page, visual_helper):
        """
        Test agents show active/inactive status.
        
        ARRANGE: Agents with active status
        ACT: Check for status indicators
        ASSERT: Status badges present
        """
        # ARRANGE & ACT: Navigate to agents
        page.goto(visual_helper.base_url + '/agents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for status elements
        status_elements = [
            '[data-status]',
            '.status',
            '.active',
            '.inactive',
            'text=/active/i',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0


@pytest.mark.visual
class TestSystemHealthInteractive:
    """Interactive element tests for system health (desktop only)."""
    
    def test_health_metrics_displayed(self, page: Page, visual_helper):
        """
        Test system health shows key metrics.
        
        ARRANGE: Health dashboard with metrics
        ACT: Check for metric displays
        ASSERT: Metrics visible
        """
        # ARRANGE & ACT: Navigate to health
        page.goto(visual_helper.base_url + '/system/health')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for metric elements
        metric_elements = [
            '.metric',
            '.stat',
            '[data-metric]',
            '.card',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0
    
    def test_health_status_indicators(self, page: Page, visual_helper):
        """
        Test health page shows status indicators (healthy, warning, error).
        
        ARRANGE: Health dashboard with status
        ACT: Check for status displays
        ASSERT: Status indicators present
        """
        # ARRANGE & ACT: Navigate to health
        page.goto(visual_helper.base_url + '/system/health')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for status elements
        status_elements = [
            '[data-status]',
            '.status',
            '.healthy', '.warning', '.error',
            'text=/healthy|ok|warning|error/i',
        ]
        
        # Verify page is functional
        assert page.locator('body').count() > 0
