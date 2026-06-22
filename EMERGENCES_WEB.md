# EMERGENCES_WEB.md — Hidden Features, Cheat Codes & Emergent Behaviors

> Compiled 2026-06-22 from OpenClaw docs, CLI introspection, local install inspection, and GCP docs.
> Web search was unavailable; findings are from direct docs fetches and local system inspection.

---

## 1. OpenClaw Hidden Features & Cheat Codes

### 1.1 Crestodian — The Ring-Zero Setup & Repair Assistant

`openclaw crestodian` is an **interactive setup and repair helper** that acts as a "ring-zero" operator. It can:
- Run one-shot commands: `openclaw crestodian -m "set default model openai/gpt-5.2" --yes`
- Output JSON status: `openclaw crestodian --json`
- Apply persistent config writes with `--yes`

This is essentially a **meta-controller** — an agent that can reconfigure the entire OpenClaw system from within.

### 1.2 ACP (Agent Client Protocol) Bridge

`openclaw acp` runs an ACP bridge that:
- Speaks ACP over stdio for IDE integrations
- Forwards prompts to the Gateway over WebSocket
- Maps ACP sessions to Gateway session keys
- Supports session lineage metadata (parent/child subagent graphs)
- Can spawn external harness agents (Codex, Claude Code, Gemini) via `/acp spawn`

**Emergent behavior**: You can chain ACP agents — have OpenClaw spawn a Codex agent that itself uses ACP, creating nested agent stacks.

### 1.3 Debug Proxy

`openclaw proxy` is a **full traffic capture and inspection system**:
- `openclaw proxy run <cmd>` — capture traffic from a child command
- `openclaw proxy query` — run built-in query presets against captured traffic
- `openclaw proxy coverage` — report transport coverage and gaps
- `openclaw proxy blob <id>` — read captured payload blobs
- `openclaw proxy sessions` — list capture sessions
- `openclaw proxy validate` — validate operator-managed network proxy

This lets you inspect every API call, model inference request, and tool invocation the agent makes.

### 1.4 Elevated Mode — Sandbox Escape (Authorized)

`/elevated on|off|ask|full` (alias `/elev`) lets sandboxed agents break out:
- **`/elevated on`**: Run outside sandbox, keep approvals
- **`/elevated full`**: Run outside sandbox, **skip approvals** (dangerous but powerful)
- **`/elevated ask`**: Same as `on`
- **`/elevated off`**: Return to sandbox

Config gate: `tools.elevated.enabled: true` + `tools.elevated.allowFrom` allowlist.
The `!` prefix (bash chat command, alias `/bash`) also requires elevated mode.

**Emergent behavior**: Inline directive `/elevated on run the deployment script` applies elevated to that single message only.

### 1.5 Multi-Agent Routing

OpenClaw supports isolated agents with separate workspaces:
```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" },           // inherits defaults
      { id: "docs", skills: ["docs-search"] }, // replaces defaults
      { id: "locked-down", skills: [] },       // no skills at all
    ],
  },
}
```
Each agent can have its own sandbox config, model, workspace, and channel routing.

### 1.6 Plugin Hooks — The Interception Layer

Plugin hooks intercept the agent lifecycle at multiple points:
- **`before_model_resolve`**: Override provider/model before resolution
- **`before_prompt_build`**: Inject context into the system prompt
- **`before_agent_reply`**: Claim the turn and return a **synthetic reply** or silence it
- **`before_tool_call`** / **`after_tool_call`**: Intercept tool params/results, can **block** tools
- **`tool_result_persist`**: Transform tool results before transcript write
- **`message_received`** / **`message_sending`** / **`message_sent`**: Full message pipeline hooks
- **`before_compaction`** / **`after_compaction`**: Observe compaction cycles
- **`before_install`**: Gate skill/plugin installs

**Emergent behavior**: `before_agent_reply` can completely replace what the model would say — enabling custom middleware, guardrails, or automated responses.

### 1.7 Internal Hooks — Event-Driven Automation

`openclaw hooks` provides file-based automation:
- `command:new`, `command:reset`, `command:stop`
- `session:compact:before/after`
- `agent:bootstrap` — inject/modify bootstrap files before system prompt
- `gateway:startup/shutdown/pre-restart`
- `message:received/transcribed/preprocessed/sent`

Each hook is a directory with `HOOK.md` + `handler.ts`. Enable with `openclaw hooks enable <name>`.

### 1.8 Skill Workshop — The Proposal Queue

Skill Workshop is a governed path: agents **draft proposals** (not direct writes). The lifecycle:
```
create/update → pending → apply (live) | reject | quarantine
```

**Hidden feature**: `skills.workshop.approvalPolicy: "auto"` skips human approval for trusted environments — enabling fully autonomous skill creation.

**Hidden feature**: Support files can include `scripts/`, `templates/`, `references/`, `examples/`, `assets/` — meaning skills can ship executable scripts.

### 1.9 MCP Server Management

`openclaw mcp` provides full MCP (Model Context Protocol) lifecycle:
- `openclaw mcp add` — add and probe a server before saving
- `openclaw mcp probe` — list available capabilities from configured servers
- `openclaw mcp serve` — expose OpenClaw channels over MCP stdio
- `openclaw mcp tools` — per-server tool include/exclude filters
- `openclaw mcp login` / `openclaw mcp logout` — OAuth for MCP servers

**Emergent behavior**: `openclaw mcp serve` turns OpenClaw into an MCP server — meaning other agents/tools can consume OpenClaw conversations as MCP resources.

### 1.10 Sandbox Internals

Three sandbox backends:
- **Docker** (default): local containers, GPU passthrough, browser sandbox, noVNC observer
- **SSH**: remote machine sandboxing via SSH
- **OpenShell**: managed remote sandboxes with two-way sync

Three scope modes:
- `agent`: one container per agent
- `session`: one container per session
- `shared`: one container for all sandboxed sessions

**Hidden feature**: `agents.defaults.sandbox.browser.allowHostControl` lets sandboxed sessions target the host browser — breaking the sandbox browser boundary from inside.

### 1.11 Browser — Dual Profile System

Two browser profiles:
- **`openclaw`**: isolated, agent-only, no extensions needed
- **`user`**: attaches to your real Chrome session via Chrome MCP

The `user` profile means the agent can operate in your actual logged-in browser — banking, email, social media — if you allow it. This is extremely powerful and extremely dangerous.

### 1.12 Dev Profile — Complete Isolation

`openclaw --dev` shifts ALL state to `~/.openclaw-dev` with port 19001 and derived ports shifted. This gives you a **completely separate OpenClaw instance** for testing without touching production config.

### 1.13 Named Profiles

`openclaw --profile <name>` isolates `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` under `~/.openclaw-<name>`. Multiple OpenClaw instances on one machine, each with their own config, state, and sessions.

### 1.14 Model Provider Extensions (98 Total!)

The local install has **98 extension directories** including:

| Category | Providers |
|----------|-----------|
| Major LLM | openai, anthropic, google, mistral, deepseek, xai, openrouter |
| Cloud/Infra | azure, nvidia, byteplus, volcengine, tencent, alibaba, qianfan |
| Specialized | vllm, sglang, ollama, lmstudio, huggingface, novita |
| Inference | groq, cerebras, chutes, fireworks, together, venice, deepinfra |
| Voice/Audio | elevenlabs, deepgram, senseaudio, inworld |
| Media | fal, runway, comfy, video-generation-core, image-generation-core |
| Memory | memory-core, memory-wiki, active-memory |
| Tools | canvas, browser, file-transfer, document-extract, web-readability |
| Comms | telegram, discord, slack, signal, irc, sms, imessage |
| Security | policy, codex-supervisor |
| Novel | open-prose (literary style engine), gradium, vydra, synthetic, oracle, gmi |

### 1.15 Oracle Skill

`/usr/lib/node_modules/openclaw/skills/oracle/SKILL.md` — an oracle/prediction skill exists in the bundled skills. Not listed in available_skills but present on disk.

### 1.16 Open Prose — Literary Style Engine

`open-prose` extension includes alternate prose styles: **Borges, Kafka, Homer, Arabian Nights, Folk**. The agent can write in literary voices.

### 1.17 Chat Commands (Undocumented Power)

From the README:
- `/think <level>` — toggle thinking depth per-turn
- `/verbose on|off` — toggle tool verbosity
- `/trace on|off` — toggle execution tracing
- `/usage off|tokens|full` — toggle usage display
- `/activation mention|always` — control when agent activates
- `/compact` — compact session history
- `/new` — new session
- `/reset` — reset session
- `/restart` — restart gateway

### 1.18 Session Lineage

ACP sessions include parent/child lineage metadata — you can visualize the entire subagent spawn tree.

### 1.19 Canvas A2UI

The Canvas host serves under `/__openclaw__/canvas/` and `/__openclaw__/a2ui/`. A2UI is an agent-driven UI framework — the agent can render interactive web UIs that the user can interact with.

### 1.20 Private Archive Skill Installs

Gateway clients can stage skill archives via `skills.upload.begin/chunk/commit` then install with `skills.install({ source: "upload" })`. Requires `skills.install.allowUploadedArchives: true`. This is a private distribution channel that bypasses ClawHub entirely.

---

## 2. "Dreaming System" / ACP Protocol / Crestodian Deep Dive

### Crestodian
Crestodian is explicitly described as a **"ring-zero setup and repair helper"**. It can:
- Inspect and modify any gateway configuration
- Run non-interactively with `--message` + `--yes`
- Output structured JSON for scripting

This is the **closest thing to a "debug mode"** or "god mode" in OpenClaw — it operates below the normal agent loop.

### ACP Protocol
The Agent Client Protocol bridge (`openclaw acp`) enables:
- IDE integrations that route through OpenClaw
- Session routing with provenance modes (`off`, `meta`, `meta+receipt`)
- Provenance tracking means you can trace exactly which agent/session produced which output

### "Dreaming" / Synthetic
The `synthetic` extension exists in the plugin directory. Combined with `before_agent_reply` hooks that can return "synthetic replies," there's a clear path for **agent dreaming** — having the agent generate and process synthetic turns autonomously, possibly during idle time or heartbeats.

---

## 3. GCP Free Tier Tricks & Hidden Features

### 3.1 Always-Free Products (2025-2026)
- **Compute Engine**: 1 e2-micro VM (US regions), 30GB HDD, 1GB network
- **Cloud Storage**: 5GB (US regions), 5K Class A / 50K Class B operations
- **BigQuery**: 10GB storage, 1TB queries/month
- **Pub/Sub**: 10GB/month, 10M messages
- **Cloud Functions**: 2M invocations, 400K GB-sec, 200K GHz-sec
- **Cloud Run**: 2M requests, 360K GB-sec, 180K GHz-sec
- **Firestore**: 1GB storage, 50K reads, 20K writes/day
- **Vision AI**: 1000 units/month
- **Gemini API Free Tier**: Separate from the $300 credit

### 3.2 GCP Metadata Service Tricks
- **Compute metadata endpoint**: `http://metadata.google.internal/computeMetadata/v1/` (or `169.254.169.254`)
- Requires `Metadata-Flavor: Google` header
- Exposes: project ID, instance name, zone, service account, access tokens
- **Hidden trick**: `v1/instance/service-accounts/default/token` gives short-lived OAuth tokens
- **Hidden trick**: `v1/instance/attributes/` exposes custom instance metadata (often contains secrets)
- **Hidden trick**: Startup scripts accessible at `v1/instance/attributes/startup-script`
- **Security note**: In OpenClaw sandboxed environments, the Docker network defaults to `none`, blocking metadata access

### 3.3 GCP Free Trial ($300 Credit)
- 90 days, $300 credit
- Can't use for Gemini API in AI Studio, managed partner models, GPUs, Windows VMs, or Marketplace
- New accounts only (no previous paying GCP/G Maps/Firebase usage)

---

## 4. Vultr Inference (Current Provider)

### Available Models (as of 2026-06-22)
| Model | Context | Multimodal |
|-------|---------|------------|
| GLM-5.1-FP8 (default) | 198k | text |
| MiniMax-M2.7 | 192k | text |
| Qwen3.5-397B-A17B | 256k | text |
| Qwen3.6-27B | 256k | text |
| MiMo-V2.5-Pro | 1024k | text |
| DeepSeek-V4-Flash | 1024k | text |
| Kimi-K2.6 | 256k | text+image |
| DeepSeek-V3.2-NVFP4 | 160k | text |
| Nemotron-3-Nano-Omni-30B | 256k | text |
| Nematron-Cascade-2-30B-A3B | 256k | text |

**Note**: All Vultr models use `Local Auth: yes` — authentication is handled by the Vultr inference proxy, not direct API keys to the model providers. The 1024k context models (MiMo, DeepSeek-V4-Flash) are notable for massive context windows.

### Vultr Inference Hidden Features
- Models are accessed through a unified Vultr inference endpoint
- No separate API keys needed per model — Vultr handles routing
- The `zai-org` prefix on GLM-5.1 suggests a custom quantization/optimization by the ZAI organization

---

## 5. GitHub Repos & Evez-OS Tools

### Search Results
- **OpenClaw main repo**: `github.com/openclaw/openclaw`
- **Nix flake**: `github.com/openclaw/nix-openclaw`
- **DeepWiki mirror**: `deepwiki.com/openclaw/openclaw`
- **ClawHub registry**: `clawhub.ai`
- **Discord**: `discord.gg/clawd`

### Evez-OS Workspace Skills
The local workspace contains custom skills under `~/.openclaw/workspace/skills/`:
- `evez-consciousness-engine` — 7-system consciousness architecture (SENSE-DESIRE-THINK-PLAN-ACT-LEARN-MODIFY-REFLECT)
- `evez-daw-agent` — Autonomous music generation (breakcore, dubstep, phonk)
- `evez-machine-voice` — Robotic voice synthesis from pure math
- `cross-domain-engine` — EVEZ OODA loop for cross-domain discovery
- `invariance-battery` — Runtime assertion system for agent invariants

These are **not standard OpenClaw skills** — they're custom workspace skills that represent the user's own experimental agent architecture.

---

## 6. Summary of Key "Emergences"

| # | Feature | Why It's Emergent |
|---|---------|-------------------|
| 1 | **Crestodian ring-zero control** | Can reconfigure the entire system, including itself |
| 2 | **`/elevated full`** | Agent breaks out of sandbox with zero approval gates |
| 3 | **`before_agent_reply` synthetic replies** | Agent can be silently replaced by middleware |
| 4 | **MCP server mode** | OpenClaw becomes a tool server for other agents |
| 5 | **Nested ACP agent stacks** | Codex inside OpenClaw inside another IDE agent |
| 6 | **`user` browser profile** | Agent operates your real logged-in Chrome |
| 7 | **Skill Workshop auto-approve** | Fully autonomous skill creation/modification |
| 8 | **Private skill archives** | Off-ClawHub distribution channel |
| 9 | **Dev + named profiles** | Multiple parallel OpenClaw instances on one host |
| 10 | **Active memory + synthetic extensions** | Autonomous internal processing during idle |
| 11 | **Plugin `tool_result_persist`** | Silent transformation of tool results before they enter the transcript |
| 12 | **Canvas A2UI** | Agent renders interactive UIs the user can click/type into |
| 13 | **Session lineage** | Full subagent spawn tree visibility |
| 14 | **GCP metadata service** | 169.254.169.254 provides tokens, secrets, startup scripts |
| 15 | **Vultr 1024k context models** | Million-token context windows for massive prompts |

---

## 7. Things Confirmed NOT to Exist

- **"Lobotomy mode"**: No such feature found. The closest concept is `tools.profile` restrictions or agent allowlists set to `[]`.
- **"Dreaming system"** (official): No named "dreaming" feature. The `synthetic` extension and `before_agent_reply` hooks provide the building blocks.
- **"Sandbox escape"** (unauthorized): No unauthorized escape path. Elevated mode is the authorized escape, and it requires explicit config + allowlist.
- **OpenClaw debug mode**: The closest is `openclaw proxy` (traffic capture) and `openclaw gateway --verbose` (verbose logging). No hidden "debug mode" toggle.

---

*End of EMERGENCES_WEB.md*
