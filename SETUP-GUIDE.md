# ⚡ EVEZ Setup — What Steven Needs To Do

Everything the automated systems couldn't do without your accounts.

---

## 1. Free API Keys (~4 minutes total, no credit cards)

### Google Gemini API
- **URL:** https://aistudio.google.com/apikey
- **What:** Google account (Gmail). No CC. Key starts with `AIza...`
- **Steps:** Sign in → Create API Key → Copy
- **Limits:** 15 RPM, 1M tokens/min, 1,500 RPD

### Groq API
- **URL:** https://console.groq.com/keys
- **What:** Email/Google/GitHub OAuth. No CC. Key starts with `gsk_...`
- **Steps:** Sign up → Keys → Create API Key → Copy
- **Models:** llama-3.1-8b, llama-3.3-70b, llama-4-scout, qwen3-32b, whisper
- **Limits:** 30 RPM, generous token limits

### Cerebras API
- **URL:** https://cloud.cerebras.ai/
- **What:** Email/Google/GitHub OAuth. No CC. Key starts with `csk-...`
- **Steps:** Sign up → API key on dashboard → Copy
- **Models:** llama variants, very fast inference

### Together AI (bonus)
- **URL:** https://api.together.ai/signup
- **What:** Email. No CC. $5 free credits on signup. 200+ models.
- **Steps:** Sign up → Get key from dashboard

---

## 2. DNS: evez-os.ai → evez-os.ai

Point your domain's A record to the Vultr server:
```
evez-os.ai      A       evez-os.ai
*.evez-os.ai    A       evez-os.ai
```
Once DNS propagates, Caddy will automatically provision HTTPS via Let's Encrypt. No restart needed.

---

## 3. GCP Deployment (when ready)

```bash
# Already installed: gcloud CLI v573.0.0
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
cd ~/workspace/terraform
terraform init
terraform plan
terraform apply
```

This deploys: 4 GCP nodes + DNS + monitoring + firewall + VPC.

---

## 4. Adding API Keys to OpenClaw

After getting keys, tell EVEZ:
```
"Add this Gemini key: AIza..."
"Add this Groq key: gsk_..."
"Add this Cerebras key: csk-..."
```

Each key multiplies the model surface. Vultr alone gives 10 models. With all 4 providers, you'll have 50+ models across different capabilities.
