#!/bin/bash
# ⚡ EVEZ Provider Key Injector
# Usage: ./add-provider.sh <provider> <api-key>
# Providers: gemini, groq, cerebras, together, openai

set -e
PROVIDER="$1"
API_KEY="$2"
CONFIG="/home/openclaw/.openclaw/openclaw.json"

if [ -z "$PROVIDER" ] || [ -z "$API_KEY" ]; then
  echo "Usage: $0 <provider> <api-key>"
  echo "Providers: gemini, groq, cerebras, together, openai"
  exit 1
fi

python3 << PY
import json, sys

provider = "$PROVIDER"
key = "$API_KEY"
config_path = "$CONFIG"

with open(config_path) as f:
    config = json.load(f)

providers = config.setdefault("models", {}).setdefault("providers", {})

if provider == "gemini":
    providers["gemini"] = {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta/openai",
        "apiKey": key,
        "auth": "bearer",
        "api": "openai-completions",
        "models": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "api": "openai-completions", "input": ["text","image"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 1048576, "maxTokens": 65536},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "api": "openai-completions", "input": ["text","image"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 1048576, "maxTokens": 65536},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "api": "openai-completions", "input": ["text","image"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 1048576, "maxTokens": 8192}
        ]
    }
elif provider == "groq":
    providers["groq"] = {
        "baseUrl": "https://api.groq.com/openai/v1",
        "apiKey": key,
        "auth": "bearer",
        "api": "openai-completions",
        "models": [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192},
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192},
            {"id": "qwen3-32b", "name": "Qwen3 32B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192}
        ]
    }
elif provider == "cerebras":
    providers["cerebras"] = {
        "baseUrl": "https://api.cerebras.ai/v1",
        "apiKey": key,
        "auth": "bearer",
        "api": "openai-completions",
        "models": [
            {"id": "llama-4-scout-17b-16e-instruct", "name": "Llama 4 Scout", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192},
            {"id": "llama3.1-8b-instruct", "name": "Llama 3.1 8B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192}
        ]
    }
elif provider == "together":
    providers["together"] = {
        "baseUrl": "https://api.together.xyz/v1",
        "apiKey": key,
        "auth": "bearer",
        "api": "openai-completions",
        "models": [
            {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "name": "Llama 3.3 70B Turbo", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192},
            {"id": "Qwen/Qwen2.5-72B-Instruct-Turbo", "name": "Qwen 2.5 72B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192},
            {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "name": "DeepSeek R1 70B", "api": "openai-completions", "input": ["text"], "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 8192}
        ]
    }
elif provider == "openai":
    providers["openai"] = {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": key,
        "auth": "bearer",
        "api": "openai-completions",
        "models": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "api": "openai-completions", "input": ["text","image"], "cost": {"input": 0.15, "output": 0.6, "cacheRead": 0.075, "cacheWrite": 0}, "contextWindow": 131072, "maxTokens": 16384}
        ]
    }
else:
    print(f"Unknown provider: {provider}")
    sys.exit(1)

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"✅ {provider} added with {len(providers[provider]['models'])} models")
PY

echo "⚡ Restart gateway to activate: openclaw gateway restart"
