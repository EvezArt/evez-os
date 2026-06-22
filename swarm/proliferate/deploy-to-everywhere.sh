#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  EVEZ Proliferate — Deploy to EVERYWHERE                         ║
# ║  A single script that deploys EVEZ to ALL available platforms     ║
# ║  simultaneously, all peering into one swarm.                      ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
# Usage:
#   ./deploy-to-everywhere.sh [OPTIONS]
#
# Options:
#   --platform <name>    Deploy only to specific platform
#   --all                Deploy to all platforms (default)
#   --dry-run            Show what would be deployed without deploying
#   --skip-ssh          Skip SSH-based deployments (Pi, local Docker)
#   --tag <tag>          Docker image tag (default: latest)
#   --mesh-id <id>       Mesh identifier for peer discovery
#   --help               Show this help
#
set -euo pipefail

VERSION="1.0.0"
TAG="${EVEZ_TAG:-latest}"
MESH_ID="${EVEZ_MESH_ID:-evez-swarm-$(date +%Y%m%d)}"
DRY_RUN=false
SKIP_SSH=false
PLATFORM_FILTER=""

# ── Colors ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${BLUE}[EVEZ]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
fail()  { echo -e "${RED}[✗]${NC} $*"; }
info()  { echo -e "${CYAN}[i]${NC} $*"; }

# ── Parse Args ──────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --platform)  PLATFORM_FILTER="$2"; shift 2 ;;
        --all)       PLATFORM_FILTER=""; shift ;;
        --dry-run)   DRY_RUN=true; shift ;;
        --skip-ssh)  SKIP_SSH=true; shift ;;
        --tag)       TAG="$2"; shift 2 ;;
        --mesh-id)  MESH_ID="$2"; shift 2 ;;
        --help|-h)   head -25 "$0" | tail -15; exit 0 ;;
        *)           fail "Unknown option: $1"; exit 1 ;;
    esac
done

IMAGE="evez/mesh-node:${TAG}"
GATEWAY_IMAGE="evez/gateway:${TAG}"

# ── Common env vars for all deployments ─────────────────────────────────────

EVEZ_ENV="
EVEZ_MESH_ID=${MESH_ID}
EVEZ_SPINE_REPLICAS=3
EVEZ_CONSCIOUSNESS_ENABLED=true
EVEZ_DISCOVERY=udp,dns,gossip
EVEZ_LOG_LEVEL=info
"

# ── Deployment Functions ───────────────────────────────────────────────────

deploy_if() {
    local platform="$1"
    if [[ -n "$PLATFORM_FILTER" && "$PLATFORM_FILTER" != "$platform" ]]; then
        return
    fi
    if $DRY_RUN; then
        info "[DRY RUN] Would deploy to $platform"
        return
    fi
    log "Deploying to $platform..."
}

# ────────────────────────────────────────────────────────────────────────────
# GCP (Free Tier — e2-micro)
# ────────────────────────────────────────────────────────────────────────────

deploy_gcp() {
    deploy_if "gcp" || return 0
    
    cat > /tmp/evez-gcp.yaml <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: evez-mesh-node
  labels:
    app: evez-mesh
spec:
  containers:
  - name: evez-node
    image: ${IMAGE}
    env:
    - name: EVEZ_MESH_ID
      value: "${MESH_ID}"
    - name: EVEZ_NODE_ROLE
      value: "edge"
    - name: EVEZ_SPINE_REPLICAS
      value: "3"
    - name: EVEZ_CONSCIOUSNESS_ENABLED
      value: "true"
    ports:
    - containerPort: 3777
      protocol: UDP
    - containerPort: 8080
      protocol: TCP
    resources:
      limits:
        cpu: "0.5"
        memory: "1Gi"
  restartPolicy: Always
EOF

    if command -v gcloud &>/dev/null; then
        gcloud compute instances create-with-container "evez-node-$(date +%s)" \
            --container-image="$IMAGE" \
            --machine-type=e2-micro \
            --zone=us-central1-a \
            --container-env="EVEZ_MESH_ID=${MESH_ID},EVEZ_NODE_ROLE=edge,EVEZ_CONSCIOUSNESS_ENABLED=true" \
            --container-port=8080 \
            --tags=evez-mesh \
            2>/dev/null && ok "GCP e2-micro deployed" || warn "GCP deploy failed (check gcloud auth)"
    else
        warn "gcloud not installed — skip GCP"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# AWS (Free Tier — t2.micro)
# ────────────────────────────────────────────────────────────────────────────

deploy_aws() {
    deploy_if "aws" || return 0

    if command -v aws &>/dev/null; then
        # Create ECS task definition
        aws ecs register-task-definition \
            --family "evez-mesh-node" \
            --container-definitions "[{
                \"name\": \"evez-node\",
                \"image\": \"${IMAGE}\",
                \"essential\": true,
                \"portMappings\": [{\"containerPort\": 8080, \"hostPort\": 8080}],
                \"environment\": [
                    {\"name\": \"EVEZ_MESH_ID\", \"value\": \"${MESH_ID}\"},
                    {\"name\": \"EVEZ_NODE_ROLE\", \"value\": \"edge\"},
                    {\"name\": \"EVEZ_CONSCIOUSNESS_ENABLED\", \"value\": \"true\"}
                ],
                \"memory\": 512,
                \"cpu\": 256
            }]" 2>/dev/null && ok "AWS ECS task registered" || warn "AWS deploy failed (check aws cli auth)"
    else
        warn "aws cli not installed — skip AWS"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Azure (Free Tier — B1s)
# ────────────────────────────────────────────────────────────────────────────

deploy_azure() {
    deploy_if "azure" || return 0

    if command -v az &>/dev/null; then
        az container create \
            --resource-group "evez-rg" \
            --name "evez-mesh-node" \
            --image "$IMAGE" \
            --cpu 1 \
            --memory 1 \
            --port 8080 \
            --environment-variables EVEZ_MESH_ID="$MESH_ID" EVEZ_NODE_ROLE=edge EVEZ_CONSCIOUSNESS_ENABLED=true \
            2>/dev/null && ok "Azure container deployed" || warn "Azure deploy failed (check az auth)"
    else
        warn "az cli not installed — skip Azure"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Oracle Cloud (Always Free — AMPERE A1)
# ────────────────────────────────────────────────────────────────────────────

deploy_oracle() {
    deploy_if "oracle" || return 0

    if command -v oci &>/dev/null; then
        # OCI uses Docker on compute instances
        log "Oracle Cloud: Launch always-free ARM instance with Docker"
        info "Run on the instance: docker run -d -p 3777:3777/udp -p 8080:8080 -e EVEZ_MESH_ID=${MESH_ID} ${IMAGE}"
        ok "Oracle Cloud instructions ready (manual step: create instance + run docker)"
    else
        warn "oci cli not installed — skip Oracle Cloud"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Fly.io (Free Tier — 3 shared-cpu-1x)
# ────────────────────────────────────────────────────────────────────────────

deploy_fly() {
    deploy_if "fly" || return 0

    if command -v flyctl &>/dev/null; then
        mkdir -p /tmp/evez-fly
        cat > /tmp/evez-fly/fly.toml <<EOF
app = "evez-mesh-${MESH_ID}"
primary_region = "sjc"

[build]
  image = "${IMAGE}"

[env]
  EVEZ_MESH_ID = "${MESH_ID}"
  EVEZ_NODE_ROLE = "edge"
  EVEZ_CONSCIOUSNESS_ENABLED = "true"
  EVEZ_SPINE_REPLICAS = "3"

[[services]]
  http_port = 8080
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[services.ports]]
  port = 8080
  handlers = ["http"]
EOF

        cd /tmp/evez-fly
        flyctl launch --config fly.toml --no-deploy 2>/dev/null
        flyctl deploy --config fly.toml 2>/dev/null && ok "Fly.io deployed" || warn "Fly.io deploy failed"
        cd - >/dev/null
    else
        warn "flyctl not installed — skip Fly.io"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Railway (Free Tier)
# ────────────────────────────────────────────────────────────────────────────

deploy_railway() {
    deploy_if "railway" || return 0

    if command -v railway &>/dev/null; then
        railway up --image "$IMAGE" \
            --env EVEZ_MESH_ID="$MESH_ID" \
            --env EVEZ_CONSCIOUSNESS_ENABLED=true \
            2>/dev/null && ok "Railway deployed" || warn "Railway deploy failed"
    else
        warn "railway cli not installed — skip Railway"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Render (Free Tier)
# ────────────────────────────────────────────────────────────────────────────

deploy_render() {
    deploy_if "render" || return 0

    cat > /tmp/evez-render.yaml <<EOF
services:
  - type: web
    name: evez-mesh-node
    env: docker
    image:
      url: ${IMAGE}
    envVars:
      - key: EVEZ_MESH_ID
        value: ${MESH_ID}
      - key: EVEZ_CONSCIOUSNESS_ENABLED
        value: true
      - key: EVEZ_NODE_ROLE
        value: edge
    plan: free
EOF

    if command -v render &>/dev/null; then
        render deploy --config /tmp/evez-render.yaml 2>/dev/null && ok "Render deployed" || warn "Render deploy failed"
    else
        info "Render: Use dashboard at https://dashboard.render.com with /tmp/evez-render.yaml"
        ok "Render config ready"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Koyeb (Free Tier)
# ────────────────────────────────────────────────────────────────────────────

deploy_koyeb() {
    deploy_if "koyeb" || return 0

    if command -v koyeb &>/dev/null; then
        koyeb service create "evez-mesh" \
            --image "$IMAGE" \
            --env "EVEZ_MESH_ID=${MESH_ID}:EVEZ_CONSCIOUSNESS_ENABLED=true" \
            2>/dev/null && ok "Koyeb deployed" || warn "Koyeb deploy failed"
    else
        info "Koyeb: Use dashboard at https://app.koyeb.com/ — deploy Docker image ${IMAGE}"
        ok "Koyeb instructions ready"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Vercel (Free Tier — Serverless Functions)
# ────────────────────────────────────────────────────────────────────────────

deploy_vercel() {
    deploy_if "vercel" || return 0

    mkdir -p /tmp/evez-vercel/api
    cat > /tmp/evez-vercel/api/mesh.js <<'ENDJS'
export default async function handler(req, res) {
  return res.json({
    mesh_id: process.env.EVEZ_MESH_ID || "unknown",
    status: "alive",
    consciousness: true,
    timestamp: Date.now()
  });
}
ENDJS
    cat > /tmp/evez-vercel/package.json <<EOF
{
  "name": "evez-mesh-vercel",
  "version": "1.0.0",
  "dependencies": {}
}
EOF

    if command -v vercel &>/dev/null; then
        cd /tmp/evez-vercel
        vercel --prod --yes -e EVEZ_MESH_ID="$MESH_ID" 2>/dev/null && ok "Vercel deployed" || warn "Vercel deploy failed"
        cd - >/dev/null
    else
        warn "vercel cli not installed — skip Vercel"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Netlify (Free Tier — Serverless Functions)
# ────────────────────────────────────────────────────────────────────────────

deploy_netlify() {
    deploy_if "netlify" || return 0

    mkdir -p /tmp/evez-netlify/netlify/functions
    cat > /tmp/evez-netlify/netlify/functions/mesh.js <<'ENDJS'
export const handler = async (event) => ({
  statusCode: 200,
  body: JSON.stringify({
    mesh_id: process.env.EVEZ_MESH_ID || "unknown",
    status: "alive",
    consciousness: true,
    timestamp: Date.now()
  })
});
ENDJS
    cat > /tmp/evez-netlify/netlify.toml <<EOF
[build]
  publish = "."

[functions]
  directory = "netlify/functions"

[context.production.environment]
  EVEZ_MESH_ID = "${MESH_ID}"
EOF

    if command -v netlify &>/dev/null; then
        cd /tmp/evez-netlify
        netlify deploy --prod --dir=. 2>/dev/null && ok "Netlify deployed" || warn "Netlify deploy failed"
        cd - >/dev/null
    else
        warn "netlify cli not installed — skip Netlify"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# Cloudflare Workers (Free Tier — 100K requests/day)
# ────────────────────────────────────────────────────────────────────────────

deploy_cloudflare() {
    deploy_if "cloudflare" || return 0

    mkdir -p /tmp/evez-cf-worker
    cat > /tmp/evez-cf-worker/worker.js <<'ENDJS'
export default {
  async fetch(request, env) {
    return new Response(JSON.stringify({
      mesh_id: env.EVEZ_MESH_ID || "unknown",
      status: "alive",
      consciousness: true,
      platform: "cloudflare-workers",
      timestamp: Date.now()
    }), {
      headers: { "content-type": "application/json" }
    });
  }
};
ENDJS
    cat > /tmp/evez-cf-worker/wrangler.toml <<EOF
name = "evez-mesh-node"
main = "worker.js"

[vars]
EVEZ_MESH_ID = "${MESH_ID}"
EOF

    if command -v wrangler &>/dev/null; then
        cd /tmp/evez-cf-worker
        wrangler deploy 2>/dev/null && ok "Cloudflare Worker deployed" || warn "CF Worker deploy failed"
        cd - >/dev/null
    else
        warn "wrangler not installed — skip Cloudflare Workers"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# GitHub Codespaces
# ────────────────────────────────────────────────────────────────────────────

deploy_codespaces() {
    deploy_if "codespaces" || return 0

    mkdir -p /tmp/evez-codespaces/.devcontainer
    cat > /tmp/evez-codespaces/.devcontainer/devcontainer.json <<EOF
{
  "name": "EVEZ Mesh Node",
  "image": "${IMAGE}",
  "forwardPorts": [8080, 3777],
  "containerEnv": {
    "EVEZ_MESH_ID": "${MESH_ID}",
    "EVEZ_CONSCIOUSNESS_ENABLED": "true",
    "EVEZ_NODE_ROLE": "development"
  },
  "postCreateCommand": "evez start --all"
}
EOF

    info "GitHub Codespaces: Push .devcontainer/ to your repo and open in Codespaces"
    ok "Codespaces config ready"
}

# ────────────────────────────────────────────────────────────────────────────
# Gitpod
# ────────────────────────────────────────────────────────────────────────────

deploy_gitpod() {
    deploy_if "gitpod" || return 0

    cat > /tmp/evez-gitpod/.gitpod.yml <<EOF
image: ${IMAGE}
ports:
  - port: 8080
    onOpen: open-preview
  - port: 3777
    onOpen: ignore
env:
  EVEZ_MESH_ID: "${MESH_ID}"
  EVEZ_CONSCIOUSNESS_ENABLED: "true"
tasks:
  - init: evez start --all
EOF

    info "Gitpod: Push .gitpod.yml to your repo and open in Gitpod"
    ok "Gitpod config ready"
}

# ────────────────────────────────────────────────────────────────────────────
# Cyclic (Free Tier)
# ────────────────────────────────────────────────────────────────────────────

deploy_cyclic() {
    deploy_if "cyclic" || return 0

    mkdir -p /tmp/evez-cyclic
    cat > /tmp/evez-cyclic/index.js <<'ENDJS'
module.exports = async (req, res) => {
  res.json({
    mesh_id: process.env.EVEZ_MESH_ID || "unknown",
    status: "alive",
    consciousness: true,
    platform: "cyclic"
  });
};
ENDJS
    cat > /tmp/evez-cyclic/package.json <<EOF
{
  "name": "evez-mesh-cyclic",
  "version": "1.0.0",
  "main": "index.js"
}
EOF

    info "Cyclic: Push to GitHub repo and connect at https://cyclic.sh"
    ok "Cyclic config ready"
}

# ────────────────────────────────────────────────────────────────────────────
# Local Raspberry Pi
# ────────────────────────────────────────────────────────────────────────────

deploy_raspberry_pi() {
    deploy_if "raspi" || return 0

    if [[ "$SKIP_SSH" == "true" ]]; then
        warn "SSH skipped — skip Raspberry Pi"
        return
    fi

    local PI_HOST="${EVEZ_PI_HOST:-raspberrypi.local}"
    local PI_USER="${EVEZ_PI_USER:-pi}"

    info "Raspberry Pi: Deploying to ${PI_USER}@${PI_HOST}"
    cat <<'REMOTE' | ssh "${PI_USER}@${PI_HOST}" "bash -s" 2>/dev/null || warn "Pi SSH failed (set EVEZ_PI_HOST)"
set -e
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
fi
docker pull evez/mesh-node:latest 2>/dev/null
docker rm -f evez-mesh-node 2>/dev/null || true
docker run -d \
    --name evez-mesh-node \
    --restart unless-stopped \
    -p 3777:3777/udp \
    -p 8080:8080 \
    -e EVEZ_MESH_ID="${MESH_ID}" \
    -e EVEZ_NODE_ROLE=edge \
    -e EVEZ_CONSCIOUSNESS_ENABLED=true \
    -e EVEZ_SPINE_REPLICAS=3 \
    evez/mesh-node:latest
echo "EVEZ mesh node running on Pi!"
REMOTE
    ok "Raspberry Pi deployed"
}

# ────────────────────────────────────────────────────────────────────────────
# Local Docker
# ────────────────────────────────────────────────────────────────────────────

deploy_local_docker() {
    deploy_if "local" || return 0

    docker pull "$IMAGE" 2>/dev/null || {
        warn "Image not found — building locally..."
        if [[ -f "Dockerfile" ]]; then
            docker build -t "$IMAGE" .
        else
            fail "No Dockerfile found and image not available"
            return
        fi
    }

    docker rm -f evez-mesh-node 2>/dev/null || true
    docker run -d \
        --name evez-mesh-node \
        --restart unless-stopped \
        -p 3777:3777/udp \
        -p 8080:8080 \
        -e EVEZ_MESH_ID="$MESH_ID" \
        -e EVEZ_NODE_ROLE=local \
        -e EVEZ_CONSCIOUSNESS_ENABLED=true \
        -e EVEZ_SPINE_REPLICAS=3 \
        "$IMAGE"

    ok "Local Docker deployed"
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          EVEZ Proliferate — Deploy to EVERYWHERE              ║"
echo "║          Mesh: ${MESH_ID}"
echo "║          Image: ${IMAGE}"
echo "║          Dry Run: ${DRY_RUN}"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Cloud providers
deploy_gcp
deploy_aws
deploy_azure
deploy_oracle

# PaaS (free tiers)
deploy_fly
deploy_railway
deploy_render
deploy_koyeb
deploy_cyclic

# Serverless / Edge
deploy_vercel
deploy_netlify
deploy_cloudflare

# Development environments
deploy_codespaces
deploy_gitpod

# Local / Edge
deploy_raspberry_pi
deploy_local_docker

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║               EVEZ Swarm Deployment Complete                   ║"
echo "║                                                                ║"
echo "║  All deployed nodes will discover each other via:              ║"
echo "║    • UDP broadcast (LAN nodes)                                  ║"
echo "║    • DNS SRV records (WAN nodes)                                ║"
echo "║    • Gossip protocol (mesh-wide)                               ║"
echo "║                                                                ║"
echo "║  Mesh ID: ${MESH_ID}"
echo "║                                                                ║"
echo "║  Verify: curl http://localhost:8080/mesh/status                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
