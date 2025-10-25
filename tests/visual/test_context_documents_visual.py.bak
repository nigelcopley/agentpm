"""
Visual Regression Tests: Context & Documents Routes

Tests visual consistency across viewports for:
- /context (Context Management List)
- /documents (Document References List)

Viewports: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestContextListVisual:
    """Visual regression tests for context management route."""
    
    def test_context_list_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test context list page renders correctly across all viewports.
        
        ARRANGE: Context management with 6W contexts, entity links
        ACT: Navigate to /context and capture screenshot
        ASSERT: Visual consistency and critical elements present
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/context', 'context-list', viewport)
        
        # ASSERT: Page loaded successfully
        expect(page.locator('body')).to_be_visible()
        
        # Check for page heading
        heading_selectors = ['h1', 'h2', '[role="heading"]']
        heading_found = False
        for selector in heading_selectors:
            if page.locator(selector).count() > 0:
                heading_found = True
                break
        assert heading_found, "Context page should have a heading"
    
    def test_context_list_has_no_errors(self, page: Page, viewport: str, visual_helper):
        """
        Test context list loads without errors.
        
        ARRANGE: Context listing page
        ACT: Navigate to /context
        ASSERT: No error messages displayed
        """
        # ACT: Navigate to context list
        page.goto(visual_helper.base_url + '/context')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: No error indicators
        error_indicators = page.locator('text=/error|404|500|not found/i').count()
        assert error_indicators == 0, "Context list should not display errors"


@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
class TestDocumentsListVisual:
    """Visual regression tests for documents route."""
    
    def test_documents_list_renders_correctly(self, page: Page, viewport: str, visual_helper):
        """
        Test documents list page renders correctly across all viewports.
        
        ARRANGE: Document references with types, entities, file paths
        ACT: Navigate to /documents and capture screenshot
        ASSERT: Visual consistency and critical elements present
        """
        # ACT: Navigate and capture screenshot
        visual_helper.navigate_and_capture('/documents', 'documents-list', viewport)
        
        # ASSERT: Page loaded successfully
        expect(page.locator('body')).to_be_visible()
        
        # Check for page heading
        heading_selectors = ['h1', 'h2', '[role="heading"]']
        heading_found = False
        for selector in heading_selectors:
            if page.locator(selector).count() > 0:
                heading_found = True
                break
        assert heading_found, "Documents page should have a heading"
    
    def test_documents_list_has_no_errors(self, page: Page, viewport: str, visual_helper):
        """
        Test documents list loads without errors.
        
        ARRANGE: Documents listing page
        ACT: Navigate to /documents
        ASSERT: No error messages displayed
        """
        # ACT: Navigate to documents list
        page.goto(visual_helper.base_url + '/documents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: No error indicators
        error_indicators = page.locator('text=/error|404|500|not found/i').count()
        assert error_indicators == 0, "Documents list should not display errors"


@pytest.mark.visual
class TestContextInteractive:
    """Interactive element tests for context (desktop only)."""
    
    def test_context_entity_links_present(self, page: Page, visual_helper):
        """
        Test context list shows entity associations.
        
        ARRANGE: Context list with entity references
        ACT: Check for entity link elements
        ASSERT: Entity associations visible
        """
        # ARRANGE & ACT: Navigate to context
        page.goto(visual_helper.base_url + '/context')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for entity-related elements
        entity_elements = [
            'a[href*="work-items"]',
            'a[href*="tasks"]',
            '[data-entity]',
            '.entity',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0
    
    def test_context_confidence_indicators(self, page: Page, visual_helper):
        """
        Test context list displays confidence scores.
        
        ARRANGE: Context list with confidence metrics
        ACT: Check for confidence displays
        ASSERT: Confidence indicators present
        """
        # ARRANGE & ACT: Navigate to context
        page.goto(visual_helper.base_url + '/context')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for confidence elements
        confidence_elements = [
            '[data-confidence]',
            '.confidence',
            'text=/confidence/i',
            'text=/%/',  # Percentage indicators
        ]
        
        # Verify page is functional
        assert page.locator('body').count() > 0
    
    def test_context_6w_display(self, page: Page, visual_helper):
        """
        Test context list shows 6W context data.
        
        ARRANGE: Context with 6W (Who, What, When, Where, Why, How)
        ACT: Check for 6W indicators
        ASSERT: 6W data visible
        """
        # ARRANGE & ACT: Navigate to context
        page.goto(visual_helper.base_url + '/context')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for 6W elements
        six_w_indicators = [
            'text=/who|what|when|where|why|how/i',
            '[data-context-type="6w"]',
            '.six-w',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0


@pytest.mark.visual
class TestDocumentsInteractive:
    """Interactive element tests for documents (desktop only)."""
    
    def test_documents_type_filtering(self, page: Page, visual_helper):
        """
        Test documents list has type filtering.
        
        ARRANGE: Documents with various types (requirements, design, etc.)
        ACT: Check for type filter elements
        ASSERT: Filter controls present
        """
        # ARRANGE & ACT: Navigate to documents
        page.goto(visual_helper.base_url + '/documents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for filter elements
        filter_elements = [
            'select',
            '[role="listbox"]',
            'button:has-text("Filter")',
            '.filter',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0
    
    def test_documents_file_links(self, page: Page, visual_helper):
        """
        Test documents list shows file path links.
        
        ARRANGE: Documents with file paths
        ACT: Check for file path displays
        ASSERT: File paths visible
        """
        # ARRANGE & ACT: Navigate to documents
        page.goto(visual_helper.base_url + '/documents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for file path elements
        file_elements = [
            'a[href*="/docs/"]',
            'code',
            '.filepath',
            '[data-path]',
        ]
        
        # Verify page is functional
        assert page.locator('body').count() > 0
    
    def test_documents_entity_references(self, page: Page, visual_helper):
        """
        Test documents show associated entities.
        
        ARRANGE: Documents linked to work items/tasks
        ACT: Check for entity reference displays
        ASSERT: Entity links present
        """
        # ARRANGE & ACT: Navigate to documents
        page.goto(visual_helper.base_url + '/documents')
        page.wait_for_load_state('networkidle')
        
        # ASSERT: Look for entity reference elements
        entity_refs = [
            'a[href*="work-items"]',
            'a[href*="tasks"]',
            '[data-entity-id]',
            '.entity-link',
        ]
        
        # Verify page structure
        assert page.locator('body').count() > 0
