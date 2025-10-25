#!/bin/bash
# Link all WI-141 documentation to database

cd /Users/nigelcopley/.project_manager/aipm-v2

# Design system docs
apm document add --entity-type=work_item --entity-id=141 \
  --file-path="docs/architecture/web/design-system.md" \
  --type=design --title="APM (Agent Project Manager) Web Design System" \
  --no-validate-file

apm document add --entity-type=work_item --entity-id=141 \
  --file-path="docs/architecture/web/component-snippets.md" \
  --type=design --title="Component Library Snippets" \
  --no-validate-file

apm document add --entity-type=work_item --entity-id=141 \
  --file-path="docs/architecture/web/quick-start.md" \
  --type=developer_guide --title="Quick Start Guide" \
  --no-validate-file

apm document add --entity-type=work_item --entity-id=141 \
  --file-path="docs/architecture/web/implementation-roadmap.md" \
  --type=implementation_plan --title="Implementation Roadmap" \
  --no-validate-file

echo "✅ Core documentation linked"

# Session summaries
for summary in SESSION_COMPLETION_SUMMARY.md FINAL_SESSION_REPORT.md COMPREHENSIVE_SESSION_SUMMARY.md PARALLEL_EXECUTION_FINAL_REPORT.md; do
  if [ -f "$summary" ]; then
    apm document add --entity-type=work_item --entity-id=141 \
      --file-path="$summary" \
      --type=session_summary --title="${summary%.md}" \
      --no-validate-file
  fi
done

echo "✅ All documentation linked to WI-141"
