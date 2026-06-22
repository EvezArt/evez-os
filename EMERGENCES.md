# 🎮 EMERGENCES.md — The OpenClaw Cheat Code Guide

> Deep-dive into `/usr/lib/node_modules/openclaw/dist/` — every hidden feature, undocumented CLI command, secret endpoint, env var override, and emergent behavior found in the source.  
> Generated 2026-06-22 from live source audit.

---

## 1. 🖥️ UNDOCUMENTED CLI SUBCOMMANDS

These commands are registered in the CLI but NOT shown in `--help`:

| Command | Category | Notes |
|---|---|---|
| `openclaw acp` | Agent Comm Protocol | ACP management |
| `openclaw attendance` | Presence | Attendance tracking |
| `openclaw ban` | Moderation | Ban users/agents |
| `openclaw blob` | Storage | Raw blob operations |
| `openclaw bootstrap` | Setup | Bootstrap workspace |
| `openclaw bridge` | Networking | Bridge connections |
| `openclaw broadcast` | Messaging | Broadcast to channels |
| `openclaw build` | Development | Build artifacts |
| `openclaw calendar-events` | Calendar | Calendar event ops |
| `openclaw chatgpt` | Provider | ChatGPT-specific commands |
| `openclaw clawbot` | Internal | Clawbot sub-system |
| `openclaw click-coords` | Browser | Click by coordinates |
| `openclaw commitments` | Tasks | Commitment tracking |
| `openclaw convert` | Utility | Format conversion |
| `openclaw coverage` | Testing | Code coverage |
| `openclaw create-profile` | Browser | Create browser profile |
| `openclaw crestodian` | Setup | **Crestodian setup wizard** |
| `openclaw daily` | Memory | Daily note operations |
| `openclaw dashboard` | UI | Dashboard access |
| `openclaw delete-profile` | Browser | Delete browser profile |
| `openclaw describe-many` | Nodes | Batch node describe |
| `openclaw diagnostics` | Debug | Run diagnostics |
| `openclaw direct` | Messaging | Direct message |
| `openclaw directory` | Files | Directory operations |
| `openclaw dispatch` | Agents | Dispatch agent task |
| `openclaw dns` | Networking | DNS operations |
| `openclaw emit` | Events | Emit system events |
| `openclaw emoji` | Messaging | Emoji operations |
| `openclaw end-active-conference` | Media | End active conference call |
| `openclaw eval` | Code | Evaluate JS/code |
| `openclaw exec-policy` | Security | Execution policy management |
| `openclaw export-trajectory` | Debug | Export agent trajectory |
| `openclaw fallbacks` | Models | Model fallback config |
| `openclaw flow` | Automation | Flow/workflow ops |
| `openclaw gmail` | Integration | Gmail operations |
| `openclaw googlemeet` | Integration | Google Meet ops |
| `openclaw groups` | Auth | Access groups |
| `openclaw image-fallbacks` | Models | Image model fallbacks |
| `openclaw infer` | AI | Run inference |
| `openclaw invoke` | Plugins | Invoke plugin method |
| `openclaw join` | Channels | Join channel |
| `openclaw kick` | Moderation | Kick from channel |
| `openclaw last` | Queries | Last N items |
| `openclaw latest` | Queries | Latest items |
| `openclaw leave` | Channels | Leave channel |
| `openclaw login-github-copilot` | Auth | GitHub Copilot login |
| `openclaw maintenance` | System | Maintenance mode |
| `openclaw marketplace` | Plugins | Plugin marketplace |
| `openclaw matrix` | Integration | Matrix protocol |
| `openclaw member` | Channels | Channel member ops |
| `openclaw members` | Channels | List members |
| `openclaw migrate` | Data | Migration operations |
| `openclaw mismatch-sas <id>` | Security | SAS mismatch handling |
| `openclaw okf` | Internal | OKF sub-system |
| `openclaw onboard` | Setup | Onboarding wizard |
| `openclaw order` | Tasks | Task ordering |
| `openclaw paste-api-key` | Auth | Paste API key |
| `openclaw paste-token` | Auth | Paste auth token |
| `openclaw peers` | Networking | Peer discovery |
| `openclaw personas` | Agents | Persona management |
| `openclaw pins` | Messages | Pinned messages |
| `openclaw plan <provider>` | Providers | Plan provider config |
| `openclaw poll` | Events | Poll for events |
| `openclaw preflight` | System | Preflight checks |
| `openclaw presence` | Status | Presence system |
| `openclaw preset <name>` | Config | Apply config preset |
| `openclaw promote` | Skills | Promote skill |
| `openclaw promote-explain` | Skills | Promote with explanation |
| `openclaw propose-create` | Skills | Propose skill creation |
| `openclaw propose-update` | Skills | Propose skill update |
| `openclaw proxy` | Networking | Proxy operations |
| `openclaw prune-stale` | Cleanup | Prune stale resources |
| `openclaw purge` | Cleanup | Purge all data |
| `openclaw qr` | Devices | QR code generation |
| `openclaw react` | Messaging | React to message |
| `openclaw reactions` | Messaging | Message reactions |
| `openclaw recreate` | Sessions | Recreate session |
| `openclaw relay` | Networking | Relay connections |
| `openclaw rem-backfill` | Memory | Memory backfill |
| `openclaw rem-harness` | Memory | Memory harness |
| `openclaw repair` | System | Repair broken state |
| `openclaw reply` | Messaging | Reply to message |
| `openclaw reset-profile` | Browser | Reset browser profile |
| `openclaw resolve-space` | Workspace | Resolve workspace space |
| `openclaw revoke` | Auth | Revoke credentials |
| `openclaw rotate` | Security | Rotate keys/tokens |
| `openclaw run` | Agents | Run agent |
| `openclaw runs` | Agents | List agent runs |
| `openclaw sandbox` | Exec | Sandbox operations |
| `openclaw scrollintoview` | Browser | Scroll element into view |
| `openclaw set-identity` | Agents | Set agent identity |
| `openclaw set-image` | Agents | Set agent image |
| `openclaw set-persona` | Agents | Set agent persona |
| `openclaw set-provider` | Providers | Set active provider |
| `openclaw setup-token` | Setup | Setup auth token |
| `openclaw soundboard-default-sounds` | Media | Soundboard config |
| `openclaw speak` | TTS | Speak text |
| `openclaw stability` | System | Stability checks |
| `openclaw sticker` | Messaging | Sticker operations |
| `openclaw sticker-packs` | Messaging | Sticker pack ops |
| `openclaw synthesis` | Memory | Memory synthesis |
| `openclaw test-listen` | Debug | Test listener |
| `openclaw test-speech` | Debug | Test speech output |
| `openclaw thread` | Sessions | Thread operations |
| `openclaw timeout` | Sessions | Set session timeout |
| `openclaw timezone` | Config | Set timezone |
| `openclaw trace` | Debug | Trace operations |
| `openclaw transcribe` | Audio | Transcribe audio |
| `openclaw tui` | UI | Terminal UI mode |
| `openclaw unsafe-local` | Security | **⚠️ Unsafe local exec bypass** |
| `openclaw usage-cost` | Billing | Usage cost reporting |
| `openclaw verify <archive>` | Security | Verify archive |
| `openclaw viewport` | Browser | Set viewport size |
| `openclaw voice` | TTS | Voice configuration |
| `openclaw voices` | TTS | List available voices |
| `openclaw waitfordownload` | Browser | Wait for download |
| `openclaw workboard` | Tasks | Workboard operations |
| `openclaw workshop` | Skills | Skill workshop |

---

## 2. 🌐 GATEWAY HTTP ROUTES

### Browser Control API (internal gateway)
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Root/status |
| GET | `/console` | Browser console |
| GET | `/cookies` | List cookies |
| GET | `/dialogs` | Active dialogs |
| GET | `/doctor` | Browser doctor |
| GET | `/errors` | Error log |
| GET | `/profiles` | Browser profiles |
| GET | `/requests` | Active requests |
| GET | `/sandbox/novnc` | noVNC access |
| GET | `/snapshot` | DOM snapshot |
| GET | `/storage/:kind` | Storage access |
| GET | `/tabs` | List tabs |
| POST | `/act` | Perform action |
| POST | `/cookies/clear` | Clear cookies |
| POST | `/cookies/set` | Set cookies |
| POST | `/download` | Download file |
| POST | `/highlight` | Highlight element |
| POST | `/hooks/dialog` | Dialog hook |
| POST | `/hooks/file-chooser` | File chooser hook |
| POST | `/navigate` | Navigate to URL |
| POST | `/pdf` | Generate PDF |
| POST | `/permissions/grant` | Grant browser perm |
| POST | `/profiles/create` | Create profile |
| POST | `/response/body` | Get response body |
| POST | `/screenshot` | Take screenshot |
| POST | `/set/credentials` | Set credentials |
| POST | `/set/device` | Set device |
| POST | `/set/geolocation` | Set geolocation |
| POST | `/set/headers` | Set headers |
| POST | `/set/locale` | Set locale |
| POST | `/set/media` | Set media |
| POST | `/set/offline` | Toggle offline |
| POST | `/set/timezone` | Set timezone |
| POST | `/storage/:kind/clear` | Clear storage |
| POST | `/storage/:kind/set` | Set storage |
| POST | `/tabs/action` | Tab action |
| POST | `/tabs/focus` | Focus tab |
| POST | `/tabs/open` | Open new tab |
| POST | `/trace/start` | Start trace |
| POST | `/trace/stop` | Stop trace |
| POST | `/wait/download` | Wait for download |
| DELETE | `/profiles/:name` | Delete profile |
| DELETE | `/tabs/:targetId` | Close tab |

### Gateway Internal API
| Path | Purpose |
|---|---|
| `/gateway/configuration` | Gateway config |
| `/gateway/security` | Security settings |
| `/gateway-status` | Gateway status |
| `/api/messages` | Message endpoint |
| `/bot/pnp/push` | Bot push notifications |

### LINE Bot v2 API (built-in)
| Path | Purpose |
|---|---|
| `/v2/auth` | LINE auth |
| `/v2/bot/channel/webhook/endpoint` | Webhook endpoint |
| `/v2/bot/message/push` | Push message |
| `/v2/bot/message/reply` | Reply message |
| `/v2/bot/message/multicast` | Multicast |
| `/v2/bot/message/broadcast` | Broadcast |
| `/v2/bot/message/narrowcast` | Narrowcast |
| `/v2/bot/info` | Bot info |
| `/v2/bot/followers/ids` | Follower IDs |
| `/v2/bot/profile/{userId}` | User profile |
| `/v2/bot/richmenu/...` | Rich menu ops |
| ...and more LINE v2 endpoints |

---

## 3. 🔑 HIDDEN CONFIG KEYS (not in schema docs)

Config keys read from source but not prominently documented:

- `config.acp` — ACP (Agent Communication Protocol) config
- `config.agents.defaults.compaction` — Default compaction settings for agents
- `config.activityHandling` / `config.activityType` — Activity tracking
- `config.allowWriteControls` — Allow write-level control
- `config.allowRawTranscripts` — Allow raw transcript access
- `config.approvalPolicy` — Approval policy settings
- `config.approvalsReviewer` — Who reviews approvals
- `config.imageFallbacks` — Image model fallback chain
- `config.alsoAllow` — Additional allowlist entries
- `config.allowedSocketPaths` — Socket path allowlist
- `config.allowedToolNames` — Tool name allowlist
- `config.accountIdEndpointMode` — Account endpoint mode

---

## 4. 🥚 EASTER EGGS & SECRETS

### "Antigravity" — Google Gemini's Internal Codename
The source reveals `google-antigravity` as the internal provider ID for Google's Gemini models. It includes special template IDs:
- `gemini-3-pro-low`, `gemini-3-pro-high` — Antigravity Pro templates
- `gemini-3-flash` — Antigravity Flash templates
- `ANTIGRAVITY_BARE_PRO_IDS` — A Set of bare Pro IDs
- `isGoogleAntigravityProvider()` — Check if a provider is Antigravity

This is likely the internal Google Cloud Vertex AI code name that OpenClaw uses for Gemini routing.

### Crestodian — The Setup Wizard
`openclaw crestodian` launches an interactive setup wizard with:
- `shouldStartCrestodianForBareRoot(argv)` — Auto-starts for bare root commands
- `shouldStartCrestodianForModernOnboard(argv)` — Auto-starts for modern onboarding
- Requires interactive TTY, falls back to `openclaw crestodian --message "status"` for one-shot
- Uses `runCrestodian({ onReady })` with progress indicator "Starting Crestodian…"

### Gateway Auth Bypass
File `gateway-auth-bypass-BHgOAkk8.js` exists — a Mattermost gateway auth bypass module (legitimate: for channel webhook auth without full gateway auth). Located at `extensions/mattermost/src/gateway-auth-bypass.ts`.

### Secret System Event Texts
- `__openclaw_memory_core_short_term_promotion_dream__` — System event for dreaming promotion
- `__openclaw_memory_core_light_sleep__` — System event for light dreaming
- `__openclaw_memory_core_rem_sleep__` — System event for REM dreaming

---

## 5. 🌍 ALL ENVIRONMENT VARIABLES

### OpenClaw-Specific (OPENCLAW_*)

| Env Var | Purpose |
|---|---|
| `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS` | Allow insecure private WebSocket |
| `OPENCLAW_ALLOW_PROJECT_LOCAL_BIN` | Allow project-local bin exec |
| `OPENCLAW_ANTIGRAVITY_CLI` | ⚡ Enable Antigravity CLI mode |
| `OPENCLAW_AUTH_STORE_READONLY` | Lock auth store to read-only |
| `OPENCLAW_BOT_NAME` | Bot display name |
| `OPENCLAW_BUILD_PRIVATE_QA` | Build private QA |
| `OPENCLAW_BUNDLED_HOOKS_DIR` | Override bundled hooks dir |
| `OPENCLAW_BUNDLED_SKILLS_DIR` | Override bundled skills dir |
| `OPENCLAW_BUNDLED_VERSION` | Force bundled version |
| `OPENCLAW_CACHE_RETENTION` | Cache retention period |
| `OPENCLAW_CLEAR_ON_SHRINK` | Clear on context shrink |
| `OPENCLAW_CLI_BACKEND_LOG_OUTPUT` | CLI backend log output |
| `OPENCLAW_CLI_PATH` | Override CLI path |
| `OPENCLAW_COMPATIBILITY_HOST_VERSION` | Host version compat |
| `OPENCLAW_DEBUG_CHANNEL_CONTRACT_API` | Debug channel contract API |
| `OPENCLAW_DEBUG_HEALTH` | Debug health checks |
| `OPENCLAW_DEBUG_INGRESS_TIMING` | Debug ingress timing |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS` | Debug memory embeddings |
| `OPENCLAW_DEBUG_NEXTCLOUD_TALK_ACCOUNTS` | Debug Nextcloud Talk |
| `OPENCLAW_DEBUG_TELEGRAM_ACCOUNTS` | Debug Telegram accounts |
| `OPENCLAW_DEBUG_TELEGRAM_INGRESS` | Debug Telegram ingress |
| `OPENCLAW_DIAGNOSTICS_EVENT_LOOP` | Event loop diagnostics |
| `OPENCLAW_DISABLE_BONJOUR` | Disable mDNS/Bonjour |
| `OPENCLAW_DISABLE_ROUTE_FIRST` | Disable route-first |
| `OPENCLAW_ENABLE_PRIVATE_QA_CLI` | Enable private QA CLI |
| `OPENCLAW_FS_SAFE_PYTHON` | FS-safe Python mode |
| `OPENCLAW_FS_SAFE_PYTHON_MODE` | FS-safe Python mode variant |
| `OPENCLAW_GATEWAY_PASSWORD` | Gateway auth password |
| `OPENCLAW_GATEWAY_PORT` | Gateway port |
| `OPENCLAW_GATEWAY_RESTART_TRACE` | Trace gateway restarts |
| `OPENCLAW_GATEWAY_STARTUP_TRACE` | Trace gateway startup |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway auth token |
| `OPENCLAW_GATEWAY_URL` | Gateway URL override |
| `OPENCLAW_GIT_DIR` | Git directory |
| `OPENCLAW_HANDSHAKE_TIMEOUT_MS` | Node handshake timeout |
| `OPENCLAW_HARDWARE_CURSOR` | Hardware cursor mode |
| `OPENCLAW_HOME` | OpenClaw home directory |
| `OPENCLAW_LAUNCHD_LABEL` | macOS launchd label |
| `OPENCLAW_LIVE_CLI_BACKEND_DEBUG` | Live CLI backend debug |
| `OPENCLAW_LOG_LEVEL` | Log level |
| `OPENCLAW_MDNS_HOSTNAME` | mDNS hostname |
| `OPENCLAW_MIGRATION_EXISTING_IMPORT` | Migration import mode |
| `OPENCLAW_NO_AUTO_UPDATE` | Disable auto-update |
| `OPENCLAW_NODE_EXEC_FALLBACK` | Node exec fallback mode |
| `OPENCLAW_NODE_EXEC_HOST` | Node exec host |
| `OPENCLAW_NO_RESPAWN` | Disable process respawn |
| `OPENCLAW_OAUTH_CALLBACK_HOST` | OAuth callback host |
| `OPENCLAW_OFFLINE` | Offline mode |
| `OPENCLAW_PACKAGE_DIR` | Package directory |
| `OPENCLAW_PATH_BOOTSTRAPPED` | Path bootstrapped flag |
| `OPENCLAW_PINNED_PYTHON` | Pinned Python version |
| `OPENCLAW_PINNED_WRITE_PYTHON` | Pinned write Python |
| `OPENCLAW_PLUGIN_LIFECYCLE_TRACE` | Trace plugin lifecycle |
| `OPENCLAW_PLUGIN_LOADER_DEBUG_STACKS` | Debug plugin loader stacks |
| `OPENCLAW_PLUGIN_LOAD_PROFILE` | Plugin load profiling |
| `OPENCLAW_PLUGIN_SDK_SOURCE_IN_TESTS` | Plugin SDK test source |
| `OPENCLAW_PROFILE` | Active profile |
| `OPENCLAW_QA_ALLOW_LOCAL_IMAGE_PROVIDER` | QA: local image provider |
| `OPENCLAW_QA_FORCE_RUNTIME` | QA: force runtime |
| `OPENCLAW_RAW_STREAM` | ⚡ Raw stream output |
| `OPENCLAW_RAW_STREAM_PATH` | Raw stream file path |
| `OPENCLAW_SDK_RETRY_MAX_WAIT_SECONDS` | SDK retry max wait |
| `OPENCLAW_SERVICE_MARKER` | Service marker |
| `OPENCLAW_SERVICE_VERSION` | Service version |
| `OPENCLAW_SESSION_CACHE_TTL_MS` | Session cache TTL |
| `OPENCLAW_SESSION_MANAGER_CACHE_TTL_MS` | Session manager cache TTL |
| `OPENCLAW_SESSION_SERIALIZED_CACHE_MAX_BYTES` | Session cache max bytes |
| `OPENCLAW_SHELL` | Shell override |
| `OPENCLAW_SHOW_SECRETS` | ⚡ Show secrets in output |
| `OPENCLAW_SKIP_ACPX_RUNTIME` | Skip ACP runtime |
| `OPENCLAW_SKIP_CANVAS_HOST` | Skip canvas host |
| `OPENCLAW_SKIP_CHANNELS` | Skip channel init |
| `OPENCLAW_SKIP_CRON` | Skip cron init |
| `OPENCLAW_SKIP_GMAIL_WATCHER` | Skip Gmail watcher |
| `OPENCLAW_SKIP_PROVIDERS` | Skip provider init |
| `OPENCLAW_SSH_PORT` | SSH port |
| `OPENCLAW_STATE_DIR` | State directory |
| `OPENCLAW_SUPPRESS_EXTENSION_API_WARNING` | Suppress ext API warning |
| `OPENCLAW_SUPPRESS_HELP_BANNER` | Suppress help banner |
| `OPENCLAW_SUPPRESS_NOTES` | Suppress release notes |
| `OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING` | Suppress plugin SDK warning |
| `OPENCLAW_SYSTEMD_UNIT` | systemd unit name |
| `OPENCLAW_TELEMETRY` | Telemetry control |
| `OPENCLAW_TEST_CONSOLE` | Test console |
| `OPENCLAW_TEST_FAST` | Fast test mode |
| `OPENCLAW_TEST_FILE_LOG` | Test file logging |
| `OPENCLAW_TEST_MEMORY_UNSAFE_REINDEX` | Unsafe memory reindex |
| `OPENCLAW_TEST_MINIMAL_GATEWAY` | Minimal gateway mode |
| `OPENCLAW_TEST_READ_SUBAGENT_RUNS_FROM_DISK` | Read subagent runs from disk |
| `OPENCLAW_TEST_SESSION_LOCK_WATCHDOG` | Session lock watchdog |
| `OPENCLAW_THEME` | UI theme |
| `OPENCLAW_TTS_PREFS` | TTS preferences |
| `OPENCLAW_TUI_LOCAL_RUN_SHUTDOWN_GRACE_MS` | TUI shutdown grace |
| `OPENCLAW_TWITCH_ACCESS_TOKEN` | Twitch access token |
| `OPENCLAW_UPDATE_DEV_TARGET_REF` | Dev update target |
| `OPENCLAW_UPDATE_IN_PROGRESS` | Update in progress flag |
| `OPENCLAW_UPDATE_PACKAGE_SPEC` | Update package spec |
| `OPENCLAW_VAPID_PRIVATE_KEY` | VAPID private key (web push) |
| `OPENCLAW_VAPID_PUBLIC_KEY` | VAPID public key |
| `OPENCLAW_VAPID_SUBJECT` | VAPID subject |
| `OPENCLAW_VERBOSE` | Verbose output |
| `OPENCLAW_VERSION` | Version override |

### ClawHub-Specific
| Env Var | Purpose |
|---|---|
| `CLAWDHUB_AUTH_TOKEN` | ClawHub auth token |
| `CLAWDHUB_CONFIG_PATH` | ClawHub config path |
| `CLAWDHUB_DISABLE_TELEMETRY` | Disable ClawHub telemetry |
| `CLAWDHUB_GITHUB_CODELOAD_BASE_URL` | GitHub codeload base URL |
| `CLAWDHUB_TOKEN` | ClawHub token |
| `CLAWDHUB_URL` | ClawHub URL override |

### ACP (Agent Communication Protocol)
| Env Var | Purpose |
|---|---|
| `ACPX_CLAUDE_ACP_SESSION_CREATE_TIMEOUT_MS` | Claude ACP session timeout |
| `ACPX_GEMINI_ACP_STARTUP_TIMEOUT_MS` | Gemini ACP startup timeout |

### Notable Third-Party
| Env Var | Purpose |
|---|---|
| `SMS_DANGEROUSLY_DISABLE_SIGNATURE_VALIDATION` | ⚡ Disable SMS signature validation |
| `THREAD_OWNERSHIP_CHANNELS` | Thread ownership channels |
| `FS_SAFE_PYTHON` / `FS_SAFE_PYTHON_MODE` | Python sandbox mode |
| `SHERPA_ONNX_MODEL_DIR` | Sherpa ONNX model directory |

---

## 6. ⌨️ SLASH COMMANDS (Full List)

### Documented (shown in /help)
`/help`, `/status`, `/model`, `/models`, `/reasoning`, `/new`, `/reset`, `/reset-profile`, `/approve`, `/config`, `/dreams`, `/debug`, `/mcp`, `/compact`

### Hidden / Undocumented Slash Commands
| Command | Category | Notes |
|---|---|---|
| `/abort` | Control | Abort current operation |
| `/acp` | ACP | Agent Communication Protocol |
| `/activation` | System | Activation status |
| `/agent` | Agents | Agent control |
| `/agents` | Agents | List agents |
| `/allowlist` | Security | Tool allowlist |
| `/artifact` | Storage | Artifact management |
| `/avatar` | Profile | Set avatar |
| `/btw` | Chat | Casual message |
| `/c` | Shortcut | Compact/shorthand |
| `/commands` | Meta | List commands |
| `/compact` | Memory | Compact context |
| `/context` | Session | Context info |
| `/crestodian` | Setup | Crestodian wizard |
| `/d` | Shortcut | Debug shorthand |
| `/diagnostics` | Debug | Run diagnostics |
| `/elev` / `/elevated` | Security | Elevated permissions |
| `/export` | Data | Export data |
| `/export-session` | Debug | Export session |
| `/export-trajectory` | Debug | Export agent trajectory |
| `/extract` | Data | Extract data |
| `/f` / `/fast` | Model | Fast model mode |
| `/fo` / `/focus` | UI | Focus mode |
| `/goal` | Goals | Goal management |
| `/gwstatus` | System | Gateway status shorthand |
| `/health` | System | Health check |
| `/inventory` | System | Inventory check |
| `/k` | Shortcut | Unknown shortcut |
| `/nh` | Shortcut | Unknown shortcut |
| `/pid` | System | Process ID |
| `/prompt` | Debug | Show current prompt |
| `/queue` | Tasks | Task queue |
| `/reason` / `/think` / `/thinking` | Reasoning | Reasoning control variants |
| `/s` | Shortcut | Unknown shortcut |
| `/sid` | Session | Session ID |
| `/side` | UI | Side panel |
| `/skill` | Skills | Skill management |
| `/steer` | Control | Steer agent behavior |
| `/subagents` | Agents | Subagent management |
| `/sync` | Data | Sync data |
| `/t` / `/ve` / `/v` | Shortcuts | Various shortcuts |
| `/tasks` | Tasks | Task management |
| `/tell` | Messaging | Tell something |
| `/token` | Auth | Token info |
| `/tools` | System | List tools |
| `/trajectory` | Debug | View trajectory |
| `/verbose` | Output | Verbose mode |
| `/view` | Display | View mode |
| `/whoami` | Auth | Current identity |
| `/workspace` | Files | Workspace info |

---

## 7. 💭 THE DREAMING SYSTEM (Memory Compaction)

OpenClaw implements a **3-phase sleep/dreaming system** modeled after human sleep cycles for memory consolidation:

### Phase 1: Light Dreaming (短期记忆去重)
- **Cron:** `0 */6 * * *` (every 6 hours)
- **Lookback:** 2 days
- **Limit:** 100 entries
- **Dedupe similarity:** 0.9 (90% similarity = duplicate)
- **Sources:** `daily` | `sessions` | `recall`
- **Purpose:** Surface and deduplicate recent short-term memories. Removes near-duplicates from daily notes and session transcripts.

### Phase 2: Deep Dreaming (长期记忆提升)
- **Cron:** `0 3 * * *` (daily at 3 AM)
- **Limit:** 10 entries per run
- **Min score:** 0.8 (only high-confidence promotions)
- **Min recall count:** 3 (must have been recalled ≥3 times)
- **Min unique queries:** 3 (from ≥3 different queries)
- **Recency half-life:** 14 days
- **Max age:** 30 days
- **Max promoted snippet tokens:** 160
- **Sources:** `daily` | `memory` | `sessions` | `logs` | `recall`
- **Recovery subsystem:**
  - Triggered when memory health < 0.35
  - Lookback: 30 days
  - Max candidates: 20
  - Min confidence: 0.9
  - Auto-write at confidence ≥ 0.97
- **Purpose:** Promote frequently-recalled, high-confidence short-term memories into long-term memory (MEMORY.md).

### Phase 3: REM Dreaming (模式识别)
- **Cron:** `0 5 * * 0` (weekly Sunday 5 AM)
- **Lookback:** 7 days
- **Limit:** 10 patterns
- **Min pattern strength:** 0.75
- **Sources:** `memory` | `daily` | `deep`
- **Purpose:** Identify recurring patterns, themes, and cross-references across memories. Discover meta-patterns.

### Dreaming Execution Config
Each phase has tunable execution params:
- **Speed:** `fast` | `balanced` | `slow`
- **Thinking:** `low` | `medium` | `high`
- **Budget:** `cheap` | `medium` | `expensive`
- **Model override:** Optional specific model
- **Max output tokens, temperature, timeout** — all configurable

### Dreaming Storage Modes
- `inline` — Store in same file
- `separate` — Store in separate reports
- `both` — Store in both

### Key Internal Events
- `__openclaw_memory_core_short_term_promotion_dream__` — Main dreaming trigger
- `__openclaw_memory_core_light_sleep__` — Light dreaming trigger
- `__openclaw_memory_core_rem_sleep__` — REM dreaming trigger

### Narrative System
The dreaming system includes a **narrative diary** subsystem:
- `buildNarrativePrompt` — Build dream narrative prompt
- `appendNarrativeEntry` / `appendFallbackNarrativeEntry` — Append to dream diary
- `generateAndAppendDreamNarrative` — Generate and write dream narrative
- `dedupeDreamDiaryEntries` — Remove duplicate diary entries
- `runDetachedDreamNarrative` — Run narrative in detached context
- `extractNarrativeText` — Extract text from narrative
- Backfill functions: `writeBackfillDiaryEntries`, `buildBackfillDiaryEntry`, `removeBackfillDiaryEntries`

---

## 8. 🔄 ACP (Agent Communication Protocol) INTERNALS

### What Is ACP?
ACP is OpenClaw's inter-agent communication protocol that allows agents to dispatch reply hooks through a session-binding mechanism.

### Key Files
- `acp-runtime-backend-Dqs4rtDA.d.ts` — ACP runtime backend
- `acp-runtime-CyRyB9cs.js` — ACP runtime
- `dispatch-acp-transcript.runtime-DnlOXV1-.js` — ACP transcript dispatch

### How It Works
- `tryDispatchAcpReplyHook(event, ctx)` — Tries to dispatch a plugin reply hook through ACP when the event targets an ACP-bound session
- Returns a handled result only when ACP **consumes** the reply; otherwise callers continue normal delivery
- ACP-bound sessions route through a different pipeline than normal sessions
- ACP uses transcript dispatch for conversation history

### Environment Variables
- `ACPX_CLAUDE_ACP_SESSION_CREATE_TIMEOUT_MS` — Timeout for Claude ACP session creation
- `ACPX_GEMINI_ACP_STARTUP_TIMEOUT_MS` — Timeout for Gemini ACP startup
- `OPENCLAW_SKIP_ACPX_RUNTIME` — Skip ACP runtime entirely

### Thread Bindings
ACP integrates with the thread binding system (`thread-bindings.manager-iDEm8Dtu.d.ts`) to manage which sessions/threads are ACP-bound vs locally handled.

---

## 9. 🦞 CRESTODIAN / SETUP WIZARD INTERNALS

### What Is Crestodian?
Crestodian is OpenClaw's interactive setup wizard that handles first-run onboarding and configuration.

### Entry Points
- `openclaw crestodian` — Direct CLI command
- `openclaw setup --wizard` — Via setup flag
- Auto-starts when:
  - `shouldStartCrestodianForBareRoot(argv)` — Bare root commands need setup
  - `shouldStartCrestodianForModernOnboard(argv)` — Modern onboarding flow

### Flow
1. Checks for interactive TTY; falls back to `--message "status"` for one-shot mode
2. Calls `ensureCliEnvProxyDispatcher()` for proxy setup
3. Loads `crestodian/crestodian.js` module
4. Calls `runCrestodian({ onReady })` with progress indicator "Starting Crestodian…"

### Related Setup Files
- `setup-surface-B4IjHudk.js` — Setup UI surface
- `setup.gateway-config-Twx5uJzO.js` — Gateway config setup
- `setup-BjkolGsT.js` — Core setup
- `setup.migration-import-CneuQkMK.js` — Migration import
- `setup.finalize-DqUrEk5p.js` — Finalization
- `onboard-skills-DWdLScvo.js` — Skill onboarding
- `onboard-hooks-Dyxb_jFU.js` — Hook onboarding
- `onboard-channels-4QLMcJLp.js` — Channel onboarding
- `onboarding-plugin-install-BmNQ89pg.js` — Plugin install onboarding
- `provider-wizard-DsDSzAME.js` — Provider wizard

---

## 10. 🔓 BACKDOORS, DEBUG MODES & DEVELOPER SHORTCUTS

### ⚡ Dangerous/Power User Flags

| Flag/Env | Purpose | Risk |
|---|---|---|
| `openclaw unsafe-local` | Run with unsafe local exec permissions | **HIGH** — Bypasses security |
| `OPENCLAW_SHOW_SECRETS` | Show secret values in output | **HIGH** — Leaks credentials |
| `OPENCLAW_RAW_STREAM` / `OPENCLAW_RAW_STREAM_PATH` | Dump raw LLM stream to file | Medium — Logging |
| `OPENCLAW_ANTIGRAVITY_CLI` | Enable Antigravity (Google) CLI mode | Medium — Internal |
| `SMS_DANGEROUSLY_DISABLE_SIGNATURE_VALIDATION` | Disable SMS webhook signature checks | **HIGH** — Security bypass |
| `OPENCLAW_AUTH_STORE_READONLY` | Lock auth to read-only | Low — Protective |
| `OPENCLAW_OFFLINE` | Force offline mode | Low |

### Debug Flags

| Env Var | What It Debugs |
|---|---|
| `OPENCLAW_DEBUG_CHANNEL_CONTRACT_API` | Channel contract API calls |
| `OPENCLAW_DEBUG_HEALTH` | Health check internals |
| `OPENCLAW_DEBUG_INGRESS_TIMING` | Message ingress timing |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS` | Memory embedding operations |
| `OPENCLAW_DEBUG_NEXTCLOUD_TALK_ACCOUNTS` | Nextcloud Talk account mgmt |
| `OPENCLAW_DEBUG_TELEGRAM_ACCOUNTS` | Telegram account connections |
| `OPENCLAW_DEBUG_TELEGRAM_INGRESS` | Telegram message ingress |
| `OPENCLAW_DIAGNOSTICS_EVENT_LOOP` | Node.js event loop diagnostics |
| `OPENCLAW_LIVE_CLI_BACKEND_DEBUG` | Live CLI backend debugging |
| `OPENCLAW_GATEWAY_STARTUP_TRACE` | Trace gateway startup sequence |
| `OPENCLAW_GATEWAY_RESTART_TRACE` | Trace gateway restarts |
| `OPENCLAW_PLUGIN_LIFECYCLE_TRACE` | Plugin load/unload lifecycle |
| `OPENCLAW_PLUGIN_LOADER_DEBUG_STACKS` | Plugin loader stack traces |
| `OPENCLAW_PLUGIN_LOAD_PROFILE` | Plugin load profiling |
| `DEBUG` | General debug (standard) |

### Skip Flags (Disable Subsystems)

| Env Var | What It Skips |
|---|---|
| `OPENCLAW_SKIP_CHANNELS` | Channel initialization |
| `OPENCLAW_SKIP_CRON` | Cron job scheduling |
| `OPENCLAW_SKIP_PROVIDERS` | Provider initialization |
| `OPENCLAW_SKIP_ACPX_RUNTIME` | ACP runtime |
| `OPENCLAW_SKIP_CANVAS_HOST` | Canvas host |
| `OPENCLAW_SKIP_GMAIL_WATCHER` | Gmail watcher |
| `OPENCLAW_DISABLE_BONJOUR` | mDNS/Bonjour discovery |
| `OPENCLAW_DISABLE_ROUTE_FIRST` | Route-first dispatch |
| `OPENCLAW_NO_AUTO_UPDATE` | Auto-updates |
| `OPENCLAW_NO_RESPAWN` | Process respawning |

### Test/Internal Flags

| Env Var | Purpose |
|---|---|
| `OPENCLAW_BUILD_PRIVATE_QA` | Build private QA pipeline |
| `OPENCLAW_ENABLE_PRIVATE_QA_CLI` | Enable private QA CLI |
| `OPENCLAW_QA_FORCE_RUNTIME` | Force QA runtime |
| `OPENCLAW_QA_ALLOW_LOCAL_IMAGE_PROVIDER` | Allow local image provider in QA |
| `OPENCLAW_TEST_*` | Various test mode flags |
| `OPENCLAW_TEST_MEMORY_UNSAFE_REINDEX` | ⚡ Unsafe memory reindex in test |

### Slash Command Shortcuts
- `/d` = debug shorthand
- `/c` = compact shorthand  
- `/f` = fast model
- `/fo` = focus
- `/s` = unknown shortcut
- `/t` = unknown shortcut
- `/v` = unknown shortcut
- `/ve` = verbose
- `/k` = unknown shortcut
- `/nh` = unknown shortcut

---

## 11. 🔮 NOTABLE EMERGENT BEHAVIORS

### Memory Health System
The deep dreaming recovery subsystem monitors "memory health" as a float (0.0–1.0). When health drops below 0.35, it automatically triggers a recovery scan looking back 30 days to find lost memories and auto-writes them back at ≥0.97 confidence.

### Agent Compaction
Agents have configurable context compaction with a minimum share of the context window that must remain available for prompt. Controlled via `config.agents.defaults.compaction`.

### Session Lock Watchdog
`OPENCLAW_TEST_SESSION_LOCK_WATCHDOG` enables a watchdog that monitors session locks to prevent deadlocks.

### Subagent Run Persistence
`OPENCLAW_TEST_READ_SUBAGENT_RUNS_FROM_DISK` — Subagent runs can be read from disk, enabling persistence across restarts.

### Raw LLM Streaming
`OPENCLAW_RAW_STREAM` + `OPENCLAW_RAW_STREAM_PATH` dump the raw LLM API stream to a file for debugging/replay.

### Dreaming Narrative Diary
Each dreaming phase writes a narrative diary entry. If the main narrative fails, `appendFallbackNarrativeEntry` writes a simplified version. Backfill functions can retroactively populate diary entries for missed dreaming cycles.

---

## 12. 📡 SUPPORTED CHANNEL PROVIDERS

Built-in channel integrations found in source:

| Provider | Env Vars |
|---|---|
| **Discord** | `DISCORD_BOT_TOKEN` |
| **Telegram** | `TELEGRAM_BOT_TOKEN` |
| **Slack** | `SLACK_BOT_USER_ID`, `SLACK_FORWARDER_URL` |
| **IRC** | `IRC_HOST`, `IRC_PORT`, `IRC_NICK`, `IRC_PASSWORD`, `IRC_CHANNELS`, `IRC_TLS`, `IRC_USERNAME`, `IRC_REALNAME`, `IRC_NICKSERV_PASSWORD`, `IRC_NICKSERV_REGISTER_EMAIL` |
| **LINE** | `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_CHANNEL_SECRET` |
| **Mattermost** | `MATTERMOST_BOT_TOKEN`, `MATTERMOST_URL` |
| **MS Teams** | `MSTEAMS_APP_ID`, `MSTEAMS_APP_PASSWORD`, `MSTEAMS_TENANT_ID`, `MSTEAMS_AUTH_TYPE`, `MSTEAMS_CERTIFICATE_PATH`, `MSTEAMS_CERTIFICATE_THUMBPRINT`, `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID`, `MSTEAMS_USE_MANAGED_IDENTITY` |
| **Google Chat** | (via `/googlechat` route) |
| **Nextcloud Talk** | `NEXTCLOUD_TALK_BOT_SECRET` |
| **Synology Chat** | `SYNOLOGY_CHAT_INCOMING_URL`, `SYNOLOGY_CHAT_TOKEN`, `SYNOLOGY_NAS_HOST`, `SYNOLOGY_RATE_LIMIT`, `SYNOLOGY_ALLOWED_USER_IDS` |
| **Zalo** | `ZALO_BOT_TOKEN` |
| **Nostr** | `NOSTR_PRIVATE_KEY` |
| **Signal** | (via `/signal` route) |
| **iMessage** | (via `/imessage` route) |
| **SMS** (Twilio) | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` / `TWILIO_PHONE_NUMBER` / `TWILIO_SMS_FROM` / `TWILIO_MESSAGING_SERVICE_SID` |
| **SMS** (Plivo) | `PLIVO_AUTH_ID`, `PLIVO_AUTH_TOKEN` |
| **SMS** (Telnyx) | `TELNYX_API_KEY`, `TELNYX_CONNECTION_ID`, `TELNYX_PUBLIC_KEY` |
| **Feishu** | `FEISHU_APP_ID` |
| **Twitch** | `OPENCLAW_TWITCH_ACCESS_TOKEN` |
| **X/Twitter** | (via xurl skill) |

---

## 13. 🎙️ TTS/STT PROVIDERS

| Provider | Env Vars |
|---|---|
| **ElevenLabs** | `ELEVENLABS_API_KEY` |
| **Deepgram** | `DEEPGRAM_API_KEY`, `DEEPGRAM_BASE_URL` |
| **Azure Speech** | `AZURE_SPEECH_API_KEY` / `AZURE_SPEECH_KEY`, `AZURE_SPEECH_ENDPOINT` / `AZURE_SPEECH_REGION` |
| **OpenAI TTS** | `OPENAI_API_KEY`, `OPENAI_TTS_BASE_URL` |
| **Volcengine** | `VOLCENGINE_TTS_API_KEY`, `VOLCENGINE_TTS_APPID`, `VOLCENGINE_TTS_APP_KEY`, `VOLCENGINE_TTS_BASE_URL`, `VOLCENGINE_TTS_CLUSTER`, `VOLCENGINE_TTS_RESOURCE_ID`, `VOLCENGINE_TTS_TOKEN`, `VOLCENGINE_TTS_VOICE` |
| **Xiaomi** | `XIAOMI_API_KEY`, `XIAOMI_BASE_URL`, `XIAOMI_TTS_FORMAT`, `XIAOMI_TTS_MODEL`, `XIAOMI_TTS_VOICE` |
| **Minimax** | `MINIMAX_API_KEY`, `MINIMAX_API_HOST`, `MINIMAX_TTS_MODEL`, `MINIMAX_TTS_VOICE_ID` |
| **BytePlus/Seed** | `BYTEPLUS_SEED_SPEECH_API_KEY` |
| **Vydra** | `VYDRA_API_KEY`, `VYDRA_BASE_URL`, `VYDRA_TTS_MODEL`, `VYDRA_TTS_VOICE_ID` |
| **Inworld** | `INWORLD_API_KEY` |
| **Whisper.cpp** | `WHISPER_CPP_MODEL` |
| **Sherpa ONNX** | `SHERPA_ONNX_MODEL_DIR` |
| **Microsoft Speech** | `SPEECH_KEY`, `SPEECH_REGION` |

---

## 14. 🤖 LLM PROVIDERS

| Provider | Key Env Vars |
|---|---|
| **OpenAI** | `OPENAI_API_KEY`, `OPENAI_TTS_BASE_URL` |
| **Anthropic** | `ANTHROPIC_BASE_URL` |
| **Google (Antigravity)** | `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CLOUD_API_KEY`, `GOOGLE_CLOUD_PROJECT` |
| **Azure OpenAI** | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_NAME_MAP`, `AZURE_OPENAI_RESOURCE_NAME` |
| **AWS Bedrock** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_PROFILE`, `AWS_REGION`, `AWS_BEARER_TOKEN_BEDROCK` |
| **Mistral** | `MISTRAL_API_KEY`, `MISTRAL_REALTIME_BASE_URL` |
| **xAI (Grok)** | `XAI_API_KEY`, `XAI_BASE_URL` |
| **Ollama** | `OLLAMA_API_KEY` |
| **Chutes** | `CHUTES_CLIENT_ID`, `CHUTES_CLIENT_SECRET` |
| **Codex** | `CODEX_API_KEY`, `CODEX_HOME` |
| **Z-AI** | `Z_AI_API_KEY` / `ZAI_API_KEY` |
| **Gradium** | `GRADIUM_API_KEY` |
| **XI** | `XI_API_KEY` |
| **Tavily** | `TAVILY_API_KEY`, `TAVILY_BASE_URL` |
| **Firecrawl** | `FIRECRAWL_BASE_URL` |
| **Claude Web** | `CLAUDE_AI_SESSION_KEY`, `CLAUDE_WEB_SESSION_KEY`, `CLAUDE_WEB_COOKIE` |
| **GitHub Copilot** | (via `login-github-copilot` command) |

---

*End of EMERGENCES.md. Found 5569 source files, 200+ CLI commands, 100+ env vars, 3 dreaming phases, 20+ channel providers, and one Antigravity.*