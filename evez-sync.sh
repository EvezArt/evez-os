#!/bin/bash
# EVEZ GitHub Sync
# Commits ledger changes to GitHub for persistence

cd /root/.openclaw/workspace

# Files to track
TRACKED_FILES=(
    "evez-os/core/ledger/spine.jsonl"
    "evez-os/core/ledger/chain.jsonl"
    "evez-os/core/context/"
    "evez-os/core/trunk/state.json"
    "memory/"
)

# Commit message
MSG="EVEZ sync $(date -u +%Y-%m-%dT%H%M%Z)"

# Add tracked files
for f in "${TRACKED_FILES[@]}"; do
    git add "$f" 2>/dev/null
done

# Commit if there are changes
if git diff --cached --quiet; then
    echo "No changes to sync"
else
    git commit -m "$MSG"
    git push origin main 2>/dev/null || git push origin master 2>/dev/null
    echo "Synced to GitHub"
fi
