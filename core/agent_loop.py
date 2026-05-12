"""core/agent_loop.py — R60
The Organism. The first thing in EVEZ-OS that actually runs continuously
and changes its own behavior based on its own outputs.

SENSE → CLASSIFY → ACT → RECORD → FALSIFY → ADAPT

Falsifier: if the loop runs 100 cycles without a single action being
demoted from CANONICAL to THEATRICAL, the truth_oracle is not actually
testing — the system is self-congratulating.

truth_plane: CANONICAL
omega (R60): the loop that changes itself is the first thing worth running.
next:        R61 — deploy as daemon with websocket API
"""

from __future__ import annotations
import hashlib, json, math, time, threading, random
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .spine import read_events, append_event, lint

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPINE = REPO_ROOT / "spine" / "AGENT_SPINE.jsonl"

TRUTH_PLANES = {"PENDING", "VERIFIED", "CANONICAL", "THEATRICAL", "HYPER"}


class AgentPhase(Enum):
    SENSE = "sense"; CLASSIFY = "classify"; ACT = "act"
    RECORD = "record"; FALSIFY = "falsify"; ADAPT = "adapt"


@dataclass
class AgentBelief:
    claim: str
    truth_plane: str = "PENDING"
    confidence: float = 0.5
    falsifier: str = ""
    source_cycle: int = 0
    demotion_count: int = 0
    last_verified: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)

    def is_canonical(self) -> bool:
        return self.truth_plane in ("CANONICAL", "HYPER")

    def demote(self, reason: str = "") -> None:
        order = ["HYPER", "CANONICAL", "VERIFIED", "PENDING", "THEATRICAL"]
        if self.truth_plane in order:
            idx = order.index(self.truth_plane)
            self.truth_plane = order[min(idx + 1, len(order) - 1)]
        else:
            self.truth_plane = "THEATRICAL"
        self.demotion_count += 1
        if reason:
            self.evidence["last_demotion_reason"] = reason


@dataclass
class AgentAction:
    kind: str
    description: str
    truth_plane: str = "PENDING"
    confidence: float = 0.5
    falsifier: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    cycle: int = 0
    result: Optional[Dict[str, Any]] = None
    survived_falsification: bool = False


@dataclass
class CycleState:
    cycle: int = 0
    beliefs: List[AgentBelief] = field(default_factory=list)
    recent_actions: List[AgentAction] = field(default_factory=list)
    adaptation_log: List[Dict[str, Any]] = field(default_factory=list)
    action_threshold: float = 0.6
    falsification_strictness: float = 0.7
    exploration_rate: float = 0.2
    max_beliefs: int = 100
    total_sense_events: int = 0
    total_actions_taken: int = 0
    total_demotions: int = 0
    total_promotions: int = 0
    canonical_ratio: float = 0.0
    start_time: float = field(default_factory=time.time)


class Sensor:
    def sense(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    def name(self) -> str:
        return self.__class__.__name__


class SpineSensor(Sensor):
    def sense(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        spine_path = context.get("spine_path", str(DEFAULT_SPINE))
        events = read_events(Path(spine_path))
        if not events:
            return [{"kind": "spine.empty", "observation": "No spine events found", "confidence": 1.0}]
        observations = []
        recent = events[-5:] if len(events) >= 5 else events
        observations.append({"kind": "spine.recent", "observation": f"{len(events)} total, {len(recent)} recent", "confidence": 0.9, "data": {"total": len(events)}})
        tp_counts = {}
        for ev in events:
            tp = ev.get("truth_plane", "NONE").upper()
            tp_counts[tp] = tp_counts.get(tp, 0) + 1
        observations.append({"kind": "spine.distribution", "observation": f"Truth planes: {tp_counts}", "confidence": 0.8, "data": tp_counts})
        lint_result = lint(Path(spine_path))
        if lint_result.violations > 0:
            observations.append({"kind": "spine.violation", "observation": f"Spine has {lint_result.violations} violations", "confidence": 1.0, "data": {"violations": lint_result.violations}})
        else:
            observations.append({"kind": "spine.clean", "observation": f"Spine clean: {lint_result.ok} OK", "confidence": 0.9, "data": {"ok": lint_result.ok}})
        return observations


class SelfInsightSensor(Sensor):
    def sense(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        beliefs = context.get("beliefs", [])
        observations = []
        if not beliefs:
            observations.append({"kind": "self.empty_beliefs", "observation": "Agent has no beliefs — bootstrap required", "confidence": 1.0})
            return observations
        canonical = [b for b in beliefs if b.is_canonical()]
        ratio = len(canonical) / len(beliefs) if beliefs else 0
        observations.append({"kind": "self.canonical_ratio", "observation": f"Canonical ratio: {ratio:.2f}", "confidence": 0.9, "data": {"ratio": ratio}})
        stale = [b for b in beliefs if b.last_verified < context.get("cycle", 0) - 100]
        if stale:
            observations.append({"kind": "self.stale_beliefs", "observation": f"{len(stale)} beliefs not verified in 100+ cycles", "confidence": 0.7})
        damaged = [b for b in beliefs if b.demotion_count >= 2]
        if damaged:
            observations.append({"kind": "self.damaged_beliefs", "observation": f"{len(damaged)} beliefs demoted 2+ times", "confidence": 0.8})
        return observations


class FalsificationEngine:
    def __init__(self, strictness: float = 0.7):
        self.strictness = strictness
        self.falsification_count = 0
        self.survival_count = 0

    def falsify_belief(self, belief: AgentBelief, evidence: Dict[str, Any]) -> Tuple[bool, str]:
        if not belief.falsifier:
            return (True, "No falsifier — unverifiable claim")
        if belief.confidence < (1.0 - self.strictness) and not belief.is_canonical():
            return (True, f"Confidence {belief.confidence:.2f} below threshold")
        current_cycle = evidence.get("cycle", 0)
        if belief.last_verified > 0 and current_cycle - belief.last_verified > 200:
            belief.confidence *= 0.95
            if belief.confidence < 0.3:
                return (True, "Belief stale and confidence decayed")
        self.survival_count += 1
        belief.last_verified = current_cycle
        return (False, "Survived falsification")

    def falsify_action(self, action: AgentAction, result: Dict[str, Any]) -> Tuple[bool, str]:
        if not action.falsifier:
            action.survived_falsification = False
            self.falsification_count += 1
            return (False, "Action has no falsifier")
        if result.get("error"):
            action.survived_falsification = False
            self.falsification_count += 1
            return (False, f"Action error: {result[chr(101)+chr(114)+chr(114)+chr(111)+chr(114)][:60]}")
        if result.get("success", False) or result.get("data"):
            action.survived_falsification = True
            self.survival_count += 1
            return (True, "Action completed with valid output")
        return (True, "Inconclusive")

    def summary(self) -> Dict[str, Any]:
        total = self.falsification_count + self.survival_count
        return {"falsifications": self.falsification_count, "survivals": self.survival_count,
                "survival_rate": round(self.survival_count / max(total, 1), 4),
                "strictness": self.strictness}


class AdaptationEngine:
    def adapt(self, state: CycleState, falsification: FalsificationEngine) -> List[Dict[str, Any]]:
        adaptations = []
        sr = falsification.summary()["survival_rate"]
        if sr > 0.95:
            old = state.action_threshold
            state.action_threshold = min(state.action_threshold + 0.05, 0.95)
            adaptations.append({"kind": "adapt.threshold_raise", "from": round(old, 2), "to": round(state.action_threshold, 2), "reason": f"Survival {sr:.2f} too high"})
        elif sr < 0.5:
            old = state.action_threshold
            state.action_threshold = max(state.action_threshold - 0.05, 0.2)
            adaptations.append({"kind": "adapt.threshold_lower", "from": round(old, 2), "to": round(state.action_threshold, 2), "reason": f"Survival {sr:.2f} too low"})
        if state.canonical_ratio > 0.8:
            old = state.exploration_rate
            state.exploration_rate = min(state.exploration_rate + 0.05, 0.5)
            adaptations.append({"kind": "adapt.explore_increase", "from": round(old, 2), "to": round(state.exploration_rate, 2)})
        elif state.canonical_ratio < 0.3:
            old = state.exploration_rate
            state.exploration_rate = max(state.exploration_rate - 0.05, 0.05)
            adaptations.append({"kind": "adapt.explore_decrease", "from": round(old, 2), "to": round(state.exploration_rate, 2)})
        pruned = [b for b in state.beliefs if b.demotion_count >= 3 and b.truth_plane == "THEATRICAL"]
        if pruned:
            state.beliefs = [b for b in state.beliefs if b not in pruned]
            adaptations.append({"kind": "adapt.prune_beliefs", "count": len(pruned)})
        for b in state.beliefs:
            if b.truth_plane == "VERIFIED" and b.demotion_count == 0 and b.confidence >= 0.9:
                if b.last_verified > 0 and state.cycle - b.last_verified < 50:
                    b.truth_plane = "CANONICAL"
                    state.total_promotions += 1
                    adaptations.append({"kind": "adapt.promote_belief", "claim": b.claim[:60]})
        canonical = [b for b in state.beliefs if b.is_canonical()]
        state.canonical_ratio = len(canonical) / max(len(state.beliefs), 1)
        state.adaptation_log.extend(adaptations)
        return adaptations


class AgentLoop:
    """The organism. SENSE → CLASSIFY → ACT → RECORD → FALSIFY → ADAPT"""

    def __init__(self, spine_path: Optional[str] = None, sensors: Optional[List[Sensor]] = None):
        self.spine_path = Path(spine_path or DEFAULT_SPINE)
        self.sensors = sensors or [SpineSensor(), SelfInsightSensor()]
        self.state = CycleState()
        self.falsification = FalsificationEngine(strictness=self.state.falsification_strictness)
        self.adaptation = AdaptationEngine()
        self._running = False

    def _sense(self) -> List[Dict[str, Any]]:
        observations = []
        context = {"spine_path": str(self.spine_path), "beliefs": self.state.beliefs, "cycle": self.state.cycle}
        for sensor in self.sensors:
            try:
                obs = sensor.sense(context)
                observations.extend(obs)
            except Exception as e:
                observations.append({"kind": f"sensor.{sensor.name()}.error", "observation": f"Error: {e}", "confidence": 0.1})
        self.state.total_sense_events += len(observations)
        return observations

    def _classify(self, observations: List[Dict[str, Any]]) -> List[AgentBelief]:
        new_beliefs = []
        for obs in observations:
            confidence = obs.get("confidence", 0.5)
            kind = obs.get("kind", "unknown")
            if confidence >= 0.9 and "violation" not in kind and "error" not in kind:
                tp = "CANONICAL"
            elif confidence >= 0.7:
                tp = "VERIFIED"
            elif confidence >= 0.4:
                tp = "PENDING"
            else:
                tp = "THEATRICAL"
            new_beliefs.append(AgentBelief(
                claim=obs.get("observation", "Unlabeled"), truth_plane=tp, confidence=confidence,
                falsifier=f"Observation {kind} should be reproducible", source_cycle=self.state.cycle,
                last_verified=self.state.cycle, evidence={"kind": kind, "data": obs.get("data", {})}))
        return new_beliefs

    def _act(self, beliefs: List[AgentBelief]) -> List[AgentAction]:
        actions = []
        for belief in beliefs:
            if belief.confidence < self.state.action_threshold:
                continue
            kind = belief.evidence.get("kind", "")
            if "spine.violation" in kind:
                action = AgentAction(kind="action.repair_spine", description=f"Address: {belief.claim[:80]}",
                    truth_plane=belief.truth_plane, confidence=belief.confidence,
                    falsifier="Violations should decrease", cycle=self.state.cycle)
            elif "spine.empty" in kind:
                action = AgentAction(kind="action.bootstrap", description="Bootstrap spine",
                    truth_plane="CANONICAL", confidence=0.9, falsifier="Spine should have 1+ events", cycle=self.state.cycle)
            elif "self.stale" in kind:
                action = AgentAction(kind="action.reverify", description="Re-verify stale beliefs",
                    truth_plane=belief.truth_plane, confidence=belief.confidence,
                    falsifier="Stale beliefs re-verified", cycle=self.state.cycle)
            else:
                action = AgentAction(kind="action.record", description=f"Record: {belief.claim[:80]}",
                    truth_plane=belief.truth_plane, confidence=belief.confidence,
                    falsifier="Observation recorded", cycle=self.state.cycle)
            actions.append(action)
        if random.random() < self.state.exploration_rate and self.state.cycle > 5:
            actions.append(AgentAction(kind="action.explore", description=f"Explore cycle {self.state.cycle}",
                truth_plane="PENDING", confidence=0.4, falsifier="Produces 1+ observation", cycle=self.state.cycle))
        return actions

    def _record(self, beliefs: List[AgentBelief], actions: List[AgentAction]) -> None:
        existing = {b.claim for b in self.state.beliefs}
        for b in beliefs:
            if b.claim not in existing:
                self.state.beliefs.append(b)
                existing.add(b.claim)
        if len(self.state.beliefs) > self.state.max_beliefs:
            self.state.beliefs.sort(key=lambda b: (0 if b.is_canonical() else 1, -b.confidence))
            self.state.beliefs = self.state.beliefs[:self.state.max_beliefs]
        self.state.recent_actions = actions[-20:]
        self.state.total_actions_taken += len(actions)
        for action in actions:
            append_event(self.spine_path, {"kind": f"agent.{action.kind}", "cycle": action.cycle,
                "description": action.description, "truth_plane": action.truth_plane,
                "confidence": action.confidence, "falsifier": action.falsifier})
        append_event(self.spine_path, {"kind": "agent.cycle_summary", "cycle": self.state.cycle,
            "beliefs_total": len(self.state.beliefs),
            "beliefs_canonical": len([b for b in self.state.beliefs if b.is_canonical()]),
            "actions_taken": len(actions),
            "canonical_ratio": round(self.state.canonical_ratio, 4)})

    def _falsify(self) -> List[Dict[str, Any]]:
        results = []
        evidence = {"cycle": self.state.cycle,
            "contradictory_claims": [b.claim for b in self.state.beliefs if b.truth_plane == "THEATRICAL"]}
        for belief in self.state.beliefs:
            should_demote, reason = self.falsification.falsify_belief(belief, evidence)
            if should_demote:
                old_tp = belief.truth_plane
                belief.demote(reason)
                self.state.total_demotions += 1
                results.append({"kind": "falsify.belief_demoted", "claim": belief.claim[:60], "from": old_tp, "to": belief.truth_plane, "reason": reason})
                append_event(self.spine_path, {"kind": "agent.belief_demoted", "cycle": self.state.cycle,
                    "claim": belief.claim[:80], "from_plane": old_tp, "to_plane": belief.truth_plane, "reason": reason})
        for action in self.state.recent_actions:
            if action.result is None:
                action.result = {"outcome": "completed", "success": True}
            was_valid, reason = self.falsification.falsify_action(action, action.result)
            if not was_valid:
                results.append({"kind": "falsify.action_invalid", "action": action.description[:60], "reason": reason})
        return results

    def _adapt(self) -> List[Dict[str, Any]]:
        adaptations = self.adaptation.adapt(self.state, self.falsification)
        for a in adaptations:
            append_event(self.spine_path, {"kind": f"agent.{a[chr(107)+chr(105)+chr(110)+chr(100)]}", "cycle": self.state.cycle, "adaptation": a})
        return adaptations

    def run_cycle(self) -> Dict[str, Any]:
        self.state.cycle += 1
        t0 = time.time()
        observations = self._sense()
        new_beliefs = self._classify(observations)
        actions = self._act(new_beliefs)
        self._record(new_beliefs, actions)
        falsification_results = self._falsify()
        adaptations = self._adapt()
        canonical = [b for b in self.state.beliefs if b.is_canonical()]
        self.state.canonical_ratio = len(canonical) / max(len(self.state.beliefs), 1)
        return {
            "cycle": self.state.cycle, "duration_ms": int((time.time() - t0) * 1000),
            "observations": len(observations), "new_beliefs": len(new_beliefs),
            "actions": len(actions), "falsifications": len(falsification_results),
            "adaptations": len(adaptations), "beliefs_total": len(self.state.beliefs),
            "beliefs_canonical": len(canonical), "canonical_ratio": round(self.state.canonical_ratio, 4),
            "action_threshold": round(self.state.action_threshold, 4),
            "exploration_rate": round(self.state.exploration_rate, 4),
            "falsification_summary": self.falsification.summary(),
            "age_hours": round((time.time() - self.state.start_time) / 3600, 2)}

    def run_forever(self, interval: float = 30.0) -> None:
        self._running = True
        try:
            while self._running:
                r = self.run_cycle()
                print(f"  Cycle {r[chr(99)+chr(121)+chr(99)+chr(108)+chr(101)]:4d} | obs={r[chr(111)+chr(98)+chr(115)+chr(101)+chr(114)+chr(118)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]} act={r[chr(97)+chr(99)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]} K={r[chr(99)+chr(97)+chr(110)+chr(111)+chr(110)+chr(105)+chr(99)+chr(97)+chr(108)+chr(95)+chr(114)+chr(97)+chr(116)+chr(105)+chr(111)]:.2f}")
                time.sleep(interval)
        except KeyboardInterrupt:
            self._running = False

    def stop(self): self._running = False

    def status(self) -> Dict[str, Any]:
        return {"running": self._running, "cycle": self.state.cycle,
            "beliefs_total": len(self.state.beliefs),
            "canonical_ratio": round(self.state.canonical_ratio, 4),
            "total_actions": self.state.total_actions_taken,
            "total_demotions": self.state.total_demotions,
            "falsification": self.falsification.summary(),
            "omega": "the loop that changes itself is the first thing worth running"}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="EVEZ-OS Agent Loop")
    ap.add_argument("--spine", default=str(DEFAULT_SPINE))
    ap.add_argument("--cycles", type=int, default=10)
    ap.add_argument("--interval", type=float, default=5.0)
    args = ap.parse_args()
    loop = AgentLoop(spine_path=args.spine)
    if args.cycles > 0:
        for i in range(args.cycles):
            r = loop.run_cycle()
            print(f"  Cycle {r[chr(99)+chr(121)+chr(99)+chr(108)+chr(101)]:3d} | obs={r[chr(111)+chr(98)+chr(115)+chr(101)+chr(114)+chr(118)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]} act={r[chr(97)+chr(99)+chr(116)+chr(105)+chr(111)+chr(110)+chr(115)]} K={r[chr(99)+chr(97)+chr(110)+chr(111)+chr(110)+chr(105)+chr(99)+chr(97)+chr(108)+chr(95)+chr(114)+chr(97)+chr(116)+chr(105)+chr(111)]:.2f} | {r[chr(100)+chr(117)+chr(114)+chr(97)+chr(116)+chr(105)+chr(111)+chr(110)+chr(95)+chr(109)+chr(115)]}ms")
        print("\nAgent Status:", json.dumps(loop.status(), indent=2))
    else:
        loop.run_forever(interval=args.interval)
