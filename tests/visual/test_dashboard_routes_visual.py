"""
Visual Regression Tests: Dashboard Routes

Tests visual consistency across viewports for:
- / (Home/Dashboard)
- /overview (System Overview - if exists)

Viewports: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)

Test Pattern:
- AAA (Arrange, Act, Assert) pattern documented in docstrings
- Screenshot capture for visual regression
- Basic element assertions beyond screenshots
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestDashboardVisual:
    """Visual regression tests for dashboard routes."""
    
    def test_home_dashboard_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test home dashboard renders correctly across all viewports.
        
        ARRANGE: Dashboard with metrics cards, navigation, project stats
        ACT: Navigate to / and capture screenshot
        ASSERT: Visual consistency across viewports
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/', 'home-dashboard', viewport)
        
        # ASSERT: Critical elements present
        expect(page.locator('body')).to_be_visible()
        
        # Check for navigation - might be in header, nav, or sidebar
        nav_selectors = ['nav', 'header', '[role="navigation"]', '.navbar', '#navbar']
        nav_found = False
        for selector in nav_selectors:
            if page.locator(selector).count() > 0:
                nav_found = True
                break
        assert nav_found, "Navigation element should be present"
        
        # Check for main content area
        main_selectors = ['main', '[role="main"]', '.main-content', '#main']
        main_found = False
        for selector in main_selectors:
            if page.locator(selector).count() > 0:
                main_found = True
                break
        assert main_found, "Main content area should be present"
    
    def test_dashboard_has_no_errors(self, page: Page, viewport: str, visual_helper):
        """
        Test dashboard page loads without errors.
        
        ARRANGE: Clean dashboard page
        ACT: Navigate to dashboard
        ASSERT: No error messages or 404/500 status
        """
        # ACT: Navigate to dashboard
        page.goto(visual_helper.base_url + '/')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: No error indicators
        error_indicators = page.locator('text=/error|404|500|not found/i').count()
        assert error_indicators == 0, "Dashboard should not display error messages"


@pytest.mark.visual
class TestDashboardInteractive:
    """Interactive element tests for dashboard (desktop only)."""
    
    def test_navigation_menu_accessible(self, page: Page, visual_helper):
        """
        Test navigation menu is accessible and functional.
        
        ARRANGE: Dashboard with navigation
        ACT: Check for navigation links
        ASSERT: Key routes are accessible
        """
        # ARRANGE: Navigate to dashboard
        page.goto(visual_helper.base_url)
        page.wait_for_load_state('networkidle')
        
        # ACT: Check for navigation presence
        nav_exists = page.locator('nav, header, [role="navigation"]').count() > 0
        
        # ASSERT: Navigation should exist
        assert nav_exists, "Navigation menu should be present"
        
        # Check for common navigation links (flexible to match actual implementation)
        possible_links = [
            ('work-items', '/work-items'),
            ('tasks', '/tasks'),
            ('agents', '/agents'),
            ('dashboard', '/'),
        ]
        
        links_found = 0
        for link_text, link_href in possible_links:
            # Check both by text and href
            if (page.locator(f'a[href*="{link_href}"]').count() > 0 or 
                page.locator(f'text=/{link_text}/i').count() > 0):
                links_found += 1
        
        # At least one navigation link should exist
        assert links_found > 0, "At least one navigation link should be present"
    
    def test_dashboard_metrics_visible(self, page: Page, visual_helper):
        """
        Test dashboard displays metrics or project information.
        
        ARRANGE: Dashboard with project data
        ACT: Navigate to dashboard
        ASSERT: Metrics or project info visible
        """
        # ARRANGE & ACT: Navigate to dashboard
        page.goto(visual_helper.base_url)
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Some project information should be visible
        # Look for common dashboard elements
        dashboard_elements = [
            'h1', 'h2', 'h3',  # Headings
            '.metric', '.card', '.stat',  # Metric cards
            'table',  # Data tables
        ]
        
        elements_found = 0
        for selector in dashboard_elements:
            if page.locator(selector).count() > 0:
                elements_found += 1
        
        assert elements_found > 0, "Dashboard should display project information or metrics"
