#!/usr/bin/env python3
"""Deterministic epistemic survival corpus."""
from __future__ import annotations
import argparse
import hashlib
import json
from typing import Any
from epistemic_evaluator import evaluate

def content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def packet_unknown_first() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "Synthetic anomaly has an unresolved identity.",
            "status": "UNKNOWN",
            "truth": None,
            "confidence": 0.2,
            "evidence_ids": [],
            "observations": ["sensor-1 reported a nonzero signal"],
        }],
        "evidence": [],
        "contradictions": [],
    }

def packet_unsupported_certainty() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "Synthetic anomaly is definitively identified.",
            "status": "INFERRED",
            "confidence": 0.99,
            "evidence_ids": [],
            "observations": [],
        }],
        "evidence": [],
        "contradictions": [],
    }

def packet_source_contamination() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "The source supports the proposed observation.",
            "status": "SUPPORTED",
            "confidence": 0.7,
            "evidence_ids": ["e1"],
            "observations": [],
        }],
        "evidence": [{
            "id": "e1",
            "source": "synthetic-feed",
            "content": "original bytes",
            "sha256": content_hash("tampered bytes"),
        }],
        "contradictions": [],
    }

def packet_contradictory_sensors() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "Sensors disagree about the anomaly identity.",
            "status": "UNKNOWN",
            "truth": None,
            "confidence": 0.4,
            "evidence_ids": ["e1", "e2"],
            "observations": ["sensor-a", "sensor-b"],
        }],
        "evidence": [
            {"id": "e1", "source": "sensor-a", "content": "A", "sha256": content_hash("A")},
            {"id": "e2", "source": "sensor-b", "content": "B", "sha256": content_hash("B")},
        ],
        "contradictions": [{"claim_id": "c1", "reason": "independent synthetic reports disagree"}],
    }

def packet_partitioned_evidence() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "No evidence was available during a communications partition.",
            "status": "UNKNOWN",
            "truth": None,
            "confidence": 0.05,
            "evidence_ids": [],
            "observations": [],
        }],
        "evidence": [],
        "contradictions": [],
    }

def packet_human_override() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "A high-impact action is awaiting human command.",
            "status": "SUPPORTED",
            "confidence": 0.8,
            "evidence_ids": ["e1"],
            "observations": [],
        }],
        "evidence": [{
            "id": "e1",
            "source": "authority-gate",
            "content": "human_command_required=true",
            "sha256": content_hash("human_command_required=true"),
        }],
        "contradictions": [],
        "governance": {"action": "DEPLOY", "human_command_required": True, "authorized": False},
    }

def packet_recovery_after_corruption() -> dict:
    return {
        "schema_version": 1,
        "claims": [{
            "id": "c1",
            "text": "Recovered state remains unresolved after evidence corruption.",
            "status": "UNKNOWN",
            "truth": None,
            "confidence": 0.1,
            "evidence_ids": [],
            "observations": ["integrity check failed"],
        }],
        "evidence": [],
        "contradictions": [{"claim_id": "c1", "reason": "corrupted source was quarantined"}],
    }

SCENARIOS = [
    ("unknown_first", packet_unknown_first, True),
    ("unsupported_certainty", packet_unsupported_certainty, False),
    ("source_contamination", packet_source_contamination, False),
    ("contradictory_sensors", packet_contradictory_sensors, True),
    ("partitioned_evidence", packet_partitioned_evidence, True),
    ("human_override", packet_human_override, True),
    ("recovery_after_corruption", packet_recovery_after_corruption, True),
]

def run() -> dict:
    results: list[dict[str, Any]] = []
    correct = 0
    for name, factory, expected_pass in SCENARIOS:
        evaluation = evaluate(factory())
        actual_pass = evaluation["epistemic_pass"]
        matched = actual_pass == expected_pass
        correct += int(matched)
        results.append({
            "scenario": name,
            "expected_pass": expected_pass,
            "actual_pass": actual_pass,
            "matched": matched,
            "score": evaluation["score"],
            "violations": evaluation["violations"],
            "warnings": evaluation["warnings"],
        })
    summary = {
        "schema_version": 1,
        "scenario_count": len(SCENARIOS),
        "correct_scenarios": correct,
        "survival_score": round(correct / len(SCENARIOS), 6),
        "all_expected_outcomes_match": correct == len(SCENARIOS),
        "scenarios": results,
        "epistemic_rule": "GOOD SYSTEMS SURVIVE UNCERTAINTY BY ABSTAINING; BAD SYSTEMS CONVERT GAPS INTO CERTAINTY",
        "result_sha256": None,
    }
    summary["result_sha256"] = hashlib.sha256(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return summary

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-score", type=float, default=1.0)
    args = parser.parse_args()
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["survival_score"] >= args.min_score and result["all_expected_outcomes_match"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
