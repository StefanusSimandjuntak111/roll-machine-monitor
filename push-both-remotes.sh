#!/bin/bash
# Push to Both Remotes Script
# Pushes changes to both origin and upstream repositories

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

info() {
    echo -e "${BLUE}[PUSH]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    error "Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    error "You have uncommitted changes. Please commit them first."
    git status --short
    exit 1
fi

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
log "Current branch: $BRANCH"

# Push to origin
info "Pushing to origin..."
if git push origin "$BRANCH"; then
    log "✅ Successfully pushed to origin"
else
    error "❌ Failed to push to origin"
    exit 1
fi

# Push to upstream
info "Pushing to upstream..."
if git push upstream "$BRANCH"; then
    log "✅ Successfully pushed to upstream"
else
    error "❌ Failed to push to upstream"
    exit 1
fi

# Summary
echo ""
echo "🎉 =================================="
echo "   DUAL REPOSITORY PUSH COMPLETE"
echo "=================================="
echo "✅ Origin: git@github.com:StefanusSimandjuntak111/roll-machine-monitor.git"
echo "✅ Upstream: git@github.com:hokgt/textilindo_roll_printer.git"
echo "📋 Branch: $BRANCH"
echo "📝 Commits pushed: $(git log --oneline origin/$BRANCH..HEAD 2>/dev/null | wc -l || echo "0")"
echo ""
echo "🔗 View changes:"
echo "   Origin:   https://github.com/StefanusSimandjuntak111/roll-machine-monitor"
echo "   Upstream: https://github.com/hokgt/textilindo_roll_printer"
echo "" 