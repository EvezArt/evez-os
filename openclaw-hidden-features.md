# OpenClaw Hidden Features & Internals

**Mined from source:** `/usr/lib/node_modules/openclaw/dist/`  
**Date:** 2026-06-22  
**Version:** Current installed (Node v22.22.3 runtime)

---

## 1. CLI Subcommands (Full List)

### Top-Level Commands
These are registered via Commander `.command()` across the CLI source files.

| Command | Category | Notes |
|---------|----------|-------|
| `gateway` | Core | Run, inspect, query WebSocket Gateway |
| `gateway run` | Gateway | Run gateway foreground |
| `gateway call` | Gateway | Call any Gateway RPC method directly |
| `gateway health` | Gateway | Fetch gateway health |
| `gateway stability` | Gateway | Stability diagnostics |
| `gateway diagnostics` | Gateway | Export support diagnostics |
| `gateway diagnostics export` | Gateway | Write shareable diagnostics .zip |
| `gateway probe` | Gateway | Show reachability, auth, read-probe |
| `gateway discover` | Gateway | Discover gateways via Bonjour |
| `gateway usage-cost` | Gateway | Usage cost summary |
| `system` | Core | System operations |
| `system start` | Service | Start gateway service |
| `system stop` | Service | Stop gateway service |
| `system restart` | Service | Restart gateway service |
| `system status` | Service | Service status |
| `system install` | Service | Install system service |
| `system uninstall` | Service | Uninstall system service |
| `cron` | Scheduling | Cron job management |
| `devices` | Node | Device management |
| `devices list` | Node | List paired devices |
| `devices approve <requestId>` | Node | Approve device pairing |
| `pairing` | Node | Pairing operations |
| `qr` | Node | QR code generation |
| `hooks` | Hooks | Hook management |
| `hooks relay` | Hooks | **HIDDEN** — Internal native harness hook relay |
| `docs` | Docs | Documentation |
| `completion` | Shell | Shell completion |
| `update` | Update | Self-update |
| `path` | Workspace | Inspect/edit workspace via oc:// paths |

### Wiki Subcommands (under `wiki` command group)
| Command | Notes |
|---------|-------|
| `wiki init` | Initialize wiki vault |
| `wiki get` | Get wiki page |
| `wiki search` | Search wiki |
| `wiki lint` | Lint wiki vault |
| `wiki compile` | Compile wiki |
| `wiki apply` | Apply wiki mutations |
| `wiki synthesis` | Run wiki synthesis |
| `wiki obsidian` | Obsidian integration |
| `wiki obsidian status` | Obsidian status |
| `wiki obsidian search` | Obsidian search |
| `wiki obsidian open` | Open in Obsidian |
| `wiki obsidian daily` | Obsidian daily notes |
| `wiki obsidian command` | Run Obsidian command |
| `wiki import` | Import into wiki |
| `wiki bridge import` | Bridge import |
| `wiki ingest` | Ingest content |
| `wiki metadata` | Page metadata |
| `wiki doctor` | Wiki health check |
| `wiki palace` | Memory palace |
| `wiki status` | Wiki status |
| `wiki unsafe-local import` | **HIDDEN** — Import from unsafe local paths |

### Workboard Subcommands (under `workboard` command group)
| Command | Notes |
|---------|-------|
| `workboard boards list` | List boards |
| `workboard boards upsert` | Create/update board |
| `workboard boards archive` | Archive board |
| `workboard boards delete` | Delete board |
| `workboard cards create` | Create card |
| `workboard cards list` | List cards |
| `workboard cards update` | Update card |
| `workboard cards.delete` | Delete card |
| `workboard cards.archive` | Archive card |
| `workboard cards.complete` | Mark complete |
| `workboard cards.claim` | Claim card |
| `workboard cards.reclaim` | Reclaim card |
| `workboard cards.release` | Release card |
| `workboard cards.block` | Block card |
| `workboard cards.unblock` | Unblock card |
| `workboard cards.move` | Move card |
| `workboard cards.link` | Link cards |
| `workboard cards.linkDependency` | Link as dependency |
| `workboard cards.promote` | Promote card |
| `workboard cards.dispatch` | Dispatch card |
| `workboard cards.decompose` | Decompose card |
| `workboard cards.specify` | Specify card |
| `workboard cards.proof` | Add proof |
| `workboard cards.comment` | Comment on card |
| `workboard cards.heartbeat` | Heartbeat signal |
| `workboard cards.runs` | Card runs |
| `workboard cards.stats` | Card stats |
| `workboard cards.diagnostics` | Card diagnostics |
| `workboard cards.diagnostics.refresh` | Refresh diagnostics |
| `workboard cards.protocolViolation` | Report protocol violation |
| `workboard cards.reassign` | Reassign card |
| `workboard cards.workerLog` | Worker log |
| `workboard cards.export` | Export cards |
| `workboard cards.bulk` | Bulk operations |
| `workboard cards.artifact` | Card artifact |
| `workboard cards.attachments.add` | Add attachment |
| `workboard cards.attachments.list` | List attachments |
| `workboard cards.attachments.get` | Get attachment |
| `workboard cards.attachments.delete` | Delete attachment |
| `workboard notifications.list` | List notifications |
| `workboard notifications.events` | Notification events |
| `workboard notifications.advance` | Advance notification |
| `workboard notifications.delete` | Delete notification |
| `workboard notifications.subscribe` | Subscribe to notifications |

---

## 2. Gateway RPC Methods (Full Catalog)

These are WebSocket RPC methods callable via `openclaw gateway call <method>`.

### Core Methods
| Method | Scope | Description |
|--------|-------|-------------|
| `health` | operator.read | Health check |
| `status` | operator.read | Gateway status |
| `diagnostics.stability` | operator.read | Stability diagnostics |
| `logs.tail` | operator.read | Tail gateway logs |
| `channels.status` | operator.read | Channel status |
| `channels.start` | operator.admin | Start channel |
| `channels.stop` | operator.admin | Stop channel |
| `channels.logout` | operator.admin | Logout channel |

### Configuration
| Method | Scope | Description |
|--------|-------|-------------|
| `config.get` | operator.read | Get config |
| `config.set` | operator.admin | Set config value |
| `config.apply` | operator.admin | Apply config (control plane) |
| `config.patch` | operator.admin | Patch config (control plane) |
| `config.schema` | operator.admin | Get config schema |
| `config.schema.lookup` | operator.read | Lookup config schema |
| `config.openFile` | — | Open config file |

### Memory & Dream System
| Method | Scope | Description |
|--------|-------|-------------|
| `doctor.memory.status` | operator.read | Memory system health |
| `doctor.memory.dreamDiary` | operator.read | View dream diary |
| `doctor.memory.backfillDreamDiary` | operator.write | Backfill dream diary |
| `doctor.memory.resetDreamDiary` | operator.write | Reset dream diary |
| `doctor.memory.resetGroundedShortTerm` | operator.write | Reset grounded short-term memory |
| `doctor.memory.repairDreamingArtifacts` | operator.write | Repair dreaming artifacts |
| `doctor.memory.dedupeDreamDiary` | operator.write | Deduplicate dream diary |
| `doctor.memory.remHarness` | operator.read | REM harness status |

### Sessions
| Method | Scope | Description |
|--------|-------|-------------|
| `sessions.create` | — | Create session |
| `sessions.list` | — | List sessions |
| `sessions.get` | — | Get session |
| `sessions.describe` | — | Describe session |
| `sessions.delete` | — | Delete session |
| `sessions.reset` | — | Reset session |
| `sessions.abort` | — | Abort session |
| `sessions.cleanup` | — | Cleanup sessions |
| `sessions.compact` | — | Compact session |
| `sessions.patch` | — | Patch session |
| `sessions.pluginPatch` | — | Plugin patch session |
| `sessions.preview` | — | Preview session |
| `sessions.resolve` | — | Resolve session |
| `sessions.send` | — | Send to session |
| `sessions.steer` | — | Steer session |
| `sessions.subscribe` | — | Subscribe to session |
| `sessions.unsubscribe` | — | Unsubscribe from session |
| `sessions.usage` | — | Session usage |
| `sessions.usage.logs` | — | Usage logs |
| `sessions.usage.timeseries` | — | Usage timeseries |
| `sessions.compaction.list` | — | List compactions |
| `sessions.compaction.get` | — | Get compaction |
| `sessions.compaction.restore` | — | Restore compaction |
| `sessions.compaction.branch` | — | Branch compaction |
| `sessions.messages.subscribe` | — | Subscribe to messages |
| `sessions.messages.unsubscribe` | — | Unsubscribe from messages |

### Chat
| Method | Scope | Description |
|--------|-------|-------------|
| `chat.send` | — | Send chat message |
| `chat.abort` | — | Abort chat |
| `chat.history` | — | Chat history |
| `chat.startup` | — | Chat startup |
| `chat.inject` | — | Inject into chat |
| `chat.metadata` | — | Chat metadata |
| `chat.message.get` | — | Get specific message |

### Agent & Identity
| Method | Scope | Description |
|--------|-------|-------------|
| `agent.identity.get` | — | Get agent identity |
| `agent.wait` | — | Wait for agent |
| `agents.create` | — | Create agent |
| `agents.update` | — | Update agent |
| `agents.delete` | — | Delete agent |
| `agents.list` | — | List agents |
| `agents.files.get` | — | Get agent files |
| `agents.files.list` | — | List agent files |
| `agents.files.set` | — | Set agent files |
| `gateway.identity.get` | — | Get gateway identity |

### Exec & Approvals
| Method | Scope | Description |
|--------|-------|-------------|
| `exec.approvals.get` | operator.admin | Get approval policy |
| `exec.approvals.set` | operator.admin | Set approval policy |
| `exec.approvals.node.get` | operator.admin | Get node approval policy |
| `exec.approvals.node.set` | operator.admin | Set node approval policy |
| `exec.approval.get` | operator.approvals | Get approval |
| `exec.approval.list` | operator.approvals | List approvals |
| `exec.approval.request` | operator.approvals | Request approval |
| `exec.approval.waitDecision` | operator.approvals | Wait for approval decision |
| `exec.approval.resolve` | operator.approvals | Resolve approval |

### Node Management
| Method | Scope | Description |
|--------|-------|-------------|
| `node.list` | — | List paired nodes |
| `node.describe` | — | Describe node |
| `node.invoke` | — | Invoke on node |
| `node.invoke.result` | — | Get invoke result |
| `node.event` | — | Node event |
| `node.pair.request` | — | Request pairing |
| `node.pair.list` | — | List pairing requests |
| `node.pair.approve` | — | Approve pairing |
| `node.pair.reject` | — | Reject pairing |
| `node.pair.remove` | — | Remove pairing |
| `node.pair.verify` | — | Verify pairing |
| `node.pending.enqueue` | — | Enqueue pending |
| `node.pending.pull` | — | Pull pending |
| `node.pending.drain` | — | Drain pending |
| `node.pending.ack` | — | Acknowledge pending |
| `node.rename` | — | Rename node |
| `node.pluginSurface.refresh` | — | Refresh plugin surface |

### Device Pairing
| Method | Scope | Description |
|--------|-------|-------------|
| `device.pair.list` | — | List device pair requests |
| `device.pair.approve` | — | Approve device |
| `device.pair.reject` | — | Reject device |
| `device.pair.remove` | — | Remove device |
| `device.token.rotate` | — | Rotate device token |
| `device.token.revoke` | — | Revoke device token |

### Models & Providers
| Method | Scope | Description |
|--------|-------|-------------|
| `models.list` | — | List available models |
| `models.authStatus` | — | Check model auth status |
| `models.authLogout` | — | Logout model auth |

### TTS
| Method | Scope | Description |
|--------|-------|-------------|
| `tts.status` | operator.read | TTS status |
| `tts.providers` | operator.read | List TTS providers |
| `tts.personas` | operator.read | List TTS personas |
| `tts.enable` | operator.write | Enable TTS |
| `tts.disable` | operator.write | Disable TTS |
| `tts.convert` | operator.write | Convert text to speech |
| `tts.setProvider` | operator.write | Set TTS provider |
| `tts.setPersona` | operator.write | Set TTS persona |

### Talk (Realtime Voice)
| Method | Scope | Description |
|--------|-------|-------------|
| `talk.mode` | — | Talk mode |
| `talk.config` | — | Talk config |
| `talk.catalog` | — | Talk catalog |
| `talk.speak` | — | Speak |
| `talk.client.create` | — | Create talk client |
| `talk.client.steer` | — | Steer talk client |
| `talk.client.toolCall` | — | Talk tool call |
| `talk.session.create` | — | Create talk session |
| `talk.session.join` | — | Join talk session |
| `talk.session.close` | — | Close talk session |
| `talk.session.startTurn` | — | Start turn |
| `talk.session.endTurn` | — | End turn |
| `talk.session.cancelTurn` | — | Cancel turn |
| `talk.session.cancelOutput` | — | Cancel output |
| `talk.session.steer` | — | Steer session |
| `talk.session.appendAudio` | — | Append audio |
| `talk.session.submitToolResult` | — | Submit tool result |

### Voice Wake
| Method | Scope | Description |
|--------|-------|-------------|
| `voicewake.get` | — | Get voice wake config |
| `voicewake.set` | — | Set voice wake config |
| `voicewake.routing.get` | — | Get voice wake routing |
| `voicewake.routing.set` | — | Set voice wake routing |

### Cron
| Method | Scope | Description |
|--------|-------|-------------|
| `cron.add` | — | Add cron job |
| `cron.get` | — | Get cron job |
| `cron.list` | — | List cron jobs |
| `cron.remove` | — | Remove cron job |
| `cron.update` | — | Update cron job |
| `cron.run` | — | Run cron job |
| `cron.runs` | — | List cron runs |
| `cron.status` | — | Cron status |

### Tasks
| Method | Scope | Description |
|--------|-------|-------------|
| `tasks.list` | — | List tasks |
| `tasks.get` | — | Get task |
| `tasks.cancel` | — | Cancel task |

### Skills
| Method | Scope | Description |
|--------|-------|-------------|
| `skills.search` | — | Search skills |
| `skills.detail` | — | Skill detail |
| `skills.status` | — | Skills status |
| `skills.bins` | — | Skill bins |
| `skills.install` | — | Install skill |
| `skills.update` | — | Update skill |
| `skills.skillCard` | — | Skill card |
| `skills.securityVerdicts` | — | Security verdicts |
| `skills.proposals.list` | — | List proposals |
| `skills.proposals.create` | — | Create proposal |
| `skills.proposals.update` | — | Update proposal |
| `skills.proposals.revise` | — | Revise proposal |
| `skills.proposals.inspect` | — | Inspect proposal |
| `skills.proposals.apply` | — | Apply proposal |
| `skills.proposals.reject` | — | Reject proposal |
| `skills.proposals.quarantine` | — | Quarantine proposal |
| `skills.proposals.requestRevision` | — | Request revision |
| `skills.upload.begin` | — | Begin skill upload |
| `skills.upload.chunk` | — | Upload chunk |
| `skills.upload.commit` | — | Commit upload |

### Tools & Commands
| Method | Scope | Description |
|--------|-------|-------------|
| `tools.catalog` | — | Tool catalog |
| `tools.effective` | — | Effective tools |
| `tools.invoke` | — | Invoke tool |
| `commands.list` | — | List commands |

### Other
| Method | Scope | Description |
|--------|-------|-------------|
| `wizard.start` | — | Start wizard |
| `wizard.next` | — | Wizard next step |
| `wizard.cancel` | — | Cancel wizard |
| `wizard.status` | — | Wizard status |
| `update.status` | — | Update status |
| `update.run` | — | Run update |
| `usage.status` | operator.read | Usage status |
| `usage.cost` | operator.read | Usage cost |
| `secrets.reload` | aux | Reload secrets |
| `secrets.resolve` | aux | Resolve secrets |
| `nativeHook.invoke` | — | Invoke native hook |
| `push.web.subscribe` | — | Subscribe to push |
| `push.web.unsubscribe` | — | Unsubscribe from push |
| `push.web.test` | — | Test push |
| `push.web.vapidPublicKey` | — | VAPID public key |
| `push.test` | — | Test push |
| `browser.request` | — | Browser control request |
| `web.login.start` | — | Start web login |
| `web.login.wait` | — | Wait for web login |
| `gateway.restart.request` | — | Request gateway restart |
| `gateway.restart.preflight` | — | Restart preflight check |
| `message.action` | — | Message action |
| `send` | — | Send message |
| `wake` | — | Wake |
| `poll` | — | Poll |
| `connect` | — | Connect |
| `environments.list` | — | List environments |
| `environments.status` | — | Environments status |
| `assistant.media.get` | — | Get assistant media |
| `artifacts.list` | — | List artifacts |
| `artifacts.get` | — | Get artifact |
| `artifacts.download` | — | Download artifact |
| `plugins.uiDescriptors` | operator.read | Plugin UI descriptors |
| `plugins.sessionAction` | dynamic | Plugin session action |
| `plugin.approval.list` | operator.approvals | Plugin approval list |
| `plugin.approval.request` | operator.approvals | Plugin approval request |
| `plugin.approval.waitDecision` | operator.approvals | Wait for plugin approval |
| `plugin.approval.resolve` | operator.approvals | Resolve plugin approval |

---

## 3. Gateway Events (WebSocket)

| Event | Description |
|-------|-------------|
| `connect.challenge` | Connection challenge |
| `agent` | Agent event |
| `chat` | Chat event |
| `session.message` | Session message |
| `session.operation` | Session operation |
| `session.tool` | Session tool call |
| `sessions.changed` | Sessions changed |
| `presence` | Presence update |
| `tick` | Tick event |
| `talk.mode` | Talk mode change |
| `talk.event` | Talk event |
| `shutdown` | Gateway shutdown |
| `health` | Health event |
| `heartbeat` | Heartbeat |
| `cron` | Cron event |
| `node.pair.requested` | Node pair requested |
| `node.pair.resolved` | Node pair resolved |
| `node.invoke.request` | Node invoke request |
| `device.pair.requested` | Device pair requested |
| `device.pair.resolved` | Device pair resolved |
| `voicewake.changed` | Voice wake changed |
| `voicewake.routing.changed` | Voice wake routing changed |
| `exec.approval.requested` | Exec approval requested |
| `exec.approval.resolved` | Exec approval resolved |
| `plugin.approval.requested` | Plugin approval requested |
| `plugin.approval.resolved` | Plugin approval resolved |
| `update.available` | Update available |

---

## 4. Browser Control HTTP API

These are HTTP endpoints served by the browser control server:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root/index |
| `/console` | GET | Browser console |
| `/cookies` | GET | List cookies |
| `/cookies/set` | POST | Set cookies |
| `/cookies/clear` | POST | Clear cookies |
| `/dialogs` | GET | List open dialogs |
| `/doctor` | GET | Browser doctor |
| `/errors` | GET | Browser errors |
| `/profiles` | GET | List browser profiles |
| `/profiles/:name` | DELETE | Delete profile |
| `/profiles/create` | POST | Create profile |
| `/requests` | GET | List requests |
| `/sandbox/novnc` | GET | noVNC access |
| `/snapshot` | GET | Page snapshot |
| `/storage/:kind` | GET | Get storage (local/session) |
| `/storage/:kind/clear` | POST | Clear storage |
| `/storage/:kind/set` | POST | Set storage value |
| `/tabs` | GET | List tabs |
| `/tabs/:targetId` | DELETE | Close tab |
| `/tabs/action` | POST | Tab action |
| `/tabs/focus` | POST | Focus tab |
| `/tabs/open` | POST | Open tab |
| `/act` | POST | Perform action |
| `/download` | POST | Download file |
| `/highlight` | POST | Highlight element |
| `/hooks/dialog` | POST | Dialog hook |
| `/hooks/file-chooser` | POST | File chooser hook |
| `/navigate` | POST | Navigate URL |
| `/pdf` | POST | Generate PDF |
| `/permissions/grant` | POST | Grant permission |
| `/response/body` | POST | Response body |
| `/screenshot` | POST | Take screenshot |
| `/set/credentials` | POST | Set credentials |
| `/set/device` | POST | Set device emulation |
| `/set/geolocation` | POST | Set geolocation |
| `/set/headers` | POST | Set headers |
| `/set/locale` | POST | Set locale |
| `/set/media` | POST | Set media |
| `/set/offline` | POST | Set offline mode |
| `/set/timezone` | POST | Set timezone |
| `/trace/start` | POST | Start trace |
| `/trace/stop` | POST | Stop trace |
| `/wait/download` | POST | Wait for download |

---

## 5. Environment Variables (Curated)

### Debug & Tracing
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_DEBUG` | Master debug flag |
| `OPENCLAW_DEBUG_CODE_MODE` | Debug code mode |
| `OPENCLAW_DEBUG_HEALTH` | Debug health checks |
| `OPENCLAW_DEBUG_INGRESS_TIMING` | Debug ingress timing |
| `OPENCLAW_DEBUG_MODEL_PAYLOAD` | Debug model API payloads |
| `OPENCLAW_DEBUG_MODEL_TRANSPORT` | Debug model transport layer |
| `OPENCLAW_DEBUG_CHANNEL_CONTRACT_API` | Debug channel contract API |
| `OPENCLAW_DEBUG_SSE` | Debug Server-Sent Events |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS` | Debug memory embeddings |
| `OPENCLAW_DEBUG_TELEGRAM_ACCOUNTS` | Debug Telegram accounts |
| `OPENCLAW_DEBUG_TELEGRAM_INGRESS` | Debug Telegram ingress |
| `OPENCLAW_DEBUG_PROXY_ENABLED` | Enable debug proxy |
| `OPENCLAW_DEBUG_PROXY_URL` | Debug proxy URL |
| `OPENCLAW_DEBUG_PROXY_SESSION_ID` | Debug proxy session ID |
| `OPENCLAW_DEBUG_PROXY_REQUIRE` | Require debug proxy |
| `OPENCLAW_DEBUG_PROXY_BLOB_DIR` | Proxy blob directory |
| `OPENCLAW_DEBUG_PROXY_CERT_DIR` | Proxy cert directory |
| `OPENCLAW_DEBUG_PROXY_DB_PATH` | Proxy DB path |
| `OPENCLAW_VERBOSE` | Verbose output mode |

### Cache Tracing
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_CACHE_TRACE` | Enable cache tracing |
| `OPENCLAW_CACHE_TRACE_FILE` | Cache trace output file |
| `OPENCLAW_CACHE_TRACE_MESSAGES` | Trace cache messages |
| `OPENCLAW_CACHE_TRACE_PROMPT` | Trace cache prompts |
| `OPENCLAW_CACHE_TRACE_SYSTEM` | Trace cache system |
| `OPENCLAW_CACHE_BOUNDARY` | Cache boundary config |
| `OPENCLAW_CACHE_RETENTION` | Cache retention policy |

### Model & Provider
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_DEFAULT_MODEL_ID` | Default model ID |
| `OPENCLAW_MODEL_ID` | Override model ID |
| `OPENCLAW_ANTHROPIC_PAYLOAD_LOG` | Log Anthropic payloads |
| `OPENCLAW_ANTHROPIC_PAYLOAD_LOG_FILE` | Anthropic payload log file |
| `OPENCLAW_LIVE_ANTHROPIC_KEY` | Live Anthropic API key |
| `OPENCLAW_LIVE_OPENAI_KEY` | Live OpenAI API key |
| `OPENCLAW_LIVE_GEMINI_KEY` | Live Gemini API key |
| `OPENCLAW_LIVE_GATEWAY` | Live gateway URL |
| `OPENCLAW_LIVE_PROVIDERS` | Live providers config |
| `OPENCLAW_LIVE_PROVIDER_DISCOVERY_TIMEOUT_MS` | Provider discovery timeout |
| `OPENCLAW_ASSISTANT_MODELS` | Assistant models config |

### Gateway
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_GATEWAY_URL` | Gateway WebSocket URL |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway auth token |
| `OPENCLAW_GATEWAY_PASSWORD` | Gateway auth password |
| `OPENCLAW_GATEWAY_PORT` | Gateway port |
| `OPENCLAW_GATEWAY_SECRET` | Gateway secret |
| `OPENCLAW_GATEWAY_INSTANCE_ID` | Gateway instance ID |
| `OPENCLAW_GATEWAY_DISCOVERY_ADVERTISE_TIMEOUT_MS` | Discovery advertise timeout |

### Browser
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_BROWSER_ENABLED` | Enable browser |
| `OPENCLAW_BROWSER_HEADLESS` | Headless mode |
| `OPENCLAW_BROWSER_NO_SANDBOX` | Disable sandbox |
| `OPENCLAW_BROWSER_CDP_PORT` | Chrome DevTools Protocol port |
| `OPENCLAW_BROWSER_CDP_AUTH_TOKEN` | CDP auth token |
| `OPENCLAW_BROWSER_EXECUTABLE_PATH` | Browser executable path |
| `OPENCLAW_BROWSER_PROFILE_NAME` | Browser profile name |
| `OPENCLAW_BROWSER_AUTO_START_TIMEOUT_MS` | Auto-start timeout |
| `OPENCLAW_BROWSER_ENABLE_NOVNC` | Enable noVNC |
| `OPENCLAW_BROWSER_NOVNC_PORT` | noVNC port |
| `OPENCLAW_BROWSER_VNC_PORT` | VNC port |
| `OPENCLAW_BROWSER_NOVNC_PASSWORD` | noVNC password |
| `OPENCLAW_BROWSER_COLOR` | Browser color |
| `OPENCLAW_BROWSER_CONTROL_MODULE` | Control module |
| `OPENCLAW_EAGER_BROWSER_CONTROL_SERVER` | Eager start browser server |
| `OPENCLAW_HARDWARE_CURSOR` | Hardware cursor mode |
| `OPENCLAW_SKIP_BROWSER_CONTROL_SERVER` | Skip browser control server |

### Exec & Shell
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_BASH_JOB_TTL_MS` | Bash job TTL |
| `OPENCLAW_BASH_MAX_OUTPUT_CHARS` | Max output chars |
| `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS` | Max pending output chars |
| `OPENCLAW_BASH_YIELD_MS` | Bash yield timeout |
| `OPENCLAW_SHELL` | Shell override |
| `OPENCLAW_SHELL_ENV_TIMEOUT_MS` | Shell env timeout |
| `OPENCLAW_EXEC_SHELL_SNAPSHOT` | Shell snapshot capture |
| `OPENCLAW_NODE_EXEC_HOST` | Node exec host |
| `OPENCLAW_NODE_EXEC_FALLBACK` | Node exec fallback |

### Paths & Workspace
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_HOME` | OpenClaw home directory |
| `OPENCLAW_WORKSPACE_DIR` | Workspace directory |
| `OPENCLAW_STATE_DIR` | State directory |
| `OPENCLAW_CONFIG_PATH` | Config file path |
| `OPENCLAW_TMP_DIR` | Temp directory |
| `OPENCLAW_AGENT_DIR` | Agent directory |
| `OPENCLAW_PACKAGE_DIR` | Package directory |

### Diagnostics
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_DIAGNOSTICS` | Enable diagnostics |
| `OPENCLAW_DIAGNOSTICS_ENV` | Diagnostics env dump |
| `OPENCLAW_DIAGNOSTICS_EVENT_LOOP` | Event loop monitoring |
| `OPENCLAW_DIAGNOSTICS_RUN_ID` | Diagnostics run ID |
| `OPENCLAW_DIAGNOSTICS_TIMELINE_PATH` | Timeline output path |

### Network & Proxy
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_PROXY_URL` | Proxy URL |
| `OPENCLAW_PROXY_ACTIVE` | Proxy active flag |
| `OPENCLAW_PROXY_CA_FILE` | Proxy CA file |
| `OPENCLAW_PROXY_LOOPBACK_MODE` | Loopback proxy mode |
| `OPENCLAW_OFFLINE` | Offline mode |
| `OPENCLAW_SSH_PORT` | SSH port |
| `OPENCLAW_TAILNET_DNS` | Tailscale DNS |
| `OPENCLAW_WIDE_AREA_DOMAIN` | Bonjour wide-area domain |
| `OPENCLAW_MDNS_HOSTNAME` | mDNS hostname |
| `OPENCLAW_DISABLE_BONJOUR` | Disable Bonjour/mDNS |

### Database & Sessions
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_SQLITE_BUSY_TIMEOUT_MS` | SQLite busy timeout |
| `OPENCLAW_SESSION_CACHE_TTL_MS` | Session cache TTL |
| `OPENCLAW_SESSION_MANAGER_CACHE_TTL_MS` | Session manager cache TTL |
| `OPENCLAW_SESSION_SERIALIZED_CACHE_MAX_BYTES` | Session cache max bytes |
| `OPENCLAW_SESSION_WRITE_LOCK_ACQUIRE_TIMEOUT_MS` | Lock acquire timeout |
| `OPENCLAW_SESSION_WRITE_LOCK_MAX_HOLD_MS` | Lock max hold time |
| `OPENCLAW_SESSION_WRITE_LOCK_STALE_MS` | Lock stale threshold |
| `OPENCLAW_AGENT_CLEANUP_TIMEOUT_MS` | Agent cleanup timeout |
| `OPENCLAW_AGENT_DB_DIR_MODE` | DB directory mode |
| `OPENCLAW_AGENT_DB_FILE_MODE` | DB file mode |

### Channels (Discord, Telegram, etc.)
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_DISCORD_GATEWAY_INFO_TIMEOUT_MS` | Discord gateway timeout |
| `OPENCLAW_DISCORD_READY_TIMEOUT_MS` | Discord ready timeout |
| `OPENCLAW_DISCORD_RUNTIME_READY_TIMEOUT_MS` | Discord runtime ready timeout |
| `OPENCLAW_TELEGRAM_DISABLE_AUTO_SELECT_FAMILY` | Disable Telegram auto-select |
| `OPENCLAW_TELEGRAM_DNS_RESULT_ORDER` | Telegram DNS order |
| `OPENCLAW_TELEGRAM_SPOOLED_HANDLER_TIMEOUT_MS` | Telegram handler timeout |
| `OPENCLAW_FEISHU_HTTP_TIMEOUT_MS` | Feishu HTTP timeout |
| `OPENCLAW_FEISHU_STARTUP_PROBE_TIMEOUT_MS` | Feishu startup timeout |

### Update & Auto-Update
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_AUTO_UPDATE` | Auto update config |
| `OPENCLAW_NO_AUTO_UPDATE` | Disable auto update |
| `OPENCLAW_UPDATE_IN_PROGRESS` | Update in progress flag |
| `OPENCLAW_UPDATE_POST_CORE` | Post-core update |
| `OPENCLAW_UPDATE_DEV_TARGET_REF` | Dev target ref |
| `OPENCLAW_UPDATE_PREFLIGHT_LINT` | Preflight lint |

### Misc
| Variable | Purpose |
|----------|---------|
| `OPENCLAW_RAW_STREAM` | Raw stream mode |
| `OPENCLAW_RAW_STREAM_PATH` | Raw stream path |
| `OPENCLAW_SHOW_SECRETS` | Show secrets in output |
| `OPENCLAW_HIDE_BANNER` | Hide startup banner |
| `OPENCLAW_SUPPRESS_NOTES` | Suppress notes |
| `OPENCLAW_SUPPRESS_HELP_BANNER` | Suppress help banner |
| `OPENCLAW_THEME` | UI theme |
| `OPENCLAW_LOCALE` | Locale |
| `OPENCLAW_LIVE_TEST` | Live test mode |
| `OPENCLAW_LIVE_CLI_BACKEND_DEBUG` | CLI backend debug |
| `OPENCLAW_LIVE_CLI_BACKEND_PRESERVE_ENV` | Preserve CLI env |
| `OPENCLAW_TTS_PREFS` | TTS preferences |
| `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS` | Allow insecure WS |
| `OPENCLAW_ALLOW_MULTI_GATEWAY` | Allow multiple gateways |
| `OPENCLAW_ALLOW_OLDER_BINARY_DESTRUCTIVE_ACTIONS` | Allow older binary actions |
| `OPENCLAW_ALLOW_PLUGIN_INSTALL_OVERRIDES` | Allow plugin install overrides |
| `OPENCLAW_TRAJECTORY` | Trajectory capture mode |
| `OPENCLAW_TRAJECTORY_DIR` | Trajectory output dir |
| `OPENCLAW_TRAJECTORY_FLUSH_TIMEOUT_MS` | Trajectory flush timeout |
| `OPENCLAW_DEVICE_NAME_PREFIX` | Device name prefix |
| `OPENCLAW_CONTAINER` | Container hint |
| `OPENCLAW_NIX_MODE` | Nix mode |
| `OPENCLAW_PINNED_PYTHON` | Pinned Python path |
| `OPENCLAW_FS_SAFE_PYTHON` | Safe Python mode |

---

## 6. Slash Commands (Full Registry)

### Essential Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `/help` | — | Show available commands |
| `/status` | — | Show current status |
| `/stop` | — | Stop the current run |
| `/reset` | — | Reset the current session |
| `/new` | — | Start a new session |
| `/compact` | — | Compact session context |
| `/think` | `/thinking`, `/t` | Set thinking level (off/low/medium/high/xhigh/adaptive/max) |
| `/model` | — | Show or set the model |
| `/models` | — | List model providers/models |
| `/export-session` | `/export` | Export session to HTML |
| `/export-trajectory` | `/trajectory` | Export JSONL trajectory |
| `/crestodian` | — | Run Crestodian setup/repair |

### Standard Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `/commands` | — | List all slash commands |
| `/tools` | — | List available runtime tools (compact/verbose) |
| `/skill` | — | Run a skill by name |
| `/context` | — | Explain context building |
| `/verbose` | `/v` | Toggle verbose mode (on/off/full) |
| `/reasoning` | `/reason` | Toggle reasoning visibility (on/off/stream) |
| `/fast` | — | Toggle fast mode (status/on/off/default) |
| `/usage` | — | Usage footer/cost (off/tokens/full/cost) |
| `/tts` | — | Control TTS (on/off/status/provider/limit/summary/audio/help) |
| `/whoami` | `/id` | Show your sender ID |
| `/session` | — | Session settings (idle/max-age) |
| `/subagents` | — | Inspect subagent runs |
| `/agents` | — | List thread-bound agents |
| `/steer` | `/tell` | Send guidance to active run |
| `/tasks` | — | List background tasks |
| `/diagnostics` | — | Gateway diagnostics |
| `/goal` | — | Goal control (status/start/pause/resume/complete/block/clear) |

### Power Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `/config` | — | Show/set config (show/get/set/unset) |
| `/mcp` | — | MCP server management |
| `/plugins` | `/plugin` | Plugin management (list/show/enable/disable) |
| `/debug` | — | Runtime debug overrides (show/reset/set/unset) |
| `/exec` | — | Exec defaults (host/security/ask/node) |
| `/elevated` | `/elev` | Elevated mode (on/off/ask/full) |
| `/activation` | — | Group activation (mention/always) |
| `/send` | — | Send policy (on/off/inherit) |
| `/allowlist` | — | List/add/remove allowlist |
| `/approve` | — | Approve/deny exec requests |
| `/queue` | — | Queue settings (mode/debounce/cap/drop) |
| `/trace` | — | Toggle plugin trace (on/off/raw) |
| `/bash` | — | Run host shell commands (text-only) |
| `/acp` | — | ACP session management (spawn/cancel/steer/close/sessions/status/set-mode/set/cwd/permissions/timeout/model/reset-options/doctor/install/help) |
| `/focus` | — | Bind thread to session target |
| `/unfocus` | — | Remove thread binding |
| `/btw` | `/side` | Side question without affecting context |
| `/restart` | — | Restart OpenClaw |

### Dynamic Dock Commands
These are generated per loaded channel plugin:
- `/dock-<plugin-id>` — Switch reply surface to a specific channel plugin
- `/dock_<plugin-id>` — Alias (underscore form)

---

## 7. Model Provider IDs (Built-In)

All provider identifiers found in the source:

| Provider ID | Type | Notes |
|-------------|------|-------|
| `anthropic` | API | Anthropic direct |
| `anthropic-messages` | API | Anthropic messages API |
| `anthropic-public` | API | Anthropic public |
| `anthropic-vertex` | API | Anthropic via Google Vertex |
| `openai` | API | OpenAI direct |
| `openai-public` | API | OpenAI public |
| `openai-responses` | API | OpenAI responses API |
| `openai-chatgpt-responses` | API | ChatGPT-style responses |
| `openai-codex` | API | OpenAI Codex |
| `azure-openai` | API | Azure OpenAI |
| `google` | API | Google Generative AI |
| `google-antigravity` | **HIDDEN** | Google Antigravity (internal/low-latency Gemini endpoint) |
| `google-gemini-cli` | API | Google via Gemini CLI |
| `google-vertex` | API | Google Vertex AI |
| `google-generative-ai` | API | Google Generative AI API |
| `deepseek` | API | DeepSeek |
| `deepseek-native` | API | DeepSeek native |
| `groq` | API | Groq |
| `groq-native` | API | Groq native |
| `xai` | API | xAI (Grok) |
| `xai-native` | API | xAI native |
| `cerebras` | API | Cerebras |
| `cerebras-native` | API | Cerebras native |
| `mistral` | API | Mistral |
| `mistral-public` | API | Mistral public |
| `together` | API | Together AI |
| `fireworks` | API | Fireworks AI |
| `perplexity` | API | Perplexity |
| `ollama` | API | Ollama (local) |
| `openrouter` | API | OpenRouter |
| `github-copilot` | API | GitHub Copilot |
| `github-copilot-native` | API | Copilot native |
| `copilot-proxy` | API | Copilot proxy |
| `claude-cli` | API | Claude CLI |
| `vllm` | API | vLLM |
| `nvidia` | API | NVIDIA |
| `nvidia-native` | API | NVIDIA native |
| `deepinfra` | API | DeepInfra |
| `novita` | API | Novita AI |
| `chutes` | API | Chutes |
| `chutes-native` | API | Chutes native |
| `venice` | API | Venice AI |
| `moonshot` | API | Moonshot (Kimi) |
| `moonshot-native` | API | Moonshot native |
| `minimax` | API | MiniMax |
| `qwen` | API | Qwen (Alibaba) |
| `qwen-chat-template` | API | Qwen chat template |
| `qianfan` | API | Qianfan (Baidu) |
| `volcengine` | API | Volcengine (ByteDance) |
| `volcengine-plan` | API | Volcengine plan |
| `byteplus` | API | BytePlus |
| `byteplus-plan` | API | BytePlus plan |
| `xiaomi` | API | Xiaomi |
| `xiaomi-native` | API | Xiaomi native |
| `xiaomi-token-plan` | API | Xiaomi token plan |
| `zai` | API | ZAI |
| `zai-native` | API | ZAI native |
| `opencode` | API | OpenCode |
| `opencode-native` | API | OpenCode native |
| `modelstudio-native` | API | Model Studio native |
| `vercel-ai-gateway` | API | Vercel AI Gateway |
| `custom` | API | Custom provider |
| `deepgram` | API | Deepgram (TTS/STT) |
| `elevenlabs` | API | ElevenLabs (TTS) |
| `brave` | API | Brave (search) |

### Google Antigravity (Hidden Provider)
Special internal provider that routes to Google's low-latency "Antigravity" Gemini endpoints:
- `gemini-3-pro-low` — Low-latency Gemini 3 Pro
- `gemini-3-pro-high` — High-quality Gemini 3 Pro
- `gemini-3-flash` — Gemini 3 Flash

These template IDs are used when provider is `google-antigravity` and resolve to different model endpoints than the standard `google` provider.

---

## 8. Dream System (Memory Consolidation)

The Dream System is OpenClaw's automated memory consolidation engine. It runs as cron jobs during off-hours.

### Dream Phases

| Phase | Purpose | Default Schedule |
|-------|---------|------------------|
| **Light Dreaming** | Lightweight daily summary | `0 3 * * *` (3 AM daily) |
| **Deep Dreaming** | Weighted short-term → MEMORY.md promotion | `0 3 * * *` (3 AM daily) |
| **REM Dreaming** | Pattern extraction & narrative | `0 3 * * *` (3 AM daily) |

**Legacy names:** Light Sleep, REM Sleep (now unified)

### Deep Dreaming Config
| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `false` | Enable deep dreaming |
| `frequency` | `0 3 * * *` | Cron expression |
| `limit` | `10` | Max entries to process |
| `minScore` | (configured) | Min score to promote |
| `minRecallCount` | `3` | Min recall count |
| `minUniqueQueries` | `3` | Min unique query sources |
| `recencyHalfLifeDays` | `14` | Recency half-life |
| `maxAgeDays` | `30` | Max entry age |
| `maxPromotedSnippetTokens` | `160` | Max tokens per promoted snippet |
| `sources` | daily, memory, sessions, logs, recall | Input sources |

### Deep Dreaming Recovery
| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Enable recovery mode |
| `triggerBelowHealth` | (configured) | Health threshold to trigger |
| `lookbackDays` | `30` | Lookback window |
| `maxRecoveredCandidates` | `20` | Max candidates |
| `minRecoveryConfidence` | (configured) | Min confidence for recovery |
| `autoWriteMinConfidence` | (configured) | Min confidence for auto-write |

### Light Dreaming Config
| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Enable light dreaming |
| `lookbackDays` | `2` | Lookback window |
| `limit` | `100` | Max entries |
| `sources` | daily, sessions, recall | Input sources |
| `dedupeSimilarity` | (default) | Deduplication threshold |

### Internal Dream Event Texts
- Unified: `__openclaw_memory_core_short_term_promotion_dream__`
- Legacy Light: `__openclaw_memory_core_light_sleep__`
- Legacy REM: `__openclaw_memory_core_rem_sleep__`

### Dream Cron Tags
- `[managed-by=memory-core.short-term-promotion]`
- Legacy: `[managed-by=memory-core.dreaming.light]`, `[managed-by=memory-core.dreaming.rem]`

---

## 9. Hidden & Undocumented Features

### Fast Mode
A session-level setting that shortcuts model selection and context building:
- `/fast on/off/default/status`
- Configurable per agent: `agents.defaults.models.<model>.params.fastMode`
- Per-agent default: `fastModeDefault`

### Elevated Mode
Allows running commands with elevated permissions:
- `/elevated on/off/ask/full`
- `ask` = prompt for approval
- `full` = full elevated access

### Unsafe Local Wiki Import
- `wiki unsafe-local import` — Import wiki pages from local filesystem paths
- Requires explicit `unsafeLocal.paths` entries
- Pages are tagged with `provenanceMode: "unsafe-local"`

### Hidden CLI Commands
- `hooks relay` — Internal native harness hook relay (hidden from help)
- `gateway call <method>` — Direct RPC to any gateway method (undocumented power tool)

### Memory Unsafe Reindex
- `OPENCLAW_TEST_MEMORY_UNSAFE_REINDEX` — Forces reindex of memory embeddings

### Proxy Debug Mode
Full local proxy for debugging HTTP/HTTPS traffic:
- `OPENCLAW_DEBUG_PROXY_ENABLED`
- `OPENCLAW_DEBUG_PROXY_URL`
- `OPENCLAW_DEBUG_PROXY_CERT_DIR`
- `OPENCLAW_DEBUG_PROXY_BLOB_DIR`
- `OPENCLAW_DEBUG_PROXY_DB_PATH`
- `OPENCLAW_DEBUG_PROXY_SESSION_ID`

### Anthropic Payload Logging
- `OPENCLAW_ANTHROPIC_PAYLOAD_LOG` — Enable Anthropic payload logging
- `OPENCLAW_ANTHROPIC_PAYLOAD_LOG_FILE` — Write payloads to file

### Raw Stream Capture
- `OPENCLAW_RAW_STREAM` — Enable raw LLM stream capture
- `OPENCLAW_RAW_STREAM_PATH` — Output path

### Cache Trace
Full cache hit/miss tracing:
- `OPENCLAW_CACHE_TRACE` — Enable
- `OPENCLAW_CACHE_TRACE_FILE` — Output file
- `OPENCLAW_CACHE_TRACE_MESSAGES` — Trace messages
- `OPENCLAW_CACHE_TRACE_PROMPT` — Trace prompts
- `OPENCLAW_CACHE_TRACE_SYSTEM` — Trace system

### Show Secrets
- `OPENCLAW_SHOW_SECRETS` — Display secrets in status/config output (normally redacted)

### Browser noVNC
- `OPENCLAW_BROWSER_ENABLE_NOVNC` — Expose browser via noVNC
- `OPENCLAW_BROWSER_NOVNC_PORT` — noVNC port
- `OPENCLAW_BROWSER_NOVNC_PASSWORD` — noVNC password
- HTTP endpoint: `/sandbox/novnc`

### Multi-Gateway
- `OPENCLAW_ALLOW_MULTI_GATEWAY` — Allow multiple gateway instances

### Insecure Private WebSocket
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS` — Allow unencrypted private WS

### Config Overwrite Logging
- `OPENCLAW_CONFIG_OVERWRITE_LOG` / `OPENCLAW_CONFIG_WRITE_ANOMALY_LOG` — Track config write anomalies

### Docker/Container Detection
- `OPENCLAW_CONTAINER` / `OPENCLAW_CONTAINER_HINT` — Container environment hints
- `OPENCLAW_DOCKER_SETUP` — Docker setup mode

### Codex Integration
- `OPENCLAW_CODEX_APP_SERVER_*` — Full Codex app server configuration
- `OPENCLAW_CODEX_COMPUTER_USE` — Computer use mode
- `OPENCLAW_CODEX_SUPERVISOR_*` — Supervisor endpoints

### Voice Wake System
Configurable voice activation:
- `voicewake.get` / `voicewake.set` — Get/set config
- `voicewake.routing.get` / `voicewake.routing.set` — Routing rules
- Events: `voicewake.changed`, `voicewake.routing.changed`

### Talk (Realtime Voice) System
Full realtime voice conversation:
- Session management (create/join/close)
- Turn management (startTurn/endTurn/cancelTurn)
- Audio streaming (appendAudio)
- Tool calls during conversation
- Steering mid-conversation

### Google Meet Integration
- `OPENCLAW_GOOGLE_MEET_*` — Full Google Meet OAuth config
- `OPENCLAW_GOOGLE_MEET_DEFAULT_MEETING` — Default meeting
- `end-active-conference` browser command

### VAPID Push
- `OPENCLAW_VAPID_PRIVATE_KEY` / `OPENCLAW_VAPID_PUBLIC_KEY` / `OPENCLAW_VAPID_SUBJECT` — Web Push VAPID keys
- `push.web.subscribe/unsubscribe/test` — Push subscription management

### APNS (Apple Push)
- `OPENCLAW_APNS_KEY_ID` / `OPENCLAW_APNS_PRIVATE_KEY` / `OPENCLAW_APNS_TEAM_ID` — Apple Push config
- `OPENCLAW_APNS_RELAY_*` — APNS relay configuration

---

## 10. Mattermost Slash Commands

For Mattermost integration, OpenClaw auto-registers these slash commands:

| Trigger | Description |
|---------|-------------|
| `/oc_status` | Show session status (model, usage, uptime) |
| `/oc_model` | View or change the current model |
| `/oc_models` | Browse available models |
| `/oc_new` | Start a new conversation session |
| `/oc_help` | Show available commands |
| `/oc_think` | Set thinking/reasoning level |
| `/oc_reasoning` | Toggle reasoning mode |
| `/oc_verbose` | Toggle verbose mode |

---

*Document generated by source mining — not all features are user-facing or stable. Use at your own risk.*