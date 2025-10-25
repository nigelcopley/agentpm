#!/usr/bin/env python3
"""
Route Response Testing Script

Tests all new blueprint routes to ensure they return proper HTTP responses,
headers, and content. This validates the route refactor implementation.
"""

import requests
import time
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RouteTest:
    """Test case for a route"""
    method: str
    path: str
    expected_status: int
    expected_content_type: str = None
    description: str = ""

class RouteTester:
    """Test all routes for proper responses"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def test_route(self, test: RouteTest) -> Dict:
        """Test a single route"""
        url = f"{self.base_url}{test.path}"
        
        try:
            if test.method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif test.method.upper() == "POST":
                response = self.session.post(url, timeout=10)
            elif test.method.upper() == "PUT":
                response = self.session.put(url, timeout=10)
            else:
                return {
                    "test": test,
                    "status": "SKIP",
                    "error": f"Unsupported method: {test.method}"
                }
            
            result = {
                "test": test,
                "status": "PASS" if response.status_code == test.expected_status else "FAIL",
                "actual_status": response.status_code,
                "expected_status": test.expected_status,
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content),
                "response_time": response.elapsed.total_seconds(),
                "headers": dict(response.headers)
            }
            
            # Check content type if specified
            if test.expected_content_type:
                if test.expected_content_type in result["content_type"]:
                    result["content_type_match"] = True
                else:
                    result["content_type_match"] = False
                    result["status"] = "FAIL"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "test": test,
                "status": "ERROR",
                "error": str(e)
            }
    
    def run_all_tests(self) -> List[Dict]:
        """Run all route tests"""
        print("🧪 Testing All New Blueprint Routes...")
        print("=" * 60)
        
        # Define all routes to test
        tests = [
            # Dashboard Routes
            RouteTest("GET", "/", 200, "text/html", "Main dashboard"),
            RouteTest("GET", "/dashboard", 200, "text/html", "Explicit dashboard"),
            RouteTest("GET", "/overview", 200, "text/html", "Project overview"),
            
            # Projects Routes
            RouteTest("GET", "/projects", 200, "text/html", "Projects list"),
            RouteTest("GET", "/projects/1", 200, "text/html", "Project detail"),
            RouteTest("GET", "/projects/1/edit", 200, "text/html", "Project edit form"),
            RouteTest("GET", "/projects/1/settings", 200, "text/html", "Project settings"),
            RouteTest("GET", "/projects/1/analytics", 200, "text/html", "Project analytics"),
            RouteTest("GET", "/projects/1/context", 200, "text/html", "Project context"),
            
            # Work Items Routes
            RouteTest("GET", "/work-items", 200, "text/html", "Work items list"),
            RouteTest("GET", "/work-items/1", 200, "text/html", "Work item detail"),
            RouteTest("GET", "/work-items/1/edit", 200, "text/html", "Work item edit form"),
            RouteTest("GET", "/work-items/1/summaries", 200, "text/html", "Work item summaries"),
            RouteTest("GET", "/work-items/1/context", 200, "text/html", "Work item context"),
            RouteTest("GET", "/work-items/1/tasks", 200, "text/html", "Work item tasks"),
            
            # Tasks Routes
            RouteTest("GET", "/tasks", 200, "text/html", "Tasks list"),
            RouteTest("GET", "/tasks/1", 200, "text/html", "Task detail"),
            RouteTest("GET", "/tasks/1/edit", 200, "text/html", "Task edit form"),
            RouteTest("GET", "/tasks/1/dependencies", 200, "text/html", "Task dependencies"),
            RouteTest("GET", "/tasks/1/blockers", 200, "text/html", "Task blockers"),
            
            # Agents Routes
            RouteTest("GET", "/agents", 200, "text/html", "Agents list"),
            RouteTest("GET", "/agents/1", 200, "text/html", "Agent detail"),
            RouteTest("GET", "/agents/1/edit", 200, "text/html", "Agent edit form"),
            RouteTest("GET", "/agents/generate", 200, "text/html", "Agent generation form"),
            
            # Rules Routes
            RouteTest("GET", "/rules", 200, "text/html", "Rules list"),
            RouteTest("GET", "/rules/1", 200, "text/html", "Rule detail"),
            RouteTest("GET", "/rules/1/edit", 200, "text/html", "Rule edit form"),
            
            # Ideas Routes
            RouteTest("GET", "/ideas", 200, "text/html", "Ideas list"),
            RouteTest("GET", "/ideas/1", 200, "text/html", "Idea detail"),
            RouteTest("GET", "/ideas/1/edit", 200, "text/html", "Idea edit form"),
            
            # Sessions Routes
            RouteTest("GET", "/sessions", 200, "text/html", "Sessions list"),
            RouteTest("GET", "/sessions/test-session", 200, "text/html", "Session detail"),
            RouteTest("GET", "/sessions/timeline", 200, "text/html", "Sessions timeline"),
            
            # Research Routes
            RouteTest("GET", "/research/evidence", 200, "text/html", "Evidence sources"),
            RouteTest("GET", "/research/events", 200, "text/html", "Events timeline"),
            RouteTest("GET", "/research/documents", 200, "text/html", "Document references"),
            
            # Contexts Routes
            RouteTest("GET", "/contexts", 200, "text/html", "Contexts list"),
            RouteTest("GET", "/contexts/1", 200, "text/html", "Context detail"),
            
            # System Routes
            RouteTest("GET", "/system/health", 200, "text/html", "System health"),
            RouteTest("GET", "/system/database", 200, "text/html", "Database metrics"),
            RouteTest("GET", "/system/workflow", 200, "text/html", "Workflow visualization"),
            RouteTest("GET", "/system/context-files", 200, "text/html", "Context files browser"),
            
            # Search Routes
            RouteTest("GET", "/search", 200, "text/html", "Search results page"),
            RouteTest("GET", "/search?q=test", 200, "text/html", "Search with query"),
            
            # API Routes
            RouteTest("GET", "/api/projects", 200, "application/json", "API projects list"),
            RouteTest("GET", "/api/projects/1", 200, "application/json", "API project detail"),
            RouteTest("GET", "/api/work-items", 200, "application/json", "API work items list"),
            RouteTest("GET", "/api/work-items/1", 200, "application/json", "API work item detail"),
            RouteTest("GET", "/api/tasks", 200, "application/json", "API tasks list"),
            RouteTest("GET", "/api/tasks/1", 200, "application/json", "API task detail"),
            RouteTest("GET", "/api/agents", 200, "application/json", "API agents list"),
            RouteTest("GET", "/api/rules", 200, "application/json", "API rules list"),
            RouteTest("GET", "/api/ideas", 200, "application/json", "API ideas list"),
            RouteTest("GET", "/api/sessions", 200, "application/json", "API sessions list"),
            RouteTest("GET", "/api/contexts", 200, "application/json", "API contexts list"),
            RouteTest("GET", "/api/search", 400, "application/json", "API search (no query)"),
            RouteTest("GET", "/api/search?q=test", 200, "application/json", "API search with query"),
            
            # Dev Routes
            RouteTest("GET", "/dev/test-toasts", 200, "text/html", "Test toasts page"),
            RouteTest("GET", "/dev/test-toast/success", 200, "text/html", "Test success toast"),
            RouteTest("GET", "/dev/test-toast/error", 200, "text/html", "Test error toast"),
            RouteTest("GET", "/dev/test/interactions", 200, "text/html", "Test interactions page"),
            
            # Redirect Routes (should redirect)
            RouteTest("GET", "/project/1", 302, None, "Legacy project detail redirect"),
            RouteTest("GET", "/project/1/context", 302, None, "Legacy project context redirect"),
            RouteTest("GET", "/project/1/settings", 302, None, "Legacy project settings redirect"),
            RouteTest("GET", "/work-item/1", 302, None, "Legacy work item detail redirect"),
            RouteTest("GET", "/work-item/1/summaries", 302, None, "Legacy work item summaries redirect"),
            RouteTest("GET", "/task/1", 302, None, "Legacy task detail redirect"),
            RouteTest("GET", "/idea/1", 302, None, "Legacy idea detail redirect"),
            RouteTest("GET", "/session/test-session", 302, None, "Legacy session detail redirect"),
            RouteTest("GET", "/context/1", 302, None, "Legacy context detail redirect"),
            RouteTest("GET", "/health", 302, None, "Legacy health redirect"),
            RouteTest("GET", "/workflow", 302, None, "Legacy workflow redirect"),
            RouteTest("GET", "/context-files", 302, None, "Legacy context files redirect"),
            
            # 404 Tests
            RouteTest("GET", "/nonexistent", 404, None, "Non-existent route"),
            RouteTest("GET", "/projects/99999", 404, None, "Non-existent project"),
            RouteTest("GET", "/work-items/99999", 404, None, "Non-existent work item"),
            RouteTest("GET", "/tasks/99999", 404, None, "Non-existent task"),
        ]
        
        # Run tests
        for i, test in enumerate(tests, 1):
            print(f"[{i:2d}/{len(tests)}] Testing {test.method} {test.path} - {test.description}")
            result = self.test_route(test)
            self.results.append(result)
            
            # Print result
            if result["status"] == "PASS":
                print(f"    ✅ {result['actual_status']} - {result['response_time']:.3f}s")
            elif result["status"] == "FAIL":
                print(f"    ❌ Expected {result['expected_status']}, got {result['actual_status']}")
            elif result["status"] == "ERROR":
                print(f"    🔥 Error: {result['error']}")
            else:
                print(f"    ⏭️  {result['status']}: {result.get('error', '')}")
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        errors = len([r for r in self.results if r["status"] == "ERROR"])
        skipped = len([r for r in self.results if r["status"] == "SKIP"])
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed:  {passed}")
        print(f"❌ Failed:  {failed}")
        print(f"🔥 Errors:  {errors}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0 or errors > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if result["status"] in ["FAIL", "ERROR"]:
                    test = result["test"]
                    print(f"  {test.method} {test.path} - {result.get('error', f'Expected {result.get("expected_status")}, got {result.get("actual_status")}')}")
        
        return passed == total

def main():
    """Main test runner"""
    print("🚀 Starting Route Response Tests")
    print("Testing Flask app on http://127.0.0.1:5000")
    print()
    
    # Wait a moment for Flask app to be ready
    print("⏳ Waiting for Flask app to be ready...")
    time.sleep(2)
    
    tester = RouteTester()
    results = tester.run_all_tests()
    success = tester.print_summary()
    
    if success:
        print("\n🎉 All routes are working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Some routes have issues that need fixing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
