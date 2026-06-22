#!/bin/bash
# evez-activate-sa-auth.sh
# Activates service account auth for all EVEZ cron jobs and scripts.
# Run on each node after deploying the service account key.
# The key JSON should be in GCP_SERVICE_ACCOUNT_KEY env var or /etc/evez/gcp-key.json

set -e

KEY_PATH="${GCP_KEY_PATH:-/etc/evez/gcp-key.json}"

if [ -z "$GCP_SERVICE_ACCOUNT_KEY" ] && [ ! -f "$KEY_PATH" ]; then
  echo "ERROR: Set GCP_SERVICE_ACCOUNT_KEY env var or put key at $KEY_PATH"
  exit 1
fi

# Write key to secure location if from env
if [ -n "$GCP_SERVICE_ACCOUNT_KEY" ] && [ ! -f "$KEY_PATH" ]; then
  mkdir -p /etc/evez
  echo "$GCP_SERVICE_ACCOUNT_KEY" > "$KEY_PATH"
  chmod 600 "$KEY_PATH"
  echo "Key written to $KEY_PATH"
fi

# Activate the service account
gcloud auth activate-service-account --key-file="$KEY_PATH"
echo "Service account activated: $(gcloud config get-value account)"

# Set project
gcloud config set project "${GCP_PROJECT_ID:-evez-firmament}"
echo "Project set: $(gcloud config get-value project)"

# Add to ~/.bashrc so it persists across sessions
PROFILE_LINE='gcloud auth activate-service-account --key-file=/etc/evez/gcp-key.json 2>/dev/null'
if ! grep -q "evez/gcp-key.json" ~/.bashrc 2>/dev/null; then
  echo "# EVEZ GCP service account auth" >> ~/.bashrc
  echo "$PROFILE_LINE" >> ~/.bashrc
  echo "Added to ~/.bashrc"
fi

echo ""
echo "GCP auth is now permanent. No more manual re-auth needed."
gcloud compute instances list --project="${GCP_PROJECT_ID:-evez-firmament}" 2>/dev/null | head -10 || echo "(no compute access yet — waiting for GCP_SERVICE_ACCOUNT_KEY secret)"
