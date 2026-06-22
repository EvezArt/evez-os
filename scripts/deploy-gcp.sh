#!/bin/bash
# ============================================================================
# deploy-gcp.sh — EVEZ Mesh GCP Deployment Script
#
# Prerequisites:
#   1. gcloud CLI authenticated (service account key or user login)
#   2. A GCP project exists
#   3. Terraform >= 1.7 installed
#   4. Set environment variables or pass arguments
#
# Usage:
#   export GCP_PROJECT_ID=evez-mesh-prod
#   export GCP_REGION=us-west1
#   export GCP_SA_KEY_PATH=/path/to/service-account-key.json
#   bash scripts/deploy-gcp.sh
#
# Or with arguments:
#   bash scripts/deploy-gcp.sh <project-id> <region> <sa-key-path>
#
# ============================================================================
set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

PROJECT_ID="${1:-${GCP_PROJECT_ID:-evez-mesh-prod}}"
REGION="${2:-${GCP_REGION:-us-west1}}"
SA_KEY_PATH="${3:-${GCP_SA_KEY_PATH:-}}"
TF_DIR="$(cd "$(dirname "$0")/../terraform" && pwd)"
AUTO_APPROVE="${GCP_AUTO_APPROVE:-false}"
VULTR_API_KEY="${VULTR_API_KEY:-}"
SSH_PUBLIC_KEY="${SSH_PUBLIC_KEY:-ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOPENCLAW-EVEZ-MESH evez@mesh}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Preflight Checks ────────────────────────────────────────────────────────

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         EVEZ MESH — GCP Deployment Script           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

preflight_failed=0

# Check gcloud
if ! command -v gcloud &>/dev/null; then
    echo -e "${RED}✗ gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install${NC}"
    preflight_failed=1
else
    echo -e "${GREEN}✓ gcloud CLI found: $(gcloud --version 2>&1 | head -1)${NC}"
fi

# Check Terraform
if ! command -v terraform &>/dev/null; then
    echo -e "${RED}✗ Terraform not found. Install: https://developer.hashicorp.com/terraform/install${NC}"
    preflight_failed=1
else
    echo -e "${GREEN}✓ Terraform found: $(terraform version -json 2>/dev/null | jq -r '.terraform_version' 2>/dev/null || terraform version | head -1)${NC}"
fi

# Check authentication
if [ -n "$SA_KEY_PATH" ] && [ -f "$SA_KEY_PATH" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$SA_KEY_PATH"
    echo -e "${GREEN}✓ Service account key: $SA_KEY_PATH${NC}"
elif [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
    echo -e "${GREEN}✓ GOOGLE_APPLICATION_CREDENTIALS set: $GOOGLE_APPLICATION_CREDENTIALS${NC}"
else
    # Check if gcloud is already authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
        echo -e "${GREEN}✓ gcloud authenticated as: $(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -1)${NC}"
    else
        echo -e "${YELLOW}⚠ No gcloud authentication detected.${NC}"
        echo -e "${YELLOW}  Authenticate first:${NC}"
        echo -e "${YELLOW}    gcloud auth login${NC}"
        echo -e "${YELLOW}    gcloud auth application-default login${NC}"
        echo -e "${YELLOW}  Or set GOOGLE_APPLICATION_CREDENTIALS to a service account key JSON.${NC}"
        preflight_failed=1
    fi
fi

# Check jq
if ! command -v jq &>/dev/null; then
    echo -e "${YELLOW}⚠ jq not found — some output formatting will be limited${NC}"
fi

if [ "$preflight_failed" -ne 0 ]; then
    echo ""
    echo -e "${RED}Preflight checks failed. Fix the issues above and re-run.${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Target:${NC}  Project = $PROJECT_ID | Region = $REGION"
echo ""

# ─── Enable GCP APIs ──────────────────────────────────────────────────────────

echo -e "${CYAN}━━━ Enabling GCP APIs ━━━${NC}"

REQUIRED_APIS=(
    "compute.googleapis.com"
    "dns.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "pubsub.googleapis.com"
    "storage.googleapis.com"
    "cloudscheduler.googleapis.com"
    "iam.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "accesscontextmanager.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    echo "  Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID" 2>&1 | tail -1 || true
done

echo -e "${GREEN}✓ GCP APIs enabled${NC}"
echo ""

# ─── Create GCS bucket for Terraform state (if not exists) ────────────────────

STATE_BUCKET="${PROJECT_ID}-terraform-state"
echo -e "${CYAN}━━━ Terraform State Bucket ━━━${NC}"

if gsutil ls -p "$PROJECT_ID" "gs://$STATE_BUCKET" &>/dev/null; then
    echo -e "${GREEN}✓ State bucket exists: gs://$STATE_BUCKET${NC}"
else
    echo "  Creating state bucket gs://$STATE_BUCKET..."
    gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$STATE_BUCKET" 2>&1 || true
    gsutil versioning set on "gs://$STATE_BUCKET" 2>&1 || true
    echo -e "${GREEN}✓ State bucket created with versioning${NC}"
fi
echo ""

# ─── Terraform Init ───────────────────────────────────────────────────────────

echo -e "${CYAN}━━━ Terraform Init ━━━${NC}"
cd "$TF_DIR"
terraform init -upgrade 2>&1 | tail -5
echo -e "${GREEN}✓ Terraform initialized${NC}"
echo ""

# ─── Terraform Plan ──────────────────────────────────────────────────────────

echo -e "${CYAN}━━━ Terraform Plan ━━━${NC}"

TF_VARS=(
    -var="project_id=$PROJECT_ID"
    -var="region=$REGION"
)

if [ -n "$VULTR_API_KEY" ]; then
    TF_VARS+=(-var="vultr_api_key=$VULTR_API_KEY")
fi

if [ -n "$SSH_PUBLIC_KEY" ]; then
    TF_VARS+=(-var="ssh_public_key=$SSH_PUBLIC_KEY")
fi

terraform plan "${TF_VARS[@]}" -out=tfplan 2>&1 | tail -20
echo -e "${GREEN}✓ Plan generated${NC}"
echo ""

# ─── Terraform Apply ─────────────────────────────────────────────────────────

if [ "$AUTO_APPROVE" = "true" ]; then
    echo -e "${CYAN}━━━ Terraform Apply (auto-approved) ━━━${NC}"
    terraform apply -auto-approve tfplan 2>&1 | tail -20
else
    echo -e "${YELLOW}━━━ Terraform Apply (review plan above) ━━━${NC}"
    echo -e "${YELLOW}Press Enter to apply, Ctrl+C to abort...${NC}"
    read -r
    terraform apply tfplan 2>&1 | tail -20
fi

echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# ─── Deploy EVEZ Services to Instances ───────────────────────────────────────

echo -e "${CYAN}━━━ Deploying EVEZ Services ━━━${NC}"

# Get controller IP
CONTROLLER_IP=$(terraform output -raw controller_public_ip 2>/dev/null || echo "")

if [ -n "$CONTROLLER_IP" ]; then
    echo "  Controller IP: $CONTROLLER_IP"
    echo "  Deploying services via SSH..."

    # Upload and run the deployment script on the controller
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

    gcloud compute scp "$SCRIPT_DIR/deploy-to-gcp-node.sh" \
        evez-controller:/tmp/deploy-evez.sh \
        --zone="$REGION-a" \
        --project="$PROJECT_ID" \
        --quiet 2>&1 | tail -3 || true

    gcloud compute ssh evez-controller \
        --zone="$REGION-a" \
        --project="$PROJECT_ID" \
        --command="bash /tmp/deploy-evez.sh" \
        --quiet 2>&1 | tail -10 || true
else
    echo -e "${YELLOW}⚠ Could not determine controller IP. Deploy services manually.${NC}"
fi

echo ""

# ─── Output Summary ──────────────────────────────────────────────────────────

echo -e "${CYAN}━━━ Deployment Summary ━━━${NC}"

terraform output 2>&1 || true

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        EVEZ MESH — Deployment Complete!             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Controller:  $CONTROLLER_IP"
echo -e "  SSH:         gcloud compute ssh evez-controller --zone=$REGION-a"
echo -e "  Services:    9111-9117 (mesh), 9118 (gateway), 9119 (rqns)"
echo -e "  DNS:         controller.evez-os.ai"
echo ""
