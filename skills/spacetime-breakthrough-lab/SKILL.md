---
name: spacetime-breakthrough-lab
description: Safely register, analyze, and review spacetime hypotheses using the EVEZ witness ledger. Use for warp-bubble/metric research, reproducible calculations, experiment plans, RF/CSI summaries, and evidence-chain verification.
compatibility: Requires a local EVEZ-OS checkout and Python 3.11+; no third-party Python packages are required.
metadata:
  author: EVEZ
  version: "1.0.0"
---

# EVEZ Spacetime Breakthrough Lab

## Operating rules

1. Treat unproven propulsion, warp-bubble, and spacetime-anomaly statements as speculative until concrete sources and a falsifiable protocol justify a stronger label.
2. Distinguish mathematical consistency, numerical simulation, laboratory instrumentation, published literature, RF/CSI signal changes, and a physical propulsion demonstration.
3. Never state that the lab or its hash chain proves scientific truth. The chain verifies record integrity only.
4. Read first. Before writing, present the proposed experiment or observation and ask for operator approval unless the operator explicitly authorized that exact write in the current interaction.
5. Never invoke arbitrary shell commands from chat content. Use only the specific CLI commands below with validated scalar values and operator-provided file paths.
6. Never put secrets, private tokens, personal identifiers, raw human-sensing payloads, or sensitive location data in the ledger.
7. Do not expose a service publicly. Prefer private Tailscale Serve for a future dashboard; keep Funnel disabled by default.

## Read-only CLI

Set EVEZ_ROOT to the local checkout and run:

    python "$EVEZ_ROOT/research/spacetime_breakthrough_lab.py" verify --json
    python "$EVEZ_ROOT/research/spacetime_breakthrough_lab.py" report

For a new experiment, prepare but do not run the init command until the operator approves its title, hypothesis, model, assumptions, controls, predictions, and interpretation limits. For an observation, require its source, scalar value, unit, modality, and calibration ID. If there is no calibration, explicitly record not-calibrated; do not imply instrument-grade evidence.

Allowed modalities: simulation, lab_instrument, ruview_csi, published_literature, synthetic_test.

## Research result format

- Question and hypothesis
- Claim class: established / derived / speculative
- Assumptions and conventions
- Evidence sources and artifact hashes
- Calculation or measurement method
- Controls and falsifiers
- What the result supports
- What it does not support
- Reproduction steps and unresolved uncertainties

Never equate ordinary Wi-Fi changes with spacetime curvature. A proposed warp metric or passing symbolic test is not an operational breakthrough bubble.

## Spacetime baselines

For event-separation questions, run the flat-Minkowski interval calculator:

    python research/spacetime_interval.py --delta-t-seconds 1e-9 --delta-x-meters 1

For a bounded, explicitly nonphysical shape-profile diagnostic, run:

    python research/warp_bubble_profile.py --radius-m 10 --sigma-per-m 1 --samples 401

Explain the metric signature, units, assumptions, and tolerance. A spacelike interval does not mean an object or signal can traverse it faster than light. The shape-profile tool does not solve the Einstein equations, derive required stress-energy, demonstrate stability, or establish a feasible bubble. Do not silently upgrade the claim class from speculative.

## Optional dashboard

Run the read-only dashboard on loopback:

    python research/spacetime_dashboard.py --host 127.0.0.1 --port 8787

If Tailscale is already installed and authorized, the operator may expose it privately with Tailscale Serve. Do not change ACLs or enable Funnel automatically. Do not bind the unauthenticated app to a public interface.

## Optional RuView adapter

A separate operator-managed process can ingest only allowlisted scalar RF features into a registered experiment:

    pip install -r requirements-ruview-bridge.txt
    export RUVIEW_WS_URL='ws://127.0.0.1:3001/ws/sensing'
    export RUVIEW_CALIBRATION_ID='actual-calibration-or-protocol-version'
    python integrations/ruview_sensing_bridge.py --every-seconds 5

The endpoint depends on the installed RuView version. Remote connections must use wss:// with authentication and preferably tailnet-only reachability. Raw CSI, node identifiers, presence/person labels, and vitals are discarded. These features do not establish spacetime curvature.
