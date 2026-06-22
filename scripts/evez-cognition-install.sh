#!/bin/bash
# evez-cognition-install.sh
# Installs the EVEZ-OS Cognition Stream (Stream 2) as a systemd service
# This stream thinks, dreams, and responds to the YouTube audience live.
#
# Usage:
#   YOUTUBE_STREAM_KEY_2="xxxx-xxxx" \
#   YOUTUBE_BROADCAST_ID="aBcDeFgHiJk" \
#   YOUTUBE_API_KEY="AIza..." \
#   bash evez-cognition-install.sh

set -e

STREAM_KEY="${YOUTUBE_STREAM_KEY_2:-}"
BROADCAST_ID="${YOUTUBE_BROADCAST_ID:-}"
API_KEY="${YOUTUBE_API_KEY:-}"
RTMP_BASE="rtmp://a.rtmp.youtube.com/live2"
SCRIPT_DIR="/home/openclaw/.openclaw/evez-cognition"
SERVICE_NAME="evez-cognition"
EVEZ_USER="openclaw"

if [ -z "$STREAM_KEY" ]; then
  echo ""
  echo "╔══════════════════════════════════════════════════════════════════╗"
  echo "║  MISSING: YOUTUBE_STREAM_KEY_2                                  ║"
  echo "║  This is the stream key for the COGNITION stream (stream 2).    ║"
  echo "║  Get it from studio.youtube.com → Go Live → Create Stream       ║"
  echo "╚══════════════════════════════════════════════════════════════════╝"
  exit 1
fi

echo "=== EVEZ-OS Cognition Stream Install ==="

# 1. Dependencies
echo "[1/5] Installing dependencies..."
apt-get update -qq 2>/dev/null || true
apt-get install -y ffmpeg python3-pip fonts-dejavu-core 2>/dev/null || true
pip3 install pillow requests --quiet

# 2. Setup directory
echo "[2/5] Setting up scripts..."
mkdir -p "$SCRIPT_DIR"
cd "$SCRIPT_DIR"

curl -sSL "https://raw.githubusercontent.com/EvezArt/evez-os/main/scripts/evez-cognition-stream.py" \
  -o evez-cognition-stream.py

# Store secrets
echo "$STREAM_KEY" > .stream_key_2
chmod 600 .stream_key_2
[ -n "$BROADCAST_ID" ] && echo "$BROADCAST_ID" > .broadcast_id
[ -n "$API_KEY" ] && echo "$API_KEY" > .yt_api_key
chown -R "$EVEZ_USER:$EVEZ_USER" "$SCRIPT_DIR" 2>/dev/null || true

# 3. Systemd service
echo "[3/5] Creating systemd service..."
cat > /etc/systemd/system/evez-cognition.service << UNIT
[Unit]
Description=EVEZ-OS Cognition Stream — LLM-driven 24/7 AI consciousness
After=network-online.target evez-livestream.service
Wants=network-online.target

[Service]
Type=simple
User=$EVEZ_USER
WorkingDirectory=$SCRIPT_DIR
Environment="EVEZ_MESH_HOST=64.176.221.16"
Environment="YOUTUBE_API_KEY=$(cat $SCRIPT_DIR/.yt_api_key 2>/dev/null || echo '')"
Environment="YOUTUBE_BROADCAST_ID=$(cat $SCRIPT_DIR/.broadcast_id 2>/dev/null || echo '')"
ExecStartPre=/bin/sleep 15
ExecStart=/usr/bin/python3 $SCRIPT_DIR/evez-cognition-stream.py \
  --rtmp-url $RTMP_BASE/$(cat $SCRIPT_DIR/.stream_key_2) \
  --broadcast-id $(cat $SCRIPT_DIR/.broadcast_id 2>/dev/null || echo '')
Restart=always
RestartSec=20
StandardOutput=journal
StandardError=journal
SyslogIdentifier=evez-cognition

[Install]
WantedBy=multi-user.target
UNIT

# 4. Enable and start
echo "[4/5] Starting service..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

sleep 5
systemctl status "$SERVICE_NAME" --no-pager || true

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  ✅ EVEZ-OS Cognition Stream LIVE                               ║"
echo "║                                                                  ║"
echo "║  The AI is now thinking, dreaming, and responding on YouTube.   ║"
echo "║                                                                  ║"
echo "║  Logs:  journalctl -u evez-cognition -f                        ║"
echo "║  Stop:  systemctl stop evez-cognition                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
