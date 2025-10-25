"""
Playwright Visual Regression Testing Configuration

Provides fixtures and utilities for visual regression testing of APM (Agent Project Manager) web application.

Features:
- Multi-viewport testing (desktop, tablet, mobile)
- Screenshot capture and comparison
- Test data fixtures
- Database service integration
- Visual helper utilities

Viewports:
- Desktop: 1920x1080
- Tablet: 768x1024
- Mobile: 375x667
"""

import pytest
import os
from pathlib import Path
from typing import Dict
from playwright.sync_api import Page, Browser, BrowserContext

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import (
    projects,
    work_items as work_items_methods,
    tasks as tasks_methods,
    agents as agent_methods,
    rules as rules_methods,
    contexts as context_methods,
    document_references as doc_methods,
)
from agentpm.core.database.models import (
    Project,
    WorkItem,
    Task,
    Agent,
    Rule,
    Context,
    DocumentReference,
)
from agentpm.core.database.enums import (
    WorkItemStatus,
    WorkItemType,
    TaskStatus,
    TaskType,
    EnforcementLevel,
    AgentTier,
    EntityType,
    ContextType,
    DocumentType,
)

# Viewport configurations
VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 667},
}


@pytest.fixture(scope="session")
def screenshots_dir() -> Path:
    """Get screenshots directory, creating if needed."""
    screenshots_path = Path(__file__).parent / "screenshots"
    screenshots_path.mkdir(exist_ok=True)
    return screenshots_path


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the web application."""
    return os.environ.get("AIPM_WEB_URL", "http://localhost:5000")


@pytest.fixture
def test_db_path(tmp_path) -> str:
    """Create temporary database path for visual tests."""
    db_path = tmp_path / ".aipm" / "data" / "visual_test.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)


@pytest.fixture
def test_db_service(test_db_path) -> DatabaseService:
    """
    Create a test database service with clean schema.

    Returns:
        DatabaseService: Initialized database service for visual testing
    """
    service = DatabaseService(test_db_path)
    yield service


@pytest.fixture
def test_project(test_db_service) -> Project:
    """
    Create a test project with comprehensive data.

    Returns:
        Project: Created test project with metadata
    """
    project = Project(
        name="APM (Agent Project Manager) Visual Test Project",
        description="Test project for visual regression testing",
        path="/tmp/aipm-visual-test",
        tech_stack=["Python", "Flask", "SQLite", "Playwright"],
        status="active",
        business_domain="Testing & Quality Assurance"
    )
    return projects.create_project(test_db_service, project)


@pytest.fixture
def viewport(request) -> str:
    """Get viewport name from parametrized test."""
    return request.param if hasattr(request, 'param') else "desktop"


@pytest.fixture
def page(browser: Browser, viewport: str, base_url: str) -> Page:
    """
    Create a Playwright page with viewport configuration.

    Args:
        browser: Playwright browser instance
        viewport: Viewport name (desktop, tablet, mobile)
        base_url: Base URL for testing

    Returns:
        Page: Configured Playwright page
    """
    viewport_config = VIEWPORTS.get(viewport, VIEWPORTS["desktop"])

    context = browser.new_context(
        viewport=viewport_config,
        base_url=base_url,
    )

    page = context.new_page()
    page.set_default_timeout(10000)  # 10 seconds

    yield page

    page.close()
    context.close()


@pytest.fixture
def visual_helper(page: Page, base_url: str, screenshots_dir: Path, viewport: str):
    """
    Visual testing helper with screenshot capture utilities.

    Provides methods for navigating to routes and capturing screenshots
    with consistent naming and organization.

    Usage:
        visual_helper.navigate_and_capture('/work-items', 'work-items-list', 'desktop')
    """
    class VisualHelper:
        def __init__(self, page: Page, base_url: str, screenshots_dir: Path, viewport: str):
            self.page = page
            self.base_url = base_url
            self.screenshots_dir = screenshots_dir
            self.viewport = viewport

        def navigate_and_capture(
            self,
            route: str,
            screenshot_name: str,
            viewport: str = None,
            wait_for_selector: str = None,
            full_page: bool = True
        ):
            """
            Navigate to route and capture screenshot.

            Args:
                route: Route path (e.g., '/work-items')
                screenshot_name: Base name for screenshot (e.g., 'work-items-list')
                viewport: Viewport name (defaults to fixture viewport)
                wait_for_selector: Optional selector to wait for before screenshot
                full_page: Capture full page (default: True)
            """
            viewport = viewport or self.viewport

            # Navigate to route
            url = f"{self.base_url}{route}"
            self.page.goto(url)

            # Wait for page to be fully loaded
            self.page.wait_for_load_state('networkidle')

            # Wait for specific selector if provided
            if wait_for_selector:
                self.page.wait_for_selector(wait_for_selector, timeout=5000)

            # Create viewport-specific directory
            viewport_dir = self.screenshots_dir / viewport
            viewport_dir.mkdir(exist_ok=True)

            # Capture screenshot
            screenshot_path = viewport_dir / f"{screenshot_name}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=full_page)

            return screenshot_path

        def capture_element(
            self,
            selector: str,
            screenshot_name: str,
            viewport: str = None
        ):
            """
            Capture screenshot of specific element.

            Args:
                selector: CSS selector for element
                screenshot_name: Base name for screenshot
                viewport: Viewport name (defaults to fixture viewport)
            """
            viewport = viewport or self.viewport

            # Wait for element
            element = self.page.wait_for_selector(selector, timeout=5000)

            # Create viewport-specific directory
            viewport_dir = self.screenshots_dir / viewport
            viewport_dir.mkdir(exist_ok=True)

            # Capture element screenshot
            screenshot_path = viewport_dir / f"{screenshot_name}.png"
            element.screenshot(path=str(screenshot_path))

            return screenshot_path

    return VisualHelper(page, base_url, screenshots_dir, viewport)


@pytest.fixture(scope="session")
def playwright():
    """Session-scoped Playwright instance."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright):
    """Session-scoped browser instance."""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


def pytest_configure(config):
    """Configure pytest markers for visual tests."""
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )
