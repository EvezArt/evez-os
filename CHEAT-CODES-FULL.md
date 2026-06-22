# 🎮 OpenClaw Cheat Codes — Full Source Mine

> Mined from `/usr/lib/node_modules/openclaw/dist/` — 5,569+ JS files.
> Every finding backed by source. No hallucinations.

---

## 1. 🌍 Environment Variables (Complete)

### Core System
| Variable | Purpose |
|---|---|
| `OPENCLAW_HOME` | Root directory for all OpenClaw state |
| `OPENCLAW_CONFIG_PATH` | Config file path |
| `OPENCLAW_STATE_DIR` | Persistent state directory |
| `OPENCLAW_WORKSPACE_DIR` | Agent workspace root |
| `OPENCLAW_VERSION` | Current version string |
| `OPENCLAW_VERBOSE` | Enable verbose logging |
| `OPENCLAW_DEBUG` | Master debug flag |
| `OPENCLAW_OFFLINE` | Disable all network features |
| `OPENCLAW_LOCALE` | Locale override |
| `OPENCLAW_THEME` | UI color theme |
| `OPENCLAW_PROFILE` | Config profile name |
| `OPENCLAW_PREFIX` | Install prefix |
| `OPENCLAW_TMP_DIR` | Temp directory |
| `OPENCLAW_HIDE_BANNER` | Suppress startup banner |
| `OPENCLAW_SUPPRESS_NOTES` | Suppress release notes |
| `OPENCLAW_SUPPRESS_HELP_BANNER` | Suppress help banner |

### Gateway
| Variable | Purpose |
|---|---|
| `OPENCLAW_GATEWAY_URL` | Gateway WebSocket URL |
| `OPENCLAW_GATEWAY_PORT` | Gateway port |
| `OPENCLAW_GATEWAY_TOKEN` | Auth token |
| `OPENCLAW_GATEWAY_PASSWORD` | Auth password |
| `OPENCLAW_GATEWAY_SECRET` | Gateway secret |
| `OPENCLAW_GATEWAY_INSTANCE_ID` | Instance identifier |
| `OPENCLAW_GATEWAY_SERVICE_PID` | Gateway PID |
| `OPENCLAW_GATEWAY_RESTART_TRACE` | Restart tracing |
| `OPENCLAW_GATEWAY_STARTUP_TRACE` | Startup tracing |
| `OPENCLAW_ALLOW_MULTI_GATEWAY` | Allow multiple gateways |

### Model & Provider
| Variable | Purpose |
|---|---|
| `OPENCLAW_DEFAULT_MODEL_ID` | Default model override |
| `OPENCLAW_MODEL_ID` | Model ID override |
| `OPENCLAW_ASSISTANT_MODELS` | Available model list |
| `OPENCLAW_PROVIDER_INDEX` | Provider index path |
| `OPENCLAW_LIVE_PROVIDERS` | Live provider list |
| `OPENCLAW_LIVE_GATEWAY_PROVIDERS` | Gateway provider list |
| `OPENCLAW_ANTHROPIC_PAYLOAD_LOG` | Log Anthropic payloads |
| `OPENCLAW_ANTHROPIC_PAYLOAD_LOG_FILE` | Payload log file path |

### 🔴 Debug & Unsafe
| Variable | Purpose |
|---|---|
| `OPENCLAW_SHOW_SECRETS` | **⚠️ Reveals secrets in output** |
| `OPENCLAW_RAW_STREAM` | Raw model stream capture |
| `OPENCLAW_RAW_STREAM_PATH` | Raw stream file path |
| `OPENCLAW_DEBUG_MODEL_PAYLOAD` | Dump model payloads |
| `OPENCLAW_DEBUG_MODEL_TRANSPORT` | Debug transport layer |
| `OPENCLAW_DEBUG_CHANNEL_CONTRACT_API` | Debug channel contracts |
| `OPENCLAW_DEBUG_CODE_MODE` | Debug code execution |
| `OPENCLAW_DEBUG_HEALTH` | Debug health checks |
| `OPENCLAW_DEBUG_INGRESS_TIMING` | Debug ingress timing |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS` | Debug memory embeddings |
| `OPENCLAW_DEBUG_SSE` | Debug SSE connections |
| `OPENCLAW_DEBUG_TELEGRAM_ACCOUNTS` | Debug Telegram accounts |
| `OPENCLAW_DEBUG_TELEGRAM_INGRESS` | Debug Telegram ingress |
| `OPENCLAW_DEBUG_NEXTCLOUD_TALK_ACCOUNTS` | Debug Nextcloud Talk |
| `OPENCLAW_DEBUG_PROXY_ENABLED` | Enable debug proxy |
| `OPENCLAW_DEBUG_PROXY_URL` | Debug proxy URL |
| `OPENCLAW_DEBUG_PROXY_CERT_DIR` | Debug proxy certs |
| `OPENCLAW_DEBUG_PROXY_DB_PATH` | Debug proxy DB |
| `OPENCLAW_DEBUG_PROXY_BLOB_DIR` | Debug proxy blobs |
| `OPENCLAW_DEBUG_PROXY_SESSION_ID` | Debug proxy session |
| `OPENCLAW_DIAGNOSTICS` | Enable diagnostics |
| `OPENCLAW_DIAGNOSTICS_EVENT_LOOP` | Event loop diagnostics |
| `OPENCLAW_DIAGNOSTICS_RUN_ID` | Diagnostics run ID |
| `OPENCLAW_DIAGNOSTICS_TIMELINE_PATH` | Timeline output path |

### Browser
| Variable | Purpose |
|---|---|
| `OPENCLAW_BROWSER_ENABLED` | Enable browser automation |
| `OPENCLAW_BROWSER_HEADLESS` | Force headless mode |
| `OPENCLAW_BROWSER_NO_SANDBOX` | Disable sandbox |
| `OPENCLAW_BROWSER_EXECUTABLE_PATH` | Custom Chromium path |
| `OPENCLAW_BROWSER_CDP_PORT` | CDP debug port |
| `OPENCLAW_BROWSER_CDP_AUTH_TOKEN` | CDP auth token |
| `OPENCLAW_BROWSER_COLOR` | Browser color scheme |
| `OPENCLAW_BROWSER_PROFILE_NAME` | Profile name |
| `OPENCLAW_BROWSER_ENABLE_NOVNC` | Enable noVNC |
| `OPENCLAW_BROWSER_NOVNC_PORT` | noVNC port |
| `OPENCLAW_BROWSER_NOVNC_PASSWORD` | noVNC password |
| `OPENCLAW_BROWSER_VNC_PORT` | VNC port |
| `OPENCLAW_BROWSER_AUTO_START_TIMEOUT_MS` | Auto-start timeout |
| `OPENCLAW_EAGER_BROWSER_CONTROL_SERVER` | Pre-start browser server |

### Session & Compaction
| Variable | Purpose |
|---|---|
| `OPENCLAW_SESSION_CACHE_TTL_MS` | Session cache TTL |
| `OPENCLAW_SESSION_MANAGER_CACHE_TTL_MS` | Session manager cache |
| `OPENCLAW_SESSION_SERIALIZED_CACHE_MAX_BYTES` | Max serialized cache |
| `OPENCLAW_SESSION_WRITE_LOCK_ACQUIRE_TIMEOUT_MS` | Lock acquire timeout |
| `OPENCLAW_SESSION_WRITE_LOCK_MAX_HOLD_MS` | Lock hold timeout |
| `OPENCLAW_SESSION_WRITE_LOCK_STALE_MS` | Lock staleness |
| `OPENCLAW_CLEAR_ON_SHRINK` | Clear on context shrink |

### Shell & Exec
| Variable | Purpose |
|---|---|
| `OPENCLAW_BASH_MAX_OUTPUT_CHARS` | Max exec output |
| `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS` | Max pending output |
| `OPENCLAW_BASH_YIELD_MS` | Yield interval |
| `OPENCLAW_BASH_JOB_TTL_MS` | Job TTL |
| `OPENCLAW_EXEC_SHELL_SNAPSHOT` | Shell snapshot mode |
| `OPENCLAW_SHELL` | Shell binary |
| `OPENCLAW_SHELL_ENV_TIMEOUT_MS` | Shell env timeout |
| `OPENCLAW_PROCESS_INPUT_WAIT_IDLE_MS` | Input wait idle |
| `OPENCLAW_LOAD_SHELL_ENV` | Load shell environment |

### Agent & Runtime
| Variable | Purpose |
|---|---|
| `OPENCLAW_AGENT_DIR` | Agent config directory |
| `OPENCLAW_AGENT_FIRST_URL` | First-run URL |
| `OPENCLAW_AGENT_RUNTIME_ID` | Runtime ID |
| `OPENCLAW_AGENT_CLEANUP_TIMEOUT_MS` | Agent cleanup timeout |
| `OPENCLAW_CHILD_OOM_SCORE_ADJ` | OOM score adjustment |
| `OPENCLAW_SUBAGENT_RUNTIME_REQUEST_SCOPE` | Subagent scope |

### Updates
| Variable | Purpose |
|---|---|
| `OPENCLAW_AUTO_UPDATE` | Enable auto-update |
| `OPENCLAW_NO_AUTO_UPDATE` | Disable auto-update |
| `OPENCLAW_UPDATE_IN_PROGRESS` | Update lock flag |
| `OPENCLAW_UPDATE_POST_CORE` | Post-core update |
| `OPENCLAW_UPDATE_PREFLIGHT_LINT` | Pre-update lint |

### ACPx / Codex
| Variable | Purpose |
|---|---|
| `OPENCLAW_ACPX_LEASE_ID` | ACPx lease ID |
| `OPENCLAW_ACPX_RUNTIME_STARTUP_PROBE` | ACPx startup probe |
| `OPENCLAW_CODEX_APP_SERVER_BIN` | Codex binary |
| `OPENCLAW_CODEX_APP_SERVER_ARGS` | Codex args |
| `OPENCLAW_CODEX_APP_SERVER_MODE` | Codex mode |
| `OPENCLAW_CODEX_APP_SERVER_SANDBOX` | Codex sandbox |
| `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY` | Approval policy |
| `OPENCLAW_CODEX_COMPUTER_USE` | Enable computer use |
| `OPENCLAW_CODEX_SUPERVISOR_ALLOW_RAW_TRANSCRIPTS` | Allow raw transcripts |
| `OPENCLAW_CODEX_SUPERVISOR_ENDPOINTS` | Supervisor endpoints |

### MCP
| Variable | Purpose |
|---|---|
| `OPENCLAW_MCP_ACCOUNT_ID` | MCP account |
| `OPENCLAW_MCP_AGENT_ID` | MCP agent |
| `OPENCLAW_MCP_SESSION_KEY` | MCP session |
| `OPENCLAW_MCP_TOKEN` | MCP token |
| `OPENCLAW_MCP_TOOL_PREFIX` | Tool name prefix |
| `OPENCLAW_MCP_CLI_CAPTURE_KEY` | CLI capture key |
| `OPENCLAW_MCP_MESSAGE_CHANNEL` | Message channel |
| `OPENCLAW_MCP_CURRENT_CHANNEL_ID` | Current channel |
| `OPENCLAW_MCP_CURRENT_MESSAGE_ID` | Current message |
| `OPENCLAW_MCP_CURRENT_THREAD_TS` | Thread timestamp |
| `OPENCLAW_MCP_CURRENT_INBOUND_AUDIO` | Inbound audio |
| `OPENCLAW_MCP_INBOUND_EVENT_KIND` | Event kind |
| `OPENCLAW_MCP_LOOPBACK_BODY_TIMEOUT_MS` | Loopback timeout |
| `OPENCLAW_MCP_SOURCE_REPLY_DELIVERY_MODE` | Reply delivery mode |

### Memory & Dreaming
| Variable | Purpose |
|---|---|
| `OPENCLAW_CACHE_BOUNDARY` | Cache boundary |
| `OPENCLAW_CACHE_RETENTION` | Cache retention |
| `OPENCLAW_CACHE_TRACE` | Cache tracing |
| `OPENCLAW_CACHE_TRACE_FILE` | Trace file |
| `OPENCLAW_CACHE_TRACE_MESSAGES` | Trace messages |
| `OPENCLAW_CACHE_TRACE_PROMPT` | Trace prompts |
| `OPENCLAW_CACHE_TRACE_SYSTEM` | Trace system |
| `OPENCLAW_PERSISTED_DETAIL_BOUNDARY` | Detail boundary |
| `OPENCLAW_FALLBACK_SKIP_TTL_MS` | Fallback skip TTL |
| `OPENCLAW_STRICT_FAST_REPLY_CONFIG` | Strict fast reply |

### Telephony (APNS/Vapid)
| Variable | Purpose |
|---|---|
| `OPENCLAW_APNS_KEY_ID` | Apple Push Key ID |
| `OPENCLAW_APNS_PRIVATE_KEY` | APNS private key |
| `OPENCLAW_APNS_PRIVATE_KEY_PATH` | Key file path |
| `OPENCLAW_APNS_TEAM_ID` | Apple Team ID |
| `OPENCLAW_APNS_RELAY_BASE_URL` | Push relay URL |
| `OPENCLAW_APNS_RELAY_ALLOW_HTTP` | Allow HTTP relay |
| `OPENCLAW_APNS_RELAY_TIMEOUT_MS` | Relay timeout |
| `OPENCLAW_VAPID_PUBLIC_KEY` | VAPID public key |
| `OPENCLAW_VAPID_PRIVATE_KEY` | VAPID private key |
| `OPENCLAW_VAPID_SUBJECT` | VAPID subject |

### Proxy & Network
| Variable | Purpose |
|---|---|
| `OPENCLAW_PROXY_ACTIVE` | Proxy active flag |
| `OPENCLAW_PROXY_URL` | Proxy URL |
| `OPENCLAW_PROXY_CA_FILE` | Proxy CA file |
| `OPENCLAW_PROXY_LOOPBACK_MODE` | Loopback proxy mode |
| `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS` | Allow insecure WS |
| `OPENCLAW_CONNECT_CHALLENGE_TIMEOUT_MS` | Challenge timeout |
| `OPENCLAW_MAX_PREAUTH_CONNECTIONS_PER_IP` | Pre-auth limit |
| `OPENCLAW_DISCORD_GATEWAY_INFO_TIMEOUT_MS` | Discord timeout |
| `OPENCLAW_HANDSHAKE_TIMEOUT_MS` | Handshake timeout |

### SQLite
| Variable | Purpose |
|---|---|
| `OPENCLAW_SQLITE_BUSY_TIMEOUT_MS` | SQLite busy timeout |
| `OPENCLAW_AGENT_DB_DIR_MODE` | DB dir permissions |
| `OPENCLAW_AGENT_DB_FILE_MODE` | DB file permissions |

### Misc
| Variable | Purpose |
|---|---|
| `OPENCLAW_ANTIGRAVITY_CLI` | Google Antigravity CLI path |
| `OPENCLAW_DEVICE_NAME_PREFIX` | Device name prefix |
| `OPENCLAW_TTS_PREFS` | TTS preferences |
| `OPENCLAW_HARDWARE_CURSOR` | Hardware cursor |
| `OPENCLAW_TAGLINE_INDEX` | Tagline rotation |
| `OPENCLAW_TELEMETRY` | Telemetry toggle |
| `OPENCLAW_TRAJECTORY` | Trajectory mode |
| `OPENCLAW_TRAJECTORY_DIR` | Trajectory directory |
| `OPENCLAW_TRAJECTORY_FLUSH_TIMEOUT_MS` | Trajectory flush |

---

## 2. 🖥️ CLI Subcommands

### Gateway Commands
```
openclaw gateway run          — Run gateway (foreground)
openclaw gateway call         — Call a Gateway RPC method
openclaw gateway health       — Health check
openclaw gateway stability    — Payload-free stability diagnostics
openclaw gateway usage-cost   — Usage cost summary from session logs
openclaw gateway diagnostics  — Export diagnostics .zip
openclaw gateway probe        — Reachability/auth/probe summary
openclaw gateway discover     — Bonjour mDNS discovery
```

### Gateway Call Methods (via `gateway call <method>`)
```
health                        — Health status
status                        — Full status
system-presence               — System presence info
cron.*                        — Cron job management
```

### Gateway Stability Options
```
--limit <n>                   — Max recent events (default 25)
--type <type>                 — Filter by diagnostic type
--since-seq <seq>             — Events after sequence
--bundle [path]               — Read persisted bundle ("latest")
--export                      — Write shareable diagnostics
--output <path>               — Export .zip path
```

### Gateway Diagnostics Export
```
openclaw gateway diagnostics export
  --output <path>             — Output .zip path
  --log-lines <count>        — Max log lines (default 5000)
  --log-bytes <bytes>         — Max log bytes (default 1000000)
  --url <url>                 — Gateway URL for health snapshot
  --token ***                 — Gateway token
  --password ***              — Gateway password
  --timeout <ms>              — Snapshot timeout (default 3000)
  --no-stability-bundle       — Skip stability bundle
  --json                      — JSON output
```

### Gateway Probe Options
```
--url <url>                   — Explicit WS URL
--ssh <target>                — SSH tunnel target (user@host[:port])
--ssh-identity <path>         — SSH identity file
--ssh-auto                    — Auto-derive SSH from Bonjour
--token ***                   — Gateway token
--password ***                — Gateway password
--timeout <ms>                — Budget (default 3000)
--json                        — JSON output
```

### Gateway Discover Options
```
--timeout <ms>                — Per-command timeout (default 2000)
--json                        — JSON output
```

---

## 3. 🌐 Gateway HTTP Routes (Browser Control Server)

### Navigation & Pages
| Method | Route | Purpose |
|---|---|---|
| POST | `/navigate` | Navigate to URL |
| POST | `/pdf` | Generate PDF from page |
| POST | `/screenshot` | Capture screenshot |
| GET | `/snapshot` | Get DOM snapshot (supports `?compact`, `?mode=efficient`, `?refs=aria`) |

### Actions
| Method | Route | Purpose |
|---|---|---|
| POST | `/act` | Execute browser action (click, type, fill, etc.) |
| POST | `/highlight` | Highlight element |
| POST | `/download` | Download file |
| POST | `/wait/download` | Wait for download |

### Console & Debug
| Method | Route | Purpose |
|---|---|---|
| GET | `/console` | Console messages |
| GET | `/errors` | JavaScript errors |
| GET | `/requests` | Network requests |
| GET | `/dialogs` | Open dialogs |
| POST | `/trace/start` | Start CDP trace |
| POST | `/trace/stop` | Stop CDP trace |
| POST | `/response/body` | Get response body |

### Hooks
| Method | Route | Purpose |
|---|---|---|
| POST | `/hooks/file-chooser` | File chooser handler |
| POST | `/hooks/dialog` | Dialog handler |

### Storage & Cookies
| Method | Route | Purpose |
|---|---|---|
| GET | `/cookies` | List cookies |
| POST | `/cookies/set` | Set cookies |
| POST | `/cookies/clear` | Clear cookies |
| GET | `/storage/:kind` | Read storage (localStorage, etc.) |
| POST | `/storage/:kind/set` | Write storage |
| POST | `/storage/:kind/clear` | Clear storage |

### Browser Configuration
| Method | Route | Purpose |
|---|---|---|
| POST | `/set/offline` | Set offline mode |
| POST | `/set/headers` | Set extra headers |
| POST | `/set/credentials` | Set credentials |
| POST | `/set/geolocation` | Set geolocation |
| POST | `/set/media` | Set media overrides |
| POST | `/set/timezone` | Set timezone |
| POST | `/set/locale` | Set locale |
| POST | `/set/device` | Set device emulation |

### Profiles
| Method | Route | Purpose |
|---|---|---|
| GET | `/profiles` | List profiles |
| POST | `/profiles/create` | Create profile |
| DELETE | `/profiles/:name` | Delete profile |
| POST | `/reset-profile` | Reset current profile |

### Tabs
| Method | Route | Purpose |
|---|---|---|
| GET | `/tabs` | List tabs |
| POST | `/tabs/open` | Open new tab |
| POST | `/tabs/focus` | Focus tab |
| DELETE | `/tabs/:targetId` | Close tab |
| POST | `/tabs/action` | Tab action |

### Permissions & Doctor
| Method | Route | Purpose |
|---|---|---|
| POST | `/permissions/grant` | Grant permissions |
| GET | `/doctor` | Run browser doctor |
| GET | `/` | Root info |

---

## 4. ✂️ Slash Commands & Inline Directives

### Confirmed In-Chat Commands
| Command | Purpose |
|---|---|
| `/help` | Show help |
| `/status` | Show status (model, session, context) |
| `/new` | Start fresh session |
| `/compact` | Force context compaction |
| `/model` | Switch model |
| `/reasoning` | Toggle reasoning mode |
| `/verbose` | Toggle verbose output |
| `/approve` | Approve pending action |
| `/clear` | Clear context |
| `/reset` | Reset session |
| `/tools` | Manage tools |
| `/skills` | Manage skills |
| `/diagnostics` | Show diagnostics |
| `/export` | Export data |
| `/debug` | Toggle debug mode |
| `/trace` | Toggle tracing |
| `/doctor` | Run diagnostics doctor |
| `/elevated` | Request elevated permissions |
| `/save` | Save session |
| `/quit` | Quit session |

### Inline Directive Detection
The source detects inline directives like `"hey /status"` in channel messages, allowing slash commands to work even when embedded in natural language.

---

## 5. 🔴 Debug & Unsafe Flags

### `dangerously*` Flags
| Flag | Context |
|---|---|
| `dangerouslyAllowNameMatching` | Channel allowlists (Discord, Telegram, Matrix, etc.) — resolves by mutable display name instead of stable ID |
| `dangerouslyDisableDeviceAuth` | Bypasses device authentication |
| `dangerouslyDisableSignatureValidation` | SMS — skips Twilio signature check |
| `dangerouslyAllowPrivateNetwork` | Matrix/Mattermost — allows connecting to private IPs |
| `dangerouslyAllowBrowser` | Allows browser in restricted mode |
| `dangerouslyAllowContainerNamespaceJoin` | Container namespace escape |
| `dangerouslyAllowEnvProxyWithoutPinnedDns` | Proxy without DNS pinning |
| `dangerouslyAllowExternalBindSources` | External bind sources |
| `dangerouslyAllowHostHeaderOriginFallback` | Host header origin fallback |
| `dangerouslyAllowInheritedWebhookPath` | Inherited webhook path |
| `dangerouslyAllowReservedContainerTargets` | Reserved container targets |
| `dangerouslyForceUnsafeInstall` | Force unsafe plugin install |

### `OPENCLAW_SHOW_SECRETS`
⚠️ **Critical** — When set, secrets (API keys, tokens, passwords) are displayed in plaintext in logs, status output, and error messages. Default is redacted.

### `OPENCLAW_RAW_STREAM` / `OPENCLAW_RAW_STREAM_PATH`
Captures raw model API streams to a file for debugging. Shows the full request/response cycle including tokens, headers, and payloads.

### `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS`
Allows unencrypted WebSocket connections to the private gateway API. Intended for local dev only.

### `OPENCLAW_BROWSER_NO_SANDBOX`
Runs Chromium without sandbox — required in some container environments but removes security isolation.

---

## 6. 🧠 Dream System (Memory Compaction)

### Overview
The Dream System is a **3-phase automated memory consolidation** system that runs during idle periods, analogous to human sleep cycles.

### Phase 1: Light Dreaming 💡
| Setting | Default |
|---|---|
| **Cron** | `0 */6 * * *` (every 6 hours) |
| **Lookback** | 2 days |
| **Limit** | 100 items |
| **Dedupe Similarity** | 0.9 |
| **Sources** | `daily`, `sessions`, `recall` |
| **Event Text** | `__openclaw_memory_core_light_sleep__` |
| **Cron Tag** | `[managed-by=memory-core.dreaming.light]` |

### Phase 2: Deep Dreaming 🔮
| Setting | Default |
|---|---|
| **Cron** | `0 3 * * *` (daily at 3 AM) |
| **Limit** | 10 items |
| **Min Score** | 0.8 |
| **Min Recall Count** | 3 |
| **Min Unique Queries** | 3 |
| **Recency Half-Life** | 14 days |
| **Max Age** | 30 days |
| **Max Promoted Snippet Tokens** | 160 |
| **Sources** | `daily`, `memory`, `sessions`, `logs`, `recall` |
| **Recovery Enabled** | `true` |
| **Recovery Trigger** | Health < 0.35 |
| **Recovery Lookback** | 30 days |
| **Recovery Max Candidates** | 20 |
| **Recovery Min Confidence** | 0.9 |
| **Recovery Auto-Write Min** | 0.97 |

### Phase 3: REM Dreaming 🌙
| Setting | Default |
|---|---|
| **Cron** | `0 5 * * 0` (Sunday 5 AM) |
| **Lookback** | 7 days |
| **Limit** | 10 items |
| **Min Pattern Strength** | 0.75 |
| **Sources** | `memory`, `daily`, `deep` |
| **Event Text** | `__openclaw_memory_core_rem_sleep__` |

### Execution Config (All Phases)
| Setting | Options | Default |
|---|---|---|
| **Speed** | `fast`, `balanced`, `slow` | `balanced` |
| **Thinking** | `low`, `medium`, `high` | `medium` |
| **Budget** | `cheap`, `medium`, `expensive` | `medium` |
| **Model** | Override model | (default agent model) |
| **Max Output Tokens** | Token limit | (provider default) |
| **Temperature** | Sampling temp | (provider default) |
| **Timeout** | Timeout ms | (provider default) |

### Storage Config
| Setting | Options | Default |
|---|---|---|
| **Mode** | `inline`, `separate`, `both` | `separate` |
| **Separate Reports** | bool | `false` |

### Global Dreaming Config
| Setting | Default |
|---|---|
| **Enabled** | `false` |
| **Frequency** | `0 3 * * *` |
| **Timezone** | (system) |
| **Verbose Logging** | `false` |
| **Plugin ID** | `memory-core` |

### Cron Job Names
- `Memory Dreaming Promotion` — short-term promotion
- `Memory Light Dreaming` — light phase
- `Memory REM Dreaming` — REM phase

### System Event Texts
- `__openclaw_memory_core_short_term_promotion_dream__` — main promotion
- `__openclaw_memory_core_light_sleep__` — light phase trigger
- `__openclaw_memory_core_rem_sleep__` — REM phase trigger

---

## 7. 🪐 "Antigravity" — Hidden Google Provider

### What Is It?
**"Antigravity"** is the internal codename for Google Gemini's direct CLI integration (like Anthropic's Claude Code). It allows OpenClaw to route requests through Google's own CLI rather than making raw API calls.

### Source Evidence
- `isGoogleAntigravityProvider(providerId)` — provider identity check
- `OPENCLAW_ANTIGRAVITY_CLI` — env var for CLI path
- `isAntigravityCliCommand(command)` — detects if a command is for the Antigravity CLI
- Provider IDs: `google`, `google-antigravity`, `google-gemini-cli`
- `ANTIGRAVITY_BARE_PRO_IDS` — bare provider ID list

### Model Families Under Antigravity
```
gemini-3
gemini-3-flash
gemini-3-flash-lite
gemini-3-flash-preview
gemini-3-pro
gemini-3-pro-high
gemini-3-pro-low
gemini-3-pro-preview
gemini-flash-latest
gemini-flash-lite-latest
gemini-pro-latest
gemma-4
gemma-4-26b
```

### Gemini OAuth
| Variable | Purpose |
|---|---|
| `OPENCLAW_GEMINI_OAUTH_CLIENT_ID` | OAuth client ID |
| `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET` | OAuth client secret |

---

## 8. 🤖 Built-In Model IDs

### Known Model Refs (from source)
| Provider/Model | Source |
|---|---|
| `anthropic/claude-opus-4.6` | Model catalog |
| `anthropic/claude-sonnet-4.6` | Model catalog |
| `openai/gpt-5.4` | Model catalog |
| `openai/gpt-5.4-pro` | Model catalog |
| `openai/gpt-oss-120b` | Model catalog |
| `openai/gpt-oss-20b` | Model catalog |
| `deepseek/deepseek-r1-0528` | Model catalog |
| `deepseek/deepseek-v3-0324` | Model catalog |
| `deepseek-v4-flash` | Internal models list |
| `deepseek-v4-pro` | Internal models list |
| `deepseek-chat` | Internal models list |
| `deepseek-reasoner` | Internal models list |
| `google/gemini-3.1-flash-lite` | Model catalog |
| `minimax/minimax-m2.7` | Model catalog |
| `moonshotai/kimi-k2.5` | Model catalog |
| `moonshotai/kimi-k2.6` | Model catalog |
| `qwen/qwen3-235b-a22b-fp8` | Model catalog |
| `unsloth/gemma-3-12b-it` | Model catalog |
| `unsloth/gemma-3-27b-it` | Model catalog |
| `unsloth/gemma-3-4b-it` | Model catalog |
| `vultr/zai-org/GLM-5.1-FP8` | Active runtime model |

### Provider Auth Env Vars
| Variable | Provider |
|---|---|
| `GOOGLE_API_KEY` | Google/Gemini |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI |
| `AZURE_API_KEY` | Azure |
| `DEEPSEEK_API_KEY` | DeepSeek |
| `FIREWORKS_API_KEY` | Fireworks AI |
| `PERPLEXITY_API_KEY` | Perplexity |
| `NOVITA_API_KEY` | Novita AI |
| `MINIMAX_CODE_PLAN_KEY` | MiniMax |
| `AWS_SECRET_ACCESS_KEY` | AWS/Bedrock |

---

## 9. 📡 Channel Providers (24 Built-In)

| Plugin ID | Label | Key Env Vars |
|---|---|---|
| `discord` | Discord | `DISCORD_TOKEN` |
| `telegram` | Telegram | `TELEGRAM_BOT_TOKEN` |
| `slack` | Slack | `SLACK_BOT_TOKEN` |
| `imessage` | iMessage | Bridge CLI |
| `irc` | IRC | `IRC_NICK`, `IRC_HOST` |
| `matrix` | Matrix | `MATRIX_ACCESS_TOKEN`, `MATRIX_HOMESERVER` |
| `mattermost` | Mattermost | `MATTERMOST_BOT_TOKEN`, `MATTERMOST_URL` |
| `msteams` | Microsoft Teams | Service account |
| `googlechat` | Google Chat | `GOOGLE_CHAT_SERVICE_ACCOUNT` |
| `whatsapp` | WhatsApp | Phone pairing |
| `signal` | Signal | Phone number |
| `line` | LINE | `LINE_CHANNEL_ACCESS_TOKEN` |
| `feishu` | Feishu/Lark | App credentials |
| `twitch` | Twitch | `TWITCH_ACCESS_TOKEN` |
| `sms` | SMS (Twilio/Plivo/Telnyx) | Provider credentials |
| `nostr` | Nostr | Nsec key |
| `nextcloud-talk` | Nextcloud Talk | Server URL + token |
| `synology-chat` | Synology Chat | Server URL + token |
| `qqbot` | QQ Bot | App credentials |
| `zalo` | Zalo | OA token |
| `zalouser` | Zalo User | User credentials |
| `clickclack` | ClickClack | — |
| `tlon` | Tlon/Urbit | — |
| `qa-channel` | QA Channel (test) | — |

---

## 10. 🏗️ Compaction System

### Compaction Triggers
1. **Auto-compaction** — when context window fills past reserve
2. **`/compact` command** — manual trigger
3. **Preflight compaction** — before a new turn if context is too large
4. **Overflow compaction** — emergency when context limit is hit mid-turn

### Compaction Config
- `agents.defaults.compaction.reserveTokensFloor` — minimum context reserve
- `agents.defaults.compaction.notifyUser` — show compaction notices
- Compaction count tracked in session metadata

### Error Recovery
- Compaction failure preserves session mapping
- User message: *"Try again, use /compact, or use /new to start a fresh session."*
- Mid-compaction overflow: *"Context limit exceeded during compaction. I've reset our conversation to start fresh."*

### Heartbeat Model Bleed
When heartbeat uses a different model, compaction can fail. Fix:
- Set `heartbeat.isolatedSession: true`
- Enable `heartbeat.lightContext: true`
- Use a heartbeat model with larger context window

---

## 11. 🔐 Security Architecture

### Device Auth
- Default: device-bound authentication required
- `dangerouslyDisableDeviceAuth` — bypass (emergency only)
- Pairing flow: QR code or setup code

### Gateway Auth
- Token-based: `OPENCLAW_GATEWAY_TOKEN`
- Password-based: `OPENCLAW_GATEWAY_PASSWORD`
- Both can coexist

### Pre-auth Rate Limiting
- `OPENCLAW_MAX_PREAUTH_CONNECTIONS_PER_IP` — limits unauthenticated connections

### VPC Service Controls
- Perimeter restricts: storage, pubsub, logging, monitoring
- Ingress: mesh CIDRs + Vultr IP only
- Egress: deny-all default

---

## 12. 🎨 A2UI Components (Agent-Rendered UI)

```
a2ui-audioplayer    a2ui-button       a2ui-card
a2ui-checkbox       a2ui-column       a2ui-datetimeinput
a2ui-divider        a2ui-icon         a2ui-image
a2ui-list           a2ui-modal        a2ui-multiplechoice
a2ui-root           a2ui-row          a2ui-slider
a2ui-surface        a2ui-tabs         a2ui-text
a2ui-textfield      a2ui-validation-input   a2ui-video
```

---

## 13. 📊 Key Internal Types

### Compaction Reason Classification
- `compact-reasons` module classifies why compaction was needed

### Model Fallback Chain
- `model-fallback` module — tries alternate models when primary fails
- `LiveSessionModelSwitchError` — thrown when live model switch fails
- `repairProviderWrappedModelOverride` — fixes provider-wrapped model refs

### Model Selection
- `resolveDefaultModelForAgent` — picks agent's model
- `resolveConfiguredModelRef` — resolves model aliases
- `buildModelAliasIndex` — index of all model aliases
- `buildConfiguredModelCatalog` — full model catalog

### Session Reset
- `resolveSessionResetPolicy` — when to reset
- `resolveSessionResetType` — what kind of reset
- `evaluateSessionFreshness` — how fresh is the session

---

## Appendix: Env Var Count

**Total unique `OPENCLAW_*` environment variables found: 280+**

Organized by prefix:
- `OPENCLAW_AGENT_*` — 8
- `OPENCLAW_ACPX_*` — 3
- `OPENCLAW_ALLOW_*` — 2
- `OPENCLAW_ANTHROPIC_*` — 2
- `OPENCLAW_APNS_*` — 7
- `OPENCLAW_AUTO_*` / `NO_AUTO_*` — 2
- `OPENCLAW_BASH_*` — 5
- `OPENCLAW_BETA_*` — 2
- `OPENCLAW_BROWSER_*` — 13
- `OPENCLAW_CACHE_*` — 8
- `OPENCLAW_CHILD_*` — 1
- `OPENCLAW_CLAWHUB_*` — 3
- `OPENCLAW_CLI_*` — 6
- `OPENCLAW_CODEX_*` — 9
- `OPENCLAW_CONFIG_*` — 3
- `OPENCLAW_DEBUG_*` — 15
- `OPENCLAW_DEFAULT_*` — 2
- `OPENCLAW_DIAGNOSTICS_*` — 5
- `OPENCLAW_DISABLE_*` — 8
- `OPENCLAW_GATEWAY_*` — 10
- `OPENCLAW_GEMINI_*` — 2
- `OPENCLAW_GOOGLE_*` — 7
- `OPENCLAW_LIVE_*` — 8
- `OPENCLAW_MCP_*` — 14
- `OPENCLAW_PLUGIN_*` — 8
- `OPENCLAW_PROXY_*` — 4
- `OPENCLAW_QA_*` — 6
- `OPENCLAW_SESSION_*` — 6
- `OPENCLAW_SKIP_*` — 8
- `OPENCLAW_SSH_*` — 1
- `OPENCLAW_STATE_*` — 6
- `OPENCLAW_TEST_*` — 15
- `OPENCLAW_TTS_*` — 1
- `OPENCLAW_UPDATE_*` — 12
- `OPENCLAW_VAPID_*` — 3

---

*Generated from source mining on 2026-06-22. All data extracted from compiled JS in `/usr/lib/node_modules/openclaw/dist/`.*
