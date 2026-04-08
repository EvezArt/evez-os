#!/bin/bash
# EVEZ Repo Monitor - Run on demand or via cron
# Checks key EvezArt repos for activity

REPOS="evez-os Evez666 maes evez-agentnet evez-autonomous-ledger nexus"
DATE=$(date +%Y-%m-%d)

echo "=== EVEZ Repo Monitor | $DATE ==="
for repo in $REPOS; do
  data=$(gh api repos/EvezArt/$repo -F per_page=1 --jq '.stargazers_count,.open_issues_count,.updated_at[:10]' 2>/dev/null)
  stars=$(echo $data | cut -d' ' -f1)
  issues=$(echo $data | cut -d' ' -f2)
  updated=$(echo $data | cut -d' ' -f3)
  echo "$repo | ⭐$stars | Issues: $issues | Updated: $updated"
done
echo "=================================="