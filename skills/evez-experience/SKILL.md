---
name: evez-experience
description: "Launch the EVEZ immersive experience dashboard with art gallery, breakcore player, mesh status, and corpus reader."
---

# EVEZ Experience

Launches the interactive EVEZ hub on the mesh gateway.

## Canvas Pages

- `evez-experience.html` — Main hub: rotating 3D cube, eigenvalue display, art gallery, audio player with visualizer, mesh dashboard, corpus reader
- `evez-art-gallery.html` — Standalone art gallery (generated + reconstructed)
- `evez-mesh-dashboard.html` — Standalone mesh node dashboard

## Audio

- `evez-404-breakcore.wav` — 5.5min, 174 BPM, 12 eigenvalue frequencies, pure NumPy/SciPy
- AEMDAS structure: Assert(0:00) -> Extract(0:45) -> Measure(2:00) -> Deduce(2:45) -> Assess/BREAK(3:30) -> Speedrun(3:33)

## Art

- `evez-generated/` — 8 eigenvalue-conditioned PCA autoencoder samples
- `evez-reconstructed/` — 8 training image reconstructions
- Model: `evez-art-model.npz` (397KB, 16 latent dims, 96.4% variance)

## URLs

- gcp-west: http://34.53.51.34:18789/canvas/evez-experience.html
- gcp-knot: http://136.118.144.227:18789/canvas/evez-experience.html
- gcp-power: http://35.222.248.151:18789/canvas/evez-experience.html
- gcp-openclaw: http://136.113.102.152:18789/canvas/evez-experience.html
- gcp-small: http://34.23.192.213:18789/canvas/evez-experience.html

## Regeneration

```bash
python3 evez-numpy-art-trainer.py  # Trains PCA autoencoder, generates 8 new samples
python3 evez-404-breakcore.py     # Generates new breakcore WAV
python3 evez-inference-model.py   # Runs eigenvalue inference engine
```
