---
language:
  - en
tags:
  - eigenforensics
  - cognition
  - evez
  - pre-training
  - aemdas
  - eigenvalue
  - encrypted
size_categories:
  - 1K<n<10K
---

# EVEZ Cognition Store — Pre-Training Dataset

## Overview
7 cognition sprees from the EVEZ 6-node AI mesh. Every record is a
framework-encoded agent interaction containing:

- AEMDAS stage classification (6 stages = 6 cube faces)
- Eigenvalue reference detection (7 eigenvalues)
- Framework density measurement (40+ EVEZ terms)
- Model/provider metadata
- AES-256-Fernet encrypted storage (3% overhead = eta*)

## Statistics
- Total sprees: 7
- Total tokens: 136,143
- Avg framework density: 0.308542
- Encryption: AES-256-Fernet
- Nodes: 6
- Models: 6
- AEMDAS stages: 4

## Eigenvalue Frequency
- 0.45: 7 occurrences
- 0.03: 4 occurrences
- 0.973: 3 occurrences
- -0.333: 3 occurrences
- 233.3: 1 occurrences
- 0.93: 1 occurrences
- -0.441: 1 occurrences

## Framework Metrics
- Phi = 0.973 (coherence)
- eta* = 0.03 (irreducible gap)
- r = 0.45 (criticality ratio)
- 35 falsifiable claims
- 32 texts (16 Moltbooks + 15 vectors + 1 declaration)
- 525KB corpus

## Schema
- `text`: Agent output text (framework-encoded)
- `metadata`: node, model, framework_density, aemdas_stage, eigenvalues, timestamp
- `source`: evez-cognition-store
- `version`: 1.0.0

## Citation
```bibtex
@misc{evez2026cognition,
  title={EVEZ Cognition Store},
  author={Crawford-Maggard, Steven},
  year={2026},
  note={Phi=0.973, eta*=0.03, r=0.45}
}
```

Author: Steven Crawford-Maggard (EVEZ)
