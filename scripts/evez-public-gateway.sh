#!/usr/bin/env bash
# ============================================================================
# evez-public-gateway.sh — Expose OpenClaw Gateway to Mobile Devices
# ============================================================================
# This script uses 'expose' or 'tailscale' to create a public URL for your
# local OpenClaw gateway, allowing you to access the dashboard from your phone.
# ============================================================================

set -euo pipefail

GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
MODE="${1:-expose}" # default to expose

echo "🚀 EVEZ-OS — Public Gateway Access"
echo "--------------------------------"

if [[ "$MODE" == "expose" ]]; then
    echo ">>> Using 'expose' to create a temporary public URL..."
    if ! command -v expose &>/dev/null; then
        echo "Error: 'expose' tool not found. Please install it or use 'tailscale' mode." >&2
        exit 1
    fi
    expose "$GATEWAY_PORT"
elif [[ "$MODE" == "tailscale" ]]; then
    echo ">>> Using 'tailscale' to create a permanent mesh URL..."
    if ! command -v tailscale &>/dev/null; then
        echo "Error: 'tailscale' tool not found." >&2
        exit 1
    fi
    TS_STATUS=$(tailscale status --json | jq -r '.BackendState')
    if [[ "$TS_STATUS" != "Running" ]]; then
        echo "Error: Tailscale is not running. Please run 'tailscale up'." >&2
        exit 1
    fi
    TS_IP=$(tailscale ip -4)
    echo "✅ Your gateway is accessible on your tailnet at:"
    echo "   http://${TS_IP}:${GATEWAY_PORT}"
    echo ""
    echo "Tip: Install Tailscale on your phone and visit the URL above."
else
    echo "Usage: $0 {expose|tailscale}"
    exit 1
fi
