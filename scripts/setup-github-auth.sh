#!/bin/bash
# GitHub Auth Setup for OpenClaw
# Run: ./scripts/setup-github-auth.sh <your-github-pat>

TOKEN="${1:?Usage: $0 <github-pat>}"
echo "$TOKEN" | gh auth login --hostname github.com --git-protocol ssh --with-token
gh auth status
echo "✅ GitHub CLI authenticated"
echo ""
echo "Adding SSH key to GitHub..."
gh ssh-key add ~/.ssh/id_ed25519.pub --title "openclaw@vultr-knot-$(date +%Y%m%d)"
echo "✅ SSH key added to GitHub"
echo ""
echo "Testing SSH connection..."
ssh -T git@github.com
