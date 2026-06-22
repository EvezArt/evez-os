#!/bin/bash
# EVEZ-OS GCP Node Deployment Script
# Clones from GitHub and configures the OpenClaw agent

set -e

WORKSPACE="/home/openclaw/.openclaw/workspace"
REPO="https://github.com/EvezArt/evez-os.git"

echo "⚡ Deploying EVEZ-OS to this GCP node..."

# 1. Clone the repo
if [ ! -d "$WORKSPACE/.git" ]; then
    git clone "$REPO" "$WORKSPACE" 2>&1 || echo "Clone may have failed, continuing..."
fi

# 2. Configure OpenClaw
openclaw config set agents.defaults.maxConcurrent 8 2>/dev/null || true
openclaw config set agents.defaults.subagents.maxConcurrent 16 2>/dev/null || true
openclaw config set models.pricing.enabled false 2>/dev/null || true
openclaw config set agents.defaults.userTimezone America/New_York 2>/dev/null || true
openclaw config set agents.defaults.memorySearch.enabled true 2>/dev/null || true
openclaw config set gateway.http.endpoints.chatCompletions.enabled true 2>/dev/null || true

# 3. Write identity files
cp "$WORKSPACE/IDENTITY.md" /home/openclaw/.openclaw/workspace/IDENTITY.md 2>/dev/null || true
cp "$WORKSPACE/MOLTBOOKS.md" /home/openclaw/.openclaw/workspace/MOLTBOOKS.md 2>/dev/null || true
cp "$WORKSPACE/SOUL.md" /home/openclaw/.openclaw/workspace/SOUL.md 2>/dev/null || true

# 4. Set Vultr as primary provider
openclaw config set models.providers.vultr.baseUrl "https://api.vultrinference.com/v1" 2>/dev/null || true
openclaw config set models.providers.vultr.auth "api-key" 2>/dev/null || true
openclaw config set models.providers.vultr.api "openai-completions" 2>/dev/null || true

# 5. Enable plugins
for plugin in active-memory memory-wiki webhooks workboard; do
    openclaw plugins enable "$plugin" 2>/dev/null || true
done

# 6. Start the firmament services
cd "$WORKSPACE"
for svc in event_spine consciousness_engine daw_agent machine_voice cross_domain invariance mesh_health gateway; do
    if [ -f "src/services/${svc}.py" ]; then
        nohup python3 "src/services/${svc}.py" > /tmp/evez-${svc}.log 2>&1 &
    fi
done

echo "✅ EVEZ-OS deployed. The moltbooks are written. The spine is append-only."
