#!/bin/bash
# Quick setup: paste API keys and they'll be loaded into the environment
# Usage: ./scripts/setup-provider-keys.sh

ENV_FILE="/home/openclaw/.openclaw/provider-keys.env"

echo "🔑 OpenClaw Provider Key Setup"
echo "=============================="
echo ""
echo "Edit $ENV_FILE directly, or paste keys here:"
echo ""

# Check current state
source "$ENV_FILE" 2>/dev/null

[ -n "$OPENROUTER_API_KEY" ] && echo "✅ OpenRouter: configured" || echo "❌ OpenRouter: missing → https://openrouter.ai/settings/keys"
[ -n "$GOOGLE_AI_API_KEY" ] && echo "✅ Google AI: configured" || echo "❌ Google AI: missing → https://aistudio.google.com/app/apikey"
[ -n "$GROQ_API_KEY" ] && echo "✅ Groq: configured" || echo "❌ Groq: missing → https://console.groq.com/keys"
[ -n "$SAMBANOVA_API_KEY" ] && echo "✅ SambaNova: configured" || echo "❌ SambaNova: missing → https://cloud.sambanova.ai/apis"

echo ""
echo "After editing keys, run:"
echo "  source $ENV_FILE"
echo "  openclaw gateway restart"
echo ""
echo "To test a key (e.g. OpenRouter):"
echo "  curl -s https://openrouter.ai/api/v1/models -H 'Authorization: Bearer \$OPENROUTER_API_KEY' | head -5"
