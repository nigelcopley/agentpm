#!/usr/bin/env python3
"""Visualize the complete orchestration flow"""

import sys
import sqlite3
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    db_path = project_root / '.aipm' / 'data' / 'aipm.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    print("\n" + "="*70)
    print("THREE-TIER ORCHESTRATION ARCHITECTURE")
    print("="*70 + "\n")
    
    # Get master orchestrator
    cursor = conn.execute("""
        SELECT id, role, display_name
        FROM agents
        WHERE orchestrator_type = 'master'
    """)
    master = cursor.fetchone()
    
    print(f"TIER 3: {master['display_name']} (id={master['id']})")
    print("        Routes work by artifact type to phase-specific orchestrators")
    print("")
    
    # Get mini orchestrators
    cursor = conn.execute("""
        SELECT id, role, display_name
        FROM agents
        WHERE orchestrator_type = 'mini'
        ORDER BY id
    """)
    mini_orchs = cursor.fetchall()
    
    print("TIER 2: Mini-Orchestrators (Phase-Specific)")
    for i, orch in enumerate(mini_orchs):
        is_last = (i == len(mini_orchs) - 1)
        prefix = "        └─" if is_last else "        ├─"
        
        print(f"{prefix} {orch['display_name']} (id={orch['id']})")
        
        # Get sub-agents
        cursor2 = conn.execute("""
            SELECT a.role, a.display_name
            FROM agent_relationships r
            JOIN agents a ON r.related_agent_id = a.id
            WHERE r.agent_id = ? AND r.relationship_type = 'delegates_to'
            ORDER BY a.role
        """, (orch['id'],))
        sub_agents = cursor2.fetchall()
        
        # Get tools
        cursor3 = conn.execute("""
            SELECT phase, tool_name, priority
            FROM agent_tools
            WHERE agent_id = ?
            ORDER BY phase, priority
        """, (orch['id'],))
        tools = cursor3.fetchall()
        
        indent = "           " if is_last else "        │  "
        
        print(f"{indent}   Delegates: {len(sub_agents)} sub-agents")
        print(f"{indent}   Tools: {len(tools)} MCP tools")
        print("")
    
    print("\nTIER 1: Sub-Agents (Single-Responsibility)")
    
    # Count sub-agents by orchestrator
    cursor = conn.execute("""
        SELECT COUNT(DISTINCT a.id) as count
        FROM agents a
        JOIN agent_relationships r ON a.id = r.related_agent_id
        WHERE r.relationship_type = 'delegates_to'
          AND a.tier = 1
    """)
    sub_count = cursor.fetchone()['count']
    
    print(f"        {sub_count} specialized sub-agents")
    print("        Examples: intent-triage, code-implementer, test-runner, etc.")
    print("")
    
    # Show artifact flow
    print("="*70)
    print("ARTIFACT FLOW (Phase by Phase)")
    print("="*70 + "\n")
    
    flow = [
        ("request.raw", "definition-orch", "workitem.ready", "D1: definition-complete"),
        ("workitem.ready", "planning-orch", "plan.snapshot", "P1: plan-complete"),
        ("plan.snapshot", "implementation-orch", "build.bundle", "I1: implementation-complete"),
        ("build.bundle", "review-test-orch", "review.approved", "R1: review-approved"),
        ("review.approved", "release-ops-orch", "release.deployed", "O1: operability-ready"),
        ("telemetry.snapshot", "evolution-orch", "evolution.backlog_delta", "E1: evolution-planned")
    ]
    
    for i, (in_artifact, orch, out_artifact, gate) in enumerate(flow, 1):
        print(f"{i}. {in_artifact}")
        print(f"   └─> {orch}")
        print(f"       ├─ Gate: {gate}")
        print(f"       └─> Produces: {out_artifact}")
        print("")
    
    # Show statistics
    print("="*70)
    print("STATISTICS")
    print("="*70 + "\n")
    
    stats = [
        ("Total Agents", "SELECT COUNT(*) FROM agents WHERE id >= 32"),
        ("Master Orchestrators", "SELECT COUNT(*) FROM agents WHERE orchestrator_type = 'master'"),
        ("Mini Orchestrators", "SELECT COUNT(*) FROM agents WHERE orchestrator_type = 'mini'"),
        ("Sub-Agents (Tier 1)", "SELECT COUNT(*) FROM agents WHERE tier = 1 AND id >= 33"),
        ("Total Relationships", "SELECT COUNT(*) FROM agent_relationships WHERE agent_id >= 32"),
        ("Delegation Relationships", "SELECT COUNT(*) FROM agent_relationships WHERE relationship_type = 'delegates_to' AND agent_id >= 32"),
        ("Reporting Relationships", "SELECT COUNT(*) FROM agent_relationships WHERE relationship_type = 'reports_to' AND agent_id >= 32"),
        ("Total Tool Assignments", "SELECT COUNT(*) FROM agent_tools WHERE agent_id >= 32"),
    ]
    
    for label, query in stats:
        cursor = conn.execute(query)
        count = cursor.fetchone()[0]
        print(f"  {label:30s}: {count}")
    
    print("\n" + "="*70 + "\n")
    
    conn.close()

if __name__ == '__main__':
    main()
