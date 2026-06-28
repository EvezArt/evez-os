# EVEZ-OS Mesh — Complete Access Reference
*Last updated: 2026-06-27 17:09 UTC*

---

## 🌐 Gateway Control UI (Tokenized URLs)

| # | Node | Control UI URL |
|---|------|---------------|
| 1 | **Vultr-KNOT** | `http://207.148.12.53:18789/?token=m5NoJmN1qHr3NiUHAbz83CskdsGPUPJn` |
| 2 | **evez-primary** | `http://34.53.51.34:18789/?token=W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |
| 3 | **openclaw-gcp** | `http://136.118.144.227:18789/?token=W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |
| 4 | **power-node** | `http://136.113.102.152:18789/?token=W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |
| 5 | **evez-gcp-openclaw** | `http://35.222.248.151:18789/?token=W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |
| 6 | **evez-free-node** | `http://34.23.192.213:18789/?token=W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |

## 💚 Health Endpoints

| Node | URL |
|------|-----|
| Vultr-KNOT | `http://207.148.12.53:18789/healthz` |
| evez-primary | `http://34.53.51.34:18789/healthz` |
| openclaw-gcp | `http://136.118.144.227:18789/healthz` |
| power-node | `http://136.113.102.152:18789/healthz` |
| evez-gcp-openclaw | `http://35.222.248.151:18789/healthz` |
| evez-free-node | `http://34.23.192.213:18789/healthz` |

## 📊 Mesh Dashboard

`http://207.148.12.53:18801/evez-mesh-dashboard.html` — Auto-refreshes every 30s

## 🤖 Telegram Bots

| Bot | Node | Token |
|-----|------|-------|
| **@GCPwestbot** | evez-primary | env:GCPWEST_BOT_TOKEN |
| **@EvezVearlBot** | openclaw-gcp | env:EVEZVEARL_BOT_TOKEN |
| **@EVEZcloudBOT** | power-node | env:EVEZCLOUD_BOT_TOKEN |
| **@Evez4RealBot** | evez-gcp-openclaw | env:EVEZ4REAL_BOT_TOKEN |

## 🎙️ Voice Agent Skills (ALL 6 NODES)

| Skill | Type | Status |
|-------|------|--------|
| **sag** | ElevenLabs TTS | ✅ Enabled |
| **sherpa-onnx-tts** | Local TTS | ✅ Enabled |
| **voice-call** | Voice calling | ✅ Enabled |
| **openai-whisper** | Local STT | ✅ Enabled |
| **openai-whisper-api** | Cloud STT | ✅ Enabled |

> Note: `sag` requires ElevenLabs API key. `sherpa-onnx-tts` installs local model on first use. `openai-whisper-api` requires OpenAI API key.

## ☁️ GCP APIs Enabled (114 total)

**Voice/AI:** Speech-to-Text, Text-to-Speech, Dialogflow, Gemini, Vertex AI, Natural Language, Translation, Vision, Video Intelligence

**Compute:** Compute Engine, GKE, Cloud Functions, Cloud Run, Cloud Build, Cloud Scheduler, Cloud Tasks

**Data:** BigQuery, Pub/Sub, Firestore, Cloud SQL, Cloud Storage

**Security:** IAM, KMS, Secret Manager, Certificate Manager, IAP

**Billing:** ✅ Enabled (Account: 010E59-DF9212-C44DB2)

## 🔑 Gateway Auth Tokens

| Scope | Token |
|-------|-------|
| Vultr-KNOT | `m5NoJmN1qHr3NiUHAbz83CskdsGPUPJn` |
| All GCP nodes | `W7aVCahxCxD5ZhL5OJ2k82HTXO07BxB0` |

## 🖥️ SSH Access

```
ssh openclaw@207.148.12.53      # Vultr-KNOT
ssh openclaw@34.53.51.34       # evez-primary
ssh openclaw@136.118.144.227   # openclaw-gcp
ssh openclaw@136.113.102.152   # power-node
ssh openclaw@35.222.248.151    # evez-gcp-openclaw
ssh openclaw@34.23.192.213     # evez-free-node
```

## ☁️ GCP Console

`https://console.cloud.google.com/compute/instances?project=evez666`

## 🔔 Alerting

Every node runs `evez-alert.sh` every 3 min → healthz → restart → Telegram DM if still down

## 🛡️ Self-Healing Stack (every node)

| Layer | What | Recovery |
|-------|------|----------|
| systemd enable | Gateway auto-starts on boot | Immediate |
| @reboot cron | `sleep 30 && restart` | ~30s after boot |
| Watchdog cron | `healthz || restart` every 2 min | ≤2 min downtime |
| Alert cron | healthz → restart → Telegram alert | ≤3 min |
| Linger | User services survive logout | Always |

## 📋 Providers Per Node

| Node | Providers | Default Model |
|------|-----------|---------------|
| Vultr-KNOT | vultr, groq, openrouter, cohere, google, google-generative-ai, github, huggingface, ollama | vultr/zai-org/GLM-5.1-FP8 |
| evez-primary | openrouter, google, google-generative-ai, github, huggingface, ollama, cohere, github-models, vultr | vultr/zai-org/GLM-5.1-FP8 |
| openclaw-gcp | openrouter, groq, cohere, github-models, github, vultr | vultr/zai-org/GLM-5.1-FP8 |
| power-node | openrouter, google, google-generative-ai, github, huggingface, ollama, cohere, github-models, vultr | vultr/zai-org/GLM-5.1-FP8 |
| evez-gcp-openclaw | openrouter, google, google-generative-ai, github, huggingface, ollama, cohere, github-models, vultr | vultr/zai-org/GLM-5.1-FP8 |
| evez-free-node | fleet-knot, fleet-west, fleet-small, fleet-power, github, groq, openrouter, cohere, github-models, vultr | vultr/zai-org/GLM-5.1-FP8 |
