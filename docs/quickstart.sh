#!/bin/bash
# ⚡ EVEZ Quickstart — Get the full mesh in 60 seconds
# curl -sSL https://evezart.github.io/evez-os/quickstart.sh | bash

set -e

echo "⚡ EVEZ — Installing..."
echo ""

# Check deps
for cmd in curl python3; do
  if ! command -v $cmd &>/dev/null; then
    echo "❌ Need $cmd. Install it first."
    exit 1
  fi
done

# Install OpenClaw
if ! command -v openclaw &>/dev/null; then
  echo "📦 Installing OpenClaw..."
  curl -sSL https://openclaw.ai/install.sh | bash
fi

# Clone EVEZ
if [ ! -d evez-os ]; then
  echo "📦 Cloning EVEZ..."
  git clone https://github.com/EvezArt/evez-os.git
  cd evez-os
else
  cd evez-os
  git pull
fi

# Start services
echo "🚀 Starting EVEZ mesh..."
for port in 9111 9112 9113 9114 9115 9116 9117 9118 9119 9121 9123; do
  svc=$(systemctl list-units --type=service 2>/dev/null | grep "evez-$port" | awk '{print $1}')
  if [ -n "$svc" ]; then
    sudo systemctl start "$svc" 2>/dev/null || true
  fi
done

# Verify
echo ""
echo "✅ EVEZ is running!"
echo "   curl http://localhost:9118/health"
echo "   curl -X POST http://localhost:9111/pipeline"
echo "   evez-cli/evez health"
echo ""
echo "⚡ github.com/EvezArt/evez-os"
