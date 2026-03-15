import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";
import crypto from "crypto";

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));

const EVENT_SPINE = process.env.EVENT_SPINE || path.resolve("../..", "spine", "EVENT_SPINE.jsonl");

// --- helpers ---

/** Returns the current UTC timestamp as an ISO 8601 string. */
function nowIso() { return new Date().toISOString(); }

/**
 * Generate a unique event ID with an optional prefix.
 * @param {string} [prefix="EV"] - Short string prepended to the UUID.
 * @returns {string} e.g. "INPUT-550e8400-e29b-41d4..."
 */
function id(prefix="EV") { return `${prefix}-${crypto.randomUUID()}`; }

/**
 * Append a single event object as a JSON line to the EVENT_SPINE file.
 *
 * Creates the parent directory if it does not exist.  The spine is an
 * append-only JSONL file; each line is one self-contained event object.
 *
 * @param {Object} ev - Event object to persist.
 * @returns {Object} The same event object (pass-through for chaining).
 */
function appendEvent(ev) {
  fs.mkdirSync(path.dirname(EVENT_SPINE), { recursive: true });
  fs.appendFileSync(EVENT_SPINE, JSON.stringify(ev) + "\n", "utf-8");
  return ev;
}

// Pending vs Final guardrail: any non-authoritative state MUST be labeled.
app.get("/healthz", (_req, res) => res.json({ ok: true, ts: nowIso() }));

/**
 * POST /input
 * Submit a player action.  The event is written to the spine with
 * status="pending" and must be finalized by the authoritative game-server
 * via POST /finalize/:eventId before it is treated as canonical.
 *
 * Body: { playerId: string, input: any }
 * Response: { ok: true, pending: true, event: Object }
 */
app.post("/input", (req, res) => {
  const { playerId, input } = req.body || {};
  if (!playerId || !input) return res.status(400).json({ ok: false, error: "playerId + input required" });

  const ev = appendEvent({
    event_id: id("INPUT"),
    type: "player_input",
    ts: nowIso(),
    playerId,
    input,
    status: "pending",
    provenance: ["apigw"],
  });

  res.json({ ok: true, pending: true, event: ev });
});

/**
 * POST /finalize/:eventId
 * Finalize a previously submitted input event.  Appends a "finalization"
 * event to the spine that references the original event by ID and records
 * the authoritative game state.  Normally called by the game-server or a
 * reconciler, not directly by clients.
 *
 * Params: eventId — the event_id string from the original /input response.
 * Body:   { authoritativeState?: Object, note?: string }
 * Response: { ok: true, final: true, event: Object }
 */
app.post("/finalize/:eventId", (req, res) => {
  const { eventId } = req.params;
  const { authoritativeState, note } = req.body || {};
  const ev = appendEvent({
    event_id: id("FINAL"),
    type: "finalization",
    ts: nowIso(),
    ref_event_id: eventId,
    status: "final",
    authoritativeState: authoritativeState ?? null,
    note: note ?? null,
    provenance: ["apigw_finalize"],
  });
  res.json({ ok: true, final: true, event: ev });
});

/**
 * GET /state/:playerId
 * Return the current read-model projection for a player.
 *
 * Scans the EVENT_SPINE for all events belonging to the given player and
 * finds the most recent "finalization" event.  If found, its
 * authoritativeState is returned; otherwise a default state is used.
 * The "pending" flag indicates whether the state has been authoritatively
 * confirmed yet.
 *
 * Params:   playerId — string identifier for the player.
 * Response: { ok: true, playerId, state: Object, provenance: string[], pending: boolean }
 */
app.get("/state/:playerId", (req, res) => {
  const playerId = req.params.playerId;
  let lines = [];
  try { lines = fs.readFileSync(EVENT_SPINE, "utf-8").trim().split("\n").filter(Boolean); } catch {}
  const events = lines.map((l) => JSON.parse(l)).filter((e) => e.playerId === playerId || e.authoritativeState?.playerId === playerId);
  const lastFinal = [...events].reverse().find((e) => e.type === "finalization" && e.authoritativeState);
  const view = lastFinal?.authoritativeState ?? { playerId, x: 0, y: 0, hp: 100 };

  res.json({
    ok: true,
    playerId,
    state: view,
    provenance: lastFinal ? ["projection_from_event_spine", lastFinal.event_id] : ["projection_default"],
    pending: !lastFinal,
  });
});

/**
 * GET /events/tail/:n
 * Return the last N events from the EVENT_SPINE for debugging purposes.
 *
 * Params:   n — number of events to return (clamped to [1, 2000]).
 * Response: { ok: true, n: number, events: Object[] }
 */
app.get("/events/tail/:n", (req, res) => {
  const n = Math.max(1, Math.min(2000, parseInt(req.params.n, 10) || 50));
  let lines = [];
  try { lines = fs.readFileSync(EVENT_SPINE, "utf-8").trim().split("\n").filter(Boolean); } catch {}
  const tail = lines.slice(-n).map((l) => JSON.parse(l));
  res.json({ ok: true, n, events: tail });
});

app.listen(8000, () => console.log("API GW on :8000 (pending/final + event spine)"));
