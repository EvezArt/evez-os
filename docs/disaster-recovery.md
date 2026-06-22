# EVEZ Disaster Recovery Plan

**Version:** 1.0 | **Last Updated:** 2026-06-22 | **Classification:** Production Critical

---

## 1. Overview

This plan covers recovery procedures for the EVEZ mesh running on Google Cloud Platform (5 nodes). The mesh is designed for self-healing — most failures resolve automatically. This document covers scenarios that exceed automatic recovery.

## 2. Architecture Summary

| Node | Role | Zone | Services |
|------|------|------|----------|
| evez-alpha | Core | us-central1-a | Consciousness Engine (:9111), Cross-Domain (:9114) |
| evez-beta | Core | us-central1-a | DAW Agent (:9112), Machine Voice (:9113) |
| evez-gamma | Core | us-central1-b | Invariance Battery (:9115), Event Spine (:9116) |
| evez-delta | Core | us-central1-b | Mesh Health (:9117), Gateway (:9118), RQNS (:9119) |
| evez-omega | Monitor | us-central1-a | Prometheus, Grafana, Alertmanager (e2-micro free tier) |

## 3. Failure Scenarios & Recovery

### 3.1 Single Node Failure

**Detection:** Mesh Health service detects via heartbeat timeout (< 60s)
**Auto-recovery:** systemd auto-restart + mesh watchdog heals services
**Manual intervention needed:** Only if node itself is unreachable

```bash
# Check node status
gcloud compute instances list --filter="tags.items=evez-mesh"

# SSH to failed node
gcloud compute ssh <node-name> --zone=<zone>

# Check systemd services
systemctl list-units --type=service --state=failed

# Restart all EVEZ services
systemctl restart evez-*

# If node won't boot, reset
gcloud compute instances reset <node-name> --zone=<zone>
```

**RTO:** < 5 minutes (auto-heal) | < 15 minutes (manual reset)

### 3.2 Multi-Node Failure (2-3 nodes)

**Severity:** HIGH — mesh degraded but functional

```bash
# Identify surviving nodes
gcloud compute instances list --filter="status=RUNNING AND tags.items=evez-mesh"

# Rebalance: move critical services to surviving nodes
# 1. SSH to a surviving node
# 2. Start the missing services:
#    python3 /opt/evez/services/consciousness-engine/server.py &
#    python3 /opt/evez/services/event-spine/server.py &

# Recreate failed nodes
for node in evez-alpha evez-beta; do
    gcloud compute instances create ${node} \
        --zone=us-central1-a \
        --machine-type=e2-standard-4 \
        --image-family=debian-12 --image-project=debian-cloud \
        --network=evez-mesh-vpc \
        --metadata-from-file=startup-script=scripts/evez-startup.sh \
        --tags=evez-mesh \
        --project=evez-firmament
done
```

**RTO:** < 30 minutes

### 3.3 Full Mesh Failure (all 5 nodes)

**Severity:** CRITICAL

1. **Don't panic.** Data is in GCP Persistent Disks + Event Spine.
2. Recreate from bootstrap script:
   ```bash
   ./scripts/gcp-bootstrap.sh evez-firmament us-central1
   ```
3. Restore Event Spine from latest GCS backup:
   ```bash
   gsutil cp gs://evez-firmament-backups/spine/latest.json /var/lib/evez/spine/
   ```
4. Verify mesh health:
   ```bash
   curl http://<lb-ip>:9117/mesh
   ```

**RTO:** < 2 hours

### 3.4 Data Corruption (Event Spine)

The Event Spine uses **hash-chained append-only** storage. Corruption is detectable.

```bash
# Verify spine integrity
curl http://<node-ip>:9116/verify

# If corrupted, restore from GCS backup
gsutil ls gs://evez-firmament-backups/spine/
gsutil cp gs://evez-firmament-backups/spine/spine-<timestamp>.json /var/lib/evez/spine/events.json

# Re-verify
curl http://<node-ip>:9116/verify
```

### 3.5 DNS Failure

If evez-os.ai DNS is not resolving:

1. Check DNS records at registrar
2. Point A record to GCP Load Balancer IP:
   ```bash
   LB_IP=$(gcloud compute forwarding-rules describe evez-forwarding-rule \
       --region=us-central1 --format="value(IPAddress)")
   echo "Set evez-os.ai A record to: ${LB_IP}"
   ```
3. Wait for DNS propagation (up to 48h, usually < 5m with Cloudflare)

## 4. Backup Strategy

| What | Where | Frequency | Retention |
|------|-------|-----------|-----------|
| Event Spine | GCS: `gs://evez-firmament-backups/spine/` | Every 6 hours | 30 days |
| VM Snapshots | GCP Snapshots | Daily | 7 days |
| Prometheus Data | GCS: `gs://evez-firmament-backups/prometheus/` | Daily | 30 days |
| Config Files | Git (GitHub) | Every push | Infinite |
| Service Code | Git + Docker Registry | Every push | Tagged |

### Automated Backup Script

```bash
# Add to crontab on evez-omega
0 */6 * * * /opt/evez/scripts/backup-spine.sh
0 2 * * * /opt/evez/scripts/backup-prometheus.sh
```

## 5. Monitoring for Disasters

- **GCP Cloud Monitoring:** Uptime checks on all node IPs
- **Prometheus Alertmanager:** Fires on NodeDown > 2m
- **Webhook Relay:** Routes alerts to TTS/voice + email
- **Grafana:** Dashboard at http://evez-omega:3000

### Critical Alert Chain

```
Node Down → Prometheus → Alertmanager → Webhook Relay (:9121) → TTS (:9125) → Voice Alert
                                                           → Email to Steven
```

## 6. Escalation Matrix

| Time Since Detection | Action | Owner |
|---------------------|--------|-------|
| 0-5 min | Auto-heal attempts | Mesh Health Service |
| 5-15 min | Alert fired, manual investigation | Steven (on-call) |
| 15-60 min | Node reset/recreate | Steven |
| 1-2 hours | Full mesh rebuild from bootstrap | Steven |
| 2+ hours | Engage GCP Support | Steven + Google Support |

## 7. Testing the DR Plan

### Monthly DR Drill

1. Simulate single node failure: `gcloud compute instances stop evez-delta --zone=us-central1-b`
2. Verify auto-heal: Watch Mesh Health dashboard for recovery
3. Restore node: `gcloud compute instances start evez-delta --zone=us-central1-b`
4. Document results

### Quarterly Full DR Test

1. Stop all 5 nodes
2. Run `./scripts/gcp-bootstrap.sh` from scratch
3. Restore Event Spine from GCS backup
4. Verify all 11 services operational
5. Document RTO achieved

## 8. Contact Information

- **Steven Maggard:** rubikspubes70@gmail.com
- **GCP Project:** evez-firmament
- **GCP Support:** https://console.cloud.google.com/support
- **GitHub:** https://github.com/EvezArt (code backup)
