#!/bin/bash
# Option A: Create new clean public repo

set -e

echo "========================================="
echo "Option A: Create New Clean Public Repo"
echo "========================================="
echo ""

cd /Users/nigelcopley/Projects/AgentPM

echo "⚠️  WARNING: This creates a fresh repo with clean history"
echo "   Your existing commit history will be replaced with a single commit"
echo ""
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "📋 Step 1: Manual Action Required"
echo ""
echo "Please create a new repository on GitHub:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: agentpm"
echo "3. Description: AgentPM - Quality-Gated AI Coding Agent Enablement System"
echo "4. Visibility: PUBLIC"
echo "5. ❌ Do NOT initialize (no README, .gitignore, license)"
echo "6. Click 'Create repository'"
echo ""
read -p "Press ENTER when you've created the repository..."

echo ""
echo "✓ GitHub repository created"
echo ""

echo "🔧 Step 2: Update local git remote..."
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:nigelcopley/agentpm.git
echo "✓ Remote set to: git@github.com:nigelcopley/agentpm.git"
echo ""

echo "🧹 Step 3: Creating clean history..."
# Create orphan branch (no history)
git checkout --orphan clean-main

# Stage everything
git add -A

# Single initial commit
git commit -m "feat: initial public release of AgentPM v0.1.0

AgentPM - Quality-Gated AI Coding Agent Enablement System

A sophisticated project management system for AI coding agents with:
- 50+ specialized agents for development tasks
- Database-driven context management (SQLite)
- Quality gate enforcement (CI-001 through CI-006)
- Framework intelligence via plugin system
- Hierarchical context (Project → Work Item → Task)
- 6W analysis framework (Who/What/When/Where/Why/How)
- Multi-provider support (Claude Code, Claude Desktop, custom)
- Web dashboard with Flask
- CLI with lazy loading (<100ms startup)

Key Features:
- Persistent memory across sessions
- Type-driven workflow validation
- Dependency tracking and blocker management
- Automated quality gates
- Framework detection (Python, Django, React, Docker, pytest)
- Code amalgamation for agent context
- Professional documentation generation

Installation:
  pip install agentpm

Quick Start:
  apm init 'My Project' /path/to/project
  apm work-item create 'Feature Name' --type feature
  apm status

Documentation: See README.md
License: Apache 2.0"

echo "✓ Clean history created"
echo ""

echo "🔄 Step 4: Replace old branch..."
git branch -D main 2>/dev/null || true
git branch -m main
echo "✓ Branch renamed to main"
echo ""

echo "🏷️  Step 5: Create release tag..."
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
echo "✓ Tag v0.1.0 created"
echo ""

echo "🚀 Step 6: Push to new repository..."
git push -u origin main --force
git push origin v0.1.0
echo "✓ Pushed to GitHub"
echo ""

echo "========================================="
echo "✓ SUCCESS! New Repository Created"
echo "========================================="
echo ""
echo "Your new repository is now live at:"
echo "https://github.com/nigelcopley/agentpm"
echo ""
echo "⚠️  Note: Old commit history has been replaced with a single commit"
echo ""
echo "Next steps:"
echo "1. Verify: https://github.com/nigelcopley/agentpm"
echo "2. Configure repository settings (topics, description, website)"
echo "3. Review README.md displays correctly"
echo "4. Proceed with PyPI release (see RELEASE.md)"
