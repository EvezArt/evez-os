# EVEZ-OS — Visual Cognition + Forensic Spine Toolkit

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org)

> **AI agents are opaque. EVEZ-OS focuses on auditable traces and artifact generation.**

This repository is a mixed workspace; the active root CLI is `tools/evez.py`.
It provides lightweight commands for:
- basic spine lint checks
- spine playback of the latest module in `spine/`
- visualization wrapper (`tools/visualize_thought.py`)
- repo-level verification summaries

## Install (manual)

```bash
git clone https://github.com/EvezArt/evez-os.git
cd evez-os
python3 tools/evez.py --help
```

Optional dependencies for richer visual output:

```bash
pip install numpy pillow scipy
```

## Quick Start

```bash
# Show available commands
python3 tools/evez.py --help

# Run basic spine lint (safe no-op if spine/ missing)
python3 tools/evez.py lint

# Run verify summary
python3 tools/evez.py verify
```

## Demo Runner

```bash
python3 tools/run_all.py --seed --mode spicy
```

This seeds spine files (if empty), regenerates cartography artifacts, and writes a transcript.

## Repo Reality (audited)

Primary runnable surfaces at repo root:
- `tools/evez.py` — top-level dispatcher CLI
- `tools/run_all.py` — seed/cartography/narration demo pipeline
- `tools/self_cartography.py`, `tools/narrate.py`, `tools/visualize_thought.py`
- `.github/workflows/ci.yml` — smoke checks for the real CLI

Additional directories such as `core/` and `os-evez/` contain parallel/legacy layouts and are **not** the only required runtime path for root CLI usage.

## License

Community license: AGPL-3.0. See `LICENSE`.
