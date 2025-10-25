#!/bin/bash
# Option B: Rename existing repo and make public

set -e

echo "========================================="
echo "Option B: Rename Existing Repo to AgentPM"
echo "========================================="
echo ""

cd /Users/nigelcopley/Projects/AgentPM

echo "📋 Step 1: Manual Actions Required"
echo ""
echo "Please complete these steps on GitHub:"
echo ""
echo "1. Rename repository:"
echo "   → Go to: https://github.com/nigelcopley/aipm/settings"
echo "   → Change 'Repository name' from 'aipm' to 'agentpm'"
echo "   → Click 'Rename'"
echo ""
echo "2. Make repository public:"
echo "   → Go to: https://github.com/nigelcopley/agentpm/settings"
echo "   → Scroll to 'Danger Zone'"
echo "   → Click 'Change repository visibility'"
echo "   → Select 'Make public'"
echo "   → Confirm"
echo ""
read -p "Press ENTER when you've completed these steps..."

echo ""
echo "✓ GitHub actions completed"
echo ""

echo "🔧 Step 2: Update local git remote..."
git remote set-url origin git@github.com:nigelcopley/agentpm.git
echo "✓ Remote updated to: git@github.com:nigelcopley/agentpm.git"
echo ""

echo "📝 Step 3: Verify remote..."
git remote -v
echo ""

echo "💾 Step 4: Commit release preparation..."
git add -A

git commit -m "refactor: rebrand to AgentPM and prepare v0.1.0 for public release

- Rename package: aipm-v2 → agentpm
- Rename module: aipm_v2 → agentpm
- Add PyPI packaging (LICENSE, MANIFEST.in, release docs)
- Update all imports and references
- Clean build artifacts
- Add verification scripts

Breaking Changes:
- Package name changed (incompatible with aipm-v2)
- Module renamed: aipm_v2 → agentpm
- Repository renamed: aipm → agentpm

See MIGRATION_SUMMARY.md for complete details"

echo "✓ Changes committed"
echo ""

echo "🏷️  Step 5: Create release tag..."
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release of AgentPM"
echo "✓ Tag v0.1.0 created"
echo ""

echo "🚀 Step 6: Push to GitHub..."
git push origin main --tags
echo "✓ Pushed to GitHub"
echo ""

echo "========================================="
echo "✓ SUCCESS! Repository Setup Complete"
echo "========================================="
echo ""
echo "Your repository is now live at:"
echo "https://github.com/nigelcopley/agentpm"
echo ""
echo "Next steps:"
echo "1. Verify: https://github.com/nigelcopley/agentpm"
echo "2. Configure repository settings (topics, description)"
echo "3. Review README.md displays correctly"
echo "4. Proceed with PyPI release (see RELEASE.md)"
