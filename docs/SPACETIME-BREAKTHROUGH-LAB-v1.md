# EVEZ Spacetime Breakthrough Lab v1

Purpose: a low-cost, mobile-first, offline-first workbench for registering spacetime hypotheses, recording model or sensor observations, hashing evidence files, and verifying an append-only evidence log.

## Scientific boundary

This is research infrastructure, not a warp-drive implementation. A mathematical warp-bubble metric, a symbolic consistency result, a simulation result, a published paper, an RF signal variation, and a working propulsion system are different evidence classes. Every registered experiment remains PROPOSED; a review event does not automatically promote it into a confirmed physical claim.

Ordinary Wi-Fi Channel State Information (CSI) is an RF observation. It does not directly measure spacetime curvature and cannot by itself establish superluminal transit or propulsion.

Use three claim classes:
- established: supported by established measurements or consensus sources, with citations;
- derived: follows from stated assumptions and a reproducible derivation;
- speculative: proposed but not experimentally established.

## Implementation

- research/spacetime_breakthrough_lab.py: standard-library CLI for experiment registration, scalar observation summaries, optional SHA-256 hashing of local evidence files, review notes, and hash-chain verification.
- mobile/evez-spacetime: Termux/Linux launcher using the checkout.
- integrations/spacetime_telegram_bridge.py: outbound HTTPS long-poll Telegram bridge with numeric user allowlisting, private-chat-only operation, narrow commands, update-ID replay suppression, no shell execution, and no inbound listener.
- schemas/spacetime-lab-experiment-v1.schema.json: experiment manifest contract.
- config/spacetime-adapters.example.json: disabled-by-default contracts for external agents, Telegram, Tailscale, and RuView-style CSI summaries.
- skills/spacetime-breakthrough-lab/SKILL.md: portable Hermes/OpenClaw agent workflow.
- tests/test_spacetime_breakthrough_lab.py and tests/test_spacetime_telegram_bridge.py: offline integrity and access-control tests.

## Android / Termux quick start

From the EVEZ-OS checkout:

    export EVEZ_ROOT="$HOME/evez-os"
    export EVEZ_SPACETIME_LEDGER="$HOME/.local/state/evez/spacetime-lab.jsonl"
    bash mobile/evez-spacetime --help

Register a hypothesis. This creates a record, not a feasibility claim:

    bash mobile/evez-spacetime init \
      --title "Metric ansatz consistency screen" \
      --hypothesis "Given declared signature, coordinate chart, and boundary conditions, the metric satisfies the listed symbolic constraints." \
      --model-name "metric-screen-v1" \
      --claim-classification speculative \
      --assumption "Metric signature and coordinate conventions are explicit." \
      --prediction "An independent implementation reproduces the tensor components." \
      --control "The zero-parameter limit reproduces the declared flat-space baseline." \
      --source-url "https://doi.org/10.1016/j.physletb.2024.138910"

Record a scalar result only with its origin and calibration context:

    bash mobile/evez-spacetime observe \
      --source "local-symbolic-check" \
      --modality simulation \
      --quantity "constraint_residual" \
      --value 0.0 \
      --unit dimensionless \
      --calibration-id "tool-version-and-config" \
      --notes "Synthetic/example run; not a physical measurement."

    bash mobile/evez-spacetime verify --json
    bash mobile/evez-spacetime report

For an evidence file, add the option --evidence-file path/to/file. The software stores its SHA-256 digest, not its contents. Keep the original artifact and record its origin separately. Do not commit credentials, personal records, or raw identifiable human-sensing data.

## Telegram bridge

1. Create a bot through Telegram's BotFather and keep its token secret.
2. In Termux, set TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USER_IDS to the bot token and one or more exact numeric user IDs. Optionally set EVEZ_SPACETIME_LEDGER.
3. Run python integrations/spacetime_telegram_bridge.py in the foreground for the first test. Android may stop background processes; this is not an always-on guarantee.
4. Commands: /help, /status, /verify, /proposal, /observation.

The bridge ignores non-private chats and non-allowlisted users. It refuses to start without an allowlist. It does not run shell commands, dispatch agent tools, control hardware, deploy software, fetch arbitrary URLs, or expose an inbound web port.

Proposal syntax: /proposal title | falsifiable hypothesis | model name

Observation syntax: /observation source | modality | quantity | scalar value | unit | calibration ID | notes

Allowed modalities: simulation, lab_instrument, ruview_csi, published_literature, synthetic_test. The value is a scalar; raw sensor arrays are deliberately excluded from the chat pathway.

## Hermes / OpenClaw

The included skill is a workflow contract, not a bundled copy of Hermes or OpenClaw and not a live remote-control integration. Install or expose the skill in the relevant agent's skills directory and grant it access only to the local lab CLI and ledger. Default to read-only review; present writes for operator approval. Do not put Telegram tokens, provider API keys, or other secrets in skills, agent memory, the ledger, or Git.

## Tailscale

The initial version does not include a web dashboard and requires no inbound service port. If a separate dashboard is added, prefer a tailnet-only Tailscale Serve endpoint. Do not use Funnel for the operator control plane by default. Telegram polling is outbound HTTPS and does not require any local port reachable from the internet.

## RuView / RF sensing

An optional WebSocket client exists at integrations/ruview_sensing_bridge.py. It reads scalar feature summaries from a RuView-compatible /ws/sensing stream and appends them to a registered experiment's witness ledger. It does not bundle RuView, firmware, or sensing hardware. Confirm the installed version and stream schema before connecting. The adapter allowlists features.mean_rssi (dBm), features.variance (source_native), and features.motion_band_power (source_native). It discards raw CSI, node identifiers, location labels, presence/person classifications, and vital-sign fields. This measures radio environment features, not spacetime curvature.

Install the optional client dependency:

    pip install -r requirements-ruview-bridge.txt

For a local RuView receiver (adjust port and path to match your installed version):

    export EVEZ_SPACETIME_LEDGER="$HOME/.local/state/evez/spacetime-lab.jsonl"
    export RUVIEW_WS_URL='ws://127.0.0.1:3001/ws/sensing'
    export RUVIEW_CALIBRATION_ID='site-baseline-v1'
    python integrations/ruview_sensing_bridge.py --every-seconds 5

Register an experiment first; the bridge refuses an empty or invalid ledger. The calibration ID must identify a real documented calibration or source/protocol version, not imply accuracy without evidence.

For a private remote endpoint, require TLS, authentication, and tailnet-only reachability:

    export RUVIEW_WS_URL='wss://ruview-host.your-tailnet.ts.net/ws/sensing'
    export RUVIEW_API_TOKEN='read-from-a-secret-manager-or-private-environment'
    export RUVIEW_CALIBRATION_ID='site-baseline-v1'

Do not embed credentials in URLs or place tokens in command history, logs, the ledger, or repository. Non-tailnet remote WSS requires the explicit RUVIEW_ALLOW_REMOTE_WSS=1 setting; remote unencrypted ws:// is refused. Ensure the upstream RuView endpoint itself enforces access control; do not expose a sensing WebSocket publicly.

## Hash chain: guarantees and limitations

Each ledger line contains a sequence number, the prior event hash, the payload, and a SHA-256 digest over deterministic JSON encoding. Verification detects edited, removed, reordered, malformed, or discontinuous entries if the original chain is available. This is a single-writer local reference ledger: not a digital signature, not a distributed consensus protocol, not full RFC 8785/JCS, and not tamper-proof against an attacker able to rewrite the entire file. Keep periodic external checkpoints if stronger auditability is required.

Hash integrity proves only that the log is internally consistent under this implementation. It does not prove that an observation is accurate, a source is trustworthy, a simulation is physically realistic, or a hypothesis is true.

## Engineering gates

1. Add independent symbolic/numerical GR backends with benchmarked tests, explicit units, and metric-signature conventions.
2. Add a provenance-aware literature adapter that stores source URI, version/date, claim and interpretation separately.
3. Add RuView intake with calibration IDs, consent controls, uncertainty fields, and synthetic/no-human fixtures before live sensing.
4. Add approval-gated Hermes/OpenClaw tool adapters; keep autonomous deployment and hardware control disabled.
5. If a dashboard is added, bind it to private Tailscale Serve, add authentication and audit logging, and leave public Funnel disabled unless explicitly enabled by the operator.
6. Add hardware-backed signatures and durable replay protection before multi-device or safety-critical use.


## Spacelike intervals and bubble-profile screening

The lab includes two independent mathematical baselines.

1. `research/spacetime_interval.py` calculates the 1D flat-Minkowski interval `s^2 = c^2 * delta_t^2 - delta_x^2` under signature (+,−). Negative `s^2` classifies a pair of events as spacelike separated. That is a geometric relation between events, not a recipe for a signal or object to travel between them faster than light.

   Example:

       python research/spacetime_interval.py --delta-t-seconds 1e-9 --delta-x-meters 1

   This is a numerical illustration only. It does not claim that an observer can send information over that separation.

2. `research/warp_bubble_profile.py` samples an Alcubierre-style radial shape function `f(r) = [tanh(sigma*(r+R)) - tanh(sigma*(r-R))] / [2*tanh(sigma*R)]` and its analytic radial derivative. These diagnostics can catch sign, unit, parameter-range, or sampling errors before a more expensive symbolic/numerical model is attempted.

   Example:

       python research/warp_bubble_profile.py --radius-m 10 --sigma-per-m 1 --samples 401 --output /tmp/profile.json

The bubble profile screen does **not** calculate the Einstein tensor, stress-energy tensor, energy-condition violations, negative-energy requirements, stability, causal control, or engineering feasibility. A profile function is an ansatz, not a complete spacetime solution. The next scientifically meaningful stage is independent symbolic derivation, explicit metric/signature conventions, an independently implemented Einstein-tensor calculation, numerical convergence checks, and a clearly described stress-energy/energy-condition analysis. A result should remain PROPOSED until independently reviewed; no single scalar score can establish a real breakthrough bubble.


## Integrated mobile operator commands

The existing EVEZ Termux operator now routes the lab tools directly:

    evezctl spacetime verify --json
    evezctl spacetime report
    evezctl spacetime init --title 'Metric screen' --hypothesis '...' --model-name metric-screen-v1
    evezctl spacetime-interval --delta-t-seconds 1e-9 --delta-x-meters 1
    evezctl spacetime-profile --radius-m 10 --sigma-per-m 1 --samples 401

These dispatch to local Python modules under EVEZ_ROOT. They do not call the remote model, turn on Telegram, establish a Tailscale tunnel, or control sensing hardware by themselves. The standalone launcher mobile/evez-spacetime works as well.

## Local dashboard and Tailscale

Run the read-only dashboard on loopback:

    python research/spacetime_dashboard.py --host 127.0.0.1 --port 8787 --ledger "$HOME/.local/state/evez/spacetime-lab.jsonl"

It exposes experiment metadata/counts, interval classification, and bounded shape-profile diagnostics; it does not expose observation bodies or analysis-note text. It is read-only and returns 405 for write methods. It binds only to loopback. If Tailscale is already installed and authorized on the device, you may privately share the local dashboard to your tailnet:

    tailscale serve --bg http://127.0.0.1:8787
    tailscale serve status

Use commands supported by your installed Tailscale version; reset Serve when no longer needed. This is not activated automatically: no sign-in, ACL change, firewall change, or public Funnel service was started. Never bind this unauthenticated dashboard directly to 0.0.0.0 or publish it via Funnel without a separate authenticated design.
