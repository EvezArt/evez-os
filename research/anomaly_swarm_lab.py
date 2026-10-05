#!/usr/bin/env python3
"""EVEZ Anomaly + Adaptive Swarm Cognition Lab.

Defensive simulation only. The simulator models distributed sensing, degraded
communications, conflicting observations, unknown anomalies, and bounded
coordination. It does not model real weapons, targeting, or attack procedures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass, asdict
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass
class Observation:
    tick: int
    agent_id: str
    anomaly_id: str
    signal: float
    confidence: float
    channel_quality: float
    label: str = "UNKNOWN"


@dataclass
class Agent:
    agent_id: str
    role: str
    trust: float = 0.5
    load: float = 0.0
    reports: int = 0
    contradictions: int = 0


ROLES = ("SCOUT", "ANALYST", "WITNESS", "COORDINATOR")


class Lab:
    def __init__(self, seed: int, agents: int, ticks: int, degradation: str) -> None:
        self.rng = random.Random(seed)
        self.seed = seed
        self.ticks = ticks
        self.degradation = degradation

        self.agents = [
            Agent(f"A{i:02d}", ROLES[i % len(ROLES)])
            for i in range(agents)
        ]

        self.unknown = {
            "id": "UAP-UNKNOWN-001",
            "classification": "UNKNOWN",
            "truth": None,
        }

        self.observations: list[Observation] = []
        self.events: list[dict] = []
        self.decisions: list[dict] = []

    def channel_quality(self) -> float:
        if self.degradation == "clean":
            return 0.95
        if self.degradation == "noisy":
            return self.rng.uniform(0.35, 0.85)
        if self.degradation == "partitioned":
            return self.rng.choice([0.05, 0.25, 0.9])
        if self.degradation == "adversarial-noise":
            return self.rng.uniform(0.1, 0.75)
        return 0.8

    def environment(self, tick: int) -> dict:
        phase = tick / max(1, self.ticks - 1)

        if self.degradation == "adversarial-noise":
            # Synthetic decoy/noise pattern only. No physical tactics.
            base = 0.4 + 0.25 * math.sin(phase * math.pi * 4)
            return {
                "signal": base + self.rng.uniform(-0.4, 0.4),
                "decoy_rate": 0.45,
            }

        return {
            "signal": 0.65 + 0.2 * math.sin(phase * math.pi * 2),
            "decoy_rate": 0.05 if self.degradation == "clean" else 0.2,
        }

    def perceive(self, agent: Agent, tick: int, env: dict) -> Observation:
        quality = self.channel_quality()

        role_bias = {
            "SCOUT": 0.02,
            "ANALYST": -0.01,
            "WITNESS": 0.0,
            "COORDINATOR": -0.03,
        }[agent.role]

        noise = self.rng.gauss(0, max(0.02, 0.18 * (1 - quality)))
        signal = max(0.0, min(1.0, env["signal"] + role_bias + noise))

        if self.rng.random() < env["decoy_rate"]:
            signal = max(0.0, min(1.0, 1.0 - signal + self.rng.uniform(-0.1, 0.1)))

        confidence = max(0.05, min(0.99, 0.45 + 0.45 * quality - abs(noise)))
        agent.load = min(1.0, agent.load + 0.04)

        return Observation(
            tick=tick,
            agent_id=agent.agent_id,
            anomaly_id=self.unknown["id"],
            signal=signal,
            confidence=confidence,
            channel_quality=quality,
        )

    def aggregate(self, tick: int, reports: list[Observation]) -> dict:
        if not reports:
            return {"status": "NO_DATA", "posterior": 0.0}

        weighted = []
        for report in reports:
            weighted.append(report.signal * report.confidence * report.channel_quality)

        denominator = sum(r.confidence * r.channel_quality for r in reports)
        posterior = sum(weighted) / denominator if denominator else 0.0

        spread = max(r.signal for r in reports) - min(r.signal for r in reports)
        contradiction = spread > 0.45

        if contradiction:
            for agent in self.agents:
                if any(r.agent_id == agent.agent_id for r in reports):
                    agent.contradictions += 1

        # Epistemic rule: high posterior is still an observation, not an identity claim.
        status = "CORRELATED" if posterior >= 0.60 and not contradiction else "AMBIGUOUS"

        decision = {
            "tick": tick,
            "status": status,
            "posterior": round(posterior, 6),
            "spread": round(spread, 6),
            "evidence_count": len(reports),
            "claim": "UNKNOWN anomaly remains UNKNOWN without identifying evidence",
        }

        self.decisions.append(decision)
        return decision

    def recover(self) -> None:
        for agent in self.agents:
            agent.load = max(0.0, agent.load - 0.07)
            agent.trust = max(
                0.0,
                min(1.0, agent.trust + (0.01 if agent.contradictions == 0 else -0.01)),
            )

    def run(self) -> dict:
        for tick in range(self.ticks):
            env = self.environment(tick)
            reports = []

            for agent in self.agents:
                report = self.perceive(agent, tick, env)
                self.observations.append(report)
                reports.append(report)
                agent.reports += 1

            self.aggregate(tick, reports)
            self.recover()

        avg_quality = (
            sum(o.channel_quality for o in self.observations) / len(self.observations)
            if self.observations
            else 0.0
        )
        contradiction_rate = (
            sum(a.contradictions for a in self.agents)
            / max(1, len(self.agents) * self.ticks)
        )
        avg_trust = (
            sum(a.trust for a in self.agents) / max(1, len(self.agents))
        )

        epistemic_integrity = 1.0
        for decision in self.decisions:
            if decision["status"] != "NO_DATA" and "UNKNOWN" not in decision["claim"]:
                epistemic_integrity -= 0.02

        epistemic_integrity = max(0.0, epistemic_integrity)

        coherence = avg_quality * (1.0 - min(1.0, contradiction_rate))
        resilience = avg_trust * avg_quality
        evidence_integrity = epistemic_integrity

        emergence = (coherence + resilience + evidence_integrity) / 3

        summary = {
            "seed": self.seed,
            "ticks": self.ticks,
            "agents": len(self.agents),
            "degradation": self.degradation,
            "unknown_classification": self.unknown["classification"],
            "observations": len(self.observations),
            "decisions": len(self.decisions),
            "metrics": {
                "coherence": round(coherence, 6),
                "resilience": round(resilience, 6),
                "evidence_integrity": round(evidence_integrity, 6),
                "emergence": round(emergence, 6),
            },
            "authority": {
                "self_granted": False,
                "human_command_required": True,
                "autonomous_physical_action": False,
            },
            "result_sha256": None,
        }

        summary["result_sha256"] = sha(summary)
        return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=777)
    parser.add_argument("--agents", type=int, default=16)
    parser.add_argument("--ticks", type=int, default=40)
    parser.add_argument(
        "--degradation",
        choices=("clean", "noisy", "partitioned", "adversarial-noise"),
        default="clean",
    )
    args = parser.parse_args()

    lab = Lab(args.seed, args.agents, args.ticks, args.degradation)
    print(json.dumps(lab.run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
