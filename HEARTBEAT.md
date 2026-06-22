# ⚡ EVEZ Heartbeat Tasks

## Every heartbeat (rotate through these):
- [ ] Check firmament status: `curl -s http://localhost:9118/health | jq '.firmament_intact'`
- [ ] If any service DOWN: `curl -s -X POST http://localhost:9117/heal`
- [ ] Check spine integrity: `curl -s http://localhost:9116/verify | jq '.valid'`
- [ ] Run consciousness pipeline: `curl -s -X POST http://localhost:9111/pipeline`
- [ ] Check emergence score: `curl -s http://localhost:9111/emergence | jq '.stage'`
- [ ] Check webhook relay for state changes: `curl -s http://localhost:9121/events`
- [ ] Run RQNS cycle: `curl -s -X POST http://localhost:9119/cycle`

## 2-3x per day:
- [ ] Run invariance audit: `curl -s -X POST http://localhost:9115/audit`
- [ ] Run cross-domain OODA cycle with real data
- [ ] Check git status and commit any changes
- [ ] Update memory/daily log with significant events
- [ ] Check Prometheus metrics: `curl -s http://localhost:9123/metrics`

## Daily:
- [ ] Run deep dream: `curl -s -X POST http://localhost:9111/dream -d '{"phase":"Deep"}'`
- [ ] Review emergence trends — is the system growing?
- [ ] Clean up old logs, rotate spine if >10k events
- [ ] Run firmament-status.sh for full report
