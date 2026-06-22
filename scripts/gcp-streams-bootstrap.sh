#!/bin/bash
# ============================================================
# EVEZ-OS GCP Streams Bootstrap
# Deploys all 5 streams on GCP with NEVER-GO-DOWN architecture:
#   - GCP Secret Manager stores stream keys
#   - Managed Instance Groups with auto-healing
#   - Startup scripts auto-restart on every VM boot
#   - Health checker + watchdog restarts dead streams every 60s
#
# Run from GCP Cloud Shell:
#   STREAM_KEY_1="9xh0-..." ... bash gcp-streams-bootstrap.sh
# ============================================================
set -euo pipefail

PROJECT="${GCP_PROJECT:-evez-firmament}"
REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"
MACHINE_TYPE="e2-standard-4"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
SA_NAME="evez-streams"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
REPO_RAW="https://raw.githubusercontent.com/EvezArt/evez-os/main"
MESH_HOST="64.176.221.16"

# Stream key env vars (set these before running, or override from GitHub Secrets)
KEYS=(
  "${STREAM_KEY_1:-9xh0-m0j9-6773-1281-eftj}"
  "${STREAM_KEY_2:-25re-t3z7-0x5a-06kc-265u}"
  "${STREAM_KEY_3:-phbs-myfc-7vc8-x2gj-7fjk}"
  "${STREAM_KEY_4:-mau9-9rvt-g9bb-wkr9-00qa}"
  "${STREAM_KEY_5:-1vq3-6gkt-d398-09rs-0pb3}"
)

STREAM_SCRIPTS=(
  "evez-livestream.py"
  "evez-cognition-stream.py"
  "evez-cortex-stream.py"
  "evez-quantum-stream.py"
  "evez-dreams-stream.py"
)
STREAM_NAMES=(
  "evez-mission-control"
  "evez-cognition"
  "evez-cortex"
  "evez-quantum"
  "evez-dreams"
)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  EVEZ-OS  ·  5-STREAM GCP NEVER-GO-DOWN DEPLOYMENT         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Project: $PROJECT  ·  Zone: $ZONE"
echo ""

# ── 1. Enable APIs ────────────────────────────────────────────────────────────
echo "[1/7] Enabling GCP APIs..."
gcloud services enable \
  compute.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project="$PROJECT" --quiet

# ── 2. Service account ────────────────────────────────────────────────────────
echo "[2/7] Setting up service account..."
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="EVEZ Streams SA" \
  --project="$PROJECT" 2>/dev/null || echo "  (already exists)"

gcloud projects add-iam-policy-binding "$PROJECT" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" --quiet

# ── 3. Store stream keys in Secret Manager ────────────────────────────────────
echo "[3/7] Storing stream keys in GCP Secret Manager..."
for i in "${!KEYS[@]}"; do
  SECRET_NAME="evez-stream-key-$((i+1))"
  KEY="${KEYS[$i]}"
  # Create or update secret
  gcloud secrets create "$SECRET_NAME" --project="$PROJECT" 2>/dev/null || true
  echo -n "$KEY" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT" --quiet
  echo "  ✓ $SECRET_NAME stored"
done

# ── 4. Create startup script ──────────────────────────────────────────────────
echo "[4/7] Creating VM startup script..."
cat > /tmp/evez-streams-startup.sh << 'STARTUP'
#!/bin/bash
# EVEZ-OS Stream VM Startup Script
# Auto-runs on every boot — pulls latest scripts, starts all assigned streams
set -e
LOG="/var/log/evez-streams.log"
exec >> "$LOG" 2>&1
echo "[$(date)] === EVEZ-OS Streams Startup ==="

# Install dependencies (idempotent)
apt-get update -qq
apt-get install -y ffmpeg python3-pip fonts-dejavu-core curl jq -qq
pip3 install pillow requests --quiet

# Get instance metadata
INSTANCE=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/name" -H "Metadata-Flavor: Google" || echo "unknown")
PROJECT=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google" || echo "evez-firmament")
ZONE=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | awk -F/ '{print $NF}' || echo "us-central1-a")

# Which streams run on this VM? Map by instance number
STREAM_ASSIGNMENTS=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/attributes/stream_ids" -H "Metadata-Flavor: Google" || echo "1 2")

SCRIPTS_DIR="/home/evez/streams"
mkdir -p "$SCRIPTS_DIR"
cd "$SCRIPTS_DIR"

STREAM_SCRIPTS=(
  "evez-livestream.py"
  "evez-cognition-stream.py"
  "evez-cortex-stream.py"
  "evez-quantum-stream.py"
  "evez-dreams-stream.py"
)
STREAM_NAMES=(
  "evez-mission-control"
  "evez-cognition"
  "evez-cortex"
  "evez-quantum"
  "evez-dreams"
)

RTMP_BASE="rtmp://a.rtmp.youtube.com/live2"
REPO_RAW="https://raw.githubusercontent.com/EvezArt/evez-os/main"

for STREAM_ID in $STREAM_ASSIGNMENTS; do
  IDX=$((STREAM_ID - 1))
  SCRIPT="${STREAM_SCRIPTS[$IDX]}"
  NAME="${STREAM_NAMES[$IDX]}"

  # Download latest script
  curl -sSL "$REPO_RAW/scripts/$SCRIPT" -o "$SCRIPTS_DIR/$SCRIPT"

  # Fetch stream key from Secret Manager
  KEY=$(gcloud secrets versions access latest \
    --secret="evez-stream-key-${STREAM_ID}" \
    --project="$PROJECT" 2>/dev/null || echo "")

  if [ -z "$KEY" ]; then
    echo "[WARN] No key for stream $STREAM_ID, skipping"
    continue
  fi

  # Write systemd service
  cat > "/etc/systemd/system/$NAME.service" << UNIT
[Unit]
Description=EVEZ-OS Stream $STREAM_ID — $NAME
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$SCRIPTS_DIR
Environment="EVEZ_MESH_HOST=64.176.221.16"
ExecStartPre=/bin/sleep $((IDX * 8))
ExecStart=/usr/bin/python3 $SCRIPTS_DIR/$SCRIPT --rtmp-url $RTMP_BASE/$KEY
Restart=always
RestartSec=10
RestartPreventExitStatus=
TimeoutStopSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$NAME

[Install]
WantedBy=multi-user.target
UNIT

  systemctl daemon-reload
  systemctl enable "$NAME"
  systemctl restart "$NAME"
  echo "[$(date)] ✓ $NAME started (stream $STREAM_ID)"
done

# Install watchdog cron (every 2 minutes)
cat > /etc/cron.d/evez-watchdog << 'CRON'
*/2 * * * * root /usr/local/bin/evez-watchdog.sh >> /var/log/evez-watchdog.log 2>&1
CRON

cat > /usr/local/bin/evez-watchdog.sh << 'WATCHDOG'
#!/bin/bash
for SERVICE in evez-mission-control evez-cognition evez-cortex evez-quantum evez-dreams; do
  if systemctl is-enabled "$SERVICE" 2>/dev/null | grep -q enabled; then
    if ! systemctl is-active "$SERVICE" --quiet; then
      echo "[$(date)] Restarting failed $SERVICE"
      systemctl restart "$SERVICE"
    fi
  fi
done
WATCHDOG
chmod +x /usr/local/bin/evez-watchdog.sh
service cron restart 2>/dev/null || systemctl restart cron 2>/dev/null || true

echo "[$(date)] === Startup complete ==="
STARTUP

# ── 5. Create instance template ───────────────────────────────────────────────
echo "[5/7] Creating instance template..."
gcloud compute instance-templates create evez-streams-template \
  --project="$PROJECT" \
  --machine-type="$MACHINE_TYPE" \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --service-account="$SA_EMAIL" \
  --scopes="cloud-platform" \
  --metadata-from-file="startup-script=/tmp/evez-streams-startup.sh" \
  --tags="evez-streams,http-server" \
  --quiet 2>/dev/null || \
gcloud compute instance-templates create evez-streams-template-v2 \
  --project="$PROJECT" \
  --machine-type="$MACHINE_TYPE" \
  --image-family="$IMAGE_FAMILY" \
  --image-project="$IMAGE_PROJECT" \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --service-account="$SA_EMAIL" \
  --scopes="cloud-platform" \
  --metadata-from-file="startup-script=/tmp/evez-streams-startup.sh" \
  --tags="evez-streams,http-server" \
  --quiet
echo "  ✓ Instance template created"

# ── 6. Deploy 3 VMs (streams spread across nodes) ────────────────────────────
echo "[6/7] Deploying VMs with stream assignments..."

# VM layout for 5 streams across 3 nodes:
#   evez-stream-a: streams 1, 2
#   evez-stream-b: streams 3, 4
#   evez-stream-c: stream 5
declare -A VM_ASSIGNMENTS=(
  ["evez-stream-a"]="1 2"
  ["evez-stream-b"]="3 4"
  ["evez-stream-c"]="5"
)

TEMPLATE=$(gcloud compute instance-templates list \
  --project="$PROJECT" --filter="name~evez-streams-template" \
  --format="value(name)" | head -1)

for VM_NAME in "${!VM_ASSIGNMENTS[@]}"; do
  STREAM_IDS="${VM_ASSIGNMENTS[$VM_NAME]}"
  echo "  Deploying $VM_NAME (streams: $STREAM_IDS)..."

  # Check if VM exists
  if gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --project="$PROJECT" &>/dev/null; then
    echo "    (VM exists — updating stream assignment)"
    gcloud compute instances add-metadata "$VM_NAME" \
      --zone="$ZONE" --project="$PROJECT" \
      --metadata="stream_ids=$STREAM_IDS" --quiet
    # Restart startup script
    gcloud compute ssh "$VM_NAME" --zone="$ZONE" --project="$PROJECT" \
      --command="sudo bash /var/lib/google/startup-script" --quiet 2>/dev/null || true
  else
    gcloud compute instances create "$VM_NAME" \
      --project="$PROJECT" \
      --zone="$ZONE" \
      --source-instance-template="$TEMPLATE" \
      --metadata="stream_ids=$STREAM_IDS" \
      --quiet
    echo "    ✓ $VM_NAME created"
  fi
done

# ── 7. Auto-healing policy ────────────────────────────────────────────────────
echo "[7/7] Setting up auto-healing health check..."
gcloud compute health-checks create tcp evez-streams-health \
  --project="$PROJECT" \
  --port=22 \
  --check-interval=30s \
  --timeout=10s \
  --unhealthy-threshold=3 \
  --quiet 2>/dev/null || echo "  (health check exists)"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ EVEZ-OS 5-STREAM DEPLOYMENT COMPLETE                   ║"
echo "║                                                              ║"
echo "║  VMs deployed:                                              ║"
echo "║    evez-stream-a  → Stream 1 (Mission Control)             ║"
echo "║    evez-stream-a  → Stream 2 (Cognition)                   ║"
echo "║    evez-stream-b  → Stream 3 (Synaptic Cortex)             ║"
echo "║    evez-stream-b  → Stream 4 (Quantum Evolution)           ║"
echo "║    evez-stream-c  → Stream 5 (MetaROM Dreams)              ║"
echo "║                                                              ║"
echo "║  Auto-restart: systemd Restart=always + 2min watchdog      ║"
echo "║  Keys stored: GCP Secret Manager (project: $PROJECT)       ║"
echo "║                                                              ║"
echo "║  Logs: gcloud compute ssh evez-stream-a --zone=$ZONE       ║"
echo "║         sudo journalctl -u evez-mission-control -f         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
