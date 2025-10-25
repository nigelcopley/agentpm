#!/bin/bash

# Git Hooks Installation Script for AIPM Validation Pipeline
# Sets up pre-commit and pre-push validation hooks
# Part of Track 3: Validation Pipeline Setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[HOOKS]${NC} $1"; }
log_success() { echo -e "${GREEN}[HOOKS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[HOOKS]${NC} $1"; }
log_error() { echo -e "${RED}[HOOKS]${NC} $1"; }

log_info "Installing AIPM validation Git hooks..."

# Check if we're in a Git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    log_error "Not in a Git repository"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
mkdir -p "$HOOKS_DIR"

# Source hooks directory
SOURCE_HOOKS_DIR="$PROJECT_ROOT/.githooks"

if [ ! -d "$SOURCE_HOOKS_DIR" ]; then
    log_error "Source hooks directory not found: $SOURCE_HOOKS_DIR"
    exit 1
fi

# Install pre-commit hook
if [ -f "$SOURCE_HOOKS_DIR/pre-commit" ]; then
    cp "$SOURCE_HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    log_success "✅ Pre-commit hook installed"
else
    log_warning "Pre-commit hook source not found"
fi

# Install pre-push hook
if [ -f "$SOURCE_HOOKS_DIR/pre-push" ]; then
    cp "$SOURCE_HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    log_success "✅ Pre-push hook installed"
else
    log_warning "Pre-push hook source not found"
fi

# Test hooks installation
log_info "Testing hooks installation..."

if [ -x "$HOOKS_DIR/pre-commit" ]; then
    log_success "✅ Pre-commit hook is executable"
else
    log_error "❌ Pre-commit hook not executable"
fi

if [ -x "$HOOKS_DIR/pre-push" ]; then
    log_success "✅ Pre-push hook is executable"
else
    log_error "❌ Pre-push hook not executable"
fi

echo
log_info "Git hooks installation complete!"
echo
echo "Installed hooks:"
echo "  - pre-commit: Runs lightweight validation before commits"
echo "  - pre-push: Runs quick validation before pushes"
echo
echo "To test the hooks:"
echo "  apm validate precommit  # Test pre-commit validation"
echo "  apm validate quick      # Test pre-push validation"
echo
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"