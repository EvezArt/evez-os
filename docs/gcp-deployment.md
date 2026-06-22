# EVEZ Mesh — GCP Deployment Guide

> **Zero-to-running on Google Cloud Platform with zero manual steps once credentials exist.**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start — One Command Deploy](#quick-start)
4. [Authentication Setup](#authentication-setup)
5. [Deployment Methods](#deployment-methods)
   - [Method 1: Terraform (Full Infrastructure)](#method-1-terraform)
   - [Method 2: Docker Compose (Cloud-Agnostic)](#method-2-docker-compose)
   - [Method 3: Kubernetes / GKE](#method-3-gke)
   - [Method 4: Cloud-Init (Single Instance)](#method-4-cloud-init)
   - [Method 5: GitHub Actions CI/CD](#method-5-cicd)
6. [Service Reference](#service-reference)
7. [DNS & Networking](#dns--networking)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Security Hardening](#security-hardening)
10. [Cost Estimates](#cost-estimates)
11. [Troubleshooting](#troubleshooting)
12. [Destroying Resources](#destroying-resources)

---

## Architecture Overview

```
                    ┌─────────────────────────────┐
                    │     GCP Project             │
                    │   evez-mesh-prod            │
                    └──────────┬──────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
   │ us-west1 │         │us-central1  │        │   Vultr    │
   │ Primary  │         │ Secondary   │        │  Primary   │
   ├──────────┤         ├─────────────┤        └─────────────┘
   │Controller│         │ Worker-2    │           evez-os-worker
   │(e2-std2) │         │ (e2-medium) │
   │Worker-0  │         └─────────────┘
   │Worker-1  │
   │Free-Tier │
   │(e2-micro)│
   └──────────┘
```

### EVEZ Service Mesh

| Port  | Service               | Description                            |
|-------|-----------------------|----------------------------------------|
| 9111  | Consciousness Engine   | 7-system autonomous cognition          |
| 9112  | DAW Agent              | Breakcore/dubstep/phonk synthesis      |
| 9113  | Machine Voice          | 5-stage robotic speech synthesis       |
| 9114  | Cross-Domain Engine    | Cross-domain correlation discovery     |
| 9115  | Invariance Battery     | Runtime invariant verification         |
| 9116  | Event Spine            | Append-only immutable event log        |
| 9117  | Mesh Health            | Self-healing orchestrator              |
| 9118  | Gateway                | Single API entry point                 |
| 9119  | RQNS Pipeline          | Reactive neuromorphic sensing          |
| 9121  | Webhook Relay          | State change notifications            |
| 9123  | Metrics                | Prometheus-compatible exporter         |
| 9124  | Geolocation            | Free IP/location APIs *(extras)*      |
| 9125  | TTS Service            | Machine voice TTS pipeline *(extras)* |

---

## Prerequisites

| Tool          | Version   | Install                                          |
|---------------|-----------|--------------------------------------------------|
| gcloud CLI    | Latest    | `https://cloud.google.com/sdk/docs/install`       |
| Terraform     | >= 1.7    | `https://developer.hashicorp.com/terraform/install`|
| Docker        | >= 24     | `https://docs.docker.com/get-docker/`              |
| kubectl       | >= 1.28   | `gcloud components install kubectl`               |
| jq            | Latest    | `sudo apt install jq`                              |

### GCP Project Setup

1. Create a project: `gcloud projects create evez-mesh-prod`
2. Link billing: `gcloud billing projects link evez-mesh-prod --billing-account=YOUR_BA`
3. Enable APIs:
   ```bash
   gcloud services enable compute dns monitoring logging pubsub storage \
     cloudscheduler iam cloudresourcemanager accesscontextmanager \
     --project=evez-mesh-prod
   ```

---

## Quick Start

```bash
# 1. Authenticate (one-time)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json

# 2. Deploy everything
bash scripts/deploy-gcp.sh evez-mesh-prod us-west1

# 3. Check health
curl http://$(terraform -chdir=terraform output -raw controller_public_ip):9118/health
```

---

## Authentication Setup

### Option A: Service Account Key (CI/CD Recommended)

1. Create a service account:
   ```bash
   gcloud iam service-accounts create evez-deployer \
     --display-name="EVEZ Deployer" \
     --project=evez-mesh-prod
   ```

2. Grant required roles:
   ```bash
   for ROLE in compute.admin dns.admin monitoring.admin logging.admin \
     pubsub.admin storage.admin iam.securityAdmin cloudscheduler.admin \
     accesscontextmanager.policyAdmin serviceusage.serviceUsageAdmin; do
     gcloud projects add-iam-policy-binding evez-mesh-prod \
       --member="serviceAccount:evez-deployer@evez-mesh-prod.iam.gserviceaccount.com" \
       --role="roles/$ROLE"
   done
   ```

3. Create and download key:
   ```bash
   gcloud iam service-accounts keys create evez-deployer-key.json \
     --iam-account=evez-deployer@evez-mesh-prod.iam.gserviceaccount.com
   ```

4. Use it:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=./evez-deployer-key.json
   ```

### Option B: User Authentication (Local Development)

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project evez-mesh-prod
```

### Option C: Workload Identity (GKE Recommended)

For GKE, use Workload Identity instead of keys:

```bash
# Create K8s SA bound to GCP SA
kubectl create serviceaccount evez-mesh-sa -n evez-mesh

gcloud iam service-accounts add-iam-policy-binding \
  evez-deployer@evez-mesh-prod.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:evez-mesh-prod.svc.id.goog[evez-mesh/evez-mesh-sa]"

kubectl annotate serviceaccount evez-mesh-sa \
  -n evez-mesh \
  iam.gke.io/gcp-service-account=evez-deployer@evez-mesh-prod.iam.gserviceaccount.com
```

---

## Deployment Methods

### Method 1: Terraform

Full infrastructure provisioning — VPC, subnets, firewall, instances, DNS, monitoring.

```bash
cd terraform

# Initialize (first time or after backend changes)
terraform init -upgrade \
  -backend-config="bucket=evez-mesh-prod-terraform-state" \
  -backend-config="prefix=terraform/state"

# Plan
terraform plan \
  -var="project_id=evez-mesh-prod" \
  -var="region=us-west1" \
  -out=tfplan

# Apply
terraform apply tfplan

# View outputs
terraform output
```

#### Makefile Shortcuts

```bash
cd terraform
make plan          # Plan with defaults
make apply         # Apply with manual approval
make apply-auto   # Apply with auto-approve
make show-ips     # Show all node IPs
make summary      # Show connection summary
make destroy      # Teardown everything
```

#### What Terraform Creates

| Resource                   | Type                    | Details                      |
|---------------------------|-------------------------|------------------------------|
| VPC (primary)             | google_compute_network  | Custom, no auto-subnets      |
| VPC (secondary)           | google_compute_network  | For peering                  |
| Subnet (us-west1)         | google_compute_subnetwork | 10.128.0.0/24             |
| Subnet (us-central1)      | google_compute_subnetwork | 10.128.1.0/24             |
| VPC Peering (bidirectional)| google_compute_network_peering | Cross-VPC routing |
| Cloud Router + NAT        | google_compute_router_nat | Outbound NAT             |
| Controller instance       | e2-standard-2           | us-west1-a, 50GB disk       |
| Worker instances (×3)     | e2-medium               | Multi-zone                  |
| Free-tier instance        | e2-micro                | Always-free                  |
| Cloud DNS zone            | evez-os.ai              | DNSSEC enabled               |
| A/CNAME records           | All nodes + services    | Controller-based routing     |
| GCS bucket                | Multi-regional US       | Versioned, CORS enabled     |
| Pub/Sub topic             | evez-mesh-events        | 1-day retention              |
| Cloud Scheduler (×3)      | Health/GC/Sync          | Free-tier friendly           |
| Uptime checks (×7)        | Ports 9111-9117         | 60-second intervals          |
| Alert policies (×3)        | Down/CPU/Disk           | Email notifications          |
| IAM audit logging         | All services            | Full audit trail             |
| VPC Service Controls      | Perimeter               | Access context policy        |
| Service accounts (×2)     | Node + Monitor          | Minimal-privilege IAM        |

---

### Method 2: Docker Compose

Cloud-agnostic deployment. Works on any Docker-capable host — GCP, AWS, Azure, DigitalOcean, VPS.

```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# Tail logs
docker compose logs -f

# Health check
curl http://localhost:9118/health

# Stop
docker compose down

# With extras (geolocation + TTS)
docker compose --profile extras up -d

# With custom registry (for pre-built images)
REGISTRY=gcr.io/evez-mesh-prod IMAGE_TAG=v1.0.0 docker compose up -d
```

#### Multi-Cloud Docker Deploy

```bash
# GCP Compute Engine
gcloud compute ssh evez-controller --command="cd workspace && docker compose up -d"

# AWS EC2
ssh ec2-user@INSTANCE_IP "cd workspace && docker compose up -d"

# DigitalOcean Droplet
ssh root@DROPLET_IP "cd workspace && docker compose up -d"

# Fly.io
fly deploy --config fly.toml

# Railway
railway up
```

---

### Method 3: Kubernetes / GKE

```bash
# Create GKE cluster (if not using Terraform)
gcloud container clusters create evez-mesh \
  --project=evez-mesh-prod \
  --region=us-west1 \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --enable-workload-identity

# Get credentials
gcloud container clusters get-credentials evez-mesh \
  --region=us-west1 \
  --project=evez-mesh-prod

# Deploy all services
kubectl apply -k k8s/

# Check deployment
kubectl get all -n evez-mesh

# Port-forward gateway
kubectl port-forward -n evez-mesh svc/gateway 9118:80

# Check health
curl http://localhost:9118/health
```

#### GKE Features

- **Gateway LoadBalancer**: Auto-provisioned external IP
- **Managed Certificate**: Auto-renewed TLS for gateway.evez-os.ai
- **HPA**: Gateway auto-scales 2-10 replicas based on CPU
- **PDB**: Maintains 1+ gateway replica during disruptions
- **NetworkPolicy**: Restricts mesh-internal traffic
- **Prometheus annotations**: Auto-scraped by GKE Managed Prometheus

---

### Method 4: Cloud-Init

Deploy to a fresh GCP instance with zero manual steps.

```bash
# Create instance with cloud-init
gcloud compute instances create evez-mesh \
  --zone=us-west1-a \
  --machine-type=e2-standard-2 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=50GB \
  --metadata-from-file=startup-script=cloud-init.sh \
  --tags=evez-node \
  --project=evez-mesh-prod

# Wait ~5-10 minutes for provisioning, then check
gcloud compute ssh evez-mesh --zone=us-west1-a --command="curl -s localhost:9118/health"
```

---

### Method 5: CI/CD

GitHub Actions auto-deploys on push to `main`.

#### Setup

1. Add GitHub Secrets:
   - `GCP_SA_KEY` — Base64-encoded service account key JSON
   - `GCP_PROJECT_ID` — Your GCP project ID
   - `VULTR_API_KEY` — Vultr API key (optional)

2. Create the service account key:
   ```bash
   # Create SA key
   gcloud iam service-accounts keys create key.json \
     --iam-account=evez-deployer@evez-mesh-prod.iam.gserviceaccount.com

   # Base64 encode for GitHub Secret
   base64 -w0 key.json | pbcopy  # macOS
   base64 -w0 key.json | xclip   # Linux
   ```

3. Add environment protection rules:
   - `production` environment → Require approval for apply
   - `production-destroy` environment → Require approval for destroy

#### Workflow Triggers

| Trigger              | Action                     |
|----------------------|----------------------------|
| PR to main           | Plan only (no changes)      |
| Push to main         | Apply + deploy services     |
| Manual: plan         | Plan only                   |
| Manual: apply        | Apply changes               |
| Manual: destroy      | Teardown infrastructure    |

---

## DNS & Networking

### Cloud DNS Zone

Terraform creates the `evez-os.ai` zone. After apply, update your domain's nameservers:

```bash
# Get nameservers
terraform output dns_zone_name_servers

# Update at your registrar (e.g., Cloudflare, GoDaddy)
# Set these nameservers:
#   ns-cloud-XX.googledomains.com.
#   ns-cloud-XX.googledomains.com.
#   ...
```

### DNS Records

| Record                    | Type   | Target                    |
|---------------------------|--------|---------------------------|
| controller.evez-os.ai    | A      | Controller public IP      |
| worker-0.evez-os.ai       | A      | Worker-0 public IP        |
| worker-1.evez-os.ai       | A      | Worker-1 public IP        |
| free.evez-os.ai           | A      | Free-tier public IP       |
| vultr.evez-os.ai          | A      | evez-os-worker             |
| consciousness.evez-os.ai  | CNAME  | controller.evez-os.ai     |
| desire.evez-os.ai         | CNAME  | controller.evez-os.ai     |
| world-model.evez-os.ai    | CNAME  | controller.evez-os.ai      |
| planner.evez-os.ai        | CNAME  | controller.evez-os.ai      |
| inner-voice.evez-os.ai    | CNAME  | controller.evez-os.ai      |
| self-modify.evez-os.ai    | CNAME  | controller.evez-os.ai      |
| agency.evez-os.ai         | CNAME  | controller.evez-os.ai      |
| *.mesh.evez-os.ai         | CNAME  | controller.evez-os.ai      |

### Firewall Rules

| Rule                        | Source                    | Ports           |
|-----------------------------|---------------------------|-----------------|
| SSH internal                | VPC CIDRs                | 22              |
| OpenClaw API internal       | VPC CIDRs                | 8443            |
| EVEZ services internal      | VPC CIDRs                | 9111-9117       |
| EVEZ services from Vultr    | evez-os-worker/32         | 9111-9117       |
| Health checks               | Google probing ranges    | 9111-9117       |
| IAP tunnel                  | 35.235.240.0/20         | 22              |
| ICMP internal               | VPC CIDRs                | ICMP            |
| Deny all ingress            | 0.0.0.0/0               | All (prio 65534) |
| Deny all egress             | 0.0.0.0/0               | All (via NAT)   |

---

## Monitoring & Alerting

### Uptime Checks

Terraform configures Google Cloud Monitoring uptime checks for all 7 core services (ports 9111-9117) with 60-second intervals.

### Alert Policies

| Alert             | Condition           | Threshold | Duration |
|-------------------|---------------------|-----------|----------|
| Service Down      | Uptime check failed | < 1       | 120s     |
| High CPU          | CPU utilization     | > 85%     | 5m       |
| High Disk         | Disk used %         | > 90%     | 10m      |

### Prometheus Metrics

The `metrics` service (port 9123) exports Prometheus-compatible metrics:

```
evez_service_status{service="consciousness",port="9111"} 1
evez_firmament_intact 1
evez_emergence_overall 0.42
evez_spine_events_total 1337
evez_rqns_cycles 42
```

### Dashboards

- **GCP Console**: Monitoring → Dashboards → "EVEZ Mesh Overview"
- **Grafana**: Import `dashboard/grafana-dashboard.json`

---

## Security Hardening

### IAM Roles (Minimal Privilege)

**Node Service Account** (`evez-node-sa`):
- `roles/logging.logWriter`
- `roles/logging.viewer`
- `roles/monitoring.metricWriter`
- `roles/monitoring.viewer`
- `roles/stackdriver.resourceMetadata.writer`
- `roles/storage.objectViewer`
- `roles/pubsub.publisher`
- `roles/compute.networkViewer`

**Monitor Service Account** (`evez-monitor-sa`):
- `roles/monitoring.admin`
- `roles/logging.viewer`
- `roles/pubsub.subscriber`

### VPC Service Controls

Terraform creates a VPC Service Perimeter restricting access to:
- Cloud Storage
- Pub/Sub
- Cloud Logging
- Cloud Monitoring

Only trusted IPs (VPC CIDRs + Vultr node) can access these services.

### OS Login

All instances enforce OS Login with two-factor authentication:
```bash
gcloud compute ssh evez-controller --zone=us-west1-a --tunnel-through-iap
```

### Audit Logging

All IAM operations are audited:
- ADMIN_READ
- DATA_READ
- DATA_WRITE

---

## Cost Estimates

### Free-Tier Only

| Resource            | Monthly Cost |
|---------------------|-------------|
| 1× e2-micro (us-west1) | $0.00    |
| 30GB pd-standard    | $0.00       |
| 1GB egress          | $0.00       |
| Pub/Sub (10GB)      | $0.00       |
| Cloud Scheduler (3) | $0.00       |
| **Total**           | **$0.00**   |

### Full Production Mesh

| Resource                          | Monthly Cost |
|-----------------------------------|-------------|
| 1× e2-standard-2 (controller)     | ~$52.50     |
| 3× e2-medium (workers)            | ~$75.00     |
| 1× e2-micro (free-tier)           | $0.00       |
| Cloud NAT (processing)            | ~$2.00      |
| Cloud DNS (1 zone)                 | ~$0.50      |
| Monitoring (uptime checks)         | ~$0.00      |
| GCS (artifacts)                    | ~$0.50      |
| Pub/Sub (events)                   | ~$0.50      |
| **Total**                          | **~$131/mo** |

> Costs are estimates. Use the [GCP Pricing Calculator](https://cloud.google.com/products/calculator) for precise figures.

---

## Troubleshooting

### Service Not Responding

```bash
# SSH into the instance
gcloud compute ssh evez-controller --zone=us-west1-a

# Check service processes
ps aux | grep python3

# Check Docker containers (if using compose)
docker compose ps

# Check logs
docker compose logs consciousness-engine
# Or direct Python:
tail -f /tmp/evez-consciousness_engine.log

# Health check
curl -s http://localhost:9118/health | jq .
```

### Terraform State Issues

```bash
cd terraform
terraform state list                    # List resources
terraform state show google_compute_instance.controller  # Inspect
terraform refresh                       # Refresh state
```

### Instance Can't Reach Services

```bash
# Check firewall rules
gcloud compute firewall-rules list --filter="network:evez-mesh-vpc"

# Check VPC routing
gcloud compute routes list --filter="network:evez-mesh-vpc"

# Test connectivity from inside
gcloud compute ssh evez-controller --command="curl -s http://localhost:9111/health"
```

### GKE Pod Not Starting

```bash
kubectl describe pod -n evez-mesh <pod-name>
kubectl logs -n evez-mesh <pod-name>
kubectl get events -n evez-mesh --sort-by='.lastTimestamp'
```

### Reset Everything

```bash
cd terraform
terraform destroy -var="project_id=evez-mesh-prod" -var="region=us-west1"
```

---

## Destroying Resources

### Terraform Destroy

```bash
cd terraform
terraform destroy \
  -var="project_id=evez-mesh-prod" \
  -var="region=us-west1"
```

### Docker Compose

```bash
docker compose down -v  # Remove containers + volumes
```

### GKE

```bash
kubectl delete -k k8s/
# Or delete the entire cluster
gcloud container clusters delete evez-mesh --region=us-west1
```

### GitHub Actions

Use the manual workflow dispatch with `action: destroy`. Requires the `production-destroy` environment approval.

---

## File Reference

| File                                    | Purpose                                    |
|-----------------------------------------|--------------------------------------------|
| `terraform/`                            | All Terraform infrastructure code          |
| `terraform/ci-apply.sh`                 | CI/CD Terraform wrapper                    |
| `scripts/deploy-gcp.sh`                 | One-command deployment script              |
| `docker-compose.yml`                     | Cloud-agnostic Docker Compose              |
| `cloud-init.sh`                         | Instance provisioning script               |
| `k8s/deployment.yml`                     | GKE Kubernetes manifests                   |
| `k8s/kustomization.yaml`                | Kustomize configuration                    |
| `.github/workflows/deploy-gcp.yml`      | GitHub Actions CI/CD workflow              |
| `docs/gcp-deployment.md`                | This document                              |

---

## Quick Reference

```bash
# Deploy everything
bash scripts/deploy-gcp.sh

# Docker Compose
docker compose up -d

# Kubernetes
kubectl apply -k k8s/

# Cloud-Init instance
gcloud compute instances create evez-mesh --metadata-from-file=startup-script=cloud-init.sh

# Health check
curl http://CONTROLLER_IP:9118/health

# SSH access
gcloud compute ssh evez-controller --zone=us-west1-a --tunnel-through-iap

# View Terraform outputs
cd terraform && terraform output

# Destroy
cd terraform && terraform destroy
```

---

*The spine is append-only. The invariants hold. The firmament is intact.* ⚡
