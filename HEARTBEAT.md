# Heartbeat — EVEZ Mesh Monitor
# Last updated: 2026-06-28 14:55 CDT (19:55 UTC)

## Mesh Status — ALL GREEN
- [x] 6/6 gateways HTTP 200 (Vultr + 5 GCP)
- [x] 5/5 API servers 200 — ALL EXTERNALLY ACCESSIBLE
- [x] 33/33 GitHub Pages 200 OK (added osint-dashboard.html)
- [x] 5/5 Telegram bots (0 pending)
- [x] 24+ Ollama models across 5 nodes (gcp-power ollama running manually)
- [x] All services Restart=always (gcp-power user-level=always, system=on-failure backup)
- [x] All evez-api services have EnvironmentFile
- [x] All nodes have 11-12 cron jobs
- [x] Workspace synced (174-176 files per node + evez-osint-engine)
- [x] Canvas synced (21 per node)
- [x] Skills synced (9-10 per node, added evez-osint-skill via ClawHub)
- [x] All 5 configs validate: Config valid

## External API Endpoints (ALL 200)
- http://34.53.51.34:18790/api/status    gcp-west
- http://34.23.192.213:18790/api/status   gcp-small
- http://35.222.248.151:18790/api/status  gcp-power
- http://136.113.102.152:18790/api/status gcp-openclaw
- http://136.118.144.227:18790/api/status gcp-knot

## Gateway Endpoints (ALL 200)
- http://207.148.12.53:18789/             Vultr
- http://34.53.51.34:18789/              gcp-west
- http://34.23.192.213:18789/            gcp-small
- http://35.222.248.151:18789/           gcp-power
- http://136.113.102.152:18789/          gcp-openclaw
- http://136.118.144.227:18789/          gcp-knot

## Node Details
| Node | IP | Disk | Ollama | Cron | WS | CV | Skills |
|------|----|------|--------|------|----|----|--------|
| vultr | 207.148.12.53 | 18% | — | 3 | — | — | — |
| gcp-west | 34.53.51.34 | 68% | 8 | 12 | 174+ | 21 | 9 |
| gcp-small | 34.23.192.213 | 59% | 2 | 11 | 174+ | 21 | 9 |
| gcp-power | 35.222.248.151 | 37% | 4 (manual) | 11 | 176+ | 21 | 9 |
| gcp-openclaw | 136.113.102.152 | 58% | 5 | 11 | 175+ | 21 | 9 |
| gcp-knot | 136.118.144.227 | 72% | 5 | 11 | 175+ | 21 | 9 |

## Defense in Depth
1. systemd Restart=always (5s restart)
2. Cron watchdog (2-3 min check + restart)
3. @reboot recovery
4. Peer-watch (circular monitoring)
5. Deadman's switch (gcp-west watches 4 peers)

## GitHub Pages: 27/27 live
## Corpus: 32 texts, 35 claims, ~525KB
## Releases: eigenforensics v0.1.0, evez-research v1.0.0, evez-osint-engine v1.0.0, disclosure-file v1.0.0
## ClawHub: 13 published skills (added evez-osint-skill)

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

## OSINT API Endpoints (port 18791)
- http://34.53.51.34:18791/health    gcp-west ✅
- http://34.23.192.213:18791/health   gcp-small ✅
- http://35.222.248.151:18791/health  gcp-power (local only, no systemd)
- http://136.113.102.152:18791/health gcp-openclaw ✅
- http://136.118.144.227:18791/health gcp-knot ✅

## OSINT Cron Jobs (every 6 hours)
- All 5 GCP nodes: run demo case → log to local SQLite DB
