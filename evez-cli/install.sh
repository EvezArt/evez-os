#!/bin/bash
# ⚡ EVEZ — One-command install
# curl -sSL https://evezart.github.io/evez-os/install.sh | bash

set -e
VERSION="1.0.0"

echo "⚡ EVEZ v${VERSION} — Installing..."
echo ""

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

# Download CLI
echo "📥 Downloading EVEZ CLI..."
curl -sSL "https://raw.githubusercontent.com/EvezArt/evez-os/main/evez-cli/evez" -o /usr/local/bin/evez 2>/dev/null || {
  mkdir -p ~/.local/bin
  curl -sSL "https://raw.githubusercontent.com/EvezArt/evez-os/main/evez-cli/evez" -o ~/.local/bin/evez
  chmod +x ~/.local/bin/evez
  echo "   Installed to ~/.local/bin/evez"
  echo "   Add to PATH: export PATH=\$PATH:~/.local/bin"
}

chmod +x /usr/local/bin/evez 2>/dev/null

echo ""
echo "✅ EVEZ CLI installed!"
echo ""
echo "   evez health       → Check mesh status"
echo "   evez dashboard     → Open web dashboard"
echo "   evez generate      → Generate music"
echo "   evez correlate     → Cross-domain correlations"
echo "   evez dream         → Trigger consciousness"
echo ""
echo "⚡ github.com/EvezArt/evez-os"
