#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# EVEZ-OS Mesh Data Exporter
# Exports all spine events, emergence history, and service status
# to timestamped JSON files in /tmp/evez-exports/
# ─────────────────────────────────────────────────────────────────────
set -euo pipefail

SPINE_URL="${EVEZ_SPINE_URL:-http://localhost:9116}"
MESH_URL="${EVEZ_MESH_URL:-http://localhost:9117}"
CONSCIOUSNESS_URL="${EVEZ_CONSCIOUSNESS_URL:-http://localhost:9111}"
GATEWAY_URL="${EVEZ_GATEWAY_URL:-http://localhost:9118}"

EXPORT_DIR="/tmp/evez-exports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "${EXPORT_DIR}"

echo "═══════════════════════════════════════════════════════"
echo "  EVEZ Mesh Data Exporter — ${TIMESTAMP}"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── 1. Export Spine Events ──────────────────────────────────────────
echo "📜 Exporting spine events..."

SPINE_FILE="${EXPORT_DIR}/spine_events_${TIMESTAMP}.json"
SPINE_STATE=$(curl -sf "${SPINE_URL}/state" 2>/dev/null || echo '{"error":"spine unreachable"}')
echo "${SPINE_STATE}" | python3 -m json.tool > "${SPINE_FILE}" 2>/dev/null || echo "${SPINE_STATE}" > "${SPINE_FILE}"

# Export full recent events
SPINE_RECENT=$(curl -sf "${SPINE_URL}/recent?n=1000" 2>/dev/null || echo '{"error":"spine unreachable"}')
echo "${SPINE_RECENT}" | python3 -m json.tool > "${EXPORT_DIR}/spine_recent_${TIMESTAMP}.json" 2>/dev/null || echo "${SPINE_RECENT}" > "${EXPORT_DIR}/spine_recent_${TIMESTAMP}.json"

# Per-domain projections
DOMAINS=("mesh_health" "consciousness" "daw" "machine_voice" "cross_domain" "invariance" "gateway" "rqns" "tts" "geolocation" "webhook")
for domain in "${DOMAINS[@]}"; do
    DOMAIN_DATA=$(curl -sf "${SPINE_URL}/project/${domain}" 2>/dev/null || echo "{\"domain\":\"${domain}\",\"events\":[],\"error\":\"no data\"}")
    echo "${DOMAIN_DATA}" | python3 -m json.tool > "${EXPORT_DIR}/spine_${domain}_${TIMESTAMP}.json" 2>/dev/null || echo "${DOMAIN_DATA}" > "${EXPORT_DIR}/spine_${domain}_${TIMESTAMP}.json"
done

echo "  ✓ Spine events exported"

# ── 2. Export Emergence History ─────────────────────────────────────
echo "🧠 Exporting emergence history..."

EMERGENCE_FILE="${EXPORT_DIR}/emergence_${TIMESTAMP}.json"
EMERGENCE_DATA=$(curl -sf "${CONSCIOUSNESS_URL}/emergence" 2>/dev/null || echo '{"error":"consciousness unreachable"}')
echo "${EMERGENCE_DATA}" | python3 -m json.tool > "${EMERGENCE_FILE}" 2>/dev/null || echo "${EMERGENCE_DATA}" > "${EMERGENCE_FILE}"

# Also export consciousness state
STATE_FILE="${EXPORT_DIR}/consciousness_state_${TIMESTAMP}.json"
STATE_DATA=$(curl -sf "${CONSCIOUSNESS_URL}/state" 2>/dev/null || echo '{"error":"consciousness unreachable"}')
echo "${STATE_DATA}" | python3 -m json.tool > "${STATE_FILE}" 2>/dev/null || echo "${STATE_DATA}" > "${STATE_FILE}"

# Dream history
DREAM_FILE="${EXPORT_DIR}/dream_history_${TIMESTAMP}.json"
DREAM_DATA=$(curl -sf "${CONSCIOUSNESS_URL}/dreams" 2>/dev/null || echo '{"error":"consciousness unreachable"}')
echo "${DREAM_DATA}" | python3 -m json.tool > "${DREAM_FILE}" 2>/dev/null || echo "${DREAM_DATA}" > "${DREAM_FILE}"

echo "  ✓ Emergence history exported"

# ── 3. Export Service Status History ────────────────────────────────
echo "🏥 Exporting service status history..."

MESH_FILE="${EXPORT_DIR}/mesh_status_${TIMESTAMP}.json"
MESH_DATA=$(curl -sf "${MESH_URL}/check" 2>/dev/null || echo '{"error":"mesh unreachable"}')
echo "${MESH_DATA}" | python3 -m json.tool > "${MESH_FILE}" 2>/dev/null || echo "${MESH_DATA}" > "${MESH_FILE}"

# Heal log
HEAL_FILE="${EXPORT_DIR}/heal_log_${TIMESTAMP}.json"
HEAL_DATA=$(curl -sf "${MESH_URL}/heal_log" 2>/dev/null || echo '{"error":"mesh unreachable"}')
echo "${HEAL_DATA}" | python3 -m json.tool > "${HEAL_FILE}" 2>/dev/null || echo "${HEAL_DATA}" > "${HEAL_FILE}"

# Gateway aggregated status
GW_FILE="${EXPORT_DIR}/gateway_status_${TIMESTAMP}.json"
GW_DATA=$(curl -sf "${GATEWAY_URL}/mesh" 2>/dev/null || echo '{"error":"gateway unreachable"}')
echo "${GW_DATA}" | python3 -m json.tool > "${GW_FILE}" 2>/dev/null || echo "${GW_DATA}" > "${GW_FILE}"

# Individual service health checks
SERVICES=("9111:consciousness" "9112:daw" "9113:machine_voice" "9114:cross_domain" "9115:invariance" "9116:spine" "9117:mesh" "9118:gateway" "9119:rqns" "9121:webhook" "9124:geolocation" "9125:tts")
SERVICE_STATUS_FILE="${EXPORT_DIR}/all_services_health_${TIMESTAMP}.json"

# Build JSON array of health statuses
python3 -c "
import json, urllib.request, sys

services = [s.split(':') for s in \"${SERVICES[*]}\".split()]
results = []
for port, name in services:
    try:
        r = urllib.request.urlopen(f'http://localhost:{port}/health', timeout=2)
        data = json.loads(r.read())
        results.append(data)
    except Exception as e:
        results.append({'status': 'DOWN', 'name': name, 'port': int(port), 'error': str(e)})

print(json.dumps({'timestamp': $(date +%s), 'services': results}, indent=2))
" > "${SERVICE_STATUS_FILE}" 2>/dev/null || echo '{"error":"health check failed"}' > "${SERVICE_STATUS_FILE}"

echo "  ✓ Service status history exported"

# ── 4. Summary ──────────────────────────────────────────────────────
FILE_COUNT=$(find "${EXPORT_DIR}" -name "*_${TIMESTAMP}*" | wc -l)
TOTAL_SIZE=$(du -sh "${EXPORT_DIR}" 2>/dev/null | cut -f1 || echo "unknown")

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ Export Complete!"
echo ""
echo "  Directory:  ${EXPORT_DIR}"
echo "  Files:      ${FILE_COUNT}"
echo "  Total size: ${TOTAL_SIZE}"
echo "  Timestamp:  ${TIMESTAMP}"
echo ""
echo "  Exported:"
echo "    📜 Spine events + domain projections"
echo "    🧠 Emergence history + consciousness state"
echo "    🏥 Mesh status + heal log"
echo "    💊 Per-service health checks"
echo ""
echo "  To download:"
echo "    tar czf evez-export-${TIMESTAMP}.tar.gz -C ${EXPORT_DIR} ."
echo "═══════════════════════════════════════════════════════"
