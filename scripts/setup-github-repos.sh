#!/bin/bash
# Set up GitHub repos, webhooks, and deploy keys once gh is authenticated
# Run: ./scripts/setup-github-repos.sh

echo "=== GitHub Repo Setup ==="
echo ""

# 1. Add SSH key to GitHub (if not already)
echo "1. Ensuring SSH key is on GitHub..."
gh ssh-key list | grep -q "openclaw@vultr-knot" && echo "  ✅ SSH key already on GitHub" || {
  gh ssh-key add ~/.ssh/id_ed25519.pub --title "openclaw@vultr-knot-$(date +%Y%m%d)"
  echo "  ✅ SSH key added"
}

# 2. Set up workspace repo remote
echo ""
echo "2. Setting up workspace repo..."
if ! git remote get-url origin &>/dev/null; then
  gh repo create EvezArt/openclaw-workspace --private --source=. --push --description "OpenClaw workspace & fleet config"
  echo "  ✅ Created private repo and pushed"
else
  echo "  ✅ Remote already configured: $(git remote get-url origin)"
fi

# 3. Clone/update key EVEZ repos locally
echo ""
echo "3. Cloning key EVEZ repos..."
REPOS=(
  "EVEZ888/openclaw"
  "EVEZ888/openclaws"
  "EvezArt/evez-os"
  "EvezArt/evez-infrastructure"
  "EvezArt/evez-site"
)
for repo in "${REPOS[@]}"; do
  REPO_DIR="/home/openclaw/repos/${repo##*/}"
  if [ -d "$REPO_DIR" ]; then
    echo "  ⏩ $repo already cloned at $REPO_DIR"
  else
    mkdir -p /home/openclaw/repos
    gh repo clone "$repo" "$REPO_DIR" -- --depth=1
    echo "  ✅ Cloned $repo"
  fi
done

echo ""
echo "=== Done ==="
