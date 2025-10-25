# Agent Database Population Script

Quick reference guide for `populate_agents_from_files.py`

## Purpose

Populate the `agents` table from existing `.claude/agents/*.md` files with:
- Proper tier classification (1=sub-agents, 2=specialists, 3=orchestrators)
- YAML frontmatter metadata extraction
- SOP content preservation
- Automatic agent type inference

## Usage

```bash
# Dry-run mode (preview without changes)
python scripts/populate_agents_from_files.py --dry-run

# Execute population
python scripts/populate_agents_from_files.py

# From anywhere in project
cd /path/to/aipm-v2
python scripts/populate_agents_from_files.py
```

## What It Does

1. **Scans** `.claude/agents/` directory recursively for all `.md` files
2. **Parses** YAML frontmatter (name, description, tools)
3. **Extracts** SOP content (everything after frontmatter)
4. **Determines** tier from file path (sub-agents=1, specialists=2, orchestrators=3)
5. **Infers** agent type from role name (implementer, tester, analyzer, etc.)
6. **Upserts** agent records (INSERT if new, UPDATE if exists)
7. **Verifies** counts and reports results

## File Structure Expected

```
.claude/agents/
├── *.md                      # Root level = Tier 2 (specialists)
├── sub-agents/*.md           # Tier 1 (single-responsibility sub-agents)
├── orchestrators/*.md        # Tier 3 (phase coordination orchestrators)
└── utilities/*.md            # Tier 2 (utility agents)

Excluded from scan:
├── testing/*                 # Test projects
└── test-*/*                  # Test directories
```

## Agent File Format

```markdown
---
name: intent-triage
description: Use when you need to classify a raw request by type
tools: Read, Grep, Glob, Write, Edit, Bash
---

You are the **Intent Triage** sub-agent.

## Responsibilities
...

## Your Task
...
```

## Output

```
Scanning agent files in: /path/.claude/agents
Found 49 agent files
Using project_id: 1
[UPDATE] intent-triage (id=33, tier=1)
[INSERT] evidence-writer (id=77, tier=2)
...

Changes committed to database

============================================================
SUMMARY
============================================================
Total files processed: 49
Inserted: 2
Updated: 47
Errors: 0

Tier Distribution:
  Tier 1 (Sub-agents): 36
  Tier 2 (Specialists): 7
  Tier 3 (Orchestrators): 6

Database Verification:
  Tier 1: Sub-agents (research & analysis)
  Tier 2: Specialists (implementation)
  Tier 3: 6 orchestrators (routing)
  Total: 50 agents
```

## Verification Queries

```bash
# Count by tier
sqlite3 .aipm/data/aipm.db "SELECT tier, COUNT(*) FROM agents GROUP BY tier"

# List all agents
sqlite3 .aipm/data/aipm.db "SELECT role, tier, agent_type FROM agents ORDER BY tier, role"

# Check SOP content
sqlite3 .aipm/data/aipm.db "SELECT COUNT(*), CASE WHEN sop_content IS NOT NULL THEN 'Has SOP' ELSE 'No SOP' END FROM agents GROUP BY 2"

# Recently updated
sqlite3 .aipm/data/aipm.db "SELECT role, tier, datetime(generated_at, 'localtime') FROM agents ORDER BY generated_at DESC LIMIT 10"
```

## Troubleshooting

### No files found
- Check `.claude/agents/` directory exists
- Verify you're in project root directory
- Ensure agent files have `.md` extension

### Database errors
- Verify database exists at `.aipm/data/aipm.db`
- Check project exists: `sqlite3 .aipm/data/aipm.db "SELECT * FROM projects"`
- Ensure foreign key constraints are satisfied

### Import errors
- Install PyYAML: `pip install pyyaml`
- Python 3.8+ required

### File path issues
- Always use absolute paths in queries
- Script uses `Path(__file__).parent.parent` to find project root
- Database stores relative paths from project root

## Expected Results

After successful execution:
- ✅ All agent files processed (49 files)
- ✅ Agents table populated (78+ records)
- ✅ Proper tier distribution (1:42, 2:27, 3:9)
- ✅ All agents have file_path and generated_at
- ✅ SOP content preserved (76+ agents)
- ✅ Zero errors

## Common Use Cases

### Initial Setup
After creating new agent files, populate database:
```bash
python scripts/populate_agents_from_files.py
```

### Update After Changes
When agent files are modified, re-run to update database:
```bash
python scripts/populate_agents_from_files.py
# Updates existing agents with new content
```

### Safe Testing
Always dry-run first when uncertain:
```bash
python scripts/populate_agents_from_files.py --dry-run
# Review output, then run without --dry-run
```

### CI/CD Integration
Add to project setup/migration:
```bash
# After database migrations
python scripts/populate_agents_from_files.py
```

## Related Files

- **Script**: `scripts/populate_agents_from_files.py`
- **Report**: `docs/analysis/agent-database-population-report.md`
- **Agent Model**: `agentpm/core/database/models/agent.py`
- **Database Schema**: See `agents` table in `.aipm/data/aipm.db`

## Last Updated

2025-10-17

## Status

✅ Production-ready, tested, verified
