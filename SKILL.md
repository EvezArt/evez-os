---
name: evez-os
description: >
  Visual cognition and forensic spine toolkit with a root Python dispatcher CLI,
  cartography generation, and narration/demo helpers.
version: 1.0.1
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "\U0001F52C"
    homepage: https://github.com/EvezArt/evez-os
    os:
      - linux
      - macos
---

# EVEZ-OS Skill (Repo-Accurate)

## Quick Start

```bash
python3 tools/evez.py --help
python3 tools/evez.py lint
python3 tools/evez.py verify
```

## Demo Pipeline

```bash
python3 tools/run_all.py --seed --mode spicy
```

## Implemented Commands (`tools/evez.py`)

| Command | Behavior |
|---------|----------|
| `lint` | Attempts to compile `spine/*.py` modules; safe no-op if missing. |
| `play` | Executes latest `spine/*.py` module; safe no-op if missing. |
| `visualize-thought` | Wrapper around `tools/visualize_thought.py`. |
| `verify` | Prints spine/docs summary and exits success. |

## Notes

- This repository contains multiple sub-layouts (`core/`, `os-evez/`, etc.).
- The root skill/CLI flow is based on the root `tools/` directory.
- Avoid claiming unimplemented subcommands; keep usage aligned to `tools/evez.py --help`.
