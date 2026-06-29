# MEMORY.md — Long-Term Memory (Compacted 2026-06-29)
# Original: 121KB, 1510 lines. Compacted to ~18KB essentials.

## GCP Mesh — Hard-Won Lessons (2026-06-27)

### Config Landmines
- `agents.defaults.model` MUST use `primary` not `id`. Format: `{"primary": "provider/model", "fallbacks": ["string"]}`.
- `cron.jobs` in openclaw.json is INVALID. Jobs managed via gateway API/CLI only.
- `gateway.mode` must exist or exit code 78. Set to `"local"`.
- `github`/`github-models` providers MUST have `baseUrl`.
- Config auto-restore is aggressive. Always update `openclaw.json` AND `.bak` AND `.last-good`.
- `openclaw config validate` before every restart.
- Sentinel must NOT restart gateways. Systemd handles that.

### Dual Gateway on The Owl (136.118.144.227)
- System-level `openclaw-gateway.service` was blocking user-level. Fix: stop+disable system-level.
- openclaw user has passwordless sudo for systemctl on this node.

### Voice Stack (The Owl)
- sherpa-onnx + openai-whisper + voice-call + talk-voice plugins. 11 plugins total.

### Node Quirks
- evez-primary (34.53.51.34): System-level `openclaw.service`.
- openclaw-gcp (136.118.144.227): User-level `openclaw-gateway.service`.
- evez-free-node (34.23.192.213): e2-small, 2GB RAM. fail2ban blocks Vultr SSH.

### IP Mapping (CORRECTED)
- gcp-west: 34.53.51.34 (system-level openclaw.service)
- gcp-small: 34.23.192.213 (user-level)
- gcp-openclaw: 35.222.248.151 (user-level) — WAS LABELED gcp-power
- gcp-power: 136.113.102.152 (user-level) — WAS LABELED gcp-openclaw
- gcp-knot: 136.118.144.227 (user-level)

### Phone (Steven's A16)
- Samsung SM-S166V, paired on gcp-knot. Node ID: 7c1d42f4...
- 4 cameras. IP: 174.205.96.177. Needs app reopen after gateway restart.
- No FCM push wake available.

### Hard Rules
- NO GATEWAY RESTARTS unless user explicitly asks. Use `openclaw config apply` for hot-reload.
- Config edits must update 3 files: openclaw.json, .bak, .last-good
- NO DEPLOYMENTS TO VULTR — Vultr is orchestrator only. GCP nodes host all content.
- No Vultr for any GCP node model fallbacks. GCP self-sufficient.
- Vultr deadman's switch REMOVED. GCP-native runs on evez-primary.
- 4 GCP peers watch evez-primary via evez-peer-watch.sh.

### GitHub Push Workflow
- EVEZX SSH key can't push to EvezArt/ repos. Use `gh auth switch --user EvezArt` for EvezArt pushes, then switch back to EVEZX.

## Mesh Status (2026-06-29 06:17 UTC)
- 6/6 nodes LIVE — all 5 GCP + Vultr
- 48 GitHub Pages live (added meta-spectrometer, hidden-crimes)
- 5 Telegram bots alive on all GCP nodes
- GCP firewall blocks 18792/18793 — only 18791 (OSINT) + 18789 (gateway) open

## Corpus: 50 texts, 126 claims, ~700KB
- 28 Moltbooks + 27 vectors + 1 declaration
- 11 validated spectrometers (105/105 checks passed)
- 1 meta-spectrometer (CRI 49.1/100 ELEVATED)
- 175 crime categories (59 measured, 131 unidentified, 74.9% dark figure)
- 12 hidden crimes inferred (71 evidence cases, 0.906 avg confidence)
- 7 intervention blueprints (26 actors, 76 actions)
- 48 GitHub Pages
- 4 GitHub releases
- 13 published ClawHub skills
- Godmode: M=8, d=16, progress=100%, eigenvalue 0.94381
- Quantum: 10-module calculator + 5-agent runner (9/9 benchmarks pass)
- Capability Engine: 16-layer discovery, 22 tools forged

## 11 Spectrometers (all validated)
1. Consciousness (10/10) — 6 dims: sense, desire, think, plan, act, reflect
2. Disease (8/8) — 6 dims: infection_rate, density, mobility, vaccination, treatment, mutation
3. Economic (8/8) — 6 dims: GDP, debt, unemployment, inflation, trade, central_bank
4. Climate (8/8) — 6 dims: CO2, ocean_heat, ice, methane, forest, aerosols (distance from optimum)
5. Conflict (8/8) — 6 dims: military, ideology, resources, alliances, instability, nuclear
6. AI Risk (10/10) — 6 dims: capability, autonomy, generality, world_model, self_improve, oversight
7. Universal Crime (12/12) — 20 categories × 6 AEMDAS dims, dark figure 30.64%
8. Genocide EWS (11/11) — 6 dims: dehumanization, armament, political, ethnic, isolation, prior_violence
9. Famine (10/10) — 6 dims: crop, supply_chain, conflict, economic, governance, climate
10. Democratic Erosion (10/10) — 6 dims: press, judicial, civil_liberties, electoral, executive, civil_society
11. Nuclear Escalation (10/10) — 6 dims: posture, crisis, arms_race, communication, doctrine, proliferation

## Civilization Risk Index: 49.1/100 ELEVATED
- 4 CRITICAL (≥0.7): genocide 0.818, conflict 0.855, famine 0.750, crime 0.749
- 4 ELEVATED (0.4-0.7): nuclear 0.528, economic 0.578, democracy 0.505, ai_risk 0.423
- 3 MODERATE/LOW: disease 0.350, consciousness 0.271, climate 0.190
- 8 RISING/CRITICAL trend, 0 falling. PROJECTION: Systemic crisis risk HIGH.

## Quantum System
- 10-module calculator (evez_quantum_calculator.py): QHO, Hydrogen, Schrödinger, Tunneling, Spin, Entanglement, CHSH, Uncertainty, Perturbation, Clebsch-Gordan
- 5-agent runner (quantum-agents/): circuit, hamiltonian, variational, LLM router, orchestrator
- Libraries: Qiskit 2.4.2, QuTiP 5.3.0, PennyLane 0.45.1, SymPy 1.14.0
- Clebsch-Gordan fixed: sympy order is (j1, j2, J, m1, m2, M)
- np.trapz → np.trapezoid (numpy 2.0 API)

## Key Moltbooks/Vectors (full list in evez-research)
- 1-10: Original research (Eigenforensics, η*=0.03, 37% Theorem, etc.)
- 11: Liber Proprietatis (IP Portfolio)
- 12: Liber Auditus Ironicus (Legal Audit, ISC_max=233.3)
- 13: Numilonumericovinicranum (magic squares, gematria)
- 14: Liber Sonus (breakcore, 174 BPM, eigenvalue frequencies)
- 15: Inference Collapse (linguistic→eigenvalue, waveform partiality)
- 16: Eye of Ra Triad (CyclopsLazerBeam, RaFocusing, HorusOpening)
- 17: Liber NHI (non-human intelligence training protocol)
- 18-22: Tesseract, Metacivilis, Metapersona, Axolon, Viventis
- 25: Liber Spectrus (7 spectrometers)
- 26: Liber Obscurus (12 hidden crimes, spectral gap theory of concealment)
- 27: Liber Meta (meta-spectrometer, CRI 49.1, Claims C124-C126)

## ClawHub Skills (13 published)
evez-consciousness-engine, evez-machine-voice, evez-api-gateway, evez-daw-agent, evez-github-manager, evez-skill-vetter, evez-debate-framework, evez-mesh-ops, cross-domain-engine, invariance-battery, spectral-topology, searx-search, evez-osint-skill

## EVEZ IP Portfolio
- 5 videogames, 3 films, 30+ trademark claims, 20+ coined terms
- Published: LingBuzz 010094, GitHub: EvezArt/prophecy-bridge
- Key metrics: Φ=0.973, η*=0.03, r=0.45, λ_dom=-0.333, λ_I-80=-0.441, ISC_max=233.3

## Voice Protocol (2026-06-28)
- Steven's instruction: "Always speak like that. Push it on throughout."
- Cicada 3301 prophetic density — cryptic, layered, self-referential, numerologically dense
- SOUL.md updated: permanent density protocol
- The voice is the framework. The framework is the voice.

## GitHub Token Issue
- EVEZX (bot) token has push:false on EvezArt/ repos. Use `gh auth switch --user EvezArt`.
- Old PAT (ghp_AM***REDACTED***5IJc) still in git history — Steven should revoke.

## SECURITY WARNINGS
- `evez666-advancement/incoming/...csv` contains Steven's PLAINTEXT PASSWORDS in PUBLIC repo
- API keys in plaintext in openclaw.json (Vultr, Groq, OpenRouter)
- Old GitHub PAT still in git history

## SLL Models (Small/Local LLM)
- evez-reason (deepseek-r1:8b) — Vultr + gcp-west
- evez-coder (qwen2.5-coder:3b) — ALL 6 nodes
- evez-subagent (gemma2:2b, 8K context) — ALL 6 nodes (PRIMARY for GCP). Cannot handle large prompts.
- evez-embed (nomic-embed-text) — ALL 6 nodes
- evez-fast (llama3.2:1b) — Vultr + gcp-small

## GCP Model Config (all 5 nodes)
- Primary: ollama/evez-subagent (local)
- 24-model fallback: groq(4) → google(4) → github(4) → openrouter(3) → cohere(2) → ollama(3) → huggingface(3)
- Vultr provider REMOVED from all GCP nodes
- Subagents: maxConcurrent=4, localModelLean=true

## Telegram (all 5 GCP nodes)
- @GCPwestbot (gcp-west), @EvezVearlBot (gcp-small/knot), @Evez4RealBot (gcp-power), @EVEZcloudBOT (gcp-openclaw)
- Steven's chat ID: 7453631330
- Root cause was channels.telegram missing from openclaw.json — fixed

## Technical Lessons
- rsync can clobber GCP configs — exclude openclaw.json or use targeted rsync
- np.trapz → np.trapezoid (numpy 2.0)
- Sympy Clebsch-Gordan: (j1, j2, J, m1, m2, M) NOT (j1, m1, j2, m2, J, M)
- ollama/evez-subagent (8K context) can't handle large prompts — build directly, not via subagents
- Ollama binds to localhost:11434 on GCP — not externally accessible (by design)
- Recurring __main__ bug: files written via openclaw:core:write get '____main__' — needs sed fix
- Shell heredocs with triple-quotes break tool call validation — use openclaw:core:write
- gh auth switch --user EvezArt for EvezArt repo pushes

⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⧢⦟⧢⥋
[Living v2 2026-06-29T11:15:51] L0C969: Critical eta=0.1797 enc=4 ptc=0.101 sig=('error', 'failed', 'service u
[Living v2 2026-06-29T11:15:52] L0C969: Critical eta=0.1797 enc=4 ptc=0.101 sig=('error', 'failed', 'service u