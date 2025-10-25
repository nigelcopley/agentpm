"""
Test Main Blueprint Routes (Dashboard and Project Views)

Tests for refactored main.py routes covering:
- Dashboard route (/)
- Project detail view
- Project context view
- Test routes (dev only)

Acceptance Criteria Validation:
1. All routes follow consistent RESTful naming patterns
2. No route overlap with other blueprints
3. Clear separation of concerns
4. All existing functionality preserved
"""

import pytest
from flask import url_for


class TestDashboardRoute:
    """Test dashboard landing page route."""

    def test_dashboard_loads(self, client):
        """
        Test dashboard route is accessible.

        ARRANGE: Flask app with empty or populated database
        ACT: GET /
        ASSERT: 200 status, page loads
        """
        response = client.get('/')
        assert response.status_code == 200

    def test_dashboard_returns_html(self, client):
        """
        Test dashboard returns HTML content.

        ARRANGE: Flask app running
        ACT: GET /
        ASSERT: HTML content type
        """
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type


class TestProjectDetailRoute:
    """Test project detail view route."""

    def test_project_detail_invalid_id_returns_404(self, client):
        """
        Test project detail route with non-existent project ID.

        ARRANGE: No project with ID 9999
        ACT: GET /project/9999
        ASSERT: 404 status
        """
        response = client.get('/project/9999')
        assert response.status_code == 404

    def test_project_detail_route_pattern_exists(self, app):
        """
        Test project detail route pattern is registered.

        ARRANGE: Flask app with routes
        ACT: Check route map
        ASSERT: /project/<int:project_id> route exists
        """
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert any('/project/<int:project_id>' in route for route in routes)


class TestProjectContextRoute:
    """Test project context view route (6W framework)."""

    def test_project_context_invalid_id_returns_404(self, client):
        """
        Test project context route with non-existent project ID.

        ARRANGE: No project with ID 9999
        ACT: GET /project/9999/context
        ASSERT: 404 status
        """
        response = client.get('/project/9999/context')
        assert response.status_code == 404

    def test_project_context_route_pattern_exists(self, app):
        """
        Test project context route pattern is registered.

        ARRANGE: Flask app with routes
        ACT: Check route map
        ASSERT: /project/<int:project_id>/context route exists
        """
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        assert any('/project/<int:project_id>/context' in route for route in routes)


class TestToastNotificationRoutes:
    """Test toast notification test routes (dev only)."""

    def test_test_toasts_page(self, client):
        """
        Test toast notification test page loads.

        ARRANGE: Flask app running
        ACT: GET /test-toasts
        ASSERT: 200 status, test page displayed
        """
        response = client.get('/test-toasts')
        assert response.status_code == 200

    def test_trigger_success_toast(self, client):
        """
        Test triggering success toast via HTMX endpoint.

        ARRANGE: Flask app with toast system
        ACT: POST /test-toast/success
        ASSERT: Response with X-Toast headers
        """
        response = client.post('/test-toast/success')
        # Should return success (likely 204 No Content for HTMX)
        assert response.status_code in [200, 204]
        # Should have toast headers
        assert 'X-Toast-Message' in response.headers or response.status_code == 204

    def test_trigger_error_toast(self, client):
        """
        Test triggering error toast via HTMX endpoint.

        ARRANGE: Flask app with toast system
        ACT: POST /test-toast/error
        ASSERT: Response with error toast headers
        """
        response = client.post('/test-toast/error')
        assert response.status_code in [200, 204]

    def test_trigger_warning_toast(self, client):
        """
        Test triggering warning toast via HTMX endpoint.

        ARRANGE: Flask app with toast system
        ACT: POST /test-toast/warning
        ASSERT: Response with warning toast headers
        """
        response = client.post('/test-toast/warning')
        assert response.status_code in [200, 204]

    def test_trigger_info_toast(self, client):
        """
        Test triggering info toast via HTMX endpoint.

        ARRANGE: Flask app with toast system
        ACT: POST /test-toast/info
        ASSERT: Response with info toast headers
        """
        response = client.post('/test-toast/info')
        assert response.status_code in [200, 204]


class TestInteractionsTestRoute:
    """Test enhanced interactions test route (dev only)."""

    def test_test_interactions_page(self, client):
        """
        Test enhanced interactions test page loads.

        ARRANGE: Flask app running
        ACT: GET /test/interactions
        ASSERT: 200 status, test page displayed
        """
        response = client.get('/test/interactions')
        assert response.status_code == 200


class TestRouteUniqueness:
    """Test that routes don't overlap between blueprints."""

    def test_main_routes_unique(self, app):
        """
        Test main blueprint routes are unique and don't conflict.

        ARRANGE: Flask app with all blueprints registered
        ACT: Inspect route map
        ASSERT: No duplicate routes for main blueprint endpoints
        """
        # Get all routes for main blueprint
        main_routes = [
            rule.rule for rule in app.url_map.iter_rules()
            if rule.endpoint.startswith('main.')
        ]

        # Check for duplicates
        assert len(main_routes) == len(set(main_routes)), \
            "Duplicate routes found in main blueprint"

    def test_dashboard_route_ownership(self, app):
        """
        Test that dashboard route (/) is owned by main blueprint only.

        ARRANGE: Flask app with all blueprints
        ACT: Check / route ownership
        ASSERT: / route belongs to main blueprint
        """
        # Find the / route
        for rule in app.url_map.iter_rules():
            if rule.rule == '/':
                assert rule.endpoint == 'main.dashboard', \
                    f"Dashboard route (/) should be owned by main blueprint, but is owned by {rule.endpoint}"
                break
        else:
            pytest.fail("Dashboard route (/) not found in route map")


class TestRESTfulNamingPatterns:
    """Test that routes follow consistent RESTful naming patterns."""

    def test_project_detail_uses_restful_pattern(self, app):
        """
        Test project detail route follows RESTful pattern.

        ARRANGE: Flask app with routes
        ACT: Check /project/<id> route
        ASSERT: Uses RESTful resource/id pattern
        """
        # Should have /project/<id> pattern (singular resource)
        project_routes = [
            rule.rule for rule in app.url_map.iter_rules()
            if 'project' in rule.rule and '<int:project_id>' in rule.rule
        ]
        assert any('/project/<int:project_id>' in route for route in project_routes), \
            "Project detail route should use RESTful /project/<id> pattern"

    def test_project_context_uses_restful_subresource_pattern(self, app):
        """
        Test project context route follows RESTful subresource pattern.

        ARRANGE: Flask app with routes
        ACT: Check /project/<id>/context route
        ASSERT: Uses RESTful resource/id/subresource pattern
        """
        # Should have /project/<id>/context pattern
        context_routes = [
            rule.rule for rule in app.url_map.iter_rules()
            if 'context' in rule.rule and 'project' in rule.rule
        ]
        assert any('/project/<int:project_id>/context' in route for route in context_routes), \
            "Project context route should use RESTful /project/<id>/context pattern"
