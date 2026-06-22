#!/bin/bash
# evez-gcp-auth-hardening.sh
# Makes GCP authentication permanent via service account (no manual re-auth needed)
# Run this ONCE on any machine with existing GCP access to generate the key.
# Then paste the JSON into GitHub Secret GCP_SERVICE_ACCOUNT_KEY.

set -e

PROJECT_ID="${GCP_PROJECT_ID:-evez-firmament}"
SA_NAME="evez-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="/tmp/evez-sa-key.json"

echo "=== EVEZ GCP Auth Hardening ==="
echo "Project: $PROJECT_ID"
echo "Service Account: $SA_EMAIL"
echo ""

# 1. Create service account (idempotent)
echo "[1/4] Creating service account..."
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="EVEZ Deploy Automation" \
  --project="$PROJECT_ID" 2>/dev/null || echo "  (already exists, continuing)"

# 2. Assign required roles
echo "[2/4] Assigning IAM roles..."
for ROLE in \
  roles/compute.admin \
  roles/storage.admin \
  roles/iam.serviceAccountUser \
  roles/logging.admin \
  roles/monitoring.admin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$ROLE" --quiet
  echo "  + $ROLE"
done

# 3. Generate JSON key
echo "[3/4] Generating key file..."
gcloud iam service-accounts keys create "$KEY_FILE" \
  --iam-account="$SA_EMAIL" \
  --project="$PROJECT_ID"
echo "  Key saved to: $KEY_FILE"

# 4. Output for GitHub Secret
echo ""
echo "[4/4] Done. Copy the JSON below into GitHub Secret GCP_SERVICE_ACCOUNT_KEY:"
echo "  Repo: https://github.com/EvezArt/evez-os/settings/secrets/actions"
echo ""
echo "=== BEGIN GCP_SERVICE_ACCOUNT_KEY ==="
cat "$KEY_FILE"
echo ""
echo "=== END GCP_SERVICE_ACCOUNT_KEY ==="
echo ""
echo "After setting the secret, the GCP deploy workflow will auto-run."
echo "Clean up: rm $KEY_FILE"
