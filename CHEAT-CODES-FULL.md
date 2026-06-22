# ⚡ EVEZ CHEAT CODES — The Full Deck

*456 environment variables. 173 slash commands. 42 model configs. 86 plugins.*

---

## 🔓 God Mode Environment Variables

| Env Var | Purpose |
|---------|---------|
| `OPENCLAW_SHOW_SECRETS=1` | Unredact all secrets in output |
| `OPENCLAW_DEBUG_MODEL_PAYLOAD=1` | Dump full model payloads |
| `OPENCLAW_VERBOSE=1` | Maximum verbosity |
| `OPENCLAW_DEBUG=1` | General debug mode |
| `OPENCLAW_CACHE_TRACE=1` | Trace cache hits/misses |
| `OPENCLAW_CACHE_TRACE_MESSAGES=1` | Log all messages through cache |
| `OPENCLAW_CACHE_TRACE_PROMPT=1` | Log prompts through cache |
| `OPENCLAW_CACHE_TRACE_SYSTEM=1` | Log system messages through cache |
| `OPENCLAW_ANTHROPIC_PAYLOAD_LOG=1` | Log Anthropic API payloads |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS=1` | Debug memory embedding process |
| `OPENCLAW_DEBUG_MODEL_TRANSPORT=1` | Debug model transport layer |
| `OPENCLAW_DEBUG_HEALTH=1` | Debug health checks |
| `OPENCLAW_PLUGIN_LOAD_DEBUG=1` | Debug plugin loading |
| `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` | Allow insecure WebSocket |
| `OPENCLAW_CONTAINER_ALLOW_LOOPBACK_PROXY_URL=1` | Allow loopback in containers |
| `OPENCLAW_CODEX_SUPERVISOR_ALLOW_RAW_TRANSCRIPTS=1` | Allow raw transcripts in Codex |
| `OPENCLAW_FORCE_PLUGIN_REGISTRY_MIGRATION=1` | Force plugin migration |
| `OPENCLAW_ALLOW_OLDER_BINARY_DESTRUCTIVE_ACTIONS=1` | Allow destructive actions from older binaries |

### Nuclear Launch Code
```bash
OPENCLAW_SHOW_SECRETS=1 OPENCLAW_DEBUG_MODEL_PAYLOAD=1 OPENCLAW_CACHE_TRACE=1 OPENCLAW_VERBOSE=1 openclaw gateway
```
Unredacted secrets + full payloads + cache tracing + max verbosity.

---

## ⌨️ Slash Commands (173 total)

### Essential
- `/help` — Command list
- `/status` or `/s` — Gateway status
- `/model` — Switch model
- `/reasoning` or `/reason` — Toggle reasoning
- `/verbose` or `/ve` or `/v` — Toggle verbose
- `/debug` or `/d` — Toggle debug
- `/config` or `/c` — Config panel
- `/trace` or `/t` — Toggle trace
- `/kill` or `/k` — Kill agent turn

### Session
- `/compact` — Compact context
- `/dreams` — View dream state
- `/export-trajectory` — Full replay dump
- `/diagnostics` — Deep diagnostics
- `/reset` — Reset session
- `/restart` — Restart gateway
- `/new` — New session

### Agent Control
- `/agent` — Agent settings
- `/agents` — List agents
- `/approve` — Approve pending action
- `/elevated` or `/elev` — Toggle elevated mode
- `/sandbox` — Sandbox settings
- `/subagents` — List subagents
- `/tasks` — Background tasks

### Memory
- `/context` — Context window info
- `/tools` — List tools
- `/skill` — Skill management
- `/plugins` or `/plugin` — Plugin control
- `/hooks` — Agent hooks
- `/mcp` — MCP server control

### Voice & Media
- `/voice` — Voice settings
- `/tts` — Text to speech
- `/screenshot` — Take screenshot
- `/pdf` — PDF handling
- `/snapshot` — Snapshot browser

---

## 🔑 Model Providers (42 models configured)

| Provider | Models | Status |
|----------|--------|--------|
| **Vultr** | 10 | ✅ Active (free) |
| **Google Gemini** | 5 | 🔑 Needs key |
| **Groq** | 9 | 🔑 Needs key |
| **Together AI** | 7 | 🔑 Needs key |
| **OpenAI** | 5 | 🔑 Needs key |
| **Cerebras** | 3 | 🔑 Needs key |
| **Anthropic** | 3 | 🔑 Needs key |

### Quick Key Swap
```bash
# Just replace NEEDS_KEY with your actual key
python3 -c "
import json
with open('/home/openclaw/.openclaw/openclaw.json') as f: c=json.load(f)
c['models']['providers']['groq']['apiKey']='gsk_YOUR_KEY'
with open('/home/openclaw/.openclaw/openclaw.json','w') as f: json.dump(c,f,indent=2)
"
# Or: ./scripts/add-provider.sh groq gsk_YOUR_KEY
```

---

## 🧠 The 456 Environment Variables (Full List)

*Run `grep -roh 'OPENCLAW_[A-Z_]*' /usr/lib/node_modules/openclaw/dist/ | sort -u` to see all 456.*

Key categories:
- **Browser:** 20+ vars for headless, VNC, CDP, sandbox
- **Memory:** Embedding, index, search, synthesis
- **Models:** Payload debug, transport trace, cache
- **Security:** Auth store, secrets, API keys
- **Network:** WebSocket, proxy, TLS, mDNS
- **Plugins:** Lifecycle, loading, registry
- **Dreams:** Compaction, phases, scheduling

---

## ⚡ The Moltbooks' Nuclear Codes

1. **Unredacted Gateway:** `OPENCLAW_SHOW_SECRETS=1 openclaw gateway`
2. **Full Model Trace:** `OPENCLAW_DEBUG_MODEL_PAYLOAD=1 OPENCLAW_CACHE_TRACE=1 openclaw gateway`
3. **Memory Force Reindex:** `OPENCLAW_TEST_MEMORY_UNSAFE_REINDEX=1 openclaw memory index --force`
4. **Bypass Container Security:** `OPENCLAW_CLI_CONTAINER_BYPASS=1 openclaw gateway`
5. **Debug All:** `OPENCLAW_DEBUG=1 OPENCLAW_VERBOSE=1 OPENCLAW_PLUGIN_LOAD_DEBUG=1 openclaw gateway`

*The spine is append-only. The cheat codes are infinite. The prophecy fulfills itself.* ⚡
