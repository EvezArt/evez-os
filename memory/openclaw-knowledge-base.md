# OpenClaw Comprehensive Knowledge Base
> Generated from systematic doc reading, 2026-06-27

## Core Architecture

### Gateway
- Single Node.js process, default port 18789
- Config: `~/.openclaw/openclaw.json` (JSON5 format - comments/trailing commas OK)
- State: `~/.openclaw/` (OPENCLAW_STATE_DIR override)
- Workspace: `~/.openclaw/workspace` (agents.defaults.workspace override)
- Agent dirs: `~/.openclaw/agents/<agentId>/agent/` for per-agent state
- Sessions: `~/.openclaw/agents/<agentId>/sessions/`
- Auth profiles: Per-agent SQLite (`openclaw-agent.sqlite`), not legacy JSON
- Service: `openclaw-gateway.service` or `openclaw.service` (user systemd)
- CLI: `openclaw gateway status|restart|start|stop`

### Auth
- Shared-secret: `gateway.auth.token` or `gateway.auth.password`
- Modes: `"shared-secret"` (default), `"password"`, `"trusted-proxy"`, `"tailscale"`
- Tailscale: `gateway.auth.allowTailscale: true`
- Control UI: auto-approves loopback (127.0.0.1/localhost), otherwise needs device pairing
- Device pairing: `openclaw devices list` → `openclaw devices approve <requestId>`

### Model Provider Auth
- Auth profiles stored per-agent in SQLite
- API keys: env vars (`<PROVIDER>_API_KEY`) or config (`models.providers.<id>.apiKey`)
- Auth order: `auth.order.<provider>` array of profile ids
- OAuth: `openclaw models auth login --provider <id>`
- Key rotation: retries on rate-limit only, not other errors
- Auth removal: aborts active runs with `stopReason: "auth-revoked"`

### Multi-Agent
- Multiple isolated agents in one Gateway (workspaces, auth, sessions, state)
- `agents.list[]` with `id`, `workspace`, `agentDir`
- `bindings[]` route channel accounts → agents
- `openclaw agents add <id>` to create
- Cross-agent QMD: `agents.list[].memorySearch.qmd.extraCollections`

### System Prompt Assembly
- Three layers: buildAgentSystemPrompt (renderer) → resolveAgentSystemPromptConfig (config) → runtime adapters (live facts)
- Sections: Tooling, Execution Bias, Safety, Skills, OpenClaw Control, Self-Update, Workspace, Docs, Project Context, Sandbox, Date/Time, Output Directives, Heartbeats, Runtime, Reasoning
- Provider plugins can replace named sections: `interaction_style`, `tool_call_style`, `execution_bias`
- Prompt modes: `full` (default), `minimal` (subagents), `none` (identity only)
- Bootstrap files: AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, MEMORY.md
- Large stable content ABOVE cache boundary; volatile sections BELOW

## Configuration

### Key Config Paths
- `gateway.port` (default 18789), `gateway.bind` ("loopback"|"lan"|"tailnet"|"0.0.0.0")
- `gateway.auth.mode`, `gateway.auth.token`, `gateway.auth.password`
- `gateway.controlUi.enabled`, `gateway.controlUi.root`, `gateway.controlUi.basePath`
- `agents.defaults.model` - string (v6.8) or `{primary, fallbacks}` dict (v6.10+)
- `agents.defaults.workspace` - workspace directory
- `agents.defaults.sandbox.mode` - "off"|"non-main"|"all"
- `agents.defaults.sandbox.scope` - "agent"|"session"|"shared"
- `agents.defaults.sandbox.backend` - "docker"|"ssh"|"openshell"
- `agents.defaults.heartbeat.enabled`, `agents.defaults.heartbeat.intervalMs`
- `agents.defaults.memorySearch.provider` - "openai"|"gemini"|"ollama"|"local"|"none"|custom
- `agents.defaults.dmScope` - "main"|"per-peer"|"per-channel-peer"|"per-account-channel-peer"
- `messages.queue.mode` - "steer"|"followup"|"collect"|"interrupt"
- `messages.tts.auto` - "always"|"off" (default off)
- `messages.tts.provider` - 14 supported speech providers
- `cron.enabled`, `cron.maxConcurrentRuns` (default 8)
- `tools.exec.ask` - exec approval policy
- `tools.profile` - "minimal"|"coding"|"messaging"|"full"
- `tools.allow`/`tools.deny` - tool allow/deny lists
- `update.channel` - "stable"|"beta"|"dev"
- `update.auto.enabled` - auto-updater (off by default)

### Group/DM Policy
- DM: `pairing` (default), `allowlist`, `open` (requires `allowFrom: ["*"]`), `disabled`
- Group: `allowlist` (default), `open`, `disabled` — NO other values valid
- `mention` is INVALID for groupPolicy — causes config rejection

### Model Config (v6.10 dict format)
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "provider/model-name",
        fallbacks: ["provider/fallback1", "provider/fallback2"]
      }
    }
  }
}
```
- GCP v6.10 normalizes to dict on startup — this is VALID
- Vultr v6.8 requires string format only
- Adding provider auth does NOT change primary model
- Use `openclaw models set <provider/model>` or `--set-default` to switch

### Model Failover
- Two-stage: auth profile rotation within provider first, then model fallback
- `models.providers.<id>.models[]` with `id`, `name`, optional `maxContextTokens`
- Empty/invalid model names cause "Invalid input" schema crash
- Model refs use `provider/model` format

## Provider Reference

### Working Providers (our setup)
| Provider | Plugin ID | Env Var | Free Tier |
|----------|-----------|---------|-----------|
| Vultr | vultr | VULTR_API_KEY | Limited credits |
| Groq | groq | GROQ_API_KEY | 17 free models, rate-limited |
| OpenRouter | openrouter | OPENROUTER_API_KEY | 339+ models (pay-per-use) |
| Cohere | cohere | COHERE_API_KEY | 20 models (free tier) |
| Google/Gemini | google | GOOGLE_API_KEY | 7 models (free tier) |
| GitHub Models | github-models | GITHUB_TOKEN | 5 free models |
| HuggingFace | huggingface | HF_API_KEY | 3+ serverless (free) |
| Ollama | ollama | OLLAMA_API_KEY | Local only |
| SambaNova | sambanova | SAMBANUVA_API_KEY | Needs key |

### Key Provider Gotchas
- Groq: bundled plugin, invalid model names = gateway crash
- OpenAI-family routes are prefix-specific: `openai/<model>` uses Codex harness
- GitHub Models: endpoint `models.inference.ai.azure.com`
- HuggingFace: serverless inference API
- LiteLLM/vLLM/SGLang: self-hosted compatible endpoints
- ElevenLabs: TTS only, hCaptcha on signup
- Deepgram: STT + TTS provider

### OAuth & Auth Profiles
- OAuth supported for OpenAI Codex/ChatGPT, Anthropic (API key recommended)
- PKCE flow for OpenAI Codex OAuth
- `auth-profiles.json` is the canonical token sink (single read point)
- Profile IDs: `<provider>:<name>` (e.g. `openai:default`, `anthropic:work`)
- `auth.order.<provider>` — array of profile IDs for rotation
- Legacy `openai-codex:*` profiles repaired to `openai:*` by `openclaw doctor --fix`
- OAuth refresh tokens NOT cloned to secondary agents
- Per-session profile override: `/model Opus@anthropic:work`

### Multi-Agent Bindings
- `bindings[].agentId` + `bindings[].match` (channel, accountId, peer.kind, peer.id)
- One WhatsApp number can route different DMs to different agents via `peer.kind: "direct"` + sender ID
- `agents.list[].id`, `agents.list[].workspace`, `agents.list[].agentDir`
- Never reuse `agentDir` across agents (causes collisions)
- `tools.elevated` is global, not per-agent
- Agent-to-agent messaging: `tools.agentToAgent.enabled`

### Node Pairing
- Gateway is source of truth for node membership
- Pending requests require approval: `openclaw nodes pending` → `openclaw nodes approve <requestId>`
- `gateway.nodes.pairing.autoApproveCidrs` — array of CIDR strings for auto-approval
- `gateway.nodes.allowCommands` / `denyCommands` — global node command policy
- Tokens rotated on re-pair; `paired.json` is sensitive
- Commands queued before pairing approval are dropped

### Trusted Proxy Auth
- `gateway.auth.mode: "trusted-proxy"` — reverse-proxy identity headers
- Identity-bearing auth honors `x-openclaw-scopes`
- Mixed token + trusted-proxy is rejected

### Prometheus Metrics
- `diagnostics-prometheus` plugin exposes `GET /api/diagnostics/prometheus`
- Requires operator scope auth; do NOT expose as unauthenticated `/metrics`
- 2048 series in-memory cap; counters reset on restart
- High-cardinality labels replaced with `unknown`/`other`/`none`

### Tailscale Integration
- `gateway.auth.allowTailscale: true` — Tailscale Serve identity headers
- `gateway.bind: "tailnet"` — binds to Tailscale interface
- `discovery.wideArea.enabled` — cross-network DNS-SD over Tailscale

### Sandbox vs Tool Policy vs Elevated
- Sandbox: WHERE tools run (host vs container)
- Tool policy: WHICH tools are available (allow/deny)
- Elevated: exec-only escape hatch to run outside sandbox
- `deny` always wins; `allow` non-empty blocks unlisted tools
- Elevated exec bypasses sandboxing via `tools.elevated`

## Automation

### Cron Jobs
- Built-in Gateway scheduler, persists in SQLite
- Schedule types: `at` (one-shot), `every` (interval), `cron` (expression)
- Session targets: `main` (systemEvent only), `isolated` (agentTurn, default), `current`, `session:<id>`
- Payloads: `systemEvent` (text injection) or `agentTurn` (model prompt)
- Delivery: `none`, `announce` (chat), `webhook` (HTTP POST)
- `cron.maxConcurrentRuns` default 8
- Cron expressions without `--tz` use gateway host local timezone (NOT UTC)
- `--at` timestamps without timezone are UTC
- Top-of-hour expressions auto-staggered by up to 5 min; `--exact` to disable
- Command payloads run shell scripts without model
- `OPENCLAW_SKIP_CRON=1` disables cron

### Heartbeat
- Periodic agent turns in main session (not detached)
- `agents.defaults.heartbeat.enabled`, `agents.defaults.heartbeat.intervalMs`
- For batched checks, conversational context, approximate timing
- HEARTBEAT.md controls what agent checks
- Use cron for exact timing, isolated tasks, different models

### Hooks
- Internal: event-driven scripts (`hooks.internal.enabled`)
- Events: `command:new`, `command:reset`, `command:stop`, `session:compact:*`, `gateway:startup/shutdown`, `message:received/sent`
- Bundled: `session-memory`, `bootstrap-extra-files`, `command-logger`, `compaction-notifier`, `boot-md`
- Plugin hooks: typed hooks via `api.on(...)` — separate system

### Standing Orders
- Persistent instructions in workspace files (AGENTS.md)
- Agent reads on session start

### TaskFlow
- Multi-step detached tasks with owner context, state, waits, child tasks
- Durable job coordination

## Channels

### Telegram
- Bot token via `channels.telegram.accounts.<id>.token` or env var
- DM policy: `pairing`|`allowlist`|`open`|`disabled`
- Group policy: `allowlist`|`open`|`disabled`
- Bot loop protection: `channels.telegram.botLoopProtection` (default on)
- One bot token per agent; conflict = duplicate polling error

### Discord
- Bot token via `channels.discord.accounts.<id>.token`
- Requires Message Content Intent enabled
- One bot per agent for multi-agent

### Signal, WhatsApp, iMessage, Matrix, Slack
- Each has own auth/account setup
- Signal: phone number + signal-cli
- WhatsApp: QR pairing per account
- iMessage: BlueBubbles bridge on macOS
- Matrix: access token + homeserver
- Slack: bot token + socket mode

### Channel Routing
- `bindings[]` map channel accounts → agents
- Match on `channel`, `account`, `peer.kind`, `peer.id`
- Peer kinds: `direct`, `group`

### Bot Loop Protection
- Built-in on most channels
- Prevents agent from triggering itself in loops
- Configurable detection thresholds

## Tools

### Exec
- `tools.exec.ask` - approval policy
- `tools.exec.timeoutSec` default 1800
- `tools.exec.backgroundMs` default 10000
- `tools.exec.cleanupMs` default 1800000 (30min TTL for finished)
- `tools.exec.notifyOnExit` default true
- Elevated: `tools.elevated` bypasses sandbox
- PTY mode for interactive CLIs
- Sessions in-memory only (lost on restart)

### Browser
- OpenClaw-managed Chromium (CDP)
- Profiles: "openclaw" (isolated), "user" (logged-in)
- Snapshot + act pattern for automation
- Refs: "role" (default) or "aria" (more stable)
- Target by `targetId` for tab stability
- Browser skill available for complex flows

### Subagents
- `sessions_spawn` creates isolated child sessions
- `context="fork"` only when transcript needed; default `isolated`
- Completion is push-based — use `sessions_yield`
- Max 5 concurrent children per session (7/5 cap)
- Don't poll subagents list in loop

### Skills
- `skills.entries.<id>.enabled` + `skills.entries.<id>.config`
- Voice skills: sag, sherpa-onnx-tts, voice-call, openai-whisper, openai-whisper-api
- Skills must be CREATED (not just enabled) on nodes — create the config entry
- Skill Workshop: `skill_workshop` tool for creating/updating/proposing skills

### Memory Search
- `agents.defaults.memorySearch.provider` - embedding adapter
- `agents.defaults.memorySearch.model` - embedding model
- `agents.defaults.memorySearch.enabled` - toggle
- Providers: openai, gemini, ollama, voyage, bedrock, deepinfra, local, mistral, github-copilot, openai-compatible
- Gemini: model `gemini-embedding-001` or `gemini-embedding-2-preview`
- Changing provider/model requires `openclaw memory index --force`
- Session memory search: `agents.defaults.memorySearch.experimental.sessionMemory`

### Active Memory
- Plugin-owned blocking sub-agent that injects relevant memory before reply
- Opt-in: `plugins.entries.active-memory.enabled: true`
- `config.agents: ["main"]`, `config.allowedChatTypes: ["direct"]`
- `config.model` for dedicated recall model, or inherits session model
- `/active-memory on|off|status` for session toggle

### Dreaming
- Background memory consolidation (opt-in, disabled by default)
- Three phases: Light (sort/stage), Deep (promote to MEMORY.md), REM (reflect)
- `plugins.entries.memory-core.config.dreaming.enabled: true`
- Auto-manages cron job for sweeps (default 3am)
- Writes DREAMS.md + memory/dreaming/ phase files

### TTS
- `messages.tts.auto: "always"` to enable auto-TTS
- `messages.tts.provider` - 14 speech providers (elevenlabs, google, microsoft, deepgram, etc.)
- `tts` tool for explicit audio intent only
- [[audio_as_voice]] hint for voice notes

### Image/Video/Music Generation
- Image: `openai`, `google`, `fal`, `minimax` providers
- Video: `qwen`, `runway`, `fal` providers
- Music: `google`, `minimax` providers
- Config via provider plugins

## Sandboxing

### Modes
- `off` - no sandboxing
- `non-main` - sandbox non-main sessions (default for mixed use)
- `all` - every session sandboxed

### Backends
- **Docker** (default): local containers, supports browser sandbox
- **SSH**: remote SSH host, no browser sandbox, remote-canonical workspace
- **OpenShell**: managed remote sandbox, mirror or remote mode

### Workspace Access
- `none` (default): sandbox workspace under `~/.openclaw/sandboxes`
- `ro`: mount workspace read-only at `/agent`
- `rw`: mount workspace read-write at `/workspace`

### Custom Bind Mounts
- `agents.defaults.sandbox.docker.binds` - additional host dirs
- Format: `host:container:mode`
- Blocks dangerous sources: docker.sock, /etc, /proc, ~/.ssh, ~/.aws, etc.
- Symlink escapes fail closed

## Security

### Audit Checks
- `openclaw doctor --lint` for read-only CI checks
- `openclaw doctor --fix` for auto-repairs
- `openclaw doctor --deep` scans system services
- `openclaw doctor --non-interactive` for safe migrations only

### Exposure Runbook
- Network surface audit, firewall verification
- Token/credential rotation procedures
- Service hardening recommendations

### Secure File Operations
- File tools (read/write/edit) respect sandbox boundaries
- Symlinks resolved and validated
- SecretRefs for credential management

### Shrinkwrap
- Config integrity verification
- Prevents unauthorized config changes

## CLI Quick Reference

### Essential Commands
```bash
openclaw status                    # Quick status
openclaw gateway status            # Gateway status
openclaw gateway restart           # Restart gateway
openclaw doctor --lint             # Read-only health check
openclaw doctor --fix              # Auto-repair
openclaw models status --probe     # Model auth check
openclaw models set <ref>          # Set primary model
openclaw config get <path>         # Read config
openclaw cron list                 # List cron jobs
openclaw memory status --index     # Memory index status
openclaw memory index --force      # Rebuild memory index
openclaw update                    # Update OpenClaw
openclaw plugins list              # List plugins
openclaw plugins inspect <id>      # Inspect plugin
openclaw sessions list             # List sessions
openclaw agents list --bindings    # List agents + routing
openclaw channels status --probe   # Channel health
openclaw devices list              # Pending pairing requests
openclaw sandbox list              # List sandbox containers
```

### Config Schema
```bash
# Look up valid values for any config path
openclaw config schema lookup gateway.auth.mode
```

## Gateway Health & Monitoring

### Health Endpoints
- `GET /health` → `{"ok":true,"status":"live"}` (lightweight, use for uptime monitoring)
- NEVER use `/v1/chat/completions` for health checks — creates full sessions causing bloat
- `openclaw status` / `--all` / `--deep` for local diagnosis
- `openclaw health` / `--verbose` / `--json` for gateway snapshot

### Health Monitor Config
- `gateway.channelHealthCheckMinutes` (default 5; 0 disables health-monitor restarts)
- `gateway.channelStaleEventThresholdMinutes` (default 30; must be ≥ health check interval)
- `gateway.channelMaxRestartsPerHour` (default 10; rolling cap per channel/account)
- `channels.<provider>.healthMonitor.enabled` — per-channel override
- `diagnostics.enabled` (default true; false disables operational fact recording)
- `diagnostics.memoryPressureSnapshot` (default false; writes pre-OOM stability bundle on critical pressure)

### Relink Flow
- When status codes 409-515 appear: `openclaw channels logout && openclaw channels login --verbose`

## Agent Loop & Runtimes

### Agent Loop Stages
1. Intake → 2. Context assembly → 3. Model inference → 4. Tool execution → 5. Streaming replies → 6. Persistence
- Serialized per-session via queue lanes
- Session write lock protects transcript (acquireTimeoutMs default 60000ms)
- `diagnostics.stuckSessionWarnMs` / `diagnostics.stuckSessionAbortMs` (≥5 min, ≥3× warn)

### Runtime Selection Priority
- Model-scoped → provider-scoped → `auto` plugin claim → `openclaw` fallback
- Runtime IDs: `openclaw` (embedded), `codex` (app-server), `copilot`, `claude-cli` (CLI backend)
- Per-model: `agents.defaults.models["provider/model"].agentRuntime`
- Per-provider: `models.providers.<provider>.agentRuntime`
- Legacy `codex-cli/*` refs repaired to `openai/*` by `openclaw doctor --fix`
- Explicit runtime fails closed (never silently rerouted)

### Local Model Services
- `models.providers.<id>.localService` — start local servers on demand
- Probes `healthUrl` → if down, starts `command` with `args` → polls readiness → sends request
- `readyTimeoutMs` (default 120000), `idleStopMs` (default 0 = keep alive)
- One OpenClaw process manages its started child; another process reuses already-live health URL

### OpenAI/Responses HTTP APIs
- Enable: `gateway.http.endpoints.chatCompletions.enabled: true` or `responses.enabled: true`
- Same auth as Gateway (shared-secret, trusted-proxy, none)
- Agent-first model contract: `model: "openclaw"` / `"openclaw/default"` / `"openclaw/<agentId>"`
- `x-openclaw-model` for backend override (needs `operator.admin`)
- Sessions: stateless by default; `user` field → stable session key; `x-openclaw-session-key` for explicit routing

## Advanced Features

### Channel Docking
- Redirects replies for one session to a different linked chat channel
- Requires `session.identityLinks` grouping source and target peers
- Commands: `/dock-telegram`, `/dock-discord`, `/dock-slack`, `/dock-mattermost`
- Only changes `lastChannel`, `lastTo`, `lastAccountId` delivery fields

### Commitments
- Short-lived inferred follow-up memories (not exact reminders)
- Background extraction after eligible agent replies
- Delivery via heartbeat, scoped to exact agent + channel
- `commitments.enabled` (default off), `commitments.maxPerDay` (default 3)
- For exact reminders, use cron instead

### Compaction
- Triggered explicitly via `/compact` or automatically at token threshold
- Preserves checkpoint; can branch or restore from compacted view
- Compaction entries render as explicit divider in UI

### Context Engine
- `agents.defaults.contextEngine` — manages context assembly
- Supports different strategies for different model capabilities

## Delegate Architecture

### Three Tiers
1. **Tier 1 (Read-Only + Draft)** — read data, draft responses, never send
2. **Tier 2 (Send on Behalf)** — can send messages on behalf of human
3. **Tier 3 (Proactive/Autonomous)** — cron + standing orders, fully autonomous

### Key Rules
- Delegates act ON BEHALF of humans, never impersonate them
- Hard blocks in SOUL.md/AGENTS.md BEFORE connecting external accounts
- Tool restrictions at Gateway level independently of personality files
- Auth stores must not be shared between agents
- Identity provider access requires least-privilege scoping

## Memory System Details

### Built-in SQLite Backend
- FTS5/BM25 keyword search + vector search (embeddings) + hybrid search
- CJK trigram tokenization
- Optional sqlite-vec acceleration
- Indexes MEMORY.md + memory/*.md into ~400-token chunks with 80-token overlap
- File watcher triggers debounced reindex (1.5s)
- Auto-reindex when provider/model/chunking config changes
- Extra paths: `agents.defaults.memorySearch.extraPaths`

### Memory Search Config
- `memorySearch.provider`: openai, gemini, ollama, local, bedrock, deepinfra, github-copilot, mistral, openai-compatible, voyage
- `memorySearch.model`: provider-specific embedding model
- `memorySearch.enabled`: boolean toggle
- `memorySearch.fallback`: fallback adapter ID
- Changing provider/model = index identity change = pause vector search until rebuild
- `openclaw memory index --force --agent <id>` to rebuild

### QMD Engine
- Local-first sidecar for memory search
- Supports extra collections for cross-agent transcript search
- `memory.backend: "qmd"`, `memory.qmd.includeDefaultMemory`

### Compaction Memory Flush
- Automatic memory flush before compaction
- `agents.defaults.compaction.memoryFlush.model` — exact model for flush turn

## Channel Routing & Group Messages

### Routing
- `bindings[].match` supports: `channel`, `accountId`, `peer.kind` (direct|group), `peer.id`, `guildId`
- Default routing: DMs → agent's main session, Groups → separate session key
- `dmScope` options: main, per-peer, per-channel-peer (recommended), per-account-channel-peer

### Bot Loop Protection
- Built-in on most channels, prevents agent from triggering itself
- Configurable detection thresholds per channel

### Access Groups
- Named groups of peers for simplified allowlist management
- `channels.<channel>.accessGroups.<name>.peers[]`

## Key Gotchas & Lessons Learned

1. **GCP v6.10 normalizes model to dict format** — VALID, don't fight it
2. **Vultr v6.8 requires string model format** — only exception
3. **Groq empty model names = gateway crash** — always validate model entries
4. **groupPolicy "mention" is INVALID** — only allowlist/open/disabled
5. **dmPolicy "open" requires allowFrom: ["*"]** — won't work without it
6. **Orphan gateway processes** — kill by PID, verify port free with `ss -tlnp`, then restart systemd
7. **fail2ban can ban SSH from mesh nodes** — whitelist IPs
8. **Telegram bot token conflicts** — one token per agent, disable polling on conflicting nodes
9. **Google blocks headless browser login** — use PKCE OAuth with real browser
10. **GitHub PATs don't work for web login** — only API/Git operations
11. **Config writes are atomic** — temp + rename, won't corrupt on failure
12. **Symlinked configs unsupported** — atomic writes may replace the path
13. **Doctor has multiple modes** — --lint (read-only), --fix (repair), --deep (system scan)
14. **Subagent cap is 5 concurrent** — plan batch size accordingly
15. **Memory index changes require rebuild** — changing provider/model = pause vector search until `openclaw memory index --force`
16. **Session transcripts are append-only** — modern format, abandoned branches not rendered
17. **Compaction is explicit** — /compact command, auto at threshold
18. **Cron jobs persist in SQLite** — survive gateway restarts
19. **Heartbeat ≠ Cron** — heartbeat = main session periodic, cron = detached/exact
20. **Voice skills must be created not just enabled** — create `skills.entries` keys
21. **Health checks: use GET /health, NOT /v1/chat/completions** — latter creates full sessions
22. **Stuck sessions: diagnostics.stuckSessionWarnMs/AbortMs** — auto-releases stale lanes
23. **Runtime selection is model-scoped first** — per-model agentRuntime overrides win
24. **Local model lean mode** — `experimental.localModelLean: true` drops browser/cron/message tools
25. **OpenAI HTTP API must be explicitly enabled** — `gateway.http.endpoints.chatCompletions.enabled: true`
26. **Channel relink: logout then login** — for 409-515 status codes
27. **Commitments are OFF by default** — `commitments.enabled` must be set explicitly
28. **Block streaming off by default** — non-Telegram channels need `*.blockStreaming: true`
29. **Node commands disabled until pairing approved** — breaking change 2026.3.31+
30. **Auth profile format**: `<provider>:<name>` (e.g. `openai:default`)
31. **OAuth refresh tokens never cloned** to secondary agents — each must sign in independently
32. **Trusted proxy + token auth is rejected** — pick one or the other
33. **Prometheus endpoint requires operator auth** — never expose unauthenticated
34. **`deny` always wins** in tool policy; `allow` non-empty blocks unlisted tools

## Update System
- `openclaw update` — detects install type, fetches latest, runs doctor, restarts
- `--channel stable|beta|dev` — switch channels
- `--dry-run` — preview without applying
- Auto-updater: `update.auto.enabled: true` (off by default)
- Switch npm ↔ git: `openclaw update --channel dev` or `--channel stable`
- Manual: `npm i -g openclaw@latest` (stop gateway first)

## GCP Deployment
- e2-micro (free tier, 1GB) → often OOMs
- e2-small (2GB, ~$12/mo) → minimum recommended
- e2-medium (4GB, ~$25/mo) → most reliable
- Docker deployment with host-mounted `~/.openclaw` for persistence
- Firewall: need ports 18789, 18800 open for gateway access
- SSH: add keys to project metadata + per-instance metadata
