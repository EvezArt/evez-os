# EVEZ as a Native Filetype

EVEZ now has a defined v1 filetype: `.evez`.

The design is intentionally boring at the byte boundary and ambitious at the semantic boundary: JSON keeps the format inspectable, while the EVEZ marker, version, epistemic state, canonicalization rule, and SHA-256 envelope make an EVEZ document identifiable and verifiable.

## What exists

- `.evez` canonical extension
- `application/vnd.evez+json` media type
- `EVEZ` format marker
- versioned schema
- deterministic canonical bytes
- SHA-256 sealing and verification
- Python reference implementation
- inert-data security model
- example document

## Minimal API

```python
from evez_file import dump, load, seal, verify

doc = {
    "evez": "EVEZ",
    "version": 1,
    "kind": "claim",
    "id": "claim-001",
    "created_at": "2026-10-05T00:00:00Z",
    "state": "PROPOSED",
    "payload": {"claim": "example"},
    "integrity": {"algorithm": "sha256", "sha256": None},
}

sealed = seal(doc)
assert verify(sealed)
dump(sealed, "claim.evez")
assert verify(load("claim.evez", verify_integrity=True))
```

The extension alone does not establish authenticity. SHA-256 establishes integrity against accidental or non-secret-changing tampering only. Authenticity requires an external signing or trust mechanism.

EVEZ therefore remains faithful to its evidence model: provenance is not truth.
