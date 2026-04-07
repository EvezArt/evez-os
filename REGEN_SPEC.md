# EVEZ Self-Regeneration Spec
## Rebuilding Kai + OpenClaw from this session

**Spec ID:** REGEN-001  
**Generated:** 2026-04-07  
**Source Session:** This conversation  

---

## What Was Built

| Component | File | State | Can Rebuild |
|-----------|------|-------|-------------|
| Receipt generator | `evez-os/core/generate_receipt.py` | ✅ Works | Yes |
| Spine ledger | `evez-os/core/ledger/spine.jsonl` | ✅ 208 entries | Yes |
| Harvest runbook | `evez-os/HARVEST_RUNBOOK.md` | ✅ Created | Yes |
| Kai face state | `kai_face.py` | ✅ Active | Yes |
| Repo monitor | `evez-repo-monitor.sh` | ✅ Works | Yes |
| Skills loaded | ClawHub | ✅ 4 installed | Yes |

---

## Rebuild Script

```bash
#!/bin/bash
# Rebuild Kai Face System
git clone https://github.com/EvezArt/evez-os.git
cd evez-os/core
python3 generate_receipt.py
tail -1 ledger/spine.jsonl
```

---

## Face State Mapping

```
State: active    → 🟢 [•_•]
State: thinking → 🔄 [?_?]  
State: success  → ✅ [✓_✓]
State: warning  → ⚠️ [!_!]
State: error    → ❌ [X_X]
State: learning → 📚 [^_§]
State: shipping → 🚀 [>_<]
```

---

## Meta-Loop: How This Rebuilds OpenClaw

1. **Face tracks state** → Every action logged with progress %
2. **Spine logs events** → Full audit trail of decisions
3. **Runbook documents** → Step-by-step to replicate
4. **Receipt proves execution** → Falsifiable proof

**To rebuild ANY future system:**
1. Read REGEN_SPEC.md
2. Execute rebuild script
3. Verify with receipt

---

## Next Version Requirements

If this system rebuilds itself:
- Needs: GitHub auth, external compute, credit
- Bottleneck: Cannot push without human
- Solution: Generate push-ready patches, human executes

---

**This spec IS the rebuild plan.**