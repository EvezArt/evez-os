#!/bin/bash
# ============================================================================
# ci-apply.sh — Terraform CI/CD wrapper for GitHub Actions
# Expects GOOGLE_APPLICATION_CREDENTIALS to point to a SA key JSON file
# ============================================================================
set -euo pipefail

ACTION="${1:-plan}"  # plan | apply | destroy
PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID must be set}"
REGION="${GCP_REGION:-us-west1}"
STATE_BUCKET="${PROJECT_ID}-terraform-state"
TF_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== EVEZ Terraform CI/CD ==="
echo "  Action:  $ACTION"
echo "  Project: $PROJECT_ID"
echo "  Region:  $REGION"

cd "$TF_DIR"

# Init with dynamic backend config
terraform init \
    -upgrade \
    -backend-config="bucket=$STATE_BUCKET" \
    -backend-config="prefix=terraform/state"

# Build variable flags
TF_VARS=(-var="project_id=$PROJECT_ID" -var="region=$REGION")

if [ -n "${VULTR_API_KEY:-}" ]; then
    TF_VARS+=(-var="vultr_api_key=$VULTR_API_KEY")
fi

if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
    TF_VARS+=(-var="ssh_public_key=$SSH_PUBLIC_KEY")
fi

case "$ACTION" in
    plan)
        terraform plan "${TF_VARS[@]}" -out=tfplan
        echo "=== Plan complete ==="
        ;;
    apply)
        terraform plan "${TF_VARS[@]}" -out=tfplan
        terraform apply -auto-approve tfplan
        echo "=== Apply complete ==="
        # Output key values for GitHub Actions
        terraform output -json > /tmp/tf-outputs.json 2>/dev/null || true
        ;;
    destroy)
        terraform destroy -auto-approve "${TF_VARS[@]}"
        echo "=== Destroy complete ==="
        ;;
    *)
        echo "Unknown action: $ACTION (use plan|apply|destroy)"
        exit 1
        ;;
esac
