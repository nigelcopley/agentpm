# GitHub Setup Options for AgentPM

**Current Situation:**
- Existing private repo: `git@github.com:nigelcopley/aipm.git`
- Rebranded to: AgentPM
- Need public repo for PyPI release

---

## 🎯 Recommendation: **Option B** - Rename & Make Public

**Why Option B is better:**
- ✅ Preserves complete git history (development journey)
- ✅ Shows professional evolution (aipm → agentpm)
- ✅ Less work - just rename and flip visibility
- ✅ Maintains any existing issues/stars
- ✅ GitHub automatically redirects old URLs

**When to choose Option A instead:**
- ❌ Git history contains sensitive data (API keys, passwords)
- ❌ Messy commit history you want to hide
- ❌ Want a completely fresh start

---

## Option B: Rename Existing Repo (RECOMMENDED)

### Step 1: Rename on GitHub (2 minutes)

**Via Web UI:**
1. Go to: https://github.com/nigelcopley/agentpm/settings
2. Scroll to "Repository name"
3. Change: `aipm` → `agentpm`
4. Click "Rename"

**GitHub will:**
- ✅ Automatically redirect `aipm` → `agentpm`
- ✅ Update clone URLs
- ✅ Preserve all issues, PRs, stars

### Step 2: Update Local Remote (30 seconds)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Update remote URL
git remote set-url origin git@github.com:nigelcopley/agentpm.git

# Verify
git remote -v
# Should show: git@github.com:nigelcopley/agentpm.git
```

### Step 3: Make Repository Public (1 minute)

**Via Web UI:**
1. Go to: https://github.com/nigelcopley/agentpm/settings
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"
4. Select "Make public"
5. Confirm by typing repository name
6. Click "I understand, change repository visibility"

### Step 4: Push Changes (1 minute)

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Stage all release preparation changes
git add -A

# Commit
git commit -m "refactor: rebrand to AgentPM and prepare v0.1.0 for public release

- Rename package: aipm-v2 → agentpm
- Rename module: aipm_v2 → agentpm
- Add PyPI packaging (LICENSE, MANIFEST.in)
- Add release documentation and verification scripts
- Update all imports and references
- Clean build artifacts

Breaking Changes:
- Package name changed (incompatible with aipm-v2)
- Module renamed: aipm_v2 → agentpm

See MIGRATION_SUMMARY.md for complete details"

# Create release tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release of AgentPM"

# Push everything
git push origin main --tags
```

### Step 5: Verify (30 seconds)

```bash
# Check repo online
open https://github.com/nigelcopley/agentpm

# Verify it's public and shows correct content
```

---

## Option A: Create New Clean Repo (Alternative)

### Step 1: Create New Repo on GitHub

**Via Web UI:**
1. Go to: https://github.com/new
2. Repository name: `agentpm`
3. Description: "AgentPM - Quality-Gated AI Coding Agent Enablement System"
4. Visibility: **Public**
5. ❌ Don't initialize (no README, .gitignore, license)
6. Click "Create repository"

### Step 2: Update Local Remote

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin git@github.com:nigelcopley/agentpm.git

# Verify
git remote -v
```

### Step 3: Clean History (Optional)

If you want to squash all history into one clean commit:

```bash
# Create orphan branch (no history)
git checkout --orphan clean-main

# Stage everything
git add -A

# Single initial commit
git commit -m "feat: initial public release of AgentPM v0.1.0

AgentPM - Quality-Gated AI Coding Agent Enablement System

Features:
- 50+ specialized agents for development tasks
- Database-driven context management
- Quality gate enforcement (CI-001 through CI-006)
- Framework intelligence via plugin system
- Hierarchical context (Project → Work Item → Task)
- 6W analysis framework (Who/What/When/Where/Why/How)
- Multi-provider support (Claude Code, Claude Desktop)
- Web dashboard with Flask
- CLI with lazy loading (<100ms startup)

See README.md for complete documentation."

# Delete old main
git branch -D main

# Rename clean-main to main
git branch -m main
```

### Step 4: Force Push to New Repo

```bash
# Push to new repo
git push -u origin main --force

# Add release tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
git push origin v0.1.0
```

---

## 🔍 Decision Helper

**Choose Option B if:**
- ✅ Your git history is clean (no secrets)
- ✅ You want to show development evolution
- ✅ You value preserving commit history
- ✅ You want the easiest path

**Choose Option A if:**
- ❌ Git history has sensitive data
- ❌ You want a single clean "Initial release" commit
- ❌ You prefer a fresh start
- ❌ Commit history is messy/embarrassing

---

## 🔒 Before Making Public: Security Check

Run this to check for potential secrets:

```bash
cd /Users/nigelcopley/Projects/AgentPM

# Check for common secret patterns
git log -p | grep -i "password\|api.key\|secret\|token\|credential" | head -20

# Check .env files in history
git log --all --full-history --oneline -- '*.env'

# Check for large files that shouldn't be there
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -20
```

If you find secrets:
1. **Don't make public yet**
2. Use BFG Repo Cleaner or `git filter-repo` to remove them
3. Force push cleaned history
4. Then make public

---

## 📋 Recommended Workflow (Option B)

```bash
# 1. Rename repo on GitHub web UI
#    aipm → agentpm

# 2. Update local remote
cd /Users/nigelcopley/Projects/AgentPM
git remote set-url origin git@github.com:nigelcopley/agentpm.git

# 3. Commit release preparation
git add -A
git commit -m "refactor: rebrand to AgentPM and prepare v0.1.0 for public release"
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# 4. Push
git push origin main --tags

# 5. Make public on GitHub web UI
#    Settings → Danger Zone → Change visibility → Public

# 6. Verify
open https://github.com/nigelcopley/agentpm
```

---

## ⚠️ Important Notes

**After making public:**
- Repository is **permanent** (can't be truly deleted, only archived)
- All commit history is **visible**
- Think before pushing sensitive data
- Once secrets are pushed, consider them compromised

**Repository settings to configure:**
1. Add topics: `python`, `cli`, `ai`, `agents`, `project-management`
2. Set description: "Quality-Gated AI Coding Agent Enablement System"
3. Set website: https://agentpm.dev (when ready)
4. Enable Issues
5. Enable Discussions (optional)
6. Configure branch protection for `main` (optional)

---

**Recommendation**: Use **Option B** unless you have specific security concerns.

**Next step**: Rename repo on GitHub, then run the commands above.
