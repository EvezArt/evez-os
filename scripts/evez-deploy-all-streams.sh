#!/bin/bash
# evez-deploy-all-streams.sh
# Deploys all 5 EVEZ-OS 24/7 YouTube streams as systemd services
# Run on the Vultr/GCP node as root or openclaw user
#
# Stream keys must be set in environment:
#   STREAM_KEY_1 through STREAM_KEY_5

set -e
EVEZ_USER="openclaw"
BASE_DIR="/home/$EVEZ_USER/.openclaw"
MESH_HOST="64.176.221.16"
RTMP_BASE="rtmp://a.rtmp.youtube.com/live2"
YT_API_KEY="${YOUTUBE_API_KEY:-}"
BROADCAST_ID="${YOUTUBE_BROADCAST_ID:-}"

declare -A STREAM_SCRIPTS=(
  [1]="evez-livestream.py"
  [2]="evez-cognition-stream.py"
  [3]="evez-cortex-stream.py"
  [4]="evez-quantum-stream.py"
  [5]="evez-dreams-stream.py"
)
declare -A STREAM_NAMES=(
  [1]="evez-mission-control"
  [2]="evez-cognition"
  [3]="evez-cortex"
  [4]="evez-quantum"
  [5]="evez-dreams"
)
declare -A STREAM_DESCS=(
  [1]="EVEZ-OS Mission Control — mesh health dashboard"
  [2]="EVEZ-OS Cognition Study — LLM inner monologue + MetaROM dreams"
  [3]="EVEZ-OS Synaptic Cortex — live neural activity visualization"
  [4]="EVEZ-OS Quantum Evolution Field — adaptive fitness dynamics"
  [5]="EVEZ-OS MetaROM Deep Dreams — generative consciousness field"
)

KEYS=(
  "${STREAM_KEY_1:-}"
  "${STREAM_KEY_2:-}"
  "${STREAM_KEY_3:-}"
  "${STREAM_KEY_4:-}"
  "${STREAM_KEY_5:-}"
)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     EVEZ-OS  — ALL 5 STREAMS DEPLOY                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Install system dependencies (once)
echo "[SETUP] Installing dependencies..."
apt-get update -qq 2>/dev/null || true
apt-get install -y ffmpeg python3-pip fonts-dejavu-core 2>/dev/null || true
pip3 install pillow requests --quiet

# 2. Create base directory
mkdir -p "$BASE_DIR/streams"
cd "$BASE_DIR/streams"

# 3. Download all scripts from GitHub
echo "[SETUP] Downloading stream scripts from GitHub..."
for script in evez-livestream.py evez-cognition-stream.py evez-cortex-stream.py evez-quantum-stream.py evez-dreams-stream.py; do
  curl -sSL "https://raw.githubusercontent.com/EvezArt/evez-os/main/scripts/$script" -o "$script"
  echo "  ✓ $script"
done
chown -R "$EVEZ_USER:$EVEZ_USER" "$BASE_DIR" 2>/dev/null || true

# 4. Install each stream as a systemd service
for i in 1 2 3 4 5; do
  SERVICE="${STREAM_NAMES[$i]}"
  SCRIPT="${STREAM_SCRIPTS[$i]}"
  DESC="${STREAM_DESCS[$i]}"
  KEY="${KEYS[$((i-1))]}"

  if [ -z "$KEY" ]; then
    echo "[SKIP] Stream $i — no key provided (set STREAM_KEY_$i)"
    continue
  fi

  echo "[STREAM $i] Installing $SERVICE..."
  echo "$KEY" > "$BASE_DIR/streams/.key_$i"
  chmod 600 "$BASE_DIR/streams/.key_$i"

  # Extra args for stream 2 (cognition) — add broadcast ID if available
  EXTRA_ARGS=""
  if [ "$i" = "2" ] && [ -n "$BROADCAST_ID" ]; then
    EXTRA_ARGS="--broadcast-id $BROADCAST_ID"
  fi

  cat > "/etc/systemd/system/$SERVICE.service" << UNIT
[Unit]
Description=$DESC
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$EVEZ_USER
WorkingDirectory=$BASE_DIR/streams
Environment="EVEZ_MESH_HOST=$MESH_HOST"
Environment="YOUTUBE_API_KEY=$YT_API_KEY"
ExecStartPre=/bin/sleep $((i * 5))
ExecStart=/usr/bin/python3 $BASE_DIR/streams/$SCRIPT \
  --rtmp-url $RTMP_BASE/\$(cat $BASE_DIR/streams/.key_$i) $EXTRA_ARGS
Restart=always
RestartSec=20
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE

[Install]
WantedBy=multi-user.target
UNIT

  systemctl daemon-reload
  systemctl enable "$SERVICE"
  systemctl restart "$SERVICE"
  echo "  ✓ $SERVICE started"
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ EVEZ-OS Streams Deployed                                ║"
echo "║                                                              ║"
echo "║  Status:  systemctl status evez-*                           ║"
echo "║  Logs:    journalctl -u evez-mission-control -f             ║"
echo "║           journalctl -u evez-cognition -f                   ║"
echo "║           journalctl -u evez-cortex -f                      ║"
echo "║           journalctl -u evez-quantum -f                     ║"
echo "║           journalctl -u evez-dreams -f                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
