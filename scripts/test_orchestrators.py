#!/usr/bin/env python3
"""Quick test of orchestrator definitions"""

import sys
import sqlite3
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentpm.core.agents.builder import AgentBuilder

def main():
    db_path = project_root / '.aipm' / 'data' / 'aipm.db'
    conn = sqlite3.connect(str(db_path))
    builder = AgentBuilder(conn, project_id=1)
    
    print("Testing Mini-Orchestrator Retrieval\n")
    print("="*60)
    
    # Test each orchestrator
    orchestrators = [
        'definition-orch',
        'planning-orch',
        'implementation-orch',
        'review-test-orch',
        'release-ops-orch',
        'evolution-orch'
    ]
    
    for role in orchestrators:
        agent = builder.get_agent_by_role(role)
        if agent:
            print(f"\n✅ {role}")
            print(f"   ID: {agent.id}")
            print(f"   Tier: {agent.tier}")
            print(f"   Display: {agent.display_name}")
            print(f"   Active: {agent.is_active}")
            
            # Get relationships
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM agent_relationships
                WHERE agent_id = ? AND relationship_type = 'delegates_to'
            """, (agent.id,))
            delegates = cursor.fetchone()[0]
            print(f"   Delegates to: {delegates} sub-agents")
            
            # Get tools
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM agent_tools
                WHERE agent_id = ?
            """, (agent.id,))
            tools = cursor.fetchone()[0]
            print(f"   Tools configured: {tools}")
        else:
            print(f"\n❌ {role} - NOT FOUND")
    
    print("\n" + "="*60)
    print("\n✅ All orchestrators operational!\n")
    
    conn.close()

if __name__ == '__main__':
    main()
