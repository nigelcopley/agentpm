#!/usr/bin/env python3
"""
Route Testing Script for APM (Agent Project Manager) Web Interface
Tests all routes and identifies issues (missing templates, 500 errors, etc.)
"""

import requests
import sys
from urllib.parse import urljoin

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

BASE_URL = "http://127.0.0.1:5002"

# All routes from WI-141 enhanced routes + standard routes
ROUTES_TO_TEST = [
    # Dashboard
    ("/", "Dashboard"),

    # Work Items
    ("/work-items", "Work Items List"),
    ("/work-items/1", "Work Item Detail (ID=1)"),

    # Tasks
    ("/tasks", "Tasks List"),
    ("/tasks/1", "Task Detail (ID=1)"),

    # Projects
    ("/projects", "Projects List"),
    ("/projects/1", "Project Detail (ID=1)"),
    ("/projects/1/settings", "Project Settings"),

    # Agents
    ("/agents", "Agents List"),
    ("/agents/1", "Agent Detail (ID=1)"),

    # Rules
    ("/rules", "Rules List"),
    ("/rules/1", "Rule Detail (ID=1)"),

    # Documents
    ("/documents", "Documents List"),
    ("/research/documents", "Research Documents"),

    # Evidence
    ("/evidence", "Evidence List"),
    ("/research/evidence", "Research Evidence"),

    # Search
    ("/search", "Search Page"),
    ("/search?q=test", "Search Results"),

    # Contexts
    ("/contexts", "Contexts List"),
    ("/contexts/1", "Context Detail (ID=1)"),

    # Ideas
    ("/ideas", "Ideas List"),
    ("/ideas/1", "Idea Detail (ID=1)"),

    # Sessions
    ("/sessions", "Sessions List"),
    ("/sessions/1", "Session Detail (ID=1)"),

    # Events
    ("/events", "Events List"),

    # System
    ("/system/database", "Database Metrics"),
    ("/workflow", "Workflow Visualization"),
    ("/system/health", "Health Check"),
]

def test_route(url, description):
    """Test a single route and return status info"""
    full_url = urljoin(BASE_URL, url)

    try:
        response = requests.get(full_url, timeout=5)
        status_code = response.status_code

        # Analyze response
        issue_type = None
        issue_details = None

        if status_code == 200:
            # Check for common error patterns in HTML
            html = response.text.lower()

            if "templatenotfound" in html or "template not found" in html:
                issue_type = "TEMPLATE_MISSING"
                # Extract template name from error
                if "jinja2.exceptions.templatenotfound" in html:
                    issue_details = "Jinja2 template not found in response"
            elif ("internal server error" in html or 
                  "500 internal server error" in html or
                  "jinja2.exceptions" in html or
                  "traceback" in html or
                  "exception" in html and "traceback" in html):
                issue_type = "SERVER_ERROR"
                issue_details = "Server error detected in page content"
            elif len(html) < 100:
                issue_type = "EMPTY_RESPONSE"
                issue_details = f"Response too small ({len(html)} bytes)"

            return {
                "url": url,
                "description": description,
                "status_code": status_code,
                "success": issue_type is None,
                "issue_type": issue_type,
                "issue_details": issue_details,
                "response_size": len(response.text)
            }

        elif status_code == 404:
            return {
                "url": url,
                "description": description,
                "status_code": status_code,
                "success": False,
                "issue_type": "NOT_FOUND",
                "issue_details": "Route not registered in Flask app",
                "response_size": len(response.text)
            }

        elif status_code == 500:
            # Try to extract error info
            import re
            html = response.text
            issue_details = "Internal server error"

            if "TemplateNotFound" in html:
                # Extract template name
                match = re.search(r"TemplateNotFound:\s*([^\n<]+)", html)
                if match:
                    issue_details = f"Missing template: {match.group(1).strip()}"
            elif "AttributeError" in html:
                match = re.search(r"AttributeError:\s*([^\n<]+)", html)
                if match:
                    issue_details = f"Attribute error: {match.group(1).strip()}"
            elif "KeyError" in html:
                match = re.search(r"KeyError:\s*([^\n<]+)", html)
                if match:
                    issue_details = f"Key error: {match.group(1).strip()}"

            return {
                "url": url,
                "description": description,
                "status_code": status_code,
                "success": False,
                "issue_type": "SERVER_ERROR",
                "issue_details": issue_details,
                "response_size": len(response.text)
            }

        else:
            return {
                "url": url,
                "description": description,
                "status_code": status_code,
                "success": False,
                "issue_type": "UNEXPECTED_STATUS",
                "issue_details": f"HTTP {status_code}",
                "response_size": len(response.text)
            }

    except requests.exceptions.ConnectionError:
        return {
            "url": url,
            "description": description,
            "status_code": None,
            "success": False,
            "issue_type": "CONNECTION_ERROR",
            "issue_details": f"Cannot connect to {BASE_URL} - is Flask running?",
            "response_size": 0
        }

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "description": description,
            "status_code": None,
            "success": False,
            "issue_type": "TIMEOUT",
            "issue_details": "Request timed out after 5 seconds",
            "response_size": 0
        }

    except Exception as e:
        return {
            "url": url,
            "description": description,
            "status_code": None,
            "success": False,
            "issue_type": "EXCEPTION",
            "issue_details": str(e),
            "response_size": 0
        }

def print_result(result):
    """Print a formatted result"""
    if result["success"]:
        print(f"{Colors.GREEN}✓{Colors.RESET} {result['description']:40} {Colors.GREEN}200 OK{Colors.RESET} ({result['response_size']:,} bytes)")
    else:
        status = result['status_code'] or "N/A"
        issue = result['issue_type']
        details = result['issue_details']

        if result['issue_type'] == "CONNECTION_ERROR":
            print(f"{Colors.RED}✗{Colors.RESET} {result['description']:40} {Colors.RED}CONNECTION FAILED{Colors.RESET}")
            print(f"  {Colors.YELLOW}→ {details}{Colors.RESET}")
        elif result['issue_type'] == "NOT_FOUND":
            print(f"{Colors.YELLOW}✗{Colors.RESET} {result['description']:40} {Colors.YELLOW}404 NOT FOUND{Colors.RESET}")
            print(f"  {Colors.YELLOW}→ {details}{Colors.RESET}")
        elif result['issue_type'] == "SERVER_ERROR":
            print(f"{Colors.RED}✗{Colors.RESET} {result['description']:40} {Colors.RED}500 ERROR{Colors.RESET}")
            print(f"  {Colors.RED}→ {details}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}✗{Colors.RESET} {result['description']:40} {Colors.YELLOW}{status} {issue}{Colors.RESET}")
            print(f"  {Colors.YELLOW}→ {details}{Colors.RESET}")

def main():
    """Main testing function"""
    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}APM (Agent Project Manager) Web Route Testing{Colors.RESET}")
    print(f"{Colors.CYAN}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.CYAN}Total Routes: {len(ROUTES_TO_TEST)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

    results = []

    # Test all routes
    for url, description in ROUTES_TO_TEST:
        result = test_route(url, description)
        results.append(result)
        print_result(result)

    # Summary
    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}SUMMARY{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    failed_count = total - success_count

    print(f"Total Routes Tested: {total}")
    print(f"{Colors.GREEN}Successful (200 OK): {success_count} ({success_count/total*100:.1f}%){Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed_count} ({failed_count/total*100:.1f}%){Colors.RESET}\n")

    # Group failures by type
    if failed_count > 0:
        print(f"{Colors.YELLOW}FAILURES BY TYPE:{Colors.RESET}\n")

        issue_types = {}
        for r in results:
            if not r["success"]:
                issue_type = r["issue_type"]
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(r)

        for issue_type, failures in issue_types.items():
            print(f"{Colors.YELLOW}{issue_type}:{Colors.RESET} {len(failures)} routes")
            for f in failures:
                print(f"  • {f['url']:30} - {f['issue_details']}")
            print()

    # Recommendations
    if failed_count > 0:
        print(f"{Colors.CYAN}RECOMMENDATIONS:{Colors.RESET}\n")

        for issue_type, failures in issue_types.items():
            if issue_type == "NOT_FOUND":
                print(f"{Colors.YELLOW}404 Routes:{Colors.RESET} Add route handlers in Flask blueprints")
            elif issue_type == "SERVER_ERROR":
                print(f"{Colors.RED}500 Errors:{Colors.RESET} Check error logs and fix template/backend issues")
                for f in failures:
                    if "Missing template" in f["issue_details"]:
                        template = f["issue_details"].replace("Missing template: ", "")
                        print(f"  → Create template: {template}")
            elif issue_type == "CONNECTION_ERROR":
                print(f"{Colors.RED}Connection Failed:{Colors.RESET} Start Flask server: python3 -m flask --app agentpm.web.app run --port 5002")
            print()

    # Exit code
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    main()
