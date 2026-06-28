#!/bin/bash
# GCP Auth Setup for OpenClaw
# Option 1: Run this on a machine with a browser
#   ./scripts/setup-gcp-auth.sh login
# Option 2: Provide a service account key JSON
#   ./scripts/setup-gcp-auth.sh service-account <key-file.json>

GCLOUD="/tmp/google-cloud-sdk/bin/gcloud"

if [ "$1" = "login" ]; then
  echo "Starting gcloud auth login (no-browser mode)..."
  echo "Visit the URL shown, get the code, and paste it back."
  $GCLOUD auth login --no-launch-browser
  echo "Setting project..."
  $GCLOUD config set project evez-os
  echo "✅ GCP authenticated"
  echo ""
  echo "Enabling OS Login for SSH..."
  $GCLOUD compute config-ssh
  echo "✅ SSH configured for GCP instances"
elif [ "$1" = "service-account" ]; then
  KEY_FILE="${2:?Usage: $0 service-account <key-file.json>}"
  $GCLOUD auth activate-service-account --key-file="$KEY_FILE"
  $GCLOUD config set project evez-os
  echo "✅ GCP authenticated via service account"
  $GCLOUD compute config-ssh
else
  echo "Usage:"
  echo "  $0 login             # Interactive login (paste verification code)"
  echo "  $0 service-account <file>  # Use a service account key JSON"
fi
