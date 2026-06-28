#!/bin/bash
# Deploy SSH public key to all fleet nodes
# Run after GCP auth is set up: ./scripts/deploy-ssh-keys.sh

SSH_PUB_KEY=$(cat ~/.ssh/id_ed25519.pub)
GCLOUD="/tmp/google-cloud-sdk/bin/gcloud"
PROJECT="evez-os"

NODES=(
  "gcp-west:34.53.51.34"
  "gcp-small:34.23.192.213" 
  "gcp-power:35.222.248.151"
  "gcp-openclaw:136.113.102.152"
  "gcp-knot:136.118.144.227"
)

echo "🔑 Deploying SSH key to fleet nodes..."
echo "Key: $SSH_PUB_KEY"
echo ""

for node in "${NODES[@]}"; do
  NAME="${node%%:*}"
  IP="${node##*:}"
  echo "--- $NAME ($IP) ---"
  
  # Try gcloud compute ssh (requires OS Login)
  # Or try direct SSH with password/key
  # Or try gcloud compute instances add-metadata
  
  echo "  Attempting gcloud compute ssh..."
  $GCLOUD compute ssh "$NAME" --project=$PROJECT --zone=us-central1-a --command="mkdir -p ~/.ssh && echo '$SSH_PUB_KEY' >> ~/.ssh/authorized_keys && sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys && echo 'Key added'" 2>&1 && echo "  ✅ $NAME done" && continue
  
  echo "  ❌ Failed on $NAME — may need manual setup"
done

echo ""
echo "Fleet SSH key deployment complete."
