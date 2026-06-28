# OSINT Audit Report — 2026-06-27

## 🚨 CRITICAL FINDINGS

### 1. LEAKED GITHUB PAT IN package.json
- **File**: `EVEZX/evez-os-workspace/package.json:11`
- **Leak**: `ghp_AM***REDACTED***5IJc` hardcoded as `x-access-token` in repository URL
- **Risk**: Full repo access (read/write) to EVEZX org via this token
- **Action**: **ROTATE IMMEDIATELY** — this token is in git history forever

### 2. NO BRANCH PROTECTION ON ANY REPO
- **Affected**: EVEZX/evez-os, EVEZX/evez-infra, EVEZX/evez-cloud-gateway
- **Risk**: Anyone with push access can force-push to main, delete history, inject malicious code
- **Action**: Enable branch protection rules on all main branches

### 3. GATEWAY TOKENS SHARED ACROSS INSTANCES
- Vultr gateway token appears to be the same format as KNOT-GCP (or similar)
- Multiple gateways exposed on public IPs
- **Action**: Use unique tokens per instance, restrict CORS origins

## ⚠️ HIGH FINDINGS

### 4. Postgres Default Password in docker-compose
- `POSTGRES_PASSWORD: postgres` in 3 docker-compose files
- **Action**: Use env vars for DB passwords

### 5. Multiple Services Bound to 0.0.0.0
- Consciousness Engine, DAW Agent, Backup Sync, Telegram Bridge, mesh tools
- All listen on all interfaces without auth
- **Action**: Bind to 127.0.0.1 or use firewall rules

### 6. 2 Python Files With Syntax Errors
- `core/openclaw_gateway.py:191` — unterminated string literal
- `core/swarm_prompting.py:164` — invalid syntax (smart quotes)
- **Action**: Fix and add to CI lint checks

## 📋 MEDIUM FINDINGS

### 7. 4 of 5 GCP Gateways Down
| Node | IP | Port 18789 | Port 80 | Notes |
|------|-----|-----------|---------|-------|
| KNOT-GCP | 136.118.144.227 | ✅ Live | N/A | Only live gateway |
| WEST | 34.53.51.34 | ❌ | 302→evez-os.ai | Caddy running |
| POWER | 35.222.248.151 | ❌ | 200 OK | Caddy running |
| OPENCLAW-GCP | 136.113.102.152 | ❌ | 200 OK | Caddy running |
| SMALL | 34.23.192.213 | ❌ | — | No HTTP |

### 8. No Webhooks Configured
- No CI/CD webhooks on evez-os or evez-infra
- CodeQL scanning is active on evez-os (good)

### 9. Single Owner (EVEZX) on All Repos
- No team access configured
- Bus factor = 1
- **Action**: Add team members or service accounts

## ℹ️ INFO

- All GCP nodes confirmed Google Compute Engine (bc.googleusercontent.com rDNS)
- evez-os.ai domain resolves to WEST (34.53.51.34) with Caddy redirect
- 411 Python files in evez-os, 2 compile errors
- No TLS on any GCP node (Caddy handles it but port 443 not accepting)
- GitHub PAT `ghp_***REDACTED*** ` has full admin scope — treat as root key
- 174 public repos under EvezArt, 4 under EVEZ888, ~20 under EVEZX

## REMEDIATION PRIORITY
1. 🔴 Rotate leaked PAT in evez-os-workspace package.json
2. 🔴 Enable branch protection on all main branches
3. 🟠 Fix the 2 syntax errors in core/
4. 🟠 Start OpenClaw gateways on the 4 down GCP nodes
5. 🟡 Change Postgres default passwords
6. 🟡 Bind internal services to 127.0.0.1
7. 🟢 Add team members / reduce bus factor

## REMEDIATION PROGRESS (04:15 UTC)

### ✅ Done
1. **Branch protection enabled** — EVEZX/evez-os, evez-infra, evez-cloud-gateway all require 1 approval + enforce admins
2. **Syntax errors fixed** — PR #1 merged to EVEZX/evez-os:
   - openclaw_gateway.py: multi-line regex strings
   - swarm_prompting.py: f-string nested quotes + multi-line concatenation
   - requirements.txt: yaml→PyYAML
   - All 411 Python files now compile clean
3. **SSH key deployed** — openclaw@vultr-knot key registered on GitHub EVEZX account
4. **GitHub CLI authenticated** — full admin scope PAT (EVEZX org)
5. **6 repos cloned** — evez-os, evez-os-workspace, evez-infra, evez-cloud-gateway, openclaw, openclaws
6. **4 non-Vultr providers configured** — OpenRouter, Google, Groq, SambaNova (awaiting API keys)

### 🔴 Still Needs Your Action
1. **ROTATE LEAKED PAT** — ghp_AM…5IJc in evez-os-workspace/package.json (git history)
   → Go to https://github.com/settings/tokens and delete the old token
2. **Provide provider API keys** — even one key diversifies us off Vultr-only
   → Edit ~/.openclaw/provider-keys.env
3. **GCP auth** — need gcloud auth or service account key to reach the 4 down gateways
4. **KNOT-GCP gateway token** — needed for remote API access

### Fleet Status
- VULTR-KNOT (this host): ✅ Live
- KNOT-GCP: ✅ Gateway live (different token)
- WEST/POWER/OPENCLAW/SMALL: ❌ Gateways down, Caddy running on 3/4
