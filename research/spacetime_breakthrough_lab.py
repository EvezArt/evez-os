#!/usr/bin/env python3
"""EVEZ Spacetime Breakthrough Lab: reproducible hypotheses and witness ledger.

Standard-library-only and offline-first. The hash chain detects edits to the
record sequence; it does not prove identity, source accuracy, or scientific truth.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "evez.spacetime-lab.event.v1"
DEFAULT_LEDGER = Path.home() / ".local/state/evez/spacetime-lab.jsonl"
CLAIM_CLASSES = {"established", "derived", "speculative"}
MODALITIES = {"simulation", "lab_instrument", "ruview_csi", "published_literature", "synthetic_test"}
EVENT_TYPES = {"SPACETIME_LAB.EXPERIMENT_REGISTERED", "SPACETIME_LAB.OBSERVATION_RECORDED", "SPACETIME_LAB.ANALYSIS_NOTE", "SPACETIME_LAB.REVIEW_RECORDED"}
ZERO_HASH = "0" * 64


class LabError(ValueError):
    """Invalid experiment, observation, or ledger state."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    # Deterministic Python JSON encoding, not a claim of full RFC 8785/JCS conformance.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_text(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LabError(f"{key} must be a non-empty string")
    return value.strip()


def validate_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(experiment, dict) or experiment.get("schema_version") != "evez.spacetime-lab.experiment.v1":
        raise LabError("unsupported or missing experiment schema_version")
    for key in ("experiment_id", "title", "hypothesis", "model_name", "created_at"):
        require_text(experiment, key)
    claim_classification = experiment.get("claim_classification")
    if not isinstance(claim_classification, str) or claim_classification not in CLAIM_CLASSES:
        raise LabError(f"claim_classification must be one of {sorted(CLAIM_CLASSES)}")
    for key in ("assumptions", "source_urls", "predictions", "controls", "safety_limits"):
        values = experiment.get(key)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise LabError(f"{key} must be a list of non-empty strings")
    for source in experiment["source_urls"]:
        if not source.startswith(("https://", "http://", "doi:")):
            raise LabError("source_urls entries must start with http://, https://, or doi:")
    if claim_classification == "speculative" and not experiment["safety_limits"]:
        raise LabError("speculative claims require explicit interpretation limits")
    return experiment


def new_experiment(*, title: str, hypothesis: str, model_name: str,
                   claim_classification: str = "speculative", assumptions: list[str] | None = None,
                   source_urls: list[str] | None = None, predictions: list[str] | None = None,
                   controls: list[str] | None = None, safety_limits: list[str] | None = None,
                   experiment_id: str | None = None) -> dict[str, Any]:
    record = {
        "schema_version": "evez.spacetime-lab.experiment.v1",
        "experiment_id": experiment_id or f"sbl-{uuid.uuid4().hex[:12]}",
        "title": title.strip(), "hypothesis": hypothesis.strip(), "model_name": model_name.strip(),
        "claim_classification": claim_classification, "epistemic_status": "PROPOSED",
        "assumptions": assumptions or [], "source_urls": source_urls or [],
        "predictions": predictions or [], "controls": controls or [],
        "safety_limits": safety_limits or [
            "A mathematical solution is not evidence of physical feasibility or an engineering prototype.",
            "Ordinary RF/CSI observations do not establish spacetime curvature or superluminal propulsion."
        ],
        "created_at": utc_now(),
    }
    return validate_experiment(record)


def validate_observation(observation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(observation, dict):
        raise LabError("observation must be a JSON object")
    for key in ("source", "modality", "quantity", "unit", "calibration_id", "observed_at"):
        require_text(observation, key)
    if not isinstance(observation["modality"], str) or observation["modality"] not in MODALITIES:
        raise LabError(f"modality must be one of {sorted(MODALITIES)}")
    value = observation.get("value")
    if value is None or isinstance(value, (dict, list)):
        raise LabError("value must be a non-null scalar JSON value")
    if isinstance(value, float) and not math.isfinite(value):
        raise LabError("value must be finite")
    uncertainty = observation.get("uncertainty")
    if uncertainty is not None and (not isinstance(uncertainty, (int, float)) or isinstance(uncertainty, bool) or not math.isfinite(float(uncertainty)) or uncertainty < 0):
        raise LabError("uncertainty must be a finite, non-negative number")
    digest = observation.get("evidence_sha256")
    if digest is not None and (not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
        raise LabError("evidence_sha256 must be a lowercase SHA-256 digest")
    return observation


def _load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                raise LabError(f"blank line in ledger at line {line_no}")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LabError(f"invalid JSON at ledger line {line_no}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise LabError(f"ledger line {line_no} is not an object")
            records.append(record)
    return records


def verify_ledger(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        records = _load_ledger(path)
        previous = ZERO_HASH
        for sequence, record in enumerate(records, 1):
            if record.get("schema_version") != SCHEMA_VERSION or record.get("sequence") != sequence:
                raise LabError(f"schema/sequence mismatch at event {sequence}")
            if record.get("previous_hash") != previous:
                raise LabError(f"previous_hash mismatch at event {sequence}")
            event = record.get("event")
            if not isinstance(event, dict) or event.get("event_type") not in EVENT_TYPES:
                raise LabError(f"malformed or unknown event at sequence {sequence}")
            material = {"sequence": sequence, "previous_hash": previous, "event": event}
            expected = sha256_hex(canonical_json(material).encode("utf-8"))
            if record.get("event_hash") != expected:
                raise LabError(f"event hash mismatch at sequence {sequence}")
            previous = expected
        return {"ok": True, "path": str(path), "events": len(records), "head_hash": previous}
    except (OSError, LabError) as exc:
        return {"ok": False, "path": str(path), "error": str(exc)}


def append_event(path: str | Path, event: dict[str, Any]) -> dict[str, Any]:
    path = Path(path)
    if not isinstance(event, dict) or event.get("event_type") not in EVENT_TYPES:
        raise LabError("event_type is not supported by this lab ledger")
    event = dict(event)
    event.setdefault("occurred_at", utc_now())
    event.setdefault("event_id", uuid.uuid4().hex)
    verified = verify_ledger(path)
    if not verified["ok"] and path.exists() and path.stat().st_size:
        raise LabError(f"refusing to append to invalid ledger: {verified['error']}")
    records = _load_ledger(path)
    registered = any(r["event"].get("event_type") == "SPACETIME_LAB.EXPERIMENT_REGISTERED" for r in records)
    kind = event["event_type"]
    if kind == "SPACETIME_LAB.EXPERIMENT_REGISTERED":
        validate_experiment(event.get("experiment"))
        if registered:
            raise LabError("ledger already has an experiment; use a separate ledger")
    elif kind == "SPACETIME_LAB.OBSERVATION_RECORDED":
        validate_observation(event.get("observation"))
        if not registered:
            raise LabError("register an experiment before adding observations")
    elif kind == "SPACETIME_LAB.ANALYSIS_NOTE":
        require_text(event, "note")
        if not registered:
            raise LabError("register an experiment before adding notes")
    elif kind == "SPACETIME_LAB.REVIEW_RECORDED":
        require_text(event, "reviewer")
        require_text(event, "decision")
        if not registered:
            raise LabError("register an experiment before adding reviews")
    previous = records[-1]["event_hash"] if records else ZERO_HASH
    sequence = len(records) + 1
    material = {"sequence": sequence, "previous_hash": previous, "event": event}
    envelope = {"schema_version": SCHEMA_VERSION, **material,
                "event_hash": sha256_hex(canonical_json(material).encode("utf-8"))}
    path.parent.mkdir(parents=True, exist_ok=True)
    # Single-writer reference implementation; not a distributed lock service.
    with path.open("a", encoding="utf-8") as stream:
        stream.write(canonical_json(envelope) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return envelope


def experiment_summary(path: str | Path) -> dict[str, Any]:
    verification = verify_ledger(path)
    if not verification["ok"]:
        return {"verification": verification, "experiment": None, "observations": [], "notes": []}
    experiment, observations, notes = None, [], []
    for record in _load_ledger(Path(path)):
        event = record["event"]
        kind = event["event_type"]
        if kind == "SPACETIME_LAB.EXPERIMENT_REGISTERED":
            experiment = event["experiment"]
        elif kind == "SPACETIME_LAB.OBSERVATION_RECORDED":
            observations.append({"sequence": record["sequence"], **event["observation"]})
        elif kind == "SPACETIME_LAB.ANALYSIS_NOTE":
            notes.append({"sequence": record["sequence"], "note": event["note"], "occurred_at": event["occurred_at"]})
    return {"verification": verification, "experiment": experiment, "observations": observations, "notes": notes}


def _json_value(raw: str) -> Any:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if value is None or isinstance(value, (dict, list)) or isinstance(value, float) and not math.isfinite(value):
        raise LabError("--value must be a finite scalar JSON value")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline-first spacetime hypothesis and evidence lab")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="register a preregistered experiment")
    init.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    init.add_argument("--title", required=True)
    init.add_argument("--hypothesis", required=True)
    init.add_argument("--model-name", required=True)
    init.add_argument("--claim-classification", choices=sorted(CLAIM_CLASSES), default="speculative")
    for option in ("assumption", "source-url", "prediction", "control", "safety-limit"):
        init.add_argument("--" + option, action="append", default=[])
    init.add_argument("--experiment-id")
    observe = sub.add_parser("observe", help="record a scalar observation")
    observe.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    for arg in ("source", "quantity", "value", "unit", "calibration-id"):
        observe.add_argument("--" + arg, required=True)
    observe.add_argument("--modality", choices=sorted(MODALITIES), required=True)
    observe.add_argument("--uncertainty", type=float)
    observe.add_argument("--evidence-uri")
    observe.add_argument("--evidence-file", type=Path)
    observe.add_argument("--notes", default="")
    note = sub.add_parser("note", help="record an analysis note")
    note.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    note.add_argument("--text", required=True)
    review = sub.add_parser("review", help="record human method review; does not promote claims")
    review.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--decision", choices=["accept-method", "request-revision", "reject-method", "insufficient-evidence"], required=True)
    review.add_argument("--notes", default="")
    for name in ("verify", "report"):
        command = sub.add_parser(name)
        command.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
        command.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            experiment = new_experiment(title=args.title, hypothesis=args.hypothesis, model_name=args.model_name,
                claim_classification=args.claim_classification, assumptions=args.assumption, source_urls=args.source_url,
                predictions=args.prediction, controls=args.control, safety_limits=args.safety_limit or None,
                experiment_id=args.experiment_id)
            result = append_event(args.ledger, {"event_type": "SPACETIME_LAB.EXPERIMENT_REGISTERED", "experiment": experiment})
            print(canonical_json({"ok": True, "experiment_id": experiment["experiment_id"], "sequence": result["sequence"], "ledger": str(args.ledger)}))
            return 0
        if args.command == "observe":
            digest = None
            if args.evidence_file:
                if not args.evidence_file.is_file():
                    raise LabError("--evidence-file does not exist")
                hasher = hashlib.sha256()
                with args.evidence_file.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        hasher.update(chunk)
                digest = hasher.hexdigest()
            observation = {"source": args.source, "modality": args.modality, "quantity": args.quantity,
                "value": _json_value(args.value), "unit": args.unit, "uncertainty": args.uncertainty,
                "calibration_id": args.calibration_id, "evidence_uri": args.evidence_uri,
                "evidence_sha256": digest, "notes": args.notes, "observed_at": utc_now()}
            result = append_event(args.ledger, {"event_type": "SPACETIME_LAB.OBSERVATION_RECORDED", "observation": observation})
            print(canonical_json({"ok": True, "sequence": result["sequence"], "event_hash": result["event_hash"]}))
            return 0
        if args.command == "note":
            result = append_event(args.ledger, {"event_type": "SPACETIME_LAB.ANALYSIS_NOTE", "note": args.text})
            print(canonical_json({"ok": True, "sequence": result["sequence"]}))
            return 0
        if args.command == "review":
            result = append_event(args.ledger, {"event_type": "SPACETIME_LAB.REVIEW_RECORDED", "reviewer": args.reviewer, "decision": args.decision, "notes": args.notes})
            print(canonical_json({"ok": True, "sequence": result["sequence"], "status_promoted": False}))
            return 0
        if args.command == "verify":
            report = verify_ledger(args.ledger)
            print(canonical_json(report) if args.json else json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
        if args.command == "report":
            report = experiment_summary(args.ledger)
            print(canonical_json(report) if args.json else json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["verification"]["ok"] else 1
    except (LabError, OSError, ValueError) as exc:
        print(canonical_json({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
