from fastapi import FastAPI
from pydantic import BaseModel, Field
import json, time, uuid, os
from pathlib import Path

try:
    from .reward_loop import EvezBrainRewardLoop
except Exception:
    from reward_loop import EvezBrainRewardLoop

try:
    from tools.evez import fsc_from_cycle, validate_cycle
except Exception:
    fsc_from_cycle = None
    validate_cycle = None

app = FastAPI(title="Agent Orchestrator (Wheel+FSC)")

EVENT_SPINE = os.getenv("EVENT_SPINE", str(Path(__file__).resolve().parents[2] / "spine" / "EVENT_SPINE.jsonl"))
SCHEMA_PATH = os.getenv("FSC_SCHEMA", str(Path(__file__).resolve().parents[2] / "schemas" / "fsc_schema.json"))
REWARD_LEDGER = os.getenv("EVEZ_REWARD_LEDGER", str(Path(__file__).resolve().parents[2] / "artifacts" / "evezbrain_reward_ledger.sqlite3"))
reward_loop = EvezBrainRewardLoop(REWARD_LEDGER)

class FSCCycleIn(BaseModel):
    ring_estimate: str = Field(default="unknown")
    anomaly: str
    context: dict = Field(default_factory=dict)
    controlled_reduction: dict = Field(default_factory=dict)



class RewardActionIn(BaseModel):
    action_type: str = Field(description="Action category: file_write/api_call/test_result/pr_merge/custom")
    success: bool = Field(default=True)
    metadata: dict = Field(default_factory=dict)


class RewardPolicyIn(BaseModel):
    candidates: list[str] = Field(default_factory=lambda: ["file_write", "api_call", "test_result", "pr_merge"])
    lookback: int = Field(default=500, ge=20, le=5000)


@app.get("/healthz")
def healthz():
    return {"ok": True, "event_spine": EVENT_SPINE, "reward_ledger": REWARD_LEDGER}

@app.post("/cycle")
def run_cycle(c: FSCCycleIn):
    cycle = {
        "cycle_id": f"CYCLE-{uuid.uuid4()}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "anomaly": c.anomaly,
        "ring_estimate": c.ring_estimate,
        "controlled_reduction": c.controlled_reduction or {},
        "context": c.context or {},
        "Sigma_f": [],
        "CS": [],
        "PS": [],
        "Omega": "",
        "tests": [],
        "results": [],
        "measures": {},
        "provenance": ["agent_orchestrator"],
    }

    # Try compute FSC (lightweight heuristic) + validate schema
    if fsc_from_cycle:
        cycle = fsc_from_cycle(cycle)
    if validate_cycle:
        valid, errors = validate_cycle(cycle, schema_path=SCHEMA_PATH)
        cycle["validation"] = {"ok": valid, "errors": errors[:20]}
    else:
        cycle["validation"] = {"ok": True, "errors": []}

    reward_event = reward_loop.record_action(
        action_type="api_call",
        success=bool(cycle["validation"].get("ok", False)),
        metadata={
            "status_code": 200 if cycle["validation"].get("ok", False) else 422,
            "latency_ms": 0,
            "anomaly": c.anomaly,
            "expanded_capability": bool(c.context.get("expanded_capability", False)),
        },
    )

    Path(EVENT_SPINE).parent.mkdir(parents=True, exist_ok=True)
    with open(EVENT_SPINE, "a", encoding="utf-8") as f:
        f.write(json.dumps(cycle, ensure_ascii=False) + "\n")
    return {
        "accepted": True,
        "cycle_id": cycle["cycle_id"],
        "pending": True,
        "validation": cycle["validation"],
        "reward_event": reward_event,
    }


@app.post("/reward/action")
def reward_action(payload: RewardActionIn):
    return reward_loop.record_action(payload.action_type, payload.success, payload.metadata)


@app.post("/reward/profile")
def reward_profile(payload: RewardPolicyIn):
    return reward_loop.decision_profile(candidates=payload.candidates, lookback=payload.lookback)


@app.get("/reward/profile")
def reward_profile_default():
    return reward_loop.decision_profile()
