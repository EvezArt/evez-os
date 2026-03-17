from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json, time, uuid, os
from pathlib import Path

try:
    from tools.evez import fsc_from_cycle, validate_cycle
except Exception:
    fsc_from_cycle = None
    validate_cycle = None

app = FastAPI(title="Agent Orchestrator (Wheel+FSC)")

EVENT_SPINE = os.getenv("EVENT_SPINE", str(Path(__file__).resolve().parents[2] / "spine" / "EVENT_SPINE.jsonl"))
SCHEMA_PATH = os.getenv("FSC_SCHEMA", str(Path(__file__).resolve().parents[2] / "schemas" / "fsc_schema.json"))

class FSCCycleIn(BaseModel):
    ring_estimate: str = Field(default="unknown")
    anomaly: str
    context: dict = Field(default_factory=dict)
    controlled_reduction: dict = Field(default_factory=dict)



DREAM_JOURNAL = os.getenv("DREAM_JOURNAL", str(Path(__file__).resolve().parents[2] / "agents" / "dream" / "dream_journal.jsonl"))


def _dream_stream():
    path = Path(DREAM_JOURNAL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    with path.open("r", encoding="utf-8") as fp:
        fp.seek(0, os.SEEK_END)
        while True:
            line = fp.readline()
            if not line:
                time.sleep(1)
                yield ": keepalive\n\n"
                continue
            yield f"data: {line.strip()}\n\n"


@app.get("/api/dream/stream")
def dream_stream():
    return StreamingResponse(_dream_stream(), media_type="text/event-stream")
@app.get("/healthz")
def healthz():
    return {"ok": True, "event_spine": EVENT_SPINE}

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

    Path(EVENT_SPINE).parent.mkdir(parents=True, exist_ok=True)
    with open(EVENT_SPINE, "a", encoding="utf-8") as f:
        f.write(json.dumps(cycle, ensure_ascii=False) + "\n")
    return {"accepted": True, "cycle_id": cycle["cycle_id"], "pending": True, "validation": cycle["validation"]}
