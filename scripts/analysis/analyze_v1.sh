#!/bin/bash
# V1 Codebase Analysis Script
# Analyzes aipm-cli-backup for transformation planning

V1_ROOT="/Users/nigelcopley/.project_manager/aipm-cli-backup/aipm_cli"
OUTPUT_DIR="/Users/nigelcopley/.project_manager/aipm-v2/docs/project-plan/04-development-strategy"
REPORT="$OUTPUT_DIR/v1-analysis-report.md"

echo "# V1 Codebase Analysis Report" > "$REPORT"
echo "" >> "$REPORT"
echo "**Generated**: $(date)" >> "$REPORT"
echo "**Source**: $V1_ROOT" >> "$REPORT"
echo "" >> "$REPORT"
echo "---" >> "$REPORT"
echo "" >> "$REPORT"

# Overall statistics
echo "## 📊 Overall Statistics" >> "$REPORT"
echo "" >> "$REPORT"
total_py=$(find "$V1_ROOT" -name "*.py" -type f | wc -l | tr -d ' ')
total_lines=$(find "$V1_ROOT" -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
total_size=$(du -sh "$V1_ROOT" | awk '{print $1}')

echo "- **Total Python Files**: $total_py" >> "$REPORT"
echo "- **Total Lines of Code**: $total_lines" >> "$REPORT"
echo "- **Total Size**: $total_size" >> "$REPORT"
echo "" >> "$REPORT"

# Service breakdown
echo "## 🔧 Service Breakdown" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Service | Files | Lines | Purpose |" >> "$REPORT"
echo "|---------|-------|-------|---------|" >> "$REPORT"

for service_dir in "$V1_ROOT/services"/*/ ; do
    if [ -d "$service_dir" ]; then
        service_name=$(basename "$service_dir")
        file_count=$(find "$service_dir" -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')
        line_count=$(find "$service_dir" -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        [ -z "$line_count" ] && line_count="0"

        echo "| $service_name | $file_count | $line_count | TBD |" >> "$REPORT"
    fi
done

echo "" >> "$REPORT"

# Plugin breakdown
echo "## 🔌 Plugin System" >> "$REPORT"
echo "" >> "$REPORT"

plugin_count=$(find "$V1_ROOT/plugins/domains" -name "plugin.py" 2>/dev/null | wc -l | tr -d ' ')
echo "- **Total Plugins**: $plugin_count" >> "$REPORT"
echo "" >> "$REPORT"

echo "### Plugin Domains" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Domain | Plugins |" >> "$REPORT"
echo "|--------|---------|" >> "$REPORT"

for domain_dir in "$V1_ROOT/plugins/domains"/*/ ; do
    if [ -d "$domain_dir" ]; then
        domain_name=$(basename "$domain_dir")
        plugin_count_domain=$(find "$domain_dir" -name "plugin.py" 2>/dev/null | wc -l | tr -d ' ')
        echo "| $domain_name | $plugin_count_domain |" >> "$REPORT"
    fi
done

echo "" >> "$REPORT"

# CLI commands
echo "## 📟 CLI Structure" >> "$REPORT"
echo "" >> "$REPORT"

cli_size=$(wc -l "$V1_ROOT/cli.py" 2>/dev/null | awk '{print $1}')
echo "- **cli.py Size**: $cli_size lines" >> "$REPORT"
echo "" >> "$REPORT"

# Adapters
echo "## 🔌 Adapters" >> "$REPORT"
echo "" >> "$REPORT"

if [ -d "$V1_ROOT/adapters" ]; then
    adapter_files=$(find "$V1_ROOT/adapters" -name "*.py" -type f | wc -l | tr -d ' ')
    echo "- **Adapter Files**: $adapter_files" >> "$REPORT"
fi

echo "" >> "$REPORT"

# Top-level modules
echo "## 📦 Top-Level Modules" >> "$REPORT"
echo "" >> "$REPORT"

for dir in "$V1_ROOT"/*/ ; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        if [ "$dir_name" != "__pycache__" ] && [ "$dir_name" != "services" ] && [ "$dir_name" != "plugins" ]; then
            file_count=$(find "$dir" -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')
            echo "- **$dir_name**: $file_count Python files" >> "$REPORT"
        fi
    fi
done

echo "" >> "$REPORT"

# File list by service
echo "## 📝 Detailed File Lists" >> "$REPORT"
echo "" >> "$REPORT"

echo "### Database Service Files" >> "$REPORT"
echo "\`\`\`" >> "$REPORT"
find "$V1_ROOT/services/database" -name "*.py" -type f 2>/dev/null | sed "s|$V1_ROOT/||" >> "$REPORT"
echo "\`\`\`" >> "$REPORT"
echo "" >> "$REPORT"

echo "### Context Service Files" >> "$REPORT"
echo "\`\`\`" >> "$REPORT"
find "$V1_ROOT/services/context" -name "*.py" -type f 2>/dev/null | sed "s|$V1_ROOT/||" >> "$REPORT"
echo "\`\`\`" >> "$REPORT"
echo "" >> "$REPORT"

echo "---" >> "$REPORT"
echo "" >> "$REPORT"
echo "**Analysis Complete**: $(date)" >> "$REPORT"

echo "✅ Analysis complete! Report saved to:"
echo "   $REPORT"