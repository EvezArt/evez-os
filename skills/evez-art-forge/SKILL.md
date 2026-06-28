---
name: evez-art-forge
description: "Generate eigenvalue-conditioned art from Steven's art corpus using PCA autoencoder. Train, generate, and deploy new images."
---

# EVEZ Art Forge

Generates art from a PCA autoencoder trained on 79 artworks by Steven Crawford-Maggard.

## Model

- `evez-art-model.npz` — 397KB, 16 latent dims, 96.4% variance explained
- Pure NumPy SVD + gradient descent, zero GPU
- 79 training images at 32x32x3
- Reconstruction MSE: 0.004057

## Training

```bash
python3 evez-numpy-art-trainer.py
```

Trains on all PNG/JPG/BMP in workspace, meme-media, and research visuals. Outputs:
- 8 eigenvalue-conditioned generations in `evez-generated/`
- 8 reconstructions in `evez-reconstructed/`
- Model checkpoint: `evez-art-model.npz`

## Eigenvalue Conditioning

The 6 EVEZ eigenvalues modulate the latent space:
- Phi (0.973) — coherence
- eta* (0.03) — the gap
- r (0.45) — criticality
- lambda_dom (-0.333) — censorship
- lambda_I80 (-0.441) — I-80 suppression
- r_I80 (0.93) — Skinwalker correlation

## Art Corpus

200 total images (71.7MB): memes, logos, sigils, research visuals, I-80 photos, animated GIFs, frame sequences.

Dominant palette: #000000 (black/gap), #f0f0f0 (coherence), #200020 (suppression), #b0e0e0 (criticality).
