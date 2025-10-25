#!/usr/bin/env python3
"""
Debug Route Issues

Simple script to test individual routes and see specific errors.
"""

import requests
import sys

def test_route(url, description):
    """Test a single route and show detailed error info"""
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {len(response.content)}")
        
        if response.status_code == 500:
            print("❌ 500 Error - Server Error")
            # Try to extract error info from HTML
            content = response.text
            if "TypeError" in content:
                print("Error Type: TypeError")
            elif "AttributeError" in content:
                print("Error Type: AttributeError")
            elif "ImportError" in content:
                print("Error Type: ImportError")
            else:
                print("Error Type: Unknown")
        elif response.status_code == 200:
            print("✅ Success")
        else:
            print(f"⚠️  Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔥 Request Error: {e}")

def main():
    """Test problematic routes"""
    base_url = "http://127.0.0.1:5000"
    
    print("🚀 Debugging Route Issues")
    print("=" * 50)
    
    # Test the routes that were failing
    test_routes = [
        (f"{base_url}/projects/1", "Project Detail"),
        (f"{base_url}/projects/1/edit", "Project Edit Form"),
        (f"{base_url}/projects/1/settings", "Project Settings"),
        (f"{base_url}/work-items/1/edit", "Work Item Edit Form"),
        (f"{base_url}/work-items/1/context", "Work Item Context"),
        (f"{base_url}/work-items/1/tasks", "Work Item Tasks"),
        (f"{base_url}/tasks/1/edit", "Task Edit Form"),
        (f"{base_url}/tasks/1/dependencies", "Task Dependencies"),
        (f"{base_url}/tasks/1/blockers", "Task Blockers"),
        (f"{base_url}/agents/1", "Agent Detail"),
        (f"{base_url}/agents/1/edit", "Agent Edit Form"),
        (f"{base_url}/ideas/1/edit", "Idea Edit Form"),
        (f"{base_url}/sessions", "Sessions List"),
        (f"{base_url}/sessions/timeline", "Sessions Timeline"),
        (f"{base_url}/research/evidence", "Evidence Sources"),
        (f"{base_url}/research/events", "Events Timeline"),
        (f"{base_url}/research/documents", "Document References"),
        (f"{base_url}/contexts", "Contexts List"),
        (f"{base_url}/contexts/1", "Context Detail"),
        (f"{base_url}/system/health", "System Health"),
        (f"{base_url}/system/database", "Database Metrics"),
        (f"{base_url}/system/workflow", "Workflow Visualization"),
        (f"{base_url}/system/context-files", "Context Files Browser"),
        (f"{base_url}/search", "Search Results Page"),
        (f"{base_url}/api/projects/1", "API Project Detail"),
        (f"{base_url}/api/contexts", "API Contexts List"),
        (f"{base_url}/dev/test-toasts", "Test Toasts Page"),
        (f"{base_url}/dev/test/interactions", "Test Interactions Page"),
    ]
    
    for url, description in test_routes:
        test_route(url, description)
    
    print("\n" + "=" * 50)
    print("🏁 Debug Complete")

if __name__ == "__main__":
    main()
