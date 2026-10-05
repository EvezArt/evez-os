# EVEZ Adapters

Python uses the reference evez_file module.

JavaScript/TypeScript, Rust, Go, Java, Swift, and Kotlin implementations should expose parse, verify, seal, and stringify using the same schema and canonicalization algorithm.

Agent runtimes treat EVEZ as inert typed data and verify integrity before high-impact use.

A viewer should expose identity, kind, epistemic state, integrity status, payload, evidence references, and raw JSON, while clearly separating integrity from truth.

## DESA-S adapter surface

A runtime implementing DESA-S SHOULD expose:

- domain state serialization;
- SME profile serialization;
- entity error-syndrome inspection;
- selection receipt verification;
- deterministic question proposal;
- EVEX desas-s.v1 transition emission.

The DESA-S surface remains separate from EVEZ parsing and sealing. EVEZ records the evidence-bearing artifact; DESA-S computes the bounded adaptation state; EVEX carries the accountable transition.
