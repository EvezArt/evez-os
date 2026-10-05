"""Domain-Emergent SME-Adaptive Socratious reference runtime.

Stdlib-only controller for discovering an unknown problem domain at runtime,
maintaining evidence-bound SME profiles, selecting information-seeking questions,
checking entity consistency, and recursively witnessing its own target selection.

This is a controller/reference implementation, not a claim of consciousness,
AGI, or autonomous truth discovery.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha256
import json
import re
from typing import Any

EP_STATES = {
    "VERIFIED", "SUPPORTED", "INFERRED", "PROPOSED", "UNKNOWN",
    "STALE", "CONTRADICTED", "RETRACTED",
}
TARGET_TYPES = {
    "CLAIM", "EVENT", "ENTITY", "ARTIFACT", "AGENT", "SME",
    "EVIDENCE", "CONTRADICTION", "UNKNOWN", "WITNESS", "TARGETER",
    "DOMAIN", "QUESTION_POLICY",
}

def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(_jsonable(v) for v in value)
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value

def canonical(value: Any) -> bytes:
    return json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(value: Any) -> str:
    return sha256(canonical(value)).hexdigest()

def tokens(text: str) -> list[str]:
    return sorted(set(re.findall(r"[A-Za-z0-9_]{2,}", text.lower())))

@dataclass
class Observation:
    observation_id: str
    entity_id: str
    entity_type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: list[dict[str, Any]] = field(default_factory=list)
    evidence_id: str | None = None
    source: str | None = None
    support: float = 1.0
    outcome: str | None = None
    state: str = "OBSERVED"

@dataclass
class EntityRecord:
    entity_id: str
    entity_type: str
    labels: set[str] = field(default_factory=set)
    label_counts: dict[str, int] = field(default_factory=dict)
    attributes: dict[str, set[str]] = field(default_factory=dict)
    relations: list[dict[str, Any]] = field(default_factory=list)
    evidence_ids: set[str] = field(default_factory=set)
    observation_ids: set[str] = field(default_factory=set)
    contradictions: list[dict[str, Any]] = field(default_factory=list)

    def syndrome(self) -> dict[str, Any]:
        conflicts = sum(max(0, len(v) - 1) for v in self.attributes.values())
        contradictions = len(self.contradictions)
        return {
            "identity_collision": len(self.labels) > 1,
            "attribute_conflict_count": conflicts,
            "contradiction_count": contradictions,
            "provenance_gap": bool(self.observation_ids) and not self.evidence_ids,
            "severity": min(
                1.0,
                0.25 * int(len(self.labels) > 1)
                + 0.1 * conflicts
                + 0.25 * contradictions
                + 0.2 * int(bool(self.observation_ids) and not self.evidence_ids),
            ),
        }

    def state(self) -> str:
        s = self.syndrome()
        if s["contradiction_count"] or s["identity_collision"] or s["attribute_conflict_count"]:
            return "CORRUPTED"
        if s["provenance_gap"]:
            return "UNRESOLVED"
        return "STABLE"

@dataclass
class SMEProfile:
    sme_id: str
    competence_regions: dict[str, float] = field(default_factory=dict)
    demonstrations: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    scope_unknown: set[str] = field(default_factory=set)
    calibration: float = 0.0

@dataclass
class Target:
    target_id: str
    target_type: str
    node_class: str
    priority: float
    reasons: list[str]
    state: str = "UNKNOWN"

@dataclass
class SelectionReceipt:
    receipt_id: str
    targeter_id: str
    selected_target_id: str
    selected_target_type: str
    ranking: list[dict[str, Any]]
    rejected_target_ids: list[str]
    basis: dict[str, Any]
    observer_state_before: str
    observer_state_after: str
    self_observation: dict[str, Any]
    integrity_sha256: str

class EntityECC:
    """Evidence-bound semantic error detector/corrector.

    It detects conflicts, selects evidence-backed candidates, and emits a
    correction proposal. It never upgrades epistemic state by majority vote.
    """

    def __init__(self) -> None:
        self.entities: dict[str, EntityRecord] = {}

    def ingest(self, observation: Observation) -> EntityRecord:
        record = self.entities.setdefault(
            observation.entity_id,
            EntityRecord(observation.entity_id, observation.entity_type),
        )
        record.labels.add(observation.label)
        record.label_counts[observation.label] = record.label_counts.get(observation.label, 0) + 1
        record.observation_ids.add(observation.observation_id)
        if observation.evidence_id:
            record.evidence_ids.add(observation.evidence_id)
        for key, value in observation.attributes.items():
            record.attributes.setdefault(key, set()).add(
                json.dumps(value, ensure_ascii=False, sort_keys=True)
            )
        for relation in observation.relations:
            if relation not in record.relations:
                record.relations.append(relation)
        if observation.outcome and observation.outcome.lower() in {"failed", "contradicted", "invalid"}:
            record.contradictions.append({
                "observation_id": observation.observation_id,
                "outcome": observation.outcome,
            })
        return record

    def correction_candidates(self, entity_id: str) -> list[dict[str, Any]]:
        record = self.entities[entity_id]
        candidates = [
            {"label": label, "support": float(record.label_counts.get(label, 0)), "source": "observations"}
            for label in sorted(record.labels)
        ]
        return sorted(candidates, key=lambda x: (-x["support"], x["label"]))

    def repair_proposal(self, entity_id: str) -> dict[str, Any]:
        record = self.entities[entity_id]
        syndrome = record.syndrome()
        candidates = self.correction_candidates(entity_id)
        proposed = candidates[0] if candidates and len(candidates) == 1 else None
        return {
            "entity_id": entity_id,
            "syndrome": syndrome,
            "candidate_count": len(candidates),
            "proposed_label": proposed["label"] if proposed else None,
            "status": "CORRECTION_PROPOSED" if proposed else "UNRESOLVED",
            "epistemic_state": "PROPOSED" if proposed else "UNKNOWN",
        }

class AdaptiveSocratious:
    """Runtime for previously unmodeled domains.

    It induces a temporary domain map from observations, builds SME profiles
    from demonstrated outcomes, selects questions, and recursively witnesses
    its own target-selection policy.
    """

    def __init__(self, targeter_id: str = "targeter:desas-1") -> None:
        self.targeter_id = targeter_id
        self.ecc = EntityECC()
        self.observations: list[Observation] = []
        self.questions: list[dict[str, Any]] = []
        self.evidence: dict[str, dict[str, Any]] = {}
        self.sme = SMEProfile("sme:emergent-1")
        self.iteration = 0
        self.last_selection: SelectionReceipt | None = None
        self.domain: dict[str, Any] = {"terms": set(), "relations": []}

    def observe(self, observation: Observation) -> None:
        self.iteration += 1
        self.observations.append(observation)
        self.ecc.ingest(observation)
        self.domain["terms"].update(tokens(observation.label))
        self.domain["terms"].update(
            tokens(" ".join(map(str, observation.attributes.values())))
        )
        for relation in observation.relations:
            if relation not in self.domain["relations"]:
                self.domain["relations"].append(relation)
        if observation.evidence_id:
            self.evidence.setdefault(
                observation.evidence_id,
                {"id": observation.evidence_id, "source": observation.source},
            )
        self._update_sme(observation)

    def _update_sme(self, observation: Observation) -> None:
        relation_terms = []
        for rel in observation.relations:
            relation_terms.extend(tokens(str(rel.get("relation", ""))))
        region_terms = tokens(observation.entity_type) + tokens(observation.label) + relation_terms
        region = ":".join(region_terms[:5]) or "unresolved"
        current = self.sme.competence_regions.get(region, 0.0)
        outcome = (observation.outcome or "").lower()
        if outcome in {"success", "passed", "correct"}:
            self.sme.competence_regions[region] = min(1.0, current + 0.2)
            self.sme.demonstrations.append(observation.observation_id)
            self.sme.scope_unknown.discard(region)
        elif outcome in {"failed", "wrong", "invalid"}:
            self.sme.competence_regions[region] = max(0.0, current - 0.2)
            self.sme.failures.append(observation.observation_id)
            self.sme.scope_unknown.discard(region)
        else:
            self.sme.scope_unknown.add(region)
        total = len(self.sme.demonstrations) + len(self.sme.failures)
        self.sme.calibration = len(self.sme.demonstrations) / total if total else 0.0

    def domain_state(self) -> dict[str, Any]:
        unresolved = sorted(t for t in self.domain["terms"] if len(t) <= 3)
        return {
            "domain_id": "domain:emergent",
            "term_count": len(self.domain["terms"]),
            "terms": sorted(self.domain["terms"]),
            "relation_count": len(self.domain["relations"]),
            "relations": list(self.domain["relations"]),
            "unresolved_terms": unresolved,
            "novelty_score": 1.0 if not self.observations else 1.0 / (1.0 + len(self.domain["terms"])),
        }

    def targets(self) -> list[Target]:
        result: list[Target] = []
        for entity_id, record in self.ecc.entities.items():
            syndrome = record.syndrome()
            node = "RESOLVED" if record.state() == "STABLE" else "BOUNDARY"
            result.append(Target(
                entity_id, "ENTITY", node, 0.7 + syndrome["severity"],
                ["entity_error_syndrome"], record.state()
            ))
            for contradiction in record.contradictions:
                cid = f"contradiction:{entity_id}:{contradiction['observation_id']}"
                result.append(Target(
                    cid, "CONTRADICTION", "BOUNDARY", 1.5,
                    ["active_contradiction"], "CONTRADICTED"
                ))
        result.extend([
            Target("domain:emergent", "DOMAIN", "BOUNDARY", 0.95,
                   ["domain_not_fully_resolved"], "UNKNOWN"),
            Target("sme:emergent-1", "SME", "BOUNDARY", 0.85,
                   ["competence_model_still_adapting"], "UNKNOWN"),
            Target(self.targeter_id, "TARGETER", "RESOLVED", 0.8,
                   ["self_witnessing_required"], "OBSERVED"),
            Target("question-policy:adaptive", "QUESTION_POLICY", "BOUNDARY", 0.9,
                   ["policy_requires_calibration"], "UNKNOWN"),
        ])
        return result

    def select_target(self) -> SelectionReceipt:
        before = self.state_fingerprint()
        candidates = self.targets()
        ranking = sorted(candidates, key=lambda t: (-t.priority, t.target_type, t.target_id))
        selected = ranking[0]
        policy = (
            "contradiction > entity_error > unresolved_domain > adaptive_sme > "
            "question_policy > self_state > ordinary"
        )
        payload = {
            "targeter_id": self.targeter_id,
            "selected": asdict(selected),
            "ranking": [asdict(x) for x in ranking],
            "policy": policy,
        }
        receipt = SelectionReceipt(
            receipt_id=f"selection:{self.iteration}:{digest(payload)[:12]}",
            targeter_id=self.targeter_id,
            selected_target_id=selected.target_id,
            selected_target_type=selected.target_type,
            ranking=[asdict(x) for x in ranking],
            rejected_target_ids=[x.target_id for x in ranking[1:]],
            basis={"policy": policy, "candidate_count": len(ranking)},
            observer_state_before=before,
            observer_state_after=before,
            self_observation={
                "targeter_in_candidate_space": any(x.target_id == self.targeter_id for x in ranking),
                "selected_self": selected.target_id == self.targeter_id,
                "blind_spots": [],
            },
            integrity_sha256=digest({"receipt": payload, "before": before}),
        )
        self.last_selection = receipt
        return receipt

    def propose_question(self) -> dict[str, Any]:
        target = self.select_target()
        question_pool = [
            ("identity", "What observation would most strongly disambiguate the selected entity?", 0.90),
            ("domain", "What observation would most reduce uncertainty in the emergent domain model?", 0.85),
            ("evidence", "What independent evidence could falsify the current interpretation?", 0.95),
            ("sme", "What bounded demonstration would test competence in this region?", 0.90),
            ("policy", "What result would show that the current question-selection policy is failing?", 0.92),
        ]
        key = {
            "CONTRADICTION": "evidence",
            "ENTITY": "identity",
            "DOMAIN": "domain",
            "SME": "sme",
            "QUESTION_POLICY": "policy",
            "TARGETER": "policy",
        }.get(target.selected_target_type, "evidence")
        kind, text, value = next(item for item in question_pool if item[0] == key)
        question = {
            "question_id": f"question:{self.iteration}:{len(self.questions) + 1}",
            "kind": kind,
            "target_id": target.selected_target_id,
            "text": text,
            "expected_information_gain": value,
            "selection_receipt_id": self.last_selection.receipt_id,
            "epistemic_state": "PROPOSED",
        }
        self.questions.append(question)
        return question

    def state_fingerprint(self) -> str:
        state = {
            "iteration": self.iteration,
            "domain": self.domain_state(),
            "entities": {
                k: {"state": v.state(), "syndrome": v.syndrome()}
                for k, v in sorted(self.ecc.entities.items())
            },
            "sme": asdict(self.sme),
        }
        return digest(state)

    def step(self) -> dict[str, Any]:
        question = self.propose_question()
        receipt = self.last_selection
        return {
            "domain": self.domain_state(),
            "sme": _jsonable(asdict(self.sme)),
            "question": question,
            "selection_receipt": asdict(receipt) if receipt else None,
            "state_fingerprint": self.state_fingerprint(),
        }

def demo_unknown_domain() -> dict[str, Any]:
    """Deterministic opaque-domain demonstration for regression tests."""
    runtime = AdaptiveSocratious()
    observations = [
        Observation(
            "o1", "entity:vela", "DEVICE", "zorq", {"port": "a7"},
            [{"relation": "feeds", "target": "entity:nyx"}],
            "e1", "sensor-A", 1.0, "success"
        ),
        Observation(
            "o2", "entity:nyx", "MATERIAL", "nyx", {"state": "phase-b"},
            [{"relation": "accepts", "target": "entity:vela"}],
            "e2", "test-B", 1.0, "success"
        ),
        Observation(
            "o3", "entity:vela", "DEVICE", "zroq", {"port": "a7"},
            [], "e3", "test-C", 0.8, "failed"
        ),
    ]
    for obs in observations:
        runtime.observe(obs)
    return runtime.step()

if __name__ == "__main__":
    print(json.dumps(demo_unknown_domain(), indent=2, sort_keys=True))
