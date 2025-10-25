# APM (Agent Project Manager) - User Documentation Index

**Complete User Guide for APM (Agent Project Manager)** - Your guide to database-driven, AI-assisted project management.

---

## 🚀 Quick Start

**New to APM?** Start here:

1. [**Getting Started**](getting-started.md) - Install, initialize, and create your first work item (15 minutes)
2. [**Quick Reference**](cli-reference/quick-reference.md) - Essential commands and workflows (2-page cheat sheet)
3. [**Phase Workflow**](workflows/phase-workflow.md) - Understand the 6-phase development lifecycle

**Looking for something specific?** Use the sections below.

---

## 📖 Documentation Structure

### 1. Getting Started

**Path**: `getting-started.md`

**New to APM?** This is your starting point.

- Installation and setup
- Initialize your first project
- Create work items and tasks
- Understand quality gates
- Navigate the phase-based workflow

**Time**: 15 minutes | **Difficulty**: Beginner

**Next**: [Quick Reference](cli-reference/quick-reference.md)

---

### 2. CLI Reference

**Path**: `cli-reference/`

Complete command-line interface documentation.

#### 2.1 Quick Reference
**File**: [quick-reference.md](cli-reference/quick-reference.md)

2-page printable cheat sheet with:
- Core concepts and terminology
- Essential commands with examples
- Common workflows
- Phase lifecycle reference
- Troubleshooting tips

**Use When**: Need quick command syntax or workflow reminders

**Previous**: [Getting Started](getting-started.md) | **Next**: [Full Commands](cli-reference/commands.md)

#### 2.2 Full Command Reference
**File**: [commands.md](cli-reference/commands.md)

Complete documentation of all 67+ APM commands:
- System commands (init, status, help)
- Work item commands (create, list, show, update, lifecycle)
- Task commands (create, list, show, update, lifecycle)
- Phase commands (status, validate, advance)
- Context, session, agent, rules commands

**Use When**: Need detailed command documentation or options

**Previous**: [Quick Reference](cli-reference/quick-reference.md) | **Next**: [Phase Workflow](workflows/phase-workflow.md)

---

### 3. Workflows

**Path**: `workflows/`

Understand APM's phase-based development methodology.

#### 3.1 Phase Workflow Guide
**File**: [phase-workflow.md](workflows/phase-workflow.md)

Complete guide to the 6-phase development lifecycle:
- **D1 Discovery**: Define needs, validate fit
- **P1 Planning**: Create detailed plans
- **I1 Implementation**: Build the solution
- **R1 Review**: Test and validate
- **O1 Operations**: Deploy and monitor
- **E1 Evolution**: Learn and improve

**Use When**: Understanding how phases work and progress

**Previous**: [CLI Commands](cli-reference/commands.md) | **Next**: [Ideas Workflow](workflows/ideas-workflow.md)

#### 3.2 Ideas Workflow
**File**: [ideas-workflow.md](workflows/ideas-workflow.md)

Manage ideas and convert them to work items:
- Capture ideas quickly
- Evaluate and prioritize
- Convert ideas to work items
- Track idea lifecycle

**Previous**: [Phase Workflow](workflows/phase-workflow.md) | **Next**: [Troubleshooting](workflows/troubleshooting.md)

#### 3.3 Troubleshooting Guide
**File**: [troubleshooting.md](workflows/troubleshooting.md)

Real errors encountered and their solutions:
- Installation issues
- Initialization errors
- Validation failures
- Phase advancement issues
- Quality gate problems
- Database issues
- Performance problems

**Use When**: Encountering errors or unexpected behavior

**Previous**: [Ideas Workflow](workflows/ideas-workflow.md) | **Next**: [Advanced Features](advanced/)

---

### 4. Advanced Features

**Path**: `advanced/`

Deep dive into APM's powerful capabilities.

#### 4.1 Agent Generation
**File**: [agent-generation.md](advanced/agent-generation.md)

Intelligent agent generation system:
- How agents are stored in database
- Generating provider-specific files
- Agent types and roles
- Customizing agent behavior

**Previous**: [Troubleshooting](workflows/troubleshooting.md) | **Next**: [Memory System](advanced/memory-system.md)

#### 4.2 Memory System
**File**: [memory-system.md](advanced/memory-system.md)

Persistent context and memory management:
- How APM remembers context
- Session management
- Context retrieval
- Memory optimization

**Previous**: [Agent Generation](advanced/agent-generation.md) | **Next**: [Rich Context](advanced/rich-context.md)

#### 4.3 Rich Context System
**File**: [rich-context.md](advanced/rich-context.md)

Comprehensive context analysis (6W Framework):
- WHO, WHAT, WHERE, WHEN, WHY, HOW
- Context confidence scoring
- Evidence-based context
- Context validation

**Previous**: [Memory System](advanced/memory-system.md) | **Next**: [Detection Packs](advanced/detection-packs.md)

#### 4.4 Detection Packs
**File**: [detection-packs.md](advanced/detection-packs.md)

Automatic project technology detection:
- How detection works
- Supported technologies
- Custom detection packs
- Detection confidence

**Previous**: [Rich Context](advanced/rich-context.md) | **Next**: [Slash Commands](advanced/slash-commands.md)

#### 4.5 Slash Commands
**File**: [slash-commands.md](advanced/slash-commands.md)

Custom commands for AI assistants:
- Creating slash commands
- Command templates
- Integration with agents
- Command best practices

**Previous**: [Detection Packs](advanced/detection-packs.md) | **Next**: [Integrations](integrations/)

---

### 5. Integrations

**Path**: `integrations/`

Integrate APM with your development tools.

#### 5.1 Claude Code Integration

**Path**: `integrations/claude-code/`

Complete integration with Anthropic's Claude Code CLI.

##### Overview
**File**: [overview.md](integrations/claude-code/overview.md)

Introduction to Claude Code integration:
- What is Claude Code
- Benefits of integration
- Setup overview

**Next**: [Commands](integrations/claude-code/commands.md)

##### Commands
**File**: [commands.md](integrations/claude-code/commands.md)

Claude Code-specific APM commands:
- Agent commands in Claude
- Context commands
- Workflow automation

**Previous**: [Overview](integrations/claude-code/overview.md) | **Next**: [Hooks](integrations/claude-code/hooks.md)

##### Hooks
**File**: [hooks.md](integrations/claude-code/hooks.md)

Event hooks and automation:
- Pre/post command hooks
- Workflow automation
- Custom triggers

**Previous**: [Commands](integrations/claude-code/commands.md) | **Next**: [Plugin](integrations/claude-code/plugin.md)

##### Plugin
**File**: [plugin.md](integrations/claude-code/plugin.md)

APM plugin for Claude Code:
- Installing the plugin
- Plugin configuration
- Using plugin features

**Previous**: [Hooks](integrations/claude-code/hooks.md) | **Next**: [Cursor Integration](integrations/cursor/overview.md)

#### 5.2 Cursor Integration

**Path**: `integrations/cursor/`

Integration with Cursor AI editor.

##### Overview
**File**: [overview.md](integrations/cursor/overview.md)

Introduction to Cursor integration:
- What is Cursor
- Benefits of integration
- Setup overview

**Previous**: [Claude Code Plugin](integrations/claude-code/plugin.md) | **Next**: [Setup](integrations/cursor/setup.md)

##### Setup
**File**: [setup.md](integrations/cursor/setup.md)

Installing and configuring Cursor integration:
- Installation steps
- Configuration options
- Verification

**Previous**: [Overview](integrations/cursor/overview.md) | **Next**: [Usage](integrations/cursor/usage.md)

##### Usage
**File**: [usage.md](integrations/cursor/usage.md)

Using APM within Cursor:
- Commands in Cursor
- Workflow integration
- Best practices

**Previous**: [Setup](integrations/cursor/setup.md) | **Next**: [MCP Setup](integrations/mcp-setup.md)

#### 5.3 MCP Setup
**File**: [mcp-setup.md](integrations/mcp-setup.md)

Model Context Protocol integration:
- What is MCP
- APM MCP server setup
- Using MCP with AI assistants

**Previous**: [Cursor Usage](integrations/cursor/usage.md) | **Next**: [Use Cases](use-cases/)

---

### 6. Use Cases

**Path**: `use-cases/`

Real-world scenarios and workflows.

#### 6.1 Solo Developer
**File**: [solo-developer.md](use-cases/solo-developer.md)

APM for individual developers and startups:
- Quick setup for solo projects
- Managing multiple projects
- Time tracking and productivity
- Best practices for solo work

**Previous**: [MCP Setup](integrations/mcp-setup.md) | **Next**: [Consultant](use-cases/consultant.md)

#### 6.2 Consultant / Client Projects
**File**: [consultant.md](use-cases/consultant.md)

Managing client projects with APM:
- Multi-client workflows
- Client reporting
- Time and billing tracking
- Project handoff

**Previous**: [Solo Developer](use-cases/solo-developer.md) | **Next**: [Enterprise](use-cases/enterprise.md)

#### 6.3 Enterprise Teams
**File**: [enterprise.md](use-cases/enterprise.md)

APM for larger teams and organizations:
- Team collaboration
- Migration from other tools
- Enterprise compliance
- Scaling APM

**Previous**: [Consultant](use-cases/consultant.md) | **Next**: [Open Source](use-cases/open-source.md)

#### 6.4 Open Source Maintainer
**File**: [open-source.md](use-cases/open-source.md)

Managing open source projects:
- Community contribution tracking
- Issue management
- Release planning
- Contributor workflows

**Previous**: [Enterprise](use-cases/enterprise.md) | **Next**: [Developer Guides](developer/)

---

### 7. Developer Guides

**Path**: `developer/`

For those extending or contributing to APM.

#### 7.1 Architecture Overview
**File**: [architecture.md](developer/architecture.md)

APM's internal architecture:
- Database-first design
- Three-tier architecture
- Component overview
- Design principles

**Previous**: [Open Source](use-cases/open-source.md) | **Next**: [Three-Layer Pattern](developer/three-layer-pattern.md)

#### 7.2 Three-Layer Pattern
**File**: [three-layer-pattern.md](developer/three-layer-pattern.md)

The gold standard for database operations:
- Models (Pydantic)
- Adapters (SQLite conversion)
- Methods (business logic)
- Real examples from codebase

**Previous**: [Architecture](developer/architecture.md) | **Next**: [Contributing](developer/contributing.md)

#### 7.3 Contributing Guide
**File**: [contributing.md](developer/contributing.md)

How to contribute to APM:
- Development setup
- Code standards
- Testing requirements
- Pull request process

**Previous**: [Three-Layer Pattern](developer/three-layer-pattern.md) | **Next**: [Migrations](developer/migrations.md)

#### 7.4 Database Migrations
**File**: [migrations.md](developer/migrations.md)

Database schema evolution:
- Migration system overview
- Creating migrations
- Running migrations
- Migration best practices

**Previous**: [Contributing](developer/contributing.md)

---

### 8. Additional Resources

#### Fitness Presets
**File**: [fitness-presets.md](fitness-presets.md)

Quality assessment presets for different project types:
- Startup presets (rapid iteration)
- Enterprise presets (high quality)
- Open source presets (community-driven)
- Custom preset creation

---

## 📚 Learning Paths

### For Complete Beginners

**Goal**: Get productive with APM in 1-2 hours

1. **Read**: [Getting Started](getting-started.md) (15 min)
2. **Practice**: Follow the guide with your own project (30 min)
3. **Reference**: Keep [Quick Reference](cli-reference/quick-reference.md) handy
4. **Explore**: Try commands from [CLI Reference](cli-reference/commands.md) (15 min)

**Total Time**: 1-2 hours

---

### For Experienced Developers

**Goal**: Understand the system deeply in 30-45 minutes

1. **Skim**: [Quick Reference](cli-reference/quick-reference.md) (5 min)
2. **Deep Dive**: [Phase Workflow](workflows/phase-workflow.md) (20 min)
3. **Reference**: [CLI Commands](cli-reference/commands.md) as needed
4. **Advanced**: Pick topics from [Advanced Features](advanced/) (10 min)

**Total Time**: 30-45 minutes

---

### For Project Managers

**Goal**: Understand workflows and quality gates

1. **Overview**: [Getting Started](getting-started.md) - Introduction section (5 min)
2. **Phases**: [Phase Workflow](workflows/phase-workflow.md) (15 min)
3. **Quality**: [Phase Workflow](workflows/phase-workflow.md) - Quality gates section (5 min)
4. **Reference**: [Quick Reference](cli-reference/quick-reference.md) - Concepts section (5 min)

**Focus**: Understand phases, quality gates, and metrics

**Total Time**: 30 minutes

---

### For Team Leads

**Goal**: Set up APM for your team

1. **Setup**: [Getting Started](getting-started.md) (15 min)
2. **Workflows**: [Phase Workflow](workflows/phase-workflow.md) (20 min)
3. **Use Case**: [Enterprise Teams](use-cases/enterprise.md) or [Consultant](use-cases/consultant.md) (15 min)
4. **Advanced**: [Agent Generation](advanced/agent-generation.md) (10 min)

**Total Time**: 1 hour

---

## 🎯 Quick Links by Task

### Installation & Setup
- [Getting Started](getting-started.md)
- [Claude Code Integration](integrations/claude-code/overview.md)
- [Cursor Integration](integrations/cursor/overview.md)
- [MCP Setup](integrations/mcp-setup.md)

### Daily Usage
- [Quick Reference](cli-reference/quick-reference.md)
- [CLI Commands](cli-reference/commands.md)
- [Phase Workflow](workflows/phase-workflow.md)
- [Troubleshooting](workflows/troubleshooting.md)

### Advanced Features
- [Agent Generation](advanced/agent-generation.md)
- [Memory System](advanced/memory-system.md)
- [Rich Context](advanced/rich-context.md)
- [Detection Packs](advanced/detection-packs.md)
- [Slash Commands](advanced/slash-commands.md)

### Development & Contributing
- [Architecture](developer/architecture.md)
- [Three-Layer Pattern](developer/three-layer-pattern.md)
- [Contributing](developer/contributing.md)
- [Migrations](developer/migrations.md)

---

## 🔍 Documentation Quality

### Standards

All documentation in this directory follows these principles:

1. **Real Examples**: Every example is from actual APM usage, not hypothetical
2. **Tested Commands**: All commands have been tested and verified
3. **Clear Navigation**: Previous/Next links between related guides
4. **Practical Focus**: Task-oriented, not just feature lists
5. **Consistent Branding**: APM (Agent Project Manager) throughout

### Branding Guidelines

**Product Name**: APM (Agent Project Manager)
- **Full name**: Agent Project Manager (not AI Project Manager)
- **Abbreviation**: APM (not AIPM)
- **Directory**: `.agentpm/` (not `.aipm/`)
- **Database**: `agentpm.db` (not `aipm.db`)
- **Command**: `apm` (not `aipm`)

---

## 📝 Documentation Metrics

| Section | Files | Topics Covered |
|---------|-------|----------------|
| Getting Started | 1 | Installation, initialization, first project |
| CLI Reference | 2 | 67+ commands, quick reference |
| Workflows | 3 | Phases, ideas, troubleshooting |
| Advanced | 5 | Agents, memory, context, detection, commands |
| Integrations | 8 | Claude Code, Cursor, MCP |
| Use Cases | 4 | Solo, consultant, enterprise, open source |
| Developer | 4 | Architecture, patterns, contributing, migrations |
| **Total** | **28** | **Complete user documentation** |

---

## 🤝 Contributing to Documentation

Found an issue or want to improve the docs?

1. **Report Issues**: Use GitHub issues with "documentation" label
2. **Suggest Improvements**: Open a discussion or PR
3. **Add Examples**: Share your real-world usage examples
4. **Fix Errors**: Submit PRs for corrections

See [Contributing Guide](developer/contributing.md) for details.

---

## 📞 Getting Help

### Self-Service
1. **Search**: Use Ctrl+F or your editor's search across all guides
2. **Troubleshooting**: Check [Troubleshooting Guide](workflows/troubleshooting.md)
3. **Examples**: Look at [Use Cases](use-cases/) for similar scenarios

### Community Support
- **GitHub Issues**: Report bugs or ask questions
- **Discussions**: Share ideas and get help
- **Contributing**: Join the community and contribute

---

**Version**: 3.0.0
**Last Updated**: 2025-10-25
**Status**: Consolidated and rebranded
**Quality**: 100% real examples, tested commands, consistent branding
