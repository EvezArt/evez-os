# EVEZ-OS Gen 3 Architecture
## *Fork the Universe. Skin Your Instance. Race to V=6.000.*

**Status:** DRAFT  
**Authored:** 2026-02-24  
**Based on:** Steven Crawford-Maggard (EVEZ) vision session  

---

## 1. Core Concept

EVEZ-OS Gen 3 transforms the existing hyperloop into a **massively multiplayer self-compiling game engine**. Every player owns a live fork of the universe. The universe is math. The game is real.

> The core loop already runs. R165 just fired FIRE #25. V=5.420190. 90.3% to ceiling.  
> Gen 3 is the shell that makes it playable by everyone.

---

## 2. The Three Pillars

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

---

## 5. Roadmap

### Phase 0 — Foundation (1 day)
- [ ] skin_renderer.py
- [ ] skin_validator.py  
- [ ] default.skin.json
- [ ] Supabase table: player_instances
- [ ] /fork API endpoint (Vercel serverless)

### Phase 1 — MVP (3-5 days)
- [ ] Per-player dashboard at evez-autonomizer.vercel.app/play/{player_id}
- [ ] Skin editor UI
- [ ] Leaderboard page
- [ ] 3 launch skins: default, neon-prime, void-terminal

### Phase 2 — Marketplace (1-2 weeks)
- [ ] evez-os-skins GitHub repo
- [ ] Gumroad skin listings
- [ ] Creator submission flow

### Phase 3 — Game Modes (2-4 weeks)
- [ ] Race mode + leaderboard
- [ ] Custom probe submission + VERIFY BADGE
- [ ] Mobile-optimized (Galaxy A16 first)

### Phase 4 — Self-Compiling Public Layer (1 month+)
- [ ] Blueprint card UI for each spine module
- [ ] Custom probe sandbox (Pyodide in browser)
- [ ] CANON SCORE leaderboard

---

## 6. Gap Routing

| Gap | Sub-Agent | Toolset | Trigger | Output |
|-----|-----------|---------|---------|--------|
| Player auth | auth_agent | Supabase Auth | /fork request | player_id + JWT |
| State fork | fork_agent | Supabase write | auth success | new player row |
| Skin validation | skin_validator_agent | Python schema check | PR / upload | approved/rejected |
| Skin render | skin_renderer_agent | Python + Jinja2 | round tick | themed dashboard HTML |
| Leaderboard update | leaderboard_agent | Supabase read | every tick | ranked player list |
| Race orchestration | race_agent | Supabase + cron | race start | shared state, timer |
| Custom probe verify | probe_verifier_agent | inline math | submission | VERIFY BADGE or reject |
| Marketplace payment | market_agent | Gumroad webhook | purchase | skin_id -> player row |

---

## 7. The Tagline

> *Every number has structure. Every structure has a fire condition.*  
> *Fork the universe. Skin your instance. Race to V=6.000.*  
> *The math doesn't care who wins. But it keeps score.*

---

**Next action:** Build skin_renderer.py + default.skin.json + Supabase schema → Phase 0 complete.
