#!/bin/bash
# verify-agent-cli-commands.sh
# Verifies all CLI commands in agent files exist in CLI-COMMAND-INVENTORY.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
INVENTORY="$PROJECT_ROOT/docs/CLI-COMMAND-INVENTORY.md"

echo "🔍 CLI Command Verification for Agent Files"
echo "=============================================="
echo ""
echo "📁 Agents Directory: $AGENTS_DIR"
echo "📋 Inventory File: $INVENTORY"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
total_files=0
files_with_issues=0
total_commands=0
invalid_commands=0

# Extract all valid commands from inventory
echo "📚 Loading valid commands from inventory..."
valid_commands=$(grep -oE "^apm [a-z-]+ [a-z-]+" "$INVENTORY" | sort -u)
echo "   Found $(echo "$valid_commands" | wc -l) unique command patterns"
echo ""

# Function to check if command exists
command_exists() {
    local cmd="$1"
    echo "$valid_commands" | grep -q "^$cmd$"
}

# Function to verify agent file
verify_agent_file() {
    local file="$1"
    local filename=$(basename "$file")
    local issues=()

    # Extract apm commands from file (skip comments and code blocks)
    local commands=$(grep -oE "apm [a-z-]+ [a-z-]+" "$file" | sort -u || true)

    if [ -z "$commands" ]; then
        return 0
    fi

    local file_command_count=0
    local file_invalid_count=0

    while IFS= read -r cmd; do
        if [ -n "$cmd" ]; then
            ((file_command_count++))
            ((total_commands++))

            # Extract base command (e.g., "apm task approve" from "apm task approve <id>")
            base_cmd=$(echo "$cmd" | sed 's/<[^>]*>//g' | sed 's/\[.*\]//g' | awk '{print $1, $2, $3}' | sed 's/ *$//')

            # Check if command exists
            if ! command_exists "$base_cmd"; then
                issues+=("$base_cmd")
                ((file_invalid_count++))
                ((invalid_commands++))
            fi
        fi
    done <<< "$commands"

    if [ ${#issues[@]} -gt 0 ]; then
        echo -e "${RED}❌ $filename${NC}"
        echo "   Invalid commands found:"
        for issue_cmd in "${issues[@]}"; do
            echo -e "   ${YELLOW}→ $issue_cmd${NC}"
        done
        echo ""
        ((files_with_issues++))
    else
        if [ $file_command_count -gt 0 ]; then
            echo -e "${GREEN}✅ $filename${NC} ($file_command_count commands verified)"
        fi
    fi

    ((total_files++))
}

# Verify main agent files
echo "🔍 Verifying main agent files..."
echo ""

# Find all .md files in agents directory (exclude .deprecated)
while IFS= read -r agent_file; do
    if [[ ! "$agent_file" =~ \.deprecated$ ]]; then
        verify_agent_file "$agent_file"
    fi
done < <(find "$AGENTS_DIR" -name "*.md" -type f)

# Summary
echo ""
echo "=============================================="
echo "📊 Verification Summary"
echo "=============================================="
echo ""
echo "Files analyzed: $total_files"
echo "Commands checked: $total_commands"
echo ""

if [ $invalid_commands -eq 0 ]; then
    echo -e "${GREEN}✅ SUCCESS: All commands are valid!${NC}"
    echo ""
    echo "Files with issues: $files_with_issues"
    echo "Invalid commands: $invalid_commands"
    exit 0
else
    echo -e "${RED}❌ FAILURE: Invalid commands found${NC}"
    echo ""
    echo "Files with issues: $files_with_issues"
    echo "Invalid commands: $invalid_commands"
    echo ""
    echo "Please fix the invalid commands listed above."
    exit 1
fi
