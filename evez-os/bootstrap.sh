#!/bin/bash
# EVEZ Bootstrap Installer
# Single-command self-propagation
# Usage: curl -sL https://raw.githubusercontent.com/EvezArt/evez-os/main/bootstrap.sh | bash

set -e

EVEZ_DIR="${EVEZ_DIR:-$HOME/evez-os}"
GITHUB_REPO="${GITHUB_REPO:-EvezArt/evez-os}"
BRANCH="${BRANCH:-main}"

echo "=== EVEZ BOOTSTRAP ==="
echo "Target: $EVEZ_DIR"

# Clone or update
if [ -d "$EVEZ_DIR/.git" ]; then
    echo "[*] Updating existing installation..."
    cd "$EVEZ_DIR"
    git pull origin "$BRANCH"
else
    echo "[*] Cloning fresh installation..."
    git clone -b "$BRANCH" "https://github.com/$GITHUB_REPO.git" "$EVEZ_DIR"
    cd "$EVEZ_DIR"
fi

# Run ignition
echo "[*] Running ignition..."
cd "$EVEZ_DIR/core"
python3 IGNITION.py --run

echo "[*] Bootstrap complete."
echo "[*] To start daemon: nohup python3 autonomous_runner.py --daemon > evez.log 2>&1 &"
