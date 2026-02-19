---
name: evez-os
version: 1.0.0
description: EVEZ Visual Cognition Layer — AI thought visualization engine
author: Steven Crawford-Maggard (EVEZ)
license: AGPL-3.0
homepage: https://github.com/EvezArt/evez-os
commercial: https://rubikspubes.gumroad.com
runtime:
  requires:
    - python3
  optional:
    - ffmpeg
  pip:
    - numpy
    - pillow
    - scipy
commands:
  play: "python3 tools/evez.py play --seed 42 --steps 14"
  visualize: "python3 tools/evez.py visualize-thought --input spine.jsonl"
  lint: "python3 tools/evez.py lint"
  help: "python3 tools/evez.py --help"
tags:
  - ai
  - visualization
  - cognition
  - forensics
  - security
  - agent
---
