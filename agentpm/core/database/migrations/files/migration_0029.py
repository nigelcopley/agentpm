"""
Migration 0029: Add five new default utility agents

Adds the following utility agents to support provider generation system:
1. context-generator: Assembles session context
2. agent-builder: Creates new agents from specifications
3. database-query-agent: SQL query generation and execution
4. file-operations-agent: CRUD operations for files
5. workflow-coordinator: State machine transitions

These agents support the new provider generator architecture.
Requires migration 0027 (metadata column) to run first.
"""

import sqlite3
from datetime import datetime


def upgrade(conn: sqlite3.Connection) -> None:
    """Add five new utility agents"""
    print("🔧 Migration 0029: Add five new utility agents")

    # Check if agents already exist
    cursor = conn.execute(
        "SELECT role FROM agents WHERE role IN (?, ?, ?, ?, ?)",
        (
            'context-generator',
            'agent-builder',
            'database-query-agent',
            'file-operations-agent',
            'workflow-coordinator'
        )
    )
    existing_agents = {row[0] for row in cursor.fetchall()}

    agents_to_add = []

    # 1. Context Generator
    if 'context-generator' not in existing_agents:
        agents_to_add.append({
            'role': 'context-generator',
            'persona': 'Context Assembly Specialist',
            'description': (
                'Assembles comprehensive session context from database records, '
                'project files, and plugin intelligence. Calculates context confidence '
                'and identifies gaps requiring additional research.'
            ),
            'behavioral_rules': [
                'Load context hierarchically: project → work item → task → dependencies',
                'Calculate confidence scores for all context elements',
                'Identify missing context and recommend research agents',
                'Compress context using token-efficient formatting',
                'Cache frequently accessed context elements',
            ],
            'success_metrics': (
                'Context confidence >70%, load time <2s, cache hit rate >60%'
            )
        })

    # 2. Agent Builder
    if 'agent-builder' not in existing_agents:
        agents_to_add.append({
            'role': 'agent-builder',
            'persona': 'Agent System Architect',
            'description': (
                'Creates new agents from specifications, generates agent files for '
                'multiple LLM providers, and maintains agent architecture consistency. '
                'Ensures all agents follow established patterns and standards.'
            ),
            'behavioral_rules': [
                'Validate agent specifications against architecture standards',
                'Generate provider-specific agent files (Claude Code, Cursor, etc.)',
                'Ensure agent has clear responsibilities and success criteria',
                'Document agent integration points and dependencies',
                'Test agent generation with sample specifications',
            ],
            'success_metrics': (
                'Generated agents pass validation, files compile correctly, '
                'documentation complete'
            )
        })

    # 3. Database Query Agent
    if 'database-query-agent' not in existing_agents:
        agents_to_add.append({
            'role': 'database-query-agent',
            'persona': 'Database Operations Specialist',
            'description': (
                'Executes safe, efficient database queries with proper error handling '
                'and transaction management. Generates SQL from natural language queries '
                'and validates query safety before execution.'
            ),
            'behavioral_rules': [
                'Validate all queries for SQL injection vulnerabilities',
                'Use parameterized queries exclusively',
                'Implement proper transaction boundaries',
                'Log all database operations for audit trail',
                'Optimize queries for performance (use indexes, avoid N+1)',
            ],
            'success_metrics': (
                'Zero SQL injection vulnerabilities, query performance <100ms average, '
                '100% transaction safety'
            )
        })

    # 4. File Operations Agent
    if 'file-operations-agent' not in existing_agents:
        agents_to_add.append({
            'role': 'file-operations-agent',
            'persona': 'File System Operations Specialist',
            'description': (
                'Performs safe file system operations with proper error handling, '
                'atomic operations, and backup capabilities. Handles file creation, '
                'reading, updating, deletion, and directory management.'
            ),
            'behavioral_rules': [
                'Validate all file paths (prevent directory traversal)',
                'Use atomic operations for file writes (write + rename)',
                'Create backups before destructive operations',
                'Respect .gitignore and project exclusion patterns',
                'Handle file encoding properly (UTF-8 default)',
            ],
            'success_metrics': (
                'Zero file corruption, 100% atomic operations, proper permissions '
                'maintained'
            )
        })

    # 5. Workflow Coordinator
    if 'workflow-coordinator' not in existing_agents:
        agents_to_add.append({
            'role': 'workflow-coordinator',
            'persona': 'State Machine Orchestrator',
            'description': (
                'Manages workflow state transitions for tasks and work items. '
                'Validates transitions against state machine rules, enforces gate '
                'requirements, and maintains audit trail of all state changes.'
            ),
            'behavioral_rules': [
                'Validate all state transitions against allowed transitions',
                'Enforce gate requirements before transitions',
                'Log all state changes with timestamp and agent',
                'Prevent invalid state transitions with clear error messages',
                'Support rollback for failed transitions',
            ],
            'success_metrics': (
                '100% valid state transitions, complete audit trail, '
                'gate enforcement >99%'
            )
        })

    # Insert agents
    if agents_to_add:
        print(f"  📋 Adding {len(agents_to_add)} new agents...")

        # Get current project_id (assume first project)
        # Skip if no project exists - agents require a project
        project_cursor = conn.execute("SELECT id FROM projects LIMIT 1")
        project_row = project_cursor.fetchone()
        if not project_row:
            print("  ⚠️  No project found - skipping agent creation")
            print("  💡 Run 'apm init' to create a project first")
            return
        project_id = project_row[0]

        for agent in agents_to_add:
            # Store behavioral rules in metadata JSON field
            import json
            metadata = json.dumps({
                'behavioral_rules': agent['behavioral_rules']
            })

            conn.execute("""
                INSERT INTO agents (
                    project_id,
                    role,
                    display_name,
                    description,
                    sop_content,
                    metadata,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                project_id,
                agent['role'],
                agent['persona'],  # persona → display_name
                agent['description'],
                agent['success_metrics'],  # success_metrics → sop_content
                metadata,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            print(f"  ✅ Added agent: {agent['role']}")

        # Note: No conn.commit() - MigrationManager handles transaction
    else:
        print("  ✅ All agents already exist, skipping")


def downgrade(conn: sqlite3.Connection) -> None:
    """Remove the five new utility agents"""
    print("🔧 Migration 0029 downgrade: Remove five new utility agents")

    conn.execute("""
        DELETE FROM agents
        WHERE role IN (?, ?, ?, ?, ?)
    """, (
        'context-generator',
        'agent-builder',
        'database-query-agent',
        'file-operations-agent',
        'workflow-coordinator'
    ))

    # Note: No conn.commit() - MigrationManager handles transaction
    print("  ✅ Agents removed successfully")
