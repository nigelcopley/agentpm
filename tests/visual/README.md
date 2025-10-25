# Visual Regression Testing

Playwright-based visual regression tests for APM (Agent Project Manager) web interface.

## Setup

**Prerequisites:**
- Playwright installed: `pip install playwright pytest-playwright`
- Browsers installed: `playwright install chromium`
- Flask app running on port 5002

## Running Tests

**Start Flask server (Terminal 1):**
```bash
FLASK_PORT=5002 python -m agentpm.web.app
```

**Run visual tests (Terminal 2):**
```bash
# All visual tests (30+ screenshots)
pytest tests/visual/ -m visual -v

# Specific test file
pytest tests/visual/test_dashboard_routes_visual.py -v
pytest tests/visual/test_work_items_routes_visual.py -v
pytest tests/visual/test_tasks_routes_visual.py -v
pytest tests/visual/test_context_documents_visual.py -v
pytest tests/visual/test_system_routes_visual.py -v

# Specific viewport
pytest tests/visual/ -m visual -k "desktop" -v
pytest tests/visual/ -m visual -k "tablet" -v
pytest tests/visual/ -m visual -k "mobile" -v

# Specific route
pytest tests/visual/ -m visual -k "dashboard" -v
pytest tests/visual/ -m visual -k "work_items" -v

# Interactive tests only (desktop-specific functionality)
pytest tests/visual/ -k "Interactive" -v
```

## Directory Structure

```
tests/visual/
├── conftest.py                           # Fixtures and helpers
├── screenshots/
│   ├── desktop/                          # Desktop screenshots (1920x1080)
│   ├── tablet/                           # Tablet screenshots (768x1024)
│   └── mobile/                           # Mobile screenshots (375x667)
├── test_dashboard_routes_visual.py       # / and /overview
├── test_work_items_routes_visual.py      # /work-items and /work-items/<id>
├── test_tasks_routes_visual.py           # /tasks and /tasks/<id>
├── test_context_documents_visual.py      # /context and /documents
└── test_system_routes_visual.py          # /search, /agents, /system/health
```

## Test Coverage

**10 Priority Routes** tested across 3 viewports (30+ total screenshot captures):

1. **Dashboard**: `/` - Main landing page with metrics
2. **Work Items List**: `/work-items` - Complex filtering, HTMX
3. **Work Item Detail**: `/work-items/<id>` - Detail view with tasks
4. **Tasks List**: `/tasks` - Task management with filtering
5. **Task Detail**: `/tasks/<id>` - Task detail view
6. **Context List**: `/context` - Context management
7. **Documents List**: `/documents` - Document management
8. **Search**: `/search` - Search interface with query params
9. **Agents**: `/agents` - Agent directory
10. **System Health**: `/system/health` - Health dashboard

## Viewport Sizes

- **Desktop**: 1920x1080 (Full HD)
- **Tablet**: 768x1024 (iPad portrait)
- **Mobile**: 375x667 (iPhone SE)

## Writing Visual Tests

```python
@pytest.mark.visual
@pytest.mark.parametrize("viewport", ["desktop", "tablet", "mobile"])
def test_dashboard_visual(page, viewport, visual_helper):
    """Test dashboard renders correctly across viewports."""
    visual_helper.navigate_and_capture('/', 'dashboard', viewport)
```

## First Run

First run creates baseline screenshots. **Review these manually** to ensure they represent the correct appearance before considering them "truth."

## Troubleshooting

**Flask not running:**
```
Error: ERR_CONNECTION_REFUSED
Solution: Start Flask server on port 5002
```

**Flaky tests:**
- Increase wait times in conftest.py
- Check for animations not being disabled
- Verify dynamic content is properly masked
