#!/bin/bash
# evez-livestream-install.sh
# Installs and starts the EVEZ-OS 24/7 YouTube livestream as a systemd service.
# Run on the Vultr/GCP node as root or with sudo.
#
# Usage: YOUTUBE_STREAM_KEY="xxxx-xxxx-xxxx-xxxx-xxxx" bash evez-livestream-install.sh

set -e

STREAM_KEY="${YOUTUBE_STREAM_KEY:-}"
RTMP_BASE="rtmp://a.rtmp.youtube.com/live2"
SCRIPT_DIR="/home/openclaw/.openclaw/evez-livestream"
SERVICE_NAME="evez-livestream"
EVEZ_USER="openclaw"

if [ -z "$STREAM_KEY" ]; then
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  MISSING: YOUTUBE_STREAM_KEY                                ║"
  echo "║                                                              ║"
  echo "║  Get it from: studio.youtube.com/channel/UC/livestreaming   ║"
  echo "║  Then run:                                                   ║"
  echo "║  YOUTUBE_STREAM_KEY='xxxx-xxxx' bash evez-livestream-install.sh ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  exit 1
fi

echo "=== EVEZ-OS Livestream Install ==="
echo "Stream key: ${STREAM_KEY:0:8}..."

# 1. Install dependencies
echo "[1/5] Installing dependencies..."
apt-get update -qq 2>/dev/null || true
apt-get install -y ffmpeg python3-pip fonts-dejavu-core 2>/dev/null || \
  (yum install -y ffmpeg python3-pip 2>/dev/null || true)
pip3 install pillow requests --quiet

# 2. Create script directory
echo "[2/5] Setting up scripts..."
mkdir -p "$SCRIPT_DIR"
cd "$SCRIPT_DIR"

# Download the renderer script from GitHub
curl -sSL "https://raw.githubusercontent.com/EvezArt/evez-os/main/scripts/evez-livestream.py" \
  -o evez-livestream.py

# Store stream key securely
echo "$STREAM_KEY" > .stream_key
chmod 600 .stream_key
chown -R "$EVEZ_USER:$EVEZ_USER" "$SCRIPT_DIR" 2>/dev/null || true

# 3. Create systemd service
echo "[3/5] Creating systemd service..."
cat > /etc/systemd/system/evez-livestream.service << UNIT
[Unit]
Description=EVEZ-OS 24/7 YouTube Livestream
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$EVEZ_USER
WorkingDirectory=$SCRIPT_DIR
Environment="EVEZ_MESH_HOST=64.176.221.16"
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 $SCRIPT_DIR/evez-livestream.py \\
  --rtmp-url $RTMP_BASE/$(cat $SCRIPT_DIR/.stream_key)
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
SyslogIdentifier=evez-livestream

[Install]
WantedBy=multi-user.target
UNIT

# 4. Enable and start
echo "[4/5] Enabling service..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# 5. Status check
echo "[5/5] Checking status..."
sleep 5
systemctl status "$SERVICE_NAME" --no-pager || true

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ EVEZ-OS Livestream STARTED                              ║"
echo "║                                                              ║"
echo "║  Check status: systemctl status evez-livestream             ║"
echo "║  View logs:    journalctl -u evez-livestream -f             ║"
echo "║  Stop:         systemctl stop evez-livestream               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
