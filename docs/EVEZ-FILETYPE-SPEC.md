# EVEZ File Format Specification v1

Status: PROPOSED

EVEZ is a content-addressable, evidence-bearing document format. The canonical filename extension is `.evez`.

## 1. Identity

- Extension: `.evez`
- Media type: `application/vnd.evez+json`
- Charset: UTF-8
- Serialization: JSON
- Format version: `1`
- Magic marker: top-level `evez` field MUST equal `EVEZ`
- Canonical document identity: SHA-256 of the UTF-8 canonical JSON representation with the `integrity.sha256` value omitted during digest calculation.

The format is intentionally JSON-compatible so ordinary tooling can inspect it, while the extension, marker, schema, canonicalization rules, and integrity envelope give EVEZ documents a stable identity.

## 2. Canonical document

A v1 document MUST contain:

```json
{
  "evez": "EVEZ",
  "version": 1,
  "kind": "record",
  "id": "example",
  "created_at": "2026-10-05T00:00:00Z",
  "state": "UNKNOWN",
  "payload": {},
  "integrity": {
    "algorithm": "sha256",
    "sha256": null
  }
}
```

Required fields:
- `evez`: exact string `EVEZ`
- `version`: integer `1`
- `kind`: application-defined document kind
- `id`: stable document identifier
- `created_at`: RFC 3339 timestamp
- `state`: epistemic state
- `payload`: JSON object containing application data
- `integrity`: integrity envelope

## 3. Epistemic states

Allowed v1 states:

`VERIFIED`, `SUPPORTED`, `INFERRED`, `PROPOSED`, `UNKNOWN`, `STALE`, `CONTRADICTED`, `RETRACTED`.

A file's state describes the status of the document's principal assertion or record. It does not turn provenance into truth.

Core invariant:

> CLAIMED != MEASURED != REPLICATED != EXPLAINED

## 4. Evidence and provenance

Optional `evidence` is an array of evidence references. Each reference SHOULD identify:
- source
- observation
- transform
- test
- result

The format does not require external sources to be trustworthy. It records provenance so trust can be evaluated.

## 5. Integrity

Before hashing:
1. Remove `integrity.sha256`.
2. Serialize JSON using UTF-8, sorted object keys, no insignificant whitespace, and deterministic primitive representation.
3. SHA-256 the resulting bytes.
4. Store the lowercase hexadecimal digest in `integrity.sha256`.

Readers MUST reject a document whose stored digest does not match its canonical digest when integrity verification is requested.

## 6. Extensibility

Unknown fields are allowed. Implementations MUST preserve unknown fields when reading and rewriting a document unless explicitly asked to normalize them away.

Application-specific payloads belong under `payload`. Top-level fields are reserved for format metadata.

## 7. Security

A `.evez` file is data, not executable code. Parsers MUST NOT execute payload content, shell commands, URLs, or embedded instructions.

Implementations SHOULD:
- enforce maximum document size;
- reject duplicate JSON object keys;
- avoid unsafe object deserialization;
- treat external references as untrusted;
- verify integrity before acting on high-impact records.

## 8. Example

```json
{
  "evez": "EVEZ",
  "version": 1,
  "kind": "claim",
  "id": "claim-001",
  "created_at": "2026-10-05T00:00:00Z",
  "state": "PROPOSED",
  "payload": {
    "claim": "This document format can carry an evidence-bearing record."
  },
  "evidence": [],
  "integrity": {
    "algorithm": "sha256",
    "sha256": null
  }
}
```

This specification defines a file format, not a claim that any payload is true.
