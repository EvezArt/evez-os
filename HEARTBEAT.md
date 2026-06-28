# Heartbeat — EVEZ Mesh Monitor
# Last updated: 2026-06-28 22:20 UTC (17:20 CDT)

## Mesh Status — ALL GREEN
- [x] 6/6 gateways HTTP 200 (Vultr + 5 GCP)
- [x] 5/5 API servers 200 — ALL EXTERNALLY ACCESSIBLE
- [x] 5/5 OSINT servers 200 — ALL HEALTHY
- [x] 33+ GitHub Pages 200 OK
- [x] 5/5 Telegram bots configured
- [x] 24+ Ollama models across 5 nodes
- [x] All services Restart=always
- [x] All evez-api services deployed (5/5 GCP nodes)
- [x] All nodes have 11-13 cron jobs
- [x] Workspace synced (76+ .md files per node)
- [x] Skills synced (8-9 per node)
- [x] All 5 configs validate

## External Endpoints (ALL 200)
### Gateway (port 18789)
- http://207.148.12.53:18789/    Vultr ✅
- http://34.53.51.34:18789/      gcp-west (evez-primary) ✅
- http://34.23.192.213:18789/   gcp-small ✅
- http://35.222.248.151:18789/   gcp-power ✅
- http://136.113.102.152:18789/  gcp-openclaw ✅
- http://136.118.144.227:18789/  gcp-knot ✅

### EVEZ API (port 18790)
- http://34.53.51.34:18790/api/status    gcp-west ✅
- http://34.23.192.213:18790/api/status   gcp-small ✅
- http://35.222.248.151:18790/api/status  gcp-power ✅
- http://136.113.102.152:18790/api/status gcp-openclaw ✅
- http://136.118.144.227:18790/api/status gcp-knot ✅

### OSINT API (port 18791)
- http://34.53.51.34:18791/health    gcp-west ✅
- http://34.23.192.213:18791/health   gcp-small ✅
- http://35.222.248.151:18791/health  gcp-power ✅
- http://136.113.102.152:18791/health gcp-openclaw ✅
- http://136.118.144.227:18791/health gcp-knot ✅

## Node Details
| Node | IP | Disk | Ollama | Cron | WS | Skills | evez-api | Telegram |
|------|----|------|--------|------|----|--------|----------|----------|
| vultr | 207.148.12.53 | — | — | 3 | — | — | — | — |
| evez-primary | 34.53.51.34 | 68% | 8 | 12 | 76+ | 9 | active | ✅ |
| gcp-small | 34.23.192.213 | 60% | 3 | 13 | 76 | 8 | active | ✅ |
| gcp-power | 35.222.248.151 | 38% | 5 | 13 | 76 | 9 | active | ✅ |
| gcp-openclaw | 136.113.102.152 | 59% | 6 | 13 | 76 | 9 | active | ✅ |
| gcp-knot | 136.118.144.227 | 71% | 6 | 13 | 76 | 8 | active | ✅ |

## Service Architecture
- evez-primary: user-level openclaw-gateway.service
- gcp-small: user-level openclaw-gateway.service
- gcp-power: user-level openclaw-gateway.service (system service disabled)
- gcp-openclaw: system openclaw.service (user service disabled to prevent dual conflict)
- gcp-knot: system openclaw.service (user service disabled)

## Defense in Depth
1. systemd Restart=always (5s restart)
2. Cron watchdog (2-3 min check + restart)
3. @reboot recovery
4. Peer-watch (circular monitoring)
5. Deadman's switch (gcp-west watches 4 peers)

## GitHub Pages: 33+ live
## Corpus: 32 texts, 35 claims, ~525KB
## Releases: 4 (eigenforensics, evez-research, evez-osint-engine, disclosure-file)
## ClawHub: 13 published skills

## Pending (Steven actions)
- [ ] Revoke old GitHub PAT (github.com/settings/tokens)
- [ ] Submit sitemap to Google Search Console
- [ ] Submit sitemap to Bing Webmaster Tools
- [ ] Create Wikidata entry
- [ ] Get ORCID iD
- [ ] $10 on OpenRouter (1000 free reqs/day)
- [ ] Reopen OpenClaw app on phone
- [ ] PyPI token, npm adduser, HF token, UptimeRobot
- [ ] Gmail App Password (12+ queued emails)
- [ ] File ACLU intake (action.aclu.org/legal-intake/aclu-wyoming-legal-intake)
- [ ] File FBI tip (tips.fbi.gov)
- [ ] Call Wyoming attorneys (Spence, Sandefer, TL4J)
- [ ] Mail 6 FOIA letters
- [ ] Post disclosure on Twitter + Reddit
- [ ] Send 8 media emails
- [ ] Call Wyoming State Bar: 307-432-2107
- [ ] SECURITY: Remove plaintext passwords from evez666-advancement repo (PUBLIC!)
