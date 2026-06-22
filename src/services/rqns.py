#!/usr/bin/env python3
"""
RQNS — Reactive Quantum Neuromorphic Sensing Pipeline
9th service of the EVEZ firmament — Port 9119

Implements:
  1. LIF Neuron Sensor — Leaky Integrate-and-Fire neuron sensing mesh state
  2. Contextual Bandit Agent — Exploration/exploitation action selection
  3. Hot-Swapping Patch Pipeline — Runtime parameter swaps without restart
  4. Falsification-Weighted Learning — Failures shift behavior 3x harder
"""

import json
import math
import random
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError

# ─── LIF Neuron ───────────────────────────────────────────────────────────────

class LIFNeuron:
    """Leaky Integrate-and-Fire neuron for mesh state sensing."""

    def __init__(self, threshold=1.0, leak=0.1, reset=0.0, refractory_periods=5):
        self.threshold = threshold
        self.leak = leak
        self.reset_voltage = reset
        self.membrane_potential = 0.0
        self.refractory = 0
        self.refractory_periods = refractory_periods
        self.spike_count = 0
        self.last_spike_time = 0.0
        self.total_input = 0.0

        # Patches
        self._patches = {"threshold": threshold, "leak": leak, "reset": reset}
        self._patch_history = []

    def integrate(self, current, dt=1.0):
        """Inject current and leak. Returns True if spike fired."""
        if self.refractory > 0:
            self.refractory -= 1
            return False

        self.membrane_potential += current * dt
        self.membrane_potential *= (1.0 - self.leak)  # leak
        self.total_input = current

        if self.membrane_potential >= self.threshold:
            self._fire()
            return True
        return False

    def _fire(self):
        self.spike_count += 1
        self.last_spike_time = time.time()
        self.membrane_potential = self.reset_voltage
        self.refractory = self.refractory_periods

    def apply_patch(self, param, value):
        if param in self._patches:
            old = self._patches[param]
            self._patches[param] = value
            setattr(self, param if param != "reset" else "reset_voltage", value)
            # Keep threshold attr in sync
            if param == "threshold":
                self.threshold = value
            elif param == "leak":
                self.leak = value
            elif param == "reset":
                self.reset_voltage = value
            self._patch_history.append({
                "param": param, "old": old, "new": value, "time": time.time()
            })
            return True
        return False

    def state(self):
        return {
            "membrane_potential": round(self.membrane_potential, 6),
            "threshold": self._patches["threshold"],
            "leak": self._patches["leak"],
            "reset_voltage": self._patches["reset"],
            "refractory_remaining": self.refractory,
            "spike_count": self.spike_count,
            "last_spike_time": self.last_spike_time,
            "last_input": round(self.total_input, 6),
        }


# ─── Contextual Bandit ────────────────────────────────────────────────────────

class ContextualBandit:
    """Multi-armed bandit with falsification-weighted learning (failures 3x)."""

    DEFAULT_ARMS = [
        "heal_mesh", "run_pipeline", "dream", "cross_correlate",
        "synthesize_audio", "falsify", "no_op"
    ]

    def __init__(self, arms=None, failure_weight=3.0, exploration_rate=0.15):
        self.arms = arms or list(self.DEFAULT_ARMS)
        self.failure_weight = failure_weight
        self.exploration_rate = exploration_rate
        self.counts = {a: 0 for a in self.arms}
        self.rewards = {a: 0.0 for a in self.arms}
        self.last_action = None
        self._patches = {"failure_weight": failure_weight, "exploration_rate": exploration_rate}
        self._patch_history = []

    def choose(self, context=None):
        """ε-greedy action selection."""
        if random.random() < self.exploration_rate:
            arm = random.choice(self.arms)
        else:
            # UCB1-style with epsilon fallback
            best_val = -1.0
            best_arm = self.arms[0]
            for a in self.arms:
                if self.counts[a] == 0:
                    best_arm = a
                    break
                avg = self.rewards[a] / self.counts[a]
                bonus = math.sqrt(2.0 * math.log(sum(self.counts.values()) + 1) / self.counts[a])
                val = avg + bonus
                if val > best_val:
                    best_val = val
                    best_arm = a
            arm = best_arm

        self.last_action = arm
        est = self._estimate(arm)
        return arm, est

    def _estimate(self, arm):
        if self.counts[arm] == 0:
            return 0.5
        return self.rewards[arm] / self.counts[arm]

    def learn(self, arm, reward):
        """Update reward. Negative rewards (failures) are amplified by failure_weight."""
        if arm not in self.arms:
            return False
        if reward < 0:
            reward *= self.failure_weight
        self.counts[arm] += 1
        self.rewards[arm] += reward
        return True

    def apply_patch(self, param, value):
        if param in self._patches:
            old = self._patches[param]
            self._patches[param] = value
            setattr(self, param, value)
            self._patch_history.append({
                "param": param, "old": old, "new": value, "time": time.time()
            })
            return True
        return False

    def state(self):
        arm_stats = {}
        for a in self.arms:
            c = self.counts[a]
            arm_stats[a] = {
                "count": c,
                "total_reward": round(self.rewards[a], 4),
                "avg_reward": round(self.rewards[a] / c, 4) if c > 0 else None,
            }
        return {
            "arms": arm_stats,
            "last_action": self.last_action,
            "failure_weight": self._patches["failure_weight"],
            "exploration_rate": self._patches["exploration_rate"],
        }


# ─── RQNS Pipeline ────────────────────────────────────────────────────────────

class RQNSPipeline:
    """Full RQNS cycle: sense → act → learn → patch check."""

    MESH_HEALTH_URL = "http://localhost:9118/health"

    def __init__(self):
        self.neuron = LIFNeuron()
        self.bandit = ContextualBandit()
        self.cycle_count = 0
        self.last_mesh_state = None
        self.last_emergence = None
        self.last_spine_rate = None
        self.patch_log = []

    def fetch_mesh_state(self):
        """Query the mesh health endpoint (port 9118)."""
        try:
            req = Request(self.MESH_HEALTH_URL, headers={"Accept": "application/json"})
            with urlopen(req, timeout=3) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e), "reachable": False}

    def sense(self, external_data=None):
        """Feed data to the LIF neuron. Returns spike decision + neuron state."""
        total_current = 0.0
        details = {}

        # 1) Mesh state sensing
        mesh = external_data or self.fetch_mesh_state()
        mesh_ok = mesh.get("reachable", True) if isinstance(mesh, dict) else True

        if isinstance(mesh, dict) and not mesh.get("error"):
            services = mesh.get("services", {})
            # Count down services
            down = sum(1 for v in services.values() if v != "UP") if isinstance(services, dict) else 0
            if down > 0:
                total_current += down * 0.4  # strong signal per down service
                details["down_services"] = down

            # Emergence score delta
            emergence = mesh.get("emergence_score") or mesh.get("emergence")
            if emergence is not None:
                if self.last_emergence is not None:
                    delta = abs(emergence - self.last_emergence)
                    if delta > 0.1:
                        total_current += delta * 0.3
                        details["emergence_delta"] = round(delta, 4)
                self.last_emergence = emergence

            # Spine event rate
            spine_rate = mesh.get("spine_event_rate") or mesh.get("spine_rate")
            if spine_rate is not None:
                if self.last_spine_rate is not None:
                    delta = abs(spine_rate - self.last_spine_rate)
                    if delta > 0.05:
                        total_current += delta * 0.2
                        details["spine_rate_delta"] = round(delta, 4)
                self.last_spine_rate = spine_rate
        else:
            # Mesh unreachable → strong negative signal
            total_current += 0.8
            details["mesh_unreachable"] = True

        self.last_mesh_state = mesh

        # Also accept raw current injection
        if external_data and isinstance(external_data, dict):
            total_current += external_data.get("inject_current", 0.0)

        spiked = self.neuron.integrate(total_current)

        return {
            "spiked": spiked,
            "current_input": round(total_current, 6),
            "details": details,
            "neuron": self.neuron.state(),
        }

    def act(self, context=None):
        arm, estimate = self.bandit.choose(context)
        return {"arm": arm, "reward_estimate": round(estimate, 4)}

    def learn(self, arm, reward):
        """Update bandit. Failures (reward<0) get 3x weight."""
        applied = self.bandit.learn(arm, reward)
        return {
            "arm": arm,
            "raw_reward": reward,
            "effective_reward": reward * self.bandit.failure_weight if reward < 0 else reward,
            "applied": applied,
            "bandit": self.bandit.state(),
        }

    def patch(self, target, param, value):
        """Hot-swap a parameter on neuron or bandit."""
        record = {
            "target": target, "param": param, "value": value,
            "time": time.time()
        }
        if target == "neuron":
            ok = self.neuron.apply_patch(param, value)
        elif target == "bandit":
            ok = self.bandit.apply_patch(param, value)
        else:
            return {"applied": False, "error": f"Unknown target: {target}"}

        record["applied"] = ok
        self.patch_log.append(record)
        return record

    def cycle(self, external_data=None, reward_override=None):
        """Full RQNS cycle: sense → act → learn → patch check."""
        self.cycle_count += 1

        # Sense
        sense_result = self.sense(external_data)

        # Act
        act_result = self.act(context=sense_result)

        # Learn — simulate reward based on spike
        if reward_override is not None:
            reward = reward_override
        elif sense_result["spiked"]:
            reward = 1.0  # spike = positive (detected anomaly)
        else:
            reward = -0.1  # no spike = mild negative (missed something?)

        learn_result = self.learn(act_result["arm"], reward)

        # Patch check — auto-patch if neuron is stuck
        patch_results = []
        if self.neuron.refractory > 3 and self.neuron.spike_count == 0:
            pr = self.patch("neuron", "threshold", self.neuron.threshold * 0.9)
            patch_results.append(pr)

        return {
            "cycle": self.cycle_count,
            "sense": sense_result,
            "act": act_result,
            "learn": learn_result,
            "patches": patch_results,
        }

    def state(self):
        return {
            "cycle_count": self.cycle_count,
            "neuron": self.neuron.state(),
            "neuron_patches": self.neuron._patch_history[-10:],
            "bandit": self.bandit.state(),
            "bandit_patches": self.bandit._patch_history[-10:],
            "patch_log": self.patch_log[-10:],
            "last_mesh_state": self.last_mesh_state,
            "last_emergence": self.last_emergence,
            "last_spine_rate": self.last_spine_rate,
        }


# ─── HTTP Server ──────────────────────────────────────────────────────────────

pipeline = RQNSPipeline()

class RQNSHandler(BaseHTTPRequestHandler):
    def _json_response(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode())
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/health":
            self._json_response(200, {
                "status": "alive",
                "service": "rqns",
                "port": 9119,
                "cycle_count": pipeline.cycle_count,
                "spike_count": pipeline.neuron.spike_count,
            })
        elif self.path == "/state":
            self._json_response(200, pipeline.state())
        else:
            self._json_response(404, {"error": "not found"})

    def do_POST(self):
        data = self._read_body()

        if self.path == "/sense":
            result = pipeline.sense(external_data=data)
            self._json_response(200, result)

        elif self.path == "/act":
            context = data.get("context")
            result = pipeline.act(context=context)
            self._json_response(200, result)

        elif self.path == "/learn":
            arm = data.get("arm")
            reward = data.get("reward", 0.0)
            if arm is None:
                self._json_response(400, {"error": "arm required"})
                return
            result = pipeline.learn(arm, reward)
            self._json_response(200, result)

        elif self.path == "/patch":
            target = data.get("target")
            param = data.get("param")
            value = data.get("value")
            if not all([target, param, value is not None]):
                self._json_response(400, {"error": "target, param, value required"})
                return
            result = pipeline.patch(target, param, value)
            self._json_response(200, result)

        elif self.path == "/cycle":
            ext = data.get("external_data")
            reward_ov = data.get("reward")
            result = pipeline.cycle(external_data=ext, reward_override=reward_ov)
            self._json_response(200, result)

        else:
            self._json_response(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        # Quiet logs
        pass


def main():
    host = "0.0.0.0"
    port = 9119
    server = HTTPServer((host, port), RQNSHandler)
    print(f"[RQNS] Reactive Quantum Neuromorphic Sensing pipeline on {host}:{port}")
    print(f"[RQNS] Endpoints: /health /sense /act /learn /patch /state /cycle")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[RQNS] Shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
