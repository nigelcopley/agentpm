# MCP Server Setup for AIPM Documentation

## Overview

This guide explains how to configure the Model Context Protocol (MCP) server to enable Claude to query AIPM documentation directly. This integration ensures agents always have access to up-to-date documentation and eliminates documentation drift.

## What is docs-mcp-server?

The Model Context Protocol (MCP) is an open standard that enables AI assistants to access external data sources. The `docs-mcp-server` specifically provides documentation access through:

- **Semantic search** across all markdown files
- **Real-time indexing** when files change
- **Context-aware retrieval** for agent queries
- **Automatic synchronization** with codebase

### Benefits for AIPM

- **No more stale docs**: Agents read directly from source
- **Reduced hallucination**: Agents cite actual documentation
- **Better context**: Agents understand current workflow state
- **Zero maintenance**: Documentation stays in sync automatically

## Installation

### Prerequisites

- Node.js 16+ (for MCP server)
- Claude Desktop app
- APM (Agent Project Manager) installed

### 1. Install docs-mcp-server

```bash
npm install -g @modelcontextprotocol/docs-server
```

Verify installation:

```bash
docs-mcp-server --version
```

### 2. Configure Claude Desktop

Add the MCP server configuration to Claude Desktop's config file.

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration**:

```json
{
  "mcpServers": {
    "aipm-docs": {
      "command": "docs-mcp-server",
      "args": [
        "--docs-path",
        "/Users/nigelcopley/.project_manager/agentpm/docs"
      ],
      "env": {
        "DOCS_INDEX_INTERVAL": "5000"
      }
    }
  }
}
```

**Configuration options**:

- `docs-path`: Absolute path to AIPM docs directory
- `DOCS_INDEX_INTERVAL`: Re-index interval in milliseconds (5000 = 5 seconds)

### 3. Restart Claude Desktop

1. Quit Claude Desktop completely
2. Relaunch the application
3. MCP server will auto-start and index documentation

## Usage

### Querying Documentation

Once configured, Claude can answer questions about AIPM using live documentation:

**Example queries**:

- "What are the current TaskStatus enum values?"
- "How do I create a work item?"
- "What's the difference between draft and ready status?"
- "Show me the workflow phase progression"
- "What are the quality gate requirements for I1?"

### Agent Integration

AIPM agents automatically benefit from MCP integration:

- **context-delivery** agent can read latest documentation
- **definition-orch** can reference current workflow requirements
- **implementation-orch** can verify quality gates
- **quality-gatekeeper** can check against current standards

### Verification

Check that MCP server is running:

```bash
# View MCP logs
tail -f ~/Library/Logs/Claude/mcp_logs/aipm-docs.log

# Test connection (from Claude Desktop)
# Ask: "What MCP servers are connected?"
```

Expected output in logs:

```
[INFO] MCP Server started: aipm-docs
[INFO] Indexing documents in: /Users/.../agentpm/docs
[INFO] Indexed 127 markdown files
[INFO] Ready for queries
```

## Integration with Testing

MCP documentation access complements our testing strategy:

| Tool | Purpose | Integration Point |
|------|---------|-------------------|
| **pytest-examples** | Test code blocks in docs | Validates doc examples work |
| **transitions** | Generate state diagrams | Creates visual documentation |
| **docs-mcp-server** | Real-time doc access | Agents query live docs |

This creates a **virtuous cycle**:

1. Code changes trigger diagram updates
2. Tests validate documentation accuracy
3. MCP serves verified documentation to agents
4. Agents make decisions based on current truth

## Troubleshooting

### MCP Server Not Starting

**Symptom**: Claude can't access documentation

**Solutions**:

1. Check Node.js version: `node --version` (requires 16+)
2. Verify installation: `which docs-mcp-server`
3. Check config path: Ensure `docs-path` exists
4. Review logs: `~/Library/Logs/Claude/mcp_logs/`

### Stale Documentation

**Symptom**: Agents reference old information

**Solutions**:

1. Restart Claude Desktop to re-index
2. Lower `DOCS_INDEX_INTERVAL` for faster updates
3. Check file permissions on docs directory

### High CPU Usage

**Symptom**: MCP server consuming resources

**Solutions**:

1. Increase `DOCS_INDEX_INTERVAL` to reduce re-indexing
2. Exclude large files via `.mcp-ignore` file
3. Limit indexing to specific directories

## Advanced Configuration

### Selective Indexing

Create `.mcp-ignore` in docs root:

```
# Ignore work-in-progress
drafts/
*.draft.md

# Ignore generated files
reference/state-diagrams/

# Ignore archives
archive/
```

### Multiple Documentation Sources

Add multiple MCP servers for different doc sets:

```json
{
  "mcpServers": {
    "aipm-docs": {
      "command": "docs-mcp-server",
      "args": ["--docs-path", "/path/to/agentpm/docs"]
    },
    "aipm-agents": {
      "command": "docs-mcp-server",
      "args": ["--docs-path", "/path/to/agentpm/.claude/agents"]
    }
  }
}
```

### CI/CD Integration

For automated testing environments:

```yaml
# .github/workflows/test-docs.yml
- name: Start MCP Server for Tests
  run: |
    docs-mcp-server --docs-path ./docs --port 3000 &
    echo $! > mcp.pid

- name: Run Documentation Tests
  run: pytest tests/docs/ -v

- name: Stop MCP Server
  run: kill $(cat mcp.pid)
```

## Next Steps

1. **Phase 1**: Configure MCP for local development
2. **Phase 2**: Add CI/CD integration for testing
3. **Phase 3**: Configure custom indexing rules
4. **Phase 4**: Integrate with other MCP tools (filesystem, git)
5. **Phase 5**: Create agent-specific documentation views

## Related Documentation

- [Documentation Testing Infrastructure](../reference/doc-testing.md)
- [State Diagram Generation](../reference/state-diagrams/)
- [Agent System Architecture](../../architecture/agents/)
- [Quality Gates](../reference/quality-gates.md)

---

**Document Type**: User Guide
**Category**: Documentation
**Last Updated**: 2025-10-20
**Version**: 1.0.0
