#!/bin/bash
# ⚡ EVEZ DNS Setup — Point evez-os.ai to 64.176.221.16
# Requires: Vultr Cloud API key (different from inference key)
# Get yours at: https://my.vultr.com/settings/#settingsapi

set -e
VULTR_API_KEY="${1:?Usage: $0 <vultr-cloud-api-key>}"
IP="64.176.221.16"
DOMAIN="evez-os.ai"

echo "⚡ Creating DNS zone for $DOMAIN → $IP"

# Create DNS zone
curl -s -X POST https://api.vultr.com/v2/domains \
  -H "Authorization: Bearer $VULTR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"domain\": \"$DOMAIN\", \"ip\": \"$IP\"}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'error' in d:
    print(f'❌ Error: {d[\"error\"]}')
    sys.exit(1)
domain = d.get('domain', {})
ns = domain.get('nameservers', [])
print(f'✅ DNS zone created!')
print(f'   Nameservers: {ns}')
print()
print('⚠️  Update your domain registrar nameservers to:')
for n in ns:
    print(f'   → {n}')
"

# Add subdomain records
for sub in api consciousness daw voice spine mesh; do
  curl -s -X POST "https://api.vultr.com/v2/domains/$DOMAIN/records" \
    -H "Authorization: Bearer $VULTR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"A\", \"name\": \"$sub\", \"data\": \"$IP\"}" > /dev/null 2>&1
  echo "  → $sub.$DOMAIN → $IP"
done

echo ""
echo "⚡ Caddy will auto-provision HTTPS once DNS propagates"
echo "   Check: https://evez-os.ai (may take up to 24h for DNS)"
