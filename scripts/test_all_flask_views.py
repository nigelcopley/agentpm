#!/usr/bin/env python3
"""
Test all Flask views with realistic parameters.

Iterates over every registered route and attempts to issue a GET request using
representative data so we surface genuine 404/500 errors instead of noise from
placeholder IDs. Routes that do not accept GET or require unsupported parameters
are skipped with an explanatory note.

Usage:
    python3 scripts/test_all_flask_views.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from flask import url_for

# Add project root to path before importing app
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentpm.web.app import app, get_database_service  # noqa: E402


SKIP_ENDPOINTS = {
    "config.rules_toggle",  # GET intentionally returns 404 (HTMX POST endpoint)
}


def _first_value(conn: sqlite3.Connection, table: str, column: str = "id") -> Optional[Any]:
    """Return the first value for the given column, or None if the table is empty."""
    try:
        row = conn.execute(
            f"SELECT {column} FROM {table} ORDER BY ROWID LIMIT 1"
        ).fetchone()
    except sqlite3.Error:
        return None

    if not row:
        return None

    # sqlite3.Row supports both index and key access
    return row[0] if not isinstance(row, sqlite3.Row) else row[column]


def _gather_sample_parameters() -> Dict[str, Any]:
    """
    Collect representative parameter values for dynamic routes.

    Pulls the first available IDs from core tables and discovers a real context
    file path so that preview/download routes can be exercised.
    """
    samples: Dict[str, Any] = {}
    db = get_database_service()

    with db.connect() as conn:
        samples["project_id"] = _first_value(conn, "projects")
        samples["work_item_id"] = _first_value(conn, "work_items")
        samples["task_id"] = _first_value(conn, "tasks")
        samples["agent_id"] = _first_value(conn, "agents")
        samples["rule_id"] = _first_value(conn, "rules")
        samples["context_id"] = _first_value(conn, "contexts")
        samples["session_id"] = _first_value(conn, "sessions", "session_id")
        samples["idea_id"] = _first_value(conn, "ideas")
        samples["document_id"] = _first_value(conn, "document_references")

    # Additional parameter defaults
    samples["toast_type"] = "info"
    samples["entity_type"] = "project"
    samples["work_item_type"] = "feature"
    samples["filter_value"] = "all"

    context_dir = Path(".aipm/contexts")
    if context_dir.exists():
        for file_path in context_dir.rglob("*"):
            if file_path.is_file():
                samples["filepath"] = file_path.relative_to(context_dir).as_posix()
                break

    return samples


def _build_route(rule, samples: Dict[str, Any]) -> Optional[str]:
    """
    Attempt to construct a URL for the given rule using the provided samples.

    Returns the URL or None if required parameters are missing.
    """
    values: Dict[str, Any] = {}

    for argument in rule.arguments:
        if argument in samples and samples[argument] is not None:
            values[argument] = samples[argument]
            continue

        if argument.endswith("_id"):
            base = argument[:-3]
            if base in samples and samples[base] is not None:
                values[argument] = samples[base]
                continue

        # Could not satisfy this parameter
        return None

    with app.test_request_context():
        try:
            return url_for(rule.endpoint, **values)
        except Exception:
            return None


def test_all_views() -> bool:
    """Exercise all GET-able Flask routes and report successes/failures."""

    print("🧪 Testing All Flask Views\n")
    print("=" * 60)

    samples = _gather_sample_parameters()

    with app.test_client() as client:
        routes = [
            rule for rule in app.url_map.iter_rules()
            if rule.endpoint != "static"
        ]

        total = len(routes)
        passed = 0
        failed = 0
        skipped = 0
        errors = []

        for index, rule in enumerate(sorted(routes, key=lambda r: r.rule), 1):
            endpoint = rule.endpoint

            if endpoint in SKIP_ENDPOINTS:
                skipped += 1
                print(f"[{index}/{total}] ⏭️  SKIP              {endpoint:40} {rule.rule} (explicit skip)")
                continue

            if "GET" not in rule.methods:
                skipped += 1
                print(f"[{index}/{total}] ⏭️  SKIP              {endpoint:40} {rule.rule} (no GET handler)")
                continue

            test_route = _build_route(rule, samples) if rule.arguments else rule.rule
            if not test_route:
                skipped += 1
                print(f"[{index}/{total}] ⏭️  SKIP              {endpoint:40} {rule.rule} (missing sample data)")
                continue

            response = client.get(test_route)

            if response.status_code == 200:
                status = "✅ PASS"
                passed += 1
            elif response.status_code in (302, 304):
                status = "✅ REDIRECT"
                passed += 1
            elif response.status_code == 404:
                status = "⚠️  404"
                failed += 1
                errors.append({
                    "endpoint": endpoint,
                    "route": test_route,
                    "status": response.status_code,
                })
            elif response.status_code == 500:
                status = "❌ ERROR 500"
                failed += 1
                errors.append({
                    "endpoint": endpoint,
                    "route": test_route,
                    "status": response.status_code,
                })
            else:
                status = f"⚠️  {response.status_code}"
                failed += 1
                errors.append({
                    "endpoint": endpoint,
                    "route": test_route,
                    "status": response.status_code,
                })

            print(f"[{index}/{total}] {status:20} {endpoint:40} {test_route}")

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed, {skipped} skipped (out of {total} total)")

    if errors:
        print(f"\n❌ {len(errors)} Errors Found:\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error['endpoint']} ({error['route']})")
            print(f"   Status: {error['status']}\n")
    else:
        print("\n✅ All tested GET views responded successfully!")

    return failed == 0


if __name__ == "__main__":
    success = test_all_views()
    sys.exit(0 if success else 1)
