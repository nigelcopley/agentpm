#!/usr/bin/env python3
"""
Agent Builder API Demo

Demonstrates programmatic agent definition using the AgentBuilder API.
Creates a sample three-tier agent architecture with relationships and tools.

Usage:
    python examples/agent_builder_demo.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentpm.core.agents.builder import AgentBuilder, create_orchestrator_agent


def setup_demo_database():
    """Create in-memory demo database with migration_0014 schema"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Apply migration_0014 schema (simplified for demo)
    conn.executescript("""
        CREATE TABLE agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            sop_content TEXT,
            capabilities TEXT DEFAULT '[]',
            is_active INTEGER DEFAULT 1,
            agent_type TEXT,
            file_path TEXT,
            generated_at TIMESTAMP,
            tier INTEGER,
            last_used_at TIMESTAMP,
            metadata TEXT DEFAULT '{}',
            execution_mode TEXT DEFAULT 'parallel',
            symbol_mode INTEGER DEFAULT 0,
            orchestrator_type TEXT,
            agent_file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE agent_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            related_agent_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (related_agent_id) REFERENCES agents(id),
            UNIQUE(agent_id, related_agent_id, relationship_type)
        );

        CREATE TABLE agent_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            priority INTEGER DEFAULT 1,
            config TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            UNIQUE(agent_id, phase, tool_name)
        );

        CREATE TABLE agent_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            scenario_name TEXT NOT NULL,
            scenario_description TEXT,
            category TEXT,
            input_context TEXT NOT NULL,
            expected_output TEXT NOT NULL,
            success_criteria TEXT,
            edge_cases TEXT DEFAULT '[]',
            effectiveness_score REAL,
            last_referenced_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        );
    """)

    return conn


def demo_basic_agent_creation(builder):
    """Demo 1: Create a basic sub-agent"""
    print("\n=== Demo 1: Basic Agent Creation ===")

    agent = builder.define_agent(
        role='context-delivery',
        display_name='Context Assembly Agent',
        description='Assembles session context from database',
        tier=1,  # Sub-agent
        execution_mode='parallel',
        capabilities=['context-assembly', 'confidence-scoring']
    )

    print(f"✓ Created agent: {agent.role} (id={agent.id})")

    # Add tool preference
    builder.add_tool(agent.id, 'context7', phase='discovery', priority=1)
    print(f"  - Added tool: context7 for discovery phase")

    # Add learning example
    builder.add_example(
        agent.id,
        'Task Context Assembly',
        input_context={'task_id': 355},
        expected_output={'confidence': 0.85, 'contexts': 5}
    )
    print(f"  - Added learning example: Task Context Assembly")

    builder.commit()
    print("✓ Changes committed\n")

    return agent


def demo_orchestrator_creation(builder):
    """Demo 2: Create orchestrator with relationships"""
    print("\n=== Demo 2: Orchestrator with Delegation ===")

    # Create master orchestrator
    master = builder.define_agent(
        role='master-orchestrator',
        display_name='Master Orchestrator',
        tier=3,
        orchestrator_type='master',
        symbol_mode=True
    )
    print(f"✓ Created master: {master.role} (id={master.id})")

    # Create sub-agents
    sub1 = builder.define_agent(role='context-delivery', tier=1)
    sub2 = builder.define_agent(role='intent-triage', tier=1)
    print(f"✓ Created sub-agents: context-delivery, intent-triage")

    builder.commit()

    # Create mini-orchestrator using convenience function
    mini = create_orchestrator_agent(
        builder,
        role='definition-orch',
        tier=2,
        delegates_to=['context-delivery', 'intent-triage'],
        reports_to='master-orchestrator',
        tools={
            'discovery': ['context7', 'sequential-thinking'],
            'reasoning': ['sequential-thinking']
        }
    )

    print(f"✓ Created mini-orchestrator: {mini.role} (id={mini.id})")
    print(f"  - Reports to: master-orchestrator")
    print(f"  - Delegates to: context-delivery, intent-triage")
    print(f"  - Tools: context7 (discovery), sequential-thinking (discovery, reasoning)")

    builder.commit()
    print("✓ Changes committed\n")

    return mini


def demo_three_tier_architecture(builder):
    """Demo 3: Complete three-tier architecture"""
    print("\n=== Demo 3: Three-Tier Architecture ===")

    # Tier 3: Master
    master = builder.define_agent(
        role='master-orchestrator',
        tier=3,
        orchestrator_type='master'
    )
    print(f"✓ Tier 3 (Master): {master.role}")

    # Tier 2: Mini-orchestrators
    mini_roles = ['definition-orch', 'planning-orch', 'implementation-orch']
    mini_agents = []

    for role in mini_roles:
        mini = builder.define_agent(
            role=role,
            tier=2,
            orchestrator_type='mini'
        )
        mini_agents.append(mini)
        builder.add_relationship(mini.id, master.id, 'reports_to')

    print(f"✓ Tier 2 (Mini-Orchestrators): {', '.join(mini_roles)}")

    # Tier 1: Sub-agents
    sub_roles = [
        'context-delivery', 'intent-triage', 'ac-writer',
        'code-implementer', 'test-runner', 'quality-gatekeeper'
    ]
    sub_agents = []

    for role in sub_roles:
        sub = builder.define_agent(role=role, tier=1)
        sub_agents.append(sub)

    print(f"✓ Tier 1 (Sub-Agents): {', '.join(sub_roles)}")

    # Add delegation relationships
    # definition-orch delegates to context-delivery, intent-triage
    builder.add_relationship(mini_agents[0].id, sub_agents[0].id, 'delegates_to')
    builder.add_relationship(mini_agents[0].id, sub_agents[1].id, 'delegates_to')

    # implementation-orch delegates to ac-writer, code-implementer
    builder.add_relationship(mini_agents[2].id, sub_agents[2].id, 'delegates_to')
    builder.add_relationship(mini_agents[2].id, sub_agents[3].id, 'delegates_to')

    builder.commit()
    print(f"\n✓ Created complete 3-tier architecture:")
    print(f"  - 1 master orchestrator")
    print(f"  - {len(mini_agents)} mini-orchestrators")
    print(f"  - {len(sub_agents)} sub-agents")
    print("✓ Changes committed\n")


def demo_transaction_rollback(builder):
    """Demo 4: Transaction rollback on error"""
    print("\n=== Demo 4: Transaction Rollback ===")

    try:
        # Create some agents
        agent1 = builder.define_agent(role='test-agent-1', tier=1)
        agent2 = builder.define_agent(role='test-agent-2', tier=1)

        print(f"✓ Created agents: test-agent-1, test-agent-2")
        print(f"  Pending operations: {len(builder.get_pending_operations())}")

        # Simulate error - invalid relationship type
        builder.add_relationship(agent1.id, agent2.id, 'invalid_type')

    except ValueError as e:
        print(f"✗ Error: {e}")
        builder.rollback()
        print("✓ Transaction rolled back - no changes persisted")

        # Verify rollback worked
        agent = builder.get_agent_by_role('test-agent-1')
        print(f"  Verification: test-agent-1 exists? {agent is not None}")
        print()


def print_agent_summary(builder):
    """Print summary of all agents in database"""
    print("\n=== Agent Summary ===")

    conn = builder.conn
    cursor = conn.execute("""
        SELECT orchestrator_type, COUNT(*) as count
        FROM agents
        GROUP BY orchestrator_type
        ORDER BY
            CASE orchestrator_type
                WHEN 'master' THEN 1
                WHEN 'mini' THEN 2
                ELSE 3
            END
    """)

    for row in cursor:
        orch_type = row['orchestrator_type'] or 'sub-agent'
        count = row['count']
        print(f"  {orch_type}: {count}")

    # Relationships
    cursor = conn.execute("SELECT COUNT(*) as count FROM agent_relationships")
    rel_count = cursor.fetchone()['count']
    print(f"\nRelationships: {rel_count}")

    # Tools
    cursor = conn.execute("SELECT COUNT(*) as count FROM agent_tools")
    tool_count = cursor.fetchone()['count']
    print(f"Tool Preferences: {tool_count}")

    # Examples
    cursor = conn.execute("SELECT COUNT(*) as count FROM agent_examples")
    example_count = cursor.fetchone()['count']
    print(f"Learning Examples: {example_count}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("Agent Builder API Demo")
    print("=" * 60)

    # Setup
    conn = setup_demo_database()
    builder = AgentBuilder(conn, project_id=1)

    print("\n✓ Database initialized")
    print("✓ AgentBuilder ready")

    # Run demos
    demo_basic_agent_creation(builder)
    demo_orchestrator_creation(builder)
    demo_three_tier_architecture(builder)
    demo_transaction_rollback(builder)

    # Summary
    print_agent_summary(builder)

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nFor more examples, see:")
    print("  - docs/components/agents/agent-builder-api.md")
    print("  - tests-BAK/core/agents/test_builder.py")
    print()

    conn.close()


if __name__ == '__main__':
    main()
