#!/bin/bash
# EVEZ Skills Publish Script
# Run this after: clawhub login (or git auth)

set -e

SKILLS_DIR="/root/.openclaw/workspace/evez-skills"
REPO_NAME="evez-skills"

echo "=== EVEZ Skills Publish ==="

# Check auth
if ! clawhub whoami &>/dev/null; then
    echo "❌ Not logged in to ClawHub"
    echo "Run: clawhub login"
    exit 1
fi

echo "✅ ClawHub authenticated"

# Navigate to skills
cd "$SKILLS_DIR"

# Publish each skill
for skill in *-skill; do
    echo "📦 Publishing: $skill"
    cd "$skill"
    
    # Check for required files
    if [ ! -f "SKILL.md" ] || [ ! -f "_meta.json" ]; then
        echo "  ⚠️ Missing SKILL.md or _meta.json"
        cd ..
        continue
    fi
    
    # Publish (using clawhub publish if available, else note)
    echo "  → Would publish: $(cat _meta.json | grep displayName | cut -d'"' -f4)"
    
    cd ..
done

echo ""
echo "=== Manual Steps Required ==="
echo "1. clawhub login (if not done)"
echo "2. For each skill: clawhub publish ./<skill-dir>/"
echo ""
echo "Or push to GitHub and share links:"
echo "  git init evez-skills"
echo "  git add ."
echo "  git commit -m 'EVEZ skills pack'"
echo "  git remote add origin https://github.com/EvezArt/evez-skills.git"
echo "  git push -u origin main"

echo ""
echo "=== Skills Ready ==="
ls -d *-skill/ | wc -l
echo "skills packaged and ready"