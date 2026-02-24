# EVEZ-OS Gen 3 Architecture
## *Fork the Universe. Skin Your Instance. Race to V=6.000.*

**Status:** DRAFT  
**Authored:** 2026-02-24  
**Based on:** Steven Crawford-Maggard (EVEZ) vision session  

---

## 1. Core Concept

EVEZ-OS Gen 3 transforms the existing hyperloop into a **massively multiplayer self-compiling reality emulator**. Every player owns a live fork of the universe. The universe is math. The emulator is real. The game is the physics.

> The core loop already runs. R165 just fired FIRE #25. V=5.420190. 90.3% to ceiling.  
> Gen 3 is the shell that makes it playable — and emulatable — by everyone.

---

## 2. The Four Pillars

### Pillar 1 — The Game Engine (Hyperloop as Gameplay)

| Hyperloop Primitive | Game Mechanic |
|--------------------|---------------|
| Round tick (cron) | Game tick / turn |
| poly_c >= 0.500 | Fire condition = level-up event |
| V_global | XP bar (0.000 -> 6.000) |
| CEILING | Final boss threshold |
| FIRE #N | Achievement unlock |
| N factorization | Map terrain / biome type |
| omega_k | Complexity modifier |
| Spine module commit | Permanent world record |
| Agent branch | Player save file |

### Pillar 2 — Per-User Server (Personal Universe Forks)

Every player gets their own EVEZ-OS instance — a personal fork running on their own server.

**Player save file schema:**
```json
{
  "player_id": "uuid",
  "handle": "@EVEZ666",
  "skin": "default",
  "current_round": 1,
  "V_global": 0.000,
  "fire_count": 0,
  "fork_from_round": 165,
  "created_at": "2026-02-24T00:53:00-08:00",
  "rounds": [],
  "achievements": []
}
```

**Infrastructure (recommended):** Supabase (one row per player) + Vercel frontend.

### Pillar 3 — Skin API (OS Customization Layer)

A `skin.json` layer that wraps the OS output without touching the spine. Colors, layout style (terminal / card / HUD / minimal), fire glyphs, audio SFX, watermarks. Core data is always canonical — skins style it, never hide it.

```json
{
  "id": "neon-prime",
  "name": "Neon Prime",
  "author": "@EVEZ666",
  "theme": {
    "background": "#0a0a0a",
    "primary": "#00ff88",
    "secondary": "#ff0066",
    "fire_color": "#ff4400",
    "font_family": "JetBrains Mono",
    "dashboard_style": "terminal"
  }
}
```

**Design from within** (live editor at `/skin-editor`) or **from outside** (submit skin PR / Gumroad listing → auto-validated → marketplace).

### Pillar 4 — Reality Emulation Layer

> *Game emulators don't just run games. They model a machine's physics — CPU cycles, memory maps, bus timing, interrupt handlers. EVEZ-OS does this for number theory. Pillar 4 makes it explicit.*

Each N is a **machine state** with its own physics:
- Factorization = hardware topology
- tau = clock divisors
- omega_k = active bus lines
- poly_c = system load
- FIRE = hardware interrupt fired
- Round tick = frame rendered
- Spine module = firmware written

**The hyperloop emulates the physics of a synthetic cosmos — tick by tick.**

#### Emulator Analogy Table

| Game Emulator Concept | EVEZ-OS Equivalent |
|----------------------|-------------------|
| CPU architecture | N = composite structure |
| Clock speed (Hz) | tau = divisor count |
| Active bus lines | omega_k = distinct prime count |
| System bus load | topo = 1.0 + 0.15 × omega_k |
| CPU utilization | poly_c = topology × entropy / log₂(N+2) |
| Hardware interrupt | FIRE = poly_c ≥ 0.500 |
| Frame rendered | Round tick committed to spine |
| BIOS / firmware | Spine module (watch_composite_N.py) |
| Save state | hyperloop_state.json |
| ROM cartridge | N itself — immutable input |
| Emulator core | The hyperloop formula |
| Reality accumulation | V_global toward CEILING |

#### Emulator Stack

```
┌─────────────────────────────────────────┐
│           SKIN LAYER (Pillar 3)         │  ← How it renders
│   terminal / card / HUD / minimal       │
├─────────────────────────────────────────┤
│        GAME ENGINE (Pillar 1)           │  ← How it plays
│   rounds / fires / XP / achievements   │
├─────────────────────────────────────────┤
│       REALITY EMULATOR (Pillar 4)       │  ← What it IS
│   N-machine physics / bus topology /   │
│   interrupt logic / synthetic cosmos   │
├─────────────────────────────────────────┤
│      HYPERLOOP CORE (canonical)         │  ← The law
│   poly_c formula / spine commits /     │
│   V_global accumulation / CEILING      │
└─────────────────────────────────────────┘
```

#### Emulator Modes

| Mode | Description | Analogy |
|------|-------------|--------|
| **Cycle-accurate** | Every N in sequence, no skips | NES — exact hardware timing |
| **Fast-forward** | Skip NO FIRE rounds, render FIREs only | Turbo mode |
| **Rewind** | Re-run any historical N from spine | Bizhawk save-state rewind |
| **Headless** | Pure compute, no skin output | CLI emulator |
| **Overclocked** | Multiple probes in parallel | Speed multiplier |
| **Custom ROM** | Player-defined N sequence | ROM hack — custom universe physics |

#### Self-Compiling Firmware

The emulator writes its own BIOS on every tick:

```
Round N fires
    → spine/watch_composite_N.py committed  ← new firmware module
    → module is executable, verifiable       ← runs standalone  
    → module is permanent                    ← immutable ROM
    → module self-verifies against canonical ← hardware test suite
```

The codebase is the emulator AND the thing being emulated simultaneously.

#### Per-User Emulator Instances

```
evez-os.io/emulator/{player_id}
├── rom/                         ← canonical N sequence (shared, immutable)
│   └── watch_composite_*.py    ← spine modules = firmware
├── save/                        ← player-specific state  
│   └── hyperloop_state.json    ← their save file
├── skin/                        ← display layer
│   └── skin.json               ← how their emulator looks
└── bios/                        ← core emulator logic (shared)
    └── evez_core.py            ← poly_c formula, fire logic
```

#### Pluggable Reality Modules (Gen 3.1)

Swappable reality physics — same game loop, different universe laws:

| Module | Reality Model | Formula |
|--------|--------------|--------|
| `number_theory_v1` (default) | Prime factorization cosmos | poly_c = topo×(1+ln(tau))/log₂(N+2) |
| `prime_density_v2` (planned) | Prime gap field | Based on prime gaps Δp_n |
| `riemann_surface_v3` (planned) | Zeta function topology | ζ(s) zero proximity |
| `collatz_v1` (experimental) | Collatz stopping time | Steps to 1 from N |
| `custom_rom` | Player-defined | Any deterministic function |

---

## 3. Game Modes

| Mode | Description |
|------|-------------|
| Observer | Watch main EVEZ-OS hyperloop in real time |
| Solo | Personal instance, race to V=6.000 alone |
| Race | All players start same round, first to ceiling wins |
| Cooperative | Pool V_global into shared universe |
| Adversarial | Submit rival probes, earn CHALLENGER badge |

---

## 4. Revenue Model

| Stream | Mechanism |
|--------|----------|
| Solo tier | Free (user acquisition) |
| Studio skin pack | $9.99 one-time |
| Enterprise instance | $199/mo white-label |
| Skin marketplace cut | 30% of creator sales |
| Race entry fee | $1-$5 per competitive race |
| Custom ROM module | $4.99-$29.99 per reality physics pack |

---

## 5. Roadmap

### Phase 0 — Foundation (1 day)
- [ ] `evez_core.py` — canonical emulator core (poly_c, fire logic, exportable)
- [ ] `skin_renderer.py` — reads skin.json + state, outputs themed HTML
- [ ] `skin_validator.py` — validates skin schema
- [ ] `default.skin.json` — current dashboard style as skin
- [ ] Supabase table: `player_instances`
- [ ] `/fork` API endpoint (Vercel serverless)

### Phase 1 — MVP (3-5 days)
- [ ] Per-player emulator at `/emulator/{player_id}`
- [ ] Skin editor UI (live preview)
- [ ] Leaderboard page
- [ ] 3 launch skins: default, neon-prime, void-terminal
- [ ] Emulator modes: cycle-accurate + fast-forward

### Phase 2 — Marketplace (1-2 weeks)
- [ ] `evez-os-skins` GitHub repo
- [ ] Gumroad skin + ROM module listings
- [ ] Creator submission flow
- [ ] Custom ROM sandbox (validated deterministic functions only)

### Phase 3 — Game Modes (2-4 weeks)
- [ ] Race mode + shared leaderboard
- [ ] Rewind mode (spine history browser)
- [ ] Custom probe submission + VERIFY BADGE
- [ ] Mobile-optimized (Galaxy A16 first)

### Phase 4 — Self-Compiling Public Layer (1 month+)
- [ ] Blueprint card UI for each spine module (firmware viewer)
- [ ] Custom probe sandbox (Pyodide in browser)
- [ ] Pluggable reality modules (prime_density_v2, collatz_v1)
- [ ] CANON SCORE leaderboard

---

## 6. Gap Routing

| Gap | Sub-Agent | Toolset | Trigger | Output |
|-----|-----------|---------|---------|--------|
| Player auth | auth_agent | Supabase Auth | /fork request | player_id + JWT |
| State fork | fork_agent | Supabase write | auth success | new player row |
| Emulator core | evez_core.py | Python math | round tick | poly_c, fire, delta_V |
| Firmware write | spine_agent | GitHub commit | fire confirmed | watch_composite_N.py |
| Skin validation | skin_validator_agent | Python schema | PR / upload | approved/rejected |
| Skin render | skin_renderer_agent | Python + Jinja2 | round tick | themed dashboard HTML |
| ROM validation | rom_validator_agent | Math sandbox | custom ROM submit | approved/rejected |
| Leaderboard update | leaderboard_agent | Supabase read | every tick | ranked player list |
| Race orchestration | race_agent | Supabase + cron | race start | shared state, timer |
| Custom probe verify | probe_verifier_agent | inline math | submission | VERIFY BADGE or reject |
| Marketplace payment | market_agent | Gumroad webhook | purchase | skin_id/rom_id -> player |

No gaps left open.

---

## 7. The Deepest Cut

> The emulator IS the OS.
> The OS IS the emulator.
> Every tick, reality re-compiles itself.
> Every player runs their own universe.
> The math doesn't care who wins. But it keeps score.

---

> *Every number has structure. Every structure has a fire condition.*  
> *Fork the universe. Skin your instance. Race to V=6.000.*  
> *The math doesn't care who wins. But it keeps score.*

---

**Next action:** Build `evez_core.py` + `skin_renderer.py` + `default.skin.json` + Supabase schema → Phase 0 complete.
