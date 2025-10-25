#!/usr/bin/env python
"""
Test Flask routes for Phase 1 implementation.

Tests:
1. Agents view (/agents) - Should load without 500 errors
2. Work item summaries timeline (/work-item/<id>/summaries) - Should display session history
"""

from agentpm.web.app import app

def test_agents_route():
    """Test agents view loads without errors"""
    with app.test_client() as client:
        response = client.get('/agents')
        print(f"\n✅ /agents route status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Agents view loads successfully (no 500 error)")
            # Check for expected content
            html = response.data.decode('utf-8')
            if 'Total Agents' in html:
                print("✅ Agents dashboard structure present")
            if 'agents_list' in html or 'No agents configured' in html:
                print("✅ Agents list or empty state present")
        else:
            print(f"❌ Agents view failed with status {response.status_code}")
            print(response.data.decode('utf-8')[:500])

def test_work_item_summaries_route():
    """Test work item summaries timeline"""
    with app.test_client() as client:
        # Test with work item 7 (has 1 summary according to DB query)
        response = client.get('/work-item/7/summaries')
        print(f"\n✅ /work-item/7/summaries route status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Summaries timeline loads successfully")
            html = response.data.decode('utf-8')

            if 'Session History' in html:
                print("✅ Session History header present")
            if 'Total Sessions' in html:
                print("✅ Summary statistics present")
            if 'Session Timeline' in html:
                print("✅ Timeline section present")
        else:
            print(f"❌ Summaries timeline failed with status {response.status_code}")
            print(response.data.decode('utf-8')[:500])

def test_work_item_with_summaries_link():
    """Test that work item detail page has the session history link"""
    with app.test_client() as client:
        response = client.get('/work-item/7')
        print(f"\n✅ /work-item/7 route status: {response.status_code}")

        if response.status_code == 200:
            html = response.data.decode('utf-8')
            if '/work-item/7/summaries' in html and 'View Session History' in html:
                print("✅ Session History link present on work item detail page")
            else:
                print("⚠️ Session History link not found on work item detail page")

if __name__ == '__main__':
    print("="*60)
    print("Testing Flask Dashboard Phase 1 Implementation")
    print("="*60)

    test_agents_route()
    test_work_item_summaries_route()
    test_work_item_with_summaries_link()

    print("\n" + "="*60)
    print("✅ All Phase 1 tests-BAK completed!")
    print("="*60)
    print("\nTo start the Flask app:")
    print("  flask --app agentpm.web.app run")
    print("\nThen visit:")
    print("  http://localhost:5000/agents")
    print("  http://localhost:5000/work-item/7/summaries")
